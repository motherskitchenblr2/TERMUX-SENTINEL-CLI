#!/data/data/com.termux/files/usr/bin/python3
"""
================================================================================
 Termux_Sentinel.py
 Next-Gen Storage Sentinel, Rogue Bot Detector, Daemon Monitor & System Auditor
 Device: Realme 12 Pro+ | Android Termux & Ubuntu proot-distro
 Design: 3D Embossed Cyber Intro, Neon Glowing Borders, Dedicated Shield Vault
================================================================================
"""

import json
import os
import re
import shlex
import shutil
import signal
import subprocess  # nosec B404
import sys
import textwrap
import time
import traceback
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

# ==============================================================================
# NEON GLOW & DARK CHARCOAL COLOR PALETTE (256-Color ANSI)
# ==============================================================================
BG_CHARCOAL = "\033[48;5;234m"
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_DIM = "\033[2m"

# Brightest Neon Color Hierarchy
NEON_CYAN = "\033[38;5;51m"
NEON_GREEN = "\033[38;5;46m"
NEON_RED = "\033[38;5;196m"
NEON_PINK = "\033[38;5;201m"
NEON_YELLOW = "\033[38;5;226m"
NEON_ORANGE = "\033[38;5;208m"
NEON_PURPLE = "\033[38;5;141m"
NEON_BLUE = "\033[38;5;39m"
BRIGHT_WHITE = "\033[38;5;231m"
TEXT_MUTED = "\033[38;5;245m"

# High-contrast action badges
BADGE_RED = f"{C_BOLD}\033[48;5;196m\033[38;5;231m"
BADGE_GREEN = f"{C_BOLD}\033[48;5;46m\033[38;5;232m"
BADGE_CYAN = f"{C_BOLD}\033[48;5;51m\033[38;5;232m"
BADGE_YELLOW = f"{C_BOLD}\033[48;5;226m\033[38;5;232m"
BADGE_BLUE = f"{C_BOLD}\033[48;5;39m\033[38;5;231m"

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

IS_WINDOWS = sys.platform == "win32"
IS_TERMUX = (
    os.path.exists("/data/data/com.termux/files/usr/bin")
    or "TERMUX_VERSION" in os.environ
)

HOME_DIR = os.path.expanduser("~")
if IS_WINDOWS:
    _appdata = os.environ.get("APPDATA") or os.path.join(HOME_DIR, "AppData", "Roaming")
    VAULT_DIR = os.path.join(_appdata, "termux_sentinel")
else:
    VAULT_DIR = os.path.join(HOME_DIR, ".config", "termux_sentinel")
VAULT_FILE = os.path.join(VAULT_DIR, "vault.json")
CRASH_LOG_FILE = os.path.join(VAULT_DIR, "crash.log")
AI_CONFIG_FILE = os.path.join(VAULT_DIR, "ai_config.json")
TRANSCRIPTS_DIR = os.path.join(VAULT_DIR, "transcripts")
SESSIONS_DIR = os.path.join(VAULT_DIR, "sessions")
ACTIVE_SESSION_FILE = os.path.join(SESSIONS_DIR, "active_session.json")
UBUNTU_ROOT = (
    "/data/data/com.termux/files/usr/var/lib/proot-distro/containers/ubuntu/rootfs"
    if IS_TERMUX
    else "/"
)


def init_windows_terminal():
    """Enables ANSI escape sequence processing in legacy Windows consoles."""
    if IS_WINDOWS:
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        except Exception:
            pass


init_windows_terminal()

# Core hardcoded safety keywords that can NEVER be touched or bypassed
CORE_SAFETY_KEYWORDS = [
    "important_documents",
    "documents",
    "protected_workspace",
    "cloud_backup",
    "remote_backup",
    "desktop",
]

DEFAULT_VAULT_ITEMS = [
    {
        "id": 1,
        "name": "Important Documents & Media",
        "pattern": "Important_Documents",
        "type": "System Scope",
        "locked": True,
        "date_added": "Default Core Shield",
    },
    {
        "id": 2,
        "name": "Personal Documents & Data",
        "pattern": "documents",
        "type": "Storage Scope",
        "locked": True,
        "date_added": "Default Core Shield",
    },
    {
        "id": 3,
        "name": "Protected Workspace",
        "pattern": "Protected_Workspace",
        "type": "Active Workspace",
        "locked": True,
        "date_added": "Default Core Shield",
    },
    {
        "id": 4,
        "name": "Primary Cloud Backup Target",
        "pattern": "Cloud_Backup",
        "type": "Cloud Target",
        "locked": True,
        "date_added": "Default Core Shield",
    },
    {
        "id": 5,
        "name": "Secondary Cloud Target",
        "pattern": "Remote_Backup",
        "type": "Cloud Target",
        "locked": True,
        "date_added": "Default Core Shield",
    },
    {
        "id": 6,
        "name": "Desktop & Work Files",
        "pattern": "Desktop",
        "type": "Desktop Scope",
        "locked": True,
        "date_added": "Default Core Shield",
    },
]


# ==============================================================================
# PRESERVATION VAULT STORAGE & LOGIC ENGINE
# ==============================================================================
def load_vault():
    """Loads preserved items from vault.json, auto-seeding defaults if needed with self-healing recovery."""
    if not os.path.exists(VAULT_FILE):
        os.makedirs(VAULT_DIR, exist_ok=True)
        local_template = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "vault.json"
        )
        if os.path.exists(local_template) and local_template != VAULT_FILE:
            try:
                shutil.copy2(local_template, VAULT_FILE)
            except Exception:
                pass
        if not os.path.exists(VAULT_FILE):
            save_vault(DEFAULT_VAULT_ITEMS)
            return list(DEFAULT_VAULT_ITEMS)
    try:
        with open(VAULT_FILE, encoding="utf-8") as vault_file:
            data = json.load(vault_file)
            if isinstance(data, list):
                # Ensure core items are present
                existing_patterns = {
                    it.get("pattern", "").lower() for it in data if isinstance(it, dict)
                }
                for def_item in DEFAULT_VAULT_ITEMS:
                    if def_item["pattern"].lower() not in existing_patterns:
                        data.append(def_item)
                return data
            if isinstance(data, dict) and "items" in data:
                return data["items"]
            return list(DEFAULT_VAULT_ITEMS)
    except Exception:
        # Self-healing on corrupted JSON or I/O failure
        try:
            corrupt_bkp = VAULT_FILE + f".corrupt.{int(time.time())}"
            shutil.copy2(VAULT_FILE, corrupt_bkp)
        except Exception:
            pass
        save_vault(DEFAULT_VAULT_ITEMS)
        return list(DEFAULT_VAULT_ITEMS)


def save_vault(items):
    """Saves vault items safely to disk using atomic rename to prevent corruption."""
    try:
        os.makedirs(VAULT_DIR, exist_ok=True)
        tmp_file = VAULT_FILE + f".tmp.{os.getpid()}"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_file, VAULT_FILE)
    except Exception:
        try:
            with open(VAULT_FILE, "w", encoding="utf-8") as f:
                json.dump(items, f, indent=2)
        except (OSError, ValueError):
            pass


def add_to_vault(name, pattern, item_type="User Shield"):
    """Adds a new pattern/path to the Preservation Vault."""
    if not pattern:
        return False, "Pattern cannot be empty"
    items = load_vault()
    pat_lower = str(pattern).strip().lower()
    for it in items:
        if it.get("pattern", "").strip().lower() == pat_lower:
            return False, f"Already protected in Vault as '{it.get('name')}'"
    next_id = max([it.get("id", 0) for it in items] + [0]) + 1
    new_item = {
        "id": next_id,
        "name": name.strip(),
        "pattern": pattern.strip(),
        "type": item_type,
        "locked": False,
        "date_added": time.strftime("%Y-%m-%d %H:%M"),
    }
    items.append(new_item)
    save_vault(items)
    return True, new_item


def remove_from_vault(item_id):
    """Removes a user-defined shield from the Vault (locked items are immune)."""
    items = load_vault()
    target = None
    for it in items:
        if it.get("id") == item_id:
            target = it
            break
    if not target:
        return False, "Shield item not found in Vault"
    if target.get("locked"):
        return (
            False,
            "Core system shields (Important Documents & Workspaces) are permanently locked for safety!",
        )
    items = [it for it in items if it.get("id") != item_id]
    save_vault(items)
    return True, target


def is_protected(path):
    """Global check: returns True if path matches core safety or any vault entry."""
    if not path:
        return False
    path_str = str(path).lower()
    for kw in CORE_SAFETY_KEYWORDS:
        if kw in path_str:
            return True
    try:
        items = load_vault()
        for it in items:
            pat = it.get("pattern", "").lower()
            if pat and pat in path_str:
                return True
    except (OSError, ValueError, TypeError):
        return False
    return False


# ==============================================================================
# TERMINAL GEOMETRY & FORMATTING HELPERS (Responsive Mobile to Wide Desktop)
# ==============================================================================
def get_term_cols(max_cols=120):
    """Returns responsive terminal columns adapted for mobile portrait (min 44) or wide desktop (up to 120)."""
    try:
        cols = shutil.get_terminal_size((44, 24)).columns
        return min(max(cols, 44), max_cols)
    except Exception:
        return 44


def char_width(ch):
    if ch in ("\ufe0e", "\ufe0f"):
        return 0
    w = unicodedata.east_asian_width(ch)
    if w in ("W", "F"):
        return 2
    if 0x1F300 <= ord(ch) <= 0x1FAFF:
        return 2
    return 1


def visible_len(s):
    """Calculates visible character length disregarding ANSI escape sequences and accounting for wide glyphs."""
    cleaned = ANSI_RE.sub("", s)
    return sum(char_width(ch) for ch in cleaned)


def make_box_row(content, border_color=NEON_CYAN, cols=44):
    """Encloses content inside a double-border neon box row strictly clamped to cols."""
    inner_w = cols - 4
    v_len = visible_len(content)
    pad = max(0, inner_w - v_len)
    return f"{border_color}║{C_RESET} {content}{' ' * pad} {border_color}║{C_RESET}"


# ==============================================================================
# 3D EMBOSSED ASCII BANNER & NEON INTRO ANIMATION
# ==============================================================================
# Individual letter components (T:7, E:5, R:5, M:8, U:7, X:6 -> total 38 chars)
LETTER_PARTS_T = [" _____ ", "|_   _|", "  | |  ", "  |_|  "]
LETTER_PARTS_E = [" ___ ", "| __|", "| _| ", "|___|"]
LETTER_PARTS_R = [" ___ ", "| _ \\", "|   /", "|_|_\\"]
LETTER_PARTS_M = [" __  __ ", "|  \\/  |", "| |\\/| |", "|_|  |_|"]
LETTER_PARTS_U = [" _   _ ", "| | | |", "| |_| |", " \\___/ "]
LETTER_PARTS_X = ["__  __", "\\ \\/ /", " >  < ", "/_/\\_\\"]

COLOR_T = "\033[38;5;51;1m"  # Electric Neon Cyan
COLOR_E = "\033[38;5;206;1m"  # Neon Hot Pink
COLOR_R = "\033[38;5;226;1m"  # Luminous Cyber Yellow
COLOR_M = "\033[38;5;208;1m"  # Vibrant Neon Orange
COLOR_U = "\033[38;5;48;1m"  # Cyber Emerald Green
COLOR_X = "\033[38;5;141;1m"  # Royal Neon Purple


