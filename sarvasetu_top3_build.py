#!/usr/bin/env python3
"""SARVASETU TOP-3 CONVICTION — whole book x 1,081 stocks x NOVEMBER
2026, top-3 highest-conviction stock-days per day (owner design order
2026-11-11 17:56 IST). RETROSPECTIVE paper scoring — NOT live
evidence. Paper only, real money Rs0. Basis: provisional per 100
shares, Rs40/trade.

STEP 1 (candidate pool): the frozen November whole book EXACTLY as the
25-book runs it — stocks_sarvaritu_logger.build_book (v2 engine book
post-C24: F4 + INV-LONG + INV-ABOVE(C22) + N4-V3 + P2F + P2F-R2 +
R2-LOWBAND, v2 law) — parameterised ONLY by universe (the 1,081-name
Sarvasetu universe, wide_nse_universe_2026-11-11.csv), data root
(data/wide1081_nov/ built from the Sarvasetu bar store
screen_work/sarvasetu_bars_octnov, Upstox 5-min bars 2026-09-30 ->
2026-11-11; NIFTY copied from data/sarvaritu_fwd so the regime series
is identical) and event calendar (the Sarvasetu merged machinery
calendar — the same inputs as the 200-wide whole-book run, whose
25-restriction anchor reproduced the frozen paper log trade-for-trade;
the same anchor is re-run here).

STEP 2 (conviction ranking, the owner's rule, mechanical): group the
pool by stock-day. Confluence = number of DISTINCT components flagging
that stock that day. Trigger magnitude % per component, from the
machinery's own signal fields:
  N4-V3      = |09:30 move| — the construction's own signal: the
               09:25-bar close vs prior close, in % (n4_raw's
               move_pct, re-derived from the same STOCKS_E inputs);
  P2F/P2F-R2/R2-LOWBAND = |reaction_ret_pct| of the candidate;
  F4         = |premove_pct| (first move to the 10:00 measure);
  INV-LONG / INV-ABOVE  = the chain machinery exposes NO % magnitude,
               so per the prescribed fallback: the trade's pool rank
               inverted to a percentile within that day's chain pool
               (population: round<=2, entry<10:30, ADR>=3.0 — the
               identical filter both INV constructions draw from),
               pool ordered by the machinery's own preference
               (-setup RANK, earlier entry, symbol, round);
               percentile = 100*(N-rank+1)/N, best rank -> 100.
A stock-day is OWNED by its highest-magnitude component (ties broken
by component name, deterministically); the trade scored is that
component's earliest trade on that stock that day.
Score = confluence*100 + owner magnitude. Rank per day: score desc,
magnitude desc, symbol asc. Take TOP 3 per day; never pad.

Outputs: sarvasetu_top3_november_2026-11-11_trades.csv (the picks),
sarvasetu_top3_november_2026-11-11_pool.csv (the full Step-1 pool with
magnitudes), sarvasetu_top3_november_2026-11-11_summary.json.
"""
import csv, json, os, re, shutil, sys
from collections import Counter, defaultdict

WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_sarvaritu_logger as L

ROOT = f"{WS}/data/wide1081_nov"
BARS = f"{WS}/screen_work/sarvasetu_bars_octnov"
UNIVERSE_CSV = f"{WS}/wide_nse_universe_2026-11-11.csv"
MERGED_CAL = f"{WS}/screen_work/sarvasetu_merged_calendar.csv"
FWD = f"{WS}/data/sarvaritu_fwd"
OUT_CSV = f"{WS}/sarvasetu_top3_november_2026-11-11_trades.csv"
OUT_POOL = f"{WS}/sarvasetu_top3_november_2026-11-11_pool.csv"
OUT_JSON = f"{WS}/sarvasetu_top3_november_2026-11-11_summary.json"
NOV_DAYS = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05",
            "2026-11-06", "2026-11-09", "2026-11-11"]
EPOCH_LO, WIN_HI = "2026-10-26", "2026-11-11"
WATCH25 = L.SYMBOLS
COMPS = ["F4", "INV-LONG", "INV-ABOVE", "N4-V3", "P2F", "P2F-R2", "R2-LOWBAND"]


