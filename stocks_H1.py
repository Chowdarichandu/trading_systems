#!/usr/bin/env python3
"""LINE H1 — October-first discovery on Chandu's OWN 25 stocks only.
Grid frozen in stocks_H1_frozen.md BEFORE scanning (O1 protocol,
home universe only — no ext, no pooled). Equity cash, LONG/SHORT,
paper only, real Rs0. Provisional per 100 shares, net = gross - Rs40.

Phase 1: October 2026 discovery scan (Oct 1-30, Oct 29/30 from the
validated 1-min aggregation, as in Line O1).
Phase 2: Jan-Sep 2026 validation of the top-2 October cells
(definitions frozen in the plan's Phase-2 addendum before scoring).

Modes: prep | scan | phase2 <cellkey1> [cellkey2] | all
Cell key: T|thr|dir|mode|exit|context  e.g. 10:00|1.0|follow|sig|T125/S050|all
"""
import csv, json, os, sys
from collections import defaultdict
import importlib.util

BASE = "/home/hatch/workspace/trading"
spec = importlib.util.spec_from_file_location("mover", f"{BASE}/stocks_tuning_mover.py")
M = importlib.util.module_from_spec(spec)
_argv = sys.argv
sys.argv = ["mover"]
spec.loader.exec_module(M)
sys.argv = _argv
U = M.U
COST = 40.0
RESULTS_F = f"{BASE}/stocks_H1_results.json"
WHICH = "old"  # home 25 only — no other universe exists in this line

TIMES = ["09:45", "10:00", "10:30", "11:00", "11:30", "12:00", "13:00", "14:00"]
THRS = [0.005, 0.01, 0.015]
DIRS = ["follow", "fade"]
MODES = ["sig", "fixed"]
EXITS = {"T05/S050": (0.5, 0.5), "T10/S050": (1.0, 0.5),
         "T125/S050": (1.25, 0.5), "T125/S065": (1.25, 0.65)}
CONTEXTS = ["all", "below50", "event", "noevent"]
EXTRA_DAYS = ["2026-10-29", "2026-10-30"]

# ---------------------------------------------------------------- prep ----
def agg_5min(sym, which, day):
    """Aggregate the Line-7 1-min cache to 5-min bars for one day.
    Returns raw-format bar dicts (09:15..15:25) or None. (O1 verbatim.)"""
    path = f"{BASE}/data/1min_stocks_oct2026/{which}/{sym}.csv"
    if not os.path.exists(path):
        return None
    buckets = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            ts = r["timestamp"][:16]  # 'YYYY-MM-DD HH:MM'
            if ts[:10] != day:
                continue
            hh, mm = int(ts[11:13]), int(ts[14:16])
            mins = hh * 60 + mm
            b = (mins - (9 * 60 + 15)) // 5
            if b < 0 or b > 74:
                continue
            bt = 9 * 60 + 15 + b * 5
            key = f"{bt // 60:02d}:{bt % 60:02d}"
            o, h, l, c = (float(r["open"]), float(r["high"]),
                          float(r["low"]), float(r["close"]))
            if key in buckets:
                bb = buckets[key]
                bb["high"] = max(bb["high"], h); bb["low"] = min(bb["low"], l)
                bb["close"] = c
            else:
                buckets[key] = {"timestamp": f"{day} {key}:00", "time": key,
                                "open": o, "high": h, "low": l, "close": c}
    if len(buckets) != 75:
        return None
    return [buckets[k] for k in sorted(buckets)]


