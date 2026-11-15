#!/usr/bin/env python3
"""Stocks tuning session 2026-11-10 — STOCKS-EVE-18 / 19 / 20.
Target flaw: RSI-STOCKS-010 (INV-ABOVE flat 0.50% stop inside one-bar noise).
Owner-directed ("start tuning", 2026-11-10); market holiday — historical only.
Candidates REGISTERED in november_rsi_candidates.md BEFORE this scoring run.

EVE-18: INV-ABOVE stop = max(0.50%, opening-range width %) — chain-faithful.
EVE-19: INV-ABOVE re-entry delay >=3 bars after a stop exit — chain-faithful.
EVE-20: INV-ABOVE drop entries whose stock's prior day moved >= +4.0% (drop
        filter on stored rows, EVE-16/17 precedent).
Incumbent: frozen SarvaRitu book, c24 dumps (whole-book transplant: variants
replace the book's INV-ABOVE rows; other components untouched).
Machinery: validation sections 2-8 exec'd exactly as stocks_engine_v2_build.py
execs them (data root = data/full_hist), giving run_chain / DAYCTX / ADR /
NIFTY_REG / g1 / cond_inv1 verbatim. Paper only, Rs0. Equity cash, home 25,
provisional per 100 shares, Rs40/trade.
"""
import csv, json, os, sys, urllib.request
from collections import defaultdict
from datetime import date, timedelta

WS = "/home/hatch/workspace/trading"
FULLHIST = f"{WS}/data/full_hist"
SHADOW = FULLHIST
RAW = FULLHIST
OUTD = f"{WS}/v2_out"
os.makedirs(OUTD, exist_ok=True)
sys.path.insert(0, WS)

SYMBOLS = ["GODREJCP", "GLENMARK", "ITC", "RECLTD", "TVSMOTOR", "UNITDSPR",
           "OBEROIRLTY", "NTPC", "INDUSTOWER", "KALYANKJIL", "HDFCBANK",
           "NHPC", "PFC", "IRCTC", "WIPRO", "NATIONALUM", "VEDL",
           "HINDCOPPER", "HINDZINC", "HINDALCO", "TATASTEEL", "ASTRAL",
           "BDL", "OIL", "HINDUNILVR"]
GAP = ["ASTRAL", "BDL", "HINDUNILVR", "OIL"]
COST = 40.0
LOG = []
def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print(s, flush=True)

_vsrc = open(f"{WS}/stocks_engine_2025_validation.py").read()
_i2 = _vsrc.index("# 2. REENTRY HEAD"); _i2 = _vsrc.rfind("\n# =", 0, _i2)
_i8 = _vsrc.index("# 8. HELPERS");     _i8 = _vsrc.rfind("\n# =", 0, _i8)
_i9 = _vsrc.index("# 9. 2026 CONTROL"); _i9 = _vsrc.rfind("\n# =", 0, _i9)
exec(compile(_vsrc[_i2:_i8], "validation_sections_2_7", "exec"), globals())
exec(compile(_vsrc[_i8:_i9], "validation_section_8_helpers", "exec"), globals())
log("machinery loaded: DAYCTX/run_chain/ADR/NIFTY_REG/g1 OK")

EXCL5 = {"BDL", "VEDL", "HINDZINC", "INDUSTOWER", "KALYANKJIL"}
# v2 INV law (cycle 22, CH-V2-9 construction): the book's INV components
# exclude these names on top of the base exclusions. Reproduction attempt 1
# (base exclusions only) rebuilt a superset whose ONLY extras were law names
# (2025: TATASTEEL 04-21, HINDALCO 04-24; 2026: TATASTEEL 02-10 x2, 02-12) —
# attempt 2 applies the documented law.
V2_LAW = {"HINDALCO", "UNITDSPR", "TATASTEEL"}
def wk(d):
    return date.fromisoformat(d).weekday() >= 5

# ---------------------------------------------------------------- stored book
def load_book(yr):
    rows = list(csv.DictReader(open(f"{WS}/stocks_engine_v2_c24_book{yr}_trades.csv")))
    for r in rows:
        r["net"] = float(r["net"])
    return rows
BOOK = {yr: load_book(yr) for yr in ("2025", "2026")}
INV_STORED = {yr: [r for r in BOOK[yr] if r["comp"] == "INV-ABOVE"] for yr in BOOK}

