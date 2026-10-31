#!/usr/bin/env python3
"""LINE S2 — Volume-Shock Entries.
Cells frozen in stocks_S2_frozen.md BEFORE scoring. CONTROLS-FIRST:
the timing audit (entry bar index == shock bar index + 1, asserted
over ALL trades) and the shifted-volume placebo run in the SAME
run as scoring; an audit failure aborts before any score prints.
Equity cash, LONG/SHORT, paper only, real Rs0. Provisional per
100 shares, net = gross - Rs40/trade. Window Jan-Oct 2026 (days
as cached via the price/volume join: home to 28 Oct, ext to
30 Oct).

Exits replayed with the programme's frozen replay_plain from
stocks_tuning_universe.py (stop-first, 15:10 square-off).
"""
import csv, json, sys
import importlib.util
from collections import defaultdict

BASE = "/home/hatch/workspace/trading"
spec = importlib.util.spec_from_file_location("univ", f"{BASE}/stocks_tuning_universe.py")
U = importlib.util.module_from_spec(spec)
_argv = sys.argv
sys.argv = ["univ"]
spec.loader.exec_module(U)
sys.argv = _argv

COST = 40.0
OLD_SYMS = ["GODREJCP", "GLENMARK", "ITC", "RECLTD", "TVSMOTOR", "UNITDSPR", "OBEROIRLTY",
            "NTPC", "INDUSTOWER", "KALYANKJIL", "HDFCBANK", "NHPC", "PFC", "IRCTC", "WIPRO",
            "NATIONALUM", "VEDL", "HINDCOPPER", "HINDZINC", "HINDALCO", "TATASTEEL",
            "ASTRAL", "BDL", "OIL", "HINDUNILVR"]
EXT_SYMS = ["RELIANCE", "TCS", "ICICIBANK", "INFY", "BHARTIARTL", "SBIN", "LT",
            "AXISBANK", "KOTAKBANK", "BAJFINANCE", "HCLTECH", "MARUTI", "SUNPHARMA",
            "TITAN", "M&M", "ULTRACEMCO", "NESTLEIND", "POWERGRID", "ONGC", "COALINDIA",
            "JSWSTEEL", "GRASIM", "CIPLA", "DRREDDY", "EICHERMOT"]
WIN_START, WIN_END = "2026-01-01", "2026-10-31"
RESULTS_F = f"{BASE}/stocks_S2_results.json"

UNIV = [("home", "progressive", "progressive_vol", OLD_SYMS),
        ("ext", "progressive_ext", "progressive_vol_ext", EXT_SYMS)]

MOVE_MIN = 0.003        # shock bar's own move, frozen
PRIOR_N = 20            # prior bars for the volume mean, frozen
MAX_ENTRIES = 2         # per stock-day, frozen
SCAN_FROM = "09:30"     # frozen scan start (i >= 20 binds in practice)


def load_days(pdir, vdir, sym):
    """Join price + volume on timestamp; return {date: [bars]} with
    each bar carrying its volume. Days are the join's days."""
    vol = {}
    with open(f"{BASE}/data/{vdir}/{sym}/spot_5m_vol.csv") as f:
        for r in csv.DictReader(f):
            vol[r["timestamp"][:16]] = float(r["volume"])
    days = {}
    with open(f"{BASE}/data/{pdir}/{sym}/spot_5m.csv") as f:
        for r in csv.DictReader(f):
            key = r["timestamp"][:16]
            if key not in vol:
                continue
            d = key[:10]
            if not (WIN_START <= d <= WIN_END):
                continue
            days.setdefault(d, []).append(
                {"time": key[11:16], "open": float(r["open"]),
                 "high": float(r["high"]), "low": float(r["low"]),
                 "close": float(r["close"]), "volume": vol[key]})
    for d in days:
        days[d].sort(key=lambda c: c["time"])
    return days


def eff_volumes(candles, shifted_map):
    """Effective volume series for a day. shifted_map=None -> the
    day's own volumes. Otherwise a {time: volume} map from the
    previous trading day (placebo); missing clock times -> None."""
    if shifted_map is None:
        return [c["volume"] for c in candles]
    return [shifted_map.get(c["time"]) for c in candles]


