#!/usr/bin/env python3
"""Snapshot the Coffee Board statistics page and report what changed.

coffee-statistics.html is a plain static page -- no ASP.NET postback, unlike
Market_Info.aspx and Advisories.aspx. It carries the production estimates by
state and district, the holdings count, the country-wise export PDFs and the
domestic consumption series. The Board edits it in place with no version or
date stamp, so the only way to know something moved is to keep the last
snapshot and diff against it.

The snapshot is the page's visible text plus the hrefs of every document it
links, so a newly posted export PDF counts as a change even when no number on
the page moved.

Exit codes
  0  the page changed (or this is the first snapshot) -- diff on stdout
  1  no change since the last snapshot
  2  the fetch failed (network, unexpected response)
"""

import argparse
import datetime as dt
import difflib
import html
import pathlib
import re
import sys
import urllib.request

URL = "https://coffeeboard.gov.in/coffee-statistics.html"
UA = "Mozilla/5.0 (compatible; malenadu-dara/1.0)"
ROOT = pathlib.Path(__file__).resolve().parent.parent
SNAP_DIR = ROOT / "sources" / "statistics"

DOC = re.compile(r'(?is)href="([^"]+\.(?:pdf|xls|xlsx|doc|docx|csv))"')
TAGS = re.compile(r"(?is)<(script|style|noscript).*?</\1>")


def normalise(page):
    """The page reduced to the lines worth diffing."""
    body = TAGS.sub(" ", page)
    text = html.unescape(re.sub(r"(?s)<[^>]+>", "\n", body))
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in text.split("\n")]
    lines = [ln for ln in lines if ln]
    docs = sorted({html.unescape(h) for h in DOC.findall(page)})
    return "\n".join(lines + ["", "-- linked documents --"] + docs) + "\n"


def fetch():
    req = urllib.request.Request(URL, headers={"User-Agent": UA})
    resp = urllib.request.urlopen(req, timeout=90)
    body = resp.read().decode("utf-8", "replace")
    if "coffee" not in body.lower() or len(body) < 5000:
        raise RuntimeError(
            "got %d bytes that do not look like the statistics page" % len(body))
    return body


def previous(before):
    """The newest snapshot on or before `before`, or None.

    On or before, not before: a second run the same day should diff against
    that morning's snapshot rather than report itself as the first one.
    """
    snaps = sorted(p for p in SNAP_DIR.glob("*/coffee-statistics.txt")
                   if p.parent.name <= before)
    return snaps[-1] if snaps else None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--date", help="snapshot date to file under (YYYY-MM-DD); default today")
    ap.add_argument("--no-save", action="store_true",
                    help="check for a change without writing a snapshot")
    args = ap.parse_args()

    stamp = args.date or dt.date.today().isoformat()

    try:
        page = fetch()
    except Exception as exc:                       # noqa: BLE001 - reported, not raised
        print("fetch failed: %s" % exc, file=sys.stderr)
        return 2

    text = normalise(page)
    prior = previous(stamp)

    if prior is None:
        print("first snapshot: nothing to compare against")
    else:
        old = prior.read_text(encoding="utf-8")
        if old == text:
            print("no change since %s" % prior.parent.name)
            return 1
        diff = difflib.unified_diff(
            old.splitlines(), text.splitlines(),
            fromfile="coffee-statistics %s" % prior.parent.name,
            tofile="coffee-statistics %s" % stamp, lineterm="", n=3)
        print("\n".join(diff))

    if not args.no_save:
        out = SNAP_DIR / stamp
        out.mkdir(parents=True, exist_ok=True)
        (out / "coffee-statistics.html").write_text(page, encoding="utf-8")
        (out / "coffee-statistics.txt").write_text(text, encoding="utf-8")
        print("\nsaved %s" % (out / "coffee-statistics.txt"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