# ------------------------------------------------- chain runners (variants)
def replay_plain_local(candles, entry_idx, sign, entry, tgt_pct, stp_pct):
    target = entry * (1 + sign * tgt_pct / 100); stop = entry * (1 - sign * stp_pct / 100)
    for j in range(entry_idx, len(candles)):
        c = candles[j]
        if sign == 1:
            if c["low"] <= stop: er, ep = "stop", stop
            elif c["high"] >= target: er, ep = "target", target
            elif c["time"] == "15:10": er, ep = "square_off", c["close"]
            else: continue
        else:
            if c["high"] >= stop: er, ep = "stop", stop
            elif c["low"] <= target: er, ep = "target", target
            elif c["time"] == "15:10": er, ep = "square_off", c["close"]
            else: continue
        return er, ep, c["time"], j, 100.0 * sign * (ep - entry)
    c = candles[-1]
    return "square_off", c["close"], c["time"], len(candles) - 1, 100.0 * sign * (c["close"] - entry)

def or_width(ctx):
    if ctx.get("or_width") is not None:
        return float(ctx["or_width"])
    orc = [c for c in ctx["raw"] if c["time"] < "09:30"]
    return max(c["high"] for c in orc) - min(c["low"] for c in orc)

def run_chain_var(sym, day, mode):
    """mode: base | orscale (EVE-18) | tight35 (EVE-18 placebo) |
             delay_stop (EVE-19) | delay_target (EVE-19 placebo).
    Mirrors validation run_chain line-for-line except the registered diff."""
    ctx = DAYCTX.get((sym, day))
    if ctx is None: return []
    candles = ctx["candles"]
    trades, start = [], 0
    min_entry_idx = -1
    guard = 0
    while True:
        guard += 1
        if guard > 500: raise RuntimeError(f"chain loop runaway {sym} {day} {mode}")
        chosen = NS["pool_pick"](ctx, NS["v4_head"](ctx, start), NS["skor_head"](ctx, start))
        if chosen is None: break
        setup, dirc, sig, idx = chosen
        if idx + 1 >= len(candles): break
        entry_idx = idx + 1
        if mode in ("delay_stop", "delay_target") and entry_idx < min_entry_idx:
            start = idx + 1
            continue
        entry = float(candles[entry_idx]["open"])
        direction = "LONG" if dirc == "CE" else "SHORT"
        sign = 1 if direction == "LONG" else -1
        if mode == "orscale":
            sp = max(0.5, or_width(ctx) / entry * 100.0)
        elif mode == "tight35":
            sp = 0.35
        else:
            sp = 0.5
        er, ep, et, exit_idx, gross = replay_plain_local(candles, entry_idx, sign, entry, 1.25, sp)
        trades.append({"date": day, "stock": sym, "direction": direction, "setup": setup,
                       "round": len(trades) + 1, "entry_time": candles[entry_idx]["time"],
                       "entry": round(entry, 2), "exit_reason": er, "exit_time": et,
                       "exit_price": round(ep, 2), "gross": round(gross, 2),
                       "net": round(gross - COST, 2), "event_status": ctx["event_status"],
                       "exit_idx": exit_idx, "entry_idx": entry_idx})
        if mode == "delay_stop" and er == "stop":
            min_entry_idx = exit_idx + 3
        if mode == "delay_target" and er == "target":
            min_entry_idx = exit_idx + 3
        start = exit_idx
    return trades

def inv_above_from_chains(mode, days_wanted):
    """Full chains on above-trend (g1) days only; p2 filter; LONG; exclusions."""
    rows = []
    for sym in SYMBOLS:
        for day in days_wanted:
            if (sym, day) not in DAYCTX: continue
            rs = run_chain_var(sym, day, mode)
            for r in rs:
                r["adr"] = ADR.get((sym, day))
            rows.extend(rs)
    p2 = [r for r in rows if r["round"] <= 2 and r["entry_time"] < "10:30"
          and (r["adr"] or 0) >= 3.0]
    return [r for r in p2 if r["direction"] == "LONG" and not wk(r["date"])
            and r["stock"] not in EXCL5 and r["stock"] not in V2_LAW]

ALL_DAYS_CTX = sorted({d for (s, d) in DAYCTX})
G1_DAYS = [d for d in ALL_DAYS_CTX if g1(d)]
log(f"DAYCTX days {ALL_DAYS_CTX[0]}..{ALL_DAYS_CTX[-1]}; above-trend (g1) days: {len(G1_DAYS)}")

# ------------------------------------------------------------- scoring utils
def S(rows):
    return {"n": len(rows), "net": round(sum(float(r["net"]) for r in rows), 2)}
