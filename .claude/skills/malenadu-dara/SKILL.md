---
name: "malenadu-dara"
description: Produce the Malenadu Dara monthly coffee newsletter — turn an ICO Coffee Market Report (or similar commodity report) into branded 1080x1350 card sets for Instagram, Facebook and WhatsApp, in spoken Kannada and English, for coffee growers in Karnataka. Use whenever the user uploads or mentions a coffee market report, ICO report, I-CIP prices, coffee export or stock figures, the monthly newsletter, Malenadu Dara, or asks for a Kannada summary, Kannada PDF, or a grower-facing brief. Also use for any request to render Kannada text into a PDF or image, since it carries the font and rendering setup needed to do that correctly.
---

# Malenadu Dara — monthly coffee brief

Default output is **two carousels of 1080x1350 cards — one Kannada, one
English** — for Instagram, Facebook and WhatsApp. The audience is a working
coffee planter in Karnataka: not an analyst, not a reader of literary Kannada.

Always produce both languages unless the user says otherwise. They are separate
posts, not two halves of one; each set stands on its own with its own cover and
its own closing card.

Three rules carry most of the value. Each was learned by getting it wrong:

1. **Spoken Kannada, not written Kannada.** The default register a model
   reaches for is newspaper Kannada, and a grower will not read it.
   `references/kannada-style.md` has the vocabulary swaps. Read it before
   writing any copy.
2. **Forces, not a verdict.** The top box lays out what pushes prices up and
   what pushes them down. It never recommends holding or selling.
3. **Check the render as an image.** Kannada shaping failures and oversize
   pages are silent in the PDF pipeline and obvious in the PNG.

## Workflow

1. Read the source report — the figures are in the first two pages plus the
   summary tables at the end.
2. Draft the Kannada copy per `references/kannada-style.md`.
3. Copy `assets/cards-monthly-kn.html` and `assets/cards-monthly-en.html` to a
   working directory and replace the copy, keeping the card structure.
   `references/cards.md` covers sizing, the contact slot and the card order.
   For the two WhatsApp templates, copy `assets/channel-qr.png` into that
   working directory as well — they reference it by relative path, and without
   it the tall image builds with a hole where the QR should be.
4. Build:
   ```bash
   python3 scripts/build_cards.py out/ work/cards-monthly-kn.html work/cards-monthly-en.html
   ```
5. View every card. Confirm Kannada renders as letters not boxes, nothing is
   clipped at the card edge, each card reports 1080x1350, and the closing card
   reports the QR surviving recompress.
6. Present each set in filename order, Kannada first.

## Output per channel

Different channels need different shapes. Produce what the destination needs,
not one file for everything.

| Channel | Output | Templates |
|---|---|---|
| Instagram, Facebook | Carousel: 6 cards x 2 languages, 1080x1350 | `cards-monthly-kn.html`, `cards-monthly-en.html` with `build_cards.py` |
| WhatsApp | **Two tall images**: summary, then details | `template-1-summary.html`, `template-2-details.html` with `build_images.py` |
| PDF on request | Render either HTML to A4 with normal margins | |

**WhatsApp gets two images, never six.** Sending a six-image carousel to a
WhatsApp channel or group is painful to read and painful to forward — people
see a wall of thumbnails and open none. The tall two-image version exists for
exactly this: image 1 is the forces box and the lead (roughly square, shows
without a tap), image 2 carries the five sections. Both carry the masthead, the
QR and the disclaimer so either one survives being forwarded alone.

When the user asks for "the post" without naming a channel, build the carousels
and the WhatsApp pair, and say which is which.

## The top box

Three labelled parts, never a fourth:

- **ಮೇಲಕ್ಕೆ ಎಳೀತಿರೋದು** — what pushes prices up, with the number attached
- **ಕೆಳಕ್ಕೆ ಎಳೀತಿರೋದು** — what pushes them down, with the number
- **ಮುಂದೆ ಗಮನಿಸಬೇಕಾದ್ದು** — the event that resolves the tension, and when

No recommendation: no hold, no sell, no "prices look likely to rise". A brief
circulated among growers saying "don't sell this month" is read as advice, and
whoever sent it owns the outcome when the market moves the other way. Give both
sides with their numbers and let the reader decide. If the user explicitly wants
a call, write it, but note once that the factors-only version is safer to
circulate.

The disclaimer strip at the foot of both images says this is a summary of the
report's figures, not a forecast or selling advice. Keep it on both.

## What goes in image 2

Five numbered sections, in this order:

1. **ಬೆಲೆ ಎಷ್ಟಿತ್ತು** — composite indicator and month-on-month change, the
   range, each group indicator (Colombian Milds / Other Milds / Brazilian
   Naturals / Robusta), New York and London futures, volatility.
2. **ಬೆಲೆ ಯಾಕೆ ಹಾಗೆ ಆಡ್ತು** — bullish drivers, bearish drivers, and what turned
   out neutral. The report names these; use its list rather than inventing one.
3. **ಸ್ಟಾಕ್ ಎಷ್ಟಿದೆ** — certified Arabica and Robusta stocks with the historical
   comparison.
4. **ಎಕ್ಸ್‌ಪೋರ್ಟ್** — global green bean exports and year to date, split by
   group, the Arabica share, exports by region.
5. **ಬೆಳೆ ಎಷ್ಟು, ಕುಡಿಯೋದು ಎಷ್ಟು** — production, consumption, surplus or deficit.

Figures stay in Latin digits (287.29, 10.76 ಮಿಲಿಯನ್ ಚೀಲ) — that is what growers
read on a price board.

Relevance is the filter. An Indian planter cares about Arabica and Robusta price
levels, stocks, and Brazil/Vietnam supply news because those set the price they
are quoted. Fine detail on, say, Nicaraguan seasonality compresses to a clause
or drops.

## Card format

- **1080x1350 (4:5).** Instagram caps uploads at 1080 wide and 1350 tall, so
  this is the largest feed post available. Every card in a carousel must be the
  same size — the first card locks the ratio for the rest.
- **Up to 20 cards per post.** The monthly brief runs about seven: cover, the
  forces box, prices, stocks, exports, production and consumption, and a closing
  card with the QR.
- **64px side padding is a safe zone, not decoration.** The Instagram profile
  grid crops 4:5 posts to the centre 1012px. Text or logos outside that get cut
  in the grid view.
- **Header and footer are identical on every card** so a single screenshotted
  card still carries the brand, the date and the contact line.
- **The contact slot** in the footer is filled in:
  `ವಿದ್ವಾನ್ ಗೌಡ · ಆಲ್ದೂರು, ಚಿಕ್ಕಮಗಳೂರು · 7975045560` / `Vidwan Gowda · Aldur, Chikmagalur · 7975045560`, with a
  rule-bounded block on the closing card carrying the same details. It comes
  from `scripts/make_cards.py`, so change it there and regenerate rather than
  editing the card HTML — see `references/cards.md`.

## Reuse for other commodities

The pipeline suits any monthly report aimed at Indian growers — pepper,
cardamom, arecanut, rubber. Section headings change; the spoken-Kannada rule,
the forces-not-verdict box, the two-image split and the QR sizing do not.
