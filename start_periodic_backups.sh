#!/usr/bin/env bash
# ==============================================================================
# InternUp - Periodic Database Auto-Backup Service (Linux / macOS)
# ==============================================================================

cd "$(dirname "$0")"

echo "========================================================================="
echo "             INTERNUP - PERIODIC DATABASE AUTO-BACKUP (LINUX/MAC)"
echo "========================================================================="
echo

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

if command -v python3 &>/dev/null; then
    PY_BIN=python3
else
    PY_BIN=python
fi

echo "Choose interval:"
echo "  [1] Every 15 minutes"
echo "  [2] Every 30 minutes (Default)"
echo "  [3] Every 1 hour"
echo "  [4] Run once now and exit"
echo

read -p "Select option [1-4, default 2]: " choice
choice=${choice:-1}

if [ "$choice" == "1" ]; then
    INTERVAL=15
elif [ "$choice" == "2" ]; then
    INTERVAL=30
elif [ "$choice" == "3" ]; then
    INTERVAL=60
elif [ "$choice" == "4" ]; then
    $PY_BIN periodic_backup.py --once
    exit 0
else
    INTERVAL=30
fi

echo "Starting auto-backup every $INTERVAL minutes (retention: 20 snapshots)..."
$PY_BIN periodic_backup.py --interval $INTERVAL --retention 20
