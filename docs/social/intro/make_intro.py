#!/usr/bin/env python3
"""Builds the pinned intro carousel (Kannada + English) for Instagram and Facebook.

Borrows the CSS, logo and QR from the generated daily deck so the intro
matches the cards exactly. Run from this folder, then build the PNGs:

    python make_intro.py
    python ../../../.claude/skills/malenadu-dara-daily/scripts/build_cards.py out/ intro-kn.html intro-en.html
"""
import re, pathlib

HERE = pathlib.Path(__file__).parent
DECK = (HERE / '../../../.claude/skills/malenadu-dara-daily/assets/cards-daily-kn.html').read_text(encoding='utf-8')
CSS = re.search(r'<style>(.*?)</style>', DECK, re.S).group(1)
LOGO = re.search(r'(<svg class="logo".*?</svg>)', DECK, re.S).group(1)
QR = re.search(r'<img src="(data:image/png;base64,[^"]+)"', DECK).group(1)

KN_CONTACT = 'ವಿದ್ವಾನ್ ಗೌಡ · ಆಲ್ದೂರು, ಚಿಕ್ಕಮಗಳೂರು · 7975045560'
EN_CONTACT = 'Vidwan Gowda · Aldur, Chikmagalur · 7975045560'
KN_SLOT = 'ವಿದ್ವಾನ್ ಗೌಡ · ಆಲ್ದೂರು, ಚಿಕ್ಕಮಗಳೂರು<br>ಫೋನ್ 7975045560<br>ಇನ್‌ಸ್ಟಾಗ್ರಾಮ್ · ಫೇಸ್‌ಬುಕ್ @malenadu.dara'
EN_SLOT = 'Vidwan Gowda · Aldur, Chikmagalur<br>Phone 7975045560<br>Instagram · Facebook @malenadu.dara'


def card(name, date, body, page, total, contact, dark):
    cls = 'card dark' if dark else 'card'
    return f'''<section class="{cls}">
  <div class="hdr">
    {LOGO}
    <div class="hname">{name}</div>
    <div class="hdate">{date}</div>
  </div>
  <div class="body">
{body}
  </div>
  <div class="ftr">
    <div class="ct">{contact}</div>
    <div class="pg">{page} / {total}</div>
  </div>
</section>'''


def qrcard(title, para, slot, disc):
    return f'''    <div class="cta">
      <img src="{QR}">
      <div class="ch">{title}</div>
      <div class="cp">{para}</div>
      <div class="slot">{slot}</div>
      <div class="disc">{disc}</div>
    </div>'''


