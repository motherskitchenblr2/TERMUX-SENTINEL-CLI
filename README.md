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
- 🛡️ **Immutable Preservation Vault (`vault.json`):** Dedicated shield registry that permanently excludes critical folders (e.g., Important Documents, developer workspaces, cloud backups) from scans and purges.
- 🕵️ **Smart Bot Detective & Daemon Sentry:** Scans Python, JavaScript, and Shell scripts; identifies automated bot scripts (`telegram`, `discord`, `bot.py`, `ai_worker`); surfaces silent background processes with instant PID termination.
- 📦 **Installed Apps & Debris Purge:** Scans and safely removes installed AI CLI tools (Codex, Qwen, Droid, Claude, Ollama, etc.), ensuring orphaned binaries, scoped packages, and command hashes are completely wiped.
- ☁️ **Cloud Synchronization & Migration:** Native Rclone background daemon with live telemetry streaming directly to Google Drive.
- ⚡ **Dual Operation Mode:** Seamlessly switch between the **Interactive Cyber Neon TUI** and headless **CLI Subcommands** for automated scripting.

---

## 🚀 Quick Start & Installation

### Cross-Platform Installation

#### 🤖 Android Termux:
```bash
git clone https://github.com/motherskitchenblr2/TERMUX-SENTINEL.git
cd TERMUX-SENTINEL
bash install.sh
```

#### 🐧 Ubuntu / Debian / Linux Desktop & Server:
```bash
git clone https://github.com/motherskitchenblr2/TERMUX-SENTINEL.git
cd TERMUX-SENTINEL
bash install.sh
```

#### 🪟 Windows (Command Prompt & PowerShell 5.1/7+):
Open PowerShell (as Administrator or standard user) and run:
```powershell
git clone https://github.com/motherskitchenblr2/TERMUX-SENTINEL.git
cd TERMUX-SENTINEL
powershell -ExecutionPolicy Bypass -File .\install.ps1
```
Or install via Python standard packaging:
```cmd
pip install -e .
```
This automatically registers `sentinel` and `termux-sentinel` globally in your terminal!

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
sentinel offload <dir> # Move heavy directory to Google Drive & reclaim local space
sentinel update        # Upgrade pkg, apt, pip, and global npm packages

# 🔍 Bloat Hunter & Automated Maintenance
sentinel hunt          # Deep scan directories eating >100 MB (npm, venv, cache)
sentinel hunt 500      # Custom threshold bloat hunt (e.g. >500 MB)
sentinel auto-clean    # Headless cron/widget auto-pruner with audit logging

# 🩺 Health Check & System Repair
sentinel doctor        # Diagnostic scan for broken packages, stale locks & dangling links
sentinel repair        # Auto-heal broken dependencies, unconfigured dpkg, and clear corrupt caches
sentinel heal          # Audit and self-heal Sentinel configs, permissions, and vault integrity

# 🤖 Agentic AI & Hardware Capacity Inspector
sentinel ai            # View Agentic AI Status & Active Model
sentinel ai inspect    # Hardware Capacity Audit & Offline Ollama Advisor
sentinel ai setup      # Connect AI Providers (OpenCode/TokenHarbor/Gemini/Groq/Ollama)
sentinel ai toggle     # Toggle between Autonomous Agentic AI & Manual Mode
sentinel ai advise     # Autonomous AI system analysis & 3-step action plan
sentinel ai "<prompt>" # One-shot AI query with live Termux system telemetry
sentinel prereqs       # Auto-check Python (required), Rclone & Ollama (optional)
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
| **`[d]`** | **Doctor & Heal** | Diagnose and repair broken packages, corrupt caches & stale locks |
| **`[g]`** | **Toggle AI Agent** | Switch between Autonomous Agentic AI and Manual Mode |
| **`[x]`** | **AI Advisor** | Run AI system telemetry analysis & optimization plan |
| **`[o]`** | **Ollama Inspector** | Hardware capacity audit & offline small model puller |
| **`[k]`** | **AI Providers** | Connect & live-sync AI providers (Token Harbor, Groq, Gemini) |
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
- **Important Documents & Media:** `Important_Documents`
- **Personal Documents & Data:** `documents`
- **Active Code Workspaces:** `Protected_Workspace`
- **Primary Cloud Backup Target:** `Cloud_Backup`
- **Secondary Cloud Backup Target:** `Remote_Backup`

Users can add custom directory paths or wildcard patterns at any time via `sentinel vault add <pattern>` or by pressing `[p]` in the TUI.

---

## ☁️ Google Drive Cloud Migration (Rclone)

Termux-Sentinel includes optimized parallel migration scripts to offload tens of gigabytes to Google Drive while keeping the phone awake with `termux-wake-lock`.

### Configuration
1. Install rclone: `pkg install rclone`
2. Configure Google Drive remote: `rclone config` (name it `remote_gdrive` or customize in scripts).
3. Secure credentials: `chmod 600 ~/.config/rclone/rclone.conf`.
4. Trigger migration: `sentinel cloud -s` or `bash ~/migrate_to_realme_bkp.sh`.

---

## 📱 Multi-Platform & Wide-Screen Support

Termux-Sentinel is designed to run seamlessly across Android mobile workstations, Linux servers, and Windows desktop terminals:
- **Android Termux:** ARM64 portrait mode with mobile-clamped 44-col HUD.
- **Ubuntu / Debian Linux:** Server & desktop terminals with full multi-column layout.
- **Windows 10 / 11:** Native Command Prompt and PowerShell support with Windows Terminal ANSI colors.
- **Responsive Wide-Screen TUI:** Automatically expands into a dual-pane Cyber Grid on displays $\ge 80$ columns, showing system storage on the left and vault status on the right.

---

## 📁 Repository Structure

```text
TERMUX-SENTINEL/
├── Termux_Sentinel.py                  # Core Sentinel Engine (Zero-dependency TUI + CLI)
├── install.sh                          # Universal installer for Termux, Ubuntu & Linux
├── install.ps1                         # One-click PowerShell installer for Windows
├── install_or_restore.sh               # Legacy Termux restore script
├── vault.json                          # Default Preservation Vault configuration
├── Termux-Sentinel                     # Termux Widget one-tap launcher with wake-lock
├── migrate_to_cmf_bkp.sh               # Device cloud migration script (Rclone)
├── setup_gdrive_credentials.py         # Google OAuth & token refresher helper
├── rclone.conf.template                # Sanitized Google Drive rclone template
├── pyproject.toml                      # Zero-dependency packaging specification
├── requirements.txt                    # Pure standard library specification
├── LICENSE                             # Apache 2.0 License
└── README.md                           # Master Documentation & Manual
```

---

## 📄 License

Licensed under the **Apache License, Version 2.0**. See the [LICENSE](LICENSE) file for full terms and conditions.

---

<p align="center">
  <b>Built with ⚡ for Termux power users. Keep your mobile Linux spotless, shielded, and synchronized.</b>
</p>
