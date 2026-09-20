---
name: "malenadu-dara-daily"
description: Produce the Malenadu Dara daily coffee post — branded 1080x1350 cards carrying the day's Karnataka rates and coffee news, in spoken Kannada and English, for Instagram, Facebook and WhatsApp. Use when the user asks for the daily news card, today's coffee news, ದಿನದ ಸುದ್ದಿ, a Kannada coffee news post, or hands over articles or links about coffee to turn into a post. For the monthly ICO market report summary use the malenadu-dara skill instead; this one is for daily, unstructured news.
---

# Malenadu Dara — daily coffee post

Default output is **two short carousels of 1080x1350 cards — one Kannada, one
English** — usually three cards each: rates, news, and a closing card with the
QR. Produce both languages unless the user says otherwise; they are separate
posts, not two halves of one.

Fixed brand chrome, free-form content. The whole design
problem here is that daily news has no fixed shape: some days there is one
story worth 200 words, some days six one-liners, some days a single number.
The template solves that by fixing only the frame.

## Fixed vs flexible

**Fixed — never restyle, reorder or drop:**

- Masthead band: ridgeline logo, ಮಲೆನಾಡು ದರ, the ದಿನದ ಕಾಫಿ ಸುದ್ದಿ subtitle, and
  the date chip on the right
- Footer band: name, date repeated, QR card
- Disclaimer strip below the footer

The date appears twice on purpose — top and bottom — because people crop and
forward, and an undated news card is worthless a week later. Always set both to
the actual date of publication, written in Kannada (19 ಸೆಪ್ಟೆಂಬರ್ 2026).

**Flexible — everything inside `.wrap`.** Use whichever blocks fit the day and
delete the rest. Do not force the news into a fixed section scheme; there isn't
one, and pretending there is produces padded filler on quiet days.

| Block | Use it for |
|---|---|
| `.lead` | One sentence framing the day, when there's a through-line. Skip it when the items are unrelated. |
| `.big` | One standout number or fact. At most one per card, or it stops standing out. |
| `.item` | A story: `.ihead` headline, a paragraph or two, `.imeta` source line. |
| `.quick` | Small items that don't need a paragraph, as a short bulleted list. |
| `.more` | A closing pointer line, if any. |

Any order, any number. A card can be one `.big` and nothing else. A card can be
five `.item`s. Three to six items is the comfortable range for one screen.

## Sourcing

The news has to come from somewhere. Search the web for the day's coffee news
unless the user supplies the material — trade press, exchange notices,
producer-country reports, weather in Brazil and Vietnam, Indian Coffee Board
announcements. Prefer primary sources over aggregators.

**Every `.item` carries a `.imeta` source line**, and the disclaimer strip says
sources are given per item. Do not put a claim on the card that you cannot
attribute. If something is a rumour or a single trader's comment, say so in the
sentence rather than dropping it in as fact.

Relevance filter: does it plausibly affect what a Karnataka grower is paid, or
what they do on the estate? Brazil weather, Vietnam shipments, exchange stocks,
Indian export policy, rain in Kodagu — yes. A new café chain opening in Seoul —
no.

## Rules carried over from the monthly brief

1. **Spoken Kannada, not literary.** Read `references/kannada-style.md` before
   writing. ಸ್ಟಾಕ್ not ದಾಸ್ತಾನು, ಎಕ್ಸ್‌ಪೋರ್ಟ್ not ರಫ್ತು.
2. **Report, don't advise.** State what happened and what it bears on. No
   "hold", no "sell", no "prices will rise". A daily card is read fast and
   forwarded far, which makes a stray recommendation more dangerous here than
   in the monthly brief, not less.
3. **Look at the rendered PNG before sending.** Kannada shaping failures are
   silent.

## Prices need two reports, not one

The rate card shows day-on-day change, so it needs **today's Coffee Board PDF
and yesterday's**. With only one, leave the change column as em-dashes and print
a line saying why. Never infer a movement from a single report — a made-up arrow
is the one error on this card a grower would act on.

Sources, in order: the Coffee Board daily PDF (authoritative, carries futures
and the export table); `kirehalli.com/coffee-prices-karnataka-DD-MM-YYYY/` as a
fetchable fallback (prices and analysis only); browser automation last. The
Board's own site often returns 500 errors — that is their server, not your setup.

Note also that the Karnataka rates in a given report are dated the **previous**
day. Put the price date on the price card and the publication date in the
header; collapsing them is the easiest way to mislead someone.

## No report on Sundays and holidays

The Board publishes on working days only. On a blank day, carry the last
published rates with an orange notice above the table saying there is no new
report, change the column heading to "last change", and date-stamp the futures
line. The news blocks still work — other sources publish daily.

## Build

```bash
cp assets/cards-daily-kn.html work/today-kn.html   # then edit the copies
cp assets/cards-daily-en.html work/today-en.html
python3 scripts/build_cards.py out/ work/today-kn.html work/today-en.html
```

Every card must come back 1080x1350, and the closing card must report the QR
surviving recompress. Then view each card and present them in filename order.

The WhatsApp templates pull in `channel-qr.png` by relative path, so copy it
into `work/` beside them or the tall image builds with a hole where the QR
should be:

```bash
cp assets/template-daily-price.html work/whatsapp-kn.html
cp assets/channel-qr.png work/
python3 scripts/build_images.py out/ work/whatsapp-kn.html
```

## Output per channel

| Channel | Output | Templates |
|---|---|---|
| Instagram, Facebook | Carousel: 3 cards x 2 languages, 1080x1350 | `cards-daily-kn.html`, `cards-daily-en.html` with `build_cards.py` |
| WhatsApp | **One tall image** per language | `template-daily-price.html` (rates + news) with `build_images.py` |

**WhatsApp gets a single image.** A daily post is short enough to fit one tall
card, and one image is far easier to forward than three. Use
`template-daily.html` instead when the day is news-only with no new rates.

When the user asks for "the post" without naming a channel, build both the
carousels and the WhatsApp image, and say which is which.

## Card format

- **1080x1350 (4:5)** — the largest Instagram feed post available; all cards in
  a carousel must match, since the first locks the ratio.
- **64px side padding is a safe zone** — the profile grid crops to the centre
  1012px, so anything outside gets cut there.
- **Header and footer repeat on every card**, so a screenshotted single card
  still carries the brand, the date and the contact line.
- **The contact slot** is filled in: `ವಿದ್ವಾನ್ ಗೌಡ · ಆಲ್ದೂರು, ಚಿಕ್ಕಮಗಳೂರು · 7975045560`
  / `Vidwan Gowda · Aldur, Chikmagalur · 7975045560`, on every card footer and as a block
  on the closing card. It comes from `scripts/make_cards.py`, so change it
  there and regenerate rather than editing the card HTML — see
  `references/cards.md`.
