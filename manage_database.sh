#!/usr/bin/env bash
cd "$(dirname "$0")"

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

if command -v python3 &>/dev/null; then
    python3 db_sync_backup.py
else
    python db_sync_backup.py
fi
