#!/data/data/com.termux/files/usr/bin/bash
# =============================================================================
# CMF Device -> Google Drive Cloud Migration & Safe Mirror
# Target: gdrive:CMF_BKP/
#   ├── Emulated/   -> /storage/emulated/0
#   ├── Termux/     -> /data/data/com.termux/files/home
#   └── Ubuntu/     -> /data/data/com.termux/files/usr/var/lib/proot-distro/containers/ubuntu/rootfs
# =============================================================================

set -e

LOCK_FILE="$HOME/.rclone_backup.lock"
if [ -f "$LOCK_FILE" ]; then
	PID=$(cat "$LOCK_FILE" 2>/dev/null)
	if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
		echo "[!] Backup process is already running (PID: $PID)."
		echo "    Monitor progress with: tail -f ~/rclone_backup.log"
		exit 0
	fi
fi
echo "$$" > "$LOCK_FILE"
cleanup() {
	rm -f "$LOCK_FILE"
	if command -v termux-wake-unlock >/dev/null 2>&1; then
		termux-wake-unlock 2>/dev/null || true
	fi
}
trap cleanup EXIT INT TERM

# Auto-detect configured rclone remote (gdrive or remote_gdrive)
if rclone listremotes 2>/dev/null | grep -q "^gdrive:"; then
	DEFAULT_REMOTE="gdrive:CMF_BKP"
else
	DEFAULT_REMOTE="remote_gdrive:CMF_BKP"
fi
BASE_REMOTE="${1:-$DEFAULT_REMOTE}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
LOG_FILE="$HOME/rclone_backup.log"
SHARED_STORAGE="/storage/emulated/0"
TERMUX_HOME="$HOME"
UBUNTU_ROOT="/data/data/com.termux/files/usr/var/lib/proot-distro/containers/ubuntu/rootfs"

# Prevent Android from sleeping during upload
if command -v termux-wake-lock >/dev/null 2>&1; then
	termux-wake-lock
fi

echo "=========================================================="
echo " 📱 DEVICE -> GOOGLE DRIVE CLOUD SYNC (CMF_BKP)"
echo " Remote Target: $BASE_REMOTE"
echo " Safe Deletion: Enabled (--delete-after with --backup-dir)"
echo " Log File:      $LOG_FILE"
echo " Started At:    $(date)"
echo "=========================================================="

RCLONE_COMMON_FLAGS=(
	--links
	--fast-list
	--drive-chunk-size 64M
	--transfers 4
	--checkers 8
	--delete-after
	--log-file "$LOG_FILE"
	--log-level INFO
	-P
)

# 1. EMULATED STORAGE (/storage/emulated/0 -> CMF_BKP/Emulated)
echo ""
echo "[1/3] Syncing Local Storage (/storage/emulated/0 -> $BASE_REMOTE/Emulated)..."
if [ -d "$SHARED_STORAGE" ]; then
	rclone sync "$SHARED_STORAGE" "$BASE_REMOTE/Emulated" "${RCLONE_COMMON_FLAGS[@]}" \
		--backup-dir "$BASE_REMOTE/Trash_Archive/Emulated/$TIMESTAMP" \
		--exclude "Android/data/**" \
		--exclude "Android/obb/**" \
		--exclude ".thumbnails/**" \
		--exclude ".trashed*/**" \
		--exclude "Trash/**" \
		--exclude ".recycle/**" \
		--exclude "LOST.DIR/**"
else
	echo "  [!] Warning: $SHARED_STORAGE not accessible. Check storage permissions."
fi

# 2. TERMUX HOME DIRECTORY ($HOME -> CMF_BKP/Termux)
echo ""
echo "[2/3] Syncing Termux Directory ($TERMUX_HOME -> $BASE_REMOTE/Termux)..."
rclone sync "$TERMUX_HOME" "$BASE_REMOTE/Termux" "${RCLONE_COMMON_FLAGS[@]}" \
	--backup-dir "$BASE_REMOTE/Trash_Archive/Termux/$TIMESTAMP" \
	--exclude "storage/**" \
	--exclude ".cache/**" \
	--exclude ".npm/**" \
	--exclude ".bun/install/cache/**" \
	--exclude ".local/share/pnpm/**" \
	--exclude ".local/share/uv/cache/**" \
	--exclude "*.log"

# 3. PROOT-DISTRO UBUNTU ROOTFS (-> CMF_BKP/Ubuntu)
if [ -d "$UBUNTU_ROOT" ]; then
	echo ""
	echo "[3/3] Syncing Ubuntu PRoot-Distro ($UBUNTU_ROOT -> $BASE_REMOTE/Ubuntu)..."
	rclone sync "$UBUNTU_ROOT" "$BASE_REMOTE/Ubuntu" "${RCLONE_COMMON_FLAGS[@]}" \
		--backup-dir "$BASE_REMOTE/Trash_Archive/Ubuntu/$TIMESTAMP" \
		--exclude "proc/**" \
		--exclude "sys/**" \
		--exclude "dev/**" \
		--exclude "tmp/**" \
		--exclude "run/**" \
		--exclude ".cache/**" \
		--exclude "var/cache/**"
else
	echo ""
	echo "  [!] Info: Ubuntu rootfs not found at $UBUNTU_ROOT (skipped)."
fi

echo ""
echo "=========================================================="
echo " ✓ Cloud Sync to $BASE_REMOTE completed successfully!"
echo " Finished At: $(date)"
echo " Log file:    $LOG_FILE"
echo " Run 'sentinel' anytime to check system health."
echo "=========================================================="
