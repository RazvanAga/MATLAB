"""FastAPI app: the spine that joins browser, agent loop, and MCP.

Lifespan opens one long-lived MCP ClientSession over stdio. In production it
launches the real MATLAB MCP Core Server in ``--matlab-session-mode=existing``
(strict): it attaches to the user's already-open, shared MATLAB R2026a and
**fails loudly at startup** if no shared session is found (F2 / S2). Set
``MATLAB_MCP_MOCK=1`` to use the in-repo Mock MCP instead (F1 chain tests).

``GET /api/stream`` runs one agentic turn and streams the resulting events to
the browser over SSE. Static assets are served from ``public/``.
"""

import asyncio
import json
import os
import sys
from contextlib import AsyncExitStack, asynccontextmanager
from pathlib import Path
from typing import Any

from anthropic import AsyncAnthropic
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from sse_starlette.sse import EventSourceResponse

from . import agent

REPO_ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DIR = REPO_ROOT / "public"

# Load ANTHROPIC_API_KEY (and friends) from a gitignored .env at the repo root,
# so the key persists across runs without re-exporting it. A real environment
# variable still wins; absent .env is a no-op. AsyncAnthropic() reads it later.
load_dotenv(REPO_ROOT / ".env")

# Real MATLAB MCP Core Server (Go binary, installed by the Simulink Agentic
# Toolkit). The Simulink extension file adds the 7 model_* tools on top of the
# 5 core tools — the agent only ever sees the DEMO_TOOLS subset (agent.py).
CORE_SERVER_BIN = Path.home() / ".matlab/agentic-toolkits/bin/matlab-mcp-core-server.exe"
SIMULINK_TOOLS_JSON = Path.home() / ".matlab/agentic-toolkits/simulink/tools/tools.json"

# How long to wait for the preflight MATLAB ping (engine attach + first eval).
PREFLIGHT_TIMEOUT_S = 90


def _use_mock() -> bool:
    """True when the in-repo Mock MCP should stand in for the real Core Server
    (F1 chain tests). Read at lifespan time so tests can set the env var."""
    return os.environ.get("MATLAB_MCP_MOCK") == "1"


def mcp_server_params() -> StdioServerParameters:
    if _use_mock():
        return StdioServerParameters(command=sys.executable, args=["-m", "mock_mcp.server"])
    return StdioServerParameters(
        command=str(CORE_SERVER_BIN),
        args=[
            "--matlab-session-mode=existing",  # strict: attach only, never start a new session
            f"--extension-file={SIMULINK_TOOLS_JSON}",
        ],
    )


async def _preflight_matlab(session: ClientSession) -> None:
    """Force the engine attach with a trivial eval so a missing shared session
    fails *here*, at startup, with a clear message — not mid-demo. In
    ``existing`` mode the Core Server has no MATLAB to talk to unless the user's
    open R2026a is on ``matlab.engine.shareEngine``."""
    try:
        result = await asyncio.wait_for(
            session.call_tool("evaluate_matlab_code", {"code": "1+1;"}),
            timeout=PREFLIGHT_TIMEOUT_S,
        )
    except Exception as exc:  # any failure here (timeout, transport, no session) is fatal
        raise RuntimeError(
            "MATLAB preflight failed: could not reach a shared MATLAB session via the "
            "MATLAB MCP Core Server (--matlab-session-mode=existing). Open MATLAB R2026a "
            "and run `matlab.engine.shareEngine`, then restart the backend."
        ) from exc
    if result.isError:
        detail = "".join(getattr(c, "text", "") for c in result.content)
        raise RuntimeError(f"MATLAB preflight returned an error: {detail.strip()}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # The agent exports figures here; create it so exportgraphics never fails on
    # a missing folder, and so the wrapper has a folder to watch.
    agent.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    async with AsyncExitStack() as stack:
        read, write = await stack.enter_async_context(stdio_client(mcp_server_params()))
        session = await stack.enter_async_context(ClientSession(read, write))
        await session.initialize()
        if not _use_mock():  # S2: prove the real, visible MATLAB is reachable before serving
            await _preflight_matlab(session)
        app.state.mcp = session
        app.state.anthropic = AsyncAnthropic()  # creds from `ant auth login` profile
        yield


app = FastAPI(lifespan=lifespan)


@app.get("/api/stream")
async def stream(request: Request, message: str, model: str = agent.DEFAULT_MODEL):
    """Run one agentic turn for ``message`` and stream SSE events to the browser."""
    if model not in agent.MODELS:  # ignore unknown values rather than 400 the demo
        model = agent.DEFAULT_MODEL

    queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

    async def emit(event: dict[str, Any]) -> None:
        await queue.put(event)

    producer = asyncio.create_task(
        agent.run_turn(
            message,
            emit,
            request.app.state.mcp,
            client=request.app.state.anthropic,
            model=model,
            # Read the driver off the module at call time so tests can stub the model.
            driver=agent.default_driver,
        )
    )

    async def event_generator():
        try:
            while True:
                event = await queue.get()
                yield {"data": json.dumps(event)}
                if event.get("type") == "done":
                    break
        finally:
            if not producer.done():
                producer.cancel()

    return EventSourceResponse(event_generator())


# Static frontend (registered last so /api/* wins). html=True serves index.html at /.
app.mount("/", StaticFiles(directory=str(PUBLIC_DIR), html=True), name="public")
