#!/usr/bin/env python3
"""Generates the four card templates (monthly/daily x Kannada/English).

Run it from `.claude/skills/`, with a copy of the channel QR named qr.png
beside it - the output paths are relative to that folder:

    cd .claude/skills
    cp malenadu-dara-daily/assets/channel-qr.png qr.png
    python3 malenadu-dara-daily/scripts/make_cards.py
    rm qr.png

Kept as a generator so the shared CSS lives in exactly one place. Editing the
generated HTML by hand works too, but the next run of this script overwrites it.
"""
import os, base64

QR = base64.b64encode(open('qr.png','rb').read()).decode()

LOGO = '''<svg class="logo" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <circle cx="32" cy="32" r="32" fill="#E1F5EE"/>
  <g transform="translate(32,32) scale(0.84) translate(-32,-32)">
    <path d="M6 46 L20 30 L30 38 L46 16 L58 26" fill="none" stroke="#0F6E56" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="46" cy="16" r="6" fill="#BA7517"/>
  </g></svg>'''

CSS = '''
@page { size: 1080px 1350px; margin: 0; }
* { box-sizing: border-box; }
body { font-family:'NotoKan', sans-serif; margin:0; color:#141414; }

.card { width:1080px; height:1350px; page-break-after:always;
        display:flex; flex-direction:column; background:#FFFFFF; overflow:hidden; }
.card:last-child { page-break-after:auto; }
.card.dark { background:#0F6E56; color:#FFFFFF; }

/* ---- HEADER: slim, same on every card ---- */
.hdr { padding:44px 72px 0 72px; display:flex; align-items:center; gap:18px; flex-shrink:0; }
.logo { width:56px; height:56px; flex-shrink:0; }
.hname { font-size:27px; font-weight:700; color:#0F6E56; letter-spacing:0.3px; }
.hdate { margin-left:auto; font-size:24px; color:#8A8A8A; white-space:nowrap; }
.dark .hname { color:#FFFFFF; }
.dark .hdate { color:#9FE1CB; }

/* ---- BODY ---- */
.body { flex:1; padding:56px 72px 40px 72px; display:flex; flex-direction:column;
        justify-content:center; overflow:hidden; }

/* ---- FOOTER: hairline + one quiet line ---- */
.ftr { padding:0 72px 44px 72px; display:flex; justify-content:space-between;
       align-items:flex-end; flex-shrink:0; font-size:22px; color:#9A9A9A; }
.ftr .ct { line-height:1.45; }
.dark .ftr { color:#79C4AC; }

/* ---- type ---- */
h1.cover { font-size:96px; line-height:1.38; margin:0 0 40px 0; font-weight:700; color:#FFFFFF; }
.covsub { font-size:38px; line-height:1.6; color:#C9EDE0; }
.covtag { align-self:flex-start; font-size:26px; color:#9FE1CB; letter-spacing:2px;
          text-transform:uppercase; margin-bottom:34px; }
h2 { font-size:56px; color:#0F6E56; margin:0 0 44px 0; line-height:1.4; font-weight:700; }
p  { font-size:34px; line-height:1.62; margin:0 0 30px 0; }
p:last-child { margin-bottom:0; }
b { font-weight:700; }
.muted { color:#6E6E6E; }

/* stacked label/value rows — replaces boxes */
.row { padding:26px 0; border-top:2px solid #E8E8E8; }
.row:last-of-type { border-bottom:2px solid #E8E8E8; }
.row .lbl { font-size:25px; color:#0F6E56; font-weight:700; letter-spacing:0.6px; margin-bottom:10px; }
.row p { font-size:33px; margin:0; line-height:1.55; }

.bignum { font-size:124px; font-weight:700; color:#0F6E56; line-height:1.25; margin:0 0 8px 0; }
.bigcap { font-size:31px; color:#6E6E6E; margin-bottom:40px; }

table { width:100%; border-collapse:collapse; }
th { font-size:23px; color:#8A8A8A; font-weight:400; text-align:left;
     padding:0 0 16px 0; border-bottom:2px solid #E8E8E8; letter-spacing:0.6px; }
th.r, td.r { text-align:right; }
td { font-size:36px; padding:26px 0; border-bottom:2px solid #F0F0F0; }
td.g { font-weight:700; }
td.v { font-weight:700; white-space:nowrap; }
td.d { font-size:30px; }
.dn { color:#B4231F; font-weight:700; }
.up { color:#0F6E56; font-weight:700; }
.flat { color:#A0A0A0; }
.note { font-size:28px; color:#6E6E6E; line-height:1.55; margin-top:34px; }

.item { margin-bottom:46px; }
.item:last-child { margin-bottom:0; }
.item .ih { font-size:42px; font-weight:700; color:#0F6E56; margin-bottom:16px; line-height:1.4; }
.item p { font-size:31px; margin:0 0 10px 0; }
.item .src { font-size:23px; color:#9A9A9A; }

/* closing card */
.cta { text-align:center; }
.cta img { width:330px; height:330px; display:block; margin:0 auto 36px auto;
           background:#FFFFFF; padding:18px; border-radius:10px; }
.cta .ch { font-size:56px; font-weight:700; margin-bottom:20px; line-height:1.4; color:#FFFFFF; }
.cta .cp { font-size:32px; color:#C9EDE0; line-height:1.55; margin-bottom:40px; }
.cta .slot { font-size:30px; color:#FFFFFF; line-height:1.7; padding:28px 0;
             border-top:2px solid #3E8E76; border-bottom:2px solid #3E8E76; }
.disc { font-size:23px; color:#79C4AC; line-height:1.55; margin-top:36px; }
'''

