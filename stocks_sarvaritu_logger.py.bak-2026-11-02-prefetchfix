#!/usr/bin/env python3
"""SARVARITU FORWARD PAPER LOGGER — whole-book live paper test of the
frozen v2 engine book ("SarvaRitu"), Nov-Dec 2026. Spec:
stocks_sarvaritu_forward_spec.md (frozen 2026-10-31, user order 20:36 IST).

The book VERBATIM, post-C24: F4 (T150/S095, first-signal-only) + INV-LONG
(T125/S050) + INV-ABOVE (C22) + N4-V3 (T150/S080) + P2F + P2F-R2 +
R2-LOWBAND + RF-1, with the complete v2 law (mechanism-scoped exclusions
banked at C1/C2/C4/C5/C7/C8/C10/C11/C13/C14/C16/C17/C19, the C23
R2-LOWBAND x UP stand-aside and the C24 INV-LONG x FLAT stand-aside,
labels = REGIME-CLASSIFIER-1). Equity cash LONG/SHORT on the underlying
25 stocks, per 100 shares, Rs40/trade, paper only, real Rs0, NO orders.

Machinery: the audited v2 loader path, parameterised by (data root,
window end) so the CONTROL and LIVE modes run the IDENTICAL code:
  - F4/INV chains: stocks_engine_2025_validation.py sections 2-8 exec'd
    (section 2's head exec is replicated here with the window as a
    parameter; the only other patch is a duplicate-guard on section 4's
    Oct-29/30 NIFTY append, inert when those dates are absent).
  - Event components: the generalised builders from
    stocks_engine_v2_build.py, exec'd from source.
  - INV-ABOVE: the Cycle-22 construction (p2 population + g1 gate pick).
  - v2 law: applied as row filters (deletion cycles are filters; their
    composition is order-free), proven by the control below.

Modes:
  --setup-fwd   copy data/full_hist -> data/sarvaritu_fwd and backfill
                Oct 29/30 2026 (+ any missing recent days) from Upstox.
  --control     build BOTH frozen years from data/full_hist and assert
                per-trade equality with the post-C24 dumps
                (stocks_engine_v2_c24_book{2025,2026}_trades.csv),
                incl. the October 2026 subset (91 tr / +Rs52,696.68) and
                a windowed October rebuild (the live-mode shape).
  --run         live day run: fetch-merge fresh data into the fwd root,
                rebuild the epoch book (epoch 2026-10-26) from the live
                calendar, append unlogged rows dated >= 2026-11-02 to
                stocks_sarvaritu_paper_log.csv, append the day line to
                stocks_sarvaritu_daily_summary.md, print a JSON summary.
"""
import argparse, csv, json, os, shutil, sys, urllib, urllib.parse
from collections import Counter, defaultdict
from datetime import date, timedelta

WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
SYMBOLS = ["GODREJCP", "GLENMARK", "ITC", "RECLTD", "TVSMOTOR", "UNITDSPR",
           "OBEROIRLTY", "NTPC", "INDUSTOWER", "KALYANKJIL", "HDFCBANK",
           "NHPC", "PFC", "IRCTC", "WIPRO", "NATIONALUM", "VEDL",
           "HINDCOPPER", "HINDZINC", "HINDALCO", "TATASTEEL", "ASTRAL",
           "BDL", "OIL", "HINDUNILVR"]
GAP = ["ASTRAL", "BDL", "HINDUNILVR", "OIL"]
COST = 40.0
FULLHIST = f"{WS}/data/full_hist"
FWD = f"{WS}/data/sarvaritu_fwd"
LIVE_CAL = f"{WS}/stocks_sarvaritu_calendar_live.csv"
LOGCSV = f"{WS}/stocks_sarvaritu_paper_log.csv"
SUMMARY_MD = f"{WS}/stocks_sarvaritu_daily_summary.md"
EPOCH_LO = "2026-10-26"        # event-sourcing epoch for the live build
TEST_START = "2026-11-02"      # first loggable trade date
LOG_FIELDS = ["date", "comp", "stock", "dir", "entry_time", "exit", "net", "regime"]

