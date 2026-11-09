#!/data/data/com.termux/files/usr/bin/bash
# =============================================================================
# Android Device -> Google Drive Cloud Migration
# Target Remote: remote_gdrive:Cloud_Backup
# Target Goal: High-Efficiency Parallel Streaming (Links Preserved)
# =============================================================================

set -e

# Auto-detect configured rclone remote (gdrive or remote_gdrive)
if rclone listremotes 2>/dev/null | grep -q "^gdrive:"; then
	DEFAULT_REMOTE="gdrive:Cloud_Backup"
else
	DEFAULT_REMOTE="remote_gdrive:Cloud_Backup"
fi
BASE_REMOTE="${1:-$DEFAULT_REMOTE}"
LOG_FILE="$HOME/rclone_backup.log"
SHARED_STORAGE="/storage/emulated/0"
TERMUX_HOME="$HOME"
UBUNTU_ROOT="/data/data/com.termux/files/usr/var/lib/proot-distro/containers/ubuntu/rootfs/root"

# Prevent Android from killing process when screen is locked
if command -v termux-wake-lock >/dev/null 2>&1; then
	termux-wake-lock
	trap 'termux-wake-unlock' EXIT
fi

echo "=========================================================="
echo " 📱 ANDROID TERMINAL -> GOOGLE DRIVE CLOUD MIGRATION"
echo " Target Remote: $BASE_REMOTE"
echo " Mode: High-Efficiency Parallel Streaming (Links Preserved)"
echo " Log File: $LOG_FILE"
echo "=========================================================="

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

# 1. IMPORTANT DOCUMENTS & PROTECTED MEDIA (Targeted Mirror)
echo ""
echo "[1/4] Syncing Important Documents & Media..."
if [ -d "$SHARED_STORAGE/Important_Documents" ]; then
	echo "  -> Mirroring Important Documents to $BASE_REMOTE/Important_Documents..."
	rclone copy "$SHARED_STORAGE/Important_Documents" "$BASE_REMOTE/Important_Documents" "${RCLONE_FLAGS[@]}"
fi

if [ -d "$SHARED_STORAGE/Documents" ]; then
	echo "  -> Mirroring Documents to $BASE_REMOTE/Documents..."
	rclone copy "$SHARED_STORAGE/Documents" "$BASE_REMOTE/Documents" "${RCLONE_FLAGS[@]}"
fi

# 2. MULTIMEDIA & DOWNLOADS
echo ""
echo "[2/4] Syncing Media & Downloads (DCIM, Movies, Downloads, Pictures)..."
for FOLDER in DCIM Download Movies Pictures Documents Music Videos; do
	if [ -d "$SHARED_STORAGE/$FOLDER" ]; then
		echo "  -> Processing $FOLDER..."
		rclone copy "$SHARED_STORAGE/$FOLDER" "$BASE_REMOTE/$FOLDER" "${RCLONE_FLAGS[@]}" \
			--exclude ".thumbnails/**" \
			--exclude "Trash/**" \
			--exclude ".trashed*/**"
	fi
done

# 3. TERMUX CLI SCRIPTS, WORKSPACES & CONFIGURATIONS
echo ""
echo "[3/4] Syncing Termux Workspaces & Configurations..."
rclone copy "$TERMUX_HOME" "$BASE_REMOTE/Termux_Home" "${RCLONE_FLAGS[@]}" \
	--exclude ".cache/**" \
	--exclude ".npm/**" \
	--exclude ".bun/install/cache/**" \
	--exclude ".local/share/pnpm/**" \
	--exclude ".local/share/uv/cache/**" \
	--exclude "storage/**" \
	--exclude "*.log"

# 4. PROOT-DISTRO UBUNTU WORKSPACE (/root)
if [ -d "$UBUNTU_ROOT" ]; then
	echo ""
	echo "[4/4] Syncing Ubuntu PRoot-Distro Workspace (/root)..."
	rclone copy "$UBUNTU_ROOT" "$BASE_REMOTE/Ubuntu_Root" "${RCLONE_FLAGS[@]}" \
		--exclude ".cache/**" \
		--exclude ".npm/**"
fi

echo ""
echo "=========================================================="
echo " ✓ Cloud Sync to $BASE_REMOTE completed successfully!"
echo " Log file: $LOG_FILE"
echo " Run 'sentinel' to audit and purge caches."
echo "=========================================================="