def card(hdr_sub, date, body, page, total, contact, dark=False):
    cls = "card dark" if dark else "card"
    return f'''<section class="{cls}">
  <div class="hdr">
    {LOGO}
    <div class="hname">{hdr_sub[0]}</div>
    <div class="hdate">{date}</div>
  </div>
  <div class="body">
{body}
  </div>
  <div class="ftr">
    <!-- CONTACT SLOT: KN_CONTACT / EN_CONTACT in make_cards.py, on every card -->
    <div class="ct">{contact}</div>
    <div class="pg">{page} / {total}</div>
  </div>
</section>'''


def doc(cards):
    return ('<!DOCTYPE html>\n<html lang="kn">\n<head>\n<meta charset="utf-8">\n<style>'
            + CSS + '</style>\n</head>\n<body>\n' + '\n'.join(cards) + '\n</body>\n</html>\n')

# ---------------------------------------------------------------- content
KN_CONTACT = 'ವಿದ್ವಾನ್ ಗೌಡ · ಆಲ್ದೂರು, ಚಿಕ್ಕಮಗಳೂರು · 7975045560'
EN_CONTACT = 'Vidwan Gowda · Aldur, Chikmagalur · 7975045560'
KN_SLOT = 'ವಿದ್ವಾನ್ ಗೌಡ · ಆಲ್ದೂರು, ಚಿಕ್ಕಮಗಳೂರು<br>ಫೋನ್ 7975045560'
EN_SLOT = 'Vidwan Gowda · Aldur, Chikmagalur<br>Phone 7975045560'

def qrcard(title, para, slot, disc):
    # CONTACT SLOT: the slot string (name / town / phone) shows as a
    # rule-bounded block on the closing card. Pass '' to leave it off.
    block = f'<div class="slot">{slot}</div>\n      ' if slot else ''
    return f'''    <div class="cta">
      <img src="data:image/png;base64,{QR}">
      <div class="ch">{title}</div>
      <div class="cp">{para}</div>
      {block}<div class="disc">{disc}</div>
    </div>'''


