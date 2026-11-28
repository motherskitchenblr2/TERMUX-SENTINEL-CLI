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


def test_cross_platform_disk_usage():
    """Verify cross-platform disk usage works and returns valid metrics."""
    used, total, free, pct = Termux_Sentinel.get_disk_usage()
    assert used != "N/A"
    assert total != "N/A"
    assert free != "N/A"
    assert "%" in pct


def test_wide_screen_columns_responsiveness(monkeypatch):
    """Verify terminal width adapts dynamically up to 120 columns."""
    # Simulated mobile portrait width
    monkeypatch.setattr(
        Termux_Sentinel.shutil,
        "get_terminal_size",
        lambda fallback: type("Size", (), {"columns": 40, "lines": 24})(),
    )
    assert Termux_Sentinel.get_term_cols() == 44  # Clamped to min 44

    # Simulated wide desktop terminal
    monkeypatch.setattr(
        Termux_Sentinel.shutil,
        "get_terminal_size",
        lambda fallback: type("Size", (), {"columns": 100, "lines": 30})(),
    )
    assert Termux_Sentinel.get_term_cols() == 100


def test_windows_simulation(monkeypatch):
    """Verify Windows platform simulation logic."""
    monkeypatch.setattr(Termux_Sentinel, "IS_WINDOWS", True)
    name = Termux_Sentinel.get_device_name()
    assert "WINDOWS" in name
    # Verify kill_process_pid handles windows execution safely
    res = Termux_Sentinel.kill_process_pid(999999)
    assert isinstance(res, bool)


def test_repair_and_doctor_diagnostics(capsys):
    """Verify repair and doctor diagnostics run cleanly without error."""
    assert hasattr(Termux_Sentinel, "cli_repair")
    assert callable(Termux_Sentinel.cli_repair)
    Termux_Sentinel.cli_repair(auto_fix=False)
    out = capsys.readouterr().out
    assert "DIAGNOSTIC" in out or "DIAGNOSTICS" in out


def test_get_user_processes_cross_platform():
    """Verify process scanning returns list of process tuples."""
    assert hasattr(Termux_Sentinel, "get_user_processes")
    procs = Termux_Sentinel.get_user_processes()
    assert isinstance(procs, list)
    if procs:
        pid, cmd = procs[0]
        assert isinstance(pid, int)
        assert isinstance(cmd, str)


def test_self_heal_sentinel(capsys):
    """Verify self-healing runs without exception."""
    assert hasattr(Termux_Sentinel, "self_heal_sentinel")
    assert callable(Termux_Sentinel.self_heal_sentinel)
    healed, issues = Termux_Sentinel.self_heal_sentinel(silent=True)
    assert isinstance(healed, list)
    assert isinstance(issues, list)


def test_corrupted_vault_auto_recovery(tmp_path, monkeypatch):
    """Verify that a corrupted or malformed vault.json auto-recovers gracefully."""
    fake_vault = tmp_path / "vault.json"
    fake_vault.write_text("{corrupt: json bad syntax", encoding="utf-8")
    monkeypatch.setattr(Termux_Sentinel, "VAULT_FILE", str(fake_vault))
    monkeypatch.setattr(Termux_Sentinel, "VAULT_DIR", str(tmp_path))

    # load_vault should intercept corruption, back it up, and restore valid default vault
    items = Termux_Sentinel.load_vault()
    assert isinstance(items, list)
    assert len(items) >= len(Termux_Sentinel.DEFAULT_VAULT_ITEMS)
    # The file should now contain valid JSON
    with open(fake_vault, encoding="utf-8") as f:
        reloaded = json.load(f)
    assert isinstance(reloaded, list)


