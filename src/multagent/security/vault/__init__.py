"""Secrets storage: no plaintext fallback when OS keyring is unavailable."""
from .vault import CredentialVault, EncryptedFileVault, KeyringVault, VaultUnavailable
__all__ = ["CredentialVault", "EncryptedFileVault", "KeyringVault", "VaultUnavailable"]
