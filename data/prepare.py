"""
Turn the raw market data into the small series the scenes animate.

    python data/prepare.py        # writes data/derived.json

Inputs (data/raw/):
  sp500_daily_1927_2019.csv  S&P 500 daily close, 1927-12-30 .. 2019-12-23 (price only,
                             no dividends). From github.com/fja05680/dow-sp500-100-years
                             (Yahoo Finance ^GSPC), MIT licensed.
  shiller_monthly.csv        Robert Shiller's monthly S&P 500 price, dividend and CPI
                             series via github.com/datasets/s-and-p-500 (ODC-PDDL).
                             Prices are monthly averages; dividends end mid-2023.
"""

import csv
import json
import random
from pathlib import Path

HERE = Path(__file__).parent
RAW = HERE / "raw"
TRADING_DAYS_2Y = 504
SEED = 7


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
def load_daily():
    with open(RAW / "sp500_daily_1927_2019.csv") as f:
        rows = list(csv.DictReader(f))
    return [r["Date"] for r in rows], [float(r["Close"]) for r in rows]


def load_monthly():
    with open(RAW / "shiller_monthly.csv") as f:
        rows = list(csv.DictReader(f))
    return [
        {
            "month": r["Date"][:7],
            "price": float(r["SP500"]),
            "dividend": float(r["Dividend"]),
            "cpi": float(r["Consumer Price Index"]),
        }
        for r in rows
    ]


def total_return_index(monthly, start="1926-12"):
    """Monthly total-return index (dividends reinvested) until dividend data runs out."""
    index, prev, out = 1.0, None, {}
    for m in monthly:
        if m["month"] < start:
            continue
        if m["dividend"] == 0:
            break
        if prev is not None:
            index *= (m["price"] + m["dividend"] / 12) / prev
        out[m["month"]] = index
        prev = m["price"]
    return out


# ---------------------------------------------------------------------------
# Market-timing game (after beatthecouch.com)
# ---------------------------------------------------------------------------
def timing_rule(prices, drop=0.10, rebound=0.10):
    """Sell after falling `drop` from the high; buy back after rising `rebound` off the low.

    Returns (in_market flags per day, list of (action, day index)).
    """
    in_market, holding, high, low, trades = [], True, prices[0], None, []
    for i, p in enumerate(prices):
        if holding:
            high = max(high, p)
            if p <= high * (1 - drop):
                holding, low = False, p
                trades.append(("sell", i))
        else:
            low = min(low, p)
            if p >= low * (1 + rebound):
                holding, high = True, p
                trades.append(("buy", i))
        in_market.append(holding)
    return in_market, trades


def growth(prices, in_market):
    """Growth factor when holding over day i -> i+1 whenever in the market at day i."""
    g = 1.0
    for i in range(1, len(prices)):
        if in_market[i - 1]:
            g *= prices[i] / prices[i - 1]
    return g


def out_of_market_runs(in_market):
    runs, i = [], 0
    while i < len(in_market):
        if in_market[i]:
            i += 1
            continue
        j = i
        while j < len(in_market) and not in_market[j]:
            j += 1
        runs.append(j - i)
        i = j
    return runs


def random_replay(n, runs, rng):
    """Same number of trades and same days out of the market, placed at random."""
    free = n - sum(runs)
    cuts = sorted(rng.sample(range(1, free), len(runs)))
    lengths = runs[:]
    rng.shuffle(lengths)
    flags, pos, prev = [True] * n, 0, 0
    for cut, length in zip(cuts, lengths):
        pos += cut - prev
        prev = cut
        for t in range(pos, min(pos + length, n)):
            flags[t] = False
        pos += length
    return flags


