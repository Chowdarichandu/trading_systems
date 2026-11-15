#!/usr/bin/env python3
"""SARVARITU WHOLE BOOK x 200 STOCKS x NOVEMBER 2026 — retrospective
paper scoring (owner order 2026-11-11 17:49 IST). NOT live evidence.

Construction: the frozen November whole book EXACTLY as the 25-book
runs it — stocks_sarvaritu_logger.py's build_book (v2 engine book
post-C24: F4 + INV-LONG + INV-ABOVE(C22) + N4-V3 + P2F + P2F-R2 +
R2-LOWBAND, v2 law) — with ONLY these parameterisations:
  * SYMBOLS: the Nifty 200 list (wide200_universe_2026-11-11.csv)
  * data root: data/wide200_nov/ — per-symbol spot_5m.csv +
    spot_daily.csv built from the Sarvasetu bar store
    (screen_work/sarvasetu_bars_octnov, Upstox 5-min bars
    2026-09-30 -> 2026-11-11; daily aggregated from the day's bars,
    the same aggregation the logger's fetch layer uses);
    NIFTY copied wholesale from data/sarvaritu_fwd (the root the
    live logger itself uses) so the regime series is identical.
  * calendar: the Sarvasetu merged machinery calendar
    (screen_work/sarvasetu_merged_calendar.csv — union of live /
    ext / jan-oct calendars, live precedence), the same event
    input the Sarvasetu November subset used.
  * epoch/window: lo = 2026-10-26 (the logger's live epoch),
    build days = the seven November trading days.
Fidelity: the production build_book's net multiset is asserted
equal to this script's detailed build (same keys), and a
25-watchlist restriction is run as an anchor against the frozen
paper log (26 trades / +Rs8,391.28).
Money basis: provisional per 100 shares, Rs40/trade, paper only.
Outputs: sarvaritu_wholebook_200_november_2026-11-11_trades.csv
+ sarvaritu_wholebook_200_summary.json (the .md is written from it).
"""
import csv, json, os, re, shutil, sys
from collections import Counter, defaultdict

WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_sarvaritu_logger as L

ROOT = f"{WS}/data/wide200_nov"
BARS = f"{WS}/screen_work/sarvasetu_bars_octnov"
UNIVERSE_CSV = f"{WS}/wide200_universe_2026-11-11.csv"
MERGED_CAL = f"{WS}/screen_work/sarvasetu_merged_calendar.csv"
FWD = f"{WS}/data/sarvaritu_fwd"
OUT_CSV = f"{WS}/sarvaritu_wholebook_200_november_2026-11-11_trades.csv"
OUT_JSON = f"{WS}/sarvaritu_wholebook_200_summary.json"
NOV_DAYS = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05",
            "2026-11-06", "2026-11-09", "2026-11-11"]
EPOCH_LO, WIN_HI = "2026-10-26", "2026-11-11"
WATCH25 = L.SYMBOLS


def universe():
    syms = []
    for i, line in enumerate(open(UNIVERSE_CSV)):
        if i < 3:
            continue
        parts = line.rstrip("\n").split(",")
        if len(parts) >= 3 and parts[2].strip():
            syms.append(parts[2].strip())
    return syms


SYMS200 = universe()


