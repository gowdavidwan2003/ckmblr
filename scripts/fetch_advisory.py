#!/usr/bin/env python3
"""Fetch the Coffee Board monthly Advisory PDF into sources/advisories/<YYYY-MM>/.

Like Market_Info.aspx, Advisories.aspx is an ASP.NET postback page -- but it
takes two rounds. First POST the year/month/language dropdowns back with
Submit to get the result grid; that response carries fresh hidden fields and a
per-row image button. POST *those* back with the button's .x/.y and the
response body is the PDF, with the Board's own name in content-disposition
(20268AugKan.pdf).

Event validation is on, so the hidden fields from one response cannot be reused
for the next -- each stage re-reads them.

Exit codes
  0  at least one advisory was saved (or was already on disk)
  1  the advisory for that month is not published yet
  2  the fetch failed (network, unexpected response)
"""

import argparse
import datetime as dt
import pathlib
import re
import sys
import urllib.parse
import urllib.request

URL = "https://coffeeboard.gov.in/Advisories.aspx"
UA = "Mozilla/5.0 (compatible; malenadu-dara/1.0)"
ROOT = pathlib.Path(__file__).resolve().parent.parent

# The dropdowns post 1-based indices, not the labels shown.
YEAR_BASE = 2018                      # option "1" is 2018
LANGUAGES = {"english": 1, "kannada": 2, "hindi": 3, "telugu": 4,
             "tamil": 5, "malayalam": 6, "odia": 7}

HIDDEN = re.compile(r"<input[^>]*type=\"hidden\"[^>]*>", re.I)
NAME = re.compile(r'name="([^"]*)"')
VALUE = re.compile(r'value="([^"]*)"')
# <input type="image" name="GridView1$ctl02$ImageButton1" ...>
IMAGE_BUTTON = re.compile(r'<input[^>]*type="image"[^>]*name="([^"]*)"', re.I)
UPLOADED = re.compile(r">(\d{1,2}/\d{1,2}/\d{4}[^<]*)<")


def hidden_fields(html):
    fields = {}
    for tag in HIDDEN.findall(html):
        name = NAME.search(tag)
        value = VALUE.search(tag)
        if name:
            fields[name.group(1)] = value.group(1) if value else ""
    return fields


def post(data, referer=URL):
    req = urllib.request.Request(
        URL,
        urllib.parse.urlencode(data).encode(),
        {"User-Agent": UA, "Content-Type": "application/x-www-form-urlencoded",
         "Referer": referer},
    )
    return urllib.request.urlopen(req, timeout=90)


def fetch(year, month, language):
    """Return (pdf_bytes, filename, uploaded_text) or None if not published."""
    req = urllib.request.Request(URL, headers={"User-Agent": UA})
    html = urllib.request.urlopen(req, timeout=90).read().decode("utf-8", "replace")

    # Stage one: apply the filter.
    data = hidden_fields(html)
    data.update({
        "ddYear": str(year - YEAR_BASE + 1),
        "ddlMonth": str(month),
        "ddl_Lang": str(LANGUAGES[language]),
        "Submit": "Submit",
    })
    grid = post(data).read().decode("utf-8", "replace")

    button = IMAGE_BUTTON.search(grid)
    if not button:
        return None                                # no row -- not published yet

    uploaded = UPLOADED.search(grid)

    # Stage two: click the row's PDF button, with that page's own hidden fields.
    data = hidden_fields(grid)
    data.update({
        "ddYear": str(year - YEAR_BASE + 1),
        "ddlMonth": str(month),
        "ddl_Lang": str(LANGUAGES[language]),
        button.group(1) + ".x": "7",
        button.group(1) + ".y": "7",
    })
    resp = post(data)
    body = resp.read()

    if not body.startswith(b"%PDF"):
        raise RuntimeError(
            "expected a PDF, got %s (%d bytes) -- the page layout may have changed"
            % (resp.headers.get("Content-Type"), len(body))
        )

    disposition = resp.headers.get("content-disposition", "")
    name = re.search(r"filename=([^;]+)", disposition)
    filename = name.group(1).strip().strip('"') if name else None

    return body, filename, uploaded.group(1).strip() if uploaded else "unknown"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--month", help="month to fetch (YYYY-MM); default this month")
    ap.add_argument("--lang", default="kannada,english",
                    help="comma-separated languages; default kannada,english")
    ap.add_argument("--out", help="directory to save into; default "
                                  "sources/advisories/<YYYY-MM>/")
    args = ap.parse_args()

    if args.month:
        year, month = (int(p) for p in args.month.split("-"))
    else:
        today = dt.datetime.now().date()
        year, month = today.year, today.month
    tag = "%04d-%02d" % (year, month)

    languages = [l.strip().lower() for l in args.lang.split(",") if l.strip()]
    for language in languages:
        if language not in LANGUAGES:
            print("unknown language: %s" % language, file=sys.stderr)
            return 2

    out_dir = pathlib.Path(args.out) if args.out else ROOT / "sources" / "advisories" / tag
    saved = 0
    missing = []

    for language in languages:
        try:
            result = fetch(year, month, language)
        except Exception as exc:                   # noqa: BLE001 - reported, not raised
            print("fetch failed (%s): %s" % (language, exc), file=sys.stderr)
            return 2

        if result is None:
            missing.append(language)
            continue

        body, filename, uploaded = result
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / ("advisory-%s-%s.pdf" % (tag, language))

        if path.exists() and path.read_bytes() == body:
            print("already saved: %s" % path)
            saved += 1
            continue

        path.write_bytes(body)
        print("saved %s (%d KB, board file %s, uploaded %s)"
              % (path, len(body) // 1024, filename, uploaded))
        saved += 1

    if missing:
        print("not up yet for %s: %s" % (tag, ", ".join(missing)))

    return 0 if saved else 1


if __name__ == "__main__":
    sys.exit(main())