def build_extra_ctx(ns, which):
    """Validate aggregation on 2026-10-28, then add DAYCTX entries for
    Oct 29/30 built with the head's own construction. (O1 verbatim.)"""
    info = {"agg_check_bars": 0, "agg_mismatch_bars": 0, "added": {}}
    daily_extra = {}  # (sym, day) -> daily dict derived from aggregation
    for sym in ns["SYMBOLS"]:
        cached = ns["DAYCTX"].get((sym, "2026-10-28"))
        agg = agg_5min(sym, which, "2026-10-28")
        if cached and agg:
            cb = {c["time"]: c for c in cached["raw"]}
            for b in agg:
                info["agg_check_bars"] += 1
                c0 = cb.get(b["time"])
                if c0 is None or any(abs(c0[k] - b[k]) > 0.051
                                     for k in ("open", "high", "low", "close")):
                    info["agg_mismatch_bars"] += 1
        spot_daily = {d["date"]: d for d in ns["stocks"][sym][1]}
        for day in EXTRA_DAYS:
            if (sym, day) in ns["DAYCTX"]:
                continue
            raw = agg_5min(sym, which, day)
            if not raw:
                continue
            daily_extra[(sym, day)] = {
                "date": day, "open": raw[0]["open"],
                "high": max(c["high"] for c in raw),
                "low": min(c["low"] for c in raw),
                "close": raw[-1]["close"]}
            prev_day = "2026-10-28" if day == "2026-10-29" else "2026-10-29"
            prev = spot_daily.get(prev_day) or daily_extra.get((sym, prev_day))
            if prev is None:
                continue
            candles = [c for c in raw if c["time"] >= "09:30"]
            or_c = [c for c in raw if c["time"] < "09:30"]
            if not candles or not or_c:
                continue
            orh = max(c["high"] for c in or_c); orl = min(c["low"] for c in or_c)
            bias, _ = ns["bias_of"](prev)
            ns["DAYCTX"][(sym, day)] = {
                "raw": raw, "candles": candles, "orh": orh, "orl": orl,
                "or_width": orh - orl, "day_open": raw[0]["open"],
                "pdh": prev["high"], "pdc": prev["close"], "pdl": prev["low"],
                "bias": bias,
                "event_status": "no_event" if day not in ns["WINDOWS"][sym]
                                else "event_window"}
            info["added"].setdefault(day, []).append(sym)
    return info


def nifty_regime():
    """INV lines' regime map verbatim (stocks_tuning_inv.regime_maps),
    Oct 29/30 extension exactly as Line O1."""
    rows = []
    with open(f"{BASE}/data/progressive/NIFTY/spot_daily.csv") as f:
        for r in csv.DictReader(f):
            try:
                rows.append({"date": r["date"][:10], "close": float(r["close"])})
            except Exception:
                pass
    rows.sort(key=lambda x: x["date"])
    try:
        import urllib.parse
        from fetch_upstox_via_connector import call, candles_df
        keys = json.load(open(f"{BASE}/data/progressive/keys.json"))
        enc = urllib.parse.quote(keys["NIFTY"], safe="")
        df = candles_df(call(f"/v3/historical-candle/{enc}/days/1/2026-10-31/2026-10-26"))
        got = {str(r["timestamp"])[:10]: float(r["close"])
               for _, r in df.iterrows()}
        last = rows[-1]
        if abs(got.get(last["date"], -1) - last["close"]) < 0.51:
            for d in ("2026-10-29", "2026-10-30"):
                if d in got:
                    rows.append({"date": d, "close": got[d]})
            rows.sort(key=lambda x: x["date"])
    except Exception as e:
        print("nifty extend failed:", str(e)[:120], flush=True)
    closes = [d["close"] for d in rows]
    out = {}
    for i, d in enumerate(rows):
        if i == 0:
            continue
        ma50 = sum(closes[i - 50:i]) / 50 if i >= 50 else None
        out[d["date"]] = {"prev_close": closes[i - 1], "ma50": ma50}
    return out, rows[-1]["date"] if rows else None


NIFTY_REG, NIFTY_LAST = None, None
def below50(day):
    r = NIFTY_REG.get(day)
    return bool(r and r["ma50"] is not None and r["prev_close"] <= r["ma50"])

# ------------------------------------------------------------- builders ----
_AUDIT = {"trades": 0, "violations": 0}