def build_root():
    if os.path.exists(ROOT):
        print(f"root exists: {ROOT}")
        return
    os.makedirs(ROOT)
    for sym in SYMS200:
        src = json.load(open(f"{BARS}/{sym}.json"))
        d5 = f"{ROOT}/{sym}"
        os.makedirs(d5)
        rows5, daily = [], {}
        for day in sorted(k for k in src if k.startswith("2026-")):
            bars = sorted(src[day], key=lambda b: b["timestamp"])
            if not bars:
                continue
            for b in bars:
                rows5.append([f"{b['timestamp']}+05:30", b["open"], b["high"],
                              b["low"], b["close"]])
            daily[day] = {"date": day, "open": bars[0]["open"],
                          "high": max(b["high"] for b in bars),
                          "low": min(b["low"] for b in bars),
                          "close": bars[-1]["close"]}
        with open(f"{d5}/spot_5m.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["timestamp", "open", "high", "low", "close"])
            w.writerows(rows5)
        with open(f"{d5}/spot_daily.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "open", "high", "low", "close"])
            for day in sorted(daily):
                d = daily[day]
                w.writerow([d["date"], d["open"], d["high"], d["low"], d["close"]])
    shutil.copytree(f"{FWD}/NIFTY", f"{ROOT}/NIFTY")
    print(f"root built: {ROOT} ({len(SYMS200)} symbols + NIFTY)")


def _log(*a):
    print(" ".join(str(x) for x in a), flush=True)


def load_machinery200(root, all_hi):
    """stocks_sarvaritu_logger.load_machinery, verbatim except the
    SYMBOLS block of the reentry head is also parameterised (the
    logger's own patches: BASE root + ALL_LO/ALL_HI window; plus the
    validation duplicate-guard, identical)."""
    g = {"__name__": "sarvaritu_machinery", "WS": WS, "SHADOW": root,
         "RAW": root, "COST": L.COST, "SYMBOLS": SYMS200, "GAP": L.GAP,
         "LOG": [], "log": _log, "csv": csv, "json": json, "os": os,
         "sys": sys, "urllib": __import__("urllib"),
         "defaultdict": defaultdict,
         "date": __import__("datetime").date,
         "timedelta": __import__("datetime").timedelta}
    src = open(f"{WS}/stocks_equity_reentry.py").read()
    head = src.split("# ---------- score both modes")[0]
    assert 'BASE = "/home/hatch/workspace/trading/data/progressive"' in head
    assert 'ALL_LO, ALL_HI = "2026-01-01", "2026-10-28"' in head
    head = head.replace('BASE = "/home/hatch/workspace/trading/data/progressive"',
                        f'BASE = "{root}"')
    head = head.replace('ALL_LO, ALL_HI = "2026-01-01", "2026-10-28"',
                        f'ALL_LO, ALL_HI = "2026-09-01", "{all_hi}"')
    sym_block = re.search(r'SYMBOLS = \[[^\]]*\]', head)
    assert sym_block, "SYMBOLS block not found in head"
    head = head[:sym_block.start()] + f"SYMBOLS = {SYMS200!r}" + head[sym_block.end():]
    NS = {}
    exec(compile(head, "reentry_head_param200", "exec"), NS)
    g["NS"] = NS
    g["DAYCTX"] = NS["DAYCTX"]
    g["ALL_DAYS"] = NS["ALL_DAYS"]
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
    bsrc = open(f"{WS}/stocks_engine_v2_build.py").read()
    j1 = bsrc.index("def load_stock(sym):")
    j2 = bsrc.index("CAL26 = ")
    g["FULLHIST"] = root
    exec(compile(bsrc[j1:j2], "v2_event_machinery", "exec"), g)
    return g


def build_base_detailed(g, cal_path, lo, hi, days):
    """The logger's build_base, field-for-field, but retaining
    entry / exit_reason / exit_time from the raw builders."""
    out = []

    def norm(comp, t, stock, dir_, entry, exit_price, exit_reason, exit_time):
        return {"comp": comp, "date": t["date"], "stock": stock, "dir": dir_,
                "entry_time": t["entry_time"],
                "entry": (round(float(entry), 2) if entry is not None else None),
                "exit": (round(float(exit_price), 2) if exit_price is not None else None),
                "exit_reason": exit_reason, "exit_time": exit_time,
                "net": round(float(t["net"]), 2)}

    raw095 = g["collect2"](days, g["F4_CFG"], 1.50, 0.95)
    for t in raw095:
        if g["f4_keep"](t):
            out.append(norm("F4", t, t["symbol"], t["dir"], t["entry"],
                            t["exit"], t["exit_reason"], t["exit_time"]))
    inv_raw, _st = g["build_inv"](days)
    for t in inv_raw:
        out.append(norm("INV-LONG", t, t["stock"], "LONG", t["entry"],
                        t["exit_price"], t["exit_reason"], t["exit_time"]))
    cands = g["reaction_candidates"](cal_path, lo, hi)
    p2f_raw = {(t["date"], t["symbol"], t["direction"], t["net_rs"]): t
               for t in (g["score_lag"](c, 1) for c in cands
                         if abs(c["reaction_ret_pct"]) >= 2.5) if t}
    for t in g["p2f_book"](cands):
        k = (t["date"], t["stock"], t["dir"], t["net"])
        assert k in p2f_raw, f"P2F exit join failed {k}"
        r = p2f_raw[k]
        out.append(norm("P2F", t, t["stock"], t["dir"], r["entry"],
                        r["exit_price"], r["exit_reason"], r["exit_time"]))
    _ge, frozen_r2, book_r2 = g["p2fr2_sets"](cands)
    fr2 = {(t["date"], t["symbol"], t["direction"], t["net_rs"]): t
           for t in frozen_r2}
    for t in book_r2:
        k = (t["date"], t["stock"], t["dir"], t["net"])
        assert k in fr2, f"P2F-R2 exit join failed {k}"
        r = fr2[k]
        out.append(norm("P2F-R2", t, t["stock"], t["dir"], r["entry"],
                        r["exit_price"], r["exit_reason"], r["exit_time"]))
    low_c, book_low = g["r2lowband_book"](cands)
    low_raw = {(t["date"], t["symbol"], t["direction"], t["net_rs"]): t
               for t in (g["score_lag"](c, 2) for c in low_c) if t}
    for t in book_low:
        k = (t["date"], t["stock"], t["dir"], t["net"])
        assert k in low_raw, f"R2-LOWBAND exit join failed {k}"
        r = low_raw[k]
        out.append(norm("R2-LOWBAND", t, t["stock"], t["dir"], r["entry"],
                        r["exit_price"], r["exit_reason"], r["exit_time"]))
    n4r = g["n4_raw"](cal_path, lo, hi)
    n4x = {(t["date"], t["symbol"], t["direction"], t["net"]): t for t in n4r}
    for t in g["n4_book"](n4r):
        k = (t["date"], t["stock"], t["dir"], t["net"])
        assert k in n4x, f"N4 exit join failed {k}"
        r = n4x[k]
        out.append(norm("N4-V3", t, t["stock"], t["dir"], r["entry"],
                        r["exit_price"], r["exit_reason"], r["exit_time"]))
    return out


def build_inv_above_detailed(g, days):
    """The logger's build_inv_above (Cycle-22), retaining detail."""
    rows = []
    for sym in g["SYMBOLS"]:
        for day in days:
            rs = g["run_chain"](sym, day, ("PLAIN", 1.25, 0.5))
            for r in rs:
                r["adr"] = g["ADR"].get((sym, day))
            rows.extend(rs)
    pop = [r for r in rows if r["round"] <= 2 and r["entry_time"] < "10:30"
           and (r["adr"] or 0) >= 3.0]
    return [{"comp": "INV-ABOVE", "date": r["date"], "stock": r["stock"],
             "dir": r["direction"], "entry_time": r["entry_time"],
             "entry": r["entry"], "exit": r["exit_price"],
             "exit_reason": r["exit_reason"], "exit_time": r["exit_time"],
             "net": round(float(r["net"]), 2)}
            for r in pop
            if g["g1"](r["date"]) and r["direction"] == "LONG"
            and not g["wk"](r["date"]) and r["stock"] not in L.BASE_EXCL
            and r["stock"] not in L.V2_INV_LAW]


def build_book_detailed(g, cal_path, lo, hi, days):
    labels = L.regime_labels(g)
    rows = build_base_detailed(g, cal_path, lo, hi, days) + \
        build_inv_above_detailed(g, days)
    rows = L.apply_law(rows, labels)
    for t in rows:
        t["regime"] = labels.get(t["date"], "UNCLASSIFIED")
    return sorted(rows, key=lambda t: (t["date"], t["entry_time"], t["stock"], t["comp"]))


def key5(t):
    return (t["comp"], t["date"], t["stock"], t["dir"], t["entry_time"],
            round(float(t["net"]), 2))


def agg(trades):
    n = len(trades)
    net = round(sum(t["net"] for t in trades), 2)
    wins = sum(1 for t in trades if t["net"] > 0)
    return {"trades": n, "net": net,
            "win_rate": (round(100.0 * wins / n, 1) if n else 0.0)}


def main():
    build_root()
    g = load_machinery200(ROOT, WIN_HI)
    days = [d for d in NOV_DAYS if any(dd == d for (_s, dd) in g["DAYCTX"])]
    print("build days (in DAYCTX):", days)

    # production build (fidelity reference) + detailed build
    prod = L.build_book(g, MERGED_CAL, EPOCH_LO, WIN_HI, days)
    mine = build_book_detailed(g, MERGED_CAL, EPOCH_LO, WIN_HI, days)
    prod_nov = [t for t in prod if t["date"] in NOV_DAYS]
    mine_nov = [t for t in mine if t["date"] in NOV_DAYS]
    fidelity = Counter(map(key5, prod_nov)) == Counter(map(key5, mine_nov))
    print(f"FIDELITY production==detailed on Nov days: {fidelity} "
          f"({len(prod_nov)} vs {len(mine_nov)} rows)")
    other_days = [t for t in mine if t["date"] not in NOV_DAYS]
    print("rows outside the 7 Nov days:", [(t["date"], t["comp"], t["stock"],
          t["net"]) for t in other_days])

    # anchor: restrict to the frozen 25 and compare with the paper log
    log_rows = list(csv.DictReader(open(L.LOGCSV)))
    log_nov = [r for r in log_rows if r["date"] in NOV_DAYS]
    mine25 = [t for t in mine_nov if t["stock"] in WATCH25]
    lk = Counter((r["comp"], r["date"], r["stock"], r["dir"], r["entry_time"],
                  round(float(r["net"]), 2)) for r in log_nov)
    mk = Counter(map(key5, mine25))
    anchor = {"log": [len(log_nov), round(sum(float(r["net"]) for r in log_nov), 2)],
              "mine25": [len(mine25), round(sum(t["net"] for t in mine25), 2)],
              "equal": lk == mk,
              "mine_only": [list(k) for k in (mk - lk).elements()],
              "log_only": [list(k) for k in (lk - mk).elements()]}
    print("ANCHOR 25-restriction vs paper log:", json.dumps(anchor))

    # coverage from the bar store (>=50 usable bars = usable, Sarvasetu rule)
    coverage, nc_active = {}, {}
    cal_rows = list(csv.DictReader(open(MERGED_CAL)))
    for day in NOV_DAYS:
        usable = 0
        for sym in SYMS200:
            src = json.load(open(f"{BARS}/{sym}.json"))
            if len(src.get(day, [])) >= 50:
                usable += 1
        coverage[day] = {"usable": usable, "universe": len(SYMS200)}
    # event-active names whose machinery inputs fall in November
    actives = set()
    for t in mine:
        actives.add(t["stock"])
    for day in NOV_DAYS:
        bad = []
        for sym in actives:
            src = json.load(open(f"{BARS}/{sym}.json"))
            if len(src.get(day, [])) < 50:
                bad.append(sym)
        if bad:
            nc_active[day] = bad

    fields = ["date", "comp", "stock", "dir", "entry_time", "entry",
              "exit", "exit_time", "exit_reason", "net", "regime"]
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for t in mine_nov:
            w.writerow({k: t.get(k) for k in fields})

    comps = ["F4", "INV-LONG", "INV-ABOVE", "N4-V3", "P2F", "P2F-R2", "R2-LOWBAND"]
    summary = {
        "universe": len(SYMS200), "days": NOV_DAYS,
        "total": agg(mine_nov),
        "per_comp": {c: agg([t for t in mine_nov if t["comp"] == c]) for c in comps},
        "per_day": {d: agg([t for t in mine_nov if t["date"] == d]) for d in NOV_DAYS},
        "best": max(mine_nov, key=lambda t: t["net"], default=None),
        "worst": min(mine_nov, key=lambda t: t["net"], default=None),
        "fidelity": fidelity, "anchor": anchor,
        "other_day_rows": [{k: t[k] for k in ("date", "comp", "stock", "dir", "net")}
                           for t in other_days],
        "coverage": coverage, "nc_active": nc_active,
        "labels": {d: L.regime_labels(g).get(d) for d in NOV_DAYS},
        "trades": mine_nov,
    }
    with open(OUT_JSON, "w") as f:
        json.dump(summary, f, indent=1, default=str)
    print(json.dumps({k: summary[k] for k in
                      ("total", "per_comp", "per_day", "fidelity", "coverage")},
                     indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
