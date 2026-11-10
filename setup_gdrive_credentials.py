#!/usr/bin/env python3
"""
Setup Google Drive OAuth Credentials in Rclone from client_secret.json.
Extracts client_id and client_secret and updates ~/.config/rclone/rclone.conf.
"""

import configparser
import glob
import json
import os
import sys

CONFIG_PATH = os.path.expanduser("~/.config/rclone/rclone.conf")


def find_client_secret(custom_path=None):
    if custom_path and os.path.isfile(custom_path):
        return custom_path

    search_patterns = [
        os.path.expanduser("~/client_secret*.json"),
        os.path.expanduser("~/*.json"),
        "/storage/emulated/0/Download/client_secret*.json",
        "/storage/emulated/0/Download/*.json",
    ]

    for pattern in search_patterns:
        for file_path in glob.glob(pattern):
            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
                    if "installed" in data or "web" in data or "client_id" in data:
                        return file_path
            except Exception:
                continue
    return None


def main():
    target_file = sys.argv[1] if len(sys.argv) > 1 else None
    secret_file = find_client_secret(target_file)

    if not secret_file:
        print("[!] No valid client_secret.json found in ~ or /storage/emulated/0/Download/")
        print("    Usage: python3 setup_gdrive_credentials.py [/path/to/client_secret.json]")
        sys.exit(1)

    print(f"[*] Found credentials file: {secret_file}")

    with open(secret_file, encoding="utf-8") as f:
        data = json.load(f)

    creds = data.get("installed") or data.get("web") or data
    client_id = creds.get("client_id")
    client_secret = creds.get("client_secret")

    if not client_id or not client_secret:
        print("[!] Error: Could not extract client_id or client_secret from file.")
        sys.exit(1)

    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    cfg = configparser.ConfigParser()
    if os.path.isfile(CONFIG_PATH):
        cfg.read(CONFIG_PATH)

    if "gdrive" not in cfg:
        cfg.add_section("gdrive")

    cfg["gdrive"]["type"] = "drive"
    cfg["gdrive"]["scope"] = "drive"
    cfg["gdrive"]["client_id"] = client_id
    cfg["gdrive"]["client_secret"] = client_secret

    # Clear any old invalid token so rclone knows to authenticate cleanly
    if "token" in cfg["gdrive"]:
        del cfg["gdrive"]["token"]

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        cfg.write(f)

    print(
        "[✓] Successfully updated ~/.config/rclone/rclone.conf with your OAuth Client credentials!"
    )
    print("\n[NEXT STEP] Run the following command in Termux to authorize with Google Drive:")
    print("    rclone config reconnect gdrive:\n")


if __name__ == "__main__":
    main()
