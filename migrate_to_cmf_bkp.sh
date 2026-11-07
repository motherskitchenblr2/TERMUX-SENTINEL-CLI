#!/data/data/com.termux/files/usr/bin/bash
# =============================================================================
# CMF PHONE 1 (Nothing Mobiles) -> Google Drive Cloud Migration
# Device: CMF Phone 1 by Nothing (128 GB ROM / 8 GB RAM)
# Target Remote: pasha_gdrive:CMF_BKP
# Target Goal: 50+ GB Storage Reclamation & Real-Time Sync
# Google Account: Pasha0118@gmail.com
# =============================================================================

set -e

BASE_REMOTE="pasha_gdrive:CMF_BKP"
LOG_FILE="$HOME/rclone_cmf_backup.log"
SHARED_STORAGE="/storage/emulated/0"
TERMUX_HOME="$HOME"
UBUNTU_ROOT="/data/data/com.termux/files/usr/var/lib/proot-distro/containers/ubuntu/rootfs/root"

# Prevent Android from killing process when screen is locked
if command -v termux-wake-lock >/dev/null 2>&1; then
	termux-wake-lock
	trap 'termux-wake-unlock' EXIT
fi

echo "=========================================================="
echo " 📱 CMF PHONE 1 -> GOOGLE DRIVE CLOUD MIGRATION"
echo " Account: Pasha0118@gmail.com"
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

# 1. WHATSAPP & TELEGRAM (Targeted Protected Mirror)
echo ""
echo "[1/4] Syncing WhatsApp & Telegram Media..."
if [ -d "$SHARED_STORAGE/Android/media/com.whatsapp" ]; then
	echo "  -> Mirroring WhatsApp Media to $BASE_REMOTE/WhatsApp/Media..."
	rclone copy "$SHARED_STORAGE/Android/media/com.whatsapp" "$BASE_REMOTE/WhatsApp/Media" "${RCLONE_FLAGS[@]}"
fi

if [ -d "$SHARED_STORAGE/Telegram" ]; then
	echo "  -> Mirroring Telegram Media to $BASE_REMOTE/Telegram..."
	rclone copy "$SHARED_STORAGE/Telegram" "$BASE_REMOTE/Telegram" "${RCLONE_FLAGS[@]}"
fi

# 2. HEAVY MULTIMEDIA & DOWNLOADS (Reclaiming the 50 GB)
echo ""
echo "[2/4] Syncing Phone Multimedia (DCIM, Movies, Downloads, Pictures)..."
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
echo " Run 'python3 ~/Termux_Sentinel.py' to audit and purge caches."
echo "=========================================================="
