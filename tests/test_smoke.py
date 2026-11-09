# pylint: skip-file
# nosec B101
"""Smoke tests for Termux-Sentinel."""

import json
from pathlib import Path

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
    assert Termux_Sentinel.is_protected("/storage/emulated/0/Important_Documents/Notes") is True
    # An ephemeral cache path should NOT be protected
    assert Termux_Sentinel.is_protected("/data/data/com.termux/files/home/.cache/tmp_junk") is False