# --- the v2 law (post-C24), from stocks_engine_state.json v2.book_law_added
BASE_EXCL = {"BDL", "VEDL", "HINDZINC", "INDUSTOWER", "KALYANKJIL"}  # INV base
V2_INV_LAW = {"HINDALCO", "UNITDSPR", "TATASTEEL"}   # C4/C5/C19 (INV-LONG) + C22 law
EXCL_V2 = {  # (comp, stock, dir) mechanism-scoped deletions banked in v2
    ("F4", "GLENMARK", "SHORT"),        # C1
    ("N4-V3", "GLENMARK", "SHORT"),     # C1
    ("N4-V3", "BDL", "SHORT"),          # C2
    ("F4", "HDFCBANK", "SHORT"),        # C7
    ("F4", "KALYANKJIL", "LONG"),       # C8
    ("N4-V3", "HINDALCO", "SHORT"),     # C10
    ("N4-V3", "HINDZINC", "LONG"),      # C11
    ("N4-V3", "UNITDSPR", "LONG"),      # C13
    ("N4-V3", "RECLTD", "LONG"),        # C14
    ("N4-V3", "WIPRO", "SHORT"),        # C16
    ("P2F-R2", "KALYANKJIL", "LONG"),   # C17
}

def _log(*a):
    print(" ".join(str(x) for x in a), flush=True)

# =====================================================================
# Machinery loader — one code path for control and live
# =====================================================================
def load_machinery(root, all_hi):
    g = {"__name__": "sarvaritu_machinery", "WS": WS, "SHADOW": root,
         "RAW": root, "COST": COST, "SYMBOLS": SYMBOLS, "GAP": GAP,
         "LOG": [], "log": _log, "csv": csv, "json": json, "os": os,
         "sys": sys, "urllib": urllib, "defaultdict": defaultdict,
         "date": date, "timedelta": timedelta}
    # -- section 2 replicated (validation lines: head exec), window param
    src = open(f"{WS}/stocks_equity_reentry.py").read()
    head = src.split("# ---------- score both modes")[0]
    assert 'BASE = "/home/hatch/workspace/trading/data/progressive"' in head
    assert 'ALL_LO, ALL_HI = "2026-01-01", "2026-10-28"' in head
    head = head.replace('BASE = "/home/hatch/workspace/trading/data/progressive"',
                        f'BASE = "{root}"')
    head = head.replace('ALL_LO, ALL_HI = "2026-01-01", "2026-10-28"',
                        f'ALL_LO, ALL_HI = "2025-01-01", "{all_hi}"')
    NS = {}
    exec(compile(head, "reentry_head_param", "exec"), NS)
    g["NS"] = NS
    g["DAYCTX"] = NS["DAYCTX"]
    g["ALL_DAYS"] = NS["ALL_DAYS"]
    # -- sections 3-8 of the validation file, verbatim except one guard:
    #    section 4 appends Oct 29/30 NIFTY closes fetched live; when the
    #    data root already carries those dates the append would duplicate
    #    them and corrupt the 50DMA series, so skip dates already present.
    vsrc = open(f"{WS}/stocks_engine_2025_validation.py").read()
    i3 = vsrc.index("# 3. OCT 29/30"); i3 = vsrc.rfind("\n# =", 0, i3)
    i9 = vsrc.index("# 9. 2026 CONTROL"); i9 = vsrc.rfind("\n# =", 0, i9)
    sec = vsrc[i3:i9]
    old_append = '        if d in got:\n            nifty_daily.append('
    assert old_append in sec
    sec = sec.replace(old_append,
                      '        if d in got and d not in {x["date"] for x in nifty_daily}:\n'
                      '            nifty_daily.append(')
    exec(compile(sec, "validation_sections_3_8", "exec"), g)
    # -- generalised event machinery from stocks_engine_v2_build.py
    bsrc = open(f"{WS}/stocks_engine_v2_build.py").read()
    j1 = bsrc.index("def load_stock(sym):")
    j2 = bsrc.index("CAL26 = ")
    g["FULLHIST"] = root
    exec(compile(bsrc[j1:j2], "v2_event_machinery", "exec"), g)
    return g

