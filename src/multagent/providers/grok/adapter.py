"""xAI Responses API with separate output mapping; tool calls remain proposals."""
from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Any
from multagent.providers.base import HTTPAdapter, ModelOutput, ProviderError, Usage


class GrokAdapter(HTTPAdapter):
    provider = "grok"
    base_url = "https://api.x.ai/v1"

    def complete(self, prompt: str, model: str, *, approved_live: bool = False,
                 tools: list[dict[str, Any]] | None = None, allow_tool_proposals: bool = False) -> ModelOutput:
        if not prompt.strip() or not model.strip():
            raise ValueError("Prompt and model must not be empty")
        payload: dict[str, Any] = {"model": model, "input": prompt, "store": False}
        if tools:
            if not allow_tool_proposals:
                raise PermissionError("Tools require explicit approval")
            if any(t.get("type") in ("mcp", "web_search", "x_search") for t in tools):
                raise PermissionError("Hosted search/MCP tools need separate policy and consent")
            payload["tools"] = tools
        data = self._request("POST", "/responses", approved_live=approved_live, payload=payload)
        try:
            text = data.get("output_text") or ""
            calls = []
            for item in data.get("output", []):
                if item.get("type") == "function_call":
                    calls.append(item)
                if item.get("type") == "message":
                    for part in item.get("content", []):
                        if part.get("type") == "output_text":
                            text += part.get("text") or ""
            usage = data.get("usage") or {}
            return ModelOutput("grok", data.get("model", model), text,
                Usage(int(usage.get("input_tokens", 0)), int(usage.get("output_tokens", 0))), tuple(calls))
        except (KeyError, IndexError, TypeError, ValueError, AttributeError) as exc:
            raise ProviderError("Grok response did not match expected schema") from exc

    def stream(self, prompt: str, model: str, *, approved_live: bool = False) -> Iterator[str]:
        self._approved(approved_live)
        with self._client() as client:
            with client.stream("POST", self.base_url + "/responses", headers=self._headers(),
                json={"model": model, "input": prompt, "store": False, "stream": True}) as response:
                if response.status_code >= 400:
                    raise ProviderError(f"Grok streaming HTTP {response.status_code}")
                for line in response.iter_lines():
                    if not line.startswith("data: "):
                        continue
                    payload = line[6:].strip()
                    if payload == "[DONE]":
                        return
                    try:
                        event = json.loads(payload)
                    except ValueError as exc:
                        raise ProviderError("Malformed Grok stream chunk") from exc
                    if event.get("type") == "response.output_text.delta":
                        yield str(event.get("delta") or "")
