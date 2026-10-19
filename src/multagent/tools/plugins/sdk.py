"""Minimal plugin SDK contract. The catalog does not execute plugin code."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Any

@dataclass(frozen=True)
class PluginContext:
    workspace_id: str
    agent_id: str
    permissions: frozenset[str]
    approved: bool = False

@dataclass(frozen=True)
class PluginResult:
    output: dict[str, Any]
    audited: bool

class Plugin(Protocol):
    name: str
    version: str
    def run(self, context: PluginContext, args: dict[str, Any]) -> PluginResult:
        ...
