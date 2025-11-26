#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "[EnvSnap] Build (macOS)"

PY=""
if [[ -x ".venv/bin/python" ]]; then
  PY=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PY="python3"
elif command -v python >/dev/null 2>&1; then
  PY="python"
else
  echo "Python not found. Install Python 3.x first."
  exit 2
fi

# create venv if missing
if [[ ! -x ".venv/bin/python" ]]; then
  echo "[EnvSnap] Creating venv..."
  $PY -m venv .venv
fi

VPY=".venv/bin/python"

echo "[EnvSnap] Upgrading pip..."
"$VPY" -m pip install --upgrade pip >/dev/null

echo "[EnvSnap] Installing PyInstaller..."
"$VPY" -m pip install --upgrade pyinstaller >/dev/null

echo "[EnvSnap] Cleaning old outputs..."
rm -rf dist build

echo "[EnvSnap] Building EnvSnap_mac.app ..."
"$VPY" -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name EnvSnap_mac \
  --paths python_core \
  python_core/envsnap_gui.py

echo
echo "[EnvSnap] Done."
echo "Output: dist/EnvSnap_mac.app"