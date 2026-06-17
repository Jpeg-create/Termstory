#!/bin/bash
set -e

echo "=== TermStory Installer v0.6.0 ==="

PYTHON=""; for cmd in python3 python; do command -v $cmd &>/dev/null && PYTHON=$cmd && break; done
[ -z "$PYTHON" ] && { echo "Python 3 not found"; exit 1; }
echo "  $($PYTHON --version)"

TMPDIR=$(mktemp -d)
echo "  Downloading..."
curl -fsSL "https://github.com/bitflicker64/Termstory/archive/refs/heads/main.tar.gz" -o "$TMPDIR/termstory.tar.gz"
tar -xzf "$TMPDIR/termstory.tar.gz" -C "$TMPDIR"
cd "$TMPDIR/Termstory-main"

echo "  Installing..."
# PEP 668 systems (Ubuntu 24.04+, Debian 13+, Python 3.12+) need --break-system-packages
# Try standard, then --user, then --break-system-packages
if $PYTHON -m pip install -e . &>/dev/null; then
  : # success
elif $PYTHON -m pip install --user -e . &>/dev/null; then
  : # success
else
  $PYTHON -m pip install --break-system-packages -e .
fi

cd /; rm -rf "$TMPDIR"

# Verify
if $PYTHON -c "import termstory" 2>/dev/null; then
  # Find where it was installed
  BIN="$HOME/.local/bin/termstory"
  [ -f "$BIN" ] && chmod +x "$BIN" 2>/dev/null
  if command -v termstory &>/dev/null; then
    echo "  ✅ Installed! Run: termstory today"
  else
    echo "  ✅ Installed! Add to ~/.zshrc: export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo "  Then: termstory today"
  fi
else
  echo "  ❌ Installation failed. Trying venv..."
  $PYTHON -m venv "$HOME/.termstory-venv"
  "$HOME/.termstory-venv/bin/pip" install -e . 2>&1 | tail -1
  echo "  ✅ Installed in venv. Run: $HOME/.termstory-venv/bin/termstory today"
  echo "  Or add to ~/.zshrc: export PATH=\"\$HOME/.termstory-venv/bin:\$PATH\""
fi
