#!/usr/bin/env python3
"""LINE L1 — LEVEL-NATIVE ENTRIES on Chandu's own 25 stocks.
Spec frozen in stocks_L1_frozen.md BEFORE scoring. Equity cash, LONG/SHORT,
paper only, real Rs0. Provisional per 100 shares, net = gross - Rs40.
HOME 25 only, Jan-Oct 2026 (Oct 29/30 from the validated 1-min aggregation).

Cells: L1-A breakout-retest (PDH/PDL), L1-B level rejection (PDH/PDL),
L1-C first break of 20-day high/low. x exits {T05/S050, T10/S050, T125/S065}
x contexts {all, below50}. Lag-placebo (levels shifted +1 day) and a full
timing audit run IN THE SAME RUN. Re-entry allowed, cap 4 entries/stock/day.
"""
import csv, json, os, sys
from collections import defaultdict
import importlib.util

BASE = "/home/hatch/workspace/trading"
PROG = f"{BASE}/data/progressive"
_spec = importlib.util.spec_from_file_location("univ", f"{BASE}/stocks_tuning_universe.py")
U = importlib.util.module_from_spec(_spec)
_argv = sys.argv; sys.argv = ["univ"]; _spec.loader.exec_module(U); sys.argv = _argv

COST = 40.0
CAP = 4
SYMBOLS = ["GODREJCP", "GLENMARK", "ITC", "RECLTD", "TVSMOTOR", "UNITDSPR",
           "OBEROIRLTY", "NTPC", "INDUSTOWER", "KALYANKJIL", "HDFCBANK", "NHPC",
           "PFC", "IRCTC", "WIPRO", "NATIONALUM", "VEDL", "HINDCOPPER",
           "HINDZINC", "HINDALCO", "TATASTEEL", "ASTRAL", "BDL", "OIL",
           "HINDUNILVR"]
EXTRA_DAYS = ["2026-10-29", "2026-10-30"]
EXITS = {"T05/S050": (0.5, 0.5), "T10/S050": (1.0, 0.5), "T125/S065": (1.25, 0.65)}
CELLS = ["L1-A", "L1-B", "L1-C"]
CONTEXTS = ["all", "below50"]
MONTHS = [f"2026-{i:02d}" for i in range(1, 11)]

# ------------------------------------------------------------ data load ----
def agg_5min(sym, day):
    """Aggregate the 1-min cache to 5-min bars for one day (O1/H1 verbatim)."""
    path = f"{BASE}/data/1min_stocks_oct2026/old/{sym}.csv"
    if not os.path.exists(path):
        return None
    buckets = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            ts = r["timestamp"][:16]
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


def load_symbol(sym):
    """Returns (bars_by_day, daily_rows) with Oct 29/30 bars aggregated and a
    derived daily row for Oct 29 appended (Oct 30's derived row too, unused
    for levels but kept for completeness). Validates the aggregation against
    the cached Oct 28 bars exactly as O1/H1 did."""
    bars = {}
    with open(f"{PROG}/{sym}/spot_5m.csv") as f:
        for r in csv.DictReader(f):
            d = r["timestamp"][:10]
            if not ("2026-01-01" <= d <= "2026-10-30"):
                continue
            bars.setdefault(d, []).append(
                {"timestamp": r["timestamp"][:19], "time": r["timestamp"][11:16],
                 "open": float(r["open"]), "high": float(r["high"]),
                 "low": float(r["low"]), "close": float(r["close"])})
    for d in bars:
        bars[d].sort(key=lambda x: x["timestamp"])
    daily = []
    with open(f"{PROG}/{sym}/spot_daily.csv") as f:
        for r in csv.DictReader(f):
            daily.append({"date": r["date"][:10], "open": float(r["open"]),
                          "high": float(r["high"]), "low": float(r["low"]),
                          "close": float(r["close"])})
    daily.sort(key=lambda x: x["date"])
    info = {"agg_check_bars": 0, "agg_mismatch_bars": 0, "added": []}
    agg28 = agg_5min(sym, "2026-10-28")
    cached28 = {c["time"]: c for c in bars.get("2026-10-28", [])}
    if agg28 and cached28:
        for b in agg28:
            info["agg_check_bars"] += 1
            c0 = cached28.get(b["time"])
            if c0 is None or any(abs(c0[k] - b[k]) > 0.051
                                 for k in ("open", "high", "low", "close")):
                info["agg_mismatch_bars"] += 1
    have_daily = {d["date"] for d in daily}
    for day in EXTRA_DAYS:
        raw = agg_5min(sym, day)
        if raw and day not in bars:
            bars[day] = raw
            info["added"].append(day)
        if raw and day not in have_daily:
            daily.append({"date": day, "open": raw[0]["open"],
                          "high": max(c["high"] for c in raw),
                          "low": min(c["low"] for c in raw),
                          "close": raw[-1]["close"]})
    daily.sort(key=lambda x: x["date"])
    return bars, daily, info


