#!/usr/bin/env python3
"""Fetch the Coffee Board daily Market Info PDF into sources/<date>/.

The Coffee Board serves the report through an ASP.NET postback on
Market_Info.aspx rather than a static URL: POST the page's hidden fields back
with __EVENTTARGET=lbnmarketinfo and the response body is the PDF itself, with
the report date in the content-disposition filename.

Exit codes
  0  a PDF was saved (or was already on disk)
  1  the site is serving an older report -- today's is not up yet
  2  the fetch failed (network, unexpected response)
"""

import argparse
import datetime as dt
import pathlib
import re
import sys
import urllib.parse
import urllib.request

URL = "https://coffeeboard.gov.in/Market_Info.aspx"
UA = "Mozilla/5.0 (compatible; malenadu-dara/1.0)"
ROOT = pathlib.Path(__file__).resolve().parent.parent

# Ma_18-09-2026_Coffee Market Report _18_September 2026.pdf
FILENAME_DATE = re.compile(r"Ma_(\d{2})-(\d{2})-(\d{4})_")
PDF_DATE = re.compile(rb"/(?:Creation|Mod)Date\s*\(D:(\d{14})")


def hidden_fields(html):
    fields = {}
    for tag in re.findall(r"<input[^>]*type=\"hidden\"[^>]*>", html):
        name = re.search(r'name="([^"]*)"', tag)
        value = re.search(r'value="([^"]*)"', tag)
        if name:
            fields[name.group(1)] = value.group(1) if value else ""
    return fields


def fetch():
    """Return (report_date, pdf_bytes, generated_at or None)."""
    req = urllib.request.Request(URL, headers={"User-Agent": UA})
    html = urllib.request.urlopen(req, timeout=90).read().decode("utf-8", "replace")

    data = hidden_fields(html)
    data.update({"__EVENTTARGET": "lbnmarketinfo", "__EVENTARGUMENT": ""})
    req = urllib.request.Request(
        URL,
        urllib.parse.urlencode(data).encode(),
        {"User-Agent": UA, "Content-Type": "application/x-www-form-urlencoded",
         "Referer": URL},
    )
    resp = urllib.request.urlopen(req, timeout=90)
    body = resp.read()

    if not body.startswith(b"%PDF"):
        raise RuntimeError(
            "expected a PDF, got %s (%d bytes) -- the page layout may have changed"
            % (resp.headers.get("Content-Type"), len(body))
        )

    disposition = resp.headers.get("content-disposition", "")
    match = FILENAME_DATE.search(disposition)
    if not match:
        raise RuntimeError("no report date in content-disposition: %r" % disposition)
    day, month, year = (int(g) for g in match.groups())

    stamps = PDF_DATE.findall(body)
    generated = None
    if stamps:
        generated = dt.datetime.strptime(max(stamps).decode(), "%Y%m%d%H%M%S")

    return dt.date(year, month, day), body, generated


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--date", help="report date to require (YYYY-MM-DD); default today")
    ap.add_argument("--any", action="store_true",
                    help="save whatever report is up, even an older one")
    ap.add_argument("--out", help="directory to save into; default sources/<report date>/")
    args = ap.parse_args()

    want = (dt.date.fromisoformat(args.date) if args.date
            else dt.datetime.now().date())

    try:
        report_date, body, generated = fetch()
    except Exception as exc:                       # noqa: BLE001 - reported, not raised
        print("fetch failed: %s" % exc, file=sys.stderr)
        return 2

    stamp = generated.strftime("%H:%M") if generated else "unknown time"

    if report_date != want and not args.any:
        print("not up yet: latest report is %s (generated %s), waiting for %s"
              % (report_date, stamp, want))
        return 1

    out_dir = pathlib.Path(args.out) if args.out else ROOT / "sources" / report_date.isoformat()
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / ("coffee-board-%s.pdf" % report_date.isoformat())

    if path.exists() and path.read_bytes() == body:
        print("already saved: %s" % path)
        return 0

    path.write_bytes(body)
    print("saved %s (%d KB, report %s, generated %s)"
          % (path, len(body) // 1024, report_date, stamp))
    return 0


if __name__ == "__main__":
    sys.exit(main())
