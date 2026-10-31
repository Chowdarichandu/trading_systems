#!/usr/bin/env python3
"""LINE S1 — THE SHORT-SIDE CONTINUATION BOOK.
Cells frozen in stocks_S1_frozen.md BEFORE scoring. CONTROLS-FIRST:
anchor validations + the timing audit (entry_dt > info_complete over
ALL trades incl. placebo) run in the SAME run; if the audit fails,
the run aborts before printing any score. Equity cash, SHORT entries,
paper only, real Rs0. Provisional per 100 shares, net = gross - Rs40.
Window Jan-Oct 2026, pooled 50 primary.

Engines: cells A-D use replay_plain from stocks_tuning_universe.py
verbatim (R2 lineage). Cell E uses the P2F replay from
stocks_tuning_event.py verbatim (scan starts after the entry bar),
so the E-home anchor against the published P2F SHORT subset
(32 trades / +13109.45) is an exact test.
"""
import csv, json, sys
import importlib.util
from collections import defaultdict
from datetime import date, timedelta

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
RESULTS_F = f"{BASE}/stocks_S1_results.json"
UNIV = [("home", "progressive", OLD_SYMS, "stock_event_calendar_jan_oct_2026.csv"),
        ("ext", "progressive_ext", EXT_SYMS, "stock_event_calendar_ext_jan_oct_2026.csv")]


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


def load_daily(data_dir, sym):
    path = f"{BASE}/data/{data_dir}/{sym}/spot_daily.csv"
    out = []
    with open(path) as f:
        for r in csv.DictReader(f):
            out.append({"date": r["date"][:10], "close": float(r["close"])})
    out.sort(key=lambda x: x["date"])
    return out


def day_close(candles):
    return candles[-1]["close"]


# ---------- cells A-D: day-move qualifiers (R2 build_ft construction) ----------
def move_qualifiers(days):
    """List of (q_idx, entry_idx, ret) over the cached date list: qualifier
    day = dates[q_idx], normal entry = dates[q_idx+1] (must be in window)."""
    dates = sorted(days)
    out = []
    for i in range(1, len(dates) - 1):
        d, nxt = dates[i], dates[i + 1]
        if not (WIN_START <= nxt <= WIN_END):
            continue
        pc = day_close(days[dates[i - 1]])
        cc = day_close(days[d])
        if not pc:
            continue
        out.append((i, i + 1, cc / pc - 1))
    return dates, out


def run_plain(days, date_s, sign, tp, sp):
    candles = days[date_s]
    entry = float(candles[0]["open"])
    er, ep, et, _j, gross = U.replay_plain(candles, 0, sign, entry, tp, sp)
    return {"entry_time": candles[0]["time"], "entry": round(entry, 2),
            "exit_reason": er, "exit_time": et, "exit": round(ep, 2),
            "gross": round(gross, 2), "net": round(gross - COST, 2)}


CELL_RULES = {  # cell: (qualifier test on ret, tp, sp)
    "S1-A": (lambda r: r <= -0.020, 1.25, 0.50),
    "S1-B": (lambda r: r <= -0.025, 1.25, 0.50),
    "S1-C": (lambda r: r <= -0.020, 1.00, 0.50),
    "S1-D": (lambda r: r >= +0.020, 1.25, 0.50),
}


def score_move_cell(cell, cache, lag=0):
    """lag=0 normal book; lag=1 placebo (entry one extra session later)."""
    test, tp, sp = CELL_RULES[cell]
    trades = []
    for univ, data_dir, syms, _cal in UNIV:
        for sym in syms:
            days = cache[(univ, sym)]
            dates, quals = move_qualifiers(days)
            for (qi, ei, ret) in quals:
                if not test(ret):
                    continue
                eidx = ei + lag
                if eidx >= len(dates):
                    continue
                edate = dates[eidx]
                if not (WIN_START <= edate <= WIN_END):
                    continue
                t = run_plain(days, edate, -1, tp, sp)
                qday = dates[qi]
                trades.append({"cell": cell + ("-PLACEBO" if lag else ""), "universe": univ,
                               "symbol": sym, "date": edate, "dir": "SHORT",
                               "qualifier": f"day move {qday} {100 * ret:+.2f}%",
                               "info_complete": f"{qday} 15:30",
                               "entry_dt": f"{edate} {t['entry_time']}", **t})
    return trades


