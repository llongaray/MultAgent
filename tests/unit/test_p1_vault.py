import pytest
from multagent.security.vault import EncryptedFileVault, VaultUnavailable


def test_encrypted_vault_explicit_unlock(tmp_path):
    pytest.importorskip("cryptography")
    path = tmp_path / "vault.json"
    vault = EncryptedFileVault(path, "a secure password above 12 chars")
    assert vault.put("deepseek", "SUPER_SECRET_TEST_VALUE") == "vault:deepseek"
    text = path.read_text()
    assert "SUPER_SECRET_TEST_VALUE" not in text
    assert vault.get("vault:deepseek") == "SUPER_SECRET_TEST_VALUE"
    with pytest.raises(VaultUnavailable):
        EncryptedFileVault(path, "another wrong password")
    assert EncryptedFileVault(path, "a secure password above 12 chars").get("vault:deepseek") == "SUPER_SECRET_TEST_VALUE"
    vault.delete("vault:deepseek")
    with pytest.raises(KeyError):
        vault.get("vault:deepseek")


def test_vault_requires_strong_unlock(tmp_path):
    with pytest.raises(ValueError):
        EncryptedFileVault(tmp_path / "x", "short")
