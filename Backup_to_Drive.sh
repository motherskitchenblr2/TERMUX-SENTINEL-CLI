#!/data/data/com.termux/files/usr/bin/bash

# Prevent phone from sleeping during upload
termux-wake-lock

echo "=========================================="
echo "    Storage -> Google Drive Backup        "
echo "=========================================="
echo ""

BASE_REMOTE="remote_gdrive:Cloud_Backup"
LOCAL_STORAGE="/storage/emulated/0"
UBUNTU_PATH="/data/data/com.termux/files/usr/var/lib/proot-distro/installed-rootfs/ubuntu"

# -------------------------------------------------------------------------
# 1. IMPORTANT DOCUMENTS & PROTECTED MEDIA (Targeted Backup)
# -------------------------------------------------------------------------
echo "[1/4] Backing up Important Documents & Media..."

# Important Documents
if [ -d "$LOCAL_STORAGE/Important_Documents" ]; then
	echo "-> Uploading Important Documents..."
	rclone copy "$LOCAL_STORAGE/Important_Documents" \
		"$BASE_REMOTE/Important_Documents" --fast-list -P -v
fi

# Documents & Data
if [ -d "$LOCAL_STORAGE/Documents" ]; then
	echo "-> Uploading Documents..."
	rclone copy "$LOCAL_STORAGE/Documents" \
		"$BASE_REMOTE/Documents" --fast-list -P -v
fi

# -------------------------------------------------------------------------
# 2. LOCAL PHONE STORAGE (All folders except 'Android')
# -------------------------------------------------------------------------
echo ""
echo "[2/4] Mirroring Phone Storage (Excluding /Android)..."
rclone copy "$LOCAL_STORAGE" "$BASE_REMOTE/Shared_Storage" \
	--exclude "/Android/**" \
	--exclude ".thumbnails/**" \
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