def universe():
    rdr = csv.DictReader([l for l in open(UNIVERSE_CSV)
                          if not l.startswith("#")])
    return [r["Symbol"] for r in rdr]


SYMS = universe()


def build_root():
    if os.path.exists(ROOT):
        print(f"root exists: {ROOT}", flush=True)
        return
    os.makedirs(ROOT)
    for n, sym in enumerate(SYMS):
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
        if n % 200 == 0:
            print(f"root build {n}/{len(SYMS)}", flush=True)
    shutil.copytree(f"{FWD}/NIFTY", f"{ROOT}/NIFTY")
    print(f"root built: {ROOT} ({len(SYMS)} symbols + NIFTY)", flush=True)


def _log(*a):
    print(" ".join(str(x) for x in a), flush=True)


def load_machinery(root, all_hi):
    """sarvaritu_wholebook_200_build.load_machinery200, generalised to
    the 1,081-name universe (identical parameterisation points)."""
    g = {"__name__": "sarvaritu_machinery", "WS": WS, "SHADOW": root,
         "RAW": root, "COST": L.COST, "SYMBOLS": SYMS, "GAP": L.GAP,
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
    head = head[:sym_block.start()] + f"SYMBOLS = {SYMS!r}" + head[sym_block.end():]
    NS = {}
    exec(compile(head, "reentry_head_param1081", "exec"), NS)
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


# ---------------------------------------------------------------------
# magnitudes
# ---------------------------------------------------------------------
def n4_move_pct(g, sym, day):
    """n4_raw's own signal: (09:25-bar close / prior close - 1) * 100,
    from the same STOCKS_E inputs n4_raw reads."""
    spot, daily = g["STOCKS_E"][sym]
    dmap = {d["date"]: i for i, d in enumerate(daily)}
    i = dmap[day]
    prev_close = daily[i - 1]["close"]
    by_time = {c["time"]: c for c in spot.get(day, [])}
    b = by_time.get("09:25")
    if b is None or not prev_close:
        return None
    return round((b["close"] / prev_close - 1) * 100, 2)


def inv_pool_percentiles(g, days):
    """The day's chain pool (round<=2, entry<10:30, ADR>=3.0 — the
    population both INV constructions draw from), ranked by the
    machinery's own preference (-setup RANK, entry_time, stock,
    round); percentile = 100*(N-rank+1)/N. Returns
    {(date, stock, round, entry_time): percentile}."""
    RANK = g["NS"]["RANK"]
    rows = []
    for sym in g["SYMBOLS"]:
        for day in days:
            rs = g["run_chain"](sym, day, ("PLAIN", 1.25, 0.5))
            for r in rs:
                r["adr"] = g["ADR"].get((sym, day))
            rows.extend(rs)
    pop = [r for r in rows if r["round"] <= 2 and r["entry_time"] < "10:30"
           and (r["adr"] or 0) >= 3.0]
    by_day = defaultdict(list)
    for r in pop:
        by_day[r["date"]].append(r)
    pct = {}
    sizes = {}
    for day, rs in by_day.items():
        rs.sort(key=lambda r: (-RANK.get(r["setup"], 0), r["entry_time"],
                               r["stock"], r["round"]))
        n = len(rs)
        sizes[day] = n
        for i, r in enumerate(rs):
            pct[(r["date"], r["stock"], r["round"], r["entry_time"])] = \
                round(100.0 * (n - i) / n, 2)
    return pct, sizes


# ---------------------------------------------------------------------
# detailed builders (the 200-wide run's, with magnitude capture added;
# trade selection identical to stocks_sarvaritu_logger.build_book)
# ---------------------------------------------------------------------
def build_base_detailed(g, cal_path, lo, hi, days, pct):
    out = []

    def norm(comp, t, stock, dir_, entry, exit_price, exit_reason,
             exit_time, magnitude, mag_kind, extra=None):
        d = {"comp": comp, "date": t["date"], "stock": stock, "dir": dir_,
             "entry_time": t["entry_time"],
             "entry": (round(float(entry), 2) if entry is not None else None),
             "exit": (round(float(exit_price), 2) if exit_price is not None else None),
             "exit_reason": exit_reason, "exit_time": exit_time,
             "net": round(float(t["net"]), 2),
             "magnitude": magnitude, "mag_kind": mag_kind}
        if extra:
            d.update(extra)
        return d

    raw095 = g["collect2"](days, g["F4_CFG"], 1.50, 0.95)
    for t in raw095:
        if g["f4_keep"](t):
            out.append(norm("F4", t, t["symbol"], t["dir"], t["entry"],
                            t["exit"], t["exit_reason"], t["exit_time"],
                            abs(t["premove_pct"]), "first_move_pct"))
    inv_raw, _st = g["build_inv"](days)
    for t in inv_raw:
        p = pct.get((t["date"], t["stock"], t["round"], t["entry_time"]))
        assert p is not None, f"INV-LONG row missing from pool {t}"
        out.append(norm("INV-LONG", t, t["stock"], "LONG", t["entry"],
                        t["exit_price"], t["exit_reason"], t["exit_time"],
                        p, "pool_percentile",
                        {"round": t["round"], "setup": t["setup"]}))
    cands = g["reaction_candidates"](cal_path, lo, hi)
    p2f_raw = {(t["date"], t["symbol"], t["direction"], t["net_rs"]): t
               for t in (g["score_lag"](c, 1) for c in cands
                         if abs(c["reaction_ret_pct"]) >= 2.5) if t}
    for t in g["p2f_book"](cands):
        k = (t["date"], t["stock"], t["dir"], t["net"])
        assert k in p2f_raw, f"P2F exit join failed {k}"
        r = p2f_raw[k]
        out.append(norm("P2F", t, t["stock"], t["dir"], r["entry"],
                        r["exit_price"], r["exit_reason"], r["exit_time"],
                        abs(t["reaction_ret_pct"]), "reaction_pct"))
    _ge, frozen_r2, book_r2 = g["p2fr2_sets"](cands)
    fr2 = {(t["date"], t["symbol"], t["direction"], t["net_rs"]): t
           for t in frozen_r2}
    for t in book_r2:
        k = (t["date"], t["stock"], t["dir"], t["net"])
        assert k in fr2, f"P2F-R2 exit join failed {k}"
        r = fr2[k]
        out.append(norm("P2F-R2", t, t["stock"], t["dir"], r["entry"],
                        r["exit_price"], r["exit_reason"], r["exit_time"],
                        abs(t["reaction_ret_pct"]), "reaction_pct"))
    low_c, book_low = g["r2lowband_book"](cands)
    low_raw = {(t["date"], t["symbol"], t["direction"], t["net_rs"]): t
               for t in (g["score_lag"](c, 2) for c in low_c) if t}
    for t in book_low:
        k = (t["date"], t["stock"], t["dir"], t["net"])
        assert k in low_raw, f"R2-LOWBAND exit join failed {k}"
        r = low_raw[k]
        out.append(norm("R2-LOWBAND", t, t["stock"], t["dir"], r["entry"],
                        r["exit_price"], r["exit_reason"], r["exit_time"],
                        abs(t["reaction_ret_pct"]), "reaction_pct"))
    n4r = g["n4_raw"](cal_path, lo, hi)
    n4x = {(t["date"], t["symbol"], t["direction"], t["net"]): t for t in n4r}
    for t in g["n4_book"](n4r):
        k = (t["date"], t["stock"], t["dir"], t["net"])
        assert k in n4x, f"N4 exit join failed {k}"
        r = n4x[k]
        mv = n4_move_pct(g, t["stock"], t["date"])
        assert mv is not None, f"N4 move missing {k}"
        out.append(norm("N4-V3", t, t["stock"], t["dir"], r["entry"],
                        r["exit_price"], r["exit_reason"], r["exit_time"],
                        abs(mv), "move_0930_pct"))
    return out


def build_inv_above_detailed(g, days, pct):
    rows = []
    for sym in g["SYMBOLS"]:
        for day in days:
            rs = g["run_chain"](sym, day, ("PLAIN", 1.25, 0.5))
            for r in rs:
                r["adr"] = g["ADR"].get((sym, day))
            rows.extend(rs)
    pop = [r for r in rows if r["round"] <= 2 and r["entry_time"] < "10:30"
           and (r["adr"] or 0) >= 3.0]
    out = []
    for r in pop:
        if g["g1"](r["date"]) and r["direction"] == "LONG" \
                and not g["wk"](r["date"]) and r["stock"] not in L.BASE_EXCL \
                and r["stock"] not in L.V2_INV_LAW:
            p = pct.get((r["date"], r["stock"], r["round"], r["entry_time"]))
            assert p is not None, f"INV-ABOVE row missing from pool {r}"
            out.append({"comp": "INV-ABOVE", "date": r["date"],
                        "stock": r["stock"], "dir": r["direction"],
                        "entry_time": r["entry_time"], "entry": r["entry"],
                        "exit": r["exit_price"],
                        "exit_reason": r["exit_reason"],
                        "exit_time": r["exit_time"],
                        "net": round(float(r["net"]), 2),
                        "magnitude": p, "mag_kind": "pool_percentile",
                        "round": r["round"], "setup": r["setup"]})
    return out


def build_book_detailed(g, cal_path, lo, hi, days, pct):
    labels = L.regime_labels(g)
    rows = build_base_detailed(g, cal_path, lo, hi, days, pct) + \
        build_inv_above_detailed(g, days, pct)
    rows = L.apply_law(rows, labels)
    for t in rows:
        t["regime"] = labels.get(t["date"], "UNCLASSIFIED")
    return sorted(rows, key=lambda t: (t["date"], t["entry_time"],
                                       t["stock"], t["comp"]))


def key5(t):
    return (t["comp"], t["date"], t["stock"], t["dir"], t["entry_time"],
            round(float(t["net"]), 2))


def agg(trades):
    n = len(trades)
    net = round(sum(t["net"] for t in trades), 2)
    wins = sum(1 for t in trades if t["net"] > 0)
    return {"trades": n, "net": net,
            "win_rate": (round(100.0 * wins / n, 1) if n else 0.0)}


def extop3(trades):
    per = defaultdict(float)
    for t in trades:
        per[t["stock"]] += t["net"]
    top3 = sorted(per.items(), key=lambda kv: -kv[1])[:3]
    ex = round(sum(t["net"] for t in trades
                   if t["stock"] not in {k for k, _ in top3}), 2)
    return ex, [(k, round(v, 2)) for k, v in top3]


def main():
    build_root()
    print("loading machinery (1081 symbols)...", flush=True)
    g = load_machinery(ROOT, WIN_HI)
    days = [d for d in NOV_DAYS if any(dd == d for (_s, dd) in g["DAYCTX"])]
    print("build days (in DAYCTX):", days, flush=True)

    print("building INV pool percentiles...", flush=True)
    pct, pool_sizes = inv_pool_percentiles(g, days)
    print("pool sizes per day:", pool_sizes, flush=True)

    print("production build (fidelity reference)...", flush=True)
    prod = L.build_book(g, MERGED_CAL, EPOCH_LO, WIN_HI, days)
    print("detailed build...", flush=True)
    mine = build_book_detailed(g, MERGED_CAL, EPOCH_LO, WIN_HI, days, pct)
    prod_nov = [t for t in prod if t["date"] in NOV_DAYS]
    pool = [t for t in mine if t["date"] in NOV_DAYS]
    fidelity = Counter(map(key5, prod_nov)) == Counter(map(key5, pool))
    print(f"FIDELITY production==detailed on Nov days: {fidelity} "
          f"({len(prod_nov)} vs {len(pool)} rows)", flush=True)
    other_days = [t for t in mine if t["date"] not in NOV_DAYS]
    print("rows outside the 7 Nov days:", [(t["date"], t["comp"], t["stock"],
          t["net"]) for t in other_days], flush=True)

    # anchor: restrict to the frozen 25, compare with the frozen paper log
    log_rows = list(csv.DictReader(open(L.LOGCSV)))
    log_nov = [r for r in log_rows if r["date"] in NOV_DAYS]
    mine25 = [t for t in pool if t["stock"] in WATCH25]
    lk = Counter((r["comp"], r["date"], r["stock"], r["dir"], r["entry_time"],
                  round(float(r["net"]), 2)) for r in log_nov)
    mk = Counter(map(key5, mine25))
    anchor = {"log": [len(log_nov), round(sum(float(r["net"]) for r in log_nov), 2)],
              "mine25": [len(mine25), round(sum(t["net"] for t in mine25), 2)],
              "equal": lk == mk,
              "mine_only": [list(k) for k in (mk - lk).elements()],
              "log_only": [list(k) for k in (lk - mk).elements()]}
    print("ANCHOR 25-restriction vs paper log:", json.dumps(anchor), flush=True)

    # ---------------- STEP 2: conviction ranking ----------------
    by_sd = defaultdict(list)          # (date, stock) -> pool trades
    for t in pool:
        by_sd[(t["date"], t["stock"])].append(t)
    ranked_days = {}
    for day in days:
        sds = []
        for (d, stock), ts in by_sd.items():
            if d != day:
                continue
            by_comp = defaultdict(list)
            for t in ts:
                by_comp[t["comp"]].append(t)
            comp_mag, comp_rep = {}, {}
            for comp, cts in by_comp.items():
                rep = sorted(cts, key=lambda t: (t["entry_time"],
                                                 t.get("round", 0)))[0]
                comp_rep[comp] = rep
                comp_mag[comp] = rep["magnitude"]
            owner = sorted(comp_mag.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
            mag = comp_mag[owner]
            sds.append({"date": day, "stock": stock,
                        "confluence": len(by_comp),
                        "components": sorted(by_comp),
                        "comp_mag": comp_mag, "owner": owner,
                        "magnitude": mag, "score": len(by_comp) * 100 + mag,
                        "trade": comp_rep[owner]})
        sds.sort(key=lambda s: (-s["score"], -s["magnitude"], s["stock"]))
        for i, s in enumerate(sds):
            s["rank"] = i + 1
        ranked_days[day] = sds
    picks = []
    for day in days:
        picks.extend(ranked_days[day][:3])

    # ---------------- coverage / NOT_COMPUTED ----------------
    coverage = {}
    for day in NOV_DAYS:
        usable = 0
        for sym in SYMS:
            src = json.load(open(f"{BARS}/{sym}.json"))
            if len(src.get(day, [])) >= 50:
                usable += 1
        coverage[day] = {"usable": usable, "universe": len(SYMS)}
    # event-active (symbol, day) pairs for November, Sarvasetu convention
    from datetime import date as _date, timedelta as _td
    SINGLE_NEWS = {"management_change", "large_order", "fda_approval",
                   "block_deal", "sector_policy", "pricing",
                   "corporate_action"}
    active = set()
    for c in g["reaction_candidates"](MERGED_CAL, EPOCH_LO, WIN_HI):
        _spot, daily = g["STOCKS_E"][c["symbol"]]
        for lag in (1, 2):
            if c["ri"] + lag < len(daily):
                dd = daily[c["ri"] + lag]["date"]
                if dd in NOV_DAYS:
                    active.add((c["symbol"], dd))
    for r in csv.DictReader(open(MERGED_CAL)):
        sym = r["stock"]
        if sym not in SYMS:
            continue
        et = r["event_type"]
        if et != "results" and et not in SINGLE_NEWS:
            continue
        if not r["event_date"]:
            continue
        ev = _date.fromisoformat(r["event_date"][:10])
        react = _date.fromisoformat(r["reaction_date"][:10]) \
            if r["reaction_date"] else None
        eff = react if (react and ev <= react <= ev + _td(days=7)) else ev
        ds = eff.isoformat()
        if ds in NOV_DAYS:
            active.add((sym, ds))
    nc_active = []
    store_cache = {}
    for sym, day in sorted(active):
        if sym not in store_cache:
            store_cache[sym] = json.load(open(f"{BARS}/{sym}.json"))
        if len(store_cache[sym].get(day, [])) < 50:
            nc_active.append({"symbol": sym, "date": day,
                              "bars": len(store_cache[sym].get(day, []))})
    print("coverage:", json.dumps(coverage), flush=True)
    print("event-active pairs:", len(active), "NOT_COMPUTED:", nc_active,
          flush=True)

    # ---------------- outputs ----------------
    pfields = ["date", "comp", "stock", "dir", "entry_time", "entry",
               "exit", "exit_time", "exit_reason", "net", "regime",
               "magnitude", "mag_kind"]
    with open(OUT_POOL, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=pfields)
        w.writeheader()
        for t in pool:
            w.writerow({k: t.get(k) for k in pfields})

    tfields = ["date", "rank", "stock", "comp", "dir", "confluence",
               "components", "trigger_pct", "mag_kind", "score",
               "entry_time", "entry", "exit_time", "exit", "exit_reason",
               "net", "regime"]
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=tfields)
        w.writeheader()
        for s in sorted(picks, key=lambda s: (s["date"], s["rank"])):
            t = s["trade"]
            w.writerow({"date": s["date"], "rank": s["rank"],
                        "stock": s["stock"], "comp": s["owner"],
                        "dir": t["dir"], "confluence": s["confluence"],
                        "components": "+".join(s["components"]),
                        "trigger_pct": s["magnitude"],
                        "mag_kind": t["mag_kind"], "score": round(s["score"], 2),
                        "entry_time": t["entry_time"], "entry": t["entry"],
                        "exit_time": t["exit_time"], "exit": t["exit"],
                        "exit_reason": t["exit_reason"], "net": t["net"],
                        "regime": t["regime"]})

    ex3_pool, top3_pool = extop3(pool)
    summary = {
        "universe": len(SYMS), "days": days,
        "fidelity": fidelity, "anchor": anchor,
        "other_day_rows": [{k: t[k] for k in ("date", "comp", "stock", "dir", "net")}
                           for t in other_days],
        "pool_total": agg(pool), "pool_ex_top3": ex3_pool,
        "pool_top3_stocks": top3_pool,
        "pool_per_comp": {c: agg([t for t in pool if t["comp"] == c])
                          for c in COMPS},
        "pool_per_day": {d: agg([t for t in pool if t["date"] == d])
                         for d in NOV_DAYS},
        "pool_stock_days_per_day": {d: len(ranked_days.get(d, []))
                                    for d in NOV_DAYS},
        "inv_pool_sizes": pool_sizes,
        "top3_total": agg([s["trade"] for s in picks]),
        "picks": [{"date": s["date"], "rank": s["rank"], "stock": s["stock"],
                   "owner": s["owner"], "confluence": s["confluence"],
                   "components": s["components"],
                   "comp_mag": s["comp_mag"],
                   "magnitude": s["magnitude"], "score": round(s["score"], 2),
                   "dir": s["trade"]["dir"],
                   "entry_time": s["trade"]["entry_time"],
                   "entry": s["trade"]["entry"], "exit": s["trade"]["exit"],
                   "exit_time": s["trade"]["exit_time"],
                   "exit_reason": s["trade"]["exit_reason"],
                   "net": s["trade"]["net"],
                   "mag_kind": s["trade"]["mag_kind"],
                   "regime": s["trade"]["regime"]} for s in picks],
        "ranked_days": {d: [{"rank": s["rank"], "stock": s["stock"],
                             "owner": s["owner"],
                             "confluence": s["confluence"],
                             "components": s["components"],
                             "magnitude": s["magnitude"],
                             "score": round(s["score"], 2),
                             "net": s["trade"]["net"]}
                            for s in ranked_days.get(d, [])]
                        for d in NOV_DAYS},
        "coverage": coverage, "nc_active": nc_active,
        "labels": {d: L.regime_labels(g).get(d) for d in NOV_DAYS},
    }
    with open(OUT_JSON, "w") as f:
        json.dump(summary, f, indent=1, default=str)
    print(json.dumps({k: summary[k] for k in
                      ("pool_total", "pool_ex_top3", "pool_top3_stocks",
                       "pool_per_comp", "pool_per_day", "top3_total",
                       "pool_stock_days_per_day")}, indent=1, default=str),
          flush=True)
    print("PICKS:")
    for s in sorted(picks, key=lambda s: (s["date"], s["rank"])):
        print(f"  {s['date']} #{s['rank']} {s['stock']} {s['owner']} "
              f"conf={s['confluence']} mag={s['magnitude']} "
              f"score={round(s['score'],2)} net={s['trade']['net']}",
              flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
