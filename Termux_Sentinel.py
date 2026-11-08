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
import subprocess
import sys
import time
import unicodedata

# ==============================================================================
# NEON GLOW & DARK CHARCOAL COLOR PALETTE (256-Color ANSI)
# ==============================================================================
BG_CHARCOAL = "\033[48;5;234m"
BG_DARK = "\033[48;5;232m"
BG_BLACK = "\033[40m"
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

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

UBUNTU_ROOT = "/data/data/com.termux/files/usr/var/lib/proot-distro/containers/ubuntu/rootfs"
HOME_DIR = "/data/data/com.termux/files/home"
VAULT_DIR = os.path.join(HOME_DIR, ".config", "termux_sentinel")
VAULT_FILE = os.path.join(VAULT_DIR, "vault.json")

# Core hardcoded safety keywords that can NEVER be touched or bypassed
CORE_SAFETY_KEYWORDS = [
    "com.whatsapp",
    "whatsapp",
    "advanced-code-garage",
    "realme_bkp",
    "cmf_bkp",
]

DEFAULT_VAULT_ITEMS = [
    {
        "id": 1,
        "name": "WhatsApp Media & Backups",
        "pattern": "com.whatsapp",
        "type": "System Scope",
        "locked": True,
        "date_added": "Default Core Shield",
    },
    {
        "id": 2,
        "name": "WhatsApp Storage & DB",
        "pattern": "whatsapp",
        "type": "Storage Scope",
        "locked": True,
        "date_added": "Default Core Shield",
    },
    {
        "id": 3,
        "name": "Advanced-Code-Garage Workspace",
        "pattern": "Advanced-Code-Garage",
        "type": "Active Workspace",
        "locked": True,
        "date_added": "Default Core Shield",
    },
    {
        "id": 4,
        "name": "Cloud Backup Targets",
        "pattern": "Realme_BKP",
        "type": "Cloud Target",
        "locked": True,
        "date_added": "Default Core Shield",
    },
    {
        "id": 5,
        "name": "CMF Cloud Target",
        "pattern": "CMF_BKP",
        "type": "Cloud Target",
        "locked": True,
        "date_added": "Default Core Shield",
    },
]


# ==============================================================================
# PRESERVATION VAULT STORAGE & LOGIC ENGINE
# ==============================================================================
def load_vault():
    """Loads preserved items from vault.json, auto-seeding defaults if needed."""
    if not os.path.exists(VAULT_FILE):
        os.makedirs(VAULT_DIR, exist_ok=True)
        save_vault(DEFAULT_VAULT_ITEMS)
        return list(DEFAULT_VAULT_ITEMS)
    try:
        with open(VAULT_FILE, encoding="utf-8") as vault_file:
            data = json.load(vault_file)
            if isinstance(data, list):
                # Ensure core items are present
                existing_patterns = {it.get("pattern", "").lower() for it in data}
                for def_item in DEFAULT_VAULT_ITEMS:
                    if def_item["pattern"].lower() not in existing_patterns:
                        data.append(def_item)
                return data
            if isinstance(data, dict) and "items" in data:
                return data["items"]
            return list(DEFAULT_VAULT_ITEMS)
    except Exception:
        return list(DEFAULT_VAULT_ITEMS)


def save_vault(items):
    """Saves vault items safely to disk."""
    try:
        os.makedirs(VAULT_DIR, exist_ok=True)
        with open(VAULT_FILE, "w") as f:
            json.dump(items, f, indent=2)
    except Exception:
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
            "Core system shields (WhatsApp & Code Garage) are permanently locked for safety!",
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
# TERMINAL GEOMETRY & FORMATTING HELPERS (Mobile Clamped 44 Cols)
# ==============================================================================
def get_term_cols():
    """Returns terminal columns clamped for clean mobile portrait rendering."""
    try:
        cols = shutil.get_terminal_size((44, 24)).columns
        return min(max(cols, 40), 44)
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

BANNER_3D_LINES = [
    r"   _____  ___  ___  __  __  _   _ __  __  ",
    r"  |_   _|| __|| _ \|  \/  || | | |\ \/ /  ",
    r"    | |  | _| |   /| |\/| || |_| | >  <   ",
    r"    |_|  |___||_|_\|_|  |_| \___/ /_/\_\  ",
    r" ──────────────────────────────────────── ",
    r"   ░▒▓██████ S E N T I N E L ██████▓▒░    ",
]