def halves(rows):
    h1 = [r for r in rows if r["date"][5:7] in ("01", "02", "03", "04", "05")]
    h2 = [r for r in rows if r["date"][5:7] not in ("01", "02", "03", "04", "05")]
    return S(h1), S(h2)
def months(rows):
    m = defaultdict(float)
    for r in rows: m[r["date"][:7]] += float(r["net"])
    return {k: round(v, 2) for k, v in sorted(m.items())}
def flips(base_rows, var_rows):
    bm, vm = months(base_rows), months(var_rows)
    return [m for m in bm if bm[m] > 0 and vm.get(m, 0.0) < 0]
def extop3(rows):
    per = defaultdict(float)
    for t in rows: per[t["stock"]] += float(t["net"])
    top = {k for k, _ in sorted(per.items(), key=lambda kv: -kv[1])[:3]}
    return round(sum(float(t["net"]) for t in rows if t["stock"] not in top), 2)
def book_with(inv_rows_by_year):
    out = {}
    for yr in ("2025", "2026"):
        rest = [r for r in BOOK[yr] if r["comp"] != "INV-ABOVE"]
        out[yr] = rest + [{"comp": "INV-ABOVE", "date": r["date"], "stock": r["stock"],
                           "dir": "LONG", "entry_time": r["entry_time"],
                           "net": float(r["net"])} for r in inv_rows_by_year[yr]]
    return out
def gate_block(name, var_inv, placebo_inv=None):
    """var_inv / placebo_inv: {yr: rows}. Returns the full gate dict."""
    vb = book_with(var_inv)
    res = {"candidate": name, "years": {}}
    for yr in ("2025", "2026"):
        res["years"][yr] = {
            "incumbent_comp": S(INV_STORED[yr]), "variant_comp": S(var_inv[yr]),
            "incumbent_book": S(BOOK[yr]), "variant_book": S(vb[yr]),
            "comp_halves_inc": halves(INV_STORED[yr]), "comp_halves_var": halves(var_inv[yr]),
            "book_halves_inc": halves(BOOK[yr]), "book_halves_var": halves(vb[yr]),
            "comp_months_inc": months(INV_STORED[yr]), "comp_months_var": months(var_inv[yr]),
            "book_months_inc": months(BOOK[yr]), "book_months_var": months(vb[yr]),
            "comp_flips": flips(INV_STORED[yr], var_inv[yr]),
            "book_flips": flips(BOOK[yr], vb[yr]),
            "book_extop3_inc": extop3(BOOK[yr]), "book_extop3_var": extop3(vb[yr]),
            "comp_extop3_inc": extop3(INV_STORED[yr]), "comp_extop3_var": extop3(var_inv[yr]),
        }
        if placebo_inv is not None:
            pb = book_with(placebo_inv)
            res["years"][yr]["placebo_comp"] = S(placebo_inv[yr])
            res["years"][yr]["placebo_book"] = S(pb[yr])
    return res
def verdict(res):
    legs = {}
    yrs = res["years"]
    legs["net_both_years_book_and_comp"] = all(
        yrs[y]["variant_book"]["net"] > yrs[y]["incumbent_book"]["net"] and
        yrs[y]["variant_comp"]["net"] > yrs[y]["incumbent_comp"]["net"] for y in yrs)
    def half_ok(inc, var):
        return not (inc["net"] > 0 and var["net"] < 0)
    legs["halves_no_positive_flips_negative"] = all(
        half_ok(yrs[y]["comp_halves_inc"][i], yrs[y]["comp_halves_var"][i]) and
        half_ok(yrs[y]["book_halves_inc"][i], yrs[y]["book_halves_var"][i])
        for y in yrs for i in (0, 1))
    legs["months_no_green_to_red"] = all(
        not yrs[y]["comp_flips"] and not yrs[y]["book_flips"] for y in yrs)
    legs["extop3_book_no_degrade"] = all(
        yrs[y]["book_extop3_var"] >= yrs[y]["book_extop3_inc"] for y in yrs)
    if "placebo_comp" in yrs["2025"]:
        legs["placebo_beaten_both_years"] = all(
            yrs[y]["variant_comp"]["net"] > yrs[y]["placebo_comp"]["net"] for y in yrs)
    res["legs"] = legs
    return legs

