#!/data/data/com.termux/files/usr/bin/bash

# Prevent phone from sleeping during upload
termux-wake-lock

echo "=========================================="
echo "    Realme_BKP -> Google Drive Backup     "
echo "=========================================="
echo ""

BASE_REMOTE="pasha_gdrive:Realme_BKP"
LOCAL_STORAGE="/storage/emulated/0"
UBUNTU_PATH="/data/data/com.termux/files/usr/var/lib/proot-distro/installed-rootfs/ubuntu"

# -------------------------------------------------------------------------
# 1. WHATSAPP & TELEGRAM (Targeted Backup)
# -------------------------------------------------------------------------
echo "[1/4] Backing up WhatsApp & Telegram..."

# WhatsApp Media
if [ -d "$LOCAL_STORAGE/Android/media/com.whatsapp" ]; then
	echo "-> Uploading WhatsApp Media..."
	rclone copy "$LOCAL_STORAGE/Android/media/com.whatsapp" \
		"$BASE_REMOTE/What & Tell_Back-up/WhatsApp/Media" --fast-list -P -v
fi

# WhatsApp Data (attempts read; logs warning if restricted by OS)
if [ -d "$LOCAL_STORAGE/Android/data/com.whatsapp" ]; then
	echo "-> Uploading WhatsApp Data..."
	rclone copy "$LOCAL_STORAGE/Android/data/com.whatsapp" \
		"$BASE_REMOTE/What & Tell_Back-up/WhatsApp/Data" --fast-list -P -v 2>/dev/null || echo "Skipping restricted WhatsApp data directory."
fi

# Telegram Data
if [ -d "$LOCAL_STORAGE/Android/data/org.telegram.messenger" ]; then
	echo "-> Uploading Telegram App Data..."
	rclone copy "$LOCAL_STORAGE/Android/data/org.telegram.messenger" \
		"$BASE_REMOTE/What & Tell_Back-up/Telegram/Data" --fast-list -P -v 2>/dev/null || echo "Skipping restricted Telegram data directory."
fi

# Telegram Public Media (Documents, Images, Video)
if [ -d "$LOCAL_STORAGE/Telegram" ]; then
	echo "-> Uploading Telegram Shared Media..."
	rclone copy "$LOCAL_STORAGE/Telegram" \
		"$BASE_REMOTE/What & Tell_Back-up/Telegram/Media" --fast-list -P -v
fi

# -------------------------------------------------------------------------
# 2. LOCAL PHONE STORAGE (All folders except 'Android')
# -------------------------------------------------------------------------
echo ""
echo "[2/4] Mirroring Phone Storage (Excluding /Android)..."
# Uses copy to preserve original structure; frees space safely
# To delete local files after upload to save storage, change 'copy' to 'move'
rclone copy "$LOCAL_STORAGE" "$BASE_REMOTE" \
	--exclude "/Android/**" \
	--exclude ".thumbnails/**" \
	--exclude "Telegram/**" \
	--fast-list -P -v

# -------------------------------------------------------------------------
# 3. PROOT-DISTRO UBUNTU WORKSPACE
# -------------------------------------------------------------------------
echo ""
echo "[3/4] Migrating Ubuntu Rootfs Projects / Data..."
if [ -d "$UBUNTU_PATH/root" ]; then
	rclone move "$UBUNTU_PATH/root" "$BASE_REMOTE/Ubuntu_Root" \
		--fast-list -P -v \
		--exclude ".cache/**" \
		--exclude ".local/share/Trash/**"
fi

# -------------------------------------------------------------------------
# 4. TERMUX NATIVE WORKSPACE
# -------------------------------------------------------------------------
echo ""
echo "[4/4] Migrating Termux Native Directory..."
if [ -d "$HOME/projects" ]; then
	rclone move "$HOME/projects" "$BASE_REMOTE/Termux_Projects" --fast-list -P -v
fi

echo ""
echo "=========================================="
echo "    Backup Finished Successfully!         "
echo "=========================================="

termux-wake-unlock
read -n 1 -s -r -p "Press any key to close..."