# ============ MONTHLY — KANNADA ============
mk = [
"""    <div class="covtag">ತಿಂಗಳ ವರದಿ</div>
    <h1 class="cover">ಆಗಸ್ಟ್‌ನಲ್ಲಿ<br>ಕಾಫಿ ಬೆಲೆ<br>ಏನಾಯ್ತು?</h1>
    <div class="covsub">ಎಲ್ ನಿನೊ ಭಯದಲ್ಲಿ ತಿಂಗಳ ಮಧ್ಯದಲ್ಲಿ ಬೆಲೆ ಏರಿತು, ಕೊನೇ ವಾರದಲ್ಲಿ ಮತ್ತೆ ಇಳೀತು. ಆಗಸ್ಟ್ ಸರಾಸರಿ ಬೆಲೆ ಜುಲೈ ತರಾನೇ ಉಳೀತು.</div>""",

"""    <h2>ಬೆಲೆ ಮೇಲೆ ಕೆಲಸ<br>ಮಾಡಿದ ಎರಡು ಶಕ್ತಿ</h2>
    <div class="row"><div class="lbl">ಮೇಲಕ್ಕೆ ಎಳೀತಿರೋದು</div>
    <p>ನ್ಯೂಯಾರ್ಕ್‌ನ ಅರೇಬಿಕಾ ಸ್ಟಾಕ್ 1999ರ ಮೇಲೆ ಇಷ್ಟು ಕಮ್ಮಿ ಆಗಿರಲಿಲ್ಲ. ಪ್ರಬಲ ಎಲ್ ನಿನೊ ಬರೋ ಚಾನ್ಸ್ 90%ಕ್ಕಿಂತ ಜಾಸ್ತಿ.</p></div>
    <div class="row"><div class="lbl">ಕೆಳಕ್ಕೆ ಎಳೀತಿರೋದು</div>
    <p>ಮುಂದಿನ ವರ್ಷ 9–10 ಮಿಲಿಯನ್ ಚೀಲ ಕಾಫಿ ಹೆಚ್ಚಿಗೆ ಉಳಿಯುತ್ತೆ ಅನ್ನೋ ಅಂದಾಜು, ಜೊತೆಗೆ ಬ್ರೆಜಿಲ್‌ನ ದಾಖಲೆ ಫಸಲು.</p></div>
    <div class="row"><div class="lbl">ಮುಂದೆ ಗಮನಿಸಬೇಕಾದ್ದು</div>
    <p>ಸೆಪ್ಟೆಂಬರ್–ಅಕ್ಟೋಬರ್‌ನಲ್ಲಿ ಬ್ರೆಜಿಲ್‌ನಲ್ಲಿ ಹೂ ಹೇಗೆ ಬಿಡುತ್ತೆ ಅನ್ನೋದು.</p></div>""",

"""    <h2>ಬೆಲೆ ಎಷ್ಟಿತ್ತು</h2>
    <table>
      <tr><th>ವಿಭಾಗ</th><th class="r">ಸೆಂಟ್/ಪೌಂಡ್</th><th class="r">ಬದಲಾವಣೆ</th></tr>
      <tr><td class="g">ICO ಸರಾಸರಿ</td><td class="r v">287.29</td><td class="r d flat">0.0%</td></tr>
      <tr><td class="g">ಕೊಲಂಬಿಯನ್ ಮೈಲ್ಡ್ಸ್</td><td class="r v">387.46</td><td class="r d up">▲ 1.1%</td></tr>
      <tr><td class="g">ಅದರ್ ಮೈಲ್ಡ್ಸ್</td><td class="r v">361.31</td><td class="r d up">▲ 0.7%</td></tr>
      <tr><td class="g">ಬ್ರೆಜಿಲ್ ನ್ಯಾಚುರಲ್ಸ್</td><td class="r v">322.24</td><td class="r d up">▲ 0.5%</td></tr>
      <tr><td class="g">ರೊಬಸ್ಟಾ</td><td class="r v">180.63</td><td class="r d dn">▼ 2.2%</td></tr>
    </table>
    <div class="note">ಫ್ಯೂಚರ್ಸ್: ನ್ಯೂಯಾರ್ಕ್ ಅರೇಬಿಕಾ ▲0.9% · ಲಂಡನ್ ರೊಬಸ್ಟಾ ▼3.0%. ಬೆಲೆ ಅಲುಗಾಡಿದ್ದು 13.7% — ಜುಲೈಗಿಂತ ಕಮ್ಮಿ.</div>""",

"""    <h2>ಸ್ಟಾಕ್ ಎಷ್ಟಿದೆ</h2>
    <div class="bignum">2,23,976</div>
    <div class="bigcap">ಚೀಲ — ನ್ಯೂಯಾರ್ಕ್‌ನ ಸರ್ಟಿಫೈಡ್ ಅರೇಬಿಕಾ ಸ್ಟಾಕ್</div>
    <p><b>1999ರ ಮೇಲೆ ಇಷ್ಟು ಕಮ್ಮಿ ಆಗಿರಲಿಲ್ಲ.</b> ಕಳೆದ ವರ್ಷಕ್ಕಿಂತ ಸುಮಾರು 68% ಕಮ್ಮಿ. ಲಂಡನ್‌ನ ರೊಬಸ್ಟಾ ಸ್ಟಾಕ್ ಮಾತ್ರ 19.5% ಏರಿದೆ.</p>
    <div class="note">ಅಂದ್ರೆ: ಈಗ ಕೈಯಲ್ಲಿರೋ ಅರೇಬಿಕಾ ಕಮ್ಮಿ, ಆದ್ರೆ ಮುಂದೆ ಬರೋ ಬೆಳೆ ಜಾಸ್ತಿ. ಈ ಎಳೆದಾಟವೇ ಈಗಿನ ಬೆಲೆ.</div>""",

"""    <h2>ಎಕ್ಸ್‌ಪೋರ್ಟ್<br>ಮತ್ತು ಬೆಳೆ</h2>
    <table>
      <tr><th>ಜುಲೈ 2026</th><th class="r">ಮಿಲಿಯನ್ ಚೀಲ</th></tr>
      <tr><td class="g">ಹಸಿ ಕಾಳು ಎಕ್ಸ್‌ಪೋರ್ಟ್</td><td class="r v">10.76 <span class="up">▲6.3%</span></td></tr>
      <tr><td class="g">ರೊಬಸ್ಟಾ</td><td class="r v">4.98 <span class="up">▲32%</span></td></tr>
      <tr><td class="g">ಅರೇಬಿಕಾ</td><td class="r v">5.78 <span class="dn">▼8.9%</span></td></tr>
      <tr><td class="g">2025/26 ಒಟ್ಟು ಬೆಳೆ</td><td class="r v">183.6 <span class="up">▲4.4%</span></td></tr>
      <tr><td class="g">ಜನ ಕುಡಿಯೋ ಕಾಫಿ</td><td class="r v">180.6 <span class="dn">▼0.8%</span></td></tr>
    </table>
    <div class="note">ನಾಲ್ಕು ವರ್ಷ ಕಾಫಿ ಕಮ್ಮಿ ಬಿದ್ದ ಮೇಲೆ, ಈ ವರ್ಷ ಮೊದಲ ಸಲ 3.0 ಮಿಲಿಯನ್ ಚೀಲ ಹೆಚ್ಚಿಗೆ ಉಳಿಯುತ್ತೆ ಅಂತ ಅಂದಾಜು.</div>""",

qrcard('ದಿನಾ ದರ ಬೇಕಾ?',
       'ಮಲೆನಾಡು ದರ WhatsApp ಚಾನೆಲ್‌ಗೆ ಸೇರಿ — ದಿನದ ದರ ಮತ್ತು ತಿಂಗಳ ವರದಿ ನೇರವಾಗಿ ಸಿಗುತ್ತೆ.',
       KN_SLOT,
       'ICO ರಿಪೋರ್ಟ್‌ನ ಅಂಕಿಅಂಶಗಳ ಸಾರಾಂಶ ಮಾತ್ರ. ಮುನ್ಸೂಚನೆ ಅಥವಾ ಮಾರಾಟದ ಸಲಹೆ ಅಲ್ಲ.'),
]