kn = [
"""    <div class="covtag">ನಮ್ಮ ಪರಿಚಯ</div>
    <h1 class="cover">ಬೆಳೆಗಾರರಿಗೆ<br>ದಿನಾ ಕಾಫಿ<br>ದರ, ಸುದ್ದಿ</h1>
    <div class="covsub">ಕರ್ನಾಟಕದ ಕಾಫಿ ದರ, ಕಾಫಿ ಸುದ್ದಿ — ನಮ್ಮ ಮಾತಲ್ಲೇ, ಒಂದೇ ಕಡೆ. ಮೊದಲು ಕನ್ನಡದಲ್ಲಿ, ಆಮೇಲೆ English‌ನಲ್ಲಿ.</div>""",

"""    <h2>ಏನೇನು ಸಿಗುತ್ತೆ</h2>
    <div class="row"><div class="lbl">ದಿನಾ ದರ</div>
    <p>ಪ್ರತಿ ಕೆಲಸದ ದಿನ ಅರೇಬಿಕಾ, ರೊಬಸ್ಟಾ — ಪಾರ್ಚ್‌ಮೆಂಟ್, ಚೆರಿ ದರ. Coffee Board ರಿಪೋರ್ಟ್‌ನಿಂದ, ನ್ಯೂಯಾರ್ಕ್–ಲಂಡನ್ ಮಾರ್ಕೆಟ್ ಜೊತೆ.</p></div>
    <div class="row"><div class="lbl">ಕಾಫಿ ಸುದ್ದಿ</div>
    <p>ಬೆಲೆ ಮೇಲೆ ಕೆಲಸ ಮಾಡೋ ಸುದ್ದಿ. ಪ್ರತಿ ಸುದ್ದಿ ಕೆಳಗೆ ಅದು ಎಲ್ಲಿಂದ ಬಂತು ಅಂತ ಮೂಲ ಇರುತ್ತೆ.</p></div>
    <div class="row"><div class="lbl">ತಿಂಗಳ ವರದಿ</div>
    <p>ICO ರಿಪೋರ್ಟ್‌ನ ಸಾರಾಂಶ — ಜಗತ್ತಿನ ಬೆಲೆ, ಸ್ಟಾಕ್, ಎಕ್ಸ್‌ಪೋರ್ಟ್, ಬೆಳೆ.</p></div>""",

"""    <h2>ನಾವು ಹೇಳದೇ<br>ಇರೋದು</h2>
    <p>ಬೆಲೆ ಏರುತ್ತೆ, ಇಳಿಯುತ್ತೆ ಅಂತ ನಾವು ಹೇಳಲ್ಲ. ಮಾರಿ, ಇಟ್ಕೊಳ್ಳಿ ಅಂತನೂ ಹೇಳಲ್ಲ.</p>
    <p>ಬೆಲೆಯನ್ನ ಮೇಲಕ್ಕೆ ಎಳೀತಿರೋದು ಏನು, ಕೆಳಕ್ಕೆ ಎಳೀತಿರೋದು ಏನು — ಅಂಕಿಅಂಶ ಸಮೇತ ತೋರಿಸ್ತೀವಿ. <b>ತೀರ್ಮಾನ ನಿಮ್ದು.</b></p>
    <div class="note">ಭಾನುವಾರ, ರಜೆ ದಿನ Coffee Board ರಿಪೋರ್ಟ್ ಬರಲ್ಲ. ಆ ದಿನ ಕೊನೇ ದರನೇ ಹಾಕ್ತೀವಿ, ಅದನ್ನೂ ಕಾರ್ಡ್ ಮೇಲೆ ಬರೀತೀವಿ.</div>""",

qrcard('ದಿನಾ ದರ ಬೇಕಾ?',
       'ಮಲೆನಾಡು ದರ WhatsApp ಗ್ರೂಪ್‌ಗೆ ಸೇರಿ — ಪ್ರತಿ ದಿನ ಕರ್ನಾಟಕದ ದರ ನೇರವಾಗಿ ಸಿಗುತ್ತೆ.',
       KN_SLOT,
       'ಮಾಹಿತಿಗಾಗಿ ಮಾತ್ರ — ಮಾರಾಟದ ಸಲಹೆ ಅಲ್ಲ.'),
]

en = [
"""    <div class="covtag">About us</div>
    <h1 class="cover">Coffee rates<br>and news,<br>every day</h1>
    <div class="covsub">Karnataka coffee prices and coffee news for growers, in one place. Kannada first, then English.</div>""",

"""    <h2>What you get</h2>
    <div class="row"><div class="lbl">DAILY RATES</div>
    <p>Arabica and Robusta, parchment and cherry, every working day — from the Coffee Board report, with New York and London alongside.</p></div>
    <div class="row"><div class="lbl">COFFEE NEWS</div>
    <p>The news that moves prices. Every item carries its source line.</p></div>
    <div class="row"><div class="lbl">MONTHLY REPORT</div>
    <p>A summary of the ICO market report — world prices, stocks, exports and production.</p></div>""",

"""    <h2>What we<br>won't tell you</h2>
    <p>We don't say where prices are going. We don't say sell or hold.</p>
    <p>We show what is pushing prices up and what is pushing them down, with the numbers. <b>The decision is yours.</b></p>
    <div class="note">The Coffee Board doesn't publish on Sundays and holidays. On those days we carry the last published rates and say so on the card.</div>""",

qrcard('Want the daily rate?',
       'Join the Malenadu Dara WhatsApp group — Karnataka prices every working day, straight to your phone.',
       EN_SLOT,
       'Information only, not selling advice.'),
]

for name, bodies, hname, date, contact in [
    ('intro-kn.html', kn, 'ಮಲೆನಾಡು ದರ', 'ಪರಿಚಯ', KN_CONTACT),
    ('intro-en.html', en, 'Malenadu Dara', 'About', EN_CONTACT),
]:
    n = len(bodies)
    cards = [card(hname, date, b, i + 1, n, contact, dark=(i in (0, n - 1)))
             for i, b in enumerate(bodies)]
    html = ('<!DOCTYPE html>\n<html lang="kn">\n<head>\n<meta charset="utf-8">\n<style>'
            + CSS + '</style>\n</head>\n<body>\n' + '\n'.join(cards) + '\n</body>\n</html>\n')
    (HERE / name).write_text(html, encoding='utf-8', newline='\n')
    print(f'{name}  ({n} cards)')
