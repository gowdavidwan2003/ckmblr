#!/usr/bin/env python3
"""Render a multi-card HTML into one 1080x1350 PNG per card, for Instagram
and Facebook carousels.

Usage:
    python3 scripts/build_cards.py out/ cards-daily-kn.html [more.html ...]

Each <section class="card"> becomes one slide, exported as <stem>-01.png,
<stem>-02.png and so on, ready to upload in order.

Why 1080x1350: Instagram caps uploads at 1080 wide and 1350 tall, so 4:5 is
the tallest feed post available. Carousels take up to 20 slides and lock every
slide to the first slide's ratio, so all cards must be identical in size.
The profile grid crops 4:5 to the centre 1012px, which is why the templates
use 64px side padding — text and logos stay inside the safe zone.

The script also checks that any QR still decodes after a simulated upload
recompress. A QR that scans on your screen can easily fail after Instagram
has had it.
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_backend

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")
FONT = os.path.join(ASSETS, "NotoSansKannada.ttf")
DPI = 96          # CSS px are 96/inch, so this yields exactly 1080x1350

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
    stem = os.path.splitext(os.path.basename(src))[0]
    pdf = os.path.join(outdir, stem + ".pdf")
    html = open(src, encoding="utf-8").read()
    html = html.replace("</head>", FACE.format(p=os.path.abspath(FONT)) + "</head>", 1)
    render_backend.html_to_pdf(html, os.path.dirname(os.path.abspath(src)), pdf)

    pages = render_backend.pdf_to_pngs(pdf, os.path.join(outdir, stem), DPI,
                                       snap=(1080, 1350))
    os.remove(pdf)
    return pages


def check(png):
    """Verify size, and decode any QR after a simulated upload recompress."""
    from PIL import Image

    with Image.open(png) as opened:
        im = opened.convert("RGB")
    size_ok = im.size == (1080, 1350)

    if not render_backend.decode_qr(im):
        return size_ok, None            # no QR on this card

    shipped = render_backend.jpeg_roundtrip(im, quality=55)  # platforms re-encode hard
    return size_ok, bool(render_backend.decode_qr(shipped))


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
        pages = render(src, outdir)
        print(f"\n{os.path.basename(src)} -> {len(pages)} cards")
        for p in pages:
            size_ok, qr = check(p)
            note = "1080x1350" if size_ok else "WRONG SIZE - carousel will crop"
            if qr is True:
                note += ", QR survives recompress"
            elif qr is False:
                note += ", QR FAILS after recompress - enlarge it"
            print(f"  {os.path.basename(p)}  {note}")

    print("\nUpload the cards in filename order. Check each one before posting: "
          "Kannada shaping failures render as empty boxes and are silent.")


if __name__ == "__main__":
    main()
