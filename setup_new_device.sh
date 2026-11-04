#!/usr/bin/env bash
# ==============================================================================
# InternUp - 1-Click New Device Automated Setup (Linux / macOS / WSL)
# ==============================================================================

set -e

cd "$(dirname "$0")"

echo "========================================================================="
echo "       INTERNUP - 1-CLICK NEW DEVICE AUTOMATED SETUP (LINUX / macOS)"
echo "========================================================================="
echo

# 1. Detect Python 3
echo "[1/5] Checking Python 3..."
if command -v python3 &>/dev/null; then
    PY_BIN=python3
elif command -v python &>/dev/null; then
    PY_BIN=python
else
    echo "[ERROR] Python 3 not found."
    echo "Install via:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install -y python3 python3-venv python3-pip"
    echo "  Fedora:        sudo dnf install -y python3 python3-pip"
    echo "  macOS:         brew install python3"
    exit 1
fi
echo "      Found: $($PY_BIN --version)"

# 2. Virtual Environment
echo
echo "[2/5] Configuring virtual environment (venv)..."
if [ ! -d "venv" ] || [ ! -f "venv/bin/python" ]; then
    rm -rf venv
    $PY_BIN -m venv venv
    echo "      [OK] Clean virtual environment created."
else
    echo "      [OK] Using existing virtual environment."
fi

source venv/bin/activate

# 3. Dependencies
echo
echo "[3/5] Installing dependencies from requirements.txt..."
pip install --quiet -r requirements.txt
echo "      [OK] Dependencies installed."

# 4. Database Setup
echo
echo "[4/5] Checking Database..."
if [ ! -f "instance/app.db" ]; then
    echo "      Database missing. Seeding demo accounts and listings..."
    python seed.py
    echo "      [OK] Database seeded."
else
    echo "      [OK] Database exists."
    python db_sync_backup.py --stats
fi

# 5. Cloudflared for Linux/Mac
echo
echo "[5/5] Checking Cloudflare Tunnel binary..."
if [ ! -f "cloudflared" ]; then
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "      Downloading cloudflared for Linux..."
        curl -sL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
        chmod +x cloudflared
        echo "      [OK] Linux cloudflared binary ready."
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "      Downloading cloudflared for macOS..."
        curl -sL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64 -o cloudflared
        chmod +x cloudflared
        echo "      [OK] macOS cloudflared binary ready."
    fi
else
    chmod +x cloudflared 2>/dev/null || true
    echo "      [OK] cloudflared is present."
fi

# Make all runner scripts executable
chmod +x *.sh 2>/dev/null || true

echo
echo "========================================================================="
echo "       ***  SETUP COMPLETE! INTERNUP IS READY ON THIS DEVICE  ***"
echo "========================================================================="
echo
echo "  HOW TO RUN:"
echo "    1. OFFLINE / LOCAL:"
echo "       ./run_local.sh"
echo "       Access in browser: http://localhost:5000"
echo
echo "    2. ONLINE (Public HTTPS Cloudflare Tunnel):"
echo "       ./run_online_cloudflare.sh"
echo
echo "    3. DATABASE BACKUP & SYNC:"
echo "       ./backup_database.sh"
echo "       ./manage_database.sh"
echo "========================================================================="
echo
