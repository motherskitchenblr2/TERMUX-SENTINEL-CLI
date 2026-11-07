#!/data/data/com.termux/files/usr/bin/bash
# =============================================================================
# Termux:Widget Shortcut - Termux_Sentinel
# Device: Realme 12 Pro+
# =============================================================================

if command -v termux-wake-lock >/dev/null 2>&1; then
	termux-wake-lock
	trap 'termux-wake-unlock' EXIT
fi

python3 /data/data/com.termux/files/home/Termux_Sentinel.py
