# pylint: skip-file
# nosec B101
"""Smoke tests for Termux-Sentinel."""

import json
from pathlib import Path

import setup_gdrive_credentials
import Termux_Sentinel


def test_import_and_entrypoints():
    """Verify module attributes and primary entry points exist."""
    assert hasattr(Termux_Sentinel, "main")
    assert hasattr(Termux_Sentinel, "cli_entrypoint")
    assert callable(Termux_Sentinel.main)
    assert callable(Termux_Sentinel.cli_entrypoint)


def test_vault_structure_and_validity():
    """Verify vault.json is valid and conforms to expected structure."""
    vault_path = Path("vault.json")
    assert vault_path.exists(), "vault.json must be present in the repository root"

    with open(vault_path, encoding="utf-8") as vault_file:
        data = json.load(vault_file)

    # In Termux-Sentinel, vault.json stores a list of shield definitions
    assert isinstance(data, (list, dict)), "vault.json root must be a list or dict"
    if isinstance(data, list):
        assert bool(data), "vault.json should contain default shield definitions"
        first_item = data[0]
        assert "name" in first_item
        assert "pattern" in first_item


def test_human_size_formatting():
    """Test human readable size conversions."""
    assert Termux_Sentinel.human_size(0) == "0.0 B"
    assert Termux_Sentinel.human_size(1024) == "1.0 KB"
    assert Termux_Sentinel.human_size(1048576) == "1.0 MB"


def test_string_formatting_helpers():
    """Verify terminal formatting width helpers."""
    assert Termux_Sentinel.char_width("A") == 1
    assert Termux_Sentinel.visible_len("Sentinel") == 8
    # Strips ANSI escape codes from length calculation
    colored_str = "\033[96mTest\033[0m"
    assert Termux_Sentinel.visible_len(colored_str) == 4


def test_vault_protection_logic():
    """Verify that is_protected identifies protected patterns."""
    assert callable(Termux_Sentinel.is_protected)
    # A path containing Important_Documents should match the default vault rule
    assert (
        Termux_Sentinel.is_protected("/storage/emulated/0/Important_Documents/Notes")
        is True
    )
    # An ephemeral cache path should NOT be protected
    assert (
        Termux_Sentinel.is_protected("/data/data/com.termux/files/home/.cache/tmp_junk")
        is False
    )


def test_gdrive_setup_does_not_log_credentials_path(tmp_path, monkeypatch, capsys):
    """The setup script must not print the credential file path."""
    credentials_path = tmp_path / "client_secret.json"
    credentials_path.write_text(
        json.dumps(
            {
                "installed": {
                    "client_id": "test-client-id",
                    "client_secret": "test-client-secret",
                }
            }
        ),
        encoding="utf-8",
    )
    config_path = tmp_path / ".config" / "rclone" / "rclone.conf"
    monkeypatch.setattr(setup_gdrive_credentials, "CONFIG_PATH", str(config_path))
    monkeypatch.setattr(
        setup_gdrive_credentials.sys,
        "argv",
        ["setup_gdrive_credentials.py", str(credentials_path)],
    )

    setup_gdrive_credentials.main()

    output = capsys.readouterr().out
    assert str(credentials_path) not in output


def test_gdrive_setup_skips_invalid_json(tmp_path, monkeypatch):
    """Credential discovery skips malformed files and continues searching."""
    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text("{not valid json", encoding="utf-8")
    valid_path = tmp_path / "client_secret.json"
    valid_path.write_text(
        json.dumps({"installed": {"client_id": "test", "client_secret": "test"}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        setup_gdrive_credentials.os.path,
        "expanduser",
        lambda path: (
            str(tmp_path)
            if path == "~"
            else str(tmp_path / path[2:]) if path.startswith("~/") else path
        ),
    )

    assert setup_gdrive_credentials.find_client_secret() == str(valid_path)


def test_storage_threshold_check():
    """Verify storage threshold detector function."""
    assert hasattr(Termux_Sentinel, "check_storage_threshold")
    is_crit, free_gb = Termux_Sentinel.check_storage_threshold(min_gb=1.0)
    assert isinstance(is_crit, bool)
    assert isinstance(free_gb, float)


def test_bloat_hunter_and_offload_entrypoints():
    """Verify new CLI commands exist and are callable."""
    assert hasattr(Termux_Sentinel, "cli_hunt")
    assert hasattr(Termux_Sentinel, "cli_offload")
    assert hasattr(Termux_Sentinel, "cli_autoclean")
    assert callable(Termux_Sentinel.cli_hunt)
    assert callable(Termux_Sentinel.cli_offload)
    assert callable(Termux_Sentinel.cli_autoclean)