def two_year_windows(prices, step=21):
    return range(0, len(prices) - TRADING_DAYS_2Y, step)


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def main():
    dates, close = load_daily()
    monthly = load_monthly()
    by_month = {m["month"]: m for m in monthly}
    tr = total_return_index(monthly)
    out = {}

    # Inflation vs. investing: $1,000 set aside in Jan 2006, in today's money
    start, end = "2006-01", "2023-06"
    months = [k for k in sorted(tr) if start <= k <= end]
    cpi0 = by_month[start]["cpi"]
    out["inflation"] = {
        "months": months,
        "cash_real": [1000 * cpi0 / by_month[k]["cpi"] for k in months],
        "stocks_real": [1000 * tr[k] / tr[start] * cpi0 / by_month[k]["cpi"] for k in months],
    }

    # Range of annualized total returns by holding period (every start month since 1927)
    keys = sorted(tr)
    rolling = {}
    for years in (1, 5, 10, 20):
        n = years * 12
        rolling[str(years)] = [
            (tr[keys[i + n]] / tr[keys[i]]) ** (1 / years) - 1 for i in range(len(keys) - n)
        ]
    out["rolling"] = {"first": keys[0], "last": keys[-1], "returns": rolling}

    # Long-run price history: daily closes (weekly sample) then Shiller monthly after 2019
    weekly = [(d, p) for i, (d, p) in enumerate(zip(dates, close)) if i % 5 == 0]
    later = [(m["month"] + "-15", m["price"]) for m in monthly if m["month"] >= "2020-01"]
    drawdowns, peak, current = [], (dates[0], close[0]), None
    for d, p in zip(dates, close):
        if p >= peak[1]:
            if current and current["depth"] <= -0.2:
                current["recovered"] = d
                drawdowns.append(current)
            peak, current = (d, p), None
            continue
        depth = p / peak[1] - 1
        if current is None or depth < current["depth"]:
            current = {"peak": peak[0], "trough": d, "depth": depth}
    # The daily file ends in 2019; the two bear markets since then (S&P 500 closes):
    drawdowns += [
        {"peak": "2020-02-19", "trough": "2020-03-23", "depth": -0.339, "recovered": "2020-08-18"},
        {"peak": "2022-01-03", "trough": "2022-10-12", "depth": -0.254, "recovered": "2024-01-19"},
    ]
    out["history"] = {"points": weekly + later, "drawdowns": drawdowns}

    # Dollar-cost averaging through the 2008 crash: $100 at each monthly average price
    dca = [k for k in sorted(by_month) if "2008-01" <= k <= "2010-12"]
    out["dca"] = {"months": dca, "prices": [by_month[k]["price"] for k in dca]}

    # Best days, 2000-2019
    i0 = dates.index("1999-12-31")
    seg_dates, seg_close = dates[i0:], close[i0:]
    daily = [seg_close[i] / seg_close[i - 1] - 1 for i in range(1, len(seg_close))]
    ranked = sorted(range(len(daily)), key=lambda i: daily[i])
    best10, worst10 = ranked[-10:], ranked[:10]

    def path(skip):
        v, pts = 10000.0, [10000.0]
        for i, r in enumerate(daily):
            if i not in skip:
                v *= 1 + r
            pts.append(v)
        return pts

    out["best_days"] = {
        "dates": seg_dates,
        "returns": daily,
        "best10": best10,
        "worst10": worst10,
        "full": path(set())[::5],
        "missed10": path(set(best10))[::5],
        "final_full": path(set())[-1],
        "final_missed": {k: path(set(ranked[-k:]))[-1] for k in (5, 10, 20, 30)},
    }

    # Market-timing game on one hidden 2-year window
    rng = random.Random(SEED)
    s = dates.index("2015-06-01")
    window = close[s : s + TRADING_DAYS_2Y]
    flags, trades = timing_rule(window)
    runs = out_of_market_runs(flags)
    replays = [growth(window, random_replay(len(window), runs, rng)) for _ in range(1000)]
    out["game"] = {
        "start": dates[s],
        "end": dates[s + TRADING_DAYS_2Y - 1],
        "prices": window,
        "in_market": flags,
        "trades": trades,
        "player": growth(window, flags),
        "couch": window[-1] / window[0],
        "replays": replays,
    }

    # Same rule on every 2-year window, 1928-2019
    windows = []
    for s in two_year_windows(close):
        w = close[s : s + TRADING_DAYS_2Y]
        f, t = timing_rule(w)
        if t:
            windows.append({"start": dates[s], "edge": growth(w, f) / (w[-1] / w[0]) - 1})
    out["all_windows"] = windows

    # A lump sum invested at once vs. spread over 12 monthly buys (cash waiting earns nothing),
    # compared one year after the first buy, for every start month
    lump = []
    for i in range(len(keys) - 12):
        at_once = tr[keys[i + 12]] / tr[keys[i]]
        spread = sum(tr[keys[i + 12]] / tr[keys[i + k]] for k in range(12)) / 12
        lump.append({"start": keys[i], "edge": at_once / spread - 1})
    out["lump_sum"] = lump

    with open(HERE / "derived.json", "w") as f:
        json.dump(out, f, separators=(",", ":"))

    game = out["game"]
    print(f"game {game['start']}..{game['end']}: couch {game['couch']:.3f}, player {game['player']:.3f}, "
          f"replays beaten by player: {sum(r < game['player'] for r in replays) / 10:.1f}%")
    print(f"rule beat the couch in {sum(w['edge'] > 0 for w in windows) / len(windows):.0%} of {len(windows)} windows")
    print(f"lump sum ahead in {sum(x['edge'] > 0 for x in lump) / len(lump):.0%} of {len(lump)} start months")
    print(f"best days: full {out['best_days']['final_full']:.0f}, missed {out['best_days']['final_missed']}")


if __name__ == "__main__":
    main()
