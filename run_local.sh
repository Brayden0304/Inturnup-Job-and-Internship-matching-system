#!/usr/bin/env bash
# ==============================================================================
# InternUp - Local Development Runner for Linux & macOS
# ==============================================================================

set -e

# Navigate to script directory
cd "$(dirname "$0")"

echo "========================================================================="
echo "       INTERNUP - LOCAL RUNNER (LINUX / macOS / WSL)"
echo "========================================================================="
echo

# 1. Check Python 3
if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
elif command -v python &>/dev/null; then
    PYTHON_CMD=python
else
    echo "[ERROR] Python 3 is not installed. Please install it using:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install -y python3 python3-venv python3-pip"
    echo "  Fedora:        sudo dnf install -y python3 python3-pip"
    echo "  Arch:          sudo pacman -S python python-pip"
    exit 1
fi

echo "[1/4] Using Python: $($PYTHON_CMD --version)"

# 2. Virtual environment setup
if [ ! -d "venv" ]; then
    echo "[2/4] Creating virtual environment (venv)..."
    $PYTHON_CMD -m venv venv
fi

# Activate venv
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# 3. Install requirements
echo "[3/4] Checking dependencies..."
pip install --quiet -r requirements.txt

# 4. Seed database if missing
if [ ! -f "instance/app.db" ]; then
    echo "[4/4] Initializing database with demo data..."
    python seed.py
else
    echo "[4/4] Database ready (instance/app.db)."
fi

echo
echo "========================================================================="
echo " Launching InternUp at: http://127.0.0.1:5000"
echo " Press Ctrl+C to stop the server."
echo "========================================================================="
echo

python app.py