def build_day(candles, eff_vol, mult, tp, sp):
    """Frozen S2 rule on one stock-day. Returns trade dicts with
    shock/entry bar indices for the timing audit."""
    trades = []
    n = len(candles)
    i = 0
    while len(trades) < MAX_ENTRIES and i < n:
        c = candles[i]
        shock = False
        sign = 0
        ratio = None
        if c["time"] >= SCAN_FROM and i >= PRIOR_N:
            window = eff_vol[i - PRIOR_N:i]
            if all(v is not None for v in window) and eff_vol[i] is not None:
                mean = sum(window) / PRIOR_N
                if mean > 0 and eff_vol[i] >= mult * mean:
                    move = c["close"] / c["open"] - 1 if c["open"] else 0.0
                    if move >= MOVE_MIN:
                        shock, sign = True, 1
                    elif move <= -MOVE_MIN:
                        shock, sign = True, -1
                    if shock:
                        ratio = eff_vol[i] / mean
        if not shock:
            i += 1
            continue
        entry_idx = i + 1
        if entry_idx >= n or candles[entry_idx]["time"] > "15:05":
            break  # no executable entry bar before the 15:10 square-off
        entry = float(candles[entry_idx]["open"])
        er, ep, et, j, gross = U.replay_plain(candles, entry_idx, sign, entry, tp, sp)
        trades.append({
            "dir": "LONG" if sign == 1 else "SHORT",
            "shock_idx": i, "entry_idx": entry_idx,
            "shock_time": c["time"],
            "shock_move_pct": round(100 * (c["close"] / c["open"] - 1), 3),
            "vol_ratio": round(ratio, 2) if ratio is not None else None,
            "entry_time": candles[entry_idx]["time"], "entry": round(entry, 2),
            "exit_reason": er, "exit_time": et, "exit": round(ep, 2),
            "gross": round(gross, 2), "net": round(gross - COST, 2)})
        i = j + 1  # resume scanning the bar after the exit bar
    return trades


CELLS = {
    # cell: (volume multiple, tp %, sp %)
    "S2-A": (3.0, 0.50, 0.50),
    "S2-B": (3.0, 1.25, 0.50),
    "S2-C": (4.0, 1.25, 0.50),
}


def score_cell(cell, cache, placebo=False):
    mult, tp, sp = CELLS[cell]
    trades = []
    for univ, syms in (("home", OLD_SYMS), ("ext", EXT_SYMS)):
        for sym in syms:
            days = cache[(univ, sym)]
            dates = sorted(days)
            for di, d in enumerate(dates):
                candles = days[d]
                if placebo:
                    if di == 0:
                        continue
                    prev = {c["time"]: c["volume"] for c in days[dates[di - 1]]}
                    ev = eff_volumes(candles, prev)
                else:
                    ev = eff_volumes(candles, None)
                for t in build_day(candles, ev, mult, tp, sp):
                    trades.append({"cell": cell, "universe": univ, "symbol": sym,
                                   "date": d, **t})
    return trades


def stats(trades, total_stocks):
    def block(ts):
        m = U.metrics(ts)
        return {"trades": m["trades"], "net": m["net"], "win_pct": m["win_pct"],
                "exp": m["exp"]}
    jm = [t for t in trades if t["date"] <= "2026-05-31"]
    jo = [t for t in trades if t["date"] >= "2026-06-01"]
    oc = [t for t in trades if t["date"][:7] == "2026-10"]
    per = defaultdict(float)
    for t in trades:
        per[t["symbol"]] += t["net"]
    return {"all": block(trades), "jan_may": block(jm), "jun_oct": block(jo),
            "october": block(oc),
            "long": block([t for t in trades if t["dir"] == "LONG"]),
            "short": block([t for t in trades if t["dir"] == "SHORT"]),
            "breadth": sum(1 for v in per.values() if v > 0),
            "stocks_total": total_stocks,
            "worst5": sorted(per.items(), key=lambda kv: kv[1])[:5],
            "best5": sorted(per.items(), key=lambda kv: -kv[1])[:5]}