def build_cell(ns, sym, day, T, thr, dirmode, mode, tp, sp, pm_override=None):
    ctx = ns["DAYCTX"].get((sym, day))
    if ctx is None:
        return []
    candles = ctx["candles"]
    pm = pm_override if pm_override is not None else M.premove(candles, T)
    if pm is None or abs(pm) < thr:
        return []
    move_dir = 1 if pm > 0 else -1
    want = move_dir if dirmode == "follow" else -move_dir
    trades = []
    def audit(entry_time, sig_time):
        _AUDIT["trades"] += 1
        if entry_time < T:
            _AUDIT["violations"] += 1
        if sig_time is not None and (sig_time < T or entry_time <= sig_time):
            _AUDIT["violations"] += 1
    if mode == "fixed":
        ei = next((i for i, c in enumerate(candles) if c["time"] >= T), None)
        if ei is None:
            return []
        entry = float(candles[ei]["open"])
        er, ep, et, xi, gross = U.replay_plain(candles, ei, want, entry, tp, sp)
        audit(candles[ei]["time"], None)
        trades.append({"date": day, "symbol": sym,
                       "dir": "LONG" if want == 1 else "SHORT",
                       "setup": "FIXED", "leg": "direct", "round": 1,
                       "sig_time": None, "entry_time": candles[ei]["time"],
                       "entry": round(entry, 2), "exit_reason": er,
                       "exit_time": et, "exit": round(ep, 2),
                       "gross": round(gross, 2), "net": round(gross - COST, 2),
                       "event": ctx["event_status"],
                       "premove_pct": round(100 * pm, 3), "meas_time": T})
        return trades
    # sig mode: first accepted V5 signal at/after T, chain cap 2
    start = next((i for i, c in enumerate(candles) if c["time"] >= T), None)
    if start is None:
        return []
    while len(trades) < 2:
        chosen = M.pick(ns, sym, day, ctx, start)
        if chosen is None:
            break
        setup, dirc, sig, idx = chosen
        if idx + 1 >= len(candles):
            break
        sign = 1 if dirc == "CE" else -1
        if sign != want:
            start = idx + 1
            continue
        ei = idx + 1
        entry = float(candles[ei]["open"])
        er, ep, et, xi, gross = U.replay_plain(candles, ei, sign, entry, tp, sp)
        audit(candles[ei]["time"], candles[idx]["time"])
        trades.append({"date": day, "symbol": sym,
                       "dir": "LONG" if sign == 1 else "SHORT",
                       "setup": setup,
                       "leg": "direct" if not trades else "round2",
                       "round": len(trades) + 1,
                       "sig_time": candles[idx]["time"],
                       "entry_time": candles[ei]["time"],
                       "entry": round(entry, 2), "exit_reason": er,
                       "exit_time": et, "exit": round(ep, 2),
                       "gross": round(gross, 2), "net": round(gross - COST, 2),
                       "event": ctx["event_status"],
                       "premove_pct": round(100 * pm, 3), "meas_time": T})
        start = xi
    return trades


def collect_window(days, T, thr, dirmode, mode, tp, sp, lag=False):
    ns = M.get_ns(WHICH)
    all_days = sorted({d for (s, d) in ns["DAYCTX"]})
    prev_of = {d: all_days[i - 1] for i, d in enumerate(all_days) if i > 0}
    out = []
    for sym in ns["SYMBOLS"]:
        for day in days:
            pm_o = None
            if lag:
                pd = prev_of.get(day)
                pctx = ns["DAYCTX"].get((sym, pd)) if pd else None
                if pctx is None:
                    continue
                pm_o = M.premove(pctx["candles"], T)
                if pm_o is None:
                    continue
            out.extend(build_cell(ns, sym, day, T, thr, dirmode, mode, tp, sp,
                                  pm_override=pm_o))
    return out


