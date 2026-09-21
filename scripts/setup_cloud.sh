#!/usr/bin/env bash
# Setup for the Linux cloud sandbox (Claude Code routines).
#
# The sandbox is Debian-based, so it gets the original engine pair -- WeasyPrint
# for HTML->PDF and pdftoppm for PDF->PNG -- rather than the Chrome/Ghostscript
# fallback the Windows machine uses. Same templates, same cards.
#
# Safe to re-run: apt and pip both no-op when everything is already present.
set -u

SUDO=""
if [ "$(id -u)" -ne 0 ]; then
  command -v sudo >/dev/null 2>&1 && SUDO="sudo"
fi

echo "--- apt: poppler + pango (WeasyPrint's GTK dependencies)"
$SUDO apt-get update -qq || echo "apt-get update failed, continuing"
$SUDO apt-get install -y --no-install-recommends \
    poppler-utils \
    libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b libffi-dev \
    fontconfig \
  || echo "apt-get install failed, continuing -- check_setup.py will report what is missing"

echo "--- pip: build dependencies"
python3 -m pip install --quiet -r "$(dirname "$0")/../requirements.txt" \
  || echo "pip install failed, continuing"

echo "--- what this machine can build with"
python3 "$(dirname "$0")/check_setup.py"
