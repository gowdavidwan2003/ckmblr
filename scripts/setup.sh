#!/usr/bin/env bash
# One-time setup for the card build pipeline.
set -e

DIR="$(dirname "$0")"

python3 -m pip install -r "$DIR/../requirements.txt" || true

# WeasyPrint needs GTK and will not import without it, and pdftoppm comes from
# poppler. Neither ships on Windows, so the build falls back to headless Chrome
# and Ghostscript there. check_setup.py reports which pair this machine has and
# exits non-zero if it has neither.
#
#   macOS:  brew install poppler
#   Ubuntu: sudo apt install poppler-utils libpango-1.0-0 libpangoft2-1.0-0
#   Windows: nothing to install if Chrome or Edge is present; Ghostscript from
#            https://ghostscript.com/releases/ covers the raster step.

python3 "$DIR/check_setup.py"