def test_atomic_save_vault(tmp_path, monkeypatch):
    """Verify save_vault writes valid json atomically."""
    test_vault = tmp_path / "vault.json"
    monkeypatch.setattr(Termux_Sentinel, "VAULT_FILE", str(test_vault))
    monkeypatch.setattr(Termux_Sentinel, "VAULT_DIR", str(tmp_path))

    data = [{"id": 99, "name": "Atomic Test", "pattern": "Test", "locked": False}]
    Termux_Sentinel.save_vault(data)
    assert test_vault.exists()
    with open(test_vault, encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded[0]["name"] == "Atomic Test"


def test_inspect_device_hardware():
    """Verify hardware inspector returns complete telemetry and recommendation tier."""
    assert hasattr(Termux_Sentinel, "inspect_device_hardware")
    info = Termux_Sentinel.inspect_device_hardware()
    assert isinstance(info, dict)
    for key in [
        "cpu_cores",
        "arch",
        "ram_total_gb",
        "disk_free_gb",
        "tier_id",
        "recommended_models",
    ]:
        assert key in info
    assert len(info["recommended_models"]) > 0
    assert "name" in info["recommended_models"][0]


def test_ai_config_crud(tmp_path, monkeypatch):
    """Verify loading, saving and toggling AI configuration."""
    cfg_path = tmp_path / "ai_config.json"
    monkeypatch.setattr(Termux_Sentinel, "AI_CONFIG_FILE", str(cfg_path))
    monkeypatch.setattr(Termux_Sentinel, "VAULT_DIR", str(tmp_path))

    cfg = Termux_Sentinel.load_ai_config()
    assert isinstance(cfg, dict)
    assert cfg.get("provider") == "ollama"

    state1 = Termux_Sentinel.toggle_agentic_mode()
    assert isinstance(state1, bool)
    assert state1 is True
    reloaded = Termux_Sentinel.load_ai_config()
    assert reloaded["agentic_enabled"] is True

    state2 = Termux_Sentinel.toggle_agentic_mode()
    assert state2 is False


def test_validate_and_sync_models_mock():
    """Verify provider validation parser logic."""
    assert hasattr(Termux_Sentinel, "validate_and_sync_models")
    ok, err, models = Termux_Sentinel.validate_and_sync_models(
        "invalid_provider", "bad_key"
    )
    assert ok is False


def test_cli_ai_entrypoint(capsys):
    """Verify cli_ai routes without crash."""
    assert hasattr(Termux_Sentinel, "cli_ai")
    Termux_Sentinel.cli_ai("status")
    out = capsys.readouterr().out
    assert "AGENTIC AI STATUS" in out


def test_check_core_prerequisites():
    """Verify check_core_prerequisites returns valid structure and properties."""
    assert hasattr(Termux_Sentinel, "check_core_prerequisites")
    assert callable(Termux_Sentinel.check_core_prerequisites)
    prereqs = Termux_Sentinel.check_core_prerequisites()
    assert isinstance(prereqs, dict)
    for tool in ("python", "rclone", "ollama"):
        assert tool in prereqs
        assert "mandatory" in prereqs[tool]
        assert "installed" in prereqs[tool]
        assert "name" in prereqs[tool]
        assert "role" in prereqs[tool]

    assert prereqs["python"]["mandatory"] is True
    assert prereqs["python"]["installed"] is True
    assert prereqs["rclone"]["mandatory"] is False
    assert prereqs["ollama"]["mandatory"] is False


def test_install_optional_dependency():
    """Verify install_optional_dependency validates input and rejects unknown tools."""
    assert hasattr(Termux_Sentinel, "install_optional_dependency")
    assert callable(Termux_Sentinel.install_optional_dependency)
    res = Termux_Sentinel.install_optional_dependency("unknown_dep_tool")
    assert res is False


def test_cli_prerequisites_entrypoint(capsys):
    """Verify cli_prerequisites runs non-interactively without error."""
    assert hasattr(Termux_Sentinel, "cli_prerequisites")
    assert callable(Termux_Sentinel.cli_prerequisites)
    Termux_Sentinel.cli_prerequisites(interactive=False)
    out = capsys.readouterr().out
    assert "PREREQUISITES" in out
    assert "Python" in out


def test_ollama_live_status_detection():
    """Verify get_ollama_live_status returns structured live telemetry."""
    assert hasattr(Termux_Sentinel, "get_ollama_live_status")
    assert callable(Termux_Sentinel.get_ollama_live_status)
    stat = Termux_Sentinel.get_ollama_live_status()
    assert isinstance(stat, dict)
    assert "running" in stat
    assert "pulled_models" in stat
    assert "model_count" in stat
    assert isinstance(stat["pulled_models"], list)


def test_ai_runtime_status_detects_storage_presence():
    """Verify get_ai_runtime_status accurately distinguishes presence vs absence of models."""
    assert hasattr(Termux_Sentinel, "get_ai_runtime_status")
    assert callable(Termux_Sentinel.get_ai_runtime_status)
    cfg = {
        "provider": "ollama",
        "model": "nonexistent_model_xyz",
        "agentic_enabled": True,
        "base_url": "http://127.0.0.1:11434",
    }
    stat = Termux_Sentinel.get_ai_runtime_status(cfg)
    assert isinstance(stat, dict)
    assert "badge" in stat
    assert "model_in_storage" in stat
    # Since nonexistent_model_xyz is not in storage, model_in_storage must be False
    assert stat["model_in_storage"] is False


def test_copy_to_clipboard_empty():
    """Verify copying empty text fails safely."""
    assert hasattr(Termux_Sentinel, "copy_to_clipboard")
    ok, msg = Termux_Sentinel.copy_to_clipboard("")
    assert ok is False
    assert "Nothing to copy" in msg


def test_copy_to_clipboard_mock(monkeypatch):
    """Verify copy_to_clipboard with mocked clipboard command."""
    monkeypatch.setattr(
        Termux_Sentinel.shutil,
        "which",
        lambda cmd: True if cmd == "termux-clipboard-set" else False,
    )

    class FakeProcess:
        returncode = 0

        def communicate(self, input=None, timeout=None):
            return b"", b""

    monkeypatch.setattr(
        Termux_Sentinel.subprocess, "Popen", lambda *args, **kwargs: FakeProcess()
    )
    ok, msg = Termux_Sentinel.copy_to_clipboard("Test copy data")
    assert ok is True
    assert "termux-clipboard-set" in msg


def test_export_chat_transcript(tmp_path, monkeypatch):
    """Verify exporting chat transcript writes markdown file with turns."""
    assert hasattr(Termux_Sentinel, "export_chat_transcript")
    monkeypatch.setattr(Termux_Sentinel, "TRANSCRIPTS_DIR", str(tmp_path))
    history = [
        {"role": "user", "content": "How much free storage do I have?"},
        {"role": "assistant", "content": "You have 10.3 GB free."},
    ]
    ok, path_out = Termux_Sentinel.export_chat_transcript(history, "test_session")
    assert ok is True
    assert path_out.endswith("test_session.md")
    p = Path(path_out)
    assert p.exists()
    content = p.read_text(encoding="utf-8")
    assert "Termux Sentinel AI Chat Transcript" in content
    assert "How much free storage do I have?" in content
    assert "You have 10.3 GB free." in content


def test_query_agentic_ai_with_history(monkeypatch):
    """Verify query_agentic_ai correctly formats multi-turn history for OpenAI-compatible providers."""
    assert hasattr(Termux_Sentinel, "query_agentic_ai")
    cfg = {
        "provider": "groq",
        "model": "llama-3.3-70b-versatile",
        "api_key": "test_groq_key",
        "base_url": "https://api.groq.com/openai/v1",
        "agentic_enabled": True,
    }
    monkeypatch.setattr(Termux_Sentinel, "load_ai_config", lambda: cfg)

    captured_payload = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        def read(self):
            return json.dumps(
                {
                    "choices": [
                        {"message": {"content": "Multi-turn answer received."}}
                    ]
                }
            ).encode("utf-8")

    def fake_urlopen(req, timeout=None):
        nonlocal captured_payload
        captured_payload = json.loads(req.data.decode("utf-8"))
        return FakeResponse()

    monkeypatch.setattr(Termux_Sentinel.urllib.request, "urlopen", fake_urlopen)

    history = [
        {"role": "user", "content": "Hello Sentinel"},
        {"role": "assistant", "content": "Hello! How can I assist you today?"},
    ]
    resp = Termux_Sentinel.query_agentic_ai("Check my disk space", history=history)
    assert resp == "Multi-turn answer received."
    assert "messages" in captured_payload
    # Should include system prompt, 2 history turns, and 1 current user prompt = 4 messages
    assert len(captured_payload["messages"]) == 4
    assert captured_payload["messages"][-1]["content"] == "Check my disk space"


def test_interactive_ai_chat_immediate_exit(monkeypatch, capsys):
    """Verify interactive_ai_chat terminates gracefully on /exit command."""
    assert hasattr(Termux_Sentinel, "interactive_ai_chat")
    inputs = iter(["/exit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
    Termux_Sentinel.interactive_ai_chat()
    out = capsys.readouterr().out
    assert "AI CHAT STUDIO" in out
    assert "Session closed" in out


def test_thinking_levels_configuration():
    """Verify thinking levels dictionary and set_thinking_level helper."""
    assert hasattr(Termux_Sentinel, "THINKING_LEVELS")
    for lvl in ("none", "low", "medium", "extra"):
        assert lvl in Termux_Sentinel.THINKING_LEVELS
        assert "prompt" in Termux_Sentinel.THINKING_LEVELS[lvl]
        assert "name" in Termux_Sentinel.THINKING_LEVELS[lvl]

    ok, name = Termux_Sentinel.set_thinking_level("none")
    assert ok is True
    assert "No Thinking" in name

    ok_alias, name_alias = Termux_Sentinel.set_thinking_level("default")
    assert ok_alias is True
    assert "Low Thinking" in name_alias

    ok_bad, _ = Termux_Sentinel.set_thinking_level("invalid_level_xyz")
    assert ok_bad is False


def test_format_thinking_response_none_strips_think():
    """Verify 'none' thinking level strips <think> reasoning blocks completely."""
    raw = "<think>\nThinking deeply about system storage...\n</think>\nHere is the answer."
    clean = Termux_Sentinel.format_thinking_response(raw, "none")
    assert clean == "Here is the answer."
    assert "<think>" not in clean


def test_format_thinking_response_low_compact():
    """Verify 'low' thinking level condenses reasoning into a 1-line badge."""
    raw = "<think>\nAnalyzing disk partitions\nChecking inodes\n</think>\nDisk is healthy."
    clean = Termux_Sentinel.format_thinking_response(raw, "low")
    assert "💭 [Analyzing disk partitions]" in clean
    assert "Disk is healthy." in clean
    assert "<think>" not in clean


def test_format_thinking_response_medium_and_extra_boxed():
    """Verify 'medium' and 'extra' format reasoning into a structured box."""
    raw = "<think>\nStep 1: Check root\nStep 2: Check cache\n</think>\nFound 2GB bloat."
    clean = Termux_Sentinel.format_thinking_response(raw, "medium")
    assert "REASONING (MEDIUM)" in clean
    assert "Step 1: Check root" in clean
    assert "Found 2GB bloat." in clean


def test_persistent_session_lifecycle(tmp_path, monkeypatch):
    """Verify creation, persistence, listing, and switching of multi-session chat memory."""
    fake_sessions_dir = tmp_path / "sessions"
    fake_active_file = fake_sessions_dir / "active_session.json"
    monkeypatch.setattr(Termux_Sentinel, "SESSIONS_DIR", str(fake_sessions_dir))
    monkeypatch.setattr(Termux_Sentinel, "ACTIVE_SESSION_FILE", str(fake_active_file))

    # 1. Create fresh session
    sess = Termux_Sentinel.create_new_session("System Optimization Session")
    assert sess["title"] == "System Optimization Session"
    assert fake_active_file.exists()

    # 2. Append conversation turn & save
    sess["history"].append({"role": "user", "content": "How to free RAM?"})
    sess["history"].append({"role": "assistant", "content": "Kill rogue daemons."})
    Termux_Sentinel.save_active_session(sess)

    # 3. Reload active session - should never forget past turns
    reloaded = Termux_Sentinel.load_active_session()
    assert len(reloaded["history"]) == 2
    assert reloaded["history"][0]["content"] == "How to free RAM?"

    # 4. Create second session
    sess2 = Termux_Sentinel.create_new_session("Docker Daemon Debugging")
    assert sess2["title"] == "Docker Daemon Debugging"

    # 5. List sessions
    all_sess = Termux_Sentinel.list_saved_sessions()
    assert len(all_sess) >= 2

    # 6. Switch back to first session
    ok, switched = Termux_Sentinel.load_session_by_id(sess["session_id"])
    assert ok is True
    assert switched["title"] == "System Optimization Session"
    assert len(switched["history"]) == 2
