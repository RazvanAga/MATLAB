"""FastAPI app: the spine that joins browser, agent loop, and MCP.

Lifespan opens one long-lived MCP ClientSession over stdio to the Mock MCP
server (this is the single connection F2 will repoint at the real MATLAB MCP
Core Server binary). ``GET /api/stream`` runs one agentic turn and streams the
resulting events to the browser over SSE. Static assets are served from
``public/``.
"""

import asyncio
import json
import sys
from contextlib import AsyncExitStack, asynccontextmanager
from pathlib import Path
from typing import Any

from anthropic import AsyncAnthropic
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from sse_starlette.sse import EventSourceResponse

from . import agent

REPO_ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DIR = REPO_ROOT / "public"

# F1: the Mock MCP server. F2 swaps this for the real Core Server binary.
MCP_SERVER = StdioServerParameters(command=sys.executable, args=["-m", "mock_mcp.server"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncExitStack() as stack:
        read, write = await stack.enter_async_context(stdio_client(MCP_SERVER))
        session = await stack.enter_async_context(ClientSession(read, write))
        await session.initialize()
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
