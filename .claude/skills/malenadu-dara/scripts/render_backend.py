#!/usr/bin/env python3
"""HTML -> PDF -> PNG with whatever this machine actually has.

The build was written around WeasyPrint and pdftoppm, which is what
scripts/setup.sh gets you on macOS and Linux. Windows has neither without a
GTK runtime and a poppler build, so this module falls back to headless Chrome
or Edge for the HTML step and to Ghostscript for the raster step.

Nothing about the cards changes. Where WeasyPrint and pdftoppm are installed
they are still used, in preference, and this module stays out of the way.
Chrome shapes Kannada through HarfBuzz much as Pango does; the templates are
untouched either way.

Override the auto-detection with MALENADU_CHROME / MALENADU_GS if the browser
or Ghostscript lives somewhere unusual.
"""

import glob
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_CHROME_NAMES = ["chrome", "google-chrome", "google-chrome-stable", "chromium",
                 "chromium-browser", "msedge", "microsoft-edge"]

_CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
]

_GS_NAMES = ["gs", "gswin64c", "gswin32c"]
_GS_GLOBS = [r"C:\Program Files\gs\*\bin\gswin64c.exe",
             r"C:\Program Files (x86)\gs\*\bin\gswin32c.exe"]


def _find(env, names, paths=(), globs=()):
    override = os.environ.get(env)
    if override:
        return override
    for n in names:
        found = shutil.which(n)
        if found:
            return found
    for p in paths:
        if os.path.exists(p):
            return p
    for g in globs:
        hits = sorted(glob.glob(g))
        if hits:
            return hits[-1]          # newest version installed
    return None


_WEASY = "unprobed"


def _weasyprint():
    """WeasyPrint, or None. Importing it raises OSError - not ImportError -
    when the Pango libraries are missing, which is the usual Windows case, and
    it prints a multi-line installation notice on the way out. That notice is
    not an error here - it just means this machine takes the Chrome path - so
    it is swallowed, and the answer cached so it is not printed once per card."""
    global _WEASY
    if _WEASY != "unprobed":
        return _WEASY
    import contextlib
    import io

    try:
        with contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            from weasyprint import HTML
        _WEASY = HTML
    except Exception:
        _WEASY = None
    return _WEASY


def importable(mod):
    """Can this module be imported? Quietly - a half-installed WeasyPrint
    talks on the way out, and that is this module's business, not the
    operator's."""
    import contextlib
    import io

    try:
        with contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            __import__(mod)
        return True
    except Exception:
        return False


def chrome():
    return _find("MALENADU_CHROME", _CHROME_NAMES, _CHROME_PATHS)


def ghostscript():
    return _find("MALENADU_GS", _GS_NAMES, globs=_GS_GLOBS)


def html_engine():
    """What will render the HTML, or None if nothing can.

    Worth asking before pip-installing WeasyPrint: on Windows it installs
    cleanly and still never imports, so a build that tried would reach for pip
    on every run and be no better off."""
    if _weasyprint():
        return "WeasyPrint"
    exe = chrome()
    return "headless " + os.path.splitext(os.path.basename(exe))[0] if exe else None


def report():
    """One line naming the engines in use, so the operator knows what drew the
    cards they are about to look at."""
    html = html_engine() or "NONE"
    raster = "pdftoppm" if shutil.which("pdftoppm") else (
        "Ghostscript" if ghostscript() else "NONE")
    return "renderer: %s -> %s" % (html, raster)


# --------------------------------------------------------------- HTML -> PDF

def html_to_pdf(html, base_url, pdf_path):
    """Render an HTML string to a single PDF.

    base_url is the directory relative URLs resolve against - the tall-image
    templates pull in channel-qr.png that way, so it has to be the folder the
    working copy lives in.
    """
    HTML = _weasyprint()
    if HTML is not None:
        HTML(string=html, base_url=base_url).write_pdf(pdf_path)
        return

    exe = chrome()
    if exe is None:
        sys.exit("No HTML renderer: WeasyPrint will not load and no Chrome or "
                 "Edge was found. Install one, or set MALENADU_CHROME.")

    # Chrome needs a file on disk, and it has to sit in base_url so relative
    # asset references still resolve.
    tmp = os.path.join(base_url or ".", ".malenadu-render-%d.html" % os.getpid())
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(html)
        subprocess.run([exe, "--headless", "--disable-gpu", "--disable-extensions",
                        "--no-pdf-header-footer",
                        "--print-to-pdf=" + os.path.abspath(pdf_path),
                        Path(tmp).absolute().as_uri()],
                       check=True, capture_output=True)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

    if not os.path.exists(pdf_path):
        sys.exit("%s produced no PDF for %s" % (os.path.basename(exe), base_url))


# --------------------------------------------------------------- PDF -> PNG

