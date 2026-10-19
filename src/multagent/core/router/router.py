"""Deterministic model routing; never silently change an agent's provider."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from multagent.core.domain import Agent


class Mode(str, Enum):
    DEEPSEEK_ONLY = "deepseek_only"
    GROK_ONLY = "grok_only"
    HYBRID = "hybrid"


class ProviderSuspended(PermissionError):
    """Agent cannot run under the selected global provider policy."""


class BudgetExceeded(ValueError):
    """Insufficient budget or unknown price; fail closed."""


@dataclass(slots=True)
class RoutingConfig:
    mode: Mode = Mode.DEEPSEEK_ONLY
    enabled: set[str] = field(default_factory=lambda: {"deepseek"})
    # (provider, model) -> (input USD per 1M tokens, output USD per 1M tokens)
    prices: dict[tuple[str, str], tuple[float, float]] = field(default_factory=dict)
    maximum_usd_per_run: float = 0.25


class Router:
    def __init__(self, config: RoutingConfig):
        if config.maximum_usd_per_run < 0:
            raise ValueError("Budget cannot be negative")
        self.config = config

    def permitted(self, agent: Agent) -> bool:
        allowed = {"deepseek"} if self.config.mode == Mode.DEEPSEEK_ONLY else (
            {"grok"} if self.config.mode == Mode.GROK_ONLY else {"deepseek", "grok"})
        return agent.enabled and agent.provider in allowed and agent.provider in self.config.enabled

    def route(self, agent: Agent, *, input_tokens: int, output_tokens: int,
              remaining_usd: float | None = None) -> tuple[str, str, float]:
        if not self.permitted(agent):
            raise ProviderSuspended("The agent's provider is disabled by global policy")
        if input_tokens < 0 or output_tokens < 0:
            raise ValueError("Token estimates must be nonnegative")
        price = self.config.prices.get((agent.provider, agent.model))
        if price is None or min(price) < 0:
            raise BudgetExceeded("No approved pricing for this provider/model")
        estimate = (input_tokens * price[0] + output_tokens * price[1]) / 1_000_000
        cap = self.config.maximum_usd_per_run
        if remaining_usd is not None:
            cap = min(cap, remaining_usd)
        if estimate > cap:
            raise BudgetExceeded("Run estimated to exceed approved cost limit")
        return agent.provider, agent.model, estimate