RESULTS = {"session": "stocks_tuning_2026-11-10",
           "basis": "equity cash, provisional per 100 shares, Rs40/trade, paper only",
           "incumbent": {yr: {"book": S(BOOK[yr]), "inv_above": S(INV_STORED[yr])}
                         for yr in BOOK}}

# ============================================================ REPRODUCTION
log("=" * 70)
log("REPRODUCTION — chain rebuild at frozen T125/S050 vs stored c24 INV-ABOVE")
base_rows = inv_above_from_chains("base", G1_DAYS)
BASE_BY_YEAR = {yr: [r for r in base_rows if r["date"].startswith(yr)] for yr in ("2025", "2026")}
def keyset(rows):
    return sorted((r["date"], r["stock"], r["entry_time"], round(float(r["net"]), 2)) for r in rows)
repro = {}
for yr in ("2025", "2026"):
    a, b = keyset(BASE_BY_YEAR[yr]), keyset(INV_STORED[yr])
    only_rebuilt = [x for x in a if x not in b]
    only_stored = [x for x in b if x not in a]
    repro[yr] = {"rebuilt": S(BASE_BY_YEAR[yr]), "stored": S(INV_STORED[yr]),
                 "exact_set_match": a == b,
                 "only_in_rebuilt": only_rebuilt[:12], "only_in_stored": only_stored[:12],
                 "n_only_rebuilt": len(only_rebuilt), "n_only_stored": len(only_stored)}
    log(f"REPRO {yr}: rebuilt {repro[yr]['rebuilt']} vs stored {repro[yr]['stored']} "
        f"| exact={a == b} | only_rebuilt={len(only_rebuilt)} only_stored={len(only_stored)}")
REPRO_OK = all(repro[yr]["exact_set_match"] for yr in repro)
RESULTS["reproduction"] = {"exact_both_years": REPRO_OK, "per_year": repro,
    "attempt1_note": "attempt 1 (base exclusions only) rebuilt a SUPERSET: every "
    "stored row matched on (date, stock, entry_time, net); the only extras were "
    "v2-INV-law names (2025 TATASTEEL 04-21 +133.05, HINDALCO 04-24 -355.95; "
    "2026 TATASTEEL 02-10 +215.11/+219.26, 02-12 -144.56). Attempt 2 applies "
    "the documented v2 INV law {HINDALCO, UNITDSPR, TATASTEEL} (cycle 22)."}
# timing assertion for EVE-18 (OR complete 09:30 before every entry)
early = [r for r in base_rows if r["entry_time"] < "09:35"]
RESULTS["timing_or_assert"] = {"inv_entries_before_0935": len(early)}
log(f"TIMING: rebuilt INV-ABOVE entries before 09:35: {len(early)} (OR-scaler knowability)")

def split(rows):
    return {yr: [r for r in rows if r["date"].startswith(yr)] for yr in ("2025", "2026")}

