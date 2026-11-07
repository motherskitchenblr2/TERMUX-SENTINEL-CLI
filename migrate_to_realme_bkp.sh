#!/data/data/com.termux/files/usr/bin/bash
# =============================================================================
# Complete & Safe Backup to Google Drive (rclone)
# Device: Realme 12 Pro+ | Android Termux + Ubuntu proot-distro
# =============================================================================

set -e

BASE_REMOTE="pasha_gdrive:Realme_BKP"
LOG_FILE="$HOME/rclone_backup.log"
UBUNTU_ROOT="/data/data/com.termux/files/usr/var/lib/proot-distro/containers/ubuntu/rootfs/root"
TERMUX_HOME="$HOME"

# Prevent Android from killing process when screen is off
if command -v termux-wake-lock >/dev/null 2>&1; then
	termux-wake-lock
	trap 'termux-wake-unlock' EXIT
fi

echo "========================================================"
echo "=== Migration & Full Backup Started: $(date) ==="
echo "=== Log output: $LOG_FILE ==="
echo "========================================================"

# Common high-efficiency rclone flags for Google Drive
# - --copy-links / --links: preserves Linux symlinks as .rclonelink
# - --fast-list: queries Google Drive directories in batch (prevents rate-limiting)
# - --drive-chunk-size 64M: uploads multi-gigabyte models/archives much faster
# - --transfers 4 --checkers 8: optimal parallel transfers for mobile connection
RCLONE_FLAGS=(
	--links
	--fast-list
	--drive-chunk-size 64M
	--transfers 4
	--checkers 8
	--log-file "$LOG_FILE"
	--log-level INFO
	-P
)

# -----------------------------------------------------------------------------
# 1. PHONE MULTIMEDIA & SHARED STORAGE
# -----------------------------------------------------------------------------
echo ""
echo "[1/3] Syncing Phone Multimedia & Downloads..."
if [ -d "$HOME/storage/shared" ]; then
	for FOLDER in DCIM Movies Download Pictures Documents Music; do
		if [ -d "$HOME/storage/shared/$FOLDER" ]; then
			echo "  -> Processing $FOLDER..."
			rclone copy "$HOME/storage/shared/$FOLDER" "$BASE_REMOTE/$FOLDER" \
				"${RCLONE_FLAGS[@]}" \
				--exclude ".thumbnails/**" \
				--exclude "Trash/**" \
				--exclude ".trashed*/**"
		fi
	done
fi

# -----------------------------------------------------------------------------
# 2. PROOT-DISTRO UBUNTU WORKSPACE (/root)
# -----------------------------------------------------------------------------
echo ""
echo "[2/3] Backing up Ubuntu Container Rootfs Workspace..."
if [ -d "$UBUNTU_ROOT" ]; then
	echo "  Source: $UBUNTU_ROOT"
	echo "  Target: $BASE_REMOTE/Ubuntu_Root"
	rclone copy "$UBUNTU_ROOT" "$BASE_REMOTE/Ubuntu_Root" \
		"${RCLONE_FLAGS[@]}" \
		--exclude ".cache/**" \
		--exclude ".local/share/Trash/**" \
		--exclude "tmp/**"
else
	echo "  [ERROR] Ubuntu root path not found: $UBUNTU_ROOT" >&2
	exit 1
fi

# -----------------------------------------------------------------------------
# 3. TERMUX NATIVE WORKSPACE ($HOME)
# -----------------------------------------------------------------------------
echo ""
echo "[3/3] Backing up Termux Native Directory..."
echo "  Source: $TERMUX_HOME"
echo "  Target: $BASE_REMOTE/Termux_Home"
# CRITICAL: Exclude 'storage/**' to prevent recursively following Android storage symlinks
rclone copy "$TERMUX_HOME" "$BASE_REMOTE/Termux_Home" \
	"${RCLONE_FLAGS[@]}" \
	--exclude "storage/**" \
	--exclude ".cache/**" \
	--exclude ".npm/_cacache/**" \
	--exclude ".local/share/Trash/**" \
	--exclude "rclone_backup.log"

echo ""
echo "========================================================"
echo "=== Full Backup Completed Successfully: $(date) ==="
echo "========================================================"