def regime_labels(g):
    """REGIME-CLASSIFIER-1, exactly as frozen (cycle22/24 construction)."""
    NIFTY_REG = g["NIFTY_REG"]
    axis = sorted(d for d in NIFTY_REG if NIFTY_REG[d]["ma50"] is not None)
    L = {}
    for j, d in enumerate(axis):
        if j < 5:
            continue
        pc, m = NIFTY_REG[d]["prev_close"], NIFTY_REG[d]["ma50"]
        s = m - NIFTY_REG[axis[j - 5]]["ma50"]
        L[d] = "UP" if (pc > m and s >= 0) else ("DOWN" if (pc <= m and s <= 0) else "FLAT")
    return L

def _norm(comp, date_, stock, dir_, entry_time, exit_price, net):
    return {"comp": comp, "date": date_, "stock": stock, "dir": dir_,
            "entry_time": entry_time,
            "exit": (round(float(exit_price), 2) if exit_price is not None else None),
            "net": round(float(net), 2)}

def build_base(g, cal_path, lo, hi, days):
    """The six v1 components under v1 law, exit prices re-joined from the
    raw builders (the *_book normalisations drop them; the join keys are
    the books' own identity fields, asserted 1:1)."""
    out = []
    raw095 = g["collect2"](days, g["F4_CFG"], 1.50, 0.95)
    for t in raw095:
        if g["f4_keep"](t):
            out.append(_norm("F4", t["date"], t["symbol"], t["dir"],
                             t["entry_time"], t["exit"], t["net"]))
    inv_raw, _st = g["build_inv"](days)
    for t in inv_raw:
        out.append(_norm("INV-LONG", t["date"], t["stock"], "LONG",
                         t["entry_time"], t["exit_price"], t["net"]))
    cands = g["reaction_candidates"](cal_path, lo, hi)
    # P2F (join exit prices from score_lag lag-1 raws)
    p2f_raw = {(t["date"], t["symbol"], t["direction"], t["net_rs"]): t["exit_price"]
               for t in (g["score_lag"](c, 1) for c in cands
                         if abs(c["reaction_ret_pct"]) >= 2.5) if t}
    for t in g["p2f_book"](cands):
        k = (t["date"], t["stock"], t["dir"], t["net"])
        assert k in p2f_raw, f"P2F exit join failed {k}"
        out.append(_norm("P2F", t["date"], t["stock"], t["dir"],
                         t["entry_time"], p2f_raw[k], t["net"]))
    # P2F-R2 (frozen rows carry exit prices)
    _ge, frozen_r2, book_r2 = g["p2fr2_sets"](cands)
    fr2 = {(t["date"], t["symbol"], t["direction"], t["net_rs"]): t["exit_price"]
           for t in frozen_r2}
    for t in book_r2:
        k = (t["date"], t["stock"], t["dir"], t["net"])
        assert k in fr2, f"P2F-R2 exit join failed {k}"
        out.append(_norm("P2F-R2", t["date"], t["stock"], t["dir"],
                         t["entry_time"], fr2[k], t["net"]))
    # R2-LOWBAND (join from score_lag lag-2 raws on the low band)
    low_c, book_low = g["r2lowband_book"](cands)
    low_raw = {(t["date"], t["symbol"], t["direction"], t["net_rs"]): t["exit_price"]
               for t in (g["score_lag"](c, 2) for c in low_c) if t}
    for t in book_low:
        k = (t["date"], t["stock"], t["dir"], t["net"])
        assert k in low_raw, f"R2-LOWBAND exit join failed {k}"
        out.append(_norm("R2-LOWBAND", t["date"], t["stock"], t["dir"],
                         t["entry_time"], low_raw[k], t["net"]))
    # N4-V3 (join from n4_raw)
    n4r = g["n4_raw"](cal_path, lo, hi)
    n4x = {(t["date"], t["symbol"], t["direction"], t["net"]): t["exit_price"]
           for t in n4r}
    for t in g["n4_book"](n4r):
        k = (t["date"], t["stock"], t["dir"], t["net"])
        assert k in n4x, f"N4 exit join failed {k}"
        out.append(_norm("N4-V3", t["date"], t["stock"], t["dir"],
                         t["entry_time"], n4x[k], t["net"]))
    return out

