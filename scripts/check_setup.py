#!/usr/bin/env python3
"""Say whether this machine can build a card, and what it would build it with.

Run it after setup, or any time the build starts behaving oddly:

    python3 scripts/check_setup.py

The pipeline needs one engine for HTML -> PDF and one for PDF -> PNG. The
original pair is WeasyPrint and pdftoppm; headless Chrome and Ghostscript
stand in for them where those are not installed, which is the normal case on
Windows. Either pair renders the same cards.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.join(HERE, "..", ".claude", "skills", "malenadu-dara-daily", "scripts")
sys.path.insert(0, os.path.abspath(SKILL))

import render_backend as rb   # noqa: E402


def main():
    ok = True

    print("python      ", sys.version.split()[0], "-", sys.executable)

    for mod, why in (("PIL", "image checks"), ("numpy", "image checks"),
                     ("cv2", "QR decoding")):
        if rb.importable(mod):
            print("%-12s ok  (%s)" % (mod, why))
        else:
            print("%-12s MISSING - pip install -r requirements.txt" % mod)
            ok = False

    print()
    if rb.importable("weasyprint"):
        print("HTML -> PDF  WeasyPrint")
    elif rb.chrome():
        print("HTML -> PDF  headless Chrome/Edge:", rb.chrome())
        print("             (WeasyPrint is not usable here - it needs GTK, which")
        print("              Windows does not ship. Chrome renders the same cards.)")
    else:
        print("HTML -> PDF  NOTHING AVAILABLE")
        print("             Install Chrome or Edge, or set MALENADU_CHROME.")
        ok = False

    import shutil
    if shutil.which("pdftoppm"):
        print("PDF -> PNG   pdftoppm:", shutil.which("pdftoppm"))
    elif rb.ghostscript():
        print("PDF -> PNG   Ghostscript:", rb.ghostscript())
    else:
        print("PDF -> PNG   NOTHING AVAILABLE")
        print("             Install poppler (pdftoppm) or Ghostscript,")
        print("             or set MALENADU_GS.")
        ok = False

    print()
    print(rb.report())
    if ok:
        print("\nReady. Build a set with:")
        print("  cd editions/<date>")
        print("  python3 ../../.claude/skills/malenadu-dara-daily/scripts/"
              "build_cards.py out/ work/today-kn.html work/today-en.html")
    else:
        print("\nNot ready - see the missing pieces above.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
