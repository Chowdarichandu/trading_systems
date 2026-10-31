#!/usr/bin/env python3
"""LINE R2 — Generalised Follow-Through + Overnight Gap.
Cells frozen in stocks_R2_frozen.md BEFORE scoring. CONTROLS-FIRST:
the timing audit (entry_dt > info_complete, asserted over ALL trades)
runs in the SAME run as scoring; if it fails, the run aborts before
printing any score. Equity cash, LONG/SHORT, paper only, real Rs0.
Provisional per 100 shares, net = gross - Rs40/trade. Window
Jan-Oct 2026 (home Oct = 1-28 as cached; ext Oct = 1-30 as cached).

Exits replayed with the programme's frozen replay_plain from
stocks_tuning_universe.py (stop-first, 15:10 square-off).
"""
import csv, json, sys, os
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
RESULTS_F = f"{BASE}/stocks_R2_results.json"

UNIV = [("home", "progressive", OLD_SYMS), ("ext", "progressive_ext", EXT_SYMS)]


def load_days(data_dir, sym):
    path = f"{BASE}/data/{data_dir}/{sym}/spot_5m.csv"
    days = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            d = r["timestamp"][:10]
            days.setdefault(d, []).append(
                {"time": r["timestamp"][11:16], "open": float(r["open"]),
                 "high": float(r["high"]), "low": float(r["low"]),
                 "close": float(r["close"])})
    for d in days:
        days[d].sort(key=lambda c: c["time"])
    return days


def day_oc(candles):
    return candles[0]["open"], candles[-1]["close"]


def build_ft(days, thr):
    """Axis 1 qualifiers: list of (entry_date, sign, bigday, move_pct)."""
    dates = sorted(days)
    out = []
    for i in range(1, len(dates) - 1):
        d, nxt = dates[i], dates[i + 1]
        if not (WIN_START <= nxt <= WIN_END):
            continue
        _, pc = day_oc(days[dates[i - 1]])
        _, cc = day_oc(days[d])
        if not pc:
            continue
        ret = cc / pc - 1
        if abs(ret) >= thr:
            out.append((nxt, 1 if ret > 0 else -1, d, round(100 * ret, 3)))
    return out


def build_gap(days, thr):
    """Axis 2 qualifiers: list of (date, gap_sign, gap_pct)."""
    dates = sorted(days)
    out = []
    for i in range(1, len(dates)):
        d = dates[i]
        if not (WIN_START <= d <= WIN_END):
            continue
        _, pc = day_oc(days[dates[i - 1]])
        op, _ = day_oc(days[d])
        if not pc:
            continue
        gap = op / pc - 1
        if abs(gap) >= thr:
            out.append((d, 1 if gap > 0 else -1, round(100 * gap, 3)))
    return out


def run_trade(days, date, entry_idx, sign, tp, sp):
    candles = days[date]
    if entry_idx >= len(candles):
        return None
    entry = float(candles[entry_idx]["open"])
    er, ep, et, _j, gross = U.replay_plain(candles, entry_idx, sign, entry, tp, sp)
    return {"entry_time": candles[entry_idx]["time"], "entry": round(entry, 2),
            "exit_reason": er, "exit_time": et, "exit": round(ep, 2),
            "gross": round(gross, 2), "net": round(gross - COST, 2)}


CELLS = {
    # cell: (axis, builder params, tp, sp, mode)
    "FT-20-T125": ("FT", 0.020, 1.25, 0.50, None),
    "FT-20-T10":  ("FT", 0.020, 1.00, 0.50, None),
    "FT-25-T125": ("FT", 0.025, 1.25, 0.50, None),
    "FT-25-T10":  ("FT", 0.025, 1.00, 0.50, None),
    "GAP-10-FOLLOW": ("GAP", 0.010, 1.25, 0.50, "follow"),
    "GAP-10-FADE":   ("GAP", 0.010, 1.25, 0.50, "fade"),
    "GAP-15-FOLLOW": ("GAP", 0.015, 1.25, 0.50, "follow"),
    "GAP-15-FADE":   ("GAP", 0.015, 1.25, 0.50, "fade"),
}


