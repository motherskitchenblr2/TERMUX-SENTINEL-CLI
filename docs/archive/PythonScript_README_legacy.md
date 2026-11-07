# 🛡️ TERMUX-SENTINEL
> **Doctor for Terminal Memory and Directories Issue**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Platform](https://img.shields.io/badge/Platform-Android%20Termux-2ea44f.svg)](https://termux.dev)
[![Python](https://img.shields.io/badge/Python-3.10%2B-yellow.svg)](https://python.org)
[![Architecture](https://img.shields.io/badge/Architecture-ARM64%20%2F%20AArch64-orange.svg)]()
[![UI](https://img.shields.io/badge/Interface-CLI%20%26%20Cyber%20TUI-ff69b4.svg)]()

```text
╔══════════════════════════════════════════╗
║   _____  ___  ___  __  __  _   _ __  __  ║
║  |_   _|| __|| _ \|  \/  || | | |\ \/ /  ║
║    | |  | _| |   /| |\/| || |_| | >  <   ║
║    |_|  |___||_|_\|_|  |_| \___/ /_/\_\  ║
║ ──────────────────────────────────────── ║
║   ░▒▓██████ S E N T I N E L ██████▓▒░    ║
╚══════════════════════════════════════════╝
```

---

## 🌟 Overview

**Termux-Sentinel** is an autonomous, production-grade storage telemetry, cache purging, bot detective, and application lifecycle engine built natively for Android Termux and PRoot Linux environments (e.g. Ubuntu).

Specifically calibrated for mobile portrait displays ($\le 44$ columns with **Shape-Lock Guarantee**), Termux-Sentinel eliminates runaway cache accumulation, discovers hidden/dormant background scripts, shields sensitive communication data, and synchronizes backups to Google Drive.

---

## ✨ Key Features

- 📱 **Mobile Portrait HUD & Shape-Lock:** Strictly formatted for $40 \le \text{cols} \le 44$. Zero line wrapping or ASCII fracturing on mobile vertical screens.
- 🎨 **Multi-Color Neon Spectrum:** Vibrant 6-color cyber aesthetic (Cyan, Pink, Yellow, Orange, Green, Purple) over Dark Charcoal background.
- 🧹 **Deep Cache Doctor:** Reclaims gigabytes from build caches, temporary directories, package managers, and runtimes:
  - `tmp` / `cache` / `pip` / `uv` / `npm` / `pnpm` / `bun` / `playwright` / container build artifacts.
- 🛡️ **Immutable Preservation Vault (`vault.json`):** Dedicated shield registry that permanently excludes critical folders (e.g., WhatsApp databases, Code Garage, cloud backups) from scans and purges.
- 🕵️ **Smart Bot Detective & Daemon Sentry:** Scans Python, JavaScript, and Shell scripts; identifies automated bot scripts (`telegram`, `discord`, `bot.py`, `ai_worker`); surfaces silent background processes with instant PID termination.
- 📦 **Installed Apps & Debris Purge:** Scans and safely removes installed AI CLI tools (Codex, Qwen, Droid, Claude, Ollama, etc.), ensuring orphaned binaries, scoped packages, and command hashes are completely wiped.
- ☁️ **Cloud Synchronization & Migration:** Native Rclone background daemon with live telemetry streaming directly to Google Drive.
- ⚡ **Dual Operation Mode:** Seamlessly switch between the **Interactive Cyber Neon TUI** and headless **CLI Subcommands** for automated scripting.

---

## 🚀 Quick Start & Installation

### One-Tap Installation
Open Termux and execute:
```bash
git clone https://github.com/motherskitchenblr2/TERMUX-SENTINEL.git
cd TERMUX-SENTINEL
bash install_or_restore.sh
```

This will automatically:
1. Install `Termux_Sentinel.py` to `$HOME/Termux_Sentinel.py`.
2. Register global CLI binaries `sentinel` and `termux-sentinel` into `$PREFIX/bin`.
3. Set up the Preservation Vault in `~/.config/termux_sentinel/vault.json`.
4. Install one-tap home screen shortcuts for **Termux:Widget** in `~/.shortcuts/`.
5. Configure cloud migration scripts with wake-lock support.

---

## 💻 CLI Subcommand Reference

Run `sentinel` from any directory or pipe it into automated cron tasks:

```bash
# 🖥️ Interactive Mode
sentinel               # Launches full interactive Cyber Neon TUI

# 📊 Telemetry & Audits
sentinel status        # Displays live storage HUD, RAM metrics & active shields
sentinel audit         # Comprehensive system audit (caches, apps, rogue bots)

# 🧹 Cache & Storage Cleaning
sentinel clean         # Purge safe recommended caches (tmp, pip, pnpm, bun)
sentinel clean --all   # Deep purge across all runtime caches & blobs
sentinel clean -d      # Dry-run preview without deleting files
sentinel clean -y      # Auto-confirm clean without manual prompt

# 🛡️ Preservation Vault
sentinel vault         # List all protected paths and regex patterns
sentinel vault add <p> # Shield a directory or pattern from all purges
sentinel vault rm <id> # Remove a user shield by ID

# 📦 App Lifecycle Manager
sentinel apps          # List installed CLI apps, tools & storage footprint
sentinel apps rm <app> # Multi-layer uninstall (wipes binaries & scoped debris)

# 🕵️ Bot Detective & Daemon Control
sentinel bots          # Scan for automated bot scripts and running daemons
sentinel bots kill <p> # Terminate process by PID with animated confirmation

# ☁️ Cloud Sync & System Updates
sentinel cloud         # View live Rclone Google Drive backup stream
sentinel cloud -s      # Start background cloud migration daemon
sentinel update        # Upgrade pkg, apt, pip, and global npm packages
sentinel help          # Display full CLI manual
```

---

## 🎮 Interactive TUI Keybindings

When running `sentinel` without arguments, navigate using single keystrokes:

| Key | Action | Function |
| :---: | :--- | :--- |
| **`[1-9]`** | **Toggle Selection** | Select / unselect items to clean, uninstall, or terminate |
| **`[c]`** | **Confirm & Execute** | Run deletions or uninstalls (*Intense Red animated sequence*) |
| **`[p]`** | **Preserve to Vault** | Shield selected items permanently (*Luminous Green animation*) |
| **`[v]`** | **Preservation Vault** | View and manage shielded directories and patterns |
| **`[m]`** | **Apps Manager** | Inspect and uninstall developer tools and agentic CLIs |
| **`[s]`** | **Bot Detective** | Audit rogue scripts and terminate silent daemons |
| **`[a]`** | **Select All Safe** | Quickly check all recommended safe-to-delete caches |
| **`[n]`** | **Deselect All** | Clear all active checkboxes |
| **`[u]`** | **System Updates** | Toggle automated package upgrades (`pkg`, `apt`, `npm`, `pip`) |
| **`[r]`** | **Cloud Telemetry** | Stream real-time Rclone cloud sync logs |
| **`[f]`** | **Refresh State** | Reload live filesystem state and storage telemetry |
| **`[b]`** | **Back / Dashboard** | Return to Master Sentinel Dashboard |
| **`[q]`** | **Quit** | Exit Termux-Sentinel cleanly |

---

## 🛡️ Preservation Vault System

The Preservation Vault (`vault.json`) guarantees that critical personal data, active code repositories, and cloud backups are **completely invisible** to scanners and **immune** to deletion.

### Default Core Shields
- **WhatsApp Media & Backups:** `com.whatsapp`
- **WhatsApp Storage & DB:** `whatsapp`
- **Active Code Workspaces:** `Advanced-Code-Garage`
- **Cloud Migration Target (Realme):** `Realme_BKP`
- **Cloud Migration Target (CMF):** `CMF_BKP`

Users can add custom directory paths or wildcard patterns at any time via `sentinel vault add <pattern>` or by pressing `[p]` in the TUI.

---

## ☁️ Google Drive Cloud Migration (Rclone)

Termux-Sentinel includes optimized parallel migration scripts to offload tens of gigabytes to Google Drive while keeping the phone awake with `termux-wake-lock`.

### Configuration
1. Install rclone: `pkg install rclone`
2. Configure Google Drive remote: `rclone config` (name it `pasha_gdrive` or customize in scripts).
3. Secure credentials: `chmod 600 ~/.config/rclone/rclone.conf`.
4. Trigger migration: `sentinel cloud -s` or `bash ~/migrate_to_realme_bkp.sh`.

---

## 📱 Multi-Device Support

Termux-Sentinel is designed to run seamlessly across multiple devices:
- **Primary Workstation:** Realme 12 Pro+ (256 GB ROM / 12 GB RAM)
- **Secondary Node:** CMF Phone 1 by Nothing (128 GB ROM / 8 GB RAM)
- Refer to [`CMF_PHONE_1_ANTIGRAVITY_INSTRUCTIONS.md`](CMF_PHONE_1_ANTIGRAVITY_INSTRUCTIONS.md) for step-by-step setup with Antigravity CLI and Gemini models.

---

## 📁 Repository Structure

```text
TERMUX-SENTINEL/
├── Termux_Sentinel.py                  # Core Sentinel Engine (TUI + CLI)
├── install_or_restore.sh               # One-tap installer and environment restorer
├── vault.json                          # Default Preservation Vault configuration
├── Termux_Sentinel.sh                  # Termux Widget one-tap launcher
├── 3_Termux_Sentinel.sh                # Numbered widget shortcut with wake-lock
├── Backup_to_Drive.sh                  # Dedicated WhatsApp & storage backup script
├── migrate_to_realme_bkp.sh            # High-efficiency Realme cloud migration script
├── migrate_to_cmf_bkp.sh               # CMF Phone 1 cloud migration script
├── rclone.conf.template                # Sanitized Google Drive rclone template
├── CMF_PHONE_1_ANTIGRAVITY_INSTRUCTIONS.md  # Multi-device Antigravity CLI guide
├── LICENSE                             # Apache 2.0 License
├── README.md                           # Master Documentation & Manual
└── Python Script/                      # Mirrored workspace package
```

---

## 📄 License

Licensed under the **Apache License, Version 2.0**. See the [LICENSE](LICENSE) file for full terms and conditions.

---

<p align="center">
  <b>Built with ⚡ for Termux power users. Keep your mobile Linux spotless, shielded, and synchronized.</b>
</p>