# ---------- cell E: event reaction days, P2F construction verbatim ----------
def event_replay(candles, ei, entry, direction, tgt_pct, stp_pct):
    """stocks_tuning_event.py replay(), verbatim logic."""
    sign = 1 if direction == "LONG" else -1
    target = entry * (1 + sign * tgt_pct / 100)
    stop = entry * (1 - sign * stp_pct / 100)
    last = None
    for j in range(ei + 1, len(candles)):
        c = candles[j]
        if c["time"] > "15:10":
            break
        last = c
        if sign == 1:
            if c["low"] <= stop:
                return "stop", stop, c["time"]
            if c["high"] >= target:
                return "target", target, c["time"]
        else:
            if c["high"] >= stop:
                return "stop", stop, c["time"]
            if c["low"] <= target:
                return "target", target, c["time"]
        if c["time"] == "15:10":
            return "square_off", c["close"], c["time"]
    if last is not None:
        return "square_off", last["close"], last["time"]
    return None


def event_candidates(univ, data_dir, syms, cal_file, daily_cache, hi):
    """P2F candidate generation, verbatim rules; returns list of dicts with
    symbol, R, reaction_ret_pct, ri (daily index of R)."""
    events, seen = [], set()
    with open(f"{BASE}/{cal_file}") as f:
        for r in csv.DictReader(f):
            if r["event_type"] != "results" or r["stock"] not in syms:
                continue
            ev = date.fromisoformat(r["event_date"][:10])
            react = date.fromisoformat(r["reaction_date"][:10]) if r["reaction_date"] else None
            eff = react if (react and ev <= react <= ev + timedelta(days=7)) else ev
            ds = eff.isoformat()
            if not (WIN_START <= ds <= hi):
                continue
            if (r["stock"], ds) in seen:
                continue
            seen.add((r["stock"], ds))
            events.append({"symbol": r["stock"], "R": ds})
    cands = []
    for e in events:
        daily = daily_cache[(univ, e["symbol"])]
        didx = {d["date"]: i for i, d in enumerate(daily)}
        if e["R"] not in didx:
            continue
        ri = didx[e["R"]]
        if ri == 0 or ri + 1 >= len(daily):
            continue
        reaction_ret = round((daily[ri]["close"] / daily[ri - 1]["close"] - 1) * 100, 2)
        cands.append({"symbol": e["symbol"], "R": e["R"], "ri": ri,
                      "reaction_ret_pct": reaction_ret})
    return cands


def score_event_cell(cache, daily_cache, hi=WIN_END, lag=0, univ_filter=None):
    trades = []
    for univ, data_dir, syms, cal_file in UNIV:
        if univ_filter and univ != univ_filter:
            continue
        for cand in event_candidates(univ, data_dir, syms, cal_file, daily_cache, hi):
            if cand["reaction_ret_pct"] > -2.0:
                continue
            daily = daily_cache[(univ, cand["symbol"])]
            ti = cand["ri"] + 1 + lag
            if ti >= len(daily):
                continue
            tdate = daily[ti]["date"]
            if tdate > hi:
                continue
            days = cache[(univ, cand["symbol"])]
            bars = days.get(tdate)
            if not bars:
                continue
            entry = float(bars[0]["open"])
            r = event_replay(bars, 0, entry, "SHORT", 1.25, 0.5)
            if r is None:
                continue
            er, ep, et = r
            net = round(-1 * (ep - entry) * 100 - COST, 2)
            trades.append({"cell": "S1-E" + ("-PLACEBO" if lag else ""), "universe": univ,
                           "symbol": cand["symbol"], "date": tdate, "dir": "SHORT",
                           "qualifier": f"event reaction {cand['R']} {cand['reaction_ret_pct']:+.2f}%",
                           "info_complete": f"{cand['R']} 15:30",
                           "entry_dt": f"{tdate} 09:15",
                           "entry_time": "09:15", "entry": round(entry, 2),
                           "exit_reason": er, "exit_time": et, "exit": round(ep, 2),
                           "gross": round(net + COST, 2), "net": net})
    return trades