def ctx_filter(trades, context):
    if context == "all":
        return trades
    if context == "below50":
        return [t for t in trades if below50(t["date"])]
    if context == "event":
        return [t for t in trades if t["event"] == "event_window"]
    return [t for t in trades if t["event"] == "no_event"]


def agg_stats(trades):
    per_stock = defaultdict(float)
    for t in trades:
        per_stock[t["symbol"]] += t["net"]
    return {"trades": len(trades), "net": round(sum(t["net"] for t in trades), 2),
            "breadth": sum(1 for v in per_stock.values() if v > 0),
            "per_stock": {k: round(v, 2) for k, v in per_stock.items()}}

# ---------------------------------------------------------------- modes ----
def load_results():
    return json.load(open(RESULTS_F)) if os.path.exists(RESULTS_F) else {}

def save_results(r):
    json.dump(r, open(RESULTS_F, "w"), indent=1)

def oct_days(ns):
    return sorted({d for (s, d) in ns["DAYCTX"] if d.startswith("2026-10")})

def mode_prep():
    global NIFTY_REG, NIFTY_LAST
    r = load_results()
    ns = M.get_ns(WHICH)
    before = len(oct_days(ns))
    inf = build_extra_ctx(ns, WHICH)
    info = {"home": {"oct_days_before": before, "oct_days_after": len(oct_days(ns)),
                     "agg_check_bars": inf["agg_check_bars"],
                     "agg_mismatch_bars": inf["agg_mismatch_bars"],
                     "added_days": {d: len(v) for d, v in inf["added"].items()}}}
    print(f"PREP home: {info['home']}", flush=True)
    NIFTY_REG, NIFTY_LAST = nifty_regime()
    info["nifty_daily_last"] = NIFTY_LAST
    info["below50_oct"] = {d: below50(d) for d in
                           ["2026-10-28", "2026-10-29", "2026-10-30"]}
    print("PREP nifty:", info["nifty_daily_last"], info["below50_oct"], flush=True)
    r["PREP"] = info
    save_results(r)
    return info

_NS_PREPPED = False
def ensure_prep():
    global _NS_PREPPED, NIFTY_REG, NIFTY_LAST
    if _NS_PREPPED:
        return
    build_extra_ctx(M.get_ns(WHICH), WHICH)
    NIFTY_REG, NIFTY_LAST = nifty_regime()
    _NS_PREPPED = True

def mode_scan():
    ensure_prep()
    r = load_results()
    days = oct_days(M.get_ns(WHICH))
    print("SCAN October days:", days, flush=True)
    grid = {}
    best_family = {}
    for T in TIMES:
        for thr in THRS:
            for dirmode in DIRS:
                for mode in MODES:
                    for exname, (tp, sp) in EXITS.items():
                        trades = collect_window(days, T, thr, dirmode, mode, tp, sp)
                        for context in CONTEXTS:
                            s = agg_stats(ctx_filter(trades, context))
                            key = f"{T}|{thr*100:g}|{dirmode}|{mode}|{exname}|{context}"
                            grid[key] = {"net": s["net"], "trades": s["trades"],
                                         "breadth": s["breadth"]}
                            fam = f"{mode}|{dirmode}"
                            if fam not in best_family or s["net"] > best_family[fam]["net"]:
                                best_family[fam] = {"key": key, **grid[key]}
                    print(f"scan {T} thr={thr:.3%} {dirmode} {mode} done", flush=True)
    r["SCAN"] = {"days": days, "grid": grid, "best_family": best_family,
                 "audit": dict(_AUDIT)}
    save_results(r)
    hits = sorted(((k, v) for k, v in grid.items() if v["net"] >= 50000),
                  key=lambda kv: -kv[1]["net"])
    near = sorted(((k, v) for k, v in grid.items() if v["net"] >= 20000),
                  key=lambda kv: -kv[1]["net"])
    print(f"SCAN done: {len(grid)} cells, HITS(>=50k): {len(hits)}, "
          f"near-zone(>=20k): {len(near)}, audit={_AUDIT}", flush=True)
    for k, v in near:
        print("NEAR", k, v, flush=True)
    for fam, v in best_family.items():
        print("BESTFAM", fam, v["key"], v["net"], flush=True)
    return grid

