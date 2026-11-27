#!/usr/bin/env bash
# =============================================================================
# Universal Cross-Platform Installer for Termux Sentinel
# Compatible with: Android Termux, Ubuntu, Debian, Fedora, Arch Linux & macOS
# =============================================================================

set -e

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 1. Prerequisite Check: Python 3 (MANDATORY to run .py scripts)
PYTHON_BIN="$(command -v python3 || command -v python || true)"

if [ -z "$PYTHON_BIN" ]; then
	echo "⚠️  Python 3 is required to run Termux Sentinel scripts (.py), but was not found."
	echo ""
	if [ -t 0 ]; then
		read -r -p "👉 Would you like to install Python now? [y/N]: " install_py_choice || install_py_choice="n"
	else
		install_py_choice="n"
	fi
	if [[ "$install_py_choice" =~ ^[Yy]$ ]]; then
		echo "📦 Installing Python..."
		if [ -n "$TERMUX_VERSION" ] || [ -d "/data/data/com.termux/files/usr/bin" ]; then
			pkg update -y && pkg install -y python
		elif command -v apt-get >/dev/null 2>&1; then
			if [ "$(id -u)" -eq 0 ]; then
				apt-get update && apt-get install -y python3 python3-pip
			else
				sudo apt-get update && sudo apt-get install -y python3 python3-pip
			fi
		elif command -v dnf >/dev/null 2>&1; then
			sudo dnf install -y python3 python3-pip
		elif command -v pacman >/dev/null 2>&1; then
			sudo pacman -Sy --noconfirm python
		elif command -v brew >/dev/null 2>&1; then
			brew install python3
		fi
		PYTHON_BIN="$(command -v python3 || command -v python || true)"
	fi
fi

if [ -z "$PYTHON_BIN" ]; then
	echo ""
	echo "❌ Error: Python 3 is required to run Termux Sentinel (.py scripts)." >&2
	echo "   Please install Python first, for example:" >&2
	echo "     - Termux:  pkg install python" >&2
	echo "     - Ubuntu:  sudo apt install python3" >&2
	echo "     - Arch:    sudo pacman -S python" >&2
	echo "     - macOS:   brew install python3" >&2
	exit 1
fi

echo "=========================================================="
echo " 🛡️  SENTINEL CLI/TUI - UNIVERSAL CROSS-PLATFORM INSTALLER"
echo "=========================================================="
echo "Source: $SOURCE_DIR"
echo "Python: $PYTHON_BIN"
echo ""

# 1. Determine platform and target bin directory
if [ -n "$TERMUX_VERSION" ] || [ -d "/data/data/com.termux/files/usr/bin" ]; then
	IS_TERMUX=true
	TARGET_BIN="${PREFIX:-/data/data/com.termux/files/usr}/bin"
	HOME_DIR="${HOME:-/data/data/com.termux/files/home}"
	VAULT_DIR="$HOME_DIR/.config/termux_sentinel"
else
	IS_TERMUX=false
	HOME_DIR="${HOME:-$HOME}"
	VAULT_DIR="$HOME_DIR/.config/termux_sentinel"
	if [ "$(id -u)" -eq 0 ]; then
		TARGET_BIN="/usr/local/bin"
	else
		TARGET_BIN="$HOME_DIR/.local/bin"
	fi
fi

mkdir -p "$TARGET_BIN"
mkdir -p "$VAULT_DIR"

# 2. Install Vault configuration if missing
if [ ! -f "$VAULT_DIR/vault.json" ] && [ -f "$SOURCE_DIR/vault.json" ]; then
	cp -vf "$SOURCE_DIR/vault.json" "$VAULT_DIR/vault.json"
	echo " ✓ Initialized Preservation Vault: $VAULT_DIR/vault.json"
fi

# 3. Create global symlinks
ln -sf "$SOURCE_DIR/Termux_Sentinel.py" "$TARGET_BIN/sentinel"
ln -sf "$SOURCE_DIR/Termux_Sentinel.py" "$TARGET_BIN/termux-sentinel"
chmod +x "$SOURCE_DIR/Termux_Sentinel.py" "$TARGET_BIN/sentinel" "$TARGET_BIN/termux-sentinel"
echo " ✓ Registered global CLI commands: $TARGET_BIN/sentinel & $TARGET_BIN/termux-sentinel"