def score_cell(cell, cache):
    axis, thr, tp, sp, mode = CELLS[cell]
    trades = []
    for univ, data_dir, syms in UNIV:
        for sym in syms:
            days = cache[(univ, sym)]
            if axis == "FT":
                for (edate, sign, bigday, mv) in build_ft(days, thr):
                    t = run_trade(days, edate, 0, sign, tp, sp)
                    if t is None:
                        continue
                    trades.append({"cell": cell, "universe": univ, "symbol": sym,
                                   "date": edate, "dir": "LONG" if sign == 1 else "SHORT",
                                   "qualifier": f"big-move day {bigday} {mv:+.2f}%",
                                   "info_complete": f"{bigday} 15:30",
                                   "entry_dt": f"{edate} {t['entry_time']}", **t})
            else:
                for (gdate, gsign, gp) in build_gap(days, thr):
                    sign = gsign if mode == "follow" else -gsign
                    candles = days[gdate]
                    idx = next((k for k, c in enumerate(candles) if c["time"] == "09:20"), None)
                    if idx is None:
                        continue
                    t = run_trade(days, gdate, idx, sign, tp, sp)
                    if t is None:
                        continue
                    trades.append({"cell": cell, "universe": univ, "symbol": sym,
                                   "date": gdate, "dir": "LONG" if sign == 1 else "SHORT",
                                   "qualifier": f"overnight gap {gdate} {gp:+.2f}% ({mode})",
                                   "info_complete": f"{gdate} 09:15",
                                   "entry_dt": f"{gdate} {t['entry_time']}", **t})
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


def dump_csv(cell, trades):
    cols = ["cell", "universe", "symbol", "date", "dir", "qualifier",
            "info_complete", "entry_dt", "entry_time", "entry", "exit_time",
            "exit", "exit_reason", "gross", "net"]
    with open(f"{BASE}/stocks_R2_{cell}_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for t in sorted(trades, key=lambda x: (x["date"], x["symbol"])):
            w.writerow({c: t.get(c, "") for c in cols})


def audit(axis, trades):
    bad = [t for t in trades if not (t["entry_dt"] > t["info_complete"])]
    print(f"AUDIT {axis}: {len(trades)} trades checked across cells, "
          f"violations = {len(bad)}", flush=True)
    for t in trades[:10]:
        print(f"  sample [{t['cell']}] {t['symbol']} {t['date']} {t['dir']}: "
              f"info_complete={t['info_complete']} -> entry={t['entry_dt']} "
              f"({t['qualifier']})", flush=True)
    return bad


def main():
    cache = {}
    for univ, data_dir, syms in UNIV:
        for sym in syms:
            cache[(univ, sym)] = load_days(data_dir, sym)
    print(f"Loaded {len(cache)} stock caches.", flush=True)

    all_trades = {}
    for cell in CELLS:
        all_trades[cell] = score_cell(cell, cache)

    # ---- CONTROLS-FIRST: audit before any score is printed ----
    ft_all = [t for c in CELLS if c.startswith("FT") for t in all_trades[c]]
    gap_all = [t for c in CELLS if c.startswith("GAP") for t in all_trades[c]]
    bad = audit("AXIS 1 FT", ft_all) + audit("AXIS 2 GAP", gap_all)
    if bad:
        print("TIMING AUDIT FAILED — aborting, no scores quoted.", flush=True)
        sys.exit(1)
    print("TIMING AUDIT CLEAN for both axes.\n", flush=True)

    results = {}
    for cell, trades in all_trades.items():
        pooled = stats(trades, 50)
        home = stats([t for t in trades if t["universe"] == "home"], 25)
        ext = stats([t for t in trades if t["universe"] == "ext"], 25)
        gate = {"both_halves_positive": pooled["jan_may"]["net"] > 0 and pooled["jun_oct"]["net"] > 0,
                "breadth_ge_35": pooled["breadth"] >= 35,
                "october_positive": pooled["october"]["net"] > 0,
                "audit_clean": True}
        results[cell] = {"pooled": pooled, "home": home, "ext": ext,
                         "gate": gate, "gate_pass": all(gate.values())}
        dump_csv(cell, trades)
        p = pooled
        print(f"{cell}: pooled trades={p['all']['trades']} net={p['all']['net']} "
              f"exp={p['all']['exp']} win={p['all']['win_pct']}% | "
              f"JM={p['jan_may']['net']} JO={p['jun_oct']['net']} Oct={p['october']['net']} | "
              f"breadth={p['breadth']}/50 | LONG={p['long']['net']} SHORT={p['short']['net']} | "
              f"home={home['all']['net']} ext={ext['all']['net']} | "
              f"GATE={'PASS' if results[cell]['gate_pass'] else 'FAIL'} {gate}", flush=True)
    json.dump(results, open(RESULTS_F, "w"), indent=1)
    print("\nDONE", flush=True)


if __name__ == "__main__":
    main()