# ============ MONTHLY — ENGLISH ============
me = [
"""    <div class="covtag">Monthly report</div>
    <h1 class="cover">What moved<br>coffee prices<br>in August</h1>
    <div class="covsub">El Niño fears lifted prices mid-month, then rain in Brazil pulled them back. August ended almost exactly where July did.</div>""",

"""    <h2>Two forces working<br>on the price</h2>
    <div class="row"><div class="lbl">PUSHING UP</div>
    <p>Certified Arabica stocks in New York are at their lowest since 1999, and NOAA puts the chance of a very strong El Niño above 90%.</p></div>
    <div class="row"><div class="lbl">PUSHING DOWN</div>
    <p>Forecasts of a 9–10 million bag surplus next year, and a record Brazilian crop coming to market.</p></div>
    <div class="row"><div class="lbl">WHAT TO WATCH</div>
    <p>Flowering in Brazil through September and October.</p></div>""",

"""    <h2>Where prices stood</h2>
    <table>
      <tr><th>Indicator</th><th class="r">US cents/lb</th><th class="r">Change</th></tr>
      <tr><td class="g">ICO composite</td><td class="r v">287.29</td><td class="r d flat">0.0%</td></tr>
      <tr><td class="g">Colombian Milds</td><td class="r v">387.46</td><td class="r d up">▲ 1.1%</td></tr>
      <tr><td class="g">Other Milds</td><td class="r v">361.31</td><td class="r d up">▲ 0.7%</td></tr>
      <tr><td class="g">Brazilian Naturals</td><td class="r v">322.24</td><td class="r d up">▲ 0.5%</td></tr>
      <tr><td class="g">Robustas</td><td class="r v">180.63</td><td class="r d dn">▼ 2.2%</td></tr>
    </table>
    <div class="note">Futures: New York Arabica ▲0.9% · London Robusta ▼3.0%. Volatility 13.7%, down from July.</div>""",

"""    <h2>Stocks</h2>
    <div class="bignum">223,976</div>
    <div class="bigcap">bags of certified Arabica in New York</div>
    <p><b>The lowest level since 1999</b> — roughly 68% below a year earlier. London Robusta stocks went the other way, up 19.5%.</p>
    <div class="note">Arabica in hand is scarce, but the crop coming is large. That tension is the price.</div>""",

"""    <h2>Exports<br>and production</h2>
    <table>
      <tr><th>July 2026</th><th class="r">Million bags</th></tr>
      <tr><td class="g">Green bean exports</td><td class="r v">10.76 <span class="up">▲6.3%</span></td></tr>
      <tr><td class="g">Robusta</td><td class="r v">4.98 <span class="up">▲32%</span></td></tr>
      <tr><td class="g">Arabica</td><td class="r v">5.78 <span class="dn">▼8.9%</span></td></tr>
      <tr><td class="g">2025/26 production</td><td class="r v">183.6 <span class="up">▲4.4%</span></td></tr>
      <tr><td class="g">Consumption</td><td class="r v">180.6 <span class="dn">▼0.8%</span></td></tr>
    </table>
    <div class="note">After four straight deficit years, the market is expected to run a 3.0 million bag surplus this year.</div>""",

qrcard('Want the daily rate?',
       'Join the Malenadu Dara WhatsApp channel — daily Karnataka prices and the monthly report, straight to your phone.',
       EN_SLOT,
       'A summary of figures published by the ICO. Not a forecast and not selling advice.'),
]

