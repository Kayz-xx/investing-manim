# Start Early, Stay Invested

A ~7 minute [Manim](https://www.manim.community/) explainer video that teaches college students how to invest.

**Watch:** [`investing_early.mp4`](investing_early.mp4) (1080p, 30 fps, no audio, so you can add your own narration or music)

## What it covers

| # | Scene class | Topic |
|---|-------------|-------|
| – | `Intro` | Title, agenda, disclaimer |
| 1 | `WhatIsInvesting` | Saving vs. investing; stocks, bonds and funds; how inflation eats cash ($1,000 → $554 in 20 yrs at 3%) |
| 2 | `IndexFunds` | One stock vs. 500; what an index fund is; why most active funds trail the S&P 500; ETF vs. index mutual fund; a 1% fee vs. 0.03% fee (~$147k difference); common broad funds |
| 3 | `Compounding` | Growth on growth, year by year; $1,000 → $14,974 over 40 years; Rule of 72; why the last decade matters most |
| 4 | `StartEarly` | Early Emma vs. Late Liam ($24k in beats $79k in); cost of starting at 22 vs. 32 vs. 42; start with $25–$50 |
| 5 | `RecurringInvesting` | Dollar-cost averaging walkthrough; why to automate; time in the market vs. missing the 10 best days |
| 6 | `TaxesLongTerm` | Short- vs. long-term capital gains; $10k profit example (incl. the 0% bracket); buy-and-hold avoids tax drag; Roth IRA and 401(k) match |
| 7 | `MakingDecisions` | Order of operations (emergency fund → debt → match → Roth → brokerage); stock/bond mix by age; crashes and recoveries; checklist and red flags |
| – | `Recap` | Seven-point playbook and a closing line |

## Rendering

Requires Python 3.9+, `ffmpeg`, and Pango/Cairo dev libraries (`libpango1.0-dev` on Debian/Ubuntu, `brew install pango` on macOS). **No LaTeX needed**, because all text uses Manim's `Text`.

```bash
python -m venv .venv && source .venv/bin/activate
pip install manim

./render_all.sh              # full video, 1080p30 -> investing_early.mp4
./render_all.sh -ql          # fast 480p preview
JOBS=4 ./render_all.sh       # render scenes in parallel

manim -pql investing_early.py Compounding   # preview a single scene
```

The video uses the [Inter](https://rsms.me/inter/) font if you have it installed and falls back to your system sans-serif otherwise.
To give viewers more or less reading time, change `Base.PACE` in `investing_early.py`.

## Assumptions and sources

- Growth examples assume a **7% average annual return** with monthly contributions. This is a common long-run assumption for a stock index fund, **not a guarantee**.
- Active vs. passive: S&P Dow Jones Indices, [SPIVA U.S. Scorecard](https://www.spglobal.com/spdji/en/spiva/article/spiva-us-year-end-2024). Over 15 years, roughly 9 in 10 U.S. large-cap active funds underperformed the S&P 500.
- Missing the best days: J.P. Morgan Asset Management analysis of a $10,000 S&P 500 investment, 2005–2024 (~$71,750 if you stayed invested vs. ~$32,871 if you missed the 10 best days). J.P. Morgan updates these figures every year.
- 2026 IRA contribution limit is $7,500 (IRS). Capital-gains rates are simplified U.S. federal rates.
- The crash chart is stylized. The 2008 (~−57%) and 2020 (~−34%) figures are approximate S&P 500 peak-to-trough drops.

*Educational content only, not financial advice.*