def build_inv_above(g, days):
    """Cycle-22 construction verbatim: p2 population, g1 gate pick."""
    rows = []
    for sym in g["SYMBOLS"]:
        for day in days:
            rs = g["run_chain"](sym, day, ("PLAIN", 1.25, 0.5))
            for r in rs:
                r["adr"] = g["ADR"].get((sym, day))
            rows.extend(rs)
    pop = [r for r in rows if r["round"] <= 2 and r["entry_time"] < "10:30"
           and (r["adr"] or 0) >= 3.0]
    return [_norm("INV-ABOVE", r["date"], r["stock"], r["direction"],
                  r["entry_time"], r["exit_price"], r["net"])
            for r in pop
            if g["g1"](r["date"]) and r["direction"] == "LONG"
            and not g["wk"](r["date"]) and r["stock"] not in BASE_EXCL
            and r["stock"] not in V2_INV_LAW]

def apply_law(rows, labels):
    out = []
    for t in rows:
        if (t["comp"], t["stock"], t["dir"]) in EXCL_V2:
            continue
        if t["comp"] == "INV-LONG" and t["stock"] in V2_INV_LAW:
            continue
        if t["comp"] == "INV-LONG" and labels.get(t["date"]) == "FLAT":
            continue                                    # C24 stand-aside
        if t["comp"] == "R2-LOWBAND" and labels.get(t["date"]) == "UP":
            continue                                    # C23 stand-aside
        out.append(t)
    return out

def build_book(g, cal_path, lo, hi, days):
    labels = regime_labels(g)
    rows = build_base(g, cal_path, lo, hi, days) + build_inv_above(g, days)
    rows = apply_law(rows, labels)
    for t in rows:
        t["regime"] = labels.get(t["date"], "UNCLASSIFIED")
    return sorted(rows, key=lambda t: (t["date"], t["entry_time"], t["stock"], t["comp"]))

def key5(t):
    return (t["comp"], t["date"], t["stock"], t["dir"], t["entry_time"],
            round(float(t["net"]), 2))

# =====================================================================
# CONTROL — reproduce the post-C24 dumps from data/full_hist
# =====================================================================
def run_control():
    CAL26 = f"{WS}/stock_event_calendar_jan_oct_2026.csv"
    CAL25 = f"{WS}/stock_event_calendar_2025.csv"
    g = load_machinery(FULLHIST, "2026-10-28")
    days = {y: sorted({d for (s, d) in g["DAYCTX"] if d.startswith(y)})
            for y in ("2025", "2026")}
    res = {}
    ok = True
    for yr, cal, lo, hi in (("2025", CAL25, "2025-01-01", "2025-12-31"),
                            ("2026", CAL26, "2026-01-01", "2026-10-28")):
        mine = build_book(g, cal, lo, hi, days[yr])
        dump = [{**r, "net": float(r["net"])}
                for r in csv.DictReader(open(f"{WS}/stocks_engine_v2_c24_book{yr}_trades.csv"))]
        same = Counter(map(key5, mine)) == Counter(map(key5, dump))
        res[yr] = {"mine": [len(mine), round(sum(t["net"] for t in mine), 2)],
                   "dump": [len(dump), round(sum(t["net"] for t in dump), 2)],
                   "per_trade_equal": same}
        ok &= same
        if not same:
            dm = Counter(map(key5, dump)); mm = Counter(map(key5, mine))
            _log(f"CONTROL {yr} DIFFS mine-only: {list((mm - dm).items())[:6]}")
            _log(f"CONTROL {yr} DIFFS dump-only: {list((dm - mm).items())[:6]}")
        _log(f"CONTROL {yr}: mine {res[yr]['mine']} vs dump {res[yr]['dump']} "
             f"per-trade equal: {same}")
    oct_mine = [t for t in build_book(g, CAL26, "2026-01-01", "2026-10-28", days["2026"])
                if t["date"].startswith("2026-10")]
    oct_ok = (len(oct_mine) == 91 and round(sum(t["net"] for t in oct_mine), 2) == 52696.68)
    _log(f"CONTROL October 2026: {len(oct_mine)} tr / "
         f"{round(sum(t['net'] for t in oct_mine), 2)} (target 91 / 52696.68): {oct_ok}")
    ok &= oct_ok
    # windowed rebuild — the live-mode shape (October days only, calendar
    # sourced from late September) must reproduce the same October rows
    days_oct = [d for d in days["2026"] if d.startswith("2026-10")]
    win = [t for t in build_book(g, CAL26, "2026-09-20", "2026-10-28", days_oct)
           if t["date"].startswith("2026-10")]
    win_ok = Counter(map(key5, win)) == Counter(map(key5, oct_mine))
    _log(f"CONTROL windowed-October == full-build October: {win_ok} "
         f"({len(win)} tr)")
    ok &= win_ok
    _log("CONTROL OVERALL:", "PASS" if ok else "FAIL")
    return 0 if ok else 2

