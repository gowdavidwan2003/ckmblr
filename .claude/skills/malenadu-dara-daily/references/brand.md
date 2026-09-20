# Malenadu Dara — brand and layout

## Palette

| Use | Hex |
|---|---|
| Masthead / footer band, section headings | `#0F6E56` |
| Disclaimer strip (darker band) | `#0B5744` |
| Light text on green | `#E1F5EE` |
| Secondary text on green | `#9FE1CB` |
| Forces-box border / accent | `#C97B2E`, heading `#8F4A12` |
| Forces-box fill | `#FDF6EF` |
| Lead-paragraph fill | `#EEF5F2` |
| Cherry on the logo | `#BA7517` |
| Body text | `#1c1c1c` |

## Logo

A ridgeline that doubles as a price line, ochre cherry on the peak, set in a
pale mint disc so the green stroke reads against the green band. It is inline
SVG in the template — vector, so it stays sharp at any size and can be lifted
out for a channel avatar.

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

Note the ridgeline rises left to right. On a price newsletter some readers take
that as a bullish signal rather than scenery. It was accepted knowingly; if that
ever becomes a problem, mirror the path or flatten the last segment.

## Page structure

Both images share the same skeleton:

1. **Masthead band** — logo, ಮಲೆನಾಡು ದರ, the subtitle, and a date chip (daily)
   or a `1 / 2` page pill (monthly) on the right.
2. **Content** — fixed five sections in the monthly brief; free-form blocks in
   the daily card.
3. **Footer band** — name and date on the left, QR card on the right.
4. **Disclaimer strip** — darker green, source line and the not-selling-advice
   line.

Every card carries the masthead, footer and disclaimer. Images get separated in
forwarding, and a loose page of price figures with no date, no source and no
disclaimer is the version you do not want circulating. The date appears in both
the masthead and the footer for the same reason.

## Page sizing

Render on a deliberately over-tall page (`@page { size: 210mm 400mm }`) with
`margin: 0`, then let the build script trim the blank tail.
That keeps everything on one canvas with no page break. If a footer band goes
missing from the output, the page was too short and it spilled onto page two —
increase the height.

## QR code: size is load-bearing

`assets/channel-qr.png` is the WhatsApp channel code, cropped to the code plus a
small quiet zone. It sits on a white card, because a QR directly on the green
band loses its quiet zone.

**Render it at 38mm.** This was established by testing, not taste. At 21mm the
code decoded perfectly from the original PNG and then failed once downscaled and
recompressed the way WhatsApp does it — which is the only path a reader ever
sees it through. 30mm was still unreliable. 38mm decodes at 800px, 1000px and
1280px wide at JPEG quality 55.

`scripts/build_images.py` re-runs that check on every build. If it prints a QR
failure, enlarge the code; do not ship it because it looks fine on screen.

## Open naming question

The newsletter masthead says **ಮಲೆನಾಡು ದರ**; the WhatsApp channel is
**ಮಲೆನಾಡು ದರ**. Two names for one thing costs recognition, which is what
a masthead is for. Unresolved — if it has since been settled, update both the
templates and this note.