def parse_key(key):
    T, thr, dirmode, mode, exname, context = key.split("|")
    return T, float(thr) / 100.0, dirmode, mode, exname, context

def run_cell(key, months_prefix, lag=False):
    T, thr, dirmode, mode, exname, context = parse_key(key)
    tp, sp = EXITS[exname]
    ns = M.get_ns(WHICH)
    days = sorted({d for (s, d) in ns["DAYCTX"]
                   if any(d.startswith(m) for m in months_prefix)})
    trades = collect_window(days, T, thr, dirmode, mode, tp, sp, lag=lag)
    return ctx_filter(trades, context)

def month_table(trades, months):
    out = {}
    for m in months:
        sel = [t for t in trades if t["date"].startswith(m)]
        out[m] = {"trades": len(sel), "net": round(sum(t["net"] for t in sel), 2)}
    return out

def mode_phase2(keys):
    ensure_prep()
    r = load_results()
    jan_sep = [f"2026-{i:02d}" for i in range(1, 10)]
    res = {}
    for key in keys:
        sel = run_cell(key, jan_sep)
        mt = month_table(sel, jan_sep)
        jm = round(sum(v["net"] for m, v in mt.items() if m <= "2026-05"), 2)
        js = round(sum(v["net"] for m, v in mt.items() if m >= "2026-06"), 2)
        s = agg_stats(sel)
        oct_sel = run_cell(key, ["2026-10"])
        pbo = run_cell(key, jan_sep, lag=True)
        ps = agg_stats(pbo)
        verdict = {"halves_both_positive": bool(jm > 0 and js > 0),
                   "breadth_ge_15": bool(s["breadth"] >= 15),
                   "placebo_beaten": bool(s["net"] > ps["net"]),
                   "REAL": bool(jm > 0 and js > 0 and s["breadth"] >= 15
                                and s["net"] > ps["net"])}
        res[key] = {"jan_sep": {"trades": s["trades"], "net": s["net"],
                                "breadth": s["breadth"], "months": mt,
                                "jan_may": jm, "jun_sep": js,
                                "exp_per_trade": round(s["net"] / s["trades"], 2)
                                if s["trades"] else None,
                                "per_stock": s["per_stock"]},
                    "oct_recheck": {"trades": len(oct_sel),
                                    "net": round(sum(t["net"] for t in oct_sel), 2)},
                    "placebo_jan_sep": {"trades": ps["trades"], "net": ps["net"],
                                        "breadth": ps["breadth"]},
                    "verdict": verdict}
        print(f"P2 {key}: JanSep net={s['net']} JM={jm} JS={js} "
              f"breadth={s['breadth']}/25 | Oct recheck={res[key]['oct_recheck']} "
              f"| placebo={ps['net']} | verdict={verdict}", flush=True)
        flat = sorted(sel, key=lambda x: (x["date"], x["symbol"]))
        tag = key.replace("|", "_").replace("/", "").replace(":", "")
        with open(f"{BASE}/stocks_H1_P2_{tag}_trades.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(flat[0].keys()) if flat else
                               ["date", "symbol"])
            w.writeheader()
            for t in flat:
                w.writerow(t)
    r["PHASE2"] = {"cells": res, "audit": dict(_AUDIT)}
    save_results(r)
    print("PHASE2 audit:", _AUDIT, flush=True)
    return res

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "scan"
    if mode == "prep":
        mode_prep()
    elif mode == "scan":
        mode_scan()
    elif mode == "phase2":
        mode_phase2(sys.argv[2:])
    else:
        print("unknown mode", mode); sys.exit(1)
    print("DONE", mode, flush=True)