# ============ DAILY — KANNADA ============
dk = [
"""    <h2>ಕರ್ನಾಟಕದ ದರ</h2>
    <table>
      <tr><th>₹ / 50 ಕೆಜಿ ಚೀಲ · 17.09.2026</th><th class="r">ದರ</th><th class="r">ಬದಲಾವಣೆ</th></tr>
      <tr><td class="g">ಅರೇಬಿಕಾ ಪಾರ್ಚ್‌ಮೆಂಟ್</td><td class="r v">23,700–24,200</td><td class="r d dn">▼150</td></tr>
      <tr><td class="g">ಅರೇಬಿಕಾ ಚೆರಿ</td><td class="r v">13,300–15,000</td><td class="r d flat">—</td></tr>
      <tr><td class="g">ರೊಬಸ್ಟಾ ಪಾರ್ಚ್‌ಮೆಂಟ್</td><td class="r v">18,000–18,500</td><td class="r d flat">—</td></tr>
      <tr><td class="g">ರೊಬಸ್ಟಾ ಚೆರಿ</td><td class="r v">10,000–10,800</td><td class="r d flat">—</td></tr>
    </table>
    <div class="note">ವಿದೇಶಿ ಮಾರ್ಕೆಟ್: ನ್ಯೂಯಾರ್ಕ್ ಅರೇಬಿಕಾ 276.50 ಸೆಂಟ್/ಪೌಂಡ್ ▼1.79% · ಲಂಡನ್ ರೊಬಸ್ಟಾ $3,391/ಟನ್ ▼1.14% · ಡಾಲರ್ ₹95.73</div>""",

"""    <h2>ಇವತ್ತಿನ ಸುದ್ದಿ</h2>
    <div class="item"><div class="ih">ಅರೇಬಿಕಾ ಎರಡೂವರೆ<br>ತಿಂಗಳ ಕನಿಷ್ಠಕ್ಕೆ</div>
    <p>ಮೂರು ವಾರದಿಂದ ಜಗತ್ತಿನಲ್ಲಿ ಕಾಫಿ ಸಪ್ಲೈ ಜಾಸ್ತಿ ಆಗುತ್ತೆ ಅನ್ನೋ ಲೆಕ್ಕಾಚಾರದಲ್ಲಿ ಮಾರ್ಕೆಟ್ ಒತ್ತಡದಲ್ಲಿದೆ.</p>
    <div class="src">ಮೂಲ: Coffee Board of India, 18.09.2026</div></div>
    <div class="item"><div class="ih">ಭಾರತದ ಎಕ್ಸ್‌ಪೋರ್ಟ್ 24% ಜಾಸ್ತಿ</div>
    <p>ಜನವರಿ 1ರಿಂದ ಸೆಪ್ಟೆಂಬರ್ 17ರವರೆಗೆ 3,50,735 ಟನ್ ರವಾನೆ. ಕಳೆದ ವರ್ಷ 2,83,514 ಟನ್ ಇತ್ತು.</p>
    <div class="src">ಮೂಲ: Coffee Board of India, 18.09.2026</div></div>""",

qrcard('ದಿನಾ ದರ ಬೇಕಾ?',
       'ಮಲೆನಾಡು ದರ WhatsApp ಚಾನೆಲ್‌ಗೆ ಸೇರಿ — ಪ್ರತಿ ದಿನ ಕರ್ನಾಟಕದ ದರ ನೇರವಾಗಿ ಸಿಗುತ್ತೆ.',
       KN_SLOT,
       'ದರಗಳು Coffee Board of India ಪ್ರಕಟಿಸಿದ Daily Coffee Market Report ನಿಂದ. ಮಾಹಿತಿಗಾಗಿ ಮಾತ್ರ — ಮಾರಾಟದ ಸಲಹೆ ಅಲ್ಲ.'),
]