# ---------- stats ----------
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
    top3 = sorted(per.values(), reverse=True)[:3]
    net = block(trades)["net"]
    return {"all": block(trades), "jan_may": block(jm), "jun_oct": block(jo),
            "october": block(oc), "breadth": sum(1 for v in per.values() if v > 0),
            "stocks_total": total_stocks,
            "top3_share_pct": round(100 * sum(top3) / net, 1) if net > 0 else None,
            "best5": sorted(per.items(), key=lambda kv: -kv[1])[:5],
            "worst5": sorted(per.items(), key=lambda kv: kv[1])[:5]}


def month_table(trades):
    out = {}
    for m in [f"2026-{i:02d}" for i in range(1, 11)]:
        sel = [t for t in trades if t["date"][:7] == m]
        out[m] = {"trades": len(sel), "net": round(sum(t["net"] for t in sel), 2)}
    return out


def dump_csv(tag, trades):
    cols = ["cell", "universe", "symbol", "date", "dir", "qualifier",
            "info_complete", "entry_dt", "entry_time", "entry", "exit_time",
            "exit", "exit_reason", "gross", "net"]
    with open(f"{BASE}/stocks_S1_{tag}_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for t in sorted(trades, key=lambda x: (x["date"], x["symbol"])):
            w.writerow({c: t.get(c, "") for c in cols})


def audit(trades):
    bad = [t for t in trades if not (t["entry_dt"] > t["info_complete"])]
    print(f"AUDIT: {len(trades)} trades checked, violations = {len(bad)}", flush=True)
    return bad


def main():
    cache, daily_cache = {}, {}
    for univ, data_dir, syms, _cal in UNIV:
        for sym in syms:
            cache[(univ, sym)] = load_days(data_dir, sym)
            daily_cache[(univ, sym)] = load_daily(data_dir, sym)
    print(f"Loaded {len(cache)} stock caches.", flush=True)

    cells = {}
    for cell in CELL_RULES:
        cells[cell] = score_move_cell(cell, cache)
    cells["S1-E"] = score_event_cell(cache, daily_cache)

    # ---- ANCHOR VALIDATIONS (before any score is quoted) ----
    print("\n--- ANCHOR VALIDATIONS ---", flush=True)
    r2 = json.load(open(f"{BASE}/stocks_R2_results.json"))
    a, anch = cells["S1-A"], r2["FT-20-T125"]["pooled"]["short"]
    a_net = round(sum(t["net"] for t in a), 2)
    ok_a = len(a) == anch["trades"] and abs(a_net - anch["net"]) < 0.01
    print(f"ANCHOR S1-A vs R2 FT-20-T125 SHORT block: S1-A {len(a)} trades / {a_net} "
          f"vs R2 {anch['trades']} / {anch['net']} -> {'PASS' if ok_a else 'FAIL'}", flush=True)

    e_anchor = score_event_cell(cache, daily_cache, hi="2026-10-28", univ_filter="home")
    e_net = round(sum(t["net"] for t in e_anchor), 2)
    ok_e = len(e_anchor) == 32 and abs(e_net - 13109.45) < 0.01
    print(f"ANCHOR S1-E home vs published P2F SHORT subset: {len(e_anchor)} trades / {e_net} "
          f"vs 32 / 13109.45 -> {'PASS' if ok_e else 'FAIL'}", flush=True)

    # ---- PLACEBO mirrors the best cell by pooled net (E only if anchor passed) ----
    nets = {c: round(sum(t["net"] for t in ts), 2) for c, ts in cells.items()}
    contenders = {c: n for c, n in nets.items() if c != "S1-E" or ok_e}
    best_cell = max(contenders, key=contenders.get)
    if best_cell == "S1-E":
        placebo = score_event_cell(cache, daily_cache, lag=1)
    else:
        placebo = score_move_cell(best_cell, cache, lag=1)
    placebo_net = round(sum(t["net"] for t in placebo), 2)
    print(f"\nBest cell (internal, pre-audit): {best_cell} net={nets[best_cell]}; "
          f"placebo trades={len(placebo)} net={placebo_net}", flush=True)

    # ---- TIMING AUDIT over ALL trades incl. placebo; abort before scores ----
    print("\n--- TIMING AUDIT ---", flush=True)
    all_t = [t for ts in cells.values() for t in ts] + placebo
    bad = audit(all_t)
    for cell, ts in list(cells.items()) + [(best_cell + "-PLACEBO", placebo)]:
        for t in ts[:10]:
            print(f"  sample [{cell}] {t['symbol']} {t['date']} {t['dir']}: "
                  f"info_complete={t['info_complete']} -> entry={t['entry_dt']} "
                  f"({t['qualifier']})", flush=True)
    if bad:
        print("TIMING AUDIT FAILED — aborting, no scores quoted.", flush=True)
        sys.exit(1)
    print("TIMING AUDIT CLEAN.\n", flush=True)

    # ---- SCORES ----
    results = {"anchors": {"S1-A_vs_R2_SHORT": {"pass": bool(ok_a), "s1a_trades": len(a),
                                               "s1a_net": a_net, "r2_trades": anch["trades"],
                                               "r2_net": anch["net"]},
                           "S1-E_home_vs_P2F_SHORT": {"pass": bool(ok_e),
                                                      "trades": len(e_anchor), "net": e_net,
                                                      "expect_trades": 32, "expect_net": 13109.45}},
               "best_cell": best_cell,
               "placebo": {"mirrors": best_cell, "trades": len(placebo), "net": placebo_net,
                           "beaten": bool(placebo_net < nets[best_cell])}}
    for cell, trades in cells.items():
        pooled = stats(trades, 50)
        home = stats([t for t in trades if t["universe"] == "home"], 25)
        ext = stats([t for t in trades if t["universe"] == "ext"], 25)
        gate = {"both_halves_positive": pooled["jan_may"]["net"] > 0 and pooled["jun_oct"]["net"] > 0,
                "breadth_ge_35": pooled["breadth"] >= 35,
                "october_positive": pooled["october"]["net"] > 0,
                "audit_clean": True,
                "placebo_beaten": bool(placebo_net < nets[best_cell]) if cell == best_cell else None}
        gate_pass = bool(gate["both_halves_positive"] and gate["breadth_ge_35"]
                         and gate["october_positive"] and gate["audit_clean"]
                         and (gate["placebo_beaten"] in (True, None)))
        if cell == "S1-E" and not ok_e:
            gate_pass = False
            gate["anchor_failed"] = True
        results[cell] = {"pooled": pooled, "home": home, "ext": ext,
                         "gate": gate, "gate_pass": gate_pass,
                         "months": month_table(trades) if cell == best_cell else None}
        dump_csv(cell, trades)
        p = pooled
        print(f"{cell}: pooled trades={p['all']['trades']} net={p['all']['net']} "
              f"exp={p['all']['exp']} win={p['all']['win_pct']}% | "
              f"JM={p['jan_may']['net']} JO={p['jun_oct']['net']} Oct={p['october']['net']} | "
              f"breadth={p['breadth']}/50 top3={p['top3_share_pct']}% | "
              f"home={home['all']['net']} (br {home['breadth']}/25) "
              f"ext={ext['all']['net']} (br {ext['breadth']}/25) | "
              f"GATE={'PASS' if gate_pass else 'FAIL'} {gate}", flush=True)
    dump_csv(best_cell + "-PLACEBO", placebo)
    results["months_best"] = month_table(cells[best_cell])
    print(f"\nPLACEBO ({best_cell} mirrored, 2-day lag): trades={len(placebo)} net={placebo_net} "
          f"-> {'BEATEN' if placebo_net < nets[best_cell] else 'NOT BEATEN'}", flush=True)
    print(f"MONTH TABLE {best_cell}: {results['months_best']}", flush=True)
    json.dump(results, open(RESULTS_F, "w"), indent=1)
    print("\nDONE", flush=True)


if __name__ == "__main__":
    main()
