#!/data/data/com.termux/files/usr/bin/bash
# =============================================================================
# Automated One-Tap Installer & Restorer for Termux Sentinel & Rclone
# Compatible with Android Termux and PRoot Linux environments
# =============================================================================

set -e

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOME_DIR="${HOME:-/data/data/com.termux/files/home}"
PREFIX_BIN="${PREFIX:-/data/data/com.termux/files/usr}/bin"

echo "=========================================================="
echo " 🛡️  TERMUX SENTINEL & RCLONE ONE-TAP RESTORER"
echo "=========================================================="
echo "Source: $SOURCE_DIR"
echo "Target: $HOME_DIR"
echo ""

# Helper to find file either in SOURCE_DIR or SOURCE_DIR/Python Script
find_src() {
	local fname="$1"
	if [ -f "$SOURCE_DIR/$fname" ]; then
		echo "$SOURCE_DIR/$fname"
	elif [ -f "$SOURCE_DIR/Python Script/$fname" ]; then
		echo "$SOURCE_DIR/Python Script/$fname"
	else
		echo ""
	fi
}

# 1. Create required directories
mkdir -p "$HOME_DIR/.shortcuts"
mkdir -p "$HOME_DIR/.config/termux_sentinel"
mkdir -p "$HOME_DIR/.config/rclone"
mkdir -p "$PREFIX_BIN"

# 2. Restore Core Sentinel & Register Global CLI Commands
SRC_PY="$(find_src "Termux_Sentinel.py")"
if [ -n "$SRC_PY" ]; then
	cp -vf "$SRC_PY" "$HOME_DIR/Termux_Sentinel.py"
	chmod +x "$HOME_DIR/Termux_Sentinel.py"

	# Register global CLI commands in $PREFIX/bin
	ln -sf "$HOME_DIR/Termux_Sentinel.py" "$PREFIX_BIN/sentinel"
	ln -sf "$HOME_DIR/Termux_Sentinel.py" "$PREFIX_BIN/termux-sentinel"
	chmod +x "$PREFIX_BIN/sentinel" "$PREFIX_BIN/termux-sentinel" 2>/dev/null || true
	echo " ✓ Registered global CLI commands: 'sentinel' & 'termux-sentinel'"
fi

# 3. Restore Preservation Vault Config
SRC_VAULT="$(find_src "vault.json")"
if [ -n "$SRC_VAULT" ]; then
	if [ ! -f "$HOME_DIR/.config/termux_sentinel/vault.json" ]; then
		cp -vf "$SRC_VAULT" "$HOME_DIR/.config/termux_sentinel/vault.json"
		echo " ✓ Installed Preservation Vault: ~/.config/termux_sentinel/vault.json"
	else
		echo " ℹ Preservation Vault already exists, preserving existing shields."
	fi
fi

# 4. Restore Termux Widget Shortcuts
SRC_W0="$(find_src "Termux-Sentinel")"
if [ -n "$SRC_W0" ]; then
	cp -vf "$SRC_W0" "$HOME_DIR/.shortcuts/Termux-Sentinel"
	chmod 755 "$HOME_DIR/.shortcuts/Termux-Sentinel"
	echo " ✓ Installed Termux Widget: ~/.shortcuts/Termux-Sentinel"
fi

SRC_W1="$(find_src "3_Termux_Sentinel.sh")"
if [ -n "$SRC_W1" ]; then
	cp -vf "$SRC_W1" "$HOME_DIR/.shortcuts/3_Termux_Sentinel.sh"
	chmod 755 "$HOME_DIR/.shortcuts/3_Termux_Sentinel.sh"
	echo " ✓ Installed Termux Widget: ~/.shortcuts/3_Termux_Sentinel.sh"
fi

SRC_W2="$(find_src "Termux_Sentinel.sh")"
if [ -n "$SRC_W2" ]; then
	cp -vf "$SRC_W2" "$HOME_DIR/.shortcuts/Termux_Sentinel.sh"
	chmod 755 "$HOME_DIR/.shortcuts/Termux_Sentinel.sh"
	echo " ✓ Installed Termux Widget: ~/.shortcuts/Termux_Sentinel.sh"
fi

# 5. Restore Cloud & Backup Scripts
SRC_REALME="$(find_src "migrate_to_realme_bkp.sh")"
if [ -n "$SRC_REALME" ]; then
	cp -vf "$SRC_REALME" "$HOME_DIR/migrate_to_realme_bkp.sh"
	chmod +x "$HOME_DIR/migrate_to_realme_bkp.sh"
	echo " ✓ Installed Realme Cloud Migration: ~/migrate_to_realme_bkp.sh"
fi

SRC_CMF="$(find_src "migrate_to_cmf_bkp.sh")"
if [ -n "$SRC_CMF" ]; then
	cp -vf "$SRC_CMF" "$HOME_DIR/migrate_to_cmf_bkp.sh"
	chmod +x "$HOME_DIR/migrate_to_cmf_bkp.sh"
	echo " ✓ Installed CMF Cloud Migration: ~/migrate_to_cmf_bkp.sh"
fi

SRC_BKP="$(find_src "Backup_to_Drive.sh")"
if [ -n "$SRC_BKP" ]; then
	cp -vf "$SRC_BKP" "$HOME_DIR/.shortcuts/Backup_to_Drive.sh"
	chmod +x "$HOME_DIR/.shortcuts/Backup_to_Drive.sh"
	echo " ✓ Installed Backup to Drive: ~/.shortcuts/Backup_to_Drive.sh"
fi

# 6. Setup Rclone Configuration
SRC_RCLONE="$(find_src "rclone.conf")"
SRC_RCLONE_TMPL="$(find_src "rclone.conf.template")"
if [ -n "$SRC_RCLONE" ]; then
	cp -vf "$SRC_RCLONE" "$HOME_DIR/.config/rclone/rclone.conf"
	chmod 600 "$HOME_DIR/.config/rclone/rclone.conf"
	echo " ✓ Restored Rclone Configuration: ~/.config/rclone/rclone.conf"
elif [ -n "$SRC_RCLONE_TMPL" ] && [ ! -f "$HOME_DIR/.config/rclone/rclone.conf" ]; then
	cp -vf "$SRC_RCLONE_TMPL" "$HOME_DIR/.config/rclone/rclone.conf.template"
	echo " ℹ Rclone template placed at ~/.config/rclone/rclone.conf.template"
fi

echo ""
echo "=========================================================="
echo " ✓ Termux Sentinel successfully installed!"
echo "   - Run interactively: sentinel"
echo "   - Run status check:  sentinel status"
echo "   - Run system audit:  sentinel audit"
echo "=========================================================="