def render_3d_banner(border_color=NEON_CYAN, title_color=None, colorful=True):
    """Renders the responsive Cyber Termux-Sentinel banner with shape-lock guarantee."""
    target_cols = get_term_cols()
    c = target_cols
    inner = c - 2
    pad_left = max(0, (inner - 38) // 2)
    pad_right = max(0, inner - 38 - pad_left)

    top = f"{border_color}╔" + "═" * inner + f"╗{C_RESET}"
    bot = f"{border_color}╚" + "═" * inner + f"╝{C_RESET}"
    bchar = f"{border_color}║{C_RESET}"
    lines = [top]

    for row in range(4):
        if colorful:
            letter_block = (
                f"{COLOR_T}{LETTER_PARTS_T[row]}{C_RESET}"
                + f"{COLOR_E}{LETTER_PARTS_E[row]}{C_RESET}"
                + f"{COLOR_R}{LETTER_PARTS_R[row]}{C_RESET}"
                + f"{COLOR_M}{LETTER_PARTS_M[row]}{C_RESET}"
                + f"{COLOR_U}{LETTER_PARTS_U[row]}{C_RESET}"
                + f"{COLOR_X}{LETTER_PARTS_X[row]}{C_RESET}"
            )
        else:
            t_col = title_color or BRIGHT_WHITE
            letter_block = (
                f"{C_BOLD}{t_col}"
                + LETTER_PARTS_T[row]
                + LETTER_PARTS_E[row]
                + LETTER_PARTS_R[row]
                + LETTER_PARTS_M[row]
                + LETTER_PARTS_U[row]
                + LETTER_PARTS_X[row]
                + f"{C_RESET}"
            )
        content = (" " * pad_left) + letter_block + (" " * pad_right)
        lines.append(f"{bchar}{content}{bchar}")

    # Neon gradient divider line
    div_dash_count = max(0, inner - 2)
    left_cnt = div_dash_count // 4
    right_cnt = div_dash_count // 4
    mid_cnt = div_dash_count - left_cnt - right_cnt
    div_content = (
        " "
        + "\033[38;5;141m"
        + ("─" * left_cnt)
        + "\033[38;5;206m"
        + ("─" * mid_cnt)
        + "\033[38;5;51m"
        + ("─" * right_cnt)
        + f"{C_RESET} "
    )
    lines.append(f"{bchar}{div_content}{bchar}")

    # Luminous Sentinel subtitle with gradient fade badges
    sub_core = (
        "\033[38;5;45m░▒▓\033[38;5;51m██████"
        + f"{C_RESET} \033[1;93mS E N T I N E L{C_RESET} \033[38;5;206m██████\033[38;5;141m▓▒░{C_RESET}"
    )
    sub_pad_l = max(0, (inner - 35) // 2)
    sub_pad_r = max(0, inner - 35 - sub_pad_l)
    sub_content = (" " * sub_pad_l) + sub_core + (" " * sub_pad_r)
    lines.append(f"{bchar}{sub_content}{bchar}")
    lines.append(bot)
    return "\n".join(lines)


def print_large_header():
    """Prints the 3D Embossed Banner as the master application header."""
    print(render_3d_banner(NEON_CYAN, colorful=True))


def clear_screen():
    """Terminal clear using ANSI escape sequences (safe, zero-fork)."""
    sys.stdout.write("\033[H\033[2J")
    sys.stdout.flush()


def animate_boot_glow():
    """High-animation 3D Embossed Startup Intro with circulating neon border."""
    clear_screen()
    frames = [
        (NEON_CYAN, "✦ INITIALIZING 3D NEON CORE...", 0.16),
        (NEON_PINK, "⚡ CALIBRATING STORAGE TELEMETRY...", 0.16),
        (NEON_PURPLE, "🛡️ MOUNTING PRESERVATION VAULT...", 0.18),
        (NEON_GREEN, "🔍 PROBING PROOT DISTRO & DAEMONS...", 0.18),
        (NEON_CYAN, "🚀 SENTINEL DEFENSE MATRIX ONLINE!", 0.20),
    ]
    for b_color, msg, delay in frames:
        clear_screen()
        print("\n" + render_3d_banner(border_color=b_color, colorful=True))
        print(
            f"\n {BG_CHARCOAL} {C_BOLD}{b_color}[ ✦ ]{C_RESET} {BRIGHT_WHITE}{msg:<34}{C_RESET}"
        )
        time.sleep(delay)
    time.sleep(0.12)


# ==============================================================================
# ANIMATION ENGINE (Red for deletions, Green for preserves/updates)
# ==============================================================================
SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


def animate_step(phase, message, color=NEON_CYAN, duration=0.6):
    """Real-time animated live status indicator."""
    steps = int(duration / 0.05)
    for i in range(steps):
        spin = SPINNER_FRAMES[i % len(SPINNER_FRAMES)]
        sys.stdout.write(
            f"\r  {BG_CHARCOAL}{C_BOLD}{color}[ {spin} {phase} ]{C_RESET} {BRIGHT_WHITE}{message[:32]}{C_RESET}   "
        )
        sys.stdout.flush()
        time.sleep(0.05)
    sys.stdout.write(
        f"\r  {BG_CHARCOAL}{C_BOLD}{color}[ ✓ {phase} ]{C_RESET} {BRIGHT_WHITE}{message[:32]}{C_RESET}\n"
    )
    sys.stdout.flush()


def animate_delete(message, duration=0.5):
    """Intense Red animated deletion feedback."""
    animate_step("DELETING", message, color=NEON_RED, duration=duration)


def animate_terminate(message, duration=0.5):
    """Intense Red animated process termination feedback."""
    animate_step("TERMINATING", message, color=NEON_RED, duration=duration)


def animate_safe(phase, message, duration=0.5):
    """Luminous Green animated success feedback."""
    animate_step(phase, message, color=NEON_GREEN, duration=duration)


# ==============================================================================
# STORAGE & DISK HELPERS
# ==============================================================================
def human_size(nbytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(nbytes) < 1024.0:
            return f"{nbytes:3.1f} {unit}"
        nbytes /= 1024.0
    return f"{nbytes:.1f} PB"


def get_dir_size(path):
    if not os.path.exists(path):
        return 0
    try:
        du_path = shutil.which("du") or "/usr/bin/du"
        out = subprocess.check_output(  # nosec B603
            [du_path, "-sk", path], stderr=subprocess.DEVNULL, timeout=1.8
        )
        return int(out.split()[0]) * 1024
    except Exception:
        try:
            sz = 0
            for entry in os.scandir(path):
                if entry.is_file(follow_symlinks=False):
                    sz += entry.stat().st_size
            return sz
        except Exception:
            return 0


def get_disk_usage():
    """Cross-platform disk usage retrieval using standard library shutil."""
    try:
        usage = shutil.disk_usage(HOME_DIR)
        total = usage.total
        free = usage.free
        used = usage.used
        pct = (used / total) * 100 if total > 0 else 0
        return human_size(used), human_size(total), human_size(free), f"{pct:.1f}%"
    except Exception:
        return "N/A", "N/A", "N/A", "N/A"


def check_storage_threshold(min_gb=5.0):
    """Returns (is_critical, free_gb) based on available disk space."""
    try:
        usage = shutil.disk_usage(HOME_DIR)
        free_gb = usage.free / (1024**3)
        return free_gb < min_gb, round(free_gb, 2)
    except Exception:
        return False, 999.0


def get_device_name():
    """Detects current mobile device brand, Windows PC, or Linux distro dynamically."""
    if IS_WINDOWS:
        try:
            import platform

            rel = platform.release()
            return f"WINDOWS {rel} WORKSTATION"
        except Exception:
            return "WINDOWS PC"

    if IS_TERMUX:
        try:
            getprop_bin = shutil.which("getprop") or "/system/bin/getprop"
            brand = (
                subprocess.check_output(  # nosec B603
                    [getprop_bin, "ro.product.brand"],
                    text=True,
                    stderr=subprocess.DEVNULL,
                )
                .strip()
                .upper()
            )
            model = (
                subprocess.check_output(  # nosec B603
                    [getprop_bin, "ro.product.model"],
                    text=True,
                    stderr=subprocess.DEVNULL,
                )
                .strip()
                .upper()
            )
            if "REALME" in brand or "RMX" in model:
                return "REALME 12 PRO+"
            elif "NOTHING" in brand or "CMF" in brand or "A015" in model:
                return "CMF PHONE 1 (NOTHING)"
            if brand:
                return f"{brand} {model}"[:24]
        except (OSError, subprocess.SubprocessError):
            pass
        return "TERMUX SENTINEL"

    # Standard Linux / Ubuntu
    try:
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        val = line.split("=", 1)[1].strip().strip('"')
                        return val.upper()[:24]
    except Exception:
        pass

    return sys.platform.upper() + " SENTINEL"


# ==============================================================================
# AI CONFIGURATION & REAL-TIME RUNTIME TELEMETRY
# ==============================================================================
DEFAULT_AI_CONFIG = {
    "provider": "ollama",
    "provider_name": "Ollama (Local Offline)",
    "base_url": "http://127.0.0.1:11434",
    "api_key": "",
    "model": "qwen2.5:3b",
    "agentic_enabled": False,
    "thinking_level": "low",
}

THINKING_LEVELS = {
    "none": {
        "id": "none",
        "name": "No Thinking",
        "badge": "NO THINKING",
        "desc": "Strips thinking blocks; outputs answers immediately without reasoning delay.",
        "prompt": "Do NOT output internal monologue or <think> tags. Provide the direct answer immediately.",
        "reasoning_effort": "low",
        "temperature": 0.2,
        "max_tokens": 600,
    },
    "low": {
        "id": "low",
        "name": "Low Thinking",
        "badge": "LOW (DEFAULT)",
        "desc": "Minimal concise thoughts (1-2 points); optimal for Android battery and speed.",
        "prompt": "Keep any reasoning ultra-concise (maximum 1-2 brief bullet points) before giving the direct answer.",
        "reasoning_effort": "low",
        "temperature": 0.3,
        "max_tokens": 800,
    },
    "medium": {
        "id": "medium",
        "name": "Medium Thinking",
        "badge": "MEDIUM",
        "desc": "Balanced reasoning for complex troubleshooting and multi-step tasks.",
        "prompt": "Reason through the problem in a clear, concise manner before giving the final solution.",
        "reasoning_effort": "medium",
        "temperature": 0.4,
        "max_tokens": 1200,
    },
    "extra": {
        "id": "extra",
        "name": "Extra Thinking",
        "badge": "EXTRA DEEP",
        "desc": "Deep chain-of-thought analysis for complex architectural or debugging challenges.",
        "prompt": "Perform thorough, comprehensive step-by-step chain-of-thought reasoning before concluding.",
        "reasoning_effort": "high",
        "temperature": 0.6,
        "max_tokens": 2048,
    },
}


def set_thinking_level(level_id):
    """Sets active thinking level and saves to ai_config.json."""
    level_id = str(level_id).lower().strip()
    alias_map = {
        "0": "none",
        "off": "none",
        "no": "none",
        "1": "low",
        "quick": "low",
        "fast": "low",
        "default": "low",
        "2": "medium",
        "med": "medium",
        "balanced": "medium",
        "3": "extra",
        "high": "extra",
        "deep": "extra",
    }
    level_id = alias_map.get(level_id, level_id)
    if level_id not in THINKING_LEVELS:
        return (
            False,
            f"Invalid level '{level_id}'. Choices: none, low, medium, extra.",
        )
    cfg = load_ai_config()
    cfg["thinking_level"] = level_id
    save_ai_config(cfg)
    return True, THINKING_LEVELS[level_id]["name"]


def format_thinking_response(raw_resp, thinking_level="low"):
    """Formats or strips <think>...</think> reasoning blocks based on active thinking level."""
    if not raw_resp:
        return ""

    lvl = thinking_level.lower().strip() if thinking_level in THINKING_LEVELS else "low"
    has_think = bool(re.search(r"<think>(.*?)</think>", raw_resp, flags=re.DOTALL))

    if not has_think:
        return raw_resp.strip()

    if lvl == "none":
        clean = re.sub(r"<think>.*?</think>", "", raw_resp, flags=re.DOTALL).strip()
        return clean if clean else raw_resp.strip()

    elif lvl == "low":
        match = re.search(r"<think>(.*?)</think>", raw_resp, flags=re.DOTALL)
        answer = re.sub(r"<think>.*?</think>", "", raw_resp, flags=re.DOTALL).strip()
        thoughts = match.group(1).strip() if match else ""
        first_line = (
            thoughts.splitlines()[0].strip()
            if thoughts
            else "Quick reasoning completed"
        )
        if len(first_line) > 65:
            first_line = first_line[:62] + "..."
        prefix = f"{TEXT_MUTED}💭 [{first_line}]{C_RESET}\n"
        return f"{prefix}\n{answer}" if answer else thoughts

    else:
        match = re.search(r"<think>(.*?)</think>", raw_resp, flags=re.DOTALL)
        answer = re.sub(r"<think>.*?</think>", "", raw_resp, flags=re.DOTALL).strip()
        thoughts = match.group(1).strip() if match else ""
        t_lines = [f"{TEXT_MUTED}│  {tl}{C_RESET}" for tl in thoughts.splitlines()[:25]]
        if len(thoughts.splitlines()) > 25:
            t_lines.append(
                f"{TEXT_MUTED}│  ... [{len(thoughts.splitlines()) - 25} lines truncated]{C_RESET}"
            )
        header = f"{TEXT_MUTED}╭─ 💭 REASONING ({lvl.upper()}) ─────────────────────────{C_RESET}"
        footer = f"{TEXT_MUTED}╰──────────────────────────────────────────────────────────{C_RESET}"
        box = "\n".join([header] + t_lines + [footer])
        return f"{box}\n\n{answer}" if answer else box


def init_sessions_dir():
    """Ensures sessions directory exists."""
    os.makedirs(SESSIONS_DIR, exist_ok=True)


def create_new_session(title=None):
    """Initializes a new persistent chat session and sets it as active."""
    init_sessions_dir()
    cfg = load_ai_config()
    session_id = (
        f"sess_{time.strftime('%Y%m%d_%H%M%S')}_{int(time.time() * 1000) % 1000:03d}"
    )
    new_sess = {
        "session_id": session_id,
        "title": title or f"Session {time.strftime('%b %d, %H:%M')}",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "model": cfg.get("model", "qwen2.5:3b"),
        "provider": cfg.get("provider", "ollama"),
        "thinking_level": cfg.get("thinking_level", "low"),
        "history": [],
    }
    save_active_session(new_sess)
    return new_sess


def load_active_session():
    """Loads current active conversation session from disk, creating one if none exists."""
    init_sessions_dir()
    if os.path.exists(ACTIVE_SESSION_FILE):
        try:
            with open(ACTIVE_SESSION_FILE, encoding="utf-8") as f:
                data = json.load(f)
                if (
                    isinstance(data, dict)
                    and "history" in data
                    and "session_id" in data
                ):
                    return data
        except Exception:
            pass
    return create_new_session()


def save_active_session(session_data):
    """Saves session atomically both as active_session.json and archived under its session_id."""
    init_sessions_dir()
    if not isinstance(session_data, dict):
        return
    session_data["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    sess_id = session_data.get(
        "session_id",
        f"sess_{time.strftime('%Y%m%d_%H%M%S')}_{int(time.time() * 1000) % 1000:03d}",
    )
    archive_f = os.path.join(SESSIONS_DIR, f"{sess_id}.json")

    try:
        tmp_active = ACTIVE_SESSION_FILE + f".tmp.{os.getpid()}"
        with open(tmp_active, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_active, ACTIVE_SESSION_FILE)
    except Exception:
        pass

    try:
        tmp_archive = archive_f + f".tmp.{os.getpid()}"
        with open(tmp_archive, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_archive, archive_f)
    except Exception:
        pass


def list_saved_sessions():
    """Lists all saved chat sessions sorted by last updated timestamp."""
    init_sessions_dir()
    sessions = []
    if not os.path.exists(SESSIONS_DIR):
        return sessions
    for entry in os.scandir(SESSIONS_DIR):
        if (
            entry.is_file()
            and entry.name.startswith("sess_")
            and entry.name.endswith(".json")
        ):
            try:
                with open(entry.path, encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "session_id" in data:
                        sessions.append(data)
            except Exception:
                pass
    sessions.sort(key=lambda s: s.get("updated_at", ""), reverse=True)
    return sessions


def load_session_by_id(target):
    """Loads a specific session by session_id or 1-based index and sets it active."""
    sessions = list_saved_sessions()
    target_str = str(target).strip()
    selected_sess = None
    if target_str.isdigit():
        idx = int(target_str)
        if 1 <= idx <= len(sessions):
            selected_sess = sessions[idx - 1]
    if not selected_sess:
        for s in sessions:
            if (
                s.get("session_id") == target_str
                or s.get("title", "").lower() == target_str.lower()
            ):
                selected_sess = s
                break
    if not selected_sess:
        return False, f"Session '{target}' not found."
    save_active_session(selected_sess)
    return True, selected_sess


def delete_session_by_id(target):
    """Deletes a saved session from disk."""
    sessions = list_saved_sessions()
    target_str = str(target).strip()
    selected_sess = None
    if target_str.isdigit():
        idx = int(target_str)
        if 1 <= idx <= len(sessions):
            selected_sess = sessions[idx - 1]
    if not selected_sess:
        for s in sessions:
            if s.get("session_id") == target_str:
                selected_sess = s
                break
    if not selected_sess:
        return False, f"Session '{target}' not found."
    sid = selected_sess["session_id"]
    sess_f = os.path.join(SESSIONS_DIR, f"{sid}.json")
    try:
        if os.path.exists(sess_f):
            os.remove(sess_f)
    except Exception as e:
        return False, str(e)
    curr = load_active_session()
    if curr.get("session_id") == sid:
        create_new_session()
    return True, f"Session '{selected_sess.get('title', sid)}' deleted."


def load_ai_config():
    """Loads current AI engine configuration from disk."""
    if not os.path.exists(AI_CONFIG_FILE):
        return dict(DEFAULT_AI_CONFIG)
    try:
        with open(AI_CONFIG_FILE, encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return {**DEFAULT_AI_CONFIG, **data}
    except Exception:
        pass
    return dict(DEFAULT_AI_CONFIG)


def save_ai_config(cfg):
    """Saves AI configuration securely with restricted file permissions."""
    try:
        os.makedirs(VAULT_DIR, exist_ok=True)
        tmp_f = AI_CONFIG_FILE + f".tmp.{os.getpid()}"
        with open(tmp_f, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_f, AI_CONFIG_FILE)
        if not IS_WINDOWS and hasattr(os, "chmod"):
            try:
                os.chmod(AI_CONFIG_FILE, 0o600)
            except OSError:
                pass
    except Exception:
        pass


def toggle_agentic_mode():
    """Toggles Agentic AI mode ON/OFF."""
    cfg = load_ai_config()
    cfg["agentic_enabled"] = not cfg.get("agentic_enabled", False)
    save_ai_config(cfg)
    return cfg["agentic_enabled"]


def get_ollama_live_status(base_url="http://127.0.0.1:11434") -> dict:
    """Verifies live Ollama daemon connectivity and lists actual downloaded models in storage."""
    running = False
    pulled_models = []

    # 1. Probe live HTTP endpoint on base_url /api/tags
    try:
        req = urllib.request.Request(
            f"{base_url}/api/tags",
            headers={"User-Agent": "TermuxSentinel/2.0"},
        )
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            data = json.loads(resp.read().decode())
            running = True
            pulled_models = [
                m.get("name") for m in data.get("models", []) if m.get("name")
            ]
    except Exception:
        running = False

    # 2. Check fallback process list if daemon is running
    if not running:
        try:
            procs = get_user_processes()
            for _pid, cmd in procs:
                if "ollama serve" in cmd:
                    running = True
                    break
        except Exception:
            pass

    return {
        "running": running,
        "base_url": base_url,
        "pulled_models": pulled_models,
        "model_count": len(pulled_models),
    }


def get_ai_runtime_status(cfg=None) -> dict:
    """Returns real-time AI engine health, live daemon connectivity, and actual storage model presence."""
    if cfg is None:
        cfg = load_ai_config()

    is_agent = cfg.get("agentic_enabled", False)
    prov = cfg.get("provider", "ollama")
    model = cfg.get("model", "None")
    api_key = cfg.get("api_key", "")
    base_url = cfg.get("base_url", "http://127.0.0.1:11434")

    if not is_agent:
        return {
            "mode": "MANUAL",
            "badge": f"{TEXT_MUTED}[○ MANUAL MODE [g]]{C_RESET}",
            "summary": "Manual mode (Agentic AI disabled)",
            "model_in_storage": False,
            "daemon_live": False,
            "pulled_models": [],
        }

    if prov == "ollama":
        stat = get_ollama_live_status(base_url)
        daemon_live = stat["running"]
        pulled = stat["pulled_models"]

        # Check if configured model is in storage
        m_base = model.split(":")[0] if model else ""
        in_storage = any(
            model in pm or (m_base and m_base == pm.split(":")[0]) for pm in pulled
        )

        if not daemon_live:
            return {
                "mode": "DAEMON_OFFLINE",
                "badge": f"{BADGE_RED} OLLAMA STOPPED {C_RESET}",
                "summary": "Ollama daemon stopped. Launch via [o] or 'sentinel ai inspect'",
                "model_in_storage": False,
                "daemon_live": False,
                "pulled_models": pulled,
            }
        elif in_storage:
            return {
                "mode": "ONLINE",
                "badge": f"{BADGE_GREEN} ONLINE: {model[:16]} {C_RESET}",
                "summary": f"Live on {base_url} ({model} verified in local storage)",
                "model_in_storage": True,
                "daemon_live": True,
                "pulled_models": pulled,
            }
        elif pulled:
            return {
                "mode": "MODEL_NOT_FOUND",
                "badge": f"{BADGE_YELLOW} NOT IN STORAGE: {model[:12]} {C_RESET}",
                "summary": f"Daemon live, but '{model}' not downloaded. Pulled: {', '.join(pulled[:3])}",
                "model_in_storage": False,
                "daemon_live": True,
                "pulled_models": pulled,
            }
        else:
            return {
                "mode": "ZERO_MODELS",
                "badge": f"{BADGE_YELLOW} 0 MODELS IN STORAGE [o] {C_RESET}",
                "summary": f"Daemon live on {base_url}, but 0 models downloaded in storage. Press [o] to pull.",
                "model_in_storage": False,
                "daemon_live": True,
                "pulled_models": [],
            }
    else:
        # Cloud providers
        if not api_key:
            return {
                "mode": "NO_API_KEY",
                "badge": f"{BADGE_YELLOW} {prov.upper()}: NO KEY {C_RESET}",
                "summary": f"No API key configured. Run 'sentinel ai setup' to activate {prov.upper()}",
                "model_in_storage": True,
                "daemon_live": True,
                "pulled_models": [],
            }
        else:
            return {
                "mode": "ONLINE",
                "badge": f"{BADGE_GREEN} ONLINE: {model[:16]} {C_RESET}",
                "summary": f"Cloud model '{model}' active via {prov.upper()}",
                "model_in_storage": True,
                "daemon_live": True,
                "pulled_models": [],
            }


# ==============================================================================
# NEON BORDER UI CONTAINERS & HEADERS (Mobile & Wide-Screen Desktop Adaptive)
# ==============================================================================
def render_hud_box(_view_name="DASHBOARD"):
    """Responsive Neon Border HUD Box (Mobile Clamped to 44, Wide Grid on Desktop >= 80)."""
    cols = get_term_cols()
    used, _total, free, pct = get_disk_usage()
    vault_items = load_vault()
    vault_count = len(vault_items)
    dev_name = get_device_name()
    is_crit, free_gb = check_storage_threshold(min_gb=5.0)

    title = f"═ {dev_name} HUD "
    if visible_len(title) > cols - 6:
        title = "═ SENTINEL HUD "
    fill = max(0, cols - 2 - visible_len(title))
    top = f"{NEON_CYAN}╔{title}" + "═" * fill + f"╗{C_RESET}"
    bot = f"{NEON_CYAN}╚" + "═" * (cols - 2) + f"╝{C_RESET}"

    if cols >= 80:
        # Wide Screen Dual-Pane Grid
        mid_col = (cols - 3) // 2
        left_w = mid_col - 2
        right_w = cols - mid_col - 5

        row1_l = f"Storage: {NEON_YELLOW}{used}{C_RESET} / {NEON_GREEN}{free} Free{C_RESET} ({pct})"
        row1_r = f"Vault: {NEON_GREEN}{vault_count} Active Shields [v]{C_RESET}"
        pad_l1 = max(0, left_w - visible_len(row1_l))
        pad_r1 = max(0, right_w - visible_len(row1_r))
        grid_row1 = f"{NEON_CYAN}║{C_RESET} {row1_l}{' ' * pad_l1} {NEON_CYAN}║{C_RESET} {row1_r}{' ' * pad_r1} {NEON_CYAN}║{C_RESET}"

        status_lbl = (
            f"Status: {NEON_RED}CRITICAL SPACE ({free_gb} GB){C_RESET}"
            if is_crit
            else f"Status: {NEON_GREEN}SYSTEM HEALTH OPTIMAL{C_RESET}"
        )
        mode_lbl = f"Workstation: {NEON_CYAN}{dev_name}{C_RESET}"
        pad_l2 = max(0, left_w - visible_len(status_lbl))
        pad_r2 = max(0, right_w - visible_len(mode_lbl))
        grid_row2 = f"{NEON_CYAN}║{C_RESET} {status_lbl}{' ' * pad_l2} {NEON_CYAN}║{C_RESET} {mode_lbl}{' ' * pad_r2} {NEON_CYAN}║{C_RESET}"

        ai_cfg = load_ai_config()
        ai_stat = get_ai_runtime_status(ai_cfg)
        ai_lbl = f"AI Agent: {ai_stat['badge']}"
        if ai_cfg.get("provider") == "ollama":
            if ai_stat["daemon_live"]:
                m_count = len(ai_stat.get("pulled_models", []))
                engine_lbl = f"Ollama: {NEON_GREEN}● LIVE (:11434 | {m_count} in storage) [o]{C_RESET}"
            else:
                engine_lbl = f"Ollama: {NEON_RED}○ STOPPED{C_RESET} [o]"
        else:
            engine_lbl = f"AI Provider: {NEON_CYAN}{ai_cfg.get('provider_name', 'Cloud')[:18]} [o]{C_RESET}"
        pad_l3 = max(0, left_w - visible_len(ai_lbl))
        pad_r3 = max(0, right_w - visible_len(engine_lbl))
        grid_row3 = f"{NEON_CYAN}║{C_RESET} {ai_lbl}{' ' * pad_l3} {NEON_CYAN}║{C_RESET} {engine_lbl}{' ' * pad_r3} {NEON_CYAN}║{C_RESET}"

        print(top)
        print(grid_row1)
        print(grid_row2)
        print(grid_row3)
        print(bot)
    else:
        # Mobile Compact Stack
        r1 = f"Used: {NEON_YELLOW}{used}{C_RESET} | Free: {NEON_GREEN}{free}{C_RESET} ({pct})"
        r2 = f"Vault: {NEON_GREEN}{vault_count} Active Shields [v]{C_RESET}"
        ai_cfg = load_ai_config()
        ai_stat = get_ai_runtime_status(ai_cfg)
        r3 = f"AI: {ai_stat['badge']} [g]"
        if ai_cfg.get("provider") == "ollama":
            if ai_stat["daemon_live"]:
                m_cnt = len(ai_stat.get("pulled_models", []))
                r4 = f"Ollama: {NEON_GREEN}● LIVE 127.0.0.1:11434{C_RESET} ({m_cnt} models in storage)"
            else:
                r4 = f"Ollama: {NEON_RED}○ STOPPED{C_RESET} [sentinel ai inspect]"
        else:
            r4 = f"Provider: {NEON_CYAN}{ai_cfg.get('provider_name', 'Cloud')}{C_RESET}"

        print(top)
        print(make_box_row(r1, border_color=NEON_CYAN, cols=cols))
        print(make_box_row(r2, border_color=NEON_CYAN, cols=cols))
        print(make_box_row(r3, border_color=NEON_CYAN, cols=cols))
        print(make_box_row(r4, border_color=NEON_CYAN, cols=cols))
        if is_crit:
            r_warn = f"{NEON_RED}⚠️ CRITICAL SPACE: {free_gb} GB FREE! [sentinel clean -y]{C_RESET}"
            print(make_box_row(r_warn, border_color=NEON_RED, cols=cols))
        print(bot)


def kill_process_pid(pid):
    """Cross-platform safe process termination (Windows taskkill vs POSIX kill)."""
    try:
        p_int = int(pid)
        if IS_WINDOWS:
            subprocess.run(
                ["taskkill", "/F", "/PID", str(p_int)],
                check=False,
                stderr=subprocess.DEVNULL,
            )
            return True
        else:
            os.kill(p_int, signal.SIGTERM)
            time.sleep(0.2)
            os.kill(p_int, signal.SIGKILL)
            return True
    except Exception:
        return False


def print_section_h2(title, color=NEON_CYAN):
    cols = get_term_cols()
    inner_w = cols - 4
    t_trunc = title[:inner_w]
    print(f"\n{C_BOLD}{color}╔═" + "═" * (cols - 4) + "╗" + C_RESET)
    print(f"{C_BOLD}{color}║ {t_trunc:<{inner_w}} ║{C_RESET}")
    print(f"{C_BOLD}{color}╚═" + "═" * (cols - 4) + "╝" + C_RESET)


def print_divider_h3(title, color=NEON_PURPLE):
    cols = get_term_cols()
    fill = max(2, cols - len(title) - 6)
    print(f"\n{C_BOLD}{color}━━▶ {title} " + "━" * fill + C_RESET)


# ==============================================================================
# DATA TARGET DEFINITIONS (FILTERED BY PRESERVATION VAULT)
# ==============================================================================
def define_cleaning_targets():
    """Returns storage targets with smart recommendations, omitting Vault items."""
    raw_targets = [
        {
            "id": 1,
            "category": "clean",
            "name": "Ubuntu /tmp temporary files",
            "paths": [os.path.join(UBUNTU_ROOT, "tmp")],
            "action_type": "empty_dir",
            "recommendation": "extra files (Safe to delete)",
            "rec_type": "safe",
            "default": True,
        },
        {
            "id": 2,
            "category": "clean",
            "name": "Termux uv/pnpm/skills cache",
            "paths": [
                os.path.join(HOME_DIR, ".cache", "uv"),
                os.path.join(HOME_DIR, ".cache", "pnpm"),
                os.path.join(HOME_DIR, ".cache", "skills-cache"),
            ],
            "action_type": "remove_paths",
            "recommendation": "cache files (Safe to delete)",
            "rec_type": "safe",
            "default": True,
        },
        {
            "id": 3,
            "category": "clean",
            "name": "Termux npm package cache",
            "paths": [os.path.join(HOME_DIR, ".npm", "_cacache")],
            "action_type": "remove_paths",
            "recommendation": "cache files (Safe to delete)",
            "rec_type": "safe",
            "default": True,
        },
        {
            "id": 4,
            "category": "clean",
            "name": "Ubuntu dev & Playwright cache",
            "paths": [os.path.join(UBUNTU_ROOT, "root", ".cache")],
            "action_type": "empty_dir",
            "recommendation": "cache files (Safe to delete)",
            "rec_type": "safe",
            "default": True,
        },
        {
            "id": 5,
            "category": "clean",
            "name": "Ubuntu npm package cache",
            "paths": [os.path.join(UBUNTU_ROOT, "root", ".npm", "_cacache")],
            "action_type": "remove_paths",
            "recommendation": "cache files (Safe to delete)",
            "rec_type": "safe",
            "default": True,
        },
        {
            "id": 6,
            "category": "clean",
            "name": "Modex duplicate & node_modules",
            "paths": [
                os.path.join(HOME_DIR, "Modex-Sandbox-", "Modex-Sandbox-"),
                os.path.join(HOME_DIR, "Modex-Sandbox-", "node_modules"),
            ],
            "action_type": "remove_paths",
            "recommendation": "extra clone (Safe to delete)",
            "rec_type": "safe",
            "default": True,
        },
        {
            "id": 7,
            "category": "clean",
            "name": "AI Agent task logs (>7d old)",
            "paths": [
                os.path.join(HOME_DIR, ".composio"),
                os.path.join(
                    HOME_DIR,
                    ".gemini",
                    "antigravity-cli",
                    "brain",
                    "*",
                    ".system_generated",
                    "tasks",
                ),
            ],
            "action_type": "remove_paths",
            "recommendation": "old task logs (Safe to delete)",
            "rec_type": "safe",
            "default": True,
        },
        {
            "id": 8,
            "category": "clean",
            "name": "Ollama local model weights",
            "paths": [os.path.join(HOME_DIR, ".ollama", "models", "blobs")],
            "action_type": "empty_dir",
            "recommendation": "model blobs (Delete if using cloud)",
            "rec_type": "review",
            "default": False,
        },
        {
            "id": 9,
            "category": "clean",
            "name": "Dormant Debian container",
            "paths": [
                "/data/data/com.termux/files/usr/var/lib/proot-distro/containers/debian-ai"
            ],
            "action_type": "command",
            "cmd": ["proot-distro", "remove", "debian-ai"],
            "recommendation": "extra distro (Purge if unused)",
            "rec_type": "review",
            "default": False,
        },
    ]

    filtered = []
    for t in raw_targets:
        if is_protected(t["name"]):
            continue
        if any(is_protected(p) for p in t.get("paths", [])):
            continue

        sz = sum(get_dir_size(p) for p in t.get("paths", []))
        t["size_bytes"] = sz
        t["size_str"] = human_size(sz)
        filtered.append(t)
    return filtered


def define_installed_apps():
    """Detects CLI/TUI apps and system dependencies, omitting Vault-preserved items."""
    raw_apps = [
        # AGENTIC CLI & TUI APPS
        {
            "id": 20,
            "category": "app",
            "app_type": "Agentic TUI",
            "name": "OpenCode AI TUI",
            "bin": os.path.join(HOME_DIR, ".opencode", "bin", "opencode"),
            "data_dirs": [
                os.path.join(HOME_DIR, ".opencode"),
                os.path.join(HOME_DIR, ".opencode.json"),
            ],
            "uninstall_cmd": f"rm -rf {os.path.join(HOME_DIR, '.opencode')} {os.path.join(HOME_DIR, '.opencode.json')}",
            "extra_bins": [os.path.join(HOME_DIR, ".opencode", "bin", "opencode")],
            "extra_dirs": [os.path.join(HOME_DIR, ".opencode")],
            "default": False,
        },
        {
            "id": 21,
            "category": "app",
            "app_type": "Agentic CLI",
            "name": "Qwen Code CLI (@qwen-code/qwen-code)",
            "bin": "/data/data/com.termux/files/usr/bin/qwen",
            "data_dirs": [os.path.join(HOME_DIR, ".qwen")],
            "uninstall_cmd": "npm uninstall -g @qwen-code/qwen-code @mmmbuto/qwen-code-termux 2>/dev/null",
            "extra_bins": ["/data/data/com.termux/files/usr/bin/qwen"],
            "extra_dirs": [
                "/data/data/com.termux/files/usr/lib/node_modules/@qwen-code",
                "/data/data/com.termux/files/usr/lib/node_modules/@mmmbuto/qwen-code-termux",
            ],
            "default": False,
        },
        {
            "id": 22,
            "category": "app",
            "app_type": "Agentic CLI",
            "name": "Codex CLI (@mmmbuto/codex-cli-termux)",
            "bin": "/data/data/com.termux/files/usr/bin/codex",
            "data_dirs": [os.path.join(HOME_DIR, ".codex")],
            "uninstall_cmd": "npm uninstall -g @mmmbuto/codex-cli-termux 2>/dev/null",
            "extra_bins": [
                "/data/data/com.termux/files/usr/bin/codex",
                "/data/data/com.termux/files/usr/bin/codex-exec",
            ],
            "extra_dirs": [
                "/data/data/com.termux/files/usr/lib/node_modules/@mmmbuto/codex-cli-termux"
            ],
            "default": False,
        },
        {
            "id": 23,
            "category": "app",
            "app_type": "Agentic Tool",
            "name": "Composio Agent Tool CLI",
            "bin": os.path.join(HOME_DIR, ".composio", "composio"),
            "data_dirs": [os.path.join(HOME_DIR, ".composio")],
            "uninstall_cmd": f"rm -rf {os.path.join(HOME_DIR, '.composio')}",
            "extra_bins": [os.path.join(HOME_DIR, ".composio", "composio")],
            "extra_dirs": [os.path.join(HOME_DIR, ".composio")],
            "default": False,
        },
        {
            "id": 24,
            "category": "app",
            "app_type": "AI Engine",
            "name": "Ollama Local LLM Runner",
            "bin": "/data/data/com.termux/files/usr/bin/ollama",
            "data_dirs": [os.path.join(HOME_DIR, ".ollama")],
            "uninstall_cmd": "pkg uninstall -y ollama",
            "extra_bins": ["/data/data/com.termux/files/usr/bin/ollama"],
            "extra_dirs": [],
            "default": False,
        },
        {
            "id": 25,
            "category": "app",
            "app_type": "Agentic CLI",
            "name": "Droid AI (droid@0.177.0)",
            "bin": os.path.join(HOME_DIR, ".local", "bin", "droid"),
            "data_dirs": [
                os.path.join(HOME_DIR, ".local", "share", "droid"),
                os.path.join(HOME_DIR, ".droid"),
            ],
            "uninstall_cmd": "npm uninstall -g droid 2>/dev/null",
            "extra_bins": [
                os.path.join(HOME_DIR, ".local", "bin", "droid"),
                "/data/data/com.termux/files/usr/bin/droid",
            ],
            "extra_dirs": ["/data/data/com.termux/files/usr/lib/node_modules/droid"],
            "default": False,
        },
        {
            "id": 26,
            "category": "app",
            "app_type": "Reverse Eng",
            "name": "REA Agents (rea-agents@6.8.0)",
            "bin": "/data/data/com.termux/files/usr/bin/rea",
            "data_dirs": [],
            "uninstall_cmd": "npm uninstall -g rea-agents 2>/dev/null",
            "extra_bins": ["/data/data/com.termux/files/usr/bin/rea"],
            "extra_dirs": [
                "/data/data/com.termux/files/usr/lib/node_modules/rea-agents"
            ],
            "default": False,
        },
        {
            "id": 27,
            "category": "app",
            "app_type": "Autonomous Agent",
            "name": "Hermes Agent Framework",
            "bin": os.path.join(HOME_DIR, "hermes-agent", "run.sh"),
            "data_dirs": [os.path.join(HOME_DIR, "hermes-agent")],
            "uninstall_cmd": f"rm -rf {os.path.join(HOME_DIR, 'hermes-agent')}",
            "extra_bins": [],
            "extra_dirs": [os.path.join(HOME_DIR, "hermes-agent")],
            "default": False,
        },
        # CORE SYSTEM DEPENDENCIES & TOOLS (DIVIDER)
        {
            "id": 30,
            "category": "dep",
            "app_type": "Cloud Storage",
            "name": "Rclone Multi-Cloud Sync",
            "bin": "/data/data/com.termux/files/usr/bin/rclone",
            "data_dirs": [os.path.join(HOME_DIR, ".config", "rclone")],
            "uninstall_cmd": "pkg uninstall -y rclone",
            "extra_bins": ["/data/data/com.termux/files/usr/bin/rclone"],
            "extra_dirs": [],
            "default": False,
        },
        {
            "id": 31,
            "category": "dep",
            "app_type": "JS Runtime",
            "name": "Bun Fast JavaScript Runtime",
            "bin": os.path.join(HOME_DIR, ".bun", "bin", "bun"),
            "data_dirs": [os.path.join(HOME_DIR, ".bun")],
            "uninstall_cmd": f"rm -rf {os.path.join(HOME_DIR, '.bun')}",
            "extra_bins": [os.path.join(HOME_DIR, ".bun", "bin", "bun")],
            "extra_dirs": [os.path.join(HOME_DIR, ".bun")],
            "default": False,
        },
        {
            "id": 32,
            "category": "dep",
            "app_type": "Package Mgr",
            "name": "pnpm Fast Disk-Efficient Package Manager",
            "bin": "/data/data/com.termux/files/usr/bin/pnpm",
            "data_dirs": [os.path.join(HOME_DIR, ".local", "share", "pnpm")],
            "uninstall_cmd": "npm uninstall -g pnpm 2>/dev/null",
            "extra_bins": [
                "/data/data/com.termux/files/usr/bin/pnpm",
                "/data/data/com.termux/files/usr/bin/pnpx",
            ],
            "extra_dirs": [
                "/data/data/com.termux/files/usr/lib/node_modules/pnpm",
                os.path.join(HOME_DIR, ".local", "share", "pnpm"),
            ],
            "default": False,
        },
        {
            "id": 33,
            "category": "dep",
            "app_type": "Dev Tool",
            "name": "GitHub CLI (gh)",
            "bin": "/data/data/com.termux/files/usr/bin/gh",
            "data_dirs": [os.path.join(HOME_DIR, ".config", "gh")],
            "uninstall_cmd": "pkg uninstall -y gh",
            "extra_bins": ["/data/data/com.termux/files/usr/bin/gh"],
            "extra_dirs": [],
            "default": False,
        },
        {
            "id": 34,
            "category": "dep",
            "app_type": "Terminal Multiplexer",
            "name": "tmux Terminal Multiplexer",
            "bin": "/data/data/com.termux/files/usr/bin/tmux",
            "data_dirs": [],
            "uninstall_cmd": "pkg uninstall -y tmux",
            "extra_bins": ["/data/data/com.termux/files/usr/bin/tmux"],
            "extra_dirs": [],
            "default": False,
        },
    ]

    installed = []
    for a in raw_apps:
        if is_protected(a["name"]):
            continue
        bpath = a["bin"]
        is_inst = False
        if (
            os.path.exists(bpath)
            or shutil.which(os.path.basename(bpath))
            or a["app_type"] == "Autonomous Agent"
            and os.path.exists(a["data_dirs"][0])
        ):
            is_inst = True

        if is_inst:
            total_data_sz = sum(get_dir_size(d) for d in a["data_dirs"])
            a["data_size_bytes"] = total_data_sz
            a["data_size_str"] = human_size(total_data_sz)
            installed.append(a)
    return installed


def define_update_targets():
    """Cross-Platform System & Dependency updates for Windows, Ubuntu, and Termux."""
    targets = []

    # 1. OS Package Managers
    if IS_WINDOWS:
        if shutil.which("winget"):
            targets.append(
                {
                    "id": 10,
                    "category": "update",
                    "name": "Update Windows Apps (winget)",
                    "recommendation": "system upgrade (Recommended)",
                    "cmd": "winget upgrade --all --include-unknown",
                    "default": False,
                }
            )
        elif shutil.which("choco"):
            targets.append(
                {
                    "id": 10,
                    "category": "update",
                    "name": "Update Chocolatey Packages",
                    "recommendation": "system upgrade (Recommended)",
                    "cmd": "choco upgrade all -y",
                    "default": False,
                }
            )
    elif IS_TERMUX:
        targets.extend(
            [
                {
                    "id": 10,
                    "category": "update",
                    "name": "Clean Termux & Ubuntu pkg cache",
                    "recommendation": "system cache (Safe to clean)",
                    "cmd": "pkg clean && pkg autoclean 2>/dev/null || true",
                    "default": True,
                },
                {
                    "id": 11,
                    "category": "update",
                    "name": "Update Termux Packages (pkg)",
                    "recommendation": "system upgrade (Recommended)",
                    "cmd": "pkg update -y && pkg upgrade -y",
                    "default": False,
                },
            ]
        )
        if os.path.isdir(UBUNTU_ROOT) and shutil.which("proot-distro"):
            targets.append(
                {
                    "id": 12,
                    "category": "update",
                    "name": "Update Ubuntu Packages (apt)",
                    "recommendation": "distro upgrade (Recommended)",
                    "cmd": "proot-distro login ubuntu -- bash -c 'apt-get update && apt-get upgrade -y'",
                    "default": False,
                }
            )
    else:
        # Standard Linux / Ubuntu
        if shutil.which("apt-get"):
            targets.extend(
                [
                    {
                        "id": 10,
                        "category": "update",
                        "name": "Clean APT Package Cache",
                        "recommendation": "system cache (Safe to clean)",
                        "cmd": "sudo apt-get clean 2>/dev/null || apt-get clean 2>/dev/null || true",
                        "default": True,
                    },
                    {
                        "id": 11,
                        "category": "update",
                        "name": "Update Linux APT Packages",
                        "recommendation": "system upgrade (Recommended)",
                        "cmd": "sudo apt-get update && sudo apt-get upgrade -y",
                        "default": False,
                    },
                ]
            )

    # 2. Universal Python pip & Node npm updates
    next_id = max([t["id"] for t in targets] + [12]) + 1
    targets.append(
        {
            "id": next_id,
            "category": "update",
            "name": "Purge Python pip build cache",
            "recommendation": "cache files (Safe to purge)",
            "cmd": f"{sys.executable} -m pip cache purge 2>/dev/null || true",
            "default": True,
        }
    )
    if shutil.which("npm"):
        targets.append(
            {
                "id": next_id + 1,
                "category": "update",
                "name": "Update Global Node.js Packages",
                "recommendation": "npm CLI tools (Update all)",
                "cmd": "npm update -g 2>/dev/null || true",
                "default": False,
            }
        )

    return targets


# ==============================================================================
# SMART BOT & SILENT BACKGROUND DAEMON DETECTIVE ENGINE
# ==============================================================================
BOT_PATTERNS = [
    re.compile(
        r"telegram|telebot|aiogram|discord|bot\.polling|bot\.run|bot_token|bottoken",
        re.IGNORECASE,
    ),
    re.compile(r"webhook|slack_sdk|tweepy|cron", re.IGNORECASE),
]


def get_user_processes():
    """Returns a list of (pid, cmdline_str) for processes owned by current user across platforms."""
    procs = []
    if IS_WINDOWS:
        try:
            out = subprocess.check_output(
                ["tasklist", "/FO", "CSV", "/NH"],
                text=True,
                stderr=subprocess.DEVNULL,
            )
            for line in out.strip().splitlines():
                parts = [p.strip('"') for p in line.split('","')]
                if len(parts) >= 2 and parts[1].isdigit():
                    procs.append((int(parts[1]), parts[0]))
            return procs
        except Exception:
            return []

    if os.path.exists("/proc"):
        my_uid = os.getuid() if hasattr(os, "getuid") else None
        for pid_str in os.listdir("/proc"):
            if not pid_str.isdigit():
                continue
            try:
                pid = int(pid_str)
                if my_uid is not None:
                    p_stat = os.stat(f"/proc/{pid_str}")
                    if p_stat.st_uid != my_uid:
                        continue
                with open(f"/proc/{pid_str}/cmdline", "rb") as f:
                    raw = f.read()
                    if not raw:
                        continue
                    parts = [
                        p.decode("utf-8", errors="ignore")
                        for p in raw.split(b"\x00")
                        if p
                    ]
                    if parts:
                        procs.append((pid, " ".join(parts)))
            except (OSError, ValueError):
                continue
    return procs


def scan_bot_scripts():
    """Intelligently detects forgotten/standalone bot scripts in milliseconds."""
    detected_bots = []
    targeted_dirs = [
        HOME_DIR,
        os.path.join(HOME_DIR, ".shortcuts"),
        os.path.join(
            HOME_DIR,
            ".gemini",
            "antigravity-cli",
            "mcp",
            "multi_ai_router",
            "telegram_bot",
        ),
        os.path.join(
            HOME_DIR,
            ".codex",
            "skills",
            "shared_skills",
            "telegram-bridge-send",
            "scripts",
        ),
        os.path.join(HOME_DIR, "Modex-Sandbox-", "src", "server"),
        os.path.join(UBUNTU_ROOT, "root"),
    ]

    running_cmds = get_user_processes()

    idx = 50
    visited = set()

    for base in targeted_dirs:
        if not os.path.exists(base):
            continue
        try:
            for fname in os.listdir(base):
                fpath = os.path.join(base, fname)
                if (
                    not os.path.isfile(fpath)
                    or fpath in visited
                    or is_protected(fpath)
                    or is_protected(fname)
                ):
                    continue
                visited.add(fpath)

                if fname.endswith((".py", ".js", ".sh", ".ts", ".mjs", ".bak")):
                    is_bot = False
                    reason = ""
                    fname_lower = fname.lower()
                    if "bot" in fname_lower or "telegram" in fname_lower:
                        is_bot = True
                        reason = "Filename matches Bot/Telegram"
                    else:
                        try:
                            with open(
                                fpath, encoding="utf-8", errors="ignore"
                            ) as bot_file:
                                head = bot_file.read(2048)
                                for pat in BOT_PATTERNS:
                                    m = pat.search(head)
                                    if m:
                                        is_bot = True
                                        reason = f"Contains '{m.group(0)}' bot logic"
                                        break
                        except (OSError, UnicodeDecodeError):
                            pass

                    if is_bot:
                        st = os.stat(fpath)
                        mtime = time.strftime(
                            "%Y-%m-%d %H:%M", time.localtime(st.st_mtime)
                        )
                        active_pid = None
                        for pid, cmd in running_cmds:
                            if fname in cmd or fpath in cmd:
                                active_pid = pid
                                break

                        if active_pid:
                            rec = f"⚠️ Active Daemon (PID: {active_pid}) - Review or Terminate"
                            rec_type = "active"
                        elif fname.endswith(".bak") or "scratch" in fpath:
                            rec = "extra file (Safe to delete backup/scratch)"
                            rec_type = "safe"
                        elif "shortcuts" in fpath:
                            rec = "widget launcher (Keep if using widget shortcut)"
                            rec_type = "review"
                        else:
                            rec = "standalone script (Delete if unneeded)"
                            rec_type = "safe"

                        detected_bots.append(
                            {
                                "id": idx,
                                "type": "bot_script",
                                "name": fname,
                                "path": fpath,
                                "size_str": human_size(st.st_size),
                                "mtime": mtime,
                                "reason": reason,
                                "active_pid": active_pid,
                                "recommendation": rec,
                                "rec_type": rec_type,
                                "default": False,
                            }
                        )
                        idx += 1
        except (OSError, PermissionError):
            pass
    return detected_bots


def scan_running_daemons():
    """Detects silently running background processes/daemons owned by current user across platforms."""
    daemons = []
    idx = 80

    for pid, cmd in get_user_processes():
        cmd_lower = cmd.lower()
        if any(
            k in cmd_lower
            for k in [
                "python",
                "node",
                "bun",
                "bot.py",
                "ollama",
                "rclone",
                "opencode",
                "qwen",
                "claude",
            ]
        ):
            if (
                "termux_sentinel" in cmd_lower
                or "ps -" in cmd_lower
                or "tasklist" in cmd_lower
            ):
                continue

            parts = cmd.split()
            script_path = None
            for t in parts[1:]:
                if t.endswith((".py", ".js", ".sh", ".ts", ".mjs")) and os.path.isfile(
                    t
                ):
                    script_path = t
                    break

            mtime = "N/A"
            if script_path and os.path.exists(script_path):
                mtime = time.strftime(
                    "%Y-%m-%d %H:%M",
                    time.localtime(os.path.getmtime(script_path)),
                )

            if "bot.py" in cmd_lower or "telegram" in cmd_lower:
                dtype = "🤖 Telegram Bot Daemon"
                rec = "Active Bot (Terminate if not using Telegram Bot)"
            elif "ollama" in cmd_lower:
                dtype = "🧠 AI Model Server (Ollama)"
                rec = "Local LLM Backend (Terminate if using cloud API)"
            elif "rclone" in cmd_lower:
                dtype = "☁️ Cloud Sync Engine (Rclone)"
                rec = "Active Cloud Backup (Keep running to finish upload)"
            elif "opencode" in cmd_lower or "qwen" in cmd_lower:
                dtype = "💻 Agent Session"
                rec = "Active Terminal Agent (Terminate if orphaned)"
            else:
                dtype = "⚙️ Background Daemon"
                rec = "Silent background worker (Terminate if forgotten)"

            daemons.append(
                {
                    "id": idx,
                    "type": "daemon",
                    "pid": pid,
                    "dtype": dtype,
                    "cmd": cmd,
                    "script_path": script_path,
                    "mtime": mtime,
                    "recommendation": rec,
                    "default": False,
                }
            )
            idx += 1
    return daemons


# ==============================================================================
# UI RENDERING ENGINES (ALL-AROUND NEON FRAMES, CLAMPED 44 COLS)
# ==============================================================================
def render_main_view(clean_targets, update_targets, selected):
    cols = get_term_cols()
    print_large_header()
    render_hud_box("DASHBOARD")

    # SECTION 1: STORAGE CLEANING TARGETS
    print_section_h2("1. STORAGE TARGETS (Select to Purge)", color=NEON_YELLOW)
    reclaim_total = 0
    name_w = 21
    for t in clean_targets:
        is_sel = selected.get(t["id"], False)
        box = (
            f"{NEON_RED}{C_BOLD}[X]{C_RESET}" if is_sel else f"{NEON_GREEN}[ ]{C_RESET}"
        )
        size_str = f"({t['size_str']})"

        if t.get("rec_type") == "safe":
            rec_color = f"{NEON_GREEN}💡 {t['recommendation'][:36]}{C_RESET}"
        else:
            rec_color = f"{NEON_YELLOW}⚠️  {t['recommendation'][:36]}{C_RESET}"

        t_name = t["name"][:name_w]
        if is_sel:
            reclaim_total += t["size_bytes"]
            print(
                f"  {box} {t['id']:2d}. {BRIGHT_WHITE}{t_name:<{name_w}}{C_RESET} {NEON_RED}{size_str:>8}{C_RESET}"
            )
        else:
            print(
                f"  {box} {t['id']:2d}. {BRIGHT_WHITE}{t_name:<{name_w}}{C_RESET} {NEON_BLUE}{size_str:>8}{C_RESET}"
            )
        print(f"    {rec_color}")

    # SECTION 2: SYSTEM & DEPENDENCY UPDATES
    print_section_h2("2. SYSTEM UPDATES (Select to Upgrade)", color=NEON_PURPLE)
    for t in update_targets:
        is_sel = selected.get(t["id"], False)
        box = (
            f"{NEON_GREEN}{C_BOLD}[X]{C_RESET}"
            if is_sel
            else f"{TEXT_MUTED}[ ]{C_RESET}"
        )
        print(f"  {box} {t['id']:2d}. {BRIGHT_WHITE}{t['name'][:cols-8]}{C_RESET}")
        print(f"    {TEXT_MUTED}↳ {t['recommendation'][:cols-8]}{C_RESET}")

    print("─" * cols)
    print(
        f" {C_BOLD}{BRIGHT_WHITE}Space to Reclaim:{C_RESET} {NEON_GREEN}{C_BOLD}{human_size(reclaim_total)}{C_RESET}"
    )

    # ALL-AROUND NEON NAVIGATION FOOTER
    nav_title = "═ COMMANDS & NAVIGATION "
    fill_nav = max(0, cols - 2 - visible_len(nav_title))
    print(f"\n{NEON_CYAN}╔{nav_title}" + "═" * fill_nav + f"╗{C_RESET}")
    print(
        make_box_row(
            f"{NEON_YELLOW}[Num]{C_RESET} Toggle item   {NEON_GREEN}[a]{C_RESET} Select Safe",
            border_color=NEON_CYAN,
            cols=cols,
        )
    )
    print(
        make_box_row(
            f"{NEON_BLUE}[n]{C_RESET} Deselect All    {NEON_PURPLE}[u]{C_RESET} Toggle Updates",
            border_color=NEON_CYAN,
            cols=cols,
        )
    )
    print(
        make_box_row(
            f"{NEON_RED}[c]{C_RESET} DELETE/PURGE    {NEON_GREEN}[p]{C_RESET} PRESERVE VAULT",
            border_color=NEON_CYAN,
            cols=cols,
        )
    )
    print(
        make_box_row(
            f"{NEON_CYAN}[v]{C_RESET} Shield Vault    {NEON_PINK}[m]{C_RESET} Apps Manager",
            border_color=NEON_CYAN,
            cols=cols,
        )
    )
    print(
        make_box_row(
            f"{NEON_CYAN}[s]{C_RESET} Bots & Daemons  {NEON_GREEN}[d]{C_RESET} Doctor & Fix",
            border_color=NEON_CYAN,
            cols=cols,
        )
    )
    print(
        make_box_row(
            f"{NEON_PINK}[g]{C_RESET} Toggle AI Agent {NEON_GREEN}[x]{C_RESET} AI Advisor",
            border_color=NEON_CYAN,
            cols=cols,
        )
    )
    print(
        make_box_row(
            f"{NEON_CYAN}[o]{C_RESET} Ollama Inspector{NEON_PURPLE}[k]{C_RESET} AI Providers",
            border_color=NEON_CYAN,
            cols=cols,
        )
    )
    print(
        make_box_row(
            f"{NEON_GREEN}[i]{C_RESET} AI Chat Studio  {NEON_GREEN}[r]{C_RESET} Cloud Sync",
            border_color=NEON_CYAN,
            cols=cols,
        )
    )
    print(
        make_box_row(
            f"{NEON_CYAN}[f]{C_RESET} Refresh State   {NEON_YELLOW}[z]{C_RESET} Pause Screen",
            border_color=NEON_CYAN,
            cols=cols,
        )
    )
    print(
        make_box_row(
            f"{NEON_RED}[q]{C_RESET} Cancel & Exit",
            border_color=NEON_CYAN,
            cols=cols,
        )
    )
    print(f"{NEON_CYAN}╚" + "═" * (cols - 2) + f"╝{C_RESET}")


def render_apps_view(apps_targets, selected):
    cols = get_term_cols()
    print_large_header()
    render_hud_box("APPS MANAGER")
    print_section_h2("3. APPS & TOOLS MANAGER", color=NEON_PINK)
    print(f" {TEXT_MUTED}Tick: [c] Uninstall | [p] Preserve to Vault{C_RESET}\n")

    agentic_apps = [a for a in apps_targets if a["category"] == "app"]
    dep_tools = [a for a in apps_targets if a["category"] == "dep"]

    print_divider_h3("INSTALLED AGENTIC CLI & TUI", color=NEON_CYAN)
    name_w = 21
    for a in agentic_apps:
        is_sel = selected.get(a["id"], False)
        box = (
            f"{NEON_RED}{C_BOLD}[X]{C_RESET}" if is_sel else f"{NEON_GREEN}[ ]{C_RESET}"
        )
        data_info = f"[{a['data_size_str']}]" if a.get("data_size_bytes", 0) > 0 else ""
        print(
            f"  {box} {a['id']:2d}. {BRIGHT_WHITE}{a['name'][:name_w]:<{name_w}}{C_RESET} {NEON_YELLOW}{data_info:>10}{C_RESET}"
        )

    print_divider_h3("DEPENDENCIES & DEV TOOLS", color=NEON_PURPLE)
    for d in dep_tools:
        is_sel = selected.get(d["id"], False)
        box = (
            f"{NEON_RED}{C_BOLD}[X]{C_RESET}" if is_sel else f"{NEON_GREEN}[ ]{C_RESET}"
        )
        data_info = f"[{d['data_size_str']}]" if d.get("data_size_bytes", 0) > 0 else ""
        print(
            f"  {box} {d['id']:2d}. {BRIGHT_WHITE}{d['name'][:name_w]:<{name_w}}{C_RESET} {NEON_YELLOW}{data_info:>10}{C_RESET}"
        )

    print("─" * cols)
    sel_apps = [a for a in apps_targets if selected.get(a["id"], False)]
    print(
        f" {C_BOLD}{BRIGHT_WHITE}Selected Apps:{C_RESET} {NEON_RED}{C_BOLD}{len(sel_apps)}{C_RESET}"
    )

    # ALL-AROUND NEON APPS NAVIGATION
    print(f"\n{NEON_PINK}╔═ APP MANAGEMENT COMMANDS ════════════════╗{C_RESET}")
    print(
        make_box_row(
            f"{NEON_YELLOW}[Num]{C_RESET} Toggle App     {NEON_RED}[c]{C_RESET} UNINSTALL APPS",
            border_color=NEON_PINK,
            cols=cols,
        )
    )
    print(
        make_box_row(
            f"{NEON_GREEN}[p]{C_RESET} PRESERVE VAULT  {NEON_CYAN}[v]{C_RESET} Shield Vault",
            border_color=NEON_PINK,
            cols=cols,
        )
    )
    print(
        make_box_row(
            f"{NEON_CYAN}[f]{C_RESET} Refresh State   {NEON_BLUE}[b]{C_RESET} Back to Main",
            border_color=NEON_PINK,
            cols=cols,
        )
    )
    print(
        make_box_row(
            f"{NEON_RED}[q]{C_RESET} Cancel & Exit", border_color=NEON_PINK, cols=cols
        )
    )
    print(f"{NEON_PINK}╚══════════════════════════════════════════╝{C_RESET}")


def render_bots_view(bot_scripts, running_daemons, selected):
    cols = get_term_cols()
    print_large_header()
    render_hud_box("BOT DETECTIVE")
    print_section_h2("4. BOTS & SILENT DAEMONS", color=NEON_CYAN)
    print(f" {TEXT_MUTED}Tick: [c] Kill/Purge | [p] Preserve{C_RESET}\n")

    print_divider_h3("DETECTED BOT & SCRIPT FILES", color=NEON_PINK)
    name_w = 20
    if not bot_scripts:
        print(f"  {NEON_GREEN}✓ No rogue bot scripts detected.{C_RESET}")
    else:
        for b in bot_scripts:
            is_sel = selected.get(b["id"], False)
            box = (
                f"{NEON_RED}{C_BOLD}[X]{C_RESET}"
                if is_sel
                else f"{NEON_GREEN}[ ]{C_RESET}"
            )
            status_tag = (
                f"{NEON_RED}● ACTIVE (PID {b['active_pid']}){C_RESET}"
                if b["active_pid"]
                else f"{TEXT_MUTED}💤 DORMANT{C_RESET}"
            )
            print(
                f"  {box} {b['id']:2d}. {BRIGHT_WHITE}{b['name'][:name_w]:<{name_w}}{C_RESET} {NEON_BLUE}({b['size_str']}){C_RESET}"
            )
            p_short = b["path"].split("/")[-1]
            print(f"    {status_tag} | {C_DIM}{p_short}{C_RESET}")
            print(f"    {NEON_YELLOW}↳ {b['recommendation'][:34]}{C_RESET}")

    print_divider_h3("SILENT BACKGROUND DAEMONS", color=NEON_ORANGE)
    if not running_daemons:
        print(f"  {NEON_GREEN}✓ No unauthorized background daemons running.{C_RESET}")
    else:
        for d in running_daemons:
            is_sel = selected.get(d["id"], False)
            box = (
                f"{NEON_RED}{C_BOLD}[X]{C_RESET}"
                if is_sel
                else f"{NEON_GREEN}[ ]{C_RESET}"
            )
            print(
                f"  {box} {d['id']:2d}. {NEON_PINK}{d['dtype'][:20]}{C_RESET} {BRIGHT_WHITE}(PID {d['pid']}){C_RESET}"
            )
            print(f"    {C_DIM}Cmd: {d['cmd'][:32]}{C_RESET}")
            if d["script_path"]:
                sp_short = d["script_path"].split("/")[-1]
                print(f"    {NEON_BLUE}{sp_short} ({d['mtime']}){C_RESET}")
            print(f"    {NEON_YELLOW}↳ {d['recommendation'][:34]}{C_RESET}")

    print("─" * cols)
    sel_bots = [b for b in bot_scripts if selected.get(b["id"], False)]
    sel_daemons = [d for d in running_daemons if selected.get(d["id"], False)]
    print(
        f" {C_BOLD}{BRIGHT_WHITE}Selected:{C_RESET} {NEON_RED}{len(sel_bots)} Scripts | {len(sel_daemons)} Daemons{C_RESET}"
    )

    # ALL-AROUND NEON BOTS NAVIGATION
    print(f"\n{NEON_CYAN}╔═ BOT DETECTIVE COMMANDS ═════════════════╗{C_RESET}")
    print(
        make_box_row(
            f"{NEON_YELLOW}[Num]{C_RESET} Toggle Item    {NEON_RED}[c]{C_RESET} KILL / PURGE",
            border_color=NEON_CYAN,
            cols=cols,
        )
    )
    print(
        make_box_row(
            f"{NEON_GREEN}[p]{C_RESET} PRESERVE VAULT  {NEON_CYAN}[v]{C_RESET} Shield Vault",
            border_color=NEON_CYAN,
            cols=cols,
        )
    )
    print(
        make_box_row(
            f"{NEON_CYAN}[f]{C_RESET} Refresh State   {NEON_BLUE}[b]{C_RESET} Back to Main",
            border_color=NEON_CYAN,
            cols=cols,
        )
    )
    print(
        make_box_row(
            f"{NEON_RED}[q]{C_RESET} Cancel & Exit", border_color=NEON_CYAN, cols=cols
        )
    )
    print(f"{NEON_CYAN}╚══════════════════════════════════════════╝{C_RESET}")


def render_vault_view(vault_items):
    """Dedicated Preservation Vault View (Shield Registry)."""
    cols = get_term_cols()
    print_large_header()
    vtitle = "═ 🛡️ PRESERVED SHIELDS "
    v_top = (
        f"{NEON_GREEN}╔{vtitle}"
        + "═" * (cols - 2 - visible_len(vtitle))
        + f"╗{C_RESET}"
    )
    print(v_top)
    print(
        make_box_row(
            f"{BRIGHT_WHITE}PERMANENT ZERO-TOUCH SHIELD REGISTRY{C_RESET}",
            border_color=NEON_GREEN,
            cols=cols,
        )
    )
    print(
        make_box_row(
            f"{TEXT_MUTED}Excluded from all audits & deletions{C_RESET}",
            border_color=NEON_GREEN,
            cols=cols,
        )
    )
    print(f"{NEON_GREEN}╚" + "═" * (cols - 2) + f"╝{C_RESET}")

    print_divider_h3("ACTIVE PRESERVED SHIELDS", color=NEON_GREEN)
    if not vault_items:
        print(f"  {TEXT_MUTED}No shields registered in Vault.{C_RESET}")
    else:
        for it in vault_items:
            iid = it.get("id", 0)
            name = it.get("name", "Unnamed Shield")
            pat = it.get("pattern", "")
            itype = it.get("type", "User Shield")
            is_locked = it.get("locked", False)

            if is_locked:
                status_str = f"{BADGE_GREEN} 🛡️ LOCKED CORE {C_RESET}"
            else:
                status_str = f"{BADGE_CYAN} 🔒 USER SHIELD {C_RESET}"

            print(
                f"  {NEON_GREEN}[{iid}]{C_RESET} {BRIGHT_WHITE}{C_BOLD}{name[:28]}{C_RESET}"
            )
            print(f"      {status_str} {NEON_PURPLE}• {itype}{C_RESET}")
            print(f"      {C_DIM}Pattern: {pat[:34]}{C_RESET}")

    print("─" * cols)
    print(f"\n{NEON_GREEN}╔═ PRESERVATION VAULT COMMANDS ════════════╗{C_RESET}")
    print(
        make_box_row(
            f"{NEON_CYAN}[+]{C_RESET} Add Custom Path {NEON_YELLOW}[-]{C_RESET} Remove Shield",
            border_color=NEON_GREEN,
            cols=cols,
        )
    )
    print(
        make_box_row(
            f"{NEON_BLUE}[b]{C_RESET} Back to Main    {NEON_RED}[q]{C_RESET} Cancel & Exit",
            border_color=NEON_GREEN,
            cols=cols,
        )
    )
    print(f"{NEON_GREEN}╚══════════════════════════════════════════╝{C_RESET}")


# ==============================================================================
# CORE PREREQUISITES & COMPANION AUDIT (PYTHON, RCLONE, OLLAMA)
# ==============================================================================
def check_core_prerequisites() -> dict:
    """Audits core runtime (Python - Mandatory) and companion tools (Rclone, Ollama - Optional)."""
    py_ver = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    py_ok = sys.version_info >= (3, 9)

    rclone_path = shutil.which("rclone")
    rclone_ver = "Unknown"
    if rclone_path:
        try:
            res = subprocess.run(
                [rclone_path, "version"], capture_output=True, text=True, check=False
            )
            if res.returncode == 0 and res.stdout:
                rclone_ver = res.stdout.splitlines()[0].strip()
        except Exception:
            pass

    ollama_path = shutil.which("ollama")
    ollama_ver = "Unknown"
    ollama_stat = get_ollama_live_status()
    if ollama_path:
        try:
            res = subprocess.run(
                [ollama_path, "--version"], capture_output=True, text=True, check=False
            )
            raw = (res.stdout or "") + "\n" + (res.stderr or "")
            for line in raw.splitlines():
                line_str = line.strip()
                if "version is" in line_str:
                    ver_part = line_str.split("version is")[-1].strip()
                    ollama_ver = (
                        f"v{ver_part}" if not ver_part.startswith("v") else ver_part
                    )
                    break
                elif "ollama version" in line_str.lower():
                    ollama_ver = line_str
                    break
            if ollama_ver == "Unknown" and raw.strip():
                ollama_ver = raw.strip().splitlines()[-1].strip()
        except Exception:
            pass

    if ollama_path and ollama_stat["running"]:
        m_cnt = len(ollama_stat["pulled_models"])
        m_info = f"{m_cnt} in storage" if m_cnt else "0 in storage - pull via [o]"
        ollama_disp_ver = f"{ollama_ver} (Live :11434)"
        ollama_disp_role = f"Live 127.0.0.1:11434 ({m_info})"
    elif ollama_path:
        ollama_disp_ver = f"{ollama_ver} (Daemon stopped)"
        ollama_disp_role = "Daemon stopped (Start via 'sentinel ai inspect')"
    else:
        ollama_disp_ver = "Not Installed"
        ollama_disp_role = "Offline Local AI Inference Engine (Optional)"

    return {
        "python": {
            "name": "Python 3 Runtime",
            "mandatory": True,
            "installed": py_ok,
            "version": py_ver,
            "path": sys.executable,
            "role": "Core Engine Execution (.py scripts)",
            "install_hint": "pkg install python  OR  apt install python3  OR  winget install Python.Python.3.12",
        },
        "rclone": {
            "name": "Rclone Cloud Sync",
            "mandatory": False,
            "installed": bool(rclone_path),
            "version": rclone_ver if rclone_path else "Not Installed",
            "path": rclone_path,
            "role": "Google Drive Cloud Backup & Offloading (Optional)",
            "install_cmd": (
                "pkg install -y rclone"
                if IS_TERMUX
                else (
                    "winget install Rclone.Rclone"
                    if IS_WINDOWS
                    else "sudo apt install -y rclone"
                )
            ),
        },
        "ollama": {
            "name": "Ollama Local AI",
            "mandatory": False,
            "installed": bool(ollama_path),
            "version": ollama_disp_ver,
            "path": ollama_path,
            "role": ollama_disp_role,
            "install_cmd": (
                "pkg install -y ollama"
                if IS_TERMUX
                else (
                    "winget install Ollama.Ollama"
                    if IS_WINDOWS
                    else "curl -fsSL https://ollama.com/install.sh | sh"
                )
            ),
        },
    }


def install_optional_dependency(dep_name: str) -> bool:
    """Interactively installs optional companion tools (rclone or ollama) based on host platform."""
    dep_name = dep_name.lower().strip()
    if dep_name not in ("rclone", "ollama"):
        print(f"{NEON_RED}Unknown companion tool: {dep_name}{C_RESET}")
        return False

    animate_safe(
        "INSTALLING", f"Installing optional tool: {dep_name.upper()}...", duration=0.8
    )

    cmd = []
    if IS_TERMUX:
        cmd = ["pkg", "install", "-y", dep_name]
    elif IS_WINDOWS:
        pkg_id = "Rclone.Rclone" if dep_name == "rclone" else "Ollama.Ollama"
        cmd = [
            "winget",
            "install",
            "--id",
            pkg_id,
            "-e",
            "--accept-source-agreements",
            "--accept-package-agreements",
        ]
    else:
        # Linux / macOS
        if dep_name == "rclone":
            if shutil.which("apt-get"):
                sudo_prefix = (
                    ["sudo"]
                    if hasattr(os, "geteuid")
                    and os.geteuid() != 0
                    and shutil.which("sudo")
                    else []
                )
                cmd = sudo_prefix + ["apt-get", "install", "-y", "rclone"]
            elif shutil.which("dnf"):
                sudo_prefix = (
                    ["sudo"]
                    if hasattr(os, "geteuid")
                    and os.geteuid() != 0
                    and shutil.which("sudo")
                    else []
                )
                cmd = sudo_prefix + ["dnf", "install", "-y", "rclone"]
            elif shutil.which("pacman"):
                sudo_prefix = (
                    ["sudo"]
                    if hasattr(os, "geteuid")
                    and os.geteuid() != 0
                    and shutil.which("sudo")
                    else []
                )
                cmd = sudo_prefix + ["pacman", "-S", "--noconfirm", "rclone"]
            elif shutil.which("brew"):
                cmd = ["brew", "install", "rclone"]
        elif dep_name == "ollama":
            if shutil.which("curl"):
                cmd = ["sh", "-c", "curl -fsSL https://ollama.com/install.sh | sh"]

    if not cmd:
        print(
            f"{NEON_RED}No automated installer command determined for {dep_name} on this platform.{C_RESET}"
        )
        return False

    try:
        res = subprocess.run(cmd, check=False)
        time.sleep(1.0)
        found = bool(shutil.which(dep_name))
        if found:
            print(
                f"\n{NEON_GREEN}✓ Successfully installed {dep_name.upper()}!{C_RESET}"
            )
            return True
        else:
            if res.returncode == 0:
                print(
                    f"\n{NEON_YELLOW}Installer finished. Restart terminal if {dep_name} is not immediately found in PATH.{C_RESET}"
                )
                return True
            else:
                print(
                    f"\n{NEON_RED}✗ Installation command exited with code {res.returncode}.{C_RESET}"
                )
                return False
    except Exception as e:
        print(f"\n{NEON_RED}Failed to install {dep_name}: {e}{C_RESET}")
        return False


def cli_prerequisites(interactive=False):
    """Audits prerequisites and optionally installs missing companion tools."""
    cols = get_term_cols()
    print_large_header()
    print_section_h2("SYSTEM PREREQUISITES & COMPANION TOOLS AUDIT", color=NEON_CYAN)

    data = check_core_prerequisites()

    print(
        f"\n{C_BOLD}{BRIGHT_WHITE}{'TOOL / RUNTIME':<22} {'TYPE':<14} {'STATUS':<16} {'ROLE & DETAILS'}{C_RESET}"
    )
    print(f"{NEON_CYAN}{'─' * (cols - 2)}{C_RESET}")

    for _k, info in data.items():
        type_badge = (
            f"{BADGE_RED} REQUIRED {C_RESET}"
            if info["mandatory"]
            else f"{BADGE_BLUE} OPTIONAL {C_RESET}"
        )
        if info["installed"]:
            status_badge = f"{BADGE_GREEN} INSTALLED {C_RESET}"
            detail = f"{info['version']} ({info['role']})"
        else:
            status_badge = (
                f"{BADGE_YELLOW} MISSING {C_RESET}"
                if not info["mandatory"]
                else f"{BADGE_RED} MISSING {C_RESET}"
            )
            detail = f"{NEON_YELLOW}{info['role']}{C_RESET}"

        trunc_name = info["name"][:20]
        print(
            f"  {BRIGHT_WHITE}{trunc_name:<20}{C_RESET} {type_badge} {status_badge} {detail}"
        )

    print(f"{NEON_CYAN}{'─' * (cols - 2)}{C_RESET}")
    print(
        f"  {C_BOLD}{NEON_GREEN}Summary:{C_RESET} Python is required to execute .py scripts. Rclone & Ollama are optional companions."
    )

    if not interactive:
        return

    missing_optionals = [
        k for k, v in data.items() if not v["mandatory"] and not v["installed"]
    ]
    if not missing_optionals:
        print(
            f"\n  {NEON_GREEN}✓ All core runtime and optional companion tools are already installed!{C_RESET}\n"
        )
        return

    print(f"\n{C_BOLD}{BRIGHT_WHITE}Optional Installation Options:{C_RESET}")
    if "rclone" in missing_optionals:
        print(
            f"  {NEON_YELLOW}[r]{C_RESET} Install Rclone (for Google Drive cloud sync & offloading)"
        )
    if "ollama" in missing_optionals:
        print(
            f"  {NEON_YELLOW}[o]{C_RESET} Install Ollama (for offline local AI models)"
        )
    print(f"  {TEXT_MUTED}[Enter / q] Skip & Continue with Sentinel{C_RESET}")

    try:
        ch = (
            input(f"\n{BG_CHARCOAL}{C_BOLD}{NEON_CYAN} Prerequisites ❯ {C_RESET}")
            .strip()
            .lower()
        )
        if ch == "r" and "rclone" in missing_optionals:
            install_optional_dependency("rclone")
        elif ch == "o" and "ollama" in missing_optionals:
            install_optional_dependency("ollama")
        else:
            print(
                f"  {TEXT_MUTED}Continuing without installing optional tools.{C_RESET}"
            )
    except (KeyboardInterrupt, EOFError):
        return


# ==============================================================================
# CLOUD STATUS & ACTIONS
# ==============================================================================
def show_rclone_status():
    cols = get_term_cols()
    clear_screen()
    print_large_header()
    print_section_h2("📡 RCLONE CLOUD BACKUP LIVE TELEMETRY", color=NEON_CYAN)

    if not shutil.which("rclone"):
        print(
            f"  {BADGE_YELLOW} RCLONE NOT INSTALLED {C_RESET} {TEXT_MUTED}Rclone is an optional companion tool for cloud sync & offload.{C_RESET}\n"
        )
        print(
            f"  {C_BOLD}{BRIGHT_WHITE}Google Drive backup and offload features require Rclone.{C_RESET}"
        )
        try:
            choice = (
                input(
                    f"\n{NEON_CYAN}👉 Would you like to install Rclone now? (y/N): {C_RESET}"
                )
                .strip()
                .lower()
            )
            if choice == "y":
                if install_optional_dependency("rclone"):
                    time.sleep(1.0)
                else:
                    return
            else:
                print(
                    f"\n  {TEXT_MUTED}Skipping Rclone. Local storage & vault features remain 100% active.{C_RESET}"
                )
                time.sleep(1.5)
                return
        except (KeyboardInterrupt, EOFError):
            return

    pgrep_bin = shutil.which("pgrep") or "pgrep"
    ps = subprocess.run(
        [pgrep_bin, "-f", "rclone"], capture_output=True, text=True
    )  # nosec B603
    if ps.returncode == 0:
        print(
            f"  {BADGE_GREEN} ACTIVE & UPLOADING {C_RESET} {BRIGHT_WHITE}Streaming backup to Google Drive...{C_RESET}"
        )
    else:
        print(
            f"  {BADGE_YELLOW} IDLE / COMPLETED {C_RESET} {TEXT_MUTED}No background rclone sync active.{C_RESET}"
        )
    print("─" * cols)
    print(f"{C_BOLD}{NEON_CYAN}Recent Upload Stream (last 15 lines):{C_RESET}")

    logs = [
        os.path.join(HOME_DIR, "test_trace.log"),
        os.path.join(HOME_DIR, "rclone_backup.log"),
    ]
    found_log = False
    for l in logs:
        if os.path.exists(l) and os.path.getsize(l) > 0:
            print(f"{C_DIM}Log: {l}{C_RESET}\n")
            try:
                with open(l, encoding="utf-8", errors="replace") as log_file:
                    log_lines = log_file.readlines()[-15:]
                    print("".join(log_lines), end="")
            except OSError:
                pass
            found_log = True
            break
    if not found_log:
        print("  No active rclone log file available.")
    print("─" * cols)
    input(
        f"\n{C_BOLD}{BRIGHT_WHITE}Press Enter to return to Termux_Sentinel...{C_RESET}"
    )


# ==============================================================================
# DUAL-ACTION: PRESERVE SELECTED TO VAULT (GREEN)
# ==============================================================================
def execute_preserve(current_view, selected, clean_targets, apps_targets, bot_scripts):
    """Moves currently selected items into the Preservation Vault."""
    items_to_preserve = []

    if current_view == "main":
        for t in clean_targets:
            if selected.get(t["id"]):
                items_to_preserve.append(
                    {
                        "name": t["name"],
                        "pattern": t["name"],
                        "type": "Preserved Target",
                    }
                )
                for p in t.get("paths", []):
                    items_to_preserve.append(
                        {
                            "name": f"{t['name']} Path",
                            "pattern": p,
                            "type": "Target Path",
                        }
                    )
    elif current_view == "apps":
        for a in apps_targets:
            if selected.get(a["id"]):
                items_to_preserve.append(
                    {
                        "name": a["name"],
                        "pattern": a["name"],
                        "type": f"Preserved App ({a['app_type']})",
                    }
                )
                for d in a.get("data_dirs", []):
                    items_to_preserve.append(
                        {
                            "name": f"{a['name']} Data",
                            "pattern": d,
                            "type": "Preserved App Data",
                        }
                    )
    elif current_view == "bots":
        for b in bot_scripts:
            if selected.get(b["id"]):
                items_to_preserve.append(
                    {"name": b["name"], "pattern": b["path"], "type": "Trusted Script"}
                )

    if not items_to_preserve:
        print(
            f"\n{NEON_YELLOW}⚠️  No items selected! Tick checkboxes with [Num] first.{C_RESET}"
        )
        time.sleep(1.2)
        return False

    animate_safe(
        "VAULTING",
        f"Moving {len(items_to_preserve)} item(s) into Preservation Vault...",
        duration=0.8,
    )
    added_count = 0
    for it in items_to_preserve:
        ok, _res = add_to_vault(it["name"], it["pattern"], it["type"])
        if ok:
            added_count += 1
            print(
                f"    {NEON_GREEN}✓ Shielded:{C_RESET} {BRIGHT_WHITE}{it['name']}{C_RESET}"
            )

    # Unselect all preserved items
    for k in list(selected.keys()):
        selected[k] = False

    print(
        f"\n  {BADGE_GREEN} PRESERVED {C_RESET} {BRIGHT_WHITE}Secured {added_count} items in Vault! Permanently hidden from future scans.{C_RESET}"
    )
    time.sleep(1.5)
    return True


# ==============================================================================
# VAULT INTERACTIVE ADD / REMOVE
# ==============================================================================
def handle_vault_add():
    """Interactive custom shield addition."""
    get_term_cols()
    print(f"\n{NEON_CYAN}╔═ ADD CUSTOM SHIELD TO VAULT ═════════════╗{C_RESET}")
    print(f" {TEXT_MUTED}Enter absolute path or keyword pattern to shield:{C_RESET}")
    try:
        pat = input(f" {NEON_CYAN}Path/Pattern ❯ {C_RESET}").strip()
    except Exception:
        return
    if not pat:
        print(f"{NEON_YELLOW}Cancelled: Empty pattern.{C_RESET}")
        time.sleep(1.0)
        return

    try:
        label = input(f" {NEON_CYAN}Label/Name   ❯ {C_RESET}").strip()
    except Exception:
        label = ""
    if not label:
        label = os.path.basename(pat) or pat

    ok, res = add_to_vault(label, pat, "Custom User Shield")
    if ok:
        animate_safe("SHIELDED", f"Shield added: {label}", duration=0.6)
    else:
        print(f"\n{NEON_YELLOW}⚠️  {res}{C_RESET}")
        time.sleep(1.5)


def handle_vault_remove():
    """Interactive custom shield removal."""
    get_term_cols()
    print(f"\n{NEON_YELLOW}╔═ REMOVE SHIELD FROM VAULT ═══════════════╗{C_RESET}")
    print(f" {TEXT_MUTED}Enter shield item number [#] to remove:{C_RESET}")
    try:
        target_str = input(f" {NEON_YELLOW}Shield # ❯ {C_RESET}").strip()
    except Exception:
        return
    if not target_str.isdigit():
        print(f"{NEON_YELLOW}Cancelled: Invalid item number.{C_RESET}")
        time.sleep(1.0)
        return

    ok, res = remove_from_vault(int(target_str))
    if ok:
        animate_safe(
            "UNSHIELDED",
            f"Removed '{res['name']}' from Vault. Restored to scans.",
            duration=0.6,
        )
    else:
        print(f"\n{BADGE_RED} BLOCKED {C_RESET} {NEON_RED}{res}{C_RESET}")
        time.sleep(1.8)


# ==============================================================================
# EXECUTION ENGINE WITH FULL COLOR-CODED ANIMATIONS (RED DELETE / GREEN UPDATE)
# ==============================================================================
def execute_actions(
    clean_targets, apps_targets, update_targets, bot_scripts, running_daemons, selected
):
    clean_items = [t for t in clean_targets if selected.get(t["id"])]
    update_items = [t for t in update_targets if selected.get(t["id"])]
    uninstall_items = [a for a in apps_targets if selected.get(a["id"])]
    del_bot_items = [b for b in bot_scripts if selected.get(b["id"])]
    kill_daemon_items = [d for d in running_daemons if selected.get(d["id"])]

    if not any(
        [clean_items, update_items, uninstall_items, del_bot_items, kill_daemon_items]
    ):
        print(f"\n{NEON_YELLOW}No items selected for execution.{C_RESET}")
        time.sleep(1.2)
        return

    total_reclaim = sum(t["size_bytes"] for t in clean_items)
    cols = get_term_cols()
    clear_screen()
    print_large_header()
    print_section_h2("⚠️  TERMUX_SENTINEL: FINAL CONFIRMATION  ⚠️", color=NEON_RED)

    if clean_items:
        print(
            f"\n{C_BOLD}{NEON_RED}▶ STORAGE CACHES TO PURGE ({human_size(total_reclaim)} Reclaimed):{C_RESET}"
        )
        for t in clean_items:
            print(f"   • {BRIGHT_WHITE}{t['name']} ({t['size_str']}){C_RESET}")

    if uninstall_items:
        print(f"\n{C_BOLD}{NEON_RED}▶ APPS TO UNINSTALL:{C_RESET}")
        for a in uninstall_items:
            print(
                f"   • {BRIGHT_WHITE}{a['name']} ({a.get('data_size_str', '0 B')} data){C_RESET}"
            )

    if del_bot_items:
        print(f"\n{C_BOLD}{NEON_RED}▶ ROGUE BOT SCRIPTS TO DELETE:{C_RESET}")
        for b in del_bot_items:
            print(f"   • {BRIGHT_WHITE}{b['name']} ({b['path']}){C_RESET}")

    if kill_daemon_items:
        print(f"\n{C_BOLD}{NEON_RED}▶ SILENT DAEMONS TO TERMINATE:{C_RESET}")
        for d in kill_daemon_items:
            print(f"   • {BRIGHT_WHITE}{d['dtype']} (PID: {d['pid']}){C_RESET}")

    if update_items:
        print(f"\n{C_BOLD}{NEON_GREEN}▶ SYSTEM & DEPENDENCY UPGRADES:{C_RESET}")
        for t in update_items:
            print(f"   • {BRIGHT_WHITE}{t['name']}{C_RESET}")

    print(
        f"\n{BADGE_RED} PROCEED? {C_RESET} {C_BOLD}{BRIGHT_WHITE}Execute operations now? (y/N): {C_RESET}",
        end="",
    )
    try:
        conf = input().strip().lower()
    except Exception:
        conf = "n"

    if conf not in ["y", "yes"]:
        print(
            f"\n{NEON_BLUE}Operation cancelled by operator. Nothing was touched.{C_RESET}"
        )
        time.sleep(1.5)
        return

    print("\n" + "─" * cols)
    animate_safe("STARTING", "Initializing Termux_Sentinel execution...", duration=0.8)

    # 1. Terminate Background Daemons (RED)
    if kill_daemon_items:
        print_divider_h3("TERMINATING BACKGROUND DAEMONS", color=NEON_RED)
        for d in kill_daemon_items:
            pid = d["pid"]
            animate_terminate(f"Stopping daemon {d['dtype']} (PID {pid})...")
            if kill_process_pid(pid):
                print(f"    {NEON_RED}✓ Terminated PID {pid}{C_RESET}")
            else:
                print(f"    {NEON_YELLOW}✗ Could not terminate PID {pid}{C_RESET}")

    # 2. Delete Rogue Bot Script Files (RED)
    if del_bot_items:
        print_divider_h3("PURGING ROGUE BOT SCRIPTS", color=NEON_RED)
        for b in del_bot_items:
            bp = b["path"]
            if is_protected(bp):
                print(f"    {NEON_GREEN}🛡️ Protected by Vault: {bp}{C_RESET}")
                continue
            animate_delete(f"Removing bot script {b['name']}...")
            try:
                if os.path.exists(bp):
                    os.remove(bp)
                print(f"    {NEON_RED}✓ Wiped: {bp}{C_RESET}")
            except Exception as e:
                print(f"    {NEON_YELLOW}✗ Error deleting {bp}: {e}{C_RESET}")

    # 3. Clean Storage Targets (RED)
    if clean_items:
        print_divider_h3("PURGING STORAGE CACHES", color=NEON_RED)
        for t in clean_items:
            animate_delete(f"Cleaning: {t['name']}...")
            if t["action_type"] == "command":
                subprocess.run(t["cmd"], check=False)  # nosec B603
            elif t["action_type"] == "empty_dir":
                for p in t["paths"]:
                    if is_protected(p):
                        print(f"    {NEON_GREEN}🛡️ Protected by Vault: {p}{C_RESET}")
                        continue
                    if os.path.exists(p):
                        for item in os.listdir(p):
                            ipath = os.path.join(p, item)
                            if is_protected(ipath):
                                continue
                            try:
                                if os.path.isdir(ipath) and not os.path.islink(ipath):
                                    shutil.rmtree(ipath, ignore_errors=True)
                                else:
                                    os.remove(ipath)
                            except OSError:
                                pass
                        print(f"    {NEON_RED}✓ Emptied: {p}{C_RESET}")
            elif t["action_type"] == "remove_paths":
                for p in t["paths"]:
                    if is_protected(p):
                        print(f"    {NEON_GREEN}🛡️ Protected by Vault: {p}{C_RESET}")
                        continue
                    if os.path.exists(p):
                        try:
                            if os.path.isdir(p) and not os.path.islink(p):
                                shutil.rmtree(p, ignore_errors=True)
                            else:
                                os.remove(p)
                            print(f"    {NEON_RED}✓ Removed: {p}{C_RESET}")
                        except Exception as e:
                            print(
                                f"    {NEON_YELLOW}✗ Error removing {p}: {e}{C_RESET}"
                            )

    # 4. Uninstall Apps & Data Prompt
    if uninstall_items:
        print_divider_h3("UNINSTALLING APPLICATIONS", color=NEON_RED)
        for a in uninstall_items:
            animate_step(
                "UNINSTALLING", f"Removing {a['name']}...", color=NEON_RED, duration=0.7
            )
            uninstall_cmd = a.get("uninstall_cmd", "")
            if uninstall_cmd:
                try:
                    subprocess.run(
                        shlex.split(uninstall_cmd), check=False
                    )  # nosec B603
                except (OSError, ValueError):
                    pass

            # Fail-safe: ensure primary binary/symlink is completely eliminated
            bpath = a.get("bin")
            if bpath and (os.path.exists(bpath) or os.path.islink(bpath)):
                try:
                    if os.path.isdir(bpath) and not os.path.islink(bpath):
                        shutil.rmtree(bpath, ignore_errors=True)
                    else:
                        os.remove(bpath)
                except (OSError, PermissionError):
                    shutil.rmtree(bpath, ignore_errors=True)

            # Fail-safe: eliminate any secondary binaries/symlinks
            for eb in a.get("extra_bins", []):
                if os.path.exists(eb) or os.path.islink(eb):
                    try:
                        os.remove(eb)
                    except (OSError, PermissionError):
                        shutil.rmtree(eb, ignore_errors=True)

            # Fail-safe: eliminate leftover node_modules or app packages
            for ed in a.get("extra_dirs", []):
                if os.path.exists(ed):
                    shutil.rmtree(ed, ignore_errors=True)

            print(
                f"    {NEON_RED}✓ Binary & package completely wiped for {a['name']}{C_RESET}"
            )

            if a.get("data_dirs"):
                print(
                    f"\n    {NEON_YELLOW}App '{a['name']}' has {a['data_size_str']} stored data.{C_RESET}"
                )
                print(
                    f"    {C_BOLD}{BRIGHT_WHITE}Remove stored app data? (YES/NO): {C_RESET}",
                    end="",
                )
                try:
                    data_conf = input().strip().lower()
                except Exception:
                    data_conf = "no"

                if data_conf in ["yes", "y"]:
                    animate_delete(f"Purging data directories of {a['name']}...")
                    for d in a["data_dirs"]:
                        if is_protected(d):
                            print(
                                f"    {NEON_GREEN}🛡️ Protected by Vault: {d}{C_RESET}"
                            )
                            continue
                        if os.path.exists(d):
                            try:
                                if os.path.isdir(d) and not os.path.islink(d):
                                    shutil.rmtree(d, ignore_errors=True)
                                else:
                                    os.remove(d)
                                print(f"    {NEON_RED}✓ Wiped: {d}{C_RESET}")
                            except Exception as e:
                                print(f"    {NEON_YELLOW}✗ Error: {e}{C_RESET}")
                else:
                    animate_safe(
                        "PRESERVED",
                        f"App data for {a['name']} preserved securely.",
                        duration=0.4,
                    )

    # 5. System & Dependency Updates (GREEN)
    if update_items:
        print_divider_h3("RUNNING SYSTEM & DEPENDENCY UPGRADES", color=NEON_GREEN)
        for t in update_items:
            animate_safe("UPDATING", f"Running: {t['name']}...", duration=0.6)
            cmd = t.get("cmd", "")
            if cmd:
                try:
                    subprocess.run(shlex.split(cmd), check=False)  # nosec B603
                except (OSError, ValueError):
                    pass
            print(f"    {NEON_GREEN}✓ Update finished for {t['name']}{C_RESET}")

    # Reset selection for all executed items
    for item in (
        clean_items + update_items + uninstall_items + del_bot_items + kill_daemon_items
    ):
        selected[item["id"]] = False

    print("\n" + "─" * cols)
    animate_safe(
        "COMPLETED", "All operations executed with 100% integrity!", duration=0.8
    )
    used, _total, free, pct = get_disk_usage()
    print(
        f"\n {BG_CHARCOAL} {C_BOLD}{BRIGHT_WHITE}UPDATED STORAGE:{C_RESET} Used: {NEON_YELLOW}{used}{C_RESET} | Free: {NEON_GREEN}{C_BOLD}{free}{C_RESET} ({NEON_PINK}{pct} full{C_RESET})"
    )
    print("─" * cols)
    input(f"{C_BOLD}{BRIGHT_WHITE}Press Enter to return to Termux_Sentinel...{C_RESET}")


# ==============================================================================
# MAIN EVENT LOOP
# ==============================================================================
def main():
    animate_boot_glow()

    clean_targets = define_cleaning_targets()
    apps_targets = define_installed_apps()
    update_targets = define_update_targets()
    bot_scripts = scan_bot_scripts()
    running_daemons = scan_running_daemons()

    # Pre-select safe defaults
    selected = {t["id"]: t["default"] for t in clean_targets}
    for a in apps_targets:
        selected[a["id"]] = False
    for u in update_targets:
        selected[u["id"]] = u["default"]
    for b in bot_scripts:
        selected[b["id"]] = False
    for d in running_daemons:
        selected[d["id"]] = False

    current_view = "main"

    while True:
        clear_screen()
        if current_view == "main":
            render_main_view(clean_targets, update_targets, selected)
        elif current_view == "apps":
            render_apps_view(apps_targets, selected)
        elif current_view == "bots":
            render_bots_view(bot_scripts, running_daemons, selected)
        elif current_view == "vault":
            render_vault_view(load_vault())

        try:
            prompt_tag = f"[{current_view.upper()}]"
            choice = (
                input(
                    f"\n{BG_CHARCOAL}{C_BOLD}{NEON_CYAN} Termux_Sentinel {prompt_tag} ❯ {C_RESET}"
                )
                .strip()
                .lower()
            )
        except (KeyboardInterrupt, EOFError):
            print(f"\n{NEON_BLUE}Exiting Termux_Sentinel.{C_RESET}")
            break

        if not choice:
            continue

        if choice == "q":
            animate_step(
                "CLOSING",
                "Termux_Sentinel shutting down safely...",
                color=NEON_BLUE,
                duration=0.4,
            )
            break
        elif choice == "c":
            execute_actions(
                clean_targets,
                apps_targets,
                update_targets,
                bot_scripts,
                running_daemons,
                selected,
            )
            animate_safe(
                "REFRESHING", "Reloading fresh system & app telemetry...", duration=0.6
            )
            clean_targets = define_cleaning_targets()
            apps_targets = define_installed_apps()
            bot_scripts = scan_bot_scripts()
            running_daemons = scan_running_daemons()
        elif choice == "f":
            animate_safe(
                "REFRESHING", "Scanning and reloading fresh telemetry...", duration=0.6
            )
            clean_targets = define_cleaning_targets()
            apps_targets = define_installed_apps()
            bot_scripts = scan_bot_scripts()
            running_daemons = scan_running_daemons()
        elif choice == "p":
            if current_view == "vault":
                print(f"\n{NEON_YELLOW}Already inside Preservation Vault.{C_RESET}")
                time.sleep(1.0)
            else:
                ok = execute_preserve(
                    current_view, selected, clean_targets, apps_targets, bot_scripts
                )
                if ok:
                    clean_targets = define_cleaning_targets()
                    apps_targets = define_installed_apps()
                    bot_scripts = scan_bot_scripts()
        elif choice == "v":
            current_view = "vault"
        elif choice == "m":
            current_view = "apps"
        elif choice == "s":
            current_view = "bots"
        elif choice == "b":
            current_view = "main"
        elif choice == "+" and current_view == "vault":
            handle_vault_add()
        elif choice == "-" and current_view == "vault":
            handle_vault_remove()
        elif choice == "a" and current_view == "main":
            for t in clean_targets:
                selected[t["id"]] = True
        elif choice == "n" and current_view == "main":
            for t in clean_targets:
                selected[t["id"]] = False
        elif choice == "u" and current_view == "main":
            curr = any(selected[t["id"]] for t in update_targets)
            for t in update_targets:
                selected[t["id"]] = not curr
        elif choice == "r":
            show_rclone_status()
        elif choice == "d":
            cli_repair(auto_fix=True)
            input(
                f"\n{C_BOLD}{BRIGHT_WHITE}Press Enter to return to Termux_Sentinel...{C_RESET}"
            )
        elif choice == "g":
            new_s = toggle_agentic_mode()
            tag = "ENABLED (ONLINE)" if new_s else "DISABLED (MANUAL MODE)"
            print(
                f"\n{NEON_GREEN if new_s else NEON_YELLOW}Agentic AI Mode is now {tag}.{C_RESET}"
            )
            time.sleep(1.0)
        elif choice in ("i", "chat", "ai"):
            interactive_ai_chat()
        elif choice == "x":
            run_agentic_ai_advisor(
                clean_targets, apps_targets, bot_scripts, running_daemons
            )
        elif choice == "o":
            render_hardware_inspection_view()
        elif choice == "k":
            interactive_ai_setup()
        elif choice == "z":
            print(
                f"\n{NEON_YELLOW}Sentinel paused. No background changes made.{C_RESET}"
            )
            input(f"{C_BOLD}{BRIGHT_WHITE}Press Enter to resume Sentinel...{C_RESET}")
        else:
            parts = choice.replace(",", " ").split()
            for part in parts:
                if part.isdigit():
                    num = int(part)
                    if num in selected:
                        selected[num] = not selected[num]


# ==============================================================================
# CLI NON-INTERACTIVE COMMAND HANDLERS
# ==============================================================================
def cli_audit():
    get_term_cols()
    print_large_header()
    render_hud_box("AUDIT")

    clean_targets = define_cleaning_targets()
    apps_targets = define_installed_apps()
    bot_scripts = scan_bot_scripts()
    running_daemons = scan_running_daemons()
    vault_items = load_vault()

    print_section_h2("1. STORAGE TARGETS AUDIT", color=NEON_YELLOW)
    reclaimable = 0
    for t in clean_targets:
        sz = t["size_bytes"]
        reclaimable += sz
        rec = t.get("recommendation", "")[:28]
        badge = (
            f"{NEON_GREEN}SAFE{C_RESET}"
            if t.get("rec_type") == "safe"
            else f"{NEON_YELLOW}REV{C_RESET}"
        )
        print(
            f"  • {BRIGHT_WHITE}{t['name'][:22]:<22}{C_RESET} {NEON_CYAN}{t['size_str']:>8}{C_RESET} [{badge}]"
        )
        print(f"    {TEXT_MUTED}↳ {rec}{C_RESET}")

    print(
        f"\n  {C_BOLD}{BRIGHT_WHITE}Reclaimable:{C_RESET} {NEON_GREEN}{C_BOLD}{human_size(reclaimable)}{C_RESET}"
    )

    print_section_h2("2. INSTALLED CLI/TUI APPS", color=NEON_PINK)
    for a in apps_targets:
        d_sz = f"[{a['data_size_str']}]" if a.get("data_size_bytes") else ""
        print(
            f"  • {BRIGHT_WHITE}{a['name'][:22]:<22}{C_RESET} {NEON_YELLOW}{d_sz:>10}{C_RESET}"
        )

    print_section_h2("3. ROGUE BOTS & DAEMONS", color=NEON_CYAN)
    if not bot_scripts:
        print(f"  {NEON_GREEN}✓ No rogue bot scripts detected.{C_RESET}")
    else:
        for b in bot_scripts[:4]:
            print(f"  • {NEON_PINK}{b['name'][:20]}{C_RESET} ({b['size_str']})")
    if not running_daemons:
        print(f"  {NEON_GREEN}✓ No background daemons.{C_RESET}")
    else:
        for d in running_daemons:
            print(f"  • {NEON_YELLOW}{d['dtype'][:24]}{C_RESET} (PID {d['pid']})")

    print_section_h2("4. PRESERVATION VAULT", color=NEON_GREEN)
    for v in vault_items:
        lock_tag = (
            f"{BADGE_GREEN} LOCKED {C_RESET}"
            if v.get("locked")
            else f"{BADGE_CYAN} USER {C_RESET}"
        )
        print(f"  {lock_tag} {BRIGHT_WHITE}{v['name'][:24]}{C_RESET}")


def cli_clean(safe_only=True, dry_run=False, auto_yes=False):
    get_term_cols()
    targets = define_cleaning_targets()
    if safe_only:
        targets = [t for t in targets if t.get("rec_type") == "safe"]

    if not targets:
        print(f"\n{NEON_GREEN}✓ System already clean! No caches to purge.{C_RESET}")
        return

    total_bytes = sum(t["size_bytes"] for t in targets)
    print_large_header()
    print_section_h2(f"PURGING {len(targets)} CACHE TARGETS", color=NEON_RED)
    for t in targets:
        print(
            f"  • {BRIGHT_WHITE}{t['name'][:24]:<24}{C_RESET} {NEON_CYAN}{t['size_str']:>8}{C_RESET}"
        )

    if dry_run:
        print(
            f"\n{BADGE_CYAN} DRY RUN {C_RESET} {TEXT_MUTED}Would reclaim {human_size(total_bytes)}. No files touched.{C_RESET}"
        )
        return

    if not auto_yes:
        print(
            f"\n{C_BOLD}{BRIGHT_WHITE}Purge these targets ({human_size(total_bytes)})? (y/N): {C_RESET}",
            end="",
        )
        try:
            conf = input().strip().lower()
        except (EOFError, KeyboardInterrupt):
            conf = "n"
        if conf not in ("y", "yes"):
            print(f"{NEON_YELLOW}Operation cancelled by operator.{C_RESET}")
            return

    for t in targets:
        animate_delete(f"Cleaning {t['name'][:24]}...")
        if t["action_type"] == "command":
            subprocess.run(t["cmd"], check=False)  # nosec B603
        elif t["action_type"] == "empty_dir":
            for p in t["paths"]:
                if is_protected(p):
                    continue
                if os.path.exists(p):
                    for item in os.listdir(p):
                        ip = os.path.join(p, item)
                        if is_protected(ip):
                            continue
                        try:
                            if os.path.isdir(ip) and not os.path.islink(ip):
                                shutil.rmtree(ip, ignore_errors=True)
                            else:
                                os.remove(ip)
                        except (OSError, UnicodeDecodeError):
                            pass
        elif t["action_type"] == "remove_paths":
            for p in t["paths"]:
                if is_protected(p):
                    continue
                if os.path.exists(p):
                    try:
                        if os.path.isdir(p) and not os.path.islink(p):
                            shutil.rmtree(p, ignore_errors=True)
                        else:
                            os.remove(p)
                    except (OSError, PermissionError):
                        shutil.rmtree(p, ignore_errors=True)

    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "cache", "purge"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )  # nosec B603
    except OSError:
        pass
    animate_safe(
        "PURGED",
        f"Successfully reclaimed {human_size(total_bytes)} storage!",
        duration=0.6,
    )
    _used, _total, free, pct = get_disk_usage()
    print(
        f"\n {BG_CHARCOAL} {C_BOLD}{BRIGHT_WHITE}UPDATED STORAGE:{C_RESET} Free: {NEON_GREEN}{C_BOLD}{free}{C_RESET} ({NEON_PINK}{pct} full{C_RESET})"
    )


def cli_vault(action="list", target=None, name=None):
    if action == "list":
        vault_items = load_vault()
        print_large_header()
        print_section_h2("PRESERVATION VAULT SHIELDS", color=NEON_GREEN)
        for v in vault_items:
            iid = v.get("id", 0)
            lock_tag = (
                f"{BADGE_GREEN} LOCKED {C_RESET}"
                if v.get("locked")
                else f"{BADGE_CYAN} USER {C_RESET}"
            )
            print(f"  [{iid}] {lock_tag} {BRIGHT_WHITE}{v['name'][:24]}{C_RESET}")
            print(f"      {TEXT_MUTED}Pattern: {v.get('pattern', '')[:32]}{C_RESET}")
    elif action in ("add", "+"):
        if not target:
            print(f"{NEON_RED}Error: Missing path or pattern to shield.{C_RESET}")
            print("Usage: sentinel vault add <path_or_pattern> [optional_name]")
            return
        label = name if name else os.path.basename(target) or target
        ok, res = add_to_vault(label, target, "CLI User Shield")
        if ok:
            print(f"{NEON_GREEN}✓ Shield added: '{label}' ({target}){C_RESET}")
        else:
            print(f"{NEON_YELLOW}⚠️  {res}{C_RESET}")
    elif action in ("remove", "rm", "del", "-"):
        if not target or not str(target).isdigit():
            print(f"{NEON_RED}Error: Provide shield ID number to remove.{C_RESET}")
            print("Usage: sentinel vault rm <id>")
            return
        ok, res = remove_from_vault(int(target))
        if ok:
            print(
                f"{NEON_GREEN}✓ Shield removed: '{res['name']}'. Restored to scans.{C_RESET}"
            )
        else:
            print(f"{NEON_RED}✗ Cannot remove: {res}{C_RESET}")


def cli_apps(action="list", target=None):
    if action == "list":
        apps_targets = define_installed_apps()
        print_large_header()
        print_section_h2("INSTALLED APPS & TOOLS", color=NEON_PINK)
        for a in apps_targets:
            d_sz = f"[{a['data_size_str']}]" if a.get("data_size_bytes") else ""
            print(
                f"  [{a['id']}] {BRIGHT_WHITE}{a['name'][:24]:<24}{C_RESET} {NEON_YELLOW}{d_sz:>10}{C_RESET}"
            )
            print(f"      {TEXT_MUTED}Bin: {a['bin'][:33]}{C_RESET}")
    elif action in ("uninstall", "rm", "del"):
        if not target:
            print(f"{NEON_RED}Error: Provide app ID or name to uninstall.{C_RESET}")
            print("Usage: sentinel apps rm <id_or_name>")
            return
        apps = define_installed_apps()
        matched = None
        for a in apps:
            if str(a["id"]) == str(target) or target.lower() in a["name"].lower():
                matched = a
                break
        if not matched:
            print(f"{NEON_YELLOW}No installed app matching '{target}'.{C_RESET}")
            return
        print(
            f"\n{C_BOLD}{NEON_RED}Uninstall {matched['name']}? (y/N): {C_RESET}", end=""
        )
        try:
            conf = input().strip().lower()
        except Exception:
            conf = "n"
        if conf not in ("y", "yes"):
            print(f"{NEON_YELLOW}Uninstallation cancelled.{C_RESET}")
            return
        animate_delete(f"Removing {matched['name']}...")
        uninstall_cmd = matched.get("uninstall_cmd", "")
        if uninstall_cmd:
            try:
                subprocess.run(shlex.split(uninstall_cmd), check=False)  # nosec B603
            except (OSError, ValueError):
                pass
        if matched.get("bin") and (
            os.path.exists(matched["bin"]) or os.path.islink(matched["bin"])
        ):
            try:
                if os.path.isdir(matched["bin"]) and not os.path.islink(matched["bin"]):
                    shutil.rmtree(matched["bin"], ignore_errors=True)
                else:
                    os.remove(matched["bin"])
            except (OSError, PermissionError):
                shutil.rmtree(matched["bin"], ignore_errors=True)
        for eb in matched.get("extra_bins", []):
            if os.path.exists(eb) or os.path.islink(eb):
                try:
                    os.remove(eb)
                except (OSError, PermissionError):
                    shutil.rmtree(eb, ignore_errors=True)
        for ed in matched.get("extra_dirs", []):
            if os.path.exists(ed):
                shutil.rmtree(ed, ignore_errors=True)
        print(f"{NEON_GREEN}✓ Uninstallation complete for {matched['name']}{C_RESET}")


def cli_bots(action="scan", pid=None):
    if action == "scan":
        bots = scan_bot_scripts()
        daemons = scan_running_daemons()
        print_large_header()
        print_section_h2("BOT SCRIPTS & DAEMONS", color=NEON_CYAN)
        print_divider_h3("DETECTED BOT SCRIPTS", color=NEON_PINK)
        if not bots:
            print(f"  {NEON_GREEN}✓ No rogue bot scripts detected.{C_RESET}")
        else:
            for b in bots:
                status_tag = (
                    f"{NEON_RED}● ACT:{b['active_pid']}{C_RESET}"
                    if b["active_pid"]
                    else f"{TEXT_MUTED}💤 DORMANT{C_RESET}"
                )
                print(
                    f"  • {BRIGHT_WHITE}{b['name'][:16]:<16}{C_RESET} {b['size_str']:>8} {status_tag}"
                )
        print_divider_h3("SILENT BACKGROUND DAEMONS", color=NEON_ORANGE)
        if not daemons:
            print(f"  {NEON_GREEN}✓ No unauthorized background daemons.{C_RESET}")
        else:
            for d in daemons:
                print(f"  • {NEON_YELLOW}{d['dtype'][:22]}{C_RESET} (PID {d['pid']})")
    elif action in ("kill", "terminate", "stop"):
        if not pid:
            print(f"{NEON_RED}Error: Provide process PID to terminate.{C_RESET}")
            print("Usage: sentinel bots kill <pid>")
            return
        try:
            p_int = int(pid)
            animate_terminate(f"Terminating PID {p_int}...")
            if kill_process_pid(p_int):
                print(f"{NEON_GREEN}✓ Process PID {p_int} terminated.{C_RESET}")
            else:
                print(f"{NEON_YELLOW}✗ Could not terminate PID {pid}{C_RESET}")
        except Exception as e:
            print(f"{NEON_YELLOW}✗ Could not terminate PID {pid}: {e}{C_RESET}")


def cli_cloud(_live=False, start=False):
    if not shutil.which("rclone"):
        print(
            f"{NEON_YELLOW}⚠️  Rclone is not installed (optional dependency for cloud sync).{C_RESET}"
        )
        try:
            choice = (
                input(
                    f"{NEON_CYAN}👉 Would you like to install Rclone now? (y/N): {C_RESET}"
                )
                .strip()
                .lower()
            )
            if choice == "y":
                if not install_optional_dependency("rclone"):
                    print(f"{NEON_RED}Rclone installation was not completed.{C_RESET}")
                    return
            else:
                print(
                    f"{TEXT_MUTED}Skipped. Local storage operations remain 100% active.{C_RESET}"
                )
                return
        except (KeyboardInterrupt, EOFError):
            return

    if start:
        animate_safe(
            "STARTING", "Launching background Rclone cloud backup...", duration=0.8
        )
        trace_path = os.path.join(HOME_DIR, "test_trace.log")
        with open(trace_path, "a", encoding="utf-8") as trace_log:
            bash_bin = shutil.which("bash") or "/bin/bash"
            cmf_script = os.path.join(HOME_DIR, "migrate_to_cmf_bkp.sh")
            repo_script = os.path.join(
                HOME_DIR, "TERMUX-SENTINEL-CLI", "migrate_to_cmf_bkp.sh"
            )
            script_path = cmf_script if os.path.isfile(cmf_script) else repo_script
            subprocess.Popen(  # nosec B603
                [bash_bin, script_path],
                stdout=trace_log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        print(
            f"{NEON_GREEN}✓ Cloud migration running in background with wake-lock.{C_RESET}"
        )
        print(f"View progress: {NEON_CYAN}sentinel cloud{C_RESET}")
    else:
        show_rclone_status()


def cli_update():
    animate_safe("UPDATING", "Running package & dependency upgrades...", duration=0.8)
    targets = define_update_targets()
    for t in targets:
        print(f"\n{NEON_CYAN}▶ {t['name']}{C_RESET}")
        cmd = t.get("cmd", "")
        if cmd:
            try:
                subprocess.run(shlex.split(cmd), check=False)  # nosec B603
            except (OSError, ValueError):
                pass
    animate_safe("COMPLETED", "All system & dependency updates finished!", duration=0.6)


def cli_hunt(threshold_mb=100, scan_path=HOME_DIR):
    """Hunts bloated directories exceeding threshold_mb in scan_path."""
    animate_safe("HUNTING", f"Scanning directories >{threshold_mb}MB...", duration=0.6)
    print_section_h2(f"BLOAT HUNTER: TARGETS > {threshold_mb} MB")

    if not os.path.exists(scan_path):
        print(f"{NEON_RED}Target path does not exist: {scan_path}{C_RESET}")
        return

    threshold_bytes = threshold_mb * 1024 * 1024
    candidates = []

    try:
        for entry in os.scandir(scan_path):
            if entry.is_symlink() or entry.name in ("storage", "proc", "sys", "dev"):
                continue
            if entry.is_dir(follow_symlinks=False):
                sz = get_dir_size(entry.path)
                if sz >= threshold_bytes:
                    candidates.append((entry.path, sz))
    except Exception as e:
        print(f"{NEON_RED}Error scanning: {e}{C_RESET}")
        return

    if not candidates:
        print(
            f"\n{NEON_GREEN}✓ Clean! No unmanaged directories exceed {threshold_mb} MB.{C_RESET}\n"
        )
        return

    candidates.sort(key=lambda x: x[1], reverse=True)
    cols = get_term_cols()

    print(
        f"\n{C_BOLD}{BRIGHT_WHITE}{'SIZE':<12} {'TARGET DIRECTORY':<{cols - 16}}{C_RESET}"
    )
    print(f"{NEON_CYAN}{'─' * (cols - 2)}{C_RESET}")

    for path, sz in candidates:
        rel = os.path.relpath(path, scan_path)
        sz_str = human_size(sz)
        tag = ""
        if "node_modules" in path:
            tag = f" {NEON_YELLOW}[NPM]{C_RESET}"
        elif ".cache" in path or "cache" in path.lower():
            tag = f" {NEON_PURPLE}[CACHE]{C_RESET}"
        elif ".venv" in path or "site-packages" in path:
            tag = f" {NEON_CYAN}[VENV]{C_RESET}"
        elif is_protected(path):
            tag = f" {NEON_GREEN}[VAULT SHIELD]{C_RESET}"

        print(f"  {NEON_YELLOW}{sz_str:<10}{C_RESET} {BRIGHT_WHITE}{rel}{C_RESET}{tag}")

    print(
        f"\n{NEON_CYAN}Tip: Move heavy directories to cloud with: {NEON_GREEN}sentinel offload <path>{C_RESET}\n"
    )


def cli_offload(target_path, remote_folder="Offloaded"):
    """Safely offload heavy directory/file to Google Drive via Rclone and free local space."""
    target_abs = os.path.abspath(os.path.expanduser(target_path))
    if not os.path.exists(target_abs):
        print(f"{NEON_RED}Error: Path does not exist: {target_abs}{C_RESET}")
        return

    if is_protected(target_abs):
        print(
            f"{NEON_RED}Protected by Vault! Refusing to offload: {target_abs}{C_RESET}"
        )
        return

    rclone_bin = shutil.which("rclone")
    if not rclone_bin:
        print(
            f"{NEON_YELLOW}⚠️  Rclone is not installed (optional tool needed to offload files to Google Drive).{C_RESET}"
        )
        try:
            choice = (
                input(
                    f"{NEON_CYAN}👉 Would you like to install Rclone now? (y/N): {C_RESET}"
                )
                .strip()
                .lower()
            )
            if choice == "y":
                if not install_optional_dependency("rclone"):
                    print(
                        f"{NEON_RED}Cannot offload: rclone installation was not completed.{C_RESET}"
                    )
                    return
                rclone_bin = shutil.which("rclone")
            else:
                print(
                    f"{TEXT_MUTED}Offload cancelled. File remains safely stored locally.{C_RESET}"
                )
                return
        except (KeyboardInterrupt, EOFError):
            return

    remotes_out = ""
    try:
        remotes_out = subprocess.check_output(
            [rclone_bin, "listremotes"], text=True, stderr=subprocess.DEVNULL
        )
    except Exception:
        pass

    remote_name = "gdrive" if "gdrive:" in remotes_out else "remote_gdrive"
    remote_dest = f"{remote_name}:{remote_folder}/{os.path.basename(target_abs)}"
    sz = (
        get_dir_size(target_abs)
        if os.path.isdir(target_abs)
        else os.path.getsize(target_abs)
    )

    print_section_h2(f"CLOUD OFFLOADER: {human_size(sz)}")
    print(f"Local Source : {NEON_CYAN}{target_abs}{C_RESET}")
    print(f"Cloud Target : {NEON_GREEN}{remote_dest}{C_RESET}")

    animate_safe(
        "OFFLOADING", f"Transferring {human_size(sz)} to {remote_name}...", duration=0.8
    )

    cmd = [
        rclone_bin,
        "move",
        target_abs,
        remote_dest,
        "--transfers",
        "4",
        "--stats",
        "2s",
    ]
    try:
        subprocess.run(cmd, check=True)  # nosec B603
        if os.path.isdir(target_abs) and os.path.exists(target_abs):
            try:
                os.rmdir(target_abs)
            except OSError:
                pass
        print(
            f"\n{NEON_GREEN}✓ Successfully offloaded {human_size(sz)} to {remote_dest}{C_RESET}"
        )
        print(f"{NEON_GREEN}✓ Local space reclaimed!{C_RESET}\n")
    except subprocess.CalledProcessError as e:
        print(f"\n{NEON_RED}✗ Offload failed with exit code {e.returncode}{C_RESET}\n")
    except Exception as e:
        print(f"\n{NEON_RED}✗ Offload error: {e}{C_RESET}\n")


def cli_autoclean():
    """Headless automated maintenance for Termux Widget and Cron schedulers."""
    log_dir = os.path.join(HOME_DIR, ".config", "termux_sentinel")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "sentinel_autoclean.log")

    _used_b, _total_b, free_b, _ = get_disk_usage()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    # Run safe purge
    cli_clean(safe_only=True, dry_run=False, auto_yes=True)

    _used_a, _total_a, free_a, _ = get_disk_usage()
    log_entry = f"[{timestamp}] Auto-clean completed. Free before: {free_b} | Free after: {free_a}\n"
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except OSError:
        pass

    termux_notify = shutil.which("termux-notification")
    if termux_notify:
        try:
            subprocess.run(
                [
                    termux_notify,
                    "--title",
                    "Termux Sentinel Auto-Clean",
                    "--content",
                    f"Maintenance complete. Free space: {free_a}",
                    "--id",
                    "sentinel_clean",
                ],
                check=False,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass


def self_heal_sentinel(silent=False):
    """Audits and self-heals Sentinel's own installation, vault integrity, permissions, PATH, and logs."""
    issues = []
    healed = []

    # 1. Config directory & Vault JSON integrity
    os.makedirs(VAULT_DIR, exist_ok=True)
    if not os.path.exists(VAULT_FILE) or os.path.getsize(VAULT_FILE) == 0:
        issues.append("Preservation Vault missing or empty")
        save_vault(DEFAULT_VAULT_ITEMS)
        healed.append("Generated fresh default Preservation Vault")
    else:
        try:
            with open(VAULT_FILE, encoding="utf-8") as f:
                v_data = json.load(f)
            if not isinstance(v_data, list):
                raise ValueError("Vault root must be a list")
            patterns = {
                it.get("pattern", "").lower() for it in v_data if isinstance(it, dict)
            }
            missing_defaults = [
                d for d in DEFAULT_VAULT_ITEMS if d["pattern"].lower() not in patterns
            ]
            if missing_defaults:
                issues.append(
                    f"{len(missing_defaults)} core safety shield(s) missing from Vault"
                )
                v_data.extend(missing_defaults)
                save_vault(v_data)
                healed.append(f"Restored {len(missing_defaults)} core safety shield(s)")
        except Exception as e:
            issues.append(f"Corrupted vault.json syntax ({e})")
            corrupt_bkp = VAULT_FILE + f".corrupt.{int(time.time())}"
            try:
                shutil.copy2(VAULT_FILE, corrupt_bkp)
            except OSError:
                pass
            save_vault(DEFAULT_VAULT_ITEMS)
            healed.append(
                f"Recovered corrupt Vault from template (backup: {os.path.basename(corrupt_bkp)})"
            )

    # 2. File permissions on Sentinel scripts
    sentinel_py = os.path.abspath(__file__)
    sentinel_dir = os.path.dirname(sentinel_py)
    if not IS_WINDOWS and hasattr(os, "access"):
        try:
            if not os.access(sentinel_py, os.X_OK):
                issues.append("Termux_Sentinel.py lacks execute permission (+x)")
                os.chmod(sentinel_py, 0o755)
                healed.append("Restored execute permissions on Termux_Sentinel.py")
            install_sh = os.path.join(sentinel_dir, "install.sh")
            if os.path.exists(install_sh) and not os.access(install_sh, os.X_OK):
                os.chmod(install_sh, 0o755)
                healed.append("Restored execute permissions on install.sh")
        except OSError:
            pass

    # 3. PATH Integration & CLI wrapper
    sentinel_cmd = shutil.which("sentinel")
    if not sentinel_cmd:
        issues.append("'sentinel' executable not found in PATH")
        target_bin_dir = None
        prefix = os.environ.get("PREFIX", "")
        if IS_TERMUX and prefix and os.path.isdir(os.path.join(prefix, "bin")):
            target_bin_dir = os.path.join(prefix, "bin")
        elif not IS_WINDOWS:
            for cand in [
                os.path.join(HOME_DIR, ".local", "bin"),
                os.path.join(HOME_DIR, "bin"),
            ]:
                if os.path.isdir(cand):
                    target_bin_dir = cand
                    break

        if target_bin_dir:
            wrapper_path = os.path.join(target_bin_dir, "sentinel")
            try:
                wrapper_content = f'#!/bin/sh\nexec {shlex.quote(sys.executable)} {shlex.quote(sentinel_py)} "$@"\n'
                with open(wrapper_path, "w", encoding="utf-8") as f:
                    f.write(wrapper_content)
                os.chmod(wrapper_path, 0o755)
                healed.append(f"Created CLI wrapper at {wrapper_path}")
            except OSError:
                pass

    # 4. Log rotation (Crash log and auto-clean log)
    for log_path in [CRASH_LOG_FILE, os.path.join(VAULT_DIR, "sentinel_autoclean.log")]:
        if os.path.exists(log_path):
            try:
                if os.path.getsize(log_path) > 1024 * 1024:  # > 1 MB
                    issues.append(f"{os.path.basename(log_path)} exceeded 1MB limit")
                    old_path = log_path + ".old"
                    if os.path.exists(old_path):
                        os.remove(old_path)
                    os.rename(log_path, old_path)
                    healed.append(f"Rotated bloated log {os.path.basename(log_path)}")
            except OSError:
                pass

    # 5. Stale Sentinel lock recovery
    rclone_lock = os.path.join(HOME_DIR, ".rclone_backup.lock")
    if os.path.exists(rclone_lock):
        running = " ".join([p[1].lower() for p in get_user_processes()])
        if "rclone" not in running:
            issues.append("Stale Sentinel cloud sync lock detected")
            try:
                os.remove(rclone_lock)
                healed.append("Removed abandoned ~/.rclone_backup.lock")
            except OSError:
                pass

    if not silent:
        print_large_header()
        print_section_h2("SENTINEL SELF-HEALING & RESCUE", color=NEON_GREEN)
        print(f"\n{C_BOLD}{BRIGHT_WHITE}INTEGRITY DIAGNOSTICS:{C_RESET}")
        if issues:
            for iss in issues:
                print(f"  {NEON_YELLOW}⚠️  Detected:{C_RESET} {iss}")
        else:
            print(
                f"  {NEON_GREEN}✓ Sentinel components operating with 100% integrity.{C_RESET}"
            )

        print(f"\n{C_BOLD}{BRIGHT_WHITE}ACTIONS APPLIED:{C_RESET}")
        if healed:
            for act in healed:
                print(f"  {NEON_GREEN}✓ Healed:{C_RESET} {act}")
            print(
                f"\n{NEON_GREEN}Self-healing finished! Sentinel restored to prime condition.{C_RESET}\n"
            )
        else:
            print(
                f"  {TEXT_MUTED}No repairs needed. All configs, permissions, and paths verified.{C_RESET}\n"
            )

    return healed, issues


def install_self_healing_hooks():
    """Installs resilient global uncaught exception hooks and signal handlers."""

    def _sig_handler(sig, frame):
        sys.stdout.write(f"\033[?25h{C_RESET}\n")
        sys.stdout.flush()
        rclone_lock = os.path.join(HOME_DIR, ".rclone_backup.lock")
        if os.path.exists(rclone_lock):
            try:
                os.remove(rclone_lock)
            except OSError:
                pass
        sys.exit(130 if sig == signal.SIGINT else 143)

    try:
        signal.signal(signal.SIGINT, _sig_handler)
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, _sig_handler)
    except (ValueError, OSError):
        pass

    def _excepthook(exc_type, exc_val, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.stdout.write(
                f"\n{NEON_YELLOW}Sentinel operation cancelled by user.{C_RESET}\n"
            )
            sys.stdout.flush()
            sys.exit(130)

        sys.stdout.write(f"\033[?25h{C_RESET}\n")
        sys.stdout.flush()

        os.makedirs(VAULT_DIR, exist_ok=True)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        tb_lines = "".join(traceback.format_exception(exc_type, exc_val, exc_tb))
        log_entry = (
            f"=== SENTINEL CRASH REPORT [{timestamp}] ===\n"
            f"Platform: {sys.platform} | Termux: {IS_TERMUX} | Windows: {IS_WINDOWS}\n"
            f"Command : {' '.join(sys.argv)}\n"
            f"Exception: {exc_type.__name__}: {exc_val}\n"
            f"Traceback:\n{tb_lines}\n"
            f"{'='*60}\n\n"
        )
        try:
            with open(CRASH_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except OSError:
            pass

        print(f"\n{BADGE_RED} CRASH INTERCEPTED {C_RESET}")
        print(
            f" {NEON_RED}An unexpected runtime error occurred: {BRIGHT_WHITE}{exc_type.__name__}: {exc_val}{C_RESET}"
        )
        print(f" {TEXT_MUTED}Full crash report saved to: {CRASH_LOG_FILE}{C_RESET}")
        print(f" {NEON_CYAN}Initiating automated self-healing rescue...{C_RESET}")

        try:
            healed, _ = self_heal_sentinel(silent=True)
            if healed:
                print(
                    f" {NEON_GREEN}✓ Self-healed {len(healed)} component(s): {', '.join(healed[:3])}{C_RESET}"
                )
        except Exception:
            pass

        print(
            f" {TEXT_MUTED}Run 'sentinel heal' to re-verify installation health.{C_RESET}\n"
        )
        sys.exit(1)

    sys.excepthook = _excepthook


def cli_repair(auto_fix=True):
    """Diagnoses and repairs broken packages, corrupted dependency caches, dangling symlinks, and stale locks."""
    get_term_cols()
    print_large_header()
    mode_str = "AUTO-REPAIR & HEAL" if auto_fix else "DIAGNOSTIC DOCTOR"
    print_section_h2(
        f"SENTINEL {mode_str}", color=NEON_GREEN if auto_fix else NEON_CYAN
    )

    actions_taken = []
    issues_found = []

    # 0. Sentinel Self-Healing & Internal Health Check
    self_healed, self_issues = self_heal_sentinel(silent=True)
    if self_issues:
        issues_found.extend(self_issues)
    if self_healed:
        actions_taken.extend(self_healed)

    # 1. Stale Process / App Locks
    animate_safe(
        "DIAGNOSTICS", "Checking lockfiles & process integrity...", duration=0.4
    )
    running_procs = get_user_processes()
    running_names = " ".join([p[1].lower() for p in running_procs])

    # Check ~/.rclone_backup.lock
    rclone_lock = os.path.join(HOME_DIR, ".rclone_backup.lock")
    if os.path.exists(rclone_lock):
        if "rclone" not in running_names:
            issues_found.append("Stale Rclone sync lock detected")
            if auto_fix:
                try:
                    os.remove(rclone_lock)
                    actions_taken.append("Removed stale ~/.rclone_backup.lock")
                except OSError:
                    pass

    # Check .git/index.lock in current directory and sentinel home
    for git_dir in [
        os.path.join(os.getcwd(), ".git"),
        os.path.join(HOME_DIR, "TERMUX-SENTINEL-CLI", ".git"),
    ]:
        lock_file = os.path.join(git_dir, "index.lock")
        if os.path.exists(lock_file):
            if "git" not in running_names:
                issues_found.append(
                    f"Stale Git index lock in {os.path.basename(os.path.dirname(git_dir))}"
                )
                if auto_fix:
                    try:
                        os.remove(lock_file)
                        actions_taken.append(f"Removed stale Git lock: {lock_file}")
                    except OSError:
                        pass

    # 2. Package Manager Lockfiles & Configuration (Termux / Debian / Ubuntu)
    dpkg_bin = shutil.which("dpkg")
    apt_bin = shutil.which("apt") or shutil.which("apt-get")

    dpkg_lock_paths = []
    prefix = os.environ.get("PREFIX", "")
    if prefix and os.path.exists(os.path.join(prefix, "var", "lib", "dpkg")):
        dpkg_lock_paths = [
            os.path.join(prefix, "var", "lib", "dpkg", "lock"),
            os.path.join(prefix, "var", "lib", "dpkg", "lock-frontend"),
            os.path.join(prefix, "var", "lib", "apt", "lists", "lock"),
        ]
    elif os.path.exists("/var/lib/dpkg"):
        dpkg_lock_paths = [
            "/var/lib/dpkg/lock",
            "/var/lib/dpkg/lock-frontend",
            "/var/lib/apt/lists/lock",
        ]

    stale_dpkg_locks = [p for p in dpkg_lock_paths if os.path.exists(p)]
    if stale_dpkg_locks:
        if not any(k in running_names for k in ("apt", "dpkg", "pkg")):
            issues_found.append(
                f"{len(stale_dpkg_locks)} stale package manager lock(s) detected"
            )
            if auto_fix:
                for lp in stale_dpkg_locks:
                    try:
                        os.remove(lp)
                        actions_taken.append(
                            f"Removed stale lock: {os.path.basename(lp)}"
                        )
                    except OSError:
                        pass

    # Check broken dpkg configuration / dependencies
    if dpkg_bin and (
        prefix or (os.geteuid() == 0 if hasattr(os, "geteuid") else False)
    ):
        try:
            audit = subprocess.run(
                [dpkg_bin, "--audit"], capture_output=True, text=True, check=False
            )
            if audit.stdout.strip() or audit.returncode != 0:
                issues_found.append("Unconfigured / interrupted dpkg packages")
                if auto_fix:
                    animate_safe(
                        "HEALING",
                        "Configuring unconfigured dpkg packages...",
                        duration=0.5,
                    )
                    subprocess.run([dpkg_bin, "--configure", "-a"], check=False)
                    if apt_bin:
                        subprocess.run([apt_bin, "install", "-f", "-y"], check=False)
                    actions_taken.append(
                        "Executed dpkg --configure -a & apt-get -f install"
                    )
        except Exception:
            pass

    # 3. Dangling / Broken Symlinks in user bins
    bin_dirs = []
    if prefix:
        bin_dirs.append(os.path.join(prefix, "bin"))
    bin_dirs.extend(
        [
            os.path.join(HOME_DIR, ".local", "bin"),
            os.path.join(HOME_DIR, "bin"),
        ]
    )

    broken_symlinks = []
    for bdir in bin_dirs:
        if os.path.isdir(bdir):
            try:
                for entry in os.listdir(bdir):
                    fpath = os.path.join(bdir, entry)
                    if is_protected(fpath):
                        continue
                    if os.path.islink(fpath) and not os.path.exists(fpath):
                        broken_symlinks.append(fpath)
            except OSError:
                pass

    if broken_symlinks:
        issues_found.append(f"{len(broken_symlinks)} broken dangling binary symlink(s)")
        if auto_fix:
            for sl in broken_symlinks:
                try:
                    os.unlink(sl)
                    actions_taken.append(
                        f"Pruned dangling symlink: {os.path.basename(sl)}"
                    )
                except OSError:
                    pass

    # 4. Python Environment & Corrupted Cache
    try:
        pip_check = subprocess.run(
            [sys.executable, "-m", "pip", "check"],
            capture_output=True,
            text=True,
            check=False,
        )
        if pip_check.returncode != 0:
            broken_msgs = [
                line.strip() for line in pip_check.stdout.splitlines() if line.strip()
            ]
            if broken_msgs:
                issues_found.append(
                    f"Python dependency conflict: {broken_msgs[0][:40]}"
                )
    except Exception:
        pass

    if auto_fix:
        # Purge pip cache to remove corrupt wheels/tarballs
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "cache", "purge"],
                capture_output=True,
                check=False,
            )
            actions_taken.append("Purged corrupted Python pip wheel/source caches")
        except Exception:
            pass

    # 5. NPM / Node Cache Integrity
    npm_bin = shutil.which("npm")
    if npm_bin and auto_fix:
        try:
            animate_safe(
                "HEALING", "Verifying and repairing npm cache...", duration=0.4
            )
            subprocess.run(
                [npm_bin, "cache", "verify"], capture_output=True, check=False
            )
            actions_taken.append("Verified and cleaned NPM cache integrity")
        except Exception:
            pass

    # Display Results
    print(f"\n{C_BOLD}{BRIGHT_WHITE}DIAGNOSTIC SUMMARY:{C_RESET}")
    if issues_found:
        for iss in issues_found:
            print(f"  {NEON_YELLOW}⚠️  Detected:{C_RESET} {iss}")
    else:
        print(
            f"  {NEON_GREEN}✓ No corrupted packages, stale locks, or broken symlinks detected.{C_RESET}"
        )

    if auto_fix:
        print(f"\n{C_BOLD}{BRIGHT_WHITE}REPAIRS APPLIED:{C_RESET}")
        if actions_taken:
            for act in actions_taken:
                print(f"  {NEON_GREEN}✓ Healed:{C_RESET} {act}")
            print(
                f"\n{NEON_GREEN}All repairs completed successfully! System dependencies healthy.{C_RESET}\n"
            )
        else:
            print(
                f"  {TEXT_MUTED}No repairs needed. System is operating at peak health.{C_RESET}\n"
            )
    else:
        print(
            f"\n{TEXT_MUTED}Run '{NEON_GREEN}sentinel repair{TEXT_MUTED}' to automatically heal detected issues.{C_RESET}\n"
        )


# ==============================================================================
# HARDWARE CAPACITY INSPECTOR & OFFLINE OLLAMA ADVISOR
# ==============================================================================
AI_PROVIDERS = {
    "tokenharbor": {
        "id": "tokenharbor",
        "name": "Token Harbor (OpenCode Default)",
        "base_url": "https://tokenharbor.ai/v1",
        "env_key": "TOKENHARBOR_API_KEY",
        "type": "openai",
        "models_endpoint": "/models",
        "badge": "OPENCODE",
        "default_models": [
            "deepseek-v4.1-flash:free",
            "qwen3.8-max",
            "gemini-3.8-flash",
            "claude-sonnet-5.5",
            "gpt-6.1-sol",
            "mimo-v2.6-flash:free",
            "glm-5.3-flash",
            "kimi-k3",
            "qwen3.8-flash",
            "deepseek-v4-pro",
        ],
    },
    "openrouter": {
        "id": "openrouter",
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "env_key": "OPENROUTER_API_KEY",
        "type": "openai",
        "models_endpoint": "/models",
        "badge": "MULTI-LLM",
        "default_models": [
            "deepseek/deepseek-r1",
            "google/gemini-2.0-flash-exp:free",
            "meta-llama/llama-3.3-70b-instruct",
            "qwen/qwen-2.5-72b-instruct",
            "anthropic/claude-3.5-sonnet",
        ],
    },
    "gemini": {
        "id": "gemini",
        "name": "Google Gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "env_key": "GEMINI_API_KEY",
        "type": "gemini",
        "models_endpoint": "/models",
        "badge": "GOOGLE",
        "default_models": [
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-2.5-flash",
        ],
    },
    "groq": {
        "id": "groq",
        "name": "Groq Cloud (Fastest Inference)",
        "base_url": "https://api.groq.com/openai/v1",
        "env_key": "GROQ_API_KEY",
        "type": "openai",
        "models_endpoint": "/models",
        "badge": "FASTEST",
        "default_models": [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "qwen-2.5-32b",
            "deepseek-r1-distill-llama-70b",
        ],
    },
    "deepseek": {
        "id": "deepseek",
        "name": "DeepSeek Official",
        "base_url": "https://api.deepseek.com/v1",
        "env_key": "DEEPSEEK_API_KEY",
        "type": "openai",
        "models_endpoint": "/models",
        "badge": "REASONING",
        "default_models": ["deepseek-chat", "deepseek-reasoner"],
    },
    "openai": {
        "id": "openai",
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "env_key": "OPENAI_API_KEY",
        "type": "openai",
        "models_endpoint": "/models",
        "badge": "FRONTIER",
        "default_models": ["gpt-4o", "gpt-4o-mini", "o1", "o3-mini"],
    },
    "anthropic": {
        "id": "anthropic",
        "name": "Anthropic Claude",
        "base_url": "https://api.anthropic.com/v1",
        "env_key": "ANTHROPIC_API_KEY",
        "type": "anthropic",
        "models_endpoint": "/models",
        "badge": "AGENTIC",
        "default_models": [
            "claude-3-7-sonnet-20250219",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
        ],
    },
    "mistral": {
        "id": "mistral",
        "name": "Mistral AI",
        "base_url": "https://api.mistral.ai/v1",
        "env_key": "MISTRAL_API_KEY",
        "type": "openai",
        "models_endpoint": "/models",
        "badge": "OPEN-WEIGHTS",
        "default_models": [
            "mistral-large-latest",
            "codestral-latest",
            "mistral-small-latest",
        ],
    },
    "ollama": {
        "id": "ollama",
        "name": "Ollama (Local Offline)",
        "base_url": "http://127.0.0.1:11434",
        "env_key": "OLLAMA_HOST",
        "type": "ollama",
        "models_endpoint": "/api/tags",
        "badge": "100% OFFLINE",
        "default_models": [
            "qwen2.5:3b",
            "deepseek-r1:1.5b",
            "gemma2:2b",
            "smollm:1.7b",
            "llama3.2:1b",
        ],
    },
}


def inspect_device_hardware():
    """Audits local device hardware capacity and determines recommended offline models."""
    cpu_cores = os.cpu_count() or 4
    arch = os.uname().machine if hasattr(os, "uname") else sys.platform

    ram_total_b = 0
    ram_avail_b = 0
    if os.path.exists("/proc/meminfo"):
        try:
            with open("/proc/meminfo", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        ram_total_b = int(line.split()[1]) * 1024
                    elif line.startswith("MemAvailable:"):
                        ram_avail_b = int(line.split()[1]) * 1024
        except Exception:
            pass

    if ram_total_b == 0:
        ram_total_b = 8 * 1024 * 1024 * 1024
        ram_avail_b = 3 * 1024 * 1024 * 1024

    ram_total_gb = round(ram_total_b / (1024**3), 2)
    ram_avail_gb = round(ram_avail_b / (1024**3), 2)

    usage = shutil.disk_usage(HOME_DIR)
    disk_free_gb = round(usage.free / (1024**3), 2)

    ollama_path = shutil.which("ollama")
    stat = get_ollama_live_status()
    ollama_running = stat["running"]
    pulled_models = stat["pulled_models"]

    if ram_total_gb < 3.5:
        tier_id = "ultra_compact"
        tier_title = "TIER 1: ULTRA-COMPACT EDGE (< 4GB RAM)"
        models = [
            {
                "name": "smollm:135m",
                "size": "135M",
                "ram": "~120 MB",
                "desc": "Instant sub-second reasoning",
            },
            {
                "name": "smollm:360m",
                "size": "360M",
                "ram": "~280 MB",
                "desc": "Lightweight command interpreter",
            },
            {
                "name": "qwen2.5:0.5b",
                "size": "0.5B",
                "ram": "~390 MB",
                "desc": "Smallest Qwen multilingual model",
            },
        ]
    elif ram_total_gb < 6.0:
        tier_id = "compact"
        tier_title = "TIER 2: MOBILE COMPACT (4GB - 6GB RAM)"
        models = [
            {
                "name": "deepseek-r1:1.5b",
                "size": "1.5B",
                "ram": "~1.1 GB",
                "desc": "Distilled reasoning core",
            },
            {
                "name": "qwen2.5:1.5b",
                "size": "1.5B",
                "ram": "~1.2 GB",
                "desc": "Fast scripting & JSON generation",
            },
            {
                "name": "smollm:1.7b",
                "size": "1.7B",
                "ram": "~1.3 GB",
                "desc": "Local instruction following",
            },
            {
                "name": "llama3.2:1b",
                "size": "1.2B",
                "ram": "~1.3 GB",
                "desc": "Meta edge instruction model",
            },
        ]
    elif ram_total_gb < 11.0:
        tier_id = "power_mobile"
        tier_title = "TIER 3: POWER MOBILE / WORKSTATION (6GB - 10GB RAM)"
        models = [
            {
                "name": "qwen2.5:3b",
                "size": "3.0B",
                "ram": "~2.1 GB",
                "desc": "Top agentic logic, tools & Python scripts",
            },
            {
                "name": "gemma2:2b",
                "size": "2.0B",
                "ram": "~1.6 GB",
                "desc": "Google Gemma edge model (efficient)",
            },
            {
                "name": "deepseek-r1:1.5b",
                "size": "1.5B",
                "ram": "~1.1 GB",
                "desc": "DeepSeek reasoning & chain-of-thought",
            },
            {
                "name": "llama3.2:3b",
                "size": "3.2B",
                "ram": "~2.3 GB",
                "desc": "Meta balanced coding & writing",
            },
            {
                "name": "phi3.5:3.8b",
                "size": "3.8B",
                "ram": "~2.5 GB",
                "desc": "Microsoft high-efficiency mini model",
            },
        ]
    else:
        tier_id = "server"
        tier_title = "TIER 4: HIGH-END SERVER (> 10GB RAM)"
        models = [
            {
                "name": "qwen2.5:7b",
                "size": "7.0B",
                "ram": "~4.6 GB",
                "desc": "Production-grade general intelligence",
            },
            {
                "name": "deepseek-r1:7b",
                "size": "7.0B",
                "ram": "~4.8 GB",
                "desc": "DeepSeek heavy reasoning model",
            },
            {
                "name": "mistral:7b",
                "size": "7.0B",
                "ram": "~4.5 GB",
                "desc": "Mistral foundational LLM",
            },
            {
                "name": "gemma2:9b",
                "size": "9.0B",
                "ram": "~5.8 GB",
                "desc": "Google heavy edge model",
            },
        ]

    return {
        "cpu_cores": cpu_cores,
        "arch": arch,
        "ram_total_gb": ram_total_gb,
        "ram_avail_gb": ram_avail_gb,
        "disk_free_gb": disk_free_gb,
        "ollama_path": ollama_path,
        "ollama_running": ollama_running,
        "pulled_models": pulled_models,
        "tier_id": tier_id,
        "tier_title": tier_title,
        "recommended_models": models,
    }


def render_hardware_inspection_view():
    """Displays Device Hardware Capacity Audit & Offline Ollama Model Advisor."""
    cols = get_term_cols()
    print_large_header()
    print_section_h2("DEVICE HARDWARE CAPACITY & OLLAMA ADVISOR", color=NEON_GREEN)

    info = inspect_device_hardware()
    print(f"\n{C_BOLD}{BRIGHT_WHITE}HARDWARE AUDIT TELEMETRY:{C_RESET}")
    print(
        f"  CPU Platform : {NEON_CYAN}{info['arch']}{C_RESET} ({info['cpu_cores']} Cores)"
    )
    print(
        f"  RAM Memory   : Total: {NEON_YELLOW}{info['ram_total_gb']} GB{C_RESET} | Available: {NEON_GREEN}{info['ram_avail_gb']} GB{C_RESET}"
    )
    print(
        f"  Disk Storage : Free Space: {NEON_GREEN}{info['disk_free_gb']} GB{C_RESET}"
    )

    ollama_stat = (
        f"{NEON_GREEN}● Running on port 11434{C_RESET}"
        if info["ollama_running"]
        else f"{NEON_YELLOW}○ Inactive (Binary: {info['ollama_path'] or 'Not in PATH'}){C_RESET}"
    )
    print(f"  Ollama Daemon: {ollama_stat}")
    if info["pulled_models"]:
        print(
            f"  Local Models : {NEON_CYAN}{', '.join(info['pulled_models'][:4])}{C_RESET}"
        )
    else:
        print(f"  Local Models : {TEXT_MUTED}None downloaded yet{C_RESET}")

    print(
        f"\n{C_BOLD}{NEON_PINK}CAPACITY CLASSIFICATION:{C_RESET} {BRIGHT_WHITE}{info['tier_title']}{C_RESET}"
    )
    print(f"\n{C_BOLD}{BRIGHT_WHITE}RECOMMENDED OFFLINE MODELS TO PULL:{C_RESET}")

    for idx, m in enumerate(info["recommended_models"], 1):
        is_pulled = any(m["name"].split(":")[0] in pm for pm in info["pulled_models"])
        badge = (
            f"{BADGE_GREEN} INSTALLED {C_RESET}"
            if is_pulled
            else f"{BADGE_CYAN} READY {C_RESET}"
        )
        print(
            f"  [{idx}] {badge} {BRIGHT_WHITE}{m['name']:<18}{C_RESET} {NEON_YELLOW}{m['ram']:<10}{C_RESET} {TEXT_MUTED}{m['desc']}{C_RESET}"
        )

    ollama_action = (
        f"{NEON_GREEN}[s]{C_RESET} Start Daemon"
        if info["ollama_path"]
        else f"{NEON_YELLOW}[i]{C_RESET} Install Ollama"
    )
    print(
        f"\n{NEON_CYAN}╔═ ACTIONS ═════════════════════════════════════════════╗{C_RESET}"
    )
    print(
        make_box_row(
            f"{NEON_YELLOW}[1-{len(info['recommended_models'])}]{C_RESET} Pull Model    {ollama_action}",
            border_color=NEON_CYAN,
            cols=cols,
        )
    )
    print(
        make_box_row(
            f"{NEON_CYAN}[c]{C_RESET} Pull Custom Model {NEON_BLUE}[b]{C_RESET} Back to Sentinel",
            border_color=NEON_CYAN,
            cols=cols,
        )
    )
    print(
        f"{NEON_CYAN}╚═══════════════════════════════════════════════════════╝{C_RESET}"
    )

    try:
        act = (
            input(f"\n{BG_CHARCOAL}{C_BOLD}{NEON_GREEN} Hardware Inspector ❯ {C_RESET}")
            .strip()
            .lower()
        )
    except (KeyboardInterrupt, EOFError):
        return

    if not act or act == "b":
        return

    if act == "i":
        if info["ollama_path"]:
            print(
                f"\n{NEON_GREEN}✓ Ollama is already installed at: {info['ollama_path']}{C_RESET}"
            )
            time.sleep(1.5)
        else:
            try:
                ch = (
                    input(
                        f"\n{NEON_CYAN}👉 Install optional tool Ollama now? (y/N): {C_RESET}"
                    )
                    .strip()
                    .lower()
                )
                if ch == "y":
                    install_optional_dependency("ollama")
                    time.sleep(1.5)
            except (KeyboardInterrupt, EOFError):
                pass
        render_hardware_inspection_view()
        return

    if act == "s":
        if not info["ollama_path"]:
            print(f"\n{NEON_YELLOW}⚠️  Ollama is not installed.{C_RESET}")
            try:
                ch = (
                    input(
                        f"{NEON_CYAN}👉 Would you like to install Ollama now? (y/N): {C_RESET}"
                    )
                    .strip()
                    .lower()
                )
                if ch == "y":
                    if install_optional_dependency("ollama"):
                        info = inspect_device_hardware()
                    else:
                        time.sleep(1.5)
                        return
                else:
                    print(
                        f"  {TEXT_MUTED}Skipping Ollama. Cloud AI models remain 100% available via [c].{C_RESET}"
                    )
                    time.sleep(1.5)
                    return
            except (KeyboardInterrupt, EOFError):
                return
        animate_safe(
            "STARTING", "Launching Ollama daemon in background...", duration=0.8
        )
        log_p = os.path.join(VAULT_DIR, "ollama.log")
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=open(log_p, "a", encoding="utf-8"),
            stderr=subprocess.STDOUT,
        )
        time.sleep(2.0)
        render_hardware_inspection_view()
        return

    target_model = None
    if act.isdigit():
        choice_idx = int(act) - 1
        if 0 <= choice_idx < len(info["recommended_models"]):
            target_model = info["recommended_models"][choice_idx]["name"]
    elif act == "c":
        try:
            target_model = input(
                f"{NEON_CYAN}Enter model tag to pull (e.g. qwen2.5:3b): {C_RESET}"
            ).strip()
        except (KeyboardInterrupt, EOFError):
            return

    if target_model:
        if not info["ollama_path"]:
            print(
                f"\n{NEON_YELLOW}⚠️  Ollama CLI is required to run offline models locally.{C_RESET}"
            )
            try:
                ch = (
                    input(
                        f"{NEON_CYAN}👉 Would you like to install Ollama now? (y/N): {C_RESET}"
                    )
                    .strip()
                    .lower()
                )
                if ch == "y":
                    if install_optional_dependency("ollama"):
                        info = inspect_device_hardware()
                    else:
                        time.sleep(1.5)
                        return
                else:
                    print(
                        f"  {TEXT_MUTED}Skipped. You can use Cloud AI providers instead with zero local installation.{C_RESET}"
                    )
                    time.sleep(1.5)
                    return
            except (KeyboardInterrupt, EOFError):
                return
        print(
            f"\n{NEON_CYAN}Starting pull for {BRIGHT_WHITE}{target_model}{NEON_CYAN}...{C_RESET}"
        )
        try:
            subprocess.run(["ollama", "pull", target_model], check=True)
            cfg = load_ai_config()
            cfg["provider"] = "ollama"
            cfg["provider_name"] = "Ollama (Local Offline)"
            cfg["model"] = target_model
            cfg["base_url"] = "http://127.0.0.1:11434"
            cfg["agentic_enabled"] = True
            save_ai_config(cfg)
            print(
                f"\n{NEON_GREEN}✓ Successfully pulled {target_model} and set as active Agentic AI!{C_RESET}"
            )
            input(f"\n{C_BOLD}Press Enter to continue...{C_RESET}")
        except Exception as e:
            print(f"\n{NEON_RED}Pull error: {e}{C_RESET}")
            time.sleep(2.0)


def validate_and_sync_models(provider_id, api_key):
    """Validates API credentials with the provider and fetches live model list."""
    p_info = AI_PROVIDERS.get(provider_id)
    if not p_info:
        return False, "Unknown provider ID", []

    base_url = p_info["base_url"]
    p_type = p_info["type"]
    headers = {"User-Agent": "TermuxSentinel/2.0"}

    if p_type == "ollama":
        url = f"{base_url}/api/tags"
    elif p_type == "gemini":
        url = f"{base_url}/models?key={api_key}"
    elif p_type == "anthropic":
        url = f"{base_url}/models"
        headers["x-api-key"] = api_key
        headers["anthropic-version"] = "2023-06-01"
    else:
        url = f"{base_url}/models"
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            live_models = []
            if p_type == "gemini":
                for m in data.get("models", []):
                    name = m.get("name", "").replace("models/", "")
                    if name:
                        live_models.append(name)
            elif p_type == "ollama":
                for m in data.get("models", []):
                    name = m.get("name")
                    if name:
                        live_models.append(name)
            else:
                for m in data.get("data", []):
                    name = m.get("id")
                    if name:
                        live_models.append(name)

            if not live_models:
                live_models = list(p_info.get("default_models", []))
            return True, "", live_models
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            return False, f"Authentication Failed (HTTP {e.code}): Invalid API key", []
        elif e.code == 404:
            return True, "", list(p_info.get("default_models", []))
        return False, f"Provider Error (HTTP {e.code})", []
    except Exception as e:
        if p_type == "ollama":
            return (
                False,
                "Could not connect to Ollama on http://127.0.0.1:11434 (Server not running)",
                [],
            )
        return False, f"Connection Failed: {e}", []


def interactive_ai_setup():
    """Interactive AI Provider selection and Live Sync Model Selector replicating OpenCode AI TUI."""
    get_term_cols()
    print_large_header()
    print_section_h2("AI PROVIDERS & LIVE SYNC MODEL SELECTOR", color=NEON_PINK)

    providers_list = list(AI_PROVIDERS.values())
    print(f"\n{C_BOLD}{BRIGHT_WHITE}SELECT AI PROVIDER:{C_RESET}\n")

    cfg = load_ai_config()
    current_pid = cfg.get("provider", "")

    for idx, p in enumerate(providers_list, 1):
        is_curr = p["id"] == current_pid
        badge = (
            f"{BADGE_GREEN} ACTIVE {C_RESET}"
            if is_curr
            else f"{BADGE_CYAN} {p['badge']} {C_RESET}"
        )
        print(f"  [{idx:2d}] {badge} {BRIGHT_WHITE}{p['name']:<32}{C_RESET}")

    print(f"\n  {TEXT_MUTED}[b] Back to Sentinel{C_RESET}")

    try:
        p_choice = (
            input(
                f"\n{BG_CHARCOAL}{C_BOLD}{NEON_CYAN} Select Provider [1-{len(providers_list)}] ❯ {C_RESET}"
            )
            .strip()
            .lower()
        )
    except (KeyboardInterrupt, EOFError):
        return

    if not p_choice or p_choice == "b":
        return

    if not p_choice.isdigit() or not (1 <= int(p_choice) <= len(providers_list)):
        print(f"{NEON_RED}Invalid provider selection.{C_RESET}")
        time.sleep(1.0)
        return

    sel_provider = providers_list[int(p_choice) - 1]
    p_id = sel_provider["id"]

    api_key = ""
    if p_id != "ollama":
        env_val = os.environ.get(sel_provider["env_key"], "")
        if env_val:
            masked_env = (
                env_val[:4] + "*" * max(0, len(env_val) - 8) + env_val[-4:]
                if len(env_val) > 8
                else "***"
            )
            print(
                f"\n{NEON_GREEN}Detected {sel_provider['env_key']} in environment: {masked_env}{C_RESET}"
            )
            try:
                use_env = input("Use this environment key? (Y/n): ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                return
            if use_env in ("", "y", "yes"):
                api_key = env_val

        if not api_key:
            print(
                f"\n{C_BOLD}{BRIGHT_WHITE}Paste API Key for {sel_provider['name']}:{C_RESET}"
            )
            try:
                api_key = input("❯ ").strip()
            except (KeyboardInterrupt, EOFError):
                return
            if not api_key:
                print(f"{NEON_YELLOW}Setup cancelled. No key entered.{C_RESET}")
                time.sleep(1.0)
                return

    animate_safe(
        "VALIDATING",
        f"Connecting & authenticating with {sel_provider['name']}...",
        duration=0.8,
    )
    ok, err, live_models = validate_and_sync_models(p_id, api_key)

    if not ok:
        print(f"\n{BADGE_RED} VALIDATION FAILED {C_RESET} {NEON_RED}{err}{C_RESET}")
        time.sleep(2.0)
        return

    print(
        f"\n{BADGE_GREEN} VALIDATED {C_RESET} {NEON_GREEN}Credentials verified! Synced {len(live_models)} models.{C_RESET}\n"
    )

    print_divider_h3(f"AVAILABLE MODELS ({sel_provider['name']})", color=NEON_GREEN)
    active_m = cfg.get("model", "")

    display_models = live_models[:25]
    for m_idx, m_name in enumerate(display_models, 1):
        is_active = m_name == active_m
        tag = f"{BADGE_GREEN} ACTIVE {C_RESET}" if is_active else "     "
        print(f"  [{m_idx:2d}] {tag} {BRIGHT_WHITE}{m_name}{C_RESET}")

    if len(live_models) > 25:
        print(f"  {TEXT_MUTED}... and {len(live_models) - 25} more models{C_RESET}")

    try:
        m_choice = input(
            f"\n{BG_CHARCOAL}{C_BOLD}{NEON_GREEN} Select Model [1-{len(display_models)}] ❯ {C_RESET}"
        ).strip()
    except (KeyboardInterrupt, EOFError):
        return

    if not m_choice:
        return

    if m_choice.isdigit() and 1 <= int(m_choice) <= len(display_models):
        chosen_model = display_models[int(m_choice) - 1]
    else:
        chosen_model = m_choice.strip()

    new_cfg = {
        "provider": p_id,
        "provider_name": sel_provider["name"],
        "base_url": sel_provider["base_url"],
        "api_key": api_key,
        "model": chosen_model,
        "agentic_enabled": True,
        "last_validated": time.strftime("%Y-%m-%d %H:%M"),
    }
    save_ai_config(new_cfg)

    dopbase_bin = shutil.which("dopbase")
    if dopbase_bin and api_key:
        try:
            subprocess.run(
                [
                    dopbase_bin,
                    "secret",
                    "set",
                    "termux_sentinel/prod",
                    sel_provider["env_key"],
                    "--stdin",
                ],
                input=api_key.encode("utf-8"),
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass

    print(
        f"\n{NEON_GREEN}✓ Active AI Model configured: {BRIGHT_WHITE}{chosen_model}{NEON_GREEN} ({sel_provider['name']}){C_RESET}"
    )
    print(f"{NEON_GREEN}✓ Agentic AI Mode is now ONLINE!{C_RESET}\n")
    time.sleep(1.5)


def query_agentic_ai(prompt, system_prompt=None, history=None):
    """Executes an AI inference request using configured local Ollama or cloud provider with multi-turn support and thinking control."""
    cfg = load_ai_config()
    p_id = cfg.get("provider", "ollama")
    p_info = AI_PROVIDERS.get(p_id, AI_PROVIDERS["ollama"])
    base_url = cfg.get("base_url", p_info["base_url"])
    model = cfg.get("model", "qwen2.5:3b")
    api_key = cfg.get("api_key", "")
    p_type = p_info["type"]
    thinking_level = cfg.get("thinking_level", "low")
    think_info = THINKING_LEVELS.get(thinking_level, THINKING_LEVELS["low"])

    sys_content = (
        system_prompt
        or "You are Termux Sentinel Autonomous AI Assistant. Keep responses concise, actionable, and strictly under 150 words."
    ) + f"\n[Thinking Directive: {think_info['name']}]: {think_info['prompt']}"

    clean_history = []
    if history and isinstance(history, list):
        # Anchor conversation premise (first 2 turns) + most recent 14 turns so context is never forgotten
        selected = (history[:2] + history[-14:]) if len(history) > 16 else history
        for turn in selected:
            if isinstance(turn, dict) and "role" in turn and "content" in turn:
                clean_history.append({"role": turn["role"], "content": turn["content"]})

    try:
        if p_type == "gemini":
            url = f"{base_url}/models/{model}:generateContent?key={api_key}"
            contents = []
            for turn in clean_history:
                g_role = "user" if turn["role"] == "user" else "model"
                contents.append({"role": g_role, "parts": [{"text": turn["content"]}]})
            if not clean_history:
                contents.append(
                    {"role": "user", "parts": [{"text": f"{sys_content}\n\n{prompt}"}]}
                )
            else:
                contents.append({"role": "user", "parts": [{"text": prompt}]})
            payload_dict = {
                "contents": contents,
                "generationConfig": {
                    "temperature": think_info["temperature"],
                    "maxOutputTokens": think_info["max_tokens"],
                },
            }
            if clean_history:
                payload_dict["systemInstruction"] = {"parts": [{"text": sys_content}]}
            payload = json.dumps(payload_dict).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "TermuxSentinel/2.0",
                },
            )
            with urllib.request.urlopen(req, timeout=25.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw_out = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                return format_thinking_response(raw_out, thinking_level)
        elif p_type == "anthropic":
            url = f"{base_url}/messages"
            messages = []
            for turn in clean_history:
                messages.append({"role": turn["role"], "content": turn["content"]})
            messages.append({"role": "user", "content": prompt})
            payload = json.dumps(
                {
                    "model": model,
                    "system": sys_content,
                    "messages": messages,
                    "max_tokens": think_info["max_tokens"],
                }
            ).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "User-Agent": "TermuxSentinel/2.0",
                },
            )
            with urllib.request.urlopen(req, timeout=25.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw_out = data["content"][0]["text"].strip()
                return format_thinking_response(raw_out, thinking_level)
        elif p_type == "ollama":
            stat = get_ollama_live_status(base_url)
            if not stat["running"]:
                return f"Error: Ollama daemon is not responding on {base_url}. Start it via 'sentinel ai inspect' or run 'ollama serve' in background."
            m_base = model.split(":")[0] if model else ""
            if not any(
                model in pm or (m_base and m_base == pm.split(":")[0])
                for pm in stat["pulled_models"]
            ):
                return (
                    f"Error: Model '{model}' is not downloaded in Ollama storage.\n"
                    f"Please run 'sentinel ai inspect' or 'ollama pull {model}' to download it first."
                )
            url_chat = f"{base_url}/api/chat"
            messages = [{"role": "system", "content": sys_content}]
            for turn in clean_history:
                messages.append({"role": turn["role"], "content": turn["content"]})
            messages.append({"role": "user", "content": prompt})
            payload_chat_dict = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": think_info["temperature"],
                    "num_predict": think_info["max_tokens"],
                },
            }
            if thinking_level == "none":
                payload_chat_dict["think"] = False
            payload_chat = json.dumps(payload_chat_dict).encode("utf-8")
            req_chat = urllib.request.Request(
                url_chat,
                data=payload_chat,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "TermuxSentinel/2.0",
                },
            )
            try:
                with urllib.request.urlopen(req_chat, timeout=30.0) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    raw_out = data.get("message", {}).get("content", "").strip()
                    return format_thinking_response(raw_out, thinking_level)
            except Exception:
                url_gen = f"{base_url}/api/generate"
                prompt_full = f"{sys_content}\n\n"
                for turn in clean_history:
                    prompt_full += f"{turn['role'].upper()}: {turn['content']}\n"
                prompt_full += f"USER: {prompt}\nASSISTANT: "
                payload_gen_dict = {
                    "model": model,
                    "prompt": prompt_full,
                    "stream": False,
                    "options": {
                        "temperature": think_info["temperature"],
                        "num_predict": think_info["max_tokens"],
                    },
                }
                if thinking_level == "none":
                    payload_gen_dict["think"] = False
                payload_gen = json.dumps(payload_gen_dict).encode("utf-8")
                req_gen = urllib.request.Request(
                    url_gen,
                    data=payload_gen,
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "TermuxSentinel/2.0",
                    },
                )
                with urllib.request.urlopen(req_gen, timeout=30.0) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    raw_out = data.get("response", "").strip()
                    return format_thinking_response(raw_out, thinking_level)
        else:
            url = f"{base_url}/chat/completions"
            messages = [{"role": "system", "content": sys_content}]
            for turn in clean_history:
                messages.append({"role": turn["role"], "content": turn["content"]})
            messages.append({"role": "user", "content": prompt})
            payload_dict = {
                "model": model,
                "messages": messages,
                "temperature": think_info["temperature"],
                "max_tokens": think_info["max_tokens"],
            }
            if think_info.get("reasoning_effort") and any(
                k in model.lower() for k in ("o1", "o3", "deepseek-r1")
            ):
                payload_dict["reasoning_effort"] = think_info["reasoning_effort"]
            payload = json.dumps(payload_dict).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                    "User-Agent": "TermuxSentinel/2.0",
                },
            )
            with urllib.request.urlopen(req, timeout=25.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw_out = data["choices"][0]["message"]["content"].strip()
                return format_thinking_response(raw_out, thinking_level)
    except Exception as e:
        return f"Inference Failed ({p_info['name']}): {e}"


def copy_to_clipboard(text):
    """Copies text to Android or system clipboard using Termux API or platform clipboards."""
    if not text:
        return False, "Nothing to copy."
    # 1. Termux API (Android)
    if shutil.which("termux-clipboard-set"):
        try:
            p = subprocess.Popen(
                ["termux-clipboard-set"],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            p.communicate(input=text.encode("utf-8"), timeout=3)
            if p.returncode == 0:
                return True, "Copied to Android clipboard via termux-clipboard-set."
        except Exception:
            pass
    # 2. Linux Wayland
    if shutil.which("wl-copy"):
        try:
            p = subprocess.Popen(
                ["wl-copy"],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            p.communicate(input=text.encode("utf-8"), timeout=3)
            if p.returncode == 0:
                return True, "Copied to clipboard via wl-copy."
        except Exception:
            pass
    # 3. Linux X11
    if shutil.which("xclip"):
        try:
            p = subprocess.Popen(
                ["xclip", "-selection", "clipboard"],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            p.communicate(input=text.encode("utf-8"), timeout=3)
            if p.returncode == 0:
                return True, "Copied to clipboard via xclip."
        except Exception:
            pass
    # 4. Windows
    if shutil.which("clip"):
        try:
            p = subprocess.Popen(
                ["clip"],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            p.communicate(input=text.encode("utf-8"), timeout=3)
            if p.returncode == 0:
                return True, "Copied to clipboard via clip."
        except Exception:
            pass
    return False, "Clipboard tool not found (install termux-api or xclip)."


def export_chat_transcript(history, filename=None):
    """Exports chat session history to a markdown file in ~/.config/termux_sentinel/transcripts/."""
    try:
        os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
        if not filename:
            ts = time.strftime("%Y%m%d_%H%M%S")
            filename = f"sentinel_chat_{ts}.md"
        elif not filename.endswith(".md"):
            filename += ".md"
        safe_fname = os.path.basename(filename)
        out_path = os.path.join(TRANSCRIPTS_DIR, safe_fname)

        cfg = load_ai_config()
        used, total, free, pct = get_disk_usage()

        lines = [
            "# Termux Sentinel AI Chat Transcript",
            f"- **Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"- **Device**: {get_device_name()}",
            f"- **Storage**: {used} used / {free} free of {total} ({pct} full)",
            f"- **Provider**: {cfg.get('provider_name', 'Ollama')}",
            f"- **Model**: {cfg.get('model', 'None')}",
            "",
            "---",
            "",
        ]

        if not history:
            lines.append("*(No conversation turns recorded)*\n")
        else:
            for turn in history:
                role = turn.get("role", "user")
                content = turn.get("content", "")
                if role == "user":
                    lines.append(f"### 👤 User\n\n{content}\n")
                elif role == "assistant":
                    lines.append(f"### 🤖 Sentinel AI\n\n{content}\n")
                lines.append("---\n")

        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return True, out_path
    except Exception as e:
        return False, str(e)


def interactive_ai_chat():
    """Dedicated interactive AI Chat Studio TUI with persistent multi-session memory, thinking controls & telemetry."""
    cols = get_term_cols()
    curr_session = load_active_session()
    history = curr_session.get("history", [])

    print("\033[2J\033[H", end="")
    print_large_header()
    render_hud_box("AI CHAT STUDIO")

    cfg = load_ai_config()
    p_name = cfg.get("provider_name", "Ollama")
    m_name = cfg.get("model", "None")
    thinking_level = cfg.get("thinking_level", "low")
    think_badge = THINKING_LEVELS.get(thinking_level, THINKING_LEVELS["low"])["badge"]

    sess_title = curr_session.get("title", "Active Session")
    if len(sess_title) > 28:
        sess_title = sess_title[:25] + "..."

    banner_title = "═ AI CHAT STUDIO ═"
    print(
        f"\n{NEON_CYAN}╔═{banner_title}"
        + "═" * max(0, cols - 4 - visible_len(banner_title))
        + f"╗{C_RESET}"
    )
    print(
        make_box_row(
            f"{C_BOLD}{BRIGHT_WHITE}Interactive Autonomous Terminal AI Assistant{C_RESET}",
            border_color=NEON_CYAN,
            cols=cols,
        )
    )
    print(
        make_box_row(
            f"Provider: {NEON_GREEN}{p_name}{C_RESET} | Model: {NEON_CYAN}{m_name}{C_RESET} | Thinking: {NEON_YELLOW}{think_badge}{C_RESET}",
            border_color=NEON_CYAN,
            cols=cols,
        )
    )
    print(
        make_box_row(
            f"Session: {BRIGHT_WHITE}{sess_title}{C_RESET} {TEXT_MUTED}({len(history)} msgs){C_RESET} | {TEXT_MUTED}/thinking, /session, /new, /help{C_RESET}",
            border_color=NEON_CYAN,
            cols=cols,
        )
    )
    print(f"{NEON_CYAN}╚" + "═" * (cols - 2) + f"╝{C_RESET}\n")

    if history:
        print(
            f"{NEON_GREEN}✓ Resumed persistent session:{C_RESET} {BRIGHT_WHITE}'{curr_session.get('title')}'{C_RESET} {TEXT_MUTED}({len(history)} messages in memory){C_RESET}"
        )
        print(
            f"{TEXT_MUTED}  Commands: /new (fresh session), /session (manage sessions), /thinking (speed/depth){C_RESET}\n"
        )

    while True:
        try:
            prompt_marker = (
                f"{NEON_GREEN}╭─ 👤 YOU{C_RESET} {TEXT_MUTED}[type /help for commands, /exit to quit]{C_RESET}\n"
                f"{NEON_GREEN}╰─➤ {C_RESET}"
            )
            user_input = input(prompt_marker).strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{NEON_YELLOW}Exiting AI Chat Studio...{C_RESET}\n")
            break

        if not user_input:
            continue

        lower = user_input.lower().strip()
        if lower in ("/exit", "/quit", ":q", "exit", "quit"):
            print(
                f"\n{NEON_YELLOW}Session closed & saved to disk. Returning to Sentinel...{C_RESET}\n"
            )
            break

        if lower in ("/help", "/?", "?"):
            print(
                f"\n{NEON_CYAN}╔═ 📖 AI CHAT STUDIO SLASH COMMANDS ═══════════════════════════════╗{C_RESET}"
            )
            help_cmds = [
                ("/help, /?", "Show this command manual"),
                (
                    "/thinking [lvl]",
                    "Set thinking depth: none, low (default), medium, extra",
                ),
                ("/session", "List all persistent conversation sessions"),
                ("/new [title]", "Start a fresh conversation session"),
                ("/load <#|id>", "Load an earlier saved conversation session"),
                ("/rename <title>", "Rename the current conversation session"),
                ("/status", "Display live system telemetry HUD"),
                ("/model", "Switch AI provider, model or update API key"),
                ("/inspect", "Audit hardware & recommend offline Ollama models"),
                ("/clean", "Execute safe cache purge directly"),
                ("/hunt [MB]", "Scan bloat directories (default: 100MB)"),
                ("/doctor", "Run system diagnostic health check"),
                ("/repair", "Auto-heal broken packages & dependencies"),
                ("/vault", "List protected directories and active shields"),
                ("/copy", "Copy last AI response to system/Android clipboard"),
                ("/export [name]", "Save chat transcript to markdown in transcripts/"),
                ("/clear, /reset", "Clear messages in the current session"),
                ("/sh <cmd>, !<cmd>", "Run shell command and analyze output in chat"),
                ("/exit, /quit", "Exit AI Chat Studio and return to Sentinel"),
            ]
            for cmd_name, desc in help_cmds:
                print(
                    f"  {NEON_YELLOW}{cmd_name:<18}{C_RESET} {BRIGHT_WHITE}{desc}{C_RESET}"
                )
            print(
                f"{NEON_CYAN}╚══════════════════════════════════════════════════════════════════╝{C_RESET}\n"
            )
            continue

        if lower.startswith("/thinking") or lower.startswith("/reasoning"):
            parts = user_input.split(maxsplit=1)
            if len(parts) > 1:
                target_lvl = parts[1].strip()
                ok, res_name = set_thinking_level(target_lvl)
                if ok:
                    print(
                        f"\n{NEON_GREEN}✓ Thinking Level updated to:{C_RESET} {BRIGHT_WHITE}{res_name}{C_RESET}\n"
                    )
                else:
                    print(f"\n{NEON_RED}✗ {res_name}{C_RESET}\n")
            else:
                cfg = load_ai_config()
                cur_lvl = cfg.get("thinking_level", "low")
                print(
                    f"\n{NEON_CYAN}╔═ 🧠 OLLAMA & AI THINKING SETTINGS ═══════════════════════════════╗{C_RESET}"
                )
                print(
                    f" Current Level: {NEON_GREEN}{THINKING_LEVELS.get(cur_lvl, {}).get('name', 'Low')}{C_RESET}\n"
                )
                print(
                    f"  [1] {BRIGHT_WHITE}No Thinking{C_RESET}    {TEXT_MUTED}- Instant answers; strips <think> blocks completely{C_RESET}"
                )
                print(
                    f"  [2] {BRIGHT_WHITE}Low Thinking{C_RESET}   {TEXT_MUTED}- Quick 1-2 bullet thoughts; battery & CPU optimized (DEFAULT){C_RESET}"
                )
                print(
                    f"  [3] {BRIGHT_WHITE}Medium Thinking{C_RESET}{TEXT_MUTED}- Balanced step-by-step reasoning{C_RESET}"
                )
                print(
                    f"  [4] {BRIGHT_WHITE}Extra Thinking{C_RESET} {TEXT_MUTED}- Deep chain-of-thought analysis{C_RESET}"
                )
                print(
                    f"{NEON_CYAN}╚══════════════════════════════════════════════════════════════════╝{C_RESET}"
                )
                try:
                    choice = input(
                        f"{NEON_YELLOW}Select thinking level [1-4 or Enter to keep]: {C_RESET}"
                    ).strip()
                except (KeyboardInterrupt, EOFError):
                    continue
                choice_map = {"1": "none", "2": "low", "3": "medium", "4": "extra"}
                if choice in choice_map:
                    _, res_name = set_thinking_level(choice_map[choice])
                    print(
                        f"\n{NEON_GREEN}✓ Thinking level set to: {res_name}{C_RESET}\n"
                    )
            continue

        if lower.startswith("/new"):
            parts = user_input.split(maxsplit=1)
            title = parts[1].strip() if len(parts) > 1 else None
            curr_session = create_new_session(title)
            history = []
            print(
                f"\n{NEON_GREEN}✓ Started fresh session:{C_RESET} {BRIGHT_WHITE}'{curr_session['title']}'{C_RESET}\n"
            )
            continue

        if lower.startswith("/load"):
            parts = user_input.split(maxsplit=1)
            if len(parts) < 2:
                print(f"\n{NEON_YELLOW}Usage: /load <# or session_id>{C_RESET}\n")
                continue
            ok, loaded = load_session_by_id(parts[1])
            if ok:
                curr_session = loaded
                history = curr_session.get("history", [])
                print(
                    f"\n{NEON_GREEN}✓ Loaded session:{C_RESET} {BRIGHT_WHITE}'{curr_session['title']}'{C_RESET} "
                    f"{TEXT_MUTED}({len(history)} messages restored){C_RESET}\n"
                )
            else:
                print(f"\n{NEON_RED}✗ {loaded}{C_RESET}\n")
            continue

        if lower.startswith("/rename"):
            parts = user_input.split(maxsplit=1)
            if len(parts) < 2:
                print(f"\n{NEON_YELLOW}Usage: /rename <new session title>{C_RESET}\n")
                continue
            curr_session["title"] = parts[1].strip()
            save_active_session(curr_session)
            print(
                f"\n{NEON_GREEN}✓ Session renamed to:{C_RESET} {BRIGHT_WHITE}'{curr_session['title']}'{C_RESET}\n"
            )
            continue

        if lower.startswith("/session") or lower.startswith("/sessions"):
            parts = user_input.split()
            subcmd = parts[1].lower() if len(parts) > 1 else "list"
            if subcmd == "new":
                title = " ".join(parts[2:]) if len(parts) > 2 else None
                curr_session = create_new_session(title)
                history = []
                print(
                    f"\n{NEON_GREEN}✓ Started fresh session:{C_RESET} {BRIGHT_WHITE}'{curr_session['title']}'{C_RESET}\n"
                )
            elif subcmd == "load":
                if len(parts) < 3:
                    print(
                        f"\n{NEON_YELLOW}Usage: /session load <# or session_id>{C_RESET}\n"
                    )
                else:
                    ok, loaded = load_session_by_id(parts[2])
                    if ok:
                        curr_session = loaded
                        history = curr_session.get("history", [])
                        print(
                            f"\n{NEON_GREEN}✓ Loaded session:{C_RESET} {BRIGHT_WHITE}'{curr_session['title']}'{C_RESET} "
                            f"{TEXT_MUTED}({len(history)} messages restored){C_RESET}\n"
                        )
                    else:
                        print(f"\n{NEON_RED}✗ {loaded}{C_RESET}\n")
            elif subcmd == "delete":
                if len(parts) < 3:
                    print(
                        f"\n{NEON_YELLOW}Usage: /session delete <# or session_id>{C_RESET}\n"
                    )
                else:
                    ok, msg = delete_session_by_id(parts[2])
                    print(f"\n{NEON_GREEN if ok else NEON_RED}{msg}{C_RESET}\n")
            else:
                # List sessions
                all_sessions = list_saved_sessions()
                print(
                    f"\n{NEON_CYAN}╔═ 💬 PERSISTENT CONVERSATION SESSIONS ({len(all_sessions)}) ═══════════╗{C_RESET}"
                )
                if not all_sessions:
                    print(f"  {TEXT_MUTED}No previous sessions archived yet.{C_RESET}")
                else:
                    for i, s in enumerate(all_sessions[:10], 1):
                        is_active = s.get("session_id") == curr_session.get(
                            "session_id"
                        )
                        tag = (
                            f"{NEON_GREEN}● ACTIVE{C_RESET}"
                            if is_active
                            else f"{TEXT_MUTED}○{C_RESET}"
                        )
                        title_disp = s.get("title", "Untitled")[:30]
                        turns_cnt = len(s.get("history", []))
                        upd = s.get("updated_at", "")[5:16]
                        print(
                            f"  [{i:2d}] {tag} {BRIGHT_WHITE}{title_disp:<30}{C_RESET} {NEON_CYAN}{turns_cnt:2d} msgs{C_RESET} {TEXT_MUTED}{upd}{C_RESET}"
                        )
                print(
                    f"{NEON_CYAN}╚══════════════════════════════════════════════════════════════════╝{C_RESET}"
                )
                print(
                    f"{TEXT_MUTED}Commands: /session new [title], /session load <#>, /session delete <#>{C_RESET}\n"
                )
            continue

        if lower == "/status":
            print()
            render_hud_box("LIVE TELEMETRY")
            print()
            continue

        if lower in ("/clear", "/reset"):
            history.clear()
            curr_session["history"] = []
            save_active_session(curr_session)
            print(
                f"\n{NEON_GREEN}✓ Conversation memory for active session cleared.{C_RESET}\n"
            )
            continue

        if lower in ("/model", "/provider", "/setup"):
            interactive_ai_setup()
            cfg = load_ai_config()
            p_name = cfg.get("provider_name", "Ollama")
            m_name = cfg.get("model", "None")
            print(f"\n{NEON_GREEN}✓ Active AI set to: {p_name} ({m_name}){C_RESET}\n")
            continue

        if lower in ("/inspect", "/hardware", "/hw"):
            render_hardware_inspection_view()
            cfg = load_ai_config()
            continue

        if lower == "/clean":
            print(f"\n{NEON_YELLOW}Running safe cache cleanup...{C_RESET}")
            cli_clean(safe_only=True, dry_run=False, auto_yes=True)
            print()
            continue

        if lower.startswith("/hunt"):
            parts = user_input.split()
            mb = 100
            if len(parts) > 1 and parts[1].isdigit():
                mb = int(parts[1])
            print(f"\n{NEON_YELLOW}Scanning for bloat directories >{mb}MB...{C_RESET}")
            cli_hunt(threshold_mb=mb)
            print()
            continue

        if lower == "/doctor":
            print(f"\n{NEON_YELLOW}Running Sentinel System Diagnostics...{C_RESET}")
            cli_repair(auto_fix=False)
            print()
            continue

        if lower == "/repair":
            print(f"\n{NEON_YELLOW}Auto-repairing system dependencies...{C_RESET}")
            cli_repair(auto_fix=True)
            print()
            continue

        if lower == "/vault":
            items = load_vault()
            print(
                f"\n{NEON_CYAN}╔═ 🛡️ ACTIVE PRESERVATION SHIELDS ({len(items)}) ═══════════════════╗{C_RESET}"
            )
            for it in items:
                lock_icon = "🔒" if it.get("locked") else "🛡️"
                print(
                    f"  {lock_icon} {BRIGHT_WHITE}#{it.get('id', 0):<2} {it.get('name')}{C_RESET}: {TEXT_MUTED}{it.get('pattern')}{C_RESET}"
                )
            print(
                f"{NEON_CYAN}╚══════════════════════════════════════════════════════════════════╝{C_RESET}\n"
            )
            continue

        if lower == "/copy":
            last_resp = None
            for turn in reversed(history):
                if turn.get("role") == "assistant":
                    last_resp = turn.get("content", "")
                    break
            if not last_resp:
                print(f"\n{NEON_YELLOW}No AI response in history to copy.{C_RESET}\n")
            else:
                ok, msg = copy_to_clipboard(last_resp)
                if ok:
                    print(f"\n{NEON_GREEN}✓ {msg}{C_RESET}\n")
                else:
                    print(f"\n{NEON_RED}✗ {msg}{C_RESET}\n")
            continue

        if lower.startswith("/export"):
            parts = user_input.split(maxsplit=1)
            fname = parts[1].strip() if len(parts) > 1 else None
            ok, out_path = export_chat_transcript(history, fname)
            if ok:
                print(
                    f"\n{NEON_GREEN}✓ Transcript exported successfully:{C_RESET} {BRIGHT_WHITE}{out_path}{C_RESET}\n"
                )
            else:
                print(
                    f"\n{NEON_RED}✗ Failed to export transcript: {out_path}{C_RESET}\n"
                )
            continue

        if lower.startswith("/sh ") or user_input.startswith("!"):
            cmd = (
                user_input[4:].strip()
                if lower.startswith("/sh ")
                else user_input[1:].strip()
            )
            if not cmd:
                print(f"\n{NEON_YELLOW}Usage: /sh <command> or !<command>{C_RESET}\n")
                continue
            print(
                f"\n{NEON_CYAN}╭─ 💻 EXEC: {BRIGHT_WHITE}{cmd}{NEON_CYAN} ─────────────────────────────{C_RESET}"
            )
            try:
                proc = subprocess.run(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=30,
                )
                output = proc.stdout.strip()
                if output:
                    for line in output.splitlines()[:25]:
                        print(f"{NEON_CYAN}│{C_RESET}  {BRIGHT_WHITE}{line}{C_RESET}")
                    if len(output.splitlines()) > 25:
                        print(
                            f"{NEON_CYAN}│{C_RESET}  {TEXT_MUTED}... [{len(output.splitlines()) - 25} lines truncated]{C_RESET}"
                        )
                else:
                    print(
                        f"{NEON_CYAN}│{C_RESET}  {TEXT_MUTED}(no output, exit code: {proc.returncode}){C_RESET}"
                    )
                print(
                    f"{NEON_CYAN}╰──────────────────────────────────────────────────────────{C_RESET}\n"
                )
                history.append(
                    {
                        "role": "user",
                        "content": f"[Executed Shell Command: `{cmd}`]\nOutput (Exit Code {proc.returncode}):\n{output[:1500]}",
                    }
                )
                history.append(
                    {
                        "role": "assistant",
                        "content": f"I observed the output of `{cmd}` (exit code {proc.returncode}). What would you like to analyze or do next with it?",
                    }
                )
                curr_session["history"] = history
                save_active_session(curr_session)
            except subprocess.TimeoutExpired:
                print(f"{NEON_RED}│ Command timed out after 30 seconds.{C_RESET}")
                print(
                    f"{NEON_CYAN}╰──────────────────────────────────────────────────────────{C_RESET}\n"
                )
            except Exception as e:
                print(f"{NEON_RED}│ Execution error: {e}{C_RESET}")
                print(
                    f"{NEON_CYAN}╰──────────────────────────────────────────────────────────{C_RESET}\n"
                )
            continue

        cfg = load_ai_config()
        used, total, free, pct = get_disk_usage()
        v_cnt = len(load_vault())
        active_model = cfg.get("model", "qwen2.5:3b")

        system_prompt = (
            f"You are Termux Sentinel Autonomous AI Assistant running locally inside Termux Android CLI.\n"
            f"System Telemetry: Device={get_device_name()}, Storage={used} used / {free} free of {total} ({pct} full), "
            f"Active Vault Shields={v_cnt}.\n"
            f"Critical Safety Rule: Never suggest deleting WhatsApp directories (com.whatsapp, com.whatsapp.w4b). "
            f"Be concise, highly practical, technically precise, and formatted in terminal-friendly markdown."
        )

        animate_safe("THINKING", f"Querying {active_model}...", duration=0.6)
        resp = query_agentic_ai(
            user_input, system_prompt=system_prompt, history=history
        )

        print(
            f"\n{NEON_PINK}╭─ 🤖 SENTINEL AI {C_RESET}{TEXT_MUTED}[{active_model}]{NEON_PINK} "
            + "─" * max(0, cols - visible_len(active_model) - 23)
            + f"{C_RESET}"
        )
        wrapper = textwrap.TextWrapper(
            width=max(36, cols - 6), break_long_words=False, replace_whitespace=False
        )
        for line in resp.splitlines():
            if not line.strip():
                print(f"{NEON_PINK}│{C_RESET}")
            else:
                wrapped_lines = wrapper.wrap(line)
                for w in wrapped_lines:
                    print(f"{NEON_PINK}│{C_RESET}  {BRIGHT_WHITE}{w}{C_RESET}")
        print(f"{NEON_PINK}╰" + "─" * (cols - 2) + f"{C_RESET}\n")

        history.append(
            {
                "role": "user",
                "content": user_input,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
        history.append(
            {
                "role": "assistant",
                "content": resp,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

        # Auto-update generic session title from first user query
        if curr_session.get("title", "").startswith("Session ") and user_input:
            curr_session["title"] = user_input[:32] + (
                "..." if len(user_input) > 32 else ""
            )

        curr_session["history"] = history
        save_active_session(curr_session)


def run_agentic_ai_advisor(
    clean_targets=None, apps_targets=None, bot_scripts=None, running_daemons=None
):
    """Feeds live system telemetry into the AI engine to generate an intelligent maintenance plan."""
    get_term_cols()
    print_large_header()
    print_section_h2("AGENTIC AI SYSTEM ADVISOR & AUTONOMOUS PLANNER", color=NEON_PINK)

    cfg = load_ai_config()
    print(
        f" Active Model: {NEON_GREEN}{cfg.get('model', 'None')}{C_RESET} ({cfg.get('provider_name', 'Ollama')})"
    )

    used, total, free, pct = get_disk_usage()
    if clean_targets is None:
        clean_targets = define_cleaning_targets()
    if running_daemons is None:
        running_daemons = scan_running_daemons()
    if bot_scripts is None:
        bot_scripts = scan_bot_scripts()

    reclaim_b = sum([t.get("size_bytes", 0) for t in clean_targets])
    top_clean = ", ".join(
        [
            f"{t['name']} ({human_size(t.get('size_bytes', 0))})"
            for t in clean_targets
            if t.get("size_bytes", 0) > 0
        ][:3]
    )
    daemon_summary = (
        ", ".join([d.get("dtype", "Worker") for d in running_daemons[:3]]) or "None"
    )

    context_prompt = (
        f"Device: {get_device_name()}\n"
        f"Storage: {used} used / {free} free of {total} ({pct} full)\n"
        f"Cleanable Caches: {human_size(reclaim_b)} across {len(clean_targets)} targets ({top_clean})\n"
        f"Background Daemons: {len(running_daemons)} detected ({daemon_summary})\n\n"
        f"Provide a concise, 3-point bullet action plan for maintenance. "
        f"Explain what is safest to purge and any warnings for active daemons."
    )

    animate_safe(
        "REASONING",
        "Agentic AI analyzing system telemetry & formulating plan...",
        duration=0.8,
    )
    advice = query_agentic_ai(context_prompt)

    print(
        f"\n{NEON_CYAN}╔═ 🤖 AGENTIC AI ACTION PLAN ══════════════════════════╗{C_RESET}"
    )
    for line in advice.splitlines():
        if line.strip():
            print(f"  {BRIGHT_WHITE}{line}{C_RESET}")
    print(
        f"{NEON_CYAN}╚═══════════════════════════════════════════════════════╝{C_RESET}"
    )

    print(
        f"\n{C_BOLD}{BRIGHT_WHITE}Execute recommended safe system cleanup now? (y/N): {C_RESET}",
        end="",
    )
    try:
        conf = input().strip().lower()
    except (KeyboardInterrupt, EOFError):
        return
    if conf in ("y", "yes"):
        cli_clean(safe_only=True, dry_run=False, auto_yes=True)
    else:
        print(f"\n{NEON_YELLOW}Cleanup skipped by user.{C_RESET}\n")
    input(f"{C_BOLD}Press Enter to return...{C_RESET}")


def cli_ai(action="menu", *args):
    """CLI subcommand router for Sentinel AI features."""
    if action in ("chat", "talk", "repl", "interactive", "studio"):
        interactive_ai_chat()
    elif action in ("thinking", "think", "reasoning"):
        if args:
            ok, name = set_thinking_level(args[0])
            if ok:
                print(
                    f"{NEON_GREEN}✓ Thinking Level updated to:{C_RESET} {BRIGHT_WHITE}{name}{C_RESET}"
                )
            else:
                print(f"{NEON_RED}✗ {name}{C_RESET}")
        else:
            cfg = load_ai_config()
            cur = cfg.get("thinking_level", "low")
            info = THINKING_LEVELS.get(cur, {})
            print(
                f"Current Thinking Level: {NEON_GREEN}{info.get('name', 'Low')}{C_RESET} ({info.get('desc', '')})"
            )
            print("Available options: none, low (default), medium, extra")
    elif action in ("sessions", "session"):
        sub = args[0].lower() if args else "list"
        if sub == "new":
            t = " ".join(args[1:]) if len(args) > 1 else None
            s = create_new_session(t)
            print(f"{NEON_GREEN}✓ Started fresh session:{C_RESET} {s['title']}")
        elif sub == "load":
            if len(args) < 2:
                print(f"{NEON_YELLOW}Usage: sentinel ai session load <#|id>{C_RESET}")
            else:
                ok, s = load_session_by_id(args[1])
                if ok:
                    print(f"{NEON_GREEN}✓ Loaded session: {s.get('title')}{C_RESET}")
                else:
                    print(f"{NEON_RED}{s}{C_RESET}")
        else:
            sess_list = list_saved_sessions()
            print_large_header()
            print_section_h2(
                f"SAVED CONVERSATION SESSIONS ({len(sess_list)})",
                color=NEON_PINK,
            )
            for i, s in enumerate(sess_list, 1):
                print(
                    f"  [{i:2d}] {BRIGHT_WHITE}{s.get('title', 'Untitled'):<32}{C_RESET} {NEON_CYAN}{len(s.get('history', [])):2d} msgs{C_RESET} {TEXT_MUTED}{s.get('updated_at', '')}{C_RESET}"
                )
    elif action in ("inspect", "hardware", "hw"):
        render_hardware_inspection_view()
    elif action in ("setup", "config", "providers", "provider"):
        interactive_ai_setup()
    elif action in ("toggle", "switch"):
        new_s = toggle_agentic_mode()
        print(
            f"{NEON_GREEN if new_s else NEON_YELLOW}Agentic AI Mode is now {'ENABLED' if new_s else 'DISABLED'}.{C_RESET}"
        )
    elif action in ("advise", "plan", "analyze"):
        run_agentic_ai_advisor()
    elif (
        action in ("ask", "query") or args or (action not in ("menu", "status", "info"))
    ):
        prompt = " ".join([action] + list(args)) if action != "ask" else " ".join(args)
        cfg = load_ai_config()
        print(f"\n{NEON_CYAN}[AI Query] {BRIGHT_WHITE}{prompt}{C_RESET}")
        print(
            f"{TEXT_MUTED}Model: {cfg.get('model')} ({cfg.get('provider_name')}){C_RESET}\n"
        )
        resp = query_agentic_ai(prompt)
        print(f"{BRIGHT_WHITE}{resp}{C_RESET}\n")
    else:
        cfg = load_ai_config()
        ai_stat = get_ai_runtime_status(cfg)
        print_large_header()
        print_section_h2("SENTINEL AGENTIC AI STATUS", color=NEON_PINK)
        print(f"  Agent Status   : {ai_stat['badge']}")
        print(
            f"  Provider       : {NEON_CYAN}{cfg.get('provider_name', 'Ollama')}{C_RESET}"
        )
        print(f"  Target Model   : {BRIGHT_WHITE}{cfg.get('model', 'None')}{C_RESET}")
        cur_think = cfg.get("thinking_level", "low")
        think_info = THINKING_LEVELS.get(cur_think, THINKING_LEVELS["low"])
        print(
            f"  Thinking Level : {NEON_YELLOW}{think_info.get('name', 'Low')}{C_RESET} ({think_info.get('badge', '')})"
        )
        print(f"  Endpoint URL   : {TEXT_MUTED}{cfg.get('base_url', 'N/A')}{C_RESET}")

        if cfg.get("provider") == "ollama":
            daemon_txt = (
                f"{NEON_GREEN}● Connected (127.0.0.1:11434 responding HTTP 200){C_RESET}"
                if ai_stat["daemon_live"]
                else f"{NEON_RED}○ Inactive / Unreachable{C_RESET}"
            )
            print(f"  Live Daemon    : {daemon_txt}")
            pulled = ai_stat.get("pulled_models", [])
            if pulled:
                print(f"  Storage Models : {NEON_CYAN}{', '.join(pulled)}{C_RESET}")
            else:
                print(
                    f"  Storage Models : {NEON_YELLOW}0 models in storage (None downloaded yet){C_RESET}"
                )

            if not ai_stat["model_in_storage"]:
                print(
                    f"\n  {BADGE_YELLOW} ATTENTION {C_RESET} {NEON_YELLOW}Model '{cfg.get('model')}' is NOT downloaded in your storage.{C_RESET}"
                )
                print(
                    f"  {TEXT_MUTED}Run 'sentinel ai inspect' or 'ollama pull {cfg.get('model')}' to download it.{C_RESET}"
                )
        print(f"\n{C_BOLD}{BRIGHT_WHITE}AI SUBCOMMANDS:{C_RESET}")
        print(
            f"  {NEON_YELLOW}sentinel ai chat     {C_RESET} {TEXT_MUTED}Interactive Cyber AI Chat Studio{C_RESET}"
        )
        print(
            f"  {NEON_YELLOW}sentinel ai inspect  {C_RESET} {TEXT_MUTED}Audit Device & Suggest Ollama Models{C_RESET}"
        )
        print(
            f"  {NEON_YELLOW}sentinel ai setup    {C_RESET} {TEXT_MUTED}Configure Cloud/Local Provider & Sync{C_RESET}"
        )
        print(
            f"  {NEON_YELLOW}sentinel ai toggle   {C_RESET} {TEXT_MUTED}Toggle Agentic AI Mode ON/OFF{C_RESET}"
        )
        print(
            f"  {NEON_YELLOW}sentinel ai advise   {C_RESET} {TEXT_MUTED}Run Autonomous System Optimization Plan{C_RESET}"
        )
        print(
            f"  {NEON_YELLOW}sentinel ai thinking {C_RESET} {TEXT_MUTED}Set Thinking: none, low, medium, extra{C_RESET}"
        )
        print(
            f"  {NEON_YELLOW}sentinel ai sessions {C_RESET} {TEXT_MUTED}List Saved Persistent Multi-Sessions{C_RESET}"
        )
        print(
            f'  {NEON_YELLOW}sentinel ai "query"  {C_RESET} {TEXT_MUTED}Ask AI Agent with System Telemetry{C_RESET}\n'
        )


def cli_help():
    cols = get_term_cols()
    print_large_header()
    title = "═ TERMUX SENTINEL CLI MANUAL "
    fill = max(0, cols - 2 - visible_len(title))
    print(f"{NEON_CYAN}╔{title}" + "═" * fill + f"╗{C_RESET}")
    print(
        make_box_row(
            f"{BRIGHT_WHITE}Global: sentinel [subcommand] [flags]{C_RESET}",
            border_color=NEON_CYAN,
            cols=cols,
        )
    )
    print(f"{NEON_CYAN}╚" + "═" * (cols - 2) + f"╝{C_RESET}")
    print(f"\n{C_BOLD}{BRIGHT_WHITE}COMMANDS:{C_RESET}")

    cmds = [
        ("sentinel", "Interactive Cyber UI"),
        ("sentinel status", "Live Telemetry HUD"),
        ("sentinel audit", "Full System Audit"),
        ("sentinel clean", "Purge Safe Caches"),
        ("sentinel clean -a", "Purge All Caches"),
        ("sentinel clean -d", "Dry-Run Preview"),
        ("sentinel clean -y", "Auto-Confirm Clean"),
        ("sentinel vault", "List Preserved Vault"),
        ("sentinel vault add", "Shield Path/Pattern"),
        ("sentinel vault rm", "Remove Shield by ID"),
        ("sentinel apps", "List Installed Apps"),
        ("sentinel apps rm", "Uninstall App/Debris"),
        ("sentinel bots", "Scan Rogue Scripts"),
        ("sentinel bots kill", "Kill Daemon by PID"),
        ("sentinel update", "Upgrade All Packages"),
        ("sentinel cloud", "View Live Cloud Sync"),
        ("sentinel cloud -s", "Start Background Sync"),
        ("sentinel hunt", "Scan Bloat Dirs >100M"),
        ("sentinel hunt [MB]", "Custom Bloat Threshold"),
        ("sentinel offload <path>", "Move Dir to Cloud"),
        ("sentinel auto-clean", "Headless Auto Prune"),
        ("sentinel doctor", "System Health Check"),
        ("sentinel repair", "Auto-Fix Broken Apps & Deps"),
        ("sentinel heal", "Self-Healing & Rescue Engine"),
        ("sentinel ai", "Agentic AI Menu & Status"),
        ("sentinel ai setup", "AI Provider & Live Sync"),
        ("sentinel ai inspect", "Hardware & Offline Models"),
        ("sentinel ai toggle", "Toggle AI Mode (ON/OFF)"),
        ("sentinel ai advise", "AI Autonomous System Plan"),
        ("sentinel chat", "Interactive AI Chat Studio"),
        ("sentinel prereqs", "Check Python, Rclone & Ollama"),
        ("sentinel help", "CLI Command Manual"),
    ]

    for cmd, desc in cmds:
        c_trunc = cmd[:20]
        d_trunc = desc[:21]
        print(
            f"  {NEON_YELLOW}{c_trunc:<20}{C_RESET} {BRIGHT_WHITE}{d_trunc:<21}{C_RESET}"
        )


# ==============================================================================
# CLI ENTRYPOINT ROUTER
# ==============================================================================
def cli_entrypoint():
    if len(sys.argv) == 1:
        main()
        return

    cmd = sys.argv[1].lower()

    if cmd in ("ui", "tui", "gui"):
        main()
    elif cmd in ("status", "-s", "--status", "info"):
        print_large_header()
        render_hud_box("STATUS")
    elif cmd in ("audit", "-a", "--audit"):
        cli_audit()
    elif cmd in ("clean", "purge"):
        safe_only = True
        dry_run = False
        auto_yes = False
        for arg in sys.argv[2:]:
            if arg in ("--all", "-a"):
                safe_only = False
            elif arg in ("--dry-run", "-d"):
                dry_run = True
            elif arg in ("-y", "--yes"):
                auto_yes = True
        cli_clean(safe_only=safe_only, dry_run=dry_run, auto_yes=auto_yes)
    elif cmd in ("vault", "shield"):
        action = sys.argv[2].lower() if len(sys.argv) > 2 else "list"
        target = sys.argv[3] if len(sys.argv) > 3 else None
        name = sys.argv[4] if len(sys.argv) > 4 else None
        cli_vault(action=action, target=target, name=name)
    elif cmd in ("apps", "app"):
        action = sys.argv[2].lower() if len(sys.argv) > 2 else "list"
        target = sys.argv[3] if len(sys.argv) > 3 else None
        cli_apps(action=action, target=target)
    elif cmd in ("bots", "bot", "daemons"):
        action = sys.argv[2].lower() if len(sys.argv) > 2 else "scan"
        pid = sys.argv[3] if len(sys.argv) > 3 else None
        cli_bots(action=action, pid=pid)
    elif cmd in ("cloud", "sync", "rclone"):
        start = any(a in ("--start", "-s") for a in sys.argv[2:])
        live = any(a in ("--live", "-l") for a in sys.argv[2:])
        cli_cloud(live=live, start=start)
    elif cmd in ("hunt", "bloat"):
        threshold_mb = 100
        scan_path = HOME_DIR
        for arg in sys.argv[2:]:
            if arg.isdigit():
                threshold_mb = int(arg)
            elif os.path.exists(arg):
                scan_path = arg
        cli_hunt(threshold_mb=threshold_mb, scan_path=scan_path)
    elif cmd in ("offload", "archive-cloud"):
        if len(sys.argv) < 3:
            print(f"{NEON_RED}Usage: sentinel offload <path> [remote_folder]{C_RESET}")
        else:
            target_path = sys.argv[2]
            remote_folder = sys.argv[3] if len(sys.argv) > 3 else "Offloaded"
            cli_offload(target_path=target_path, remote_folder=remote_folder)
    elif cmd in ("auto-clean", "autoclean", "cron"):
        cli_autoclean()
    elif cmd in ("repair", "fix"):
        auto_fix = not any(a in ("--check", "--dry-run", "-d") for a in sys.argv[2:])
        cli_repair(auto_fix=auto_fix)
    elif cmd in ("doctor", "diagnose", "diag"):
        auto_fix = any(a in ("--fix", "-f", "-y") for a in sys.argv[2:])
        cli_repair(auto_fix=auto_fix)
    elif cmd in ("heal", "self-heal", "selfheal", "rescue"):
        self_heal_sentinel(silent=False)
    elif cmd in ("chat", "talk", "repl", "interactive", "studio"):
        interactive_ai_chat()
    elif cmd in ("ai", "agent", "llm"):
        sub = sys.argv[2].lower() if len(sys.argv) > 2 else "menu"
        extra = sys.argv[3:] if len(sys.argv) > 3 else []
        cli_ai(sub, *extra)
    elif cmd in ("prereqs", "prereq", "deps", "dependencies", "check"):
        interactive = not any(
            a in ("--non-interactive", "--quiet", "-q") for a in sys.argv[2:]
        )
        cli_prerequisites(interactive=interactive)
    elif cmd in ("update", "upgrade"):
        cli_update()
    elif cmd in ("help", "-h", "--help"):
        cli_help()
    else:
        print(f"\n{NEON_RED}Unknown command: '{cmd}'{C_RESET}")
        print(
            f"Run {NEON_CYAN}'sentinel help'{C_RESET} to view all available commands.\n"
        )


install_self_healing_hooks()

if __name__ == "__main__":
    cli_entrypoint()