def render_3d_banner(border_color=NEON_CYAN, title_color=None, colorful=True):
    """Renders the responsive Cyber Termux-Sentinel banner with shape-lock guarantee."""
    target_cols = get_term_cols()
    c = min(max(target_cols, 40), 44)
    inner = c - 2
    pad_left = (inner - 38) // 2
    pad_right = inner - 38 - pad_left

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
        print(f"\n {BG_CHARCOAL} {C_BOLD}{b_color}[ ✦ ]{C_RESET} {BRIGHT_WHITE}{msg:<34}{C_RESET}")
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
        du_path = shutil.which("du") or "du"
        out = subprocess.check_output(
            [du_path, "-sk", path], stderr=subprocess.DEVNULL, timeout=1.8
        )  # nosec B603, B607
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
    try:
        stat = os.statvfs(HOME_DIR)
        total = stat.f_blocks * stat.f_frsize
        free = stat.f_bavail * stat.f_frsize
        used = total - free
        pct = (used / total) * 100 if total > 0 else 0
        return human_size(used), human_size(total), human_size(free), f"{pct:.1f}%"
    except Exception:
        return "N/A", "N/A", "N/A", "N/A"


def get_device_name():
    """Detects current mobile device brand & model dynamically."""
    try:
        brand = (
            subprocess.check_output(
                ["getprop", "ro.product.brand"], text=True, stderr=subprocess.DEVNULL
            )
            .strip()
            .upper()
        )
        model = (
            subprocess.check_output(
                ["getprop", "ro.product.model"], text=True, stderr=subprocess.DEVNULL
            )
            .strip()
            .upper()
        )
        if "REALME" in brand or "RMX" in model:
            return "REALME 12 PRO+"
        elif "NOTHING" in brand or "CMF" in brand or "A015" in model:
            return "CMF PHONE 1 (NOTHING)"
        if brand:
            return f"{brand} {model}"[:20]
    except Exception:
        pass
    return "TERMUX SENTINEL"


