"""DeepSeek and Grok API key onboarding. User-facing text never includes the secret."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

from multagent.providers.base import ProviderError
from multagent.providers.deepseek import DeepSeekAdapter
from multagent.providers.grok import GrokAdapter
from multagent.security.vault import vault_ref

PROVIDERS = frozenset({"deepseek", "grok"})


class CredentialRejected(ValueError):
    """Rejected credential input. The message is safe to show in the UI."""


class SecretStore(Protocol):
    def put(self, name: str, secret: str) -> str: ...
    def get(self, reference: str) -> str: ...
    def contains(self, reference: str) -> bool: ...
    def delete(self, reference: str) -> None: ...


def require_provider(provider: str) -> str:
    if provider not in PROVIDERS:
        raise CredentialRejected("Provedor não suportado")
    return provider


def reference_for(provider: str) -> str:
    return vault_ref(require_provider(provider))


def validate_api_key(secret: str) -> str:
    if not isinstance(secret, str) or not secret or any(character.isspace() for character in secret):
        raise CredentialRejected("Informe uma API key sem espaços")
    if len(secret) < 12:
        raise CredentialRejected("A API key informada é inválida")
    return secret


def store_api_key(vault: SecretStore, provider: str, secret: str) -> str:
    provider = require_provider(provider)
    cleaned = validate_api_key(secret)
    return vault.put(provider, cleaned)


def probe_stored_credential(
    vault: SecretStore,
    provider: str,
    *,
    client_factory: Callable[..., Any] | None = None,
    approved_live: bool = False,
) -> None:
    """Confirm the stored key with the provider. Raises a message that omits the secret."""
    provider = require_provider(provider)
    reference = reference_for(provider)
    if not vault.contains(reference):
        raise CredentialRejected("Nenhuma credencial configurada para este provedor")
    adapter_cls = DeepSeekAdapter if provider == "deepseek" else GrokAdapter
    try:
        found = adapter_cls(vault, reference, client_factory=client_factory).models(
            approved_live=approved_live
        )
    except ProviderError:
        raise
    except (OSError, ValueError, KeyError, TypeError, TimeoutError, ConnectionError) as exc:
        raise ProviderError("Falha ao validar a credencial") from exc
    if not found:
        raise ProviderError("O provedor não confirmou a credencial")
