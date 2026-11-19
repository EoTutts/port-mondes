#!/bin/sh
set -eu
root=${A11Y_GAME_DIR:-$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)}
export A11Y_GAME_DIR="$root"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONHOME="$root/python38/usr"
export PYTHONPATH="$root/vendor:$root/engine:$root/sdk"
export LD_LIBRARY_PATH="$root/compat/lib:$PYTHONHOME/lib:$PYTHONHOME/lib/aarch64-linux-gnu:${LD_LIBRARY_PATH:-}"
cd "$root"
if [ "${1:-}" = "--check-runtime" ]; then
    exec "$PYTHONHOME/bin/python3.8" -c 'import sys, ctypes, socket, pickle; from PIL import Image; from r36s_a11y.speech import _user_voice; print("Port Mondes: Python", sys.version.split()[0], "ctypes/Pillow/SDK OK; configurações da voz:", _user_voice())'
fi
exec "$PYTHONHOME/bin/python3.8" "$root/sdk/main.py"
