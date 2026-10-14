# Investing early: visual aids for a talk

17 short [Manim](https://www.manim.community/) clips to play behind a speaker who's teaching college students to invest.
The visuals carry each idea, and on-screen text is limited to labels and the one number worth remembering.
Most clips use **real S&P 500 history**; the projections use an assumed 7% a year and say so on screen.

- `clips/` has one file per idea, so you can advance them like slides.
- [`investing_early.mp4`](investing_early.mp4) is all 17 clips in talk order (1080p30, no audio).

Each clip ends on a held frame, so there's time to talk before it clears.

## The clips and what to say over them

| # | Clip | On screen | Numbers worth saying |
|---|------|-----------|----------------------|
| 1 | `Ownership` | A company drawn as 100 shares. One share lifts out and grows with the company, then dividends flow to it. | $100 for 1% of the company; it becomes $160 when the company is worth 1.6× more |
| 2 | `CashVsInflation` | $1,000 from Jan 2006 (about when the audience was born) kept as cash vs. put in the S&P 500, in today's dollars | Cash buys **$650** of stuff; invested buys **$3,104**, including the 2008 crash |
| 3 | `StockPicking` | Every U.S. stock since 1926 as 100 squares, sorted by outcome. Then random picks of 10, then an index wraps all 100. | **4%** of stocks made all of the market's net gains, **57%** did worse than T-bills, and 10 random picks miss every winner **65%** of the time |
| 4 | `ActiveFunds` | 100 managed funds racing the index for 15 years, with a live count of how many are still ahead | About **10 of 100** finish ahead. Real-world SPIVA: ~9 in 10 trail over 15 years |
| 5 | `IndexFund` | One share of an S&P 500 fund breaks apart into 500 company slices sized by value | One purchase, 500 companies |
| 6 | `Fees` | $200/month from 22 to 65 at a 0.03% vs. 1% fee, with the gap shaded | **$147,172** lost to fees |
| 7 | `Compounding` | 40 yearly bars of $1,000 at 7%, each split into what you put in, simple growth, and growth on growth | Of the $14,974 at the end, **$11,174** is growth on growth. It doubles about every 10 years |
| 8 | `StartEarly` | Emma pays in from 22 to 32 and stops; Liam pays in from 32 to 65. Then bars for starting at 22, 32 and 42 | Emma puts in $24k and ends with **$320,827**; Liam puts in $79k and ends with **$296,151**. Each decade of waiting roughly halves the result |
| 9 | `TimeHorizon` | One dot per start month since 1927: the S&P 500's average yearly return held for 1, 5, 10 and 20 years | Lost money **26% / 12% / 5% / 0%** of the time. No 20-year stretch lost money, even after inflation |
| 10 | `Crashes` | S&P 500 from 1928 to 2026 on a log scale, with every 20%+ drop shaded from peak to recovery | −86% (1929), −48% (1973), −34% (1987), −49% (2000), −57% (2008), −34% (2020). Every one ended in a new high |
| 11 | `BeatTheCouch` | The [beatthecouch.com](https://beatthecouch.com) game on a hidden 2-year stretch, played live, then revealed and audited against 1,000 random replays | Couch **$11,426** vs. your rule **$9,744**. Your timing did worse than **99.5%** of random timings |
| 12 | `TimingRules` | The same rule on all 885 two-year stretches since 1928 | The couch won **64%** of the time |
| 13 | `BestDays` | All 5,026 trading days of 2000–2019 as bars; the 10 best and 10 worst light up, then two growth lines | 8 of the 10 best days came in the same months as the worst. Missing them turns $21,943 into **$10,960** |
| 14 | `DollarCostAveraging` | $100 a month through 2008–2010 on real prices, with each month's shares stacked as dots. Then the crash months are paused | Crash months buy almost twice the shares. Kept buying: **$4,162**. Paused Oct 2008 – Dec 2009, then put the saved cash in: **$3,813** |
| 15 | `LumpSum` | Every start month since 1927: a lump sum invested at once vs. spread over 12 months, one year later | All at once came out ahead **73%** of the time |
| 16 | `Taxes` | 40 years of $10,000 at 7%, both paying 20% tax on gains: one sells every year, the other holds | Hold and pay once: **$121,796**. Sell every year: **$88,421** |
| 17 | `Priorities` | Paycheck money overflowing buckets in order, then a target-date glide path | Emergency fund → high-interest debt → employer match → tax-free account (if your country has one) → index funds |

### How "stay invested" and "invest every month" fit together

They're the same message: **money in the market as early as possible, and kept there.**

- If you **already have a lump sum**, invest it now (clip 15). Markets rise more often than they fall, so all-at-once beat spreading it out about 3 times in 4.
- If your money **arrives monthly** (most students), invest each paycheck as it comes. That isn't a strategy for "beating" a lump sum; it's simply investing the money as soon as you have it.
- Making it **automatic** is what keeps you invested. It removes the temptation to pause when prices fall (clip 14), which is just market timing again (clips 11–13). The lower average cost from buying more in bad months is a side effect, not the reason.

## Rendering

You need Python 3.9+, `ffmpeg`, and the Pango/Cairo dev libraries (`libpango1.0-dev` on Debian/Ubuntu, `brew install pango` on macOS). No LaTeX is needed.

```bash
python -m venv .venv && source .venv/bin/activate
pip install manim

./render_all.sh                          # every clip at 1080p30, plus investing_early.mp4
./render_all.sh -ql                      # fast 480p preview
JOBS=4 ./render_all.sh                   # render clips in parallel
manim -pql investing.py BeatTheCouch     # one clip
```

- **Font:** Roboto ships in `fonts/` (Apache 2.0) and is registered at startup, so nothing needs installing. To switch fonts (e.g. Montserrat), drop the `.ttf` files in `fonts/` and change `FONT` in `style.py`.
- **Colors:** `style.py` holds the palette. Every two-way comparison uses blue vs. orange, which stays distinct for colorblind viewers; gold marks the key number.
- **Pace:** `Clip.PACE` in `style.py` stretches every animation and pause (1.5 = 50% slower than Manim's defaults); `Clip.HOLD` sets the pause at each moment worth talking over.

## Data and method

`data/prepare.py` turns the raw files in `data/raw/` into `data/derived.json`, which the clips read.

- **Daily S&P 500 closes, 1927–2019:** [fja05680/dow-sp500-100-years](https://github.com/fja05680/dow-sp500-100-years), from Yahoo Finance, MIT licensed. Price only, without dividends. Used for the crash chart, the best days and the timing game.
- **Monthly S&P 500 price, dividends and CPI:** Robert Shiller's data via [datasets/s-and-p-500](https://github.com/datasets/s-and-p-500). Prices are monthly averages. Used for total returns with dividends, the inflation clip, the holding-period dots, dollar-cost averaging, and the 2020–2026 part of the crash chart.
- **Timing game:** modeled on [beatthecouch.com](https://beatthecouch.com), where you get $10,000 and a hidden 2-year window of 1928–2019 S&P 500 history, and the couch buys on day one. The rule here is "sell after a 10% drop from the high, buy back after a 10% bounce off the low". The audit replays the same number of trades and days out of the market at random dates, 1,000 times, as the site's own check does.
- **Stocks vs. T-bills:** Bessembinder (2018), *Do stocks outperform Treasury bills?*, Journal of Financial Economics: U.S. common stocks 1926–2016. The 65% figure is the chance that 10 random picks out of 100 include none of the top 4.
- **Active funds:** the race is a simulation (index − 1.1% a year in fees ± random luck), tuned to match S&P Dow Jones Indices' [SPIVA](https://www.spglobal.com/spdji/en/research-insights/spiva/) finding that ~9 in 10 U.S. large-cap funds trail the S&P 500 over 15 years.
- **Lump sum vs. spread out:** for every start month, a lump sum invested at once vs. the same amount in 12 equal monthly buys, valued 12 months after the first buy. Cash waiting to be invested earns nothing here, which slightly flatters investing at once.
- **Taxes:** a generic 20% tax on gains, charged when gains are realized. Rules differ by country (some don't tax capital gains, some tax them every year), so the clip says so.
- The bear markets of 2020 (−33.9%) and 2022 (−25.4%) come after the daily file ends, so their depths and dates are entered by hand in `prepare.py`.

*Educational only, not financial advice. Past returns don't guarantee future ones.*