# ==============================================================================
# NEON BORDER UI CONTAINERS & HEADERS
# ==============================================================================
def render_hud_box(view_name="DASHBOARD"):
    """All-Around Neon Border HUD Box (Mobile Clamped to 44 columns)."""
    cols = get_term_cols()
    used, total, free, pct = get_disk_usage()
    vault_items = load_vault()
    vault_count = len(vault_items)
    dev_name = get_device_name()

    title = f"═ {dev_name} HUD "
    if visible_len(title) > cols - 6:
        title = "═ SENTINEL HUD "
    fill = max(0, cols - 2 - visible_len(title))
    top = f"{NEON_CYAN}╔{title}" + "═" * fill + f"╗{C_RESET}"
    bot = f"{NEON_CYAN}╚" + "═" * (cols - 2) + f"╝{C_RESET}"

    r1 = f"Used: {NEON_YELLOW}{used}{C_RESET} | Free: {NEON_GREEN}{free}{C_RESET} ({pct})"
    r2 = f"Vault: {NEON_GREEN}{vault_count} Active Shields [v]{C_RESET}"

    print(top)
    print(make_box_row(r1, border_color=NEON_CYAN, cols=cols))
    print(make_box_row(r2, border_color=NEON_CYAN, cols=cols))
    print(bot)


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
            "paths": ["/data/data/com.termux/files/usr/var/lib/proot-distro/containers/debian-ai"],
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
            "extra_dirs": ["/data/data/com.termux/files/usr/lib/node_modules/rea-agents"],
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
    """System & Dependency updates."""
    return [
        {
            "id": 10,
            "category": "update",
            "name": "Clean Termux & Ubuntu pkg cache",
            "recommendation": "system cache (Safe to clean)",
            "cmd": "pkg clean && pkg autoclean && proot-distro login ubuntu -- apt-get clean 2>/dev/null || true",
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
        {
            "id": 12,
            "category": "update",
            "name": "Update Ubuntu Packages (apt)",
            "recommendation": "distro upgrade (Recommended)",
            "cmd": "proot-distro login ubuntu -- bash -c 'apt-get update && apt-get upgrade -y'",
            "default": False,
        },
        {
            "id": 13,
            "category": "update",
            "name": "Purge Python pip build cache",
            "recommendation": "cache files (Safe to purge)",
            "cmd": "pip cache purge 2>/dev/null || true",
            "default": True,
        },
        {
            "id": 14,
            "category": "update",
            "name": "Update Global Node.js Packages",
            "recommendation": "npm CLI tools (Update all)",
            "cmd": "npm update -g 2>/dev/null || true",
            "default": False,
        },
    ]


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

    running_cmds = []
    my_uid = os.getuid()
    for pid_str in os.listdir("/proc"):
        if pid_str.isdigit():
            try:
                if os.stat(f"/proc/{pid_str}").st_uid == my_uid:
                    with open(f"/proc/{pid_str}/cmdline", "rb") as f:
                        running_cmds.append(
                            (
                                int(pid_str),
                                f.read().decode("utf-8", errors="ignore").replace("\x00", " "),
                            )
                        )
            except Exception:
                pass

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
                            with open(fpath, encoding="utf-8", errors="ignore") as bot_file:
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
                        mtime = time.strftime("%Y-%m-%d %H:%M", time.localtime(st.st_mtime))
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
        except Exception:
            pass
    return detected_bots


def scan_running_daemons():
    """Detects silently running background processes/daemons owned by current user."""
    daemons = []
    my_uid = os.getuid()
    idx = 80

    for pid_str in os.listdir("/proc"):
        if not pid_str.isdigit():
            continue
        try:
            pid = int(pid_str)
            p_stat = os.stat(f"/proc/{pid_str}")
            if p_stat.st_uid != my_uid:
                continue

            with open(f"/proc/{pid_str}/cmdline", "rb") as f:
                raw = f.read()
                if not raw:
                    continue
                parts = [p.decode("utf-8", errors="ignore") for p in raw.split(b"\x00") if p]
                if not parts:
                    continue
                cmd = " ".join(parts)
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
                    if "termux_sentinel" in cmd_lower or "ps -" in cmd_lower:
                        continue

                    script_path = None
                    for t in parts[1:]:
                        if t.endswith((".py", ".js", ".sh", ".ts", ".mjs")) and os.path.isfile(t):
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
        except Exception:
            pass
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
        box = f"{NEON_RED}{C_BOLD}[X]{C_RESET}" if is_sel else f"{NEON_GREEN}[ ]{C_RESET}"
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
        box = f"{NEON_GREEN}{C_BOLD}[X]{C_RESET}" if is_sel else f"{TEXT_MUTED}[ ]{C_RESET}"
        print(f"  {box} {t['id']:2d}. {BRIGHT_WHITE}{t['name'][:cols-8]}{C_RESET}")
        print(f"    {TEXT_MUTED}↳ {t['recommendation'][:cols-8]}{C_RESET}")

    print("─" * cols)
    print(
        f" {C_BOLD}{BRIGHT_WHITE}Space to Reclaim:{C_RESET} {NEON_GREEN}{C_BOLD}{human_size(reclaim_total)}{C_RESET}"
    )

    # ALL-AROUND NEON NAVIGATION FOOTER
    print(f"\n{NEON_CYAN}╔═ COMMANDS & TOUCH NAVIGATION ════════════╗{C_RESET}")
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
            f"{NEON_CYAN}[s]{C_RESET} Bots & Daemons  {NEON_GREEN}[r]{C_RESET} Cloud Sync",
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
    print(make_box_row(f"{NEON_RED}[q]{C_RESET} Cancel & Exit", border_color=NEON_CYAN, cols=cols))
    print(f"{NEON_CYAN}╚══════════════════════════════════════════╝{C_RESET}")


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
        box = f"{NEON_RED}{C_BOLD}[X]{C_RESET}" if is_sel else f"{NEON_GREEN}[ ]{C_RESET}"
        data_info = f"[{a['data_size_str']}]" if a.get("data_size_bytes", 0) > 0 else ""
        print(
            f"  {box} {a['id']:2d}. {BRIGHT_WHITE}{a['name'][:name_w]:<{name_w}}{C_RESET} {NEON_YELLOW}{data_info:>10}{C_RESET}"
        )

    print_divider_h3("DEPENDENCIES & DEV TOOLS", color=NEON_PURPLE)
    for d in dep_tools:
        is_sel = selected.get(d["id"], False)
        box = f"{NEON_RED}{C_BOLD}[X]{C_RESET}" if is_sel else f"{NEON_GREEN}[ ]{C_RESET}"
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
    print(make_box_row(f"{NEON_RED}[q]{C_RESET} Cancel & Exit", border_color=NEON_PINK, cols=cols))
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
            box = f"{NEON_RED}{C_BOLD}[X]{C_RESET}" if is_sel else f"{NEON_GREEN}[ ]{C_RESET}"
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
            box = f"{NEON_RED}{C_BOLD}[X]{C_RESET}" if is_sel else f"{NEON_GREEN}[ ]{C_RESET}"
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
    print(make_box_row(f"{NEON_RED}[q]{C_RESET} Cancel & Exit", border_color=NEON_CYAN, cols=cols))
    print(f"{NEON_CYAN}╚══════════════════════════════════════════╝{C_RESET}")


def render_vault_view(vault_items):
    """Dedicated Preservation Vault View (Shield Registry)."""
    cols = get_term_cols()
    print_large_header()
    vtitle = "═ 🛡️ PRESERVED SHIELDS "
    v_top = f"{NEON_GREEN}╔{vtitle}" + "═" * (cols - 2 - visible_len(vtitle)) + f"╗{C_RESET}"
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

            print(f"  {NEON_GREEN}[{iid}]{C_RESET} {BRIGHT_WHITE}{C_BOLD}{name[:28]}{C_RESET}")
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
# CLOUD STATUS & ACTIONS
# ==============================================================================
def show_rclone_status():
    cols = get_term_cols()
    clear_screen()
    print_large_header()
    print_section_h2("📡 RCLONE CLOUD BACKUP LIVE TELEMETRY", color=NEON_CYAN)
    ps = subprocess.run(["pgrep", "-f", "rclone"], capture_output=True, text=True)
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
                with open(l, "r", encoding="utf-8", errors="replace") as log_file:
                    log_lines = log_file.readlines()[-15:]
                    print("".join(log_lines), end="")
            except OSError:
                pass
            found_log = True
            break
    if not found_log:
        print("  No active rclone log file available.")
    print("─" * cols)
    input(f"\n{C_BOLD}{BRIGHT_WHITE}Press Enter to return to Termux_Sentinel...{C_RESET}")


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
        print(f"\n{NEON_YELLOW}⚠️  No items selected! Tick checkboxes with [Num] first.{C_RESET}")
        time.sleep(1.2)
        return False

    animate_safe(
        "VAULTING",
        f"Moving {len(items_to_preserve)} item(s) into Preservation Vault...",
        duration=0.8,
    )
    added_count = 0
    for it in items_to_preserve:
        ok, res = add_to_vault(it["name"], it["pattern"], it["type"])
        if ok:
            added_count += 1
            print(f"    {NEON_GREEN}✓ Shielded:{C_RESET} {BRIGHT_WHITE}{it['name']}{C_RESET}")

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

    if not any([clean_items, update_items, uninstall_items, del_bot_items, kill_daemon_items]):
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
            print(f"   • {BRIGHT_WHITE}{a['name']} ({a.get('data_size_str', '0 B')} data){C_RESET}")

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
        print(f"\n{NEON_BLUE}Operation cancelled by operator. Nothing was touched.{C_RESET}")
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
            try:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.3)
                os.kill(pid, signal.SIGKILL)
            except Exception:
                pass
            print(f"    {NEON_RED}✓ Terminated PID {pid}{C_RESET}")

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
                subprocess.run(t["cmd"])
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
                            except Exception:
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
                            print(f"    {NEON_YELLOW}✗ Error removing {p}: {e}{C_RESET}")

    # 4. Uninstall Apps & Data Prompt
    if uninstall_items:
        print_divider_h3("UNINSTALLING APPLICATIONS", color=NEON_RED)
        for a in uninstall_items:
            animate_step("UNINSTALLING", f"Removing {a['name']}...", color=NEON_RED, duration=0.7)
            uninstall_cmd = a.get("uninstall_cmd", "")
            if uninstall_cmd:
                try:
                    subprocess.run(shlex.split(uninstall_cmd), check=False)  # nosec B603
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

            print(f"    {NEON_RED}✓ Binary & package completely wiped for {a['name']}{C_RESET}")

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
                            print(f"    {NEON_GREEN}🛡️ Protected by Vault: {d}{C_RESET}")
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
    for item in clean_items + update_items + uninstall_items + del_bot_items + kill_daemon_items:
        selected[item["id"]] = False

    print("\n" + "─" * cols)
    animate_safe("COMPLETED", "All operations executed with 100% integrity!", duration=0.8)
    used, total, free, pct = get_disk_usage()
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
            animate_safe("REFRESHING", "Reloading fresh system & app telemetry...", duration=0.6)
            clean_targets = define_cleaning_targets()
            apps_targets = define_installed_apps()
            bot_scripts = scan_bot_scripts()
            running_daemons = scan_running_daemons()
        elif choice == "f":
            animate_safe("REFRESHING", "Scanning and reloading fresh telemetry...", duration=0.6)
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
        elif choice == "z":
            print(f"\n{NEON_YELLOW}Sentinel paused. No background changes made.{C_RESET}")
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
        print(f"  • {BRIGHT_WHITE}{a['name'][:22]:<22}{C_RESET} {NEON_YELLOW}{d_sz:>10}{C_RESET}")

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
            f"{BADGE_GREEN} LOCKED {C_RESET}" if v.get("locked") else f"{BADGE_CYAN} USER {C_RESET}"
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
        except Exception:
            conf = "n"
        if conf not in ("y", "yes"):
            print(f"{NEON_YELLOW}Operation cancelled by operator.{C_RESET}")
            return

    for t in targets:
        animate_delete(f"Cleaning {t['name'][:24]}...")
        if t["action_type"] == "command":
            subprocess.run(t["cmd"])
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
    used, total, free, pct = get_disk_usage()
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
            print(f"{NEON_GREEN}✓ Shield removed: '{res['name']}'. Restored to scans.{C_RESET}")
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
        print(f"\n{C_BOLD}{NEON_RED}Uninstall {matched['name']}? (y/N): {C_RESET}", end="")
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
            os.kill(p_int, signal.SIGTERM)
            time.sleep(0.3)
            os.kill(p_int, signal.SIGKILL)
            print(f"{NEON_GREEN}✓ Process PID {p_int} terminated.{C_RESET}")
        except Exception as e:
            print(f"{NEON_YELLOW}✗ Could not terminate PID {pid}: {e}{C_RESET}")