def compute_levels(daily):
    """levels[date] from daily rows strictly before date."""
    out = {}
    for i, d in enumerate(daily):
        if i == 0:
            continue
        prev = daily[i - 1]
        lv = {"pdh": prev["high"], "pdl": prev["low"], "pdc": prev["close"]}
        if i >= 5:
            lv["h5"] = max(x["high"] for x in daily[i - 5:i])
            lv["l5"] = min(x["low"] for x in daily[i - 5:i])
        if i >= 20:
            lv["h20"] = max(x["high"] for x in daily[i - 20:i])
            lv["l20"] = min(x["low"] for x in daily[i - 20:i])
        out[d["date"]] = lv
    return out


def nifty_regime():
    """Line H1's regime construction verbatim (INV lines' map + connector
    extension for Oct 29/30)."""
    rows = []
    with open(f"{PROG}/NIFTY/spot_daily.csv") as f:
        for r in csv.DictReader(f):
            try:
                rows.append({"date": r["date"][:10], "close": float(r["close"])})
            except Exception:
                pass
    rows.sort(key=lambda x: x["date"])
    try:
        import urllib.parse
        from fetch_upstox_via_connector import call, candles_df
        keys = json.load(open(f"{PROG}/keys.json"))
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
    return out, (rows[-1]["date"] if rows else None)


NIFTY_REG = None
def below50(day):
    r = NIFTY_REG.get(day)
    return bool(r and r["ma50"] is not None and r["prev_close"] <= r["ma50"])

# --------------------------------------------------------- cell engines ----
def _mk_trade(sym, day, cell, sign, level_name, level, bars, ei, tp, sp,
              trig_idx, extra):
    entry = float(bars[ei]["open"])
    er, ep, et, xi, gross = U.replay_plain(bars, ei, sign, entry, tp, sp)
    t = {"date": day, "symbol": sym, "cell": cell,
         "dir": "LONG" if sign == 1 else "SHORT", "level_name": level_name,
         "level": round(level, 2), "trig_idx": trig_idx,
         "trig_time": bars[trig_idx]["time"],
         "entry_time": bars[ei]["time"], "entry_idx": ei,
         "entry": round(entry, 2), "exit_reason": er, "exit_time": et,
         "exit_idx": xi, "exit": round(ep, 2),
         "gross": round(gross, 2), "net": round(gross - COST, 2)}
    t.update(extra)
    return t, xi


def sim_A(sym, day, bars, lv, tp, sp):
    """Breakout-retest on PDH (long) / PDL (short)."""
    pdh, pdl = lv["pdh"], lv["pdl"]
    trades = []
    i = 0
    n = len(bars)
    while i < n and len(trades) < CAP:
        # run BOTH state machines from bar i; take the earliest trigger
        found = []
        for sign, level, lname in ((1, pdh, "PDH"), (-1, pdl, "PDL")):
            state, break_idx = "WAIT", None
            j = i
            while j < n:
                c = bars[j]
                if state == "WAIT":
                    if (sign == 1 and c["close"] > level) or \
                       (sign == -1 and c["close"] < level):
                        state, break_idx = "BREAK", j
                else:  # BREAK: invalidation first, then retest
                    if (sign == 1 and c["close"] < level * 0.999) or \
                       (sign == -1 and c["close"] > level * 1.001):
                        state, break_idx = "WAIT", None
                    elif sign == 1 and level * 0.999 <= c["low"] <= level * 1.002 \
                            and c["close"] >= level:
                        found.append((j, sign, lname, level, break_idx))
                        break
                    elif sign == -1 and level * 0.998 <= c["high"] <= level * 1.001 \
                            and c["close"] <= level:
                        found.append((j, sign, lname, level, break_idx))
                        break
                j += 1
        if not found:
            break
        found.sort(key=lambda x: x[0])
        tj, sign, lname, level, bidx = found[0]
        ei = tj + 1
        if ei >= n or bars[ei]["time"] > "15:10":
            break
        t, xi = _mk_trade(sym, day, "L1-A", sign, lname, level, bars, ei, tp,
                          sp, tj, {"break_idx": bidx})
        trades.append(t)
        i = xi + 1
    return trades


