#!/usr/bin/env python3
"""LINE S4 — Last-hour momentum (Axis A) + VWAP deviation reversion (Axis B).
Cells frozen in stocks_S4_frozen.md BEFORE scoring. CONTROLS-FIRST:
the timing audit (entry strictly after qualifier, by bar index AND by
timestamp; VWAP through signal bar only; placebo level from previous
day only) runs in the SAME run as scoring and aborts the run before
any score is printed if it fails. Equity cash, LONG/SHORT, paper only,
real Rs0. Provisional per 100 shares, net = gross - Rs40/trade.
Window Jan-Oct 2026 as cached (home Oct 1-28; ext Oct 1-30).

Axis A exits: A-MOM-T05 reuses the programme's frozen replay_plain
(stop-first, 15:10 square-off); A-MOM-SQ / A-FADE-SQ exit at the 15:10
bar close. Axis B exits use an absolute target level (signal-bar VWAP,
capped at 0.75%) with a 0.5% stop, stop-first, 15:10 square-off.
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
RESULTS_F = f"{BASE}/stocks_S4_results.json"
UNIV = [("home", "progressive", "progressive_vol", OLD_SYMS),
        ("ext", "progressive_ext", "progressive_vol_ext", EXT_SYMS)]

DEV = 0.015          # Axis B deviation threshold
CAP_PCT = 0.75       # Axis B target cap (%)
STOP_PCT = 0.50      # Axis B stop (%)


def load_days(price_dir, vol_dir, sym):
    """Price bars with volume joined on timestamp. Asserts alignment."""
    days = {}
    with open(f"{BASE}/data/{price_dir}/{sym}/spot_5m.csv") as f:
        for r in csv.DictReader(f):
            d = r["timestamp"][:10]
            days.setdefault(d, []).append(
                {"time": r["timestamp"][11:16], "open": float(r["open"]),
                 "high": float(r["high"]), "low": float(r["low"]),
                 "close": float(r["close"]), "vol": None})
    vol = {}
    with open(f"{BASE}/data/{vol_dir}/{sym}/spot_5m_vol.csv") as f:
        for r in csv.DictReader(f):
            vol[(r["timestamp"][:10], r["timestamp"][11:16])] = float(r["volume"])
    for d, cs in days.items():
        cs.sort(key=lambda c: c["time"])
        for c in cs:
            # Volume cache covers 2026 only; pre-2026 bars get vol=None
            # (those days are never scored; only their final VWAP could
            # serve as a placebo level, and None correctly disables it).
            c["vol"] = vol.get((d, c["time"]))
    return days


def vwap_series(candles):
    """Cumulative intraday VWAP through each bar (bars <= t only).
    None for any bar of a day with missing volume."""
    out, pv, vv, ok = [], 0.0, 0.0, True
    for c in candles:
        if c["vol"] is None:
            ok = False
        if ok:
            tp = (c["high"] + c["low"] + c["close"]) / 3.0
            pv += tp * c["vol"]
            vv += c["vol"]
        out.append(pv / vv if (ok and vv > 0) else None)
    return out


def exit_1510(candles, entry_idx, sign, entry):
    for j in range(entry_idx, len(candles)):
        if candles[j]["time"] == "15:10":
            ep = candles[j]["close"]
            return "square_off", ep, "15:10", 100.0 * sign * (ep - entry)
    c = candles[-1]
    return "square_off", c["close"], c["time"], 100.0 * sign * (c["close"] - entry)


def replay_level(candles, entry_idx, sign, entry, target_px, stop_px):
    """Absolute-level replay, stop-first, 15:10 square-off."""
    for j in range(entry_idx, len(candles)):
        c = candles[j]
        if sign == 1:
            if c["low"] <= stop_px:
                er, ep = "stop", stop_px
            elif c["high"] >= target_px:
                er, ep = "target", target_px
            elif c["time"] == "15:10":
                er, ep = "square_off", c["close"]
            else:
                continue
        else:
            if c["high"] >= stop_px:
                er, ep = "stop", stop_px
            elif c["low"] <= target_px:
                er, ep = "target", target_px
            elif c["time"] == "15:10":
                er, ep = "square_off", c["close"]
            else:
                continue
        return er, ep, c["time"], 100.0 * sign * (ep - entry)
    c = candles[-1]
    return "square_off", c["close"], c["time"], 100.0 * sign * (c["close"] - entry)


# ---------------- Axis A ----------------

def axis_a_day(candles):
    """Returns (move_pct, sig_idx, entry_idx) or None."""
    idx = {c["time"]: k for k, c in enumerate(candles)}
    if "14:30" not in idx or "14:35" not in idx:
        return None
    si, ei = idx["14:30"], idx["14:35"]
    day_open = candles[0]["open"]
    if not day_open:
        return None
    move = candles[si]["close"] / day_open - 1
    if abs(move) < 0.01:
        return None
    return move, si, ei


def run_axis_a(cache):
    trades = {c: [] for c in ("A-MOM-SQ", "A-MOM-T05", "A-FADE-SQ")}
    for univ, _, _, syms in UNIV:
        for sym in syms:
            for date, candles in sorted(cache[(univ, sym)].items()):
                if not (WIN_START <= date <= WIN_END):
                    continue
                q = axis_a_day(candles)
                if q is None:
                    continue
                move, si, ei = q
                sign = 1 if move > 0 else -1
                entry = float(candles[ei]["open"])
                qual = f"day move by 14:30 {100 * move:+.2f}%"
                base = {"universe": univ, "symbol": sym, "date": date,
                        "qualifier": qual, "info_complete": f"{date} 14:30",
                        "entry_dt": f"{date} 14:35", "entry_time": "14:35",
                        "entry": round(entry, 2), "sig_idx": si, "entry_idx": ei}
                # momentum, square-off exit
                er, ep, et, gross = exit_1510(candles, ei, sign, entry)
                trades["A-MOM-SQ"].append({**base, "cell": "A-MOM-SQ",
                    "dir": "LONG" if sign == 1 else "SHORT", "exit_reason": er,
                    "exit_time": et, "exit": round(ep, 2), "gross": round(gross, 2),
                    "net": round(gross - COST, 2)})
                # momentum, T05/S050
                er, ep, et, _j, gross = U.replay_plain(candles, ei, sign, entry, 0.5, 0.5)
                trades["A-MOM-T05"].append({**base, "cell": "A-MOM-T05",
                    "dir": "LONG" if sign == 1 else "SHORT", "exit_reason": er,
                    "exit_time": et, "exit": round(ep, 2), "gross": round(gross, 2),
                    "net": round(gross - COST, 2)})
                # fade control, square-off exit
                er, ep, et, gross = exit_1510(candles, ei, -sign, entry)
                trades["A-FADE-SQ"].append({**base, "cell": "A-FADE-SQ",
                    "dir": "SHORT" if sign == 1 else "LONG", "exit_reason": er,
                    "exit_time": et, "exit": round(ep, 2), "gross": round(gross, 2),
                    "net": round(gross - COST, 2)})
    return trades


# ---------------- Axis B ----------------

def axis_b_day(candles, stale_vwap):
    """First deviation triggers vs live VWAP and vs stale level.
    Returns dict cell -> trade spec (without prices filled)."""
    vw = vwap_series(candles)
    out = {}
    pending = {"B-REV-LONG": ("rev", 1), "B-REV-SHORT": ("rev", -1),
               "B-PBO-LONG": ("pbo", 1), "B-PBO-SHORT": ("pbo", -1)}
    for k, c in enumerate(candles):
        if not pending:
            break
        if c["time"] < "11:00" or c["time"] > "15:05":
            continue
        for cell, (kind, sign) in list(pending.items()):
            level = vw[k] if kind == "rev" else stale_vwap
            if level is None:
                continue
            dev = c["close"] / level - 1
            if (sign == 1 and dev <= -DEV) or (sign == -1 and dev >= DEV):
                out[cell] = {"sig_idx": k, "level": level, "kind": kind,
                             "sign": sign, "dev_pct": round(100 * dev, 3)}
                del pending[cell]
    return out


def run_axis_b(cache):
    cells = ("B-REV-LONG", "B-REV-SHORT", "B-PBO-LONG", "B-PBO-SHORT")
    trades = {c: [] for c in cells}
    skips = {c: 0 for c in cells}
    for univ, _, _, syms in UNIV:
        for sym in syms:
            days = cache[(univ, sym)]
            dates = sorted(days)
            final_vwap = {}
            for d in dates:
                vw = vwap_series(days[d])
                final_vwap[d] = vw[-1] if vw else None
            for i, date in enumerate(dates):
                if not (WIN_START <= date <= WIN_END) or i == 0:
                    continue
                stale = final_vwap[dates[i - 1]]  # None -> placebo cells
                # simply find no level and are skipped inside axis_b_day
                candles = days[date]
                hits = axis_b_day(candles, stale)
                for cell, h in hits.items():
                    ei = h["sig_idx"] + 1
                    if ei >= len(candles):
                        continue
                    entry = float(candles[ei]["open"])
                    level = h["level"]
                    sign = h["sign"]
                    if (sign == 1 and entry >= level) or (sign == -1 and entry <= level):
                        skips[cell] += 1
                        continue
                    cap_px = entry * (1 + sign * CAP_PCT / 100)
                    target = min(level, cap_px) if sign == 1 else max(level, cap_px)
                    stop = entry * (1 - sign * STOP_PCT / 100)
                    er, ep, et, gross = replay_level(candles, ei, sign, entry, target, stop)
                    if h["kind"] == "rev":
                        qual = f"close {h['dev_pct']:+.2f}% vs intraday VWAP {level:.2f}"
                        info = f"{date} {candles[h['sig_idx']]['time']}"
                    else:
                        qual = f"close {h['dev_pct']:+.2f}% vs stale VWAP {level:.2f} ({dates[i-1]})"
                        info = f"{dates[i - 1]} 15:30"
                    trades[cell].append({
                        "cell": cell, "universe": univ, "symbol": sym, "date": date,
                        "dir": "LONG" if sign == 1 else "SHORT", "qualifier": qual,
                        "info_complete": info,
                        "entry_dt": f"{date} {candles[ei]['time']}",
                        "entry_time": candles[ei]["time"], "entry": round(entry, 2),
                        "exit_reason": er, "exit_time": et, "exit": round(ep, 2),
                        "gross": round(gross, 2), "net": round(gross - COST, 2),
                        "sig_idx": h["sig_idx"], "entry_idx": ei,
                        "level": round(level, 2), "target": round(target, 2)})
    return trades, skips


# ---------------- stats / dump / audit ----------------

def stats(trades, total_stocks):
    def block(ts):
        m = U.metrics(ts)
        return {"trades": m["trades"], "net": m["net"], "win_pct": m["win_pct"], "exp": m["exp"]}
    jm = [t for t in trades if t["date"] <= "2026-05-31"]
    jo = [t for t in trades if t["date"] >= "2026-06-01"]
    oc = [t for t in trades if t["date"][:7] == "2026-10"]
    per = defaultdict(float)
    for t in trades:
        per[t["symbol"]] += t["net"]
    exits = defaultdict(int)
    for t in trades:
        exits[t["exit_reason"]] += 1
    return {"all": block(trades), "jan_may": block(jm), "jun_oct": block(jo),
            "october": block(oc),
            "long": block([t for t in trades if t["dir"] == "LONG"]),
            "short": block([t for t in trades if t["dir"] == "SHORT"]),
            "breadth": sum(1 for v in per.values() if v > 0),
            "stocks_total": total_stocks,
            "worst5": sorted(per.items(), key=lambda kv: kv[1])[:5],
            "best5": sorted(per.items(), key=lambda kv: -kv[1])[:5],
            "exits": dict(exits)}


def dump_csv(cell, trades):
    cols = ["cell", "universe", "symbol", "date", "dir", "qualifier",
            "info_complete", "entry_dt", "entry_time", "entry", "exit_time",
            "exit", "exit_reason", "gross", "net"]
    with open(f"{BASE}/stocks_S4_{cell}_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for t in sorted(trades, key=lambda x: (x["date"], x["symbol"])):
            w.writerow({c: t.get(c, "") for c in cols})


def audit(axis, trades):
    bad = []
    for t in trades:
        if not (t["entry_idx"] > t["sig_idx"]):
            bad.append((t, "entry_idx <= sig_idx"))
        if not (t["entry_dt"] > t["info_complete"]):
            bad.append((t, "entry_dt <= info_complete"))
    print(f"AUDIT {axis}: {len(trades)} trades checked, violations = {len(bad)}", flush=True)
    for t in trades[:5]:
        print(f"  sample [{t['cell']}] {t['symbol']} {t['date']} {t['dir']}: "
              f"info_complete={t['info_complete']} -> entry={t['entry_dt']} ({t['qualifier']})",
              flush=True)
    if bad:
        for t, why in bad[:5]:
            print("  VIOLATION:", why, t["cell"], t["symbol"], t["date"], flush=True)
    return bad


def gate_of(pooled):
    return {"both_halves_positive": pooled["jan_may"]["net"] > 0 and pooled["jun_oct"]["net"] > 0,
            "breadth_ge_35": pooled["breadth"] >= 35,
            "october_positive": pooled["october"]["net"] > 0,
            "audit_clean": True}


def main():
    cache = {}
    for univ, pd_, vd, syms in UNIV:
        for sym in syms:
            cache[(univ, sym)] = load_days(pd_, vd, sym)
    print(f"Loaded {len(cache)} stock caches (price+volume joined).", flush=True)

    a_trades = run_axis_a(cache)
    b_trades, b_skips = run_axis_b(cache)

    # ---- CONTROLS-FIRST: audits before any score is printed ----
    bad = []
    bad += audit("AXIS A", [t for ts in a_trades.values() for t in ts])
    bad += audit("AXIS B", [t for ts in b_trades.values() for t in ts])
    if bad:
        print("TIMING AUDIT FAILED — aborting, no scores quoted.", flush=True)
        sys.exit(1)
    print("TIMING AUDIT CLEAN for both axes.\n", flush=True)

    results = {"axis_b_skips_entry_past_level": b_skips}
    for cell, trades in {**a_trades, **b_trades}.items():
        pooled = stats(trades, 50)
        home = stats([t for t in trades if t["universe"] == "home"], 25)
        ext = stats([t for t in trades if t["universe"] == "ext"], 25)
        results[cell] = {"pooled": pooled, "home": home, "ext": ext}
        dump_csv(cell, trades)
        p = pooled
        print(f"{cell}: pooled trades={p['all']['trades']} net={p['all']['net']} "
              f"exp={p['all']['exp']} win={p['all']['win_pct']}% | "
              f"JM={p['jan_may']['net']} JO={p['jun_oct']['net']} Oct={p['october']['net']} | "
              f"breadth={p['breadth']}/50 | LONG={p['long']['net']} SHORT={p['short']['net']} | "
              f"home={home['all']['net']} ext={ext['all']['net']} | exits={p['exits']}", flush=True)

    # ---- gates incl. control legs ----
    ga = gate_of(results["A-MOM-SQ"]["pooled"])
    ga["control_beaten"] = results["A-MOM-SQ"]["pooled"]["all"]["net"] > results["A-FADE-SQ"]["pooled"]["all"]["net"]
    results["A-MOM-SQ"]["gate"] = ga
    results["A-MOM-SQ"]["gate_pass"] = all(ga.values())
    gt = gate_of(results["A-MOM-T05"]["pooled"])
    gt["control_beaten"] = ga["control_beaten"]
    results["A-MOM-T05"]["gate"] = gt
    results["A-MOM-T05"]["gate_pass"] = all(gt.values())

    rev_net = results["B-REV-LONG"]["pooled"]["all"]["net"] + results["B-REV-SHORT"]["pooled"]["all"]["net"]
    pbo_net = results["B-PBO-LONG"]["pooled"]["all"]["net"] + results["B-PBO-SHORT"]["pooled"]["all"]["net"]
    for cell, pbo in (("B-REV-LONG", "B-PBO-LONG"), ("B-REV-SHORT", "B-PBO-SHORT")):
        g = gate_of(results[cell]["pooled"])
        g["control_beaten"] = (results[cell]["pooled"]["all"]["net"] > results[pbo]["pooled"]["all"]["net"]
                               and rev_net > pbo_net)
        results[cell]["gate"] = g
        results[cell]["gate_pass"] = all(g.values())
    results["axis_b_combined"] = {"rev_net": rev_net, "pbo_net": pbo_net}
    print(f"\nGATE A-MOM-SQ: {results['A-MOM-SQ']['gate']} -> {'PASS' if results['A-MOM-SQ']['gate_pass'] else 'FAIL'}", flush=True)
    print(f"GATE A-MOM-T05: {results['A-MOM-T05']['gate']} -> {'PASS' if results['A-MOM-T05']['gate_pass'] else 'FAIL'}", flush=True)
    for cell in ("B-REV-LONG", "B-REV-SHORT"):
        print(f"GATE {cell}: {results[cell]['gate']} -> {'PASS' if results[cell]['gate_pass'] else 'FAIL'}", flush=True)
    print(f"Axis B combined: REV={rev_net} vs PBO={pbo_net}", flush=True)
    json.dump(results, open(RESULTS_F, "w"), indent=1)
    print("\nDONE", flush=True)


if __name__ == "__main__":
    main()
