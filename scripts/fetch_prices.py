#!/usr/bin/env python3
"""Fetch the previous session's closing prices into sources/<date>/prices/.

Three markets, three sources, none of them a plain page scrape -- investing.com
and stooq both sit behind a bot wall, so the numbers come from the endpoints
that serve those pages their data:

  Robusta  ICE Europe RC1!   TradingView scanner, USD per tonne
  Arabica  ICE US     KC=F   Yahoo daily bar, US cents per lb
  Pepper   IPSTA FMC daily market report PDF, rupees per quintal

Arabica takes Yahoo because that is a settled daily bar; the TradingView quote
for KC1! is a delayed last price that can sit days stale, and it rides along as
a cross-check instead. When the two disagree by more than 2% the entry carries a
"disagreement" field -- check both before the number goes on a card.

Run it at 06:00 IST and every market is shut: ICE London settles ~21:30 IST and
ICE US ~01:00 IST, the IPSTA report goes up the previous evening. So what comes
back is the previous session's close, which is what the card carries.

IPSTA's certificate is expired, so its HTTPS is unverified and the PDF link the
page gives is plain http. The report date is taken from the page's own table,
never from the PDF's overlapped date line.

Writes sources/<date>/prices/prices.json plus the raw pepper PDF, and prints a
human-readable summary.

Exit codes
  0  every market fetched
  1  some markets fetched, some missing (prices.json holds what came back)
  2  nothing fetched
"""

import argparse
import datetime as dt
import json
import pathlib
import re
import ssl
import subprocess
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

TRADINGVIEW = "https://scanner.tradingview.com/futures/scan"
TV_COLUMNS = ["close", "change", "change_abs", "open", "high", "low",
              "currency", "description", "update_time"]
TV_SYMBOLS = {"ICEEUR:RC1!": "robusta", "ICEUS:KC1!": "arabica"}

YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/KC=F?range=10d&interval=1d"

IPSTA_PAGE = "https://ipstaindia.com/market-data.php"
IPSTA_ROW = re.compile(
    r"<th[^>]*>\s*\d+\.\s*</th>\s*<td[^>]*>\s*([^<]+?)\s*</td>\s*"
    r"<td[^>]*>\s*<a href=\"([^\"]+\.pdf)\"", re.I | re.S)
PEPPER_LINE = re.compile(r"([A-Z][A-Z0-9 ]*[A-Z0-9])?\s+(\d{4,6})\s+(\d{4,6})\s+"
                         r"(\d{4,6})\s+(\d{4,6})\s*$")
SPOT_NOTE = re.compile(r"With Spot\s*:\s*([A-Z ]+)")

NO_VERIFY = ssl.create_default_context()
NO_VERIFY.check_hostname = False
NO_VERIFY.verify_mode = ssl.CERT_NONE


def get(url, data=None, headers=None, context=None, timeout=60):
    head = {"User-Agent": UA}
    head.update(headers or {})
    return urllib.request.urlopen(
        urllib.request.Request(url, data, head), timeout=timeout, context=context).read()


def fetch_futures():
    """Robusta and Arabica off the TradingView scanner."""
    payload = {"symbols": {"tickers": list(TV_SYMBOLS), "query": {"types": []}},
               "columns": TV_COLUMNS}
    body = get(TRADINGVIEW, json.dumps(payload).encode(),
               {"Content-Type": "application/json",
                "Origin": "https://www.tradingview.com",
                "Referer": "https://www.tradingview.com/"})
    out = {}
    for row in json.loads(body).get("data", []):
        name = TV_SYMBOLS.get(row["s"])
        if not name:
            continue
        cells = dict(zip(TV_COLUMNS, row["d"]))
        stamp = cells.get("update_time")
        out[name] = {
            "symbol": row["s"],
            "close": cells["close"],
            "change_pct": cells["change"],
            "change_abs": cells["change_abs"],
            "open": cells["open"], "high": cells["high"], "low": cells["low"],
            "unit": ("USD per tonne" if cells["currency"] == "USD"
                     else "US cents per lb"),
            "contract": cells["description"],
            "as_of": (dt.datetime.fromtimestamp(stamp, dt.timezone.utc).isoformat()
                      if stamp else None),
            "source": "TradingView scanner (%s)" % row["s"],
        }
    return out


def fetch_arabica_yahoo():
    """Last two daily settles for Coffee C -- cross-check for the scanner."""
    chart = json.loads(get(YAHOO))["chart"]["result"][0]
    closes = [(t, c) for t, c in zip(chart["timestamp"],
                                     chart["indicators"]["quote"][0]["close"])
              if c is not None]
    if not closes:
        raise RuntimeError("no daily closes in the Yahoo response")
    stamp, close = closes[-1]
    prev = closes[-2][1] if len(closes) > 1 else None
    return {
        "symbol": "KC=F",
        "close": round(close, 2),
        "change_abs": round(close - prev, 2) if prev else None,
        "change_pct": round((close - prev) / prev * 100, 2) if prev else None,
        "unit": "US cents per lb",
        "contract": chart["meta"].get("shortName") or "Coffee C",
        "as_of": dt.datetime.fromtimestamp(stamp, dt.timezone.utc).date().isoformat(),
        "source": "Yahoo Finance daily bar (KC=F)",
    }


