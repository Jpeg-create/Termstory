#!/bin/bash
# TermStory — One-command install from source
# curl -fsSL https://raw.githubusercontent.com/bitflicker64/Termstory/main/install.sh | bash

set -e

echo "=== TermStory Installer v0.6.0 ==="
echo ""

# Detect Python
PYTHON=""
for cmd in python3 python; do
  command -v $cmd &>/dev/null && PYTHON=$cmd && break
done
[ -z "$PYTHON" ] && { echo "❌ Python 3 not found. Install: https://python.org"; exit 1; }
PYVER=$($PYTHON --version 2>&1)
echo "  ✓ $PYVER"

# Ensure pip
$PYTHON -m pip install --upgrade pip setuptools wheel -q 2>/dev/null || true

# Install from GitHub source
echo "  ↓ Downloading TermStory v0.6.0..."
TMPDIR=$(mktemp -d)
curl -fsSL "https://github.com/bitflicker64/Termstory/archive/refs/heads/main.tar.gz" -o "$TMPDIR/termstory.tar.gz"
tar -xzf "$TMPDIR/termstory.tar.gz" -C "$TMPDIR"

echo "  🔧 Installing..."
cd "$TMPDIR/Termstory-main"
$PYTHON -m pip install -e . 2>&1 | tail -3

# Cleanup
cd /; rm -rf "$TMPDIR"

echo ""
# Verify
if $PYTHON -m termstory.cli --version 2>/dev/null || $PYTHON -m termstory.cli today --help &>/dev/null; then
  echo "✅ Installed! Run: termstory today"
else
  echo "⚠️  Install dir may need PATH: $PYTHON -m termstory.cli today"
fi
