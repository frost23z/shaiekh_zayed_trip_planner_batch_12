#!/usr/bin/env bash

set -euo pipefail

# Always run from the repository root, no matter where the script is called from.
cd "$(dirname "${BASH_SOURCE[0]}")"

VENV_DIR=".venv"

echo "==> Checking virtual environment..."

if [ ! -d "$VENV_DIR" ]; then
    echo "==> Creating virtual environment..."
    python3 -m venv "$VENV_DIR"

    echo "==> Upgrading pip..."
    "$VENV_DIR/bin/python" -m pip install --upgrade pip
fi

echo "==> Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "==> Installing dependencies..."
python -m pip install -r requirements.txt

echo "==> Starting Smart Group Trip Planner API..."
exec python run.py
