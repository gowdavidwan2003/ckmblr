# Distribution

| Channel | Format | Notes |
|---|---|---|
| WhatsApp group | Daily: one tall image per language. Monthly: two tall images (summary, then details) per language. | Admin-only posting, so the group reads like a channel but forwards better. Never send the six-card carousel here. |
| Instagram | Carousel, 1080x1350. Daily ~3 cards, monthly ~6-7. | Kannada and English as two separate posts. Profile grid crops to the centre 1012px — keep everything inside the 64px safe zone. |
| Facebook | Same carousel as Instagram. | |

Kannada goes out first, English second. Cards upload in filename order.

## Contact line

- Name: Vidwan Gowda / ವಿದ್ವಾನ್ ಗೌಡ
- Town: Aldur, Chikmagalur / ಆಲ್ದೂರು, ಚಿಕ್ಕಮಗಳೂರು
- Phone: 7975045560

Live on every card since 20 September 2026, as one line in each card footer:

```
ವಿದ್ವಾನ್ ಗೌಡ · ಆಲ್ದೂರು, ಚಿಕ್ಕಮಗಳೂರು · 7975045560
Vidwan Gowda · Aldur, Chikmagalur · 7975045560
```

plus a rule-bounded block on the closing card with the phone on its own line,
and a line in the foot band of the tall WhatsApp images.

To change them, edit `KN_CONTACT` / `EN_CONTACT` / `KN_SLOT` / `EN_SLOT` in
either skill's `scripts/make_cards.py` and regenerate the four card decks:

```bash
cd .claude/skills
cp malenadu-dara-daily/assets/channel-qr.png qr.png
python3 malenadu-dara-daily/scripts/make_cards.py
rm qr.png
```

The four tall templates are not generated — edit those by hand. They carry the
Kannada line; swap it for the English one when the copy is English.

## QR

`assets/channel-qr.png` inside each skill points at the WhatsApp group. If the
group link ever changes, replace the QR in **both** skills — they carry separate
copies. The build script checks the QR still decodes after a simulated upload
recompress; if it reports a failure, enlarge it rather than shipping it.
