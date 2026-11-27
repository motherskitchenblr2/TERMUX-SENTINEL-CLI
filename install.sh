#!/usr/bin/env bash
# =============================================================================
# Universal Cross-Platform Installer for Termux Sentinel
# Compatible with: Android Termux, Ubuntu, Debian, Fedora, Arch Linux & macOS
# =============================================================================

set -e

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="$(command -v python3 || command -v python || true)"

if [ -z "$PYTHON_BIN" ]; then
	echo "Error: Python 3.9+ is required but not installed." >&2
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

echo ""
echo "=========================================================="
echo " ✓ Installation Successful!"
echo "   - Interactive TUI:  sentinel"
echo "   - System Status:    sentinel status"
echo "   - Deep Bloat Scan:  sentinel hunt"
echo "   - CLI Manual:       sentinel help"
echo "=========================================================="