# 4. Termux-specific widget shortcuts
if [ "$IS_TERMUX" = true ]; then
	mkdir -p "$HOME_DIR/.shortcuts/tasks"
	if [ -f "$SOURCE_DIR/Termux-Sentinel" ]; then
		cp -vf "$SOURCE_DIR/Termux-Sentinel" "$HOME_DIR/.shortcuts/Termux-Sentinel"
		chmod 755 "$HOME_DIR/.shortcuts/Termux-Sentinel"
		echo " ✓ Installed Termux:Widget Shortcut: ~/.shortcuts/Termux-Sentinel"
	fi
	if [ -f "$SOURCE_DIR/Terminal-Sentinal" ]; then
		cp -vf "$SOURCE_DIR/Terminal-Sentinal" "$HOME_DIR/.shortcuts/Terminal-Sentinal"
		chmod 755 "$HOME_DIR/.shortcuts/Terminal-Sentinal"
		if [ -d "$HOME_DIR/.shortcuts/icons" ] && [ -f "$HOME_DIR/.shortcuts/icons/Sentinel.png" ]; then
			cp -vf "$HOME_DIR/.shortcuts/icons/Sentinel.png" "$HOME_DIR/.shortcuts/icons/Terminal-Sentinal.png" 2>/dev/null || true
		fi
		echo " ✓ Installed Termux:Widget Shortcut: ~/.shortcuts/Terminal-Sentinal"
	fi
	ln -sf "$SOURCE_DIR/Termux_Sentinel.py" "$HOME_DIR/Termux_Sentinel.py" 2>/dev/null || true
else
	# Ensure ~/.local/bin is in PATH for Ubuntu/Debian non-root users
	if [[ ":$PATH:" != *":$TARGET_BIN:"* ]]; then
		for rc in "$HOME_DIR/.bashrc" "$HOME_DIR/.zshrc"; do
			if [ -f "$rc" ] && ! grep -q "$TARGET_BIN" "$rc"; then
				echo "export PATH=\"$TARGET_BIN:\$PATH\"" >>"$rc"
				echo " ✓ Appended $TARGET_BIN to $rc"
			fi
		done
	fi
fi

# 5. Check Optional Companion Tools: Rclone & Ollama
RCLONE_BIN="$(command -v rclone || true)"
if [ -z "$RCLONE_BIN" ]; then
	echo ""
	echo "☁️  [Optional] Rclone is not installed (needed only for Google Drive sync & offload)."
	if [ -t 0 ]; then
		read -r -p "👉 Would you like to install Rclone now? [y/N]: " install_rclone_choice || install_rclone_choice="n"
	else
		install_rclone_choice="n"
	fi
	if [[ "$install_rclone_choice" =~ ^[Yy]$ ]]; then
		echo "📦 Installing Rclone..."
		if [ "$IS_TERMUX" = true ]; then
			pkg install -y rclone || true
		elif command -v apt-get >/dev/null 2>&1; then
			if [ "$(id -u)" -eq 0 ]; then
				apt-get install -y rclone || true
			else
				sudo apt-get install -y rclone || true
			fi
		elif command -v dnf >/dev/null 2>&1; then
			sudo dnf install -y rclone || true
		elif command -v pacman >/dev/null 2>&1; then
			sudo pacman -S --noconfirm rclone || true
		elif command -v brew >/dev/null 2>&1; then
			brew install rclone || true
		fi
	else
		echo "   ℹ️  Skipped Rclone. Local storage and vault features remain 100% active."
	fi
else
	echo " ✓ Detected Rclone: $RCLONE_BIN"
fi

OLLAMA_BIN="$(command -v ollama || true)"
if [ -z "$OLLAMA_BIN" ]; then
	echo ""
	echo "🧠 [Optional] Ollama is not installed (needed only for offline local AI models)."
	echo "   (Note: Cloud AI APIs like Gemini, Groq, OpenRouter work with zero local tools!)"
	if [ -t 0 ]; then
		read -r -p "👉 Would you like to install Ollama now? [y/N]: " install_ollama_choice || install_ollama_choice="n"
	else
		install_ollama_choice="n"
	fi
	if [[ "$install_ollama_choice" =~ ^[Yy]$ ]]; then
		echo "📦 Installing Ollama..."
		if [ "$IS_TERMUX" = true ]; then
			pkg install -y ollama || echo "Notice: If ollama is unavailable in standard Termux pkg, use cloud AI providers."
		elif command -v curl >/dev/null 2>&1; then
			curl -fsSL https://ollama.com/install.sh | sh || true
		fi
	else
		echo "   ℹ️  Skipped Ollama. Cloud AI models remain 100% available via 'sentinel ai setup'."
	fi
else
	echo " ✓ Detected Ollama: $OLLAMA_BIN"
fi

echo ""
echo "=========================================================="
echo " ✓ Installation Successful!"
echo "   - Interactive TUI:  sentinel"
echo "   - System Status:    sentinel status"
echo "   - Deep Bloat Scan:  sentinel hunt"
echo "   - CLI Manual:       sentinel help"
echo "=========================================================="
