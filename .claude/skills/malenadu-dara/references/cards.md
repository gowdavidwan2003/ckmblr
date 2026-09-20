# Social card format

## Size

**1080 x 1350 px (4:5).** Instagram caps uploads at 1080 wide and 1350 tall, so
4:5 is the tallest feed post available — square wastes about 20% of the screen.
Facebook and WhatsApp both handle 4:5 fine, so one size covers all three.

Every card in a carousel must be the same size. Instagram locks the whole
carousel to the first card's ratio and crops the rest to match.

Up to 20 cards per post. In practice: three for a daily post, about seven for
the monthly brief. Nobody swipes twenty.

## Safe zone

Side padding is **64px and is not decoration**. The Instagram profile grid
previews 4:5 posts cropped to the centre 1012px, trimming 34px from each side.
Anything closer to the edge than that — text, the logo, the page number — gets
cut in grid view even though it looks fine in the feed.

## Fixed chrome

Deliberately slim, so the content fills the card rather than the frame:

- **Header**: small ridgeline logo, the wordmark in green, date in grey on the
  right. No coloured band — a heavy band on every card eats about 15% of the
  height and leaves the content looking stranded.
- **Footer**: the contact slot on the left, card number on the right, both in
  quiet grey. No band.

They repeat on every card because single cards get screenshotted and forwarded
out of the carousel. A loose card still has to say who made it, when, and how to
reach you.

## Green bookends, white interior

The cover and the closing card are solid `#0F6E56` with white type. Everything
between them is white with green headings. The green cards carry the brand in
the feed; the white ones carry the information. Making every card green looks
loud and makes tables harder to read.

## Filling the card

Type is large on purpose: headings 56px, body 34px, table values 36px, the
standout figure 124px. At smaller sizes the content floats in the middle of a
1350px card and looks unfinished. If a card looks empty, **merge it with the
next one or raise the type size** — do not add decoration to fill space.

Boxes and tinted panels were removed in favour of hairline rules (`.row`,
table borders). Fewer filled shapes, larger type, same information.

## The contact slot — live

Name, town and phone number are filled in and appear on every card:

```
ವಿದ್ವಾನ್ ಗೌಡ · ಆಲ್ದೂರು, ಚಿಕ್ಕಮಗಳೂರು · 7975045560
Vidwan Gowda · Aldur, Chikmagalur · 7975045560
```

One line in each card footer, and a rule-bounded block on the closing card with
the phone on its own line.

**The card decks are generated.** The contact lives in `KN_CONTACT` /
`EN_CONTACT` (the footer line) and `KN_SLOT` / `EN_SLOT` (the closing block) in
`scripts/make_cards.py`. Change it there and regenerate — the next run
overwrites hand-edits to `assets/cards-*.html`:

```bash
cd .claude/skills
cp malenadu-dara-daily/assets/channel-qr.png qr.png
python3 malenadu-dara-daily/scripts/make_cards.py
rm qr.png
```

The four tall WhatsApp templates are **not** generated, so they are edited by
hand. They carry the Kannada line in the foot band; swap it for the English one
when the copy is English.

Details of record are in `docs/distribution.md`.

## The QR

The closing card carries the WhatsApp channel QR at 300px. That size was chosen
by testing, not taste: the code has to survive the platform re-encoding the
image. `build_cards.py` re-runs that check on every build and prints a warning
if a card's QR stops decoding — if it does, enlarge it rather than shipping it
because it looks fine on screen.

Only the closing card carries the QR. Repeating it on every card wastes the
space and trains people to swipe past it.

## Two languages, two posts

Kannada and English are **separate posts**, not alternating cards in one
carousel. Each set gets its own cover and its own closing card. Mixing them
halves the useful length of the post for every reader.

## Typography note

Kannada needs more line-height than Latin script — vowel marks sit above and
below the base line, and at headline sizes they collide at the line-heights that
look fine in English. Headings use 1.45, body 1.6. If a Kannada heading looks
cramped, raise the line-height; don't reduce the font size.

## Palette

| Use | Hex |
|---|---|
| Header band, headings | `#0F6E56` |
| Footer band | `#0B5744` |
| Light text on green | `#E1F5EE` |
| Secondary text on green | `#9FE1CB` |
| Accent box border / heading | `#C97B2E` / `#8F4A12` |
| Accent box fill | `#FDF6EF` |
| Quiet panel fill | `#EEF5F2` |
| Logo cherry | `#BA7517` |
| Rise / fall markers | `#0F6E56` / `#B4231F` |

## Logo

```svg
<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <circle cx="32" cy="32" r="32" fill="#E1F5EE"/>
  <g transform="translate(32,32) scale(0.84) translate(-32,-32)">
    <path d="M6 46 L20 30 L30 38 L46 16 L58 26" fill="none" stroke="#0F6E56"
          stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="46" cy="16" r="6" fill="#BA7517"/>
  </g>
</svg>
```

The ridgeline rises left to right, so it reads as a rising price line as well as
a hill. Accepted knowingly; mirror the path if that ever becomes a problem.

## Open naming question

The masthead says **ಮಲೆನಾಡು ದರ**; the WhatsApp channel is **ಮಲೆನಾಡು ದರ**.
Two names for one thing costs recognition. Unresolved — if it has since been
settled, update both templates and this note.
