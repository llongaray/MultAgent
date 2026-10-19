import pytest
from multagent.core.domain import Agent
from multagent.core.router import BudgetExceeded, Mode, ProviderSuspended, Router, RoutingConfig
from multagent.providers import ProviderDenied
from multagent.providers.deepseek import DeepSeekAdapter
from multagent.providers.grok import GrokAdapter


class FakeVault:
    def get(self, ref):
        assert ref == "vault:provider"
        return "FAKE_ONLY_DO_NOT_SHIP"


class Response:
    status_code = 200
    def __init__(self, result):
        self.result = result
    def json(self):
        return self.result


class Client:
    def __init__(self, result):
        self.result = result
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def request(self, method, url, headers=None, json=None):
        assert url.startswith("https://")
        assert headers["Authorization"].startswith("Bearer ")
        return Response(self.result)


def test_deepseek_mock_and_explicit_opt_in():
    adapter = DeepSeekAdapter(FakeVault(), "vault:provider", client_factory=lambda **_: Client({
        "model": "model-ds", "choices": [{"message": {"content": "hello", "tool_calls": [{"id": "call1"}]}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5},
    }))
    with pytest.raises(ProviderDenied):
        adapter.complete("hello", "model-ds")
    result = adapter.complete("hello", "model-ds", approved_live=True)
    assert result.text == "hello" and result.usage.output_tokens == 5
    assert result.tool_calls[0]["id"] == "call1"
    with pytest.raises(PermissionError):
        adapter.complete("hello", "model-ds", tools=[{"type": "function"}], approved_live=True)


def test_grok_responses_mock_no_hosted_tools():
    adapter = GrokAdapter(FakeVault(), "vault:provider", client_factory=lambda **_: Client({
        "model": "model-grok", "output": [{"type": "message", "content": [{"type": "output_text", "text": "ok"}]}],
        "usage": {"input_tokens": 10, "output_tokens": 8},
    }))
    assert adapter.complete("hi", "model-grok", approved_live=True).text == "ok"
    with pytest.raises(PermissionError):
        adapter.complete("hi", "model-grok", approved_live=True, allow_tool_proposals=True,
            tools=[{"type": "mcp"}])


@pytest.mark.parametrize("mode,provider,works", [
    (Mode.DEEPSEEK_ONLY, "deepseek", True),
    (Mode.DEEPSEEK_ONLY, "grok", False),
    (Mode.GROK_ONLY, "grok", True),
    (Mode.GROK_ONLY, "deepseek", False),
    (Mode.HYBRID, "deepseek", True),
    (Mode.HYBRID, "grok", True),
])
def test_router_modes(mode, provider, works):
    a = Agent("a", "w", "Employee", provider, "model")
    router = Router(RoutingConfig(mode, {"deepseek", "grok"}, {(provider, "model"): (0.1, 0.3)}))
    if works:
        assert router.route(a, input_tokens=1000, output_tokens=1000)[:2] == (provider, "model")
    else:
        with pytest.raises(ProviderSuspended):
            router.route(a, input_tokens=1000, output_tokens=1000)


def test_budget_and_unknown_price_fail_closed():
    a = Agent("a", "w", "Employee", "deepseek", "unknown")
    router = Router(RoutingConfig())
    with pytest.raises(BudgetExceeded):
        router.route(a, input_tokens=2, output_tokens=2)