def fetch_pepper(out_dir):
    """The latest IPSTA daily market report: date and link off the page's table."""
    html = get(IPSTA_PAGE, context=NO_VERIFY).decode("utf-8", "replace")
    rows = IPSTA_ROW.findall(html)
    if not rows:
        raise RuntimeError("no report rows on %s -- the page layout may have changed"
                           % IPSTA_PAGE)
    when, link = rows[0]
    report_date = dt.datetime.strptime(when.replace(",", ""), "%d %b %Y").date()

    pdf = get(link, context=NO_VERIFY)
    if not pdf.startswith(b"%PDF"):
        raise RuntimeError("%s did not return a PDF" % link)
    path = out_dir / ("ipsta-pepper-%s.pdf" % report_date.isoformat())
    path.write_bytes(pdf)

    grades = {}
    text = ""
    try:
        text = subprocess.run(["pdftotext", "-layout", str(path), "-"],
                              capture_output=True, text=True, timeout=60).stdout
    except (OSError, subprocess.SubprocessError) as exc:
        print("pdftotext unavailable (%s) -- saved the PDF, read it by hand" % exc,
              file=sys.stderr)

    # The report prints some grades to the left of their row and some, like
    # "500 GL", on the line underneath it -- so an unlabelled row waits for the
    # next label line rather than being dropped.
    pending = None
    for line in text.splitlines():
        match = PEPPER_LINE.search(line.rstrip())
        if match:
            row = {"open": int(match.group(2)), "high": int(match.group(3)),
                   "low": int(match.group(4)), "close": int(match.group(5))}
            name = (match.group(1) or "").strip()
            if name:
                grades[name] = row
            else:
                pending = row
            continue
        # "500 GL" opens with a digit, so a label is anything with a letter in
        # it -- the first such line after the row is the grade it belongs to.
        stripped = line.strip()
        if pending and any(c.isalpha() for c in stripped):
            grades[stripped] = pending
            pending = None

    spot = SPOT_NOTE.search(text)
    return {
        "report_date": report_date.isoformat(),
        "grades": grades,
        "unit": "rupees per quintal (100 kg)",
        "spot_note": spot.group(1).strip() if spot else None,
        "pdf": path.name,
        "source": "IPSTA daily market report, %s" % link,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", help="edition date (YYYY-MM-DD); default today")
    ap.add_argument("--out", help="directory to write into; "
                                  "default sources/<date>/prices/")
    args = ap.parse_args()

    date = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
    out_dir = (pathlib.Path(args.out) if args.out
               else ROOT / "sources" / date.isoformat() / "prices")
    out_dir.mkdir(parents=True, exist_ok=True)

    prices = {"edition_date": date.isoformat(),
              "fetched_at": dt.datetime.now().astimezone().isoformat(),
              "markets": {}, "errors": {}}

    try:
        prices["markets"].update(fetch_futures())
    except Exception as exc:                       # noqa: BLE001 - reported, not raised
        prices["errors"]["futures"] = str(exc)

    delayed = prices["markets"].pop("arabica", None)
    try:
        arabica = fetch_arabica_yahoo()
        if delayed:
            arabica["cross_check"] = delayed
            gap = abs(arabica["close"] - delayed["close"]) / arabica["close"] * 100
            if gap > 2:
                arabica["disagreement"] = (
                    "Yahoo %s vs TradingView %s (%.1f%% apart) -- likely different "
                    "contract months, or the delayed quote is stale. Check before "
                    "this goes on a card."
                    % (arabica["close"], delayed["close"], gap))
        prices["markets"]["arabica"] = arabica
    except Exception as exc:                       # noqa: BLE001
        prices["errors"]["arabica_yahoo"] = str(exc)
        if delayed:
            prices["markets"]["arabica"] = delayed

    try:
        prices["markets"]["pepper"] = fetch_pepper(out_dir)
    except Exception as exc:                       # noqa: BLE001
        prices["errors"]["pepper"] = str(exc)

    path = out_dir / "prices.json"
    path.write_text(json.dumps(prices, indent=2), encoding="utf-8")

    got = prices["markets"]
    for name in ("robusta", "arabica"):
        row = got.get(name)
        if row:
            print("%-8s %10s  %s  (%+.2f%%, %s)  [%s]"
                  % (name, row["close"], row["unit"], row.get("change_pct") or 0,
                     row.get("as_of"), row["source"]))
            if row.get("disagreement"):
                print("         ! %s" % row["disagreement"])
    if "pepper" in got:
        pep = got["pepper"]
        grades = ", ".join("%s %s" % (k, v["close"]) for k, v in pep["grades"].items())
        print("pepper   %s  %s  (report %s)"
              % (grades or "see PDF", pep["unit"], pep["report_date"]))
    for where, why in prices["errors"].items():
        print("failed: %s: %s" % (where, why), file=sys.stderr)

    print("wrote %s" % path)
    if not got:
        return 2
    return 1 if len(got) < 3 else 0


if __name__ == "__main__":
    sys.exit(main())