# ============ DAILY — ENGLISH ============
de = [
"""    <h2>Karnataka rates</h2>
    <table>
      <tr><th>₹ per 50 kg bag · 17.09.2026</th><th class="r">Rate</th><th class="r">Change</th></tr>
      <tr><td class="g">Arabica Parchment</td><td class="r v">23,700–24,200</td><td class="r d dn">▼150</td></tr>
      <tr><td class="g">Arabica Cherry</td><td class="r v">13,300–15,000</td><td class="r d flat">—</td></tr>
      <tr><td class="g">Robusta Parchment</td><td class="r v">18,000–18,500</td><td class="r d flat">—</td></tr>
      <tr><td class="g">Robusta Cherry</td><td class="r v">10,000–10,800</td><td class="r d flat">—</td></tr>
    </table>
    <div class="note">World market: NY Arabica 276.50 c/lb ▼1.79% · London Robusta $3,391/t ▼1.14% · USD ₹95.73</div>""",

"""    <h2>Today's news</h2>
    <div class="item"><div class="ih">Arabica at a<br>2.5-month low</div>
    <p>Prices have been under pressure for three weeks on expectations of abundant global supply.</p>
    <div class="src">Source: Coffee Board of India, 18.09.2026</div></div>
    <div class="item"><div class="ih">Indian exports up 24%</div>
    <p>350,735 tonnes shipped between 1 January and 17 September, against 283,514 tonnes a year earlier.</p>
    <div class="src">Source: Coffee Board of India, 18.09.2026</div></div>""",

qrcard('Want the daily rate?',
       'Join the Malenadu Dara WhatsApp channel — Karnataka prices every working day, straight to your phone.',
       EN_SLOT,
       'Prices from the Coffee Board of India Daily Coffee Market Report. Information only, not selling advice.'),
]

SETS = [
 ('malenadu-dara/assets/cards-monthly-kn.html', mk, ('ಮಲೆನಾಡು ದರ',''), 'ಆಗಸ್ಟ್ 2026', KN_CONTACT, True),
 ('malenadu-dara/assets/cards-monthly-en.html', me, ('Malenadu Dara',''), 'August 2026', EN_CONTACT, True),
 ('malenadu-dara-daily/assets/cards-daily-kn.html', dk, ('ಮಲೆನಾಡು ದರ',''), '18 ಸೆಪ್ಟೆಂಬರ್ 2026', KN_CONTACT, False),
 ('malenadu-dara-daily/assets/cards-daily-en.html', de, ('Malenadu Dara',''), '18 September 2026', EN_CONTACT, False),
]

for path, bodies, hdr, date, contact, cover_dark in SETS:
    n = len(bodies)
    # green bookends: cover and closing card are dark, interior cards are white
    cards = [card(hdr, date, b, i + 1, n, contact,
                  dark=(i == n - 1 or (cover_dark and i == 0)))
             for i, b in enumerate(bodies)]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # newline='\n' so regenerating on Windows does not flip every line to CRLF
    open(path, 'w', encoding='utf-8', newline='\n').write(doc(cards))
    print(f'{path}  ({n} cards)')