def sim_B(sym, day, bars, lv, tp, sp):
    """Level rejection at PDL (long) / PDH (short)."""
    pdh, pdl = lv["pdh"], lv["pdl"]
    trades = []
    i = 0
    n = len(bars)
    while i < n and len(trades) < CAP:
        trig = None
        for j in range(i, n):
            c = bars[j]
            if c["low"] <= pdl * 1.001 and c["close"] > pdl:
                trig = (j, 1, "PDL", pdl)
                break
            if c["high"] >= pdh * 0.999 and c["close"] < pdh:
                trig = (j, -1, "PDH", pdh)
                break
        if trig is None:
            break
        tj, sign, lname, level = trig
        ei = tj + 1
        if ei >= n or bars[ei]["time"] > "15:10":
            break
        t, xi = _mk_trade(sym, day, "L1-B", sign, lname, level, bars, ei, tp,
                          sp, tj, {})
        trades.append(t)
        i = xi + 1
    return trades


def sim_C(sym, day, bars, lv, tp, sp):
    """First intraday break of H20 (long) / L20 (short); breaks are consumed
    for the day even if a position blocks the entry."""
    if "h20" not in lv:
        return []
    h20, l20 = lv["h20"], lv["l20"]
    first = {}  # sign -> bar idx of first break
    for j, c in enumerate(bars):
        up = c["high"] > h20
        dn = c["low"] < l20
        if up and dn:
            first.setdefault(1, None); first.setdefault(-1, None)
            if first[1] is None: first[1] = "both"
            if first[-1] is None: first[-1] = "both"
            continue
        if up and 1 not in first:
            first[1] = j
        if dn and -1 not in first:
            first[-1] = j
    cands = sorted((v, s) for s, v in first.items() if isinstance(v, int))
    trades = []
    free_from = 0  # first bar index at which we are flat (scan position)
    for tj, sign in cands:
        if len(trades) >= CAP:
            break
        if tj < free_from:
            continue  # break occurred inside an open position -> consumed
        ei = tj + 1
        if ei >= len(bars) or bars[ei]["time"] > "15:10":
            continue
        t, xi = _mk_trade(sym, day, "L1-C", sign,
                          "H20" if sign == 1 else "L20",
                          h20 if sign == 1 else l20, bars, ei, tp, sp, tj, {})
        trades.append(t)
        free_from = xi + 1
    return trades


SIMS = {"L1-A": sim_A, "L1-B": sim_B, "L1-C": sim_C}

