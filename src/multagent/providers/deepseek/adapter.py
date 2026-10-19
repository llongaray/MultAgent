"""DeepSeek Chat Completions with token accounting, SSE and tool-call proposals."""
from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Any
from multagent.providers.base import HTTPAdapter, ModelOutput, ProviderError, Usage


class DeepSeekAdapter(HTTPAdapter):
    provider = "deepseek"
    base_url = "https://api.deepseek.com"

    def complete(self, prompt: str, model: str, *, approved_live: bool = False,
                 tools: list[dict[str, Any]] | None = None, allow_tool_proposals: bool = False) -> ModelOutput:
        if not prompt.strip() or not model.strip():
            raise ValueError("Prompt and model must not be empty")
        data: dict[str, Any] = {"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False}
        if tools:
            if not allow_tool_proposals:
                raise PermissionError("Tools require approval; no implicit execution")
            data["tools"] = tools  # proposals only; execute via separately approved gateway
        result = self._request("POST", "/chat/completions", approved_live=approved_live, payload=data)
        try:
            message = result["choices"][0]["message"]
            usage = result.get("usage") or {}
            return ModelOutput("deepseek", result.get("model", model), message.get("content") or "",
                Usage(int(usage.get("prompt_tokens", 0)), int(usage.get("completion_tokens", 0))),
                tuple(message.get("tool_calls") or ()))
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise ProviderError("DeepSeek response did not match expected schema") from exc

    def stream(self, prompt: str, model: str, *, approved_live: bool = False) -> Iterator[str]:
        self._approved(approved_live)
        with self._client() as client:
            with client.stream("POST", self.base_url + "/chat/completions", headers=self._headers(),
                json={"model": model, "messages": [{"role": "user", "content": prompt}], "stream": True}) as response:
                if response.status_code >= 400:
                    raise ProviderError(f"DeepSeek streaming HTTP {response.status_code}")
                for line in response.iter_lines():
                    if not line.startswith("data: "):
                        continue
                    data = line[6:].strip()
                    if data == "[DONE]":
                        return
                    try:
                        event = json.loads(data)
                        delta = event.get("choices", [{}])[0].get("delta", {})
                        if isinstance(delta.get("content"), str):
                            yield delta["content"]
                    except (ValueError, KeyError, IndexError, TypeError) as exc:
                        raise ProviderError("Malformed DeepSeek stream chunk") from exc
