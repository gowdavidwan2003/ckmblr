# coffee — ಮಲೆನಾಡು ದರ

Claude Code project for the Malenadu Dara coffee publication: daily rate and
news cards, and the monthly market brief, in Kannada and English, for Instagram,
Facebook and WhatsApp.

## Setup

```bash
unzip coffee.zip && cd coffee
bash scripts/setup.sh     # python deps, then reports what it can render with
claude
```

Optionally `git init && git add . && git commit -m "Malenadu Dara"` to start
tracking it.

The build needs one engine for HTML->PDF and one for PDF->PNG, and takes
whichever it finds:

| | HTML -> PDF | PDF -> PNG |
|---|---|---|
| macOS, Linux | WeasyPrint | `pdftoppm` |
| Windows | headless Chrome or Edge | Ghostscript |

- macOS: `brew install poppler`
- Debian/Ubuntu: `sudo apt install poppler-utils libpango-1.0-0 libpangoft2-1.0-0`
- Windows: nothing to install if Chrome or Edge is there; Ghostscript from
  <https://ghostscript.com/releases/> covers the raster step. WeasyPrint and
  poppler both want libraries Windows does not ship, so the fallback is the
  normal path there, not a degraded one.

`python3 scripts/check_setup.py` prints what it found and what it would use.

## Use

Inside `claude`, either ask in plain words or use the commands:

```
/daily                 build today's rate + news cards
/daily news-only       no new Coffee Board report today
/monthly sources/2026-09/ico-report.pdf
```

Claude picks up `CLAUDE.md` automatically, and the two skills under
`.claude/skills/` load when the work matches them.

## What's where

| Path | |
|---|---|
| `CLAUDE.md` | standing rules — read this first |
| `.claude/skills/malenadu-dara-daily/` | daily post: templates, build scripts, style refs |
| `.claude/skills/malenadu-dara/` | monthly ICO brief |
| `.claude/commands/` | `/daily`, `/monthly` |
| `sources/` | raw inputs (Coffee Board PDFs, ICO reports) |
| `editions/` | one folder per edition; `work/` HTML, `out/` PNGs |
| `docs/distribution.md` | channels, posting order, contact line |
| `scripts/check_setup.py` | what this machine can render with |

Each skill is self-contained — its own copy of the Kannada font, the QR and the
card templates — so it can be lifted out into another project unchanged.

## Posting

Kannada set first, English second, cards in filename order. Check each PNG
before it goes out: Kannada that failed to shape renders as empty boxes and
nothing in the build warns you.
