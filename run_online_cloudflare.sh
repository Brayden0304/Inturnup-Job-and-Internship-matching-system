#!/usr/bin/env bash
# ==============================================================================
# InternUp - Cloudflare Online Host Runner for Linux & macOS
# ==============================================================================

set -e

# Navigate to script directory
cd "$(dirname "$0")"

echo "========================================================================="
echo "       INTERNUP - CLOUDFLARE ONLINE HOST (LINUX / macOS / WSL)"
echo "========================================================================="
echo

# 1. Detect Python
if command -v python3 &>/dev/null; then
    PY_BIN=python3
elif command -v python &>/dev/null; then
    PY_BIN=python
else
    echo "[ERROR] Python 3 not found. Please install python3."
    exit 1
fi

# 2. Virtual environment
if [ ! -d "venv" ]; then
    echo "[1/4] Setting up Python virtual environment..."
    $PY_BIN -m venv venv
fi

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# 3. Dependencies
echo "[2/4] Verifying packages..."
pip install --quiet -r requirements.txt

# 4. Run the cross-platform python controller
echo "[3/4] Launching cross-platform online controller..."
python run_cloudflare.py