def dump_variant(rows_by_year, label, extra_cols=()):
    fn = f"{WS}/stocks_tuning_2026-11-10_{label}_trades.csv"
    cols = ["date", "stock", "dir", "entry_time", "entry", "exit_reason",
            "exit_time", "exit_price", "net"] + list(extra_cols)
    with open(fn, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for yr in ("2025", "2026"):
            for r in sorted(rows_by_year[yr], key=lambda x: (x["date"], x["entry_time"], x["stock"])):
                row = {"date": r["date"], "stock": r["stock"], "dir": "LONG",
                       "entry_time": r["entry_time"], "entry": r.get("entry", ""),
                       "exit_reason": r.get("exit_reason", ""), "exit_time": r.get("exit_time", ""),
                       "exit_price": r.get("exit_price", ""), "net": float(r["net"])}
                for c in extra_cols: row[c] = r.get(c, "")
                w.writerow(row)
    return fn

def resum_file(fn):
    rows = list(csv.DictReader(open(fn)))
    return {yr: round(sum(float(r["net"]) for r in rows if r["date"].startswith(yr)), 2)
            for yr in ("2025", "2026")}

# ============================================================ EVE-18
log("=" * 70)
log("STOCKS-EVE-18 — OR-scaled stop (chain-faithful) + tight35 placebo")
if REPRO_OK:
    var18 = split(inv_above_from_chains("orscale", G1_DAYS))
    plac18 = split(inv_above_from_chains("tight35", G1_DAYS))
    res18 = gate_block("EVE-18_orscale_stop", var18, plac18)
    verdict(res18)
    res18["legs"]["reproduction"] = True
    res18["legs"]["timing"] = len(early) == 0
    res18["pass"] = all(res18["legs"].values())
    fn18 = dump_variant(var18, "eve18")
    rs = resum_file(fn18)
    res18["independent_resum_from_csv"] = rs
    res18["resum_matches"] = all(abs(rs[yr] - res18["years"][yr]["variant_comp"]["net"]) < 0.005
                                 for yr in rs)
    res18["pass"] = res18["pass"] and res18["resum_matches"]
    n_scaled = {}
    RESULTS["eve18"] = res18
    log(f"EVE-18 variant comp: " + " | ".join(
        f"{y} {res18['years'][y]['variant_comp']} vs inc {res18['years'][y]['incumbent_comp']}"
        for y in res18['years']))
    log(f"EVE-18 legs: {res18['legs']} | PASS={res18['pass']}")
else:
    RESULTS["eve18"] = {"pass": False, "failed_leg": "reproduction",
                        "note": "chain rebuild did not reproduce the stored set; variant not scored"}
    log("EVE-18 FAIL — reproduction leg (variant not scored)")

# ============================================================ EVE-19
log("=" * 70)
log("STOCKS-EVE-19 — re-entry delay >=3 bars after stop exit + delay-after-target placebo")
if REPRO_OK:
    var19 = split(inv_above_from_chains("delay_stop", G1_DAYS))
    plac19 = split(inv_above_from_chains("delay_target", G1_DAYS))
    res19 = gate_block("EVE-19_reentry_delay_stop", var19, plac19)
    verdict(res19)
    res19["legs"]["reproduction"] = True
    # timing verification on produced rows: for consecutive kept rounds on the
    # same stock-day, when the earlier round exited by stop, the next round's
    # entry bar index must be >= stop-exit bar index + 3. (Chain is sequential,
    # so this subset check is sound: any intervening round entered at or after
    # the same threshold, and later entries are strictly later.)
    viol = 0; checked = 0
    for yr in var19:
        by = defaultdict(list)
        for r in var19[yr]: by[(r["date"], r["stock"])].append(r)
        for k, rs_ in by.items():
            rs_ = sorted(rs_, key=lambda r: r["entry_idx"])
            for a, b in zip(rs_, rs_[1:]):
                if a["exit_reason"] == "stop":
                    checked += 1
                    if b["entry_idx"] < a["exit_idx"] + 3: viol += 1
    res19["delay_check"] = {"pairs_checked": checked, "violations": viol}
    res19["legs"]["timing"] = (viol == 0)
    res19["pass"] = all(res19["legs"].values())
    fn19 = dump_variant(var19, "eve19")
    rs = resum_file(fn19)
    res19["independent_resum_from_csv"] = rs
    res19["resum_matches"] = all(abs(rs[yr] - res19["years"][yr]["variant_comp"]["net"]) < 0.005
                                 for yr in rs)
    res19["pass"] = res19["pass"] and res19["resum_matches"]
    RESULTS["eve19"] = res19
    log(f"EVE-19 variant comp: " + " | ".join(
        f"{y} {res19['years'][y]['variant_comp']} vs inc {res19['years'][y]['incumbent_comp']}"
        for y in res19['years']))
    log(f"EVE-19 legs: {res19['legs']} | PASS={res19['pass']}")
else:
    RESULTS["eve19"] = {"pass": False, "failed_leg": "reproduction",
                        "note": "chain rebuild did not reproduce the stored set; variant not scored"}
    log("EVE-19 FAIL — reproduction leg (variant not scored)")

# ============================================================ EVE-20
log("=" * 70)
log("STOCKS-EVE-20 — prior-day spike (>= +4.0%) exclusion, drop filter on stored rows")
DAILY = {}
for sym in SYMBOLS:
    rows = []
    with open(f"{FULLHIST}/{sym}/spot_daily.csv") as f:
        for r in csv.DictReader(f):
            rows.append((r["date"][:10], float(r["close"])))
    rows.sort()
    DAILY[sym] = rows
def prior_day_move(sym, day):
    rows = DAILY[sym]
    idx = [i for i, (d, c) in enumerate(rows) if d == day]
    if not idx or idx[0] < 2: return None
    i = idx[0]
    return (rows[i - 1][1] / rows[i - 2][1] - 1) * 100.0
for yr in ("2025", "2026"):
    for r in INV_STORED[yr]:
        r["_pdm"] = prior_day_move(r["stock"], r["date"])
missing_pdm = sum(1 for yr in INV_STORED for r in INV_STORED[yr] if r["_pdm"] is None)
kept20, dropped20 = {}, {}
for yr in ("2025", "2026"):
    kept20[yr] = [r for r in INV_STORED[yr] if not (r["_pdm"] is not None and r["_pdm"] >= 4.0)]
    dropped20[yr] = [r for r in INV_STORED[yr] if r["_pdm"] is not None and r["_pdm"] >= 4.0]
res20 = gate_block("EVE-20_prior_day_spike_exclusion", kept20)
verdict(res20)
# placebos: chronological skip of the same per-year count; mirror drop (<= -4%)
plac20c, plac20m = {}, {}
for yr in ("2025", "2026"):
    n = len(dropped20[yr])
    srt = sorted(INV_STORED[yr], key=lambda r: (r["date"], r["entry_time"]))
    plac20c[yr] = srt[n:]
    plac20m[yr] = [r for r in INV_STORED[yr] if not (r["_pdm"] is not None and r["_pdm"] <= -4.0)]
res20["placebo_chrono"] = {yr: S(plac20c[yr]) for yr in plac20c}
res20["mirror_drop_downspike"] = {yr: S(plac20m[yr]) for yr in plac20m}
res20["dropped"] = {yr: S(dropped20[yr]) for yr in dropped20}
res20["legs"]["placebo_chrono_beaten_both_years"] = all(
    res20["years"][yr]["variant_comp"]["net"] > res20["placebo_chrono"][yr]["net"] for yr in res20["years"])
res20["legs"]["timing"] = True  # inputs are two prior daily closes, known pre-entry
res20["pass"] = all(res20["legs"].values())
RESULTS["eve20"] = res20
RESULTS["eve20_missing_prior_move"] = missing_pdm
log(f"EVE-20 dropped: {res20['dropped']} | missing prior-move rows: {missing_pdm}")
log(f"EVE-20 variant comp: " + " | ".join(
    f"{y} {res20['years'][y]['variant_comp']} vs inc {res20['years'][y]['incumbent_comp']}"
    for y in res20['years']))
log(f"EVE-20 legs: {res20['legs']} | PASS={res20['pass']}")

# ============================================================ Nov-9 counterfactual (evidence only, NOT a score)
FWD = f"{WS}/data/sarvaritu_fwd"
def fwd_bars(sym, day):
    out = []
    p = f"{FWD}/{sym}/spot_5m.csv"
    if not os.path.exists(p): return out
    for r in csv.DictReader(open(p)):
        if r["timestamp"][:10] == day:
            out.append((r["timestamp"][11:16], float(r["open"]), float(r["high"]),
                        float(r["low"]), float(r["close"])))
    return sorted(out)
gb = fwd_bars("GLENMARK", "2026-11-09")
cf = {}
if gb:
    orc = [b for b in gb if b[0] in ("09:15", "09:20", "09:25")]
    orw = max(b[2] for b in orc) - min(b[3] for b in orc)
    for et, entry in (("09:35", 2658.00), ("09:40", 2650.80)):
        sp_pct = max(0.5, orw / entry * 100.0)
        stop = round(entry * (1 - sp_pct / 100), 2); tgt = round(entry * 1.0125, 2)
        outcome = "no_exit"
        for t, o, h, l, c in gb:
            if t <= et or t > "15:10": continue
            if l <= stop: outcome = f"stop@{t}"; break
            if h >= tgt: outcome = f"target@{t}"; break
            if t == "15:10": outcome = "square_off"
        cf[et] = {"entry": entry, "or_width": round(orw, 2), "or_width_pct": round(orw / entry * 100, 3),
                  "scaled_stop_pct": round(sp_pct, 3), "scaled_stop": stop, "target": tgt,
                  "outcome_under_eve18": outcome}
    cf["eve20_prior_day_move_glenmark"] = "Nov-6 close-to-close +4.36% (P2F-R2 basis, journalled) >= +4.0 -> both rounds dropped"
    cf["eve19_note"] = "round 2 entered 1 bar after round 1's stop bar under stored timing; the >=3-bar delay would have suppressed it"
RESULTS["nov9_counterfactual_evidence_only"] = cf
log(f"NOV-9 COUNTERFACTUAL (evidence only): {json.dumps(cf)}")

json.dump(RESULTS, open(f"{WS}/stocks_tuning_2026-11-10_summary.json", "w"), indent=1, default=str)
log("wrote stocks_tuning_2026-11-10_summary.json")
print("\n".join(LOG))
