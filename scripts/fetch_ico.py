#!/usr/bin/env python3
"""Fetch the ICO Coffee Market Report for the previous month into ico/<YYYY-MM>/.

ICO posts month M's report during month M+1, on no fixed day (5th to 30th
over 2024-26). The routine checks on the 25th and, if it is not out yet,
again on the last day of the month.

Usage:
    python3 scripts/fetch_ico.py                  # report for last month
    python3 scripts/fetch_ico.py 2026-08          # a specific report month
    python3 scripts/fetch_ico.py --last-day-only  # no-op unless today (UTC) is month-end

Exit codes (the routine branches on these):
    0  report downloaded to ico/<YYYY-MM>/source/ -> build the cards
    3  cards already built for that month (ico/<YYYY-MM>/out/ has PNGs) -> nothing to do
    4  ICO has not posted the report yet -> try again at the next slot
    5  --last-day-only and today is not the last day of the month -> nothing to do
"""
import calendar
import datetime as dt
import pathlib
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
UA = {"User-Agent": "Mozilla/5.0 (Malenadu Dara report fetcher)"}


def report_url(year, month):
    # Coffee year runs October-September: Oct 2025 .. Sep 2026 live in cy2025-26.
    start = year if month >= 10 else year - 1
    cy = f"cy{start}-{str(start + 1)[2:]}"
    return f"https://www.ico.org/documents/{cy}/cmr-{month:02d}{str(year)[2:]}-e.pdf"


def main(argv):
    today = dt.datetime.now(dt.timezone.utc).date()
    args = [a for a in argv if not a.startswith("--")]

    if "--last-day-only" in argv:
        if today.day != calendar.monthrange(today.year, today.month)[1]:
            print(f"{today}: not the last day of the month, skipping")
            return 5

    if args:
        year, month = map(int, args[0].split("-"))
    else:
        last = today.replace(day=1) - dt.timedelta(days=1)
        year, month = last.year, last.month

    tag = f"{year}-{month:02d}"
    folder = ROOT / "ico" / tag
    if any((folder / "out").glob("*.png")):
        print(f"{tag}: cards already built in {folder / 'out'}")
        return 3

    url = report_url(year, month)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
            data = r.read()
            modified = r.headers.get("Last-Modified", "unknown")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"{tag}: not posted yet ({url} -> 404)")
            return 4
        raise

    if not data.startswith(b"%PDF"):
        print(f"{tag}: {url} did not return a PDF, treating as not posted")
        return 4

    dest = folder / "source" / url.rsplit("/", 1)[1]
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    print(f"{tag}: downloaded {len(data):,} bytes to {dest.relative_to(ROOT)}")
    print(f"ICO posted it: {modified}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
