"""The selected model tier must reach the driver, and Haiku must run without the
Opus/Sonnet-only thinking+effort params (which would 400)."""

from backend import agent
from backend.agent import default_driver, run_turn


class _EmptyTools:
    tools: list = []


class _FakeSession:
    async def list_tools(self):
        return _EmptyTools()


async def _noop_emit(event):
    pass


async def test_run_turn_threads_selected_model():
    captured: dict = {}

    def capturing_driver(client, messages, tools, instrumented, model):
        captured["model"] = model

        async def gen():
            return
            yield  # make this an async generator

        return gen()

    await run_turn("hi", _noop_emit, _FakeSession(), model="sonnet", driver=capturing_driver)
    assert captured["model"] == "sonnet"


def test_model_registry_and_haiku_runs_plain():
    assert set(agent.MODELS) == {"opus", "sonnet", "haiku"}
    assert agent.DEFAULT_MODEL in agent.MODELS
    # Haiku 4.5 rejects adaptive thinking + effort, so it must send neither.
    assert agent._MODEL_PARAMS["haiku"] == {}
    assert "effort" in agent._MODEL_PARAMS["opus"]["output_config"]


def test_default_driver_builds_correct_request():
    captured: dict = {}

    class FakeMessages:
        def tool_runner(self, **kwargs):
            captured.update(kwargs)
            return iter(())

    class FakeBeta:
        messages = FakeMessages()

    class FakeClient:
        beta = FakeBeta()

    default_driver(FakeClient(), [{"role": "user", "content": "x"}], [], None, "haiku")
    assert captured["model"] == "claude-haiku-4-5"
    assert "thinking" not in captured and "output_config" not in captured

    captured.clear()
    default_driver(FakeClient(), [{"role": "user", "content": "x"}], [], None, "opus")
    assert captured["model"] == "claude-opus-4-8"
    assert captured["thinking"] == {"type": "adaptive"}
    assert captured["output_config"] == {"effort": "medium"}
