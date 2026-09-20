#!/usr/bin/env python3
"""Render the Malenadu Dara newsletter HTML into shareable PNGs.

Usage:
    python3 scripts/build_images.py out/ template-1-summary.html template-2-details.html

For each input HTML it writes a single trimmed PNG, then checks that any QR
code in the page still decodes after a simulated WhatsApp downscale and
recompress. That check is the point of this script — a QR that decodes from
the pristine PNG can easily fail once WhatsApp has had it, and you cannot see
that by looking.
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_backend

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")
FONT = os.path.join(ASSETS, "NotoSansKannada.ttf")
DPI = 160

FACE = """<style>
@font-face {{ font-family:'NotoKan'; src:url('file://{p}'); font-weight:400; }}
@font-face {{ font-family:'NotoKan'; src:url('file://{p}'); font-weight:700; }}
</style>"""


def ensure(mod, pkg=None):
    if render_backend.importable(mod):
        return
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", pkg or mod,
                        "--break-system-packages", "-q"], check=True)
    except Exception:
        pass          # render_backend picks an engine from what is present


def render(src, outdir):
    from PIL import Image
    import numpy as np

    stem = os.path.splitext(os.path.basename(src))[0]
    pdf = os.path.join(outdir, stem + ".pdf")
    png = os.path.join(outdir, stem + ".png")

    html = open(src, encoding="utf-8").read()
    html = html.replace("</head>", FACE.format(p=os.path.abspath(FONT)) + "</head>", 1)
    render_backend.html_to_pdf(html, os.path.dirname(os.path.abspath(src)), pdf)

    raw = render_backend.pdf_to_pngs(pdf, os.path.join(outdir, stem + "-raw"),
                                     DPI, first=1, last=1)[0]
    with Image.open(raw) as opened:     # closed before the remove below - Windows
        im = opened.convert("RGB")
    a = np.asarray(im)
    w, h = im.size
    # Trim trailing blank space: the page is deliberately over-tall so nothing
    # splits across two pages, then cropped back to the content.
    nonwhite = (a < 245).any(axis=2).any(axis=1)
    last = int(nonwhite.nonzero()[0].max())
    im.crop((0, 0, w, min(h, last + 2))).save(png)
    os.remove(raw)
    os.remove(pdf)
    return png


def check_qr(png):
    """Decode the QR after simulated WhatsApp compression. Returns None if the
    page has no QR, True/False otherwise."""
    from PIL import Image

    with Image.open(png) as opened:
        im = opened.convert("RGB")
    if not render_backend.decode_qr(im):
        return None  # no readable QR on this page at all

    for width in (800, 1000, 1280):
        shipped = render_backend.jpeg_roundtrip(im, quality=55, width=width)
        if not render_backend.decode_qr(shipped):
            return False
    return True


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    outdir, sources = sys.argv[1], sys.argv[2:]
    os.makedirs(outdir, exist_ok=True)

    if not render_backend.html_engine():
        ensure("weasyprint")      # nothing here can draw HTML yet; try for one
    ensure("PIL", "pillow")
    ensure("numpy")
    ensure("cv2", "opencv-python-headless")
    print(render_backend.report())

    for src in sources:
        png = render(src, outdir)
        from PIL import Image
        print(f"{png}  {Image.open(png).size}")
        ok = check_qr(png)
        if ok is True:
            print("   QR survives compression")
        elif ok is False:
            print("   QR FAILS after compression — enlarge it (see references/brand.md)")
        else:
            print("   no QR on this page")

    print("\nView each PNG before sending. Kannada shaping failures render as "
          "empty boxes and are otherwise silent.")


if __name__ == "__main__":
    main()
