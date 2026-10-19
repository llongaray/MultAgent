"""Consistent provider protocol with explicit opt-in for paid network requests."""
from __future__ import annotations

from dataclasses import dataclass, field
import time
from typing import Any, Callable


class ProviderDenied(PermissionError):
    """Request was not explicitly approved for paid/remote execution."""


class ProviderError(RuntimeError):
    """Remote provider failure without leaking keys or user prompts."""


@dataclass(frozen=True, slots=True)
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass(frozen=True, slots=True)
class ModelOutput:
    provider: str
    model: str
    text: str
    usage: Usage = field(default_factory=Usage)
    tool_calls: tuple[dict[str, Any], ...] = ()  # Recorded; NEVER executed here


class HTTPAdapter:
    """Common HTTP transport; normal operations require explicit live approval."""
    provider: str = ""
    base_url: str = ""

    def __init__(self, vault: Any, credential_ref: str, *, client_factory: Callable[..., Any] | None = None) -> None:
        self.vault, self.credential_ref, self.client_factory = vault, credential_ref, client_factory
        if not credential_ref.startswith("vault:"):
            raise ValueError("Credentials must be vault references")

    def _client(self) -> Any:
        if self.client_factory is not None:
            return self.client_factory(timeout=30)
        try:
            import httpx
        except ImportError as exc:
            raise ProviderError("Install the optional providers extra") from exc
        return httpx.Client(timeout=30, follow_redirects=False)

    def _headers(self) -> dict[str, str]:
        key = self.vault.get(self.credential_ref)
        if not key:
            raise ProviderError("Provider credential missing")
        return {"Authorization": "Bearer " + key, "Content-Type": "application/json"}

    @staticmethod
    def _approved(approved_live: bool) -> None:
        if approved_live is not True:
            raise ProviderDenied("Remote inference needs an explicit authorization")

    def _request(self, method: str, path: str, *, approved_live: bool, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        self._approved(approved_live)
        with self._client() as client:
            for attempt in range(3):
                try:
                    r = client.request(method, self.base_url + path, headers=self._headers(), json=payload)
                    if r.status_code in (429, 500, 502, 503, 504) and attempt < 2:
                        time.sleep(0.2 * (2**attempt))
                        continue
                    if r.status_code >= 400:
                        raise ProviderError(f"{self.provider} returned HTTP {r.status_code}")
                    data: dict[str, Any] = r.json()
                    return data
                except (TimeoutError, ConnectionError) as exc:
                    if attempt == 2:
                        raise ProviderError(f"{self.provider} network error") from exc
                    time.sleep(0.2 * (2**attempt))
        raise ProviderError("Provider request exhausted retries")

    def models(self, *, approved_live: bool = False) -> list[str]:
        data = self._request("GET", "/models", approved_live=approved_live)
        return [str(m["id"]) for m in data.get("data", []) if isinstance(m, dict) and m.get("id")]