# ---------------------------------------------------------------- audit ----
def audit_trade(t, bars, lv):
    """Independent re-verification of one trade against re-derived levels.
    Returns a list of violation strings (empty = clean)."""
    v = []
    ei, tj = t["entry_idx"], t["trig_idx"]
    if ei != tj + 1:
        v.append("entry_not_after_trigger")
    if bars[ei]["time"] != t["entry_time"] or abs(bars[ei]["open"] - t["entry"]) > 0.011:
        v.append("entry_price_mismatch")
    if bars[tj]["time"] != t["trig_time"]:
        v.append("trigger_time_mismatch")
    sign = 1 if t["dir"] == "LONG" else -1
    cell = t["cell"]
    if cell == "L1-B":
        if t["level_name"] == "PDL":
            lvl = lv["pdl"]
            c = bars[tj]
            if not (c["low"] <= lvl * 1.001 and c["close"] > lvl):
                v.append("B_trigger_condition")
        else:
            lvl = lv["pdh"]
            c = bars[tj]
            if not (c["high"] >= lvl * 0.999 and c["close"] < lvl):
                v.append("B_trigger_condition")
        if abs(lvl - t["level"]) > 0.011:
            v.append("level_mismatch")
    elif cell == "L1-C":
        lvl = lv["h20"] if t["level_name"] == "H20" else lv["l20"]
        if abs(lvl - t["level"]) > 0.011:
            v.append("level_mismatch")
        for j in range(0, tj):
            c = bars[j]
            if t["level_name"] == "H20" and c["high"] > lvl:
                v.append("C_not_first_break"); break
            if t["level_name"] == "L20" and c["low"] < lvl:
                v.append("C_not_first_break"); break
        c = bars[tj]
        if t["level_name"] == "H20" and not c["high"] > lvl:
            v.append("C_trigger_condition")
        if t["level_name"] == "L20" and not c["low"] < lvl:
            v.append("C_trigger_condition")
    elif cell == "L1-A":
        lvl = lv["pdh"] if t["level_name"] == "PDH" else lv["pdl"]
        if abs(lvl - t["level"]) > 0.011:
            v.append("level_mismatch")
        bi = t.get("break_idx")
        if bi is None or not (0 <= bi < tj):
            v.append("A_break_missing")
        else:
            bc = bars[bi]
            if sign == 1 and not bc["close"] > lvl:
                v.append("A_break_condition")
            if sign == -1 and not bc["close"] < lvl:
                v.append("A_break_condition")
            # no invalidation and no earlier retest between break+1 .. tj-1
            for j in range(bi + 1, tj):
                c = bars[j]
                if sign == 1:
                    if c["close"] < lvl * 0.999:
                        v.append("A_invalidated_before_trigger"); break
                    if lvl * 0.999 <= c["low"] <= lvl * 1.002 and c["close"] >= lvl:
                        v.append("A_earlier_retest"); break
                else:
                    if c["close"] > lvl * 1.001:
                        v.append("A_invalidated_before_trigger"); break
                    if lvl * 0.998 <= c["high"] <= lvl * 1.001 and c["close"] <= lvl:
                        v.append("A_earlier_retest"); break
            c = bars[tj]
            if sign == 1 and not (lvl * 0.999 <= c["low"] <= lvl * 1.002
                                  and c["close"] >= lvl):
                v.append("A_retest_condition")
            if sign == -1 and not (lvl * 0.998 <= c["high"] <= lvl * 1.001
                                   and c["close"] <= lvl):
                v.append("A_retest_condition")
    return v

# ------------------------------------------------------------------ main ---
def stats(trades):
    per_stock = defaultdict(float)
    for t in trades:
        per_stock[t["symbol"]] += t["net"]
    net = round(sum(t["net"] for t in trades), 2)
    return {"trades": len(trades), "net": net,
            "breadth": sum(1 for x in per_stock.values() if x > 0),
            "expectancy": round(net / len(trades), 2) if trades else None,
            "per_stock": {k: round(x, 2) for k, x in sorted(per_stock.items())}}


def month_table(trades):
    out = {}
    green = 0
    for m in MONTHS:
        sel = [t for t in trades if t["date"].startswith(m)]
        net = round(sum(t["net"] for t in sel), 2)
        out[m] = {"trades": len(sel), "net": net}
        if net > 0:
            green += 1
    return out, green


