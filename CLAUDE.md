# ಮಲೆನಾಡು ದರ / Malenadu Dara

A coffee publication for growers in Karnataka. Two products:

- **Daily** — the day's Karnataka rates and coffee news → skill `malenadu-dara-daily`
- **Monthly** — a brief built from the ICO Coffee Market Report → skill `malenadu-dara`

Every edition ships in **two languages as two separate posts**: spoken Kannada
first, then English. They are not two halves of one post; each set has its own
cover and its own closing card.

Distribution: a WhatsApp group with admin-only posting, plus Instagram and
Facebook. Cards are 1080x1350 PNGs — images, never PDFs, unless asked.

## Non-negotiables

These four are where the work goes wrong when it goes wrong. They apply to
everything in this repo, daily and monthly alike.

1. **Spoken Kannada, not literary Kannada.** The default a model reaches for is
   newspaper Kannada and a grower will not read it. ಸ್ಟಾಕ್ not ದಾಸ್ತಾನು,
   ಎಕ್ಸ್‌ಪೋರ್ಟ್ not ರಫ್ತು. Read `references/kannada-style.md` inside the skill
   before writing any copy.
2. **Report, don't advise.** Lay out what pushes prices up and what pushes them
   down, with the numbers. Never "hold", never "sell", never "prices will rise".
   A card circulated among growers that says don't sell is read as advice, and
   whoever sent it owns the outcome. The disclaimer strip stays on every card.
3. **Attribute everything.** Each news item carries its source line. A rumour or
   a single trader's comment is written as one, not dropped in as fact.
4. **Look at the rendered PNG before presenting.** Kannada shaping failures come
   out as empty boxes and are completely silent in the PDF step. Confirm every
   card reports 1080x1350 and that the QR survives recompress.

## Dates and prices

- The Coffee Board publishes on working days only. On Sundays and holidays,
  carry the last published rates with the orange no-new-report notice, change
  the column heading to "last change", and date-stamp the futures line.
- Karnataka rates inside a report are dated the **previous** day. Price date
  goes on the price card, publication date in the header. Never collapse them.
- Day-on-day change needs **today's Coffee Board PDF and yesterday's**. With one
  report only, leave the change column as em-dashes and print the reason. Never
  infer a movement from a single report.

## Layout

```
sources/           raw inputs, one folder per date — Coffee Board PDFs, ICO reports
editions/          one folder per edition: YYYY-MM-DD (daily), YYYY-MM (monthly)
  today/           daily: the full post (rates + news + export)
  market/          daily: market close cards
  news/            daily: news-only cards
    work/          in each set: edited copies of the card HTML
    out/           in each set: the built PNGs that get posted
.claude/skills/    the two skills, each self-contained (assets, scripts, references)
docs/              distribution and contact details
```

Work on **copies** in `editions/<date>/<set>/work/`. Never edit the templates in
`.claude/skills/*/assets/` for a single edition — those are the masters.

## Build

```bash
cd editions/2026-09-20/today
python3 ../../../.claude/skills/malenadu-dara-daily/scripts/build_cards.py out/ work/today-kn.html work/today-en.html
```

`build_cards.py` → carousel cards (Instagram, Facebook).
`build_images.py` → the tall single image (WhatsApp).

First run on a new machine: `bash scripts/setup.sh`, then
`python3 scripts/check_setup.py` any time the build misbehaves — it prints
which engines it found.

The build needs one engine for HTML->PDF and one for PDF->PNG. On macOS and
Linux that is WeasyPrint and `pdftoppm` (poppler). On Windows neither installs
without a GTK runtime and a poppler build, so it falls back to headless Chrome
or Edge and to Ghostscript. Same templates, same cards; `build_cards.py` prints
the pair it used on every run.

## Contact slot

Filled in and live on every card: `ವಿದ್ವಾನ್ ಗೌಡ · ಆಲ್ದೂರು, ಚಿಕ್ಕಮಗಳೂರು · 7975045560` /
`Vidwan Gowda · Aldur, Chikmagalur · 7975045560`. One line per card footer, a rule-bounded
block on the closing card, and a line in the foot band of the tall WhatsApp
images. Details of record: `docs/distribution.md`.

The four card decks are **generated** — change the contact in either skill's
`scripts/make_cards.py` (`KN_CONTACT` / `EN_CONTACT` for the footer line,
`KN_SLOT` / `EN_SLOT` for the closing block) and regenerate, because the next
run overwrites hand-edits to `assets/cards-*.html`:

```bash
cd .claude/skills
cp malenadu-dara-daily/assets/channel-qr.png qr.png
python3 malenadu-dara-daily/scripts/make_cards.py
rm qr.png
```

The four tall templates are hand-edited and carry the Kannada line; swap it for
the English one when the copy is English.