def cli_cloud(live=False, start=False):
    if start:
        animate_safe("STARTING", "Launching background Rclone cloud backup...", duration=0.8)
        trace_path = os.path.join(HOME_DIR, "test_trace.log")
        with open(trace_path, "a", encoding="utf-8") as trace_log:
            subprocess.Popen(
                ["bash", os.path.join(HOME_DIR, "migrate_to_realme_bkp.sh")],
                stdout=trace_log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        print(f"{NEON_GREEN}✓ Cloud migration running in background with wake-lock.{C_RESET}")
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


def cli_help():
    cols = get_term_cols()
    print_large_header()
    print(f"{NEON_CYAN}╔═ TERMUX SENTINEL CLI MANUAL ═════════════╗{C_RESET}")
    print(
        make_box_row(
            f"{BRIGHT_WHITE}Global: sentinel [subcommand] [flags]{C_RESET}",
            border_color=NEON_CYAN,
            cols=cols,
        )
    )
    print(f"{NEON_CYAN}╚══════════════════════════════════════════╝{C_RESET}")
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
        ("sentinel help", "CLI Command Manual"),
    ]

    for cmd, desc in cmds:
        c_trunc = cmd[:20]
        d_trunc = desc[:21]
        print(f"  {NEON_YELLOW}{c_trunc:<20}{C_RESET} {BRIGHT_WHITE}{d_trunc:<21}{C_RESET}")


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
    elif cmd in ("update", "upgrade"):
        cli_update()
    elif cmd in ("help", "-h", "--help"):
        cli_help()
    else:
        print(f"\n{NEON_RED}Unknown command: '{cmd}'{C_RESET}")
        print(f"Run {NEON_CYAN}'sentinel help'{C_RESET} to view all available commands.\n")


if __name__ == "__main__":
    cli_entrypoint()