def main():
    global NIFTY_REG
    data = {}
    agg_info = {"check": 0, "mismatch": 0, "added": defaultdict(int)}
    for sym in SYMBOLS:
        bars, daily, info = load_symbol(sym)
        agg_info["check"] += info["agg_check_bars"]
        agg_info["mismatch"] += info["agg_mismatch_bars"]
        for d in info["added"]:
            agg_info["added"][d] += 1
        levels = compute_levels(daily)
        days = sorted(d for d in bars if "2026-01-01" <= d <= "2026-10-30")
        data[sym] = {"bars": bars, "levels": levels, "days": days}
    print("AGG validation:", agg_info["check"], "bars,",
          agg_info["mismatch"], "mismatches; added:", dict(agg_info["added"]),
          flush=True)
    if agg_info["mismatch"]:
        print("ABORT: aggregation mismatch"); sys.exit(1)
    NIFTY_REG, nifty_last = nifty_regime()
    print("NIFTY daily last:", nifty_last,
          "| below50 Oct28/29/30:", [below50(d) for d in
          ("2026-10-28", "2026-10-29", "2026-10-30")], flush=True)

    results = {"agg": {"check_bars": agg_info["check"],
                       "mismatch_bars": agg_info["mismatch"],
                       "added": dict(agg_info["added"])},
               "nifty_daily_last": nifty_last, "cells": {}}
    audit = {"trades": 0, "violations": 0, "violation_kinds": defaultdict(int)}
    best_dump = {}

    for cell in CELLS:
        for exname, (tp, sp) in EXITS.items():
            raw_all, raw_pbo = [], []
            for sym in SYMBOLS:
                d = data[sym]
                days = d["days"]
                prev_of = {days[k]: days[k - 1] for k in range(1, len(days))}
                for day in days:
                    bars = d["bars"][day]
                    lv = d["levels"].get(day)
                    if lv is None:
                        continue
                    ts = SIMS[cell](sym, day, bars, lv, tp, sp)
                    for t in ts:
                        t["placebo"] = False
                    raw_all.extend(ts)
                    # audit real trades (levels re-derived identically here;
                    # levels come from compute_levels over spot_daily.csv)
                    for t in ts:
                        audit["trades"] += 1
                        for kind in audit_trade(t, bars, lv):
                            audit["violations"] += 1
                            audit["violation_kinds"][kind] += 1
                    # sequencing audit per stock-day (real)
                    sd = sorted(ts, key=lambda x: x["entry_idx"])
                    if len(sd) > CAP:
                        audit["violations"] += 1
                        audit["violation_kinds"]["cap_exceeded"] += 1
                    for a, b in zip(sd, sd[1:]):
                        if b["entry_idx"] <= a["exit_idx"]:
                            audit["violations"] += 1
                            audit["violation_kinds"]["overlap"] += 1
                    # placebo: levels of the previous trading day
                    pd = prev_of.get(day)
                    if pd is None:
                        continue
                    plv = d["levels"].get(pd)
                    if plv is None:
                        continue
                    pts = SIMS[cell](sym, day, bars, plv, tp, sp)
                    for t in pts:
                        t["placebo"] = True
                    raw_pbo.extend(pts)
                    for t in pts:
                        audit["trades"] += 1
                        for kind in audit_trade(t, bars, plv):
                            audit["violations"] += 1
                            audit["violation_kinds"]["placebo_" + kind] += 1
            for context in CONTEXTS:
                if context == "below50":
                    sel = [t for t in raw_all if below50(t["date"])]
                    psel = [t for t in raw_pbo if below50(t["date"])]
                else:
                    sel, psel = raw_all, raw_pbo
                s = stats(sel)
                ps = stats(psel)
                mt, green = month_table(sel)
                jm = round(sum(v["net"] for m, v in mt.items() if m <= "2026-05"), 2)
                jo = round(sum(v["net"] for m, v in mt.items() if m >= "2026-06"), 2)
                oct_net = mt["2026-10"]["net"]
                key = f"{cell}|{exname}|{context}"
                gate = {"jan_oct_pos": s["net"] > 0, "jan_may_pos": jm > 0,
                        "jun_oct_pos": jo > 0, "oct_pos": oct_net > 0,
                        "breadth_ge15": s["breadth"] >= 15,
                        "exp_ge100": (s["expectancy"] or -1) >= 100,
                        "beats_placebo": s["net"] > ps["net"]}
                results["cells"][key] = {
                    **s, "jan_may": jm, "jun_oct": jo, "october": oct_net,
                    "months": mt, "months_green": green,
                    "placebo": {"trades": ps["trades"], "net": ps["net"],
                                "breadth": ps["breadth"]},
                    "gate": gate}
                best_dump[key] = sel
                print(f"{key}: net={s['net']} trades={s['trades']} "
                      f"JM={jm} JO={jo} Oct={oct_net} breadth={s['breadth']}/25 "
                      f"exp={s['expectancy']} green={green}/10 "
                      f"placebo={ps['net']}", flush=True)
    results["audit"] = {"trades": audit["trades"],
                        "violations": audit["violations"],
                        "violation_kinds": dict(audit["violation_kinds"])}
    json.dump(results, open(f"{BASE}/stocks_L1_results.json", "w"), indent=1)
    # dump trades of the best cell by Jan-Oct net (for the record)
    best_key = max(results["cells"], key=lambda k: results["cells"][k]["net"])
    flat = sorted(best_dump[best_key],
                  key=lambda x: (x["date"], x["symbol"], x["entry_time"]))
    if flat:
        with open(f"{BASE}/stocks_L1_best_trades.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(flat[0].keys()))
            w.writeheader()
            for t in flat:
                w.writerow(t)
    print("AUDIT:", results["audit"], flush=True)
    print("BEST:", best_key, results["cells"][best_key]["net"], flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
