"""Unit coverage for the F2 wiring in backend.app: real-vs-mock server selection
and the strict ``existing``-mode preflight that must fail loudly at startup.

The live happy path (real Core Server attaching to a shared MATLAB) is validated
manually per the issue; here we cover the selection logic and the failure path,
which can't be triggered live without unsharing MATLAB.
"""

import asyncio

import pytest

from backend import app


def test_mcp_server_params_defaults_to_real(monkeypatch):
    monkeypatch.delenv("MATLAB_MCP_MOCK", raising=False)
    params = app.mcp_server_params()
    assert params.command == str(app.CORE_SERVER_BIN)
    assert "--matlab-session-mode=existing" in params.args


def test_mcp_server_params_mock_when_env_set(monkeypatch):
    monkeypatch.setenv("MATLAB_MCP_MOCK", "1")
    params = app.mcp_server_params()
    assert params.args == ["-m", "mock_mcp.server"]


class _Text:
    def __init__(self, text: str) -> None:
        self.text = text


class _Result:
    def __init__(self, is_error: bool, text: str = "") -> None:
        self.isError = is_error
        self.content = [_Text(text)]


async def test_preflight_raises_when_tool_call_fails():
    class _Session:
        async def call_tool(self, *args, **kwargs):
            raise ConnectionError("no shared session")

    with pytest.raises(RuntimeError, match="MATLAB preflight failed"):
        await app._preflight_matlab(_Session())


async def test_preflight_raises_on_error_result():
    class _Session:
        async def call_tool(self, *args, **kwargs):
            return _Result(is_error=True, text="License checkout failed")

    with pytest.raises(RuntimeError, match="License checkout failed"):
        await app._preflight_matlab(_Session())


async def test_preflight_passes_on_clean_result():
    class _Session:
        async def call_tool(self, *args, **kwargs):
            return _Result(is_error=False, text="ans = 2")

    await app._preflight_matlab(_Session())  # must not raise
