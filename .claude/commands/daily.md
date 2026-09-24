---
description: Build today's Malenadu Dara daily cards (Kannada + English)
---

Build today's daily post using the `malenadu-dara-daily` skill.

Extra instruction from me, if any: $ARGUMENTS

Steps:

1. Work out today's date and create `editions/<YYYY-MM-DD>/today/{work,out}/`.
   The full daily post lives in `today/`; `market/` and `news/` sit beside it.
2. Rates: find today's Coffee Board daily PDF **and yesterday's** — the
   day-on-day change column needs both. Fallback order is in the skill. Save
   whatever you fetch into `sources/<YYYY-MM-DD>/`. If only one report exists,
   leave the change column as em-dashes and print the reason on the card. If
   it's a Sunday or a holiday, carry the last published rates with the
   no-new-report notice.
3. News: search for the day's coffee news — Brazil and Vietnam weather and
   shipments, exchange stocks, Indian export policy, Coffee Board
   announcements, rain in Kodagu and Chikmagaluru. Prefer primary sources.
   Every item needs a source line. Filter: does it plausibly affect what a
   Karnataka grower gets paid?
4. Show me the Kannada and English copy before building, so I can correct the
   register.
5. Copy the templates into `today/work/`, fill them in, then build the carousels and
   the WhatsApp image.
6. View every PNG. Confirm 1080x1350, no clipping, Kannada rendering as letters
   not boxes, QR surviving recompress. Then present them in filename order,
   Kannada first, and say which files are the carousel and which is WhatsApp.

No buy/sell call anywhere on the cards.