def dump_csv(tag, trades):
    cols = ["cell", "universe", "symbol", "date", "dir", "shock_time",
            "shock_move_pct", "vol_ratio", "entry_time", "entry",
            "exit_time", "exit", "exit_reason", "gross", "net"]
    with open(f"{BASE}/stocks_S2_{tag}_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for t in sorted(trades, key=lambda x: (x["date"], x["symbol"], x["entry_time"])):
            w.writerow({c: t.get(c, "") for c in cols})


def audit(tag, trades):
    """Timing audit: entry must be exactly the bar after the shock
    bar (shock fully closed), shock must have >= PRIOR_N priors."""
    bad = [t for t in trades
           if t["entry_idx"] != t["shock_idx"] + 1 or t["shock_idx"] < PRIOR_N]
    print(f"AUDIT {tag}: {len(trades)} trades checked, violations = {len(bad)}",
          flush=True)
    for t in trades[:5]:
        print(f"  sample [{t['cell']}] {t['symbol']} {t['date']} {t['dir']}: "
              f"shock bar idx {t['shock_idx']} closed {t['shock_time']} "
              f"(move {t['shock_move_pct']:+.2f}%, vol x{t['vol_ratio']}) "
              f"-> entry idx {t['entry_idx']} at {t['entry_time']}", flush=True)
    return bad


def gate(pooled, placebo_net):
    return {
        "jan_may_positive": pooled["jan_may"]["net"] > 0,
        "jun_oct_positive": pooled["jun_oct"]["net"] > 0,
        "breadth_ge_35": pooled["breadth"] >= 35,
        "october_positive": pooled["october"]["net"] > 0,
        "placebo_beaten": placebo_net is not None and pooled["all"]["net"] > placebo_net,
    }


def main():
    cache = {}
    for univ, pdir, vdir, syms in UNIV:
        for sym in syms:
            cache[(univ, sym)] = load_days(pdir, vdir, sym)
    joined = sum(len(v[d]) for v in cache.values() for d in v)
    print(f"Loaded {len(cache)} stock caches, {joined} joined bars.", flush=True)

    all_trades = {cell: score_cell(cell, cache) for cell in CELLS}

    # ---- CONTROLS-FIRST: audit before any score is printed ----
    bad = []
    for cell, trades in all_trades.items():
        bad += audit(cell, trades)
    if bad:
        print("TIMING AUDIT FAILED — aborting, no scores quoted.", flush=True)
        sys.exit(1)
    print("TIMING AUDIT CLEAN for all cells.\n", flush=True)

    # ---- Placebo on the best cell (pooled net; tie -> lower letter) ----
    nets = {c: sum(t["net"] for t in ts) for c, ts in all_trades.items()}
    best = sorted(CELLS, key=lambda c: (-nets[c], c))[0]
    placebo_trades = score_cell(best, cache, placebo=True)
    badp = audit(f"PLACEBO({best}, shifted volume)", placebo_trades)
    if badp:
        print("PLACEBO TIMING AUDIT FAILED — aborting.", flush=True)
        sys.exit(1)
    placebo_net = round(sum(t["net"] for t in placebo_trades), 2)
    print(f"Best cell = {best}; shifted-volume placebo pooled net = "
          f"Rs {placebo_net:+.2f} on {len(placebo_trades)} trades.\n", flush=True)

    results = {"placebo": {"cell": best, "trades": len(placebo_trades),
                           "net": placebo_net,
                           "pooled": stats(placebo_trades, 50)}}
    for cell, trades in all_trades.items():
        pooled = stats(trades, 50)
        home = stats([t for t in trades if t["universe"] == "home"], 25)
        ext = stats([t for t in trades if t["universe"] == "ext"], 25)
        g = gate(pooled, placebo_net if cell == best else None)
        results[cell] = {"pooled": pooled, "home": home, "ext": ext,
                         "gate_vs_placebo_cell_only": g,
                         "gate_pass_ex_placebo": all(
                             v for k, v in g.items() if k != "placebo_beaten")}
        dump_csv(cell, trades)
        p = pooled
        print(f"{cell}: pooled trades={p['all']['trades']} net={p['all']['net']:+.2f} "
              f"exp={p['all']['exp']:+.2f} win={p['all']['win_pct']}% "
              f"JM={p['jan_may']['net']:+.2f} JO={p['jun_oct']['net']:+.2f} "
              f"Oct={p['october']['net']:+.2f} breadth={p['breadth']}/50 "
              f"L={p['long']['net']:+.2f} S={p['short']['net']:+.2f} | "
              f"home net={home['all']['net']:+.2f} br={home['breadth']}/25 | "
              f"ext net={ext['all']['net']:+.2f} br={ext['breadth']}/25",
              flush=True)
    dump_csv(f"{best}_PLACEBO", placebo_trades)
    json.dump(results, open(RESULTS_F, "w"), indent=1)
    print("\nDONE. Results in", RESULTS_F, flush=True)


if __name__ == "__main__":
    main()
