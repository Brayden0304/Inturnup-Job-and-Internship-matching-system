#!/usr/bin/env bash
# ==============================================================================
# InternUp - Database Backup Runner for Linux & macOS
# ==============================================================================

cd "$(dirname "$0")"

echo "========================================================================="
echo "             INTERNUP - ONE-CLICK DATABASE BACKUP (LINUX/MAC)"
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

$PY_BIN db_sync_backup.py --backup
echo
$PY_BIN db_sync_backup.py --stats

echo
echo "========================================================================="
echo "[SUCCESS] Backup complete! Snapshots stored in ./backups/"
echo "========================================================================="