# =====================================================================
# Fetch + merge (Upstox via the registered connector; read-only)
# =====================================================================
def fetch_merge(root, frm, to):
    """Append-only merge of fresh 5m + daily bars into the data root.
    Existing dates are NEVER overwritten (history is frozen); only dates
    absent from the root are added. Returns {sym: (max_daily, max_5m)}."""
    import pandas as pd
    from fetch_upstox_via_connector import call, candles_df
    keys = json.load(open(f"{WS}/data/progressive/keys.json"))
    report = {}
    for sym in SYMBOLS + ["NIFTY"]:
        enc = urllib.parse.quote(keys[sym], safe="")
        d5 = f"{root}/{sym}"
        os.makedirs(d5, exist_ok=True)
        # daily
        df = None
        try:
            df = candles_df(call(f"/v3/historical-candle/{enc}/days/1/{to}/{frm}"))
        except Exception:
            df = None
        if df is None or df.empty:
            payload = call(f"/v2/historical-candle/{enc}/day/{to}/{frm}")
            df = candles_df(payload)
        dpath = f"{d5}/spot_daily.csv"
        have = {}
        if os.path.exists(dpath):
            for r in csv.DictReader(open(dpath)):
                have[r["date"][:10]] = r
        if df is not None and not df.empty:
            for _, r in df.iterrows():
                d = str(r["timestamp"])[:10]
                if d not in have:
                    have[d] = {"date": d, "open": r["open"], "high": r["high"],
                               "low": r["low"], "close": r["close"]}
        with open(dpath + ".tmp", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "open", "high", "low", "close"])
            for d in sorted(have):
                r = have[d]
                w.writerow([d, r["open"], r["high"], r["low"], r["close"]])
        os.replace(dpath + ".tmp", dpath)
        # 5-minute
        payload = call(f"/v3/historical-candle/{enc}/minutes/5/{to}/{frm}")
        df5 = candles_df(payload)
        spath = f"{d5}/spot_5m.csv"
        have_dates, lines = set(), []
        if os.path.exists(spath):
            with open(spath) as f:
                rd = csv.reader(f)
                header = next(rd)
                for row in rd:
                    lines.append(row)
                    have_dates.add(row[0][:10])
        else:
            header = ["timestamp", "open", "high", "low", "close"]
        if df5 is not None and not df5.empty:
            d5f = df5.copy()
            d5f["ts"] = (pd.to_datetime(d5f["timestamp"]).dt.tz_localize(None)
                         .dt.strftime("%Y-%m-%d %H:%M:%S") + "+05:30")
            new = [r for _, r in d5f.iterrows() if r["ts"][:10] not in have_dates]
            for r in new:
                lines.append([r["ts"], r["open"], r["high"], r["low"], r["close"]])
            lines.sort(key=lambda x: x[0])
        with open(spath + ".tmp", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(lines)
        os.replace(spath + ".tmp", spath)
        mx_d = max(have) if have else None
        mx_5 = lines[-1][0][:10] if lines else None
        report[sym] = (mx_d, mx_5)
        _log(f"fetch {sym}: daily->{mx_d} 5m->{mx_5}")
    return report

def setup_fwd():
    if os.path.exists(FWD):
        _log(f"fwd root already exists: {FWD}")
    else:
        shutil.copytree(FULLHIST, FWD)
        _log(f"copied {FULLHIST} -> {FWD}")
    rep = fetch_merge(FWD, "2026-10-15", "2026-10-31")
    bad = {s: v for s, v in rep.items()
           if v[0] is None or v[0] < "2026-10-30" or v[1] is None or v[1] < "2026-10-30"}
    _log("SETUP fetch: symbols not reaching 2026-10-30:", bad if bad else "none")
    if not os.path.exists(LOGCSV):
        with open(LOGCSV, "w", newline="") as f:
            csv.writer(f).writerow(LOG_FIELDS)
        _log(f"created {LOGCSV} (header only)")
    if not os.path.exists(SUMMARY_MD):
        with open(SUMMARY_MD, "w") as f:
            f.write("# SarvaRitu forward paper test — daily summary\n"
                    "Frozen book, paper only, real Rs0, provisional per 100 shares, Rs40/trade.\n\n")
        _log(f"created {SUMMARY_MD}")
    return 0 if not bad else 2

# =====================================================================
# LIVE RUN
# =====================================================================
def run_live(target):
    frm = (date.fromisoformat(target) - timedelta(days=16)).isoformat()
    try:
        rep = fetch_merge(FWD, frm, target)
    except Exception as e:
        print(json.dumps({"date": target, "status": "fetch_failed",
                          "error": str(e)[:300]}))
        return 2
    missing = [s for s in SYMBOLS if rep[s][1] is None or rep[s][1] < target]
    nifty_missing = rep["NIFTY"][1] is None or rep["NIFTY"][1] < target
    if nifty_missing or len(missing) >= 20:
        line = (f"- {target} | NO MARKET DATA (nifty_missing={nifty_missing}, "
                f"symbols_missing={len(missing)}) — nothing logged")
        with open(SUMMARY_MD, "a") as f:
            f.write(line + "\n")
        print(json.dumps({"date": target, "status": "no_data",
                          "nifty_missing": nifty_missing,
                          "symbols_missing": missing}))
        return 0
    g = load_machinery(FWD, "2026-12-31")
    days = sorted({d for (s, d) in g["DAYCTX"] if EPOCH_LO <= d <= target})
    book = build_book(g, LIVE_CAL, EPOCH_LO, target, days)
    have = set()
    if os.path.exists(LOGCSV):
        for r in csv.DictReader(open(LOGCSV)):
            have.add((r["date"], r["comp"], r["stock"], r["dir"], r["entry_time"]))
    new = [t for t in book
           if TEST_START <= t["date"] <= target
           and (t["date"], t["comp"], t["stock"], t["dir"], t["entry_time"]) not in have]
    if new:
        with open(LOGCSV, "a", newline="") as f:
            w = csv.writer(f)
            for t in new:
                w.writerow([t["date"], t["comp"], t["stock"], t["dir"],
                            t["entry_time"], t["exit"], t["net"], t["regime"]])
    rows = list(csv.DictReader(open(LOGCSV)))
    day_rows = [t for t in new if t["date"] == target]
    month = target[:7]
    mrows = [r for r in rows if r["date"].startswith(month)]
    mnet = round(sum(float(r["net"]) for r in mrows), 2)
    day_net = round(sum(t["net"] for t in day_rows), 2)
    by_comp = {}
    for t in day_rows:
        by_comp[t["comp"]] = by_comp.get(t["comp"], 0) + 1
    labels = regime_labels(g)
    summary = {"date": target, "status": "ok",
               "regime": labels.get(target, "UNCLASSIFIED"),
               "new_rows_logged": len(new),
               "day_trades": len(day_rows), "day_net": day_net,
               "day_by_comp": by_comp,
               "month": month, "month_trades": len(mrows), "month_net": mnet,
               "data_missing": missing,
               "total_logged": len(rows),
               "total_net": round(sum(float(r["net"]) for r in rows), 2)}
    comp_s = ", ".join(f"{k} {v}" for k, v in sorted(by_comp.items())) or "none"
    miss_s = ", ".join(missing) if missing else "none"
    line = (f"- {target} | regime {summary['regime']} | trades {len(day_rows)} "
            f"({comp_s}) | day net {day_net:+.2f} | {month} running "
            f"{mnet:+.2f} ({len(mrows)} tr) | DATA_MISSING: {miss_s}")
    with open(SUMMARY_MD, "a") as f:
        f.write(line + "\n")
    print(json.dumps(summary))
    return 0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--control", action="store_true")
    ap.add_argument("--setup-fwd", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--date", default=None, help="IST date YYYY-MM-DD (default: today IST)")
    args = ap.parse_args()
    if args.control:
        return run_control()
    if args.setup_fwd:
        return setup_fwd()
    if args.run:
        if args.date:
            target = args.date
        else:
            import pytz
            from datetime import datetime
            target = datetime.now(pytz.timezone("Asia/Kolkata")).date().isoformat()
        return run_live(target)
    ap.print_help()
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