def pdf_to_pngs(pdf_path, prefix, dpi, first=None, last=None, snap=None):
    """Rasterise a PDF to one PNG per page, named the way pdftoppm names them:
    prefix-1.png, or prefix-01.png once there are ten or more pages.

    snap=(w, h) trims a page that comes out a pixel or two over that size.
    Chrome writes a 1080x1350 card as a 1013.04pt page rather than 1012.5pt,
    which Ghostscript then rounds up to 1351 rows. Cropping that overshoot
    keeps the cards pixel-exact without rescaling the type; anything further
    off is left alone, so the size check in the build script still fails loudly.
    """
    outdir = os.path.dirname(prefix) or "."
    stem = os.path.basename(prefix)
    if shutil.which("pdftoppm"):
        cmd = ["pdftoppm", "-png", "-r", str(dpi)]
        if first:
            cmd += ["-f", str(first)]
        if last:
            cmd += ["-l", str(last)]
        subprocess.run(cmd + [pdf_path, prefix], check=True)
    else:
        gs = ghostscript()
        if gs is None:
            sys.exit("No rasteriser: neither pdftoppm (poppler) nor Ghostscript "
                     "was found. Install one, or set MALENADU_GS.")
        cmd = [gs, "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=png16m",
               "-r" + str(dpi), "-dTextAlphaBits=4", "-dGraphicsAlphaBits=4"]
        if first:
            cmd.append("-dFirstPage=%d" % first)
        if last:
            cmd.append("-dLastPage=%d" % last)
        cmd += ["-o", prefix + "-%d.png", pdf_path]
        subprocess.run(cmd, check=True, capture_output=True)
        _pad_names(outdir, stem)

    pages = sorted(f for f in os.listdir(outdir)
                   if f.startswith(stem + "-") and f.endswith(".png"))
    paths = [os.path.join(outdir, p) for p in pages]
    if snap:
        for p in paths:
            _snap(p, snap)
    return paths


def _pad_names(outdir, stem):
    """Ghostscript counts 1, 2 ... 10; pdftoppm pads to a fixed width so the
    files sort in page order. A twenty-card carousel uploads in filename
    order, so the padding is not cosmetic."""
    pages = [f for f in os.listdir(outdir)
             if f.startswith(stem + "-") and f.endswith(".png")]
    width = len(str(len(pages)))
    if width < 2:
        return
    for f in pages:
        n = f[len(stem) + 1:-4]
        if n.isdigit() and len(n) < width:
            os.replace(os.path.join(outdir, f),
                       os.path.join(outdir, "%s-%0*d.png" % (stem, width, int(n))))


def _snap(png, size):
    from PIL import Image

    with Image.open(png) as im:
        w, h = im.size
        if (w, h) == size:
            return
        if 0 <= w - size[0] <= 2 and 0 <= h - size[1] <= 2:
            im.crop((0, 0, size[0], size[1])).save(png)


def decode_qr(im):
    """Decode the QR in a page image, or return "" if there is none.

    cv2's detector reads the QR happily from a crop but often fails to *find*
    it in a whole tall page - the QR is only about 130px in a 1322x1925 image.
    A miss there reads as "no QR on this page", which quietly skips the check
    the build is running in the first place, so fall back to sweeping
    overlapping windows before believing there is no QR.
    """
    import cv2
    import numpy as np

    det = cv2.QRCodeDetector()

    def read(pil):
        arr = np.array(pil.convert("RGB"))[:, :, ::-1].copy()
        try:
            text = det.detectAndDecode(arr)[0]
        except cv2.error:
            return ""
        return text or ""

    found = read(im)
    if found:
        return found

    # Several window sizes, tightest first: the detector is fussy about how
    # much other content shares the frame. The QR on a tall WhatsApp page
    # reads inside a 400px window and is missed inside a 660px one.
    w, h = im.size
    for win in (400, 640, 900):
        if win > max(w, h):
            break
        step = win // 2
        for top in range(0, max(1, h - win // 2), step):
            for left in range(0, max(1, w - win // 2), step):
                box = (left, top, min(left + win, w), min(top + win, h))
                if box[2] - box[0] < 200 or box[3] - box[1] < 200:
                    continue
                found = read(im.crop(box))
                if found:
                    return found
    return ""


def jpeg_roundtrip(im, quality=55, width=None):
    """Re-encode an image the way an upload does, and hand back what comes out.

    The QR checks need a scratch JPEG; the original scripts wrote /tmp/_ig.jpg,
    which is not a path Windows has.
    """
    from PIL import Image

    if width:
        im = im.resize((width, int(im.size[1] * width / im.size[0])), Image.LANCZOS)
    fd, tmp = tempfile.mkstemp(suffix=".jpg")
    os.close(fd)
    try:
        im.save(tmp, quality=quality)
        with Image.open(tmp) as out:
            return out.convert("RGB").copy()
    finally:
        os.remove(tmp)
