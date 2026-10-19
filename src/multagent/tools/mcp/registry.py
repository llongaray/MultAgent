"""Metadata-only MCP Registry discovery; discovery never installs or runs tools."""
from __future__ import annotations
from urllib.parse import urlsplit
from typing import Any

class RegistryDenied(PermissionError):
    pass

class Registry:
    def __init__(self, base_url: str, *, allowed_host: str, http_factory: Any = None) -> None:
        url = urlsplit(base_url)
        if (url.scheme != "https" or url.hostname != allowed_host or url.username or url.password
            or url.query or url.fragment or url.port not in (None, 443)):
            raise RegistryDenied("Registry URL is not explicitly trusted")
        self.url, self.http_factory = base_url.rstrip("/"), http_factory

    def discover(self, *, approved_network: bool = False) -> list[dict[str, Any]]:
        if not approved_network:
            raise RegistryDenied("Registry discovery requires network consent")
        if self.http_factory:
            client = self.http_factory(timeout=20)
        else:
            try:
                import httpx
            except ImportError as exc:
                raise RuntimeError("Install multagent[forges]") from exc
            client = httpx.Client(timeout=20, follow_redirects=False)
        with client as session:
            response = session.get(self.url)
            if response.status_code != 200 or len(response.content) > 2_000_000:
                raise RegistryDenied("Registry returned an invalid or oversized response")
            data = response.json()
        collection = data.get("servers", []) if isinstance(data, dict) else []
        if not isinstance(collection, list):
            raise RegistryDenied("Registry response schema invalid")
        # Metadata is untrusted input. Do not translate registry entries into tool grants.
        return [v for v in collection[:100] if isinstance(v, dict)]
