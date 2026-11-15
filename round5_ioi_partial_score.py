#!/usr/bin/env python3
"""ROUND 5 — IOI PARTIAL-WINDOW READ (2026-11-14). LOCAL CACHE ONLY.

Scores IOI-1 / IOI-2 on the 104 band-complete Jan-Jun 2026 days that
the cached chunk store supports (the full build was halted by an
Upstox HTTP 429 at 59.1%; the standing rule forbids new requests to
that provider scope in this attempt).

ZERO NETWORK BY CONSTRUCTION: this file contains no urllib / requests
/ socket import and reads only files on disk (stored spot series,
the daily-OI CSV, and round5_ioi_data/chunks/). Any datum not in the
cache is NC, never fetched.

Logic is copied verbatim from the frozen pipeline wherever it exists:
band/quadrant aggregation from round5_ioi_build.py (its fetch driver
is NOT imported — it would fetch at import), contract_bars /
replay_entry / direction from round5_ioi_score.py, and replay_g0 from
oi_buildup_score.py (likewise not imported — it loads a token at
module level) for the same 09:20-anchor equivalence assertion the
frozen scorer runs.

THIS IS A PARTIAL-WINDOW READ — JAN-JUN, 104 DAYS — NOT THE GATE.
No Jan-Oct gate verdict, no Jul-Oct figure, no November
counterfactual is computed. Writes round5_ioi_partial_trades.csv and
round5_ioi_partial_results.json; modifies nothing else; arms nothing.
Paper only, real money Rs0, buying only, 1 lot of 30, Rs220/trade.
"""
import csv, json
from pathlib import Path
from collections import Counter

TR = Path.home() / "workspace/trading"
OUT = TR / "round5_ioi_data"
CH = OUT / "chunks"
LOT, COST = 30, 220.0
TITLE = "PARTIAL WINDOW — JAN–JUN, 104 DAYS — NOT THE GATE"
WINDOW_END = "2026-06-30"

# ---------------- spot (build.py's construction, local files only) ----
spot_raw = json.load(open(TR / "daily2leg/spot.json"))
SPOT = {}
for d, bars in spot_raw["BANKNIFTY"].items():
    SPOT[d] = {b[0]: (float(b[1]), float(b[2]), float(b[3]), float(b[4]))
               for b in bars}
nov_bars = json.loads((TR / "oi_history/spot_nov_bars.json").read_text())
for d, bars in nov_bars.get("BANKNIFTY", {}).items():
    SPOT.setdefault(d, {b[0]: (float(b[1]), float(b[2]), float(b[3]),
                                float(b[4])) for b in bars})
extra_fn = TR / "round4_history/spot_extra.json"
if extra_fn.exists():
    for d, bars in json.loads(extra_fn.read_text()).items():
        SPOT.setdefault(d, {b[0]: (float(b[1]), float(b[2]), float(b[3]),
                                   float(b[4])) for b in bars})

# ---------------- day list (Jan-Jun only) ------------------------------
oi_rows = {}
with open(TR / "oi_history/banknifty_daily_oi.csv") as f:
    for r in csv.DictReader(f):
        oi_rows[r["date"]] = r
DAYS = [(d, "PARTIAL_JANJUN", oi_rows[d]["expiry"])
        for d in sorted(oi_rows) if "2026-01-01" <= d <= WINDOW_END]

# ---------------- bands (build.py, verbatim) ---------------------------
def band_of(day):
    bars = SPOT.get(day)
    if not bars or "10:55" not in bars:
        return None, None
    spot = bars["10:55"][3]
    atm = int(round(spot / 100.0)) * 100
    return spot, [atm + 100 * k for k in range(-5, 6)]

DAYINFO = {}
for d, w, exp in DAYS:
    spot, band = band_of(d)
    DAYINFO[d] = dict(window=w, expiry=exp, spot1055=spot, band=band)

# ---------------- chunk store (build.py aggregate, verbatim) -----------
_cache = {}
def agg_contract_bars(exp, s, t):
    """{(date): {time: (o,h,l,c,vol,oi)}} from cached chunks."""
    ck = (exp, s, t)
    if ck in _cache:
        return _cache[ck]
    days = {}
    for fn in sorted(CH.glob(f"chunk_{exp}_{s}{t}_*.json")):
        body = json.loads(fn.read_text())
        for c in ((body.get("data") or {}).get("candles") or []):
            days.setdefault(c[0][:10], {})[c[0][11:16]] = (
                float(c[1]), float(c[2]), float(c[3]), float(c[4]),
                float(c[5]), float(c[6]))
    _cache[ck] = days
    return days

def quadrant(doi, dp):
    if doi == 0 or dp == 0:
        return "FLAT"
    if doi > 0 and dp > 0:
        return "LONG_BUILDUP"
    if doi > 0 and dp < 0:
        return "SHORT_BUILDUP"
    if doi < 0 and dp > 0:
        return "SHORT_COVERING"
    return "LONG_UNWINDING"

ds = {}
for d, info in DAYINFO.items():
    base = dict(date=d, window=info["window"], expiry=info["expiry"],
                spot1055=info["spot1055"],
                atm=(int(round(info["spot1055"] / 100.0)) * 100
                     if info["spot1055"] else ""))
    if info["band"] is None:
        ds[d] = {**base, "status": "NC_NO_SPOT",
                 "nc_detail": "no 10:55 spot bar"}
        continue
    agg = {s: dict(doi=0.0, pb=0.0, pr=0.0) for s in ("CE", "PE")}
    missing = []
    for s in info["band"]:
        for t in ("CE", "PE"):
            bars = agg_contract_bars(info["expiry"], s, t).get(d, {})
            b0, b1 = bars.get("09:15"), bars.get("10:55")
            if b0 is None or b1 is None:
                missing.append(f"{s}{t}:{'base' if b0 is None else ''}"
                               f"{'read' if b1 is None else ''}")
                continue
            agg[t]["doi"] += b1[5] - b0[5]
            agg[t]["pb"] += b0[3]
            agg[t]["pr"] += b1[3]
    if missing:
        ds[d] = {**base, "status": "NC_BAND",
                 "nc_detail": ";".join(missing[:6]),
                 "n_missing": len(missing)}
        continue
    ce, pe = agg["CE"], agg["PE"]
    ds[d] = {**base, "status": "complete",
             "ce_doi": ce["doi"], "pe_doi": pe["doi"],
             "ce_p_base": round(ce["pb"], 2), "ce_p_read": round(ce["pr"], 2),
             "ce_dp": round(ce["pr"] - ce["pb"], 2),
             "pe_p_base": round(pe["pb"], 2), "pe_p_read": round(pe["pr"], 2),
             "pe_dp": round(pe["pr"] - pe["pb"], 2),
             "ce_q": quadrant(ce["doi"], ce["pr"] - ce["pb"]),
             "pe_q": quadrant(pe["doi"], pe["pr"] - pe["pb"]),
             "nc_detail": ""}

ALL_DAYS = sorted(ds)
COMPLETE_DAYS = [d for d in ALL_DAYS if ds[d]["status"] == "complete"]
NC_BAND_DAYS = [d for d in ALL_DAYS if ds[d]["status"] == "NC_BAND"]
NC_NO_SPOT_DAYS = [d for d in ALL_DAYS if ds[d]["status"] == "NC_NO_SPOT"]
comp_by_month = Counter(d[:7] for d in COMPLETE_DAYS)
nc_by_month = Counter(d[:7] for d in NC_BAND_DAYS)
print("window days:", len(ALL_DAYS), "| complete:", len(COMPLETE_DAYS),
      dict(sorted(comp_by_month.items())), "| NC_BAND:", len(NC_BAND_DAYS),
      dict(sorted(nc_by_month.items())), "| NC_NO_SPOT:",
      len(NC_NO_SPOT_DAYS), flush=True)
assert len(COMPLETE_DAYS) == 104, \
    f"complete-day count {len(COMPLETE_DAYS)} != 104 (frozen halt record)"
assert len(NC_BAND_DAYS) == 16 and not NC_NO_SPOT_DAYS, \
    "NC profile differs from the frozen halt record"
MEDIAN_DAY = COMPLETE_DAYS[len(COMPLETE_DAYS) // 2]  # 53rd of 104

# ---------------- per-day premium bars (score.py, verbatim) ------------
_bars_cache = {}
def contract_bars(exp, strike, typ, day):
    ck = (exp, strike, typ)
    if ck not in _bars_cache:
        days = {}
        for fn in sorted(CH.glob(f"chunk_{exp}_{strike}{typ}_*.json")):
            body = json.loads(fn.read_text())
            for c in ((body.get("data") or {}).get("candles") or []):
                days.setdefault(c[0][:10], {})[c[0][11:16]] = (
                    float(c[1]), float(c[2]), float(c[3]), float(c[4]),
                    float(c[5]), float(c[6]))
        _bars_cache[ck] = days
    bars = _bars_cache[ck].get(day)
    if not bars:
        return None
    return sorted((t, v[0], v[1], v[2], v[3]) for t, v in bars.items())

# ---------------- exit replay (score.py, verbatim) ---------------------
def replay_entry(bars, entry_time):
    """Mirror of the frozen replay_g0 with the entry bar anchored at
    entry_time instead of 09:20. Stop -50 checked BEFORE target +90
    on every bar from the entry bar onward; fills at the level;
    square-off at the 15:10 bar close."""
    if not bars:
        return None
    bs = [b for b in bars if b[0] >= entry_time]
    if not bs or bs[0][0] != entry_time:
        return None
    entry = bs[0][1]
    stop, target, sq = entry - 50.0, entry + 90.0, "15:10"
    def out(px, reason, t, ft):
        return dict(entry=entry, exit=px, exit_time=t, exit_reason=reason,
                    ft=ft, net=round((px - entry) * LOT - COST, 2))
    for (t, o, h, l, cl) in bs:
        if t > sq:
            break
        if l <= stop:
            return out(stop, "stop", t, 0)
        if h >= target:
            return out(target, "target", t, 1)
        if t == sq:
            return out(cl, "square_off", t, 0)
    lb = bs[-1]
    return out(lb[4], "square_off", lb[0], 0)

# ---------------- frozen replay_g0 (oi_buildup_score.py, verbatim) -----
def replay_g0(bars, lot):
    bs = [b for b in bars if b[0] >= "09:20"]
    if not bs or bs[0][0] != "09:20":
        return None
    entry = bs[0][1]
    stop, target, sq = entry - 50.0, entry + 90.0, "15:10"
    def out(px, reason, t, ft):
        return dict(entry=entry, exit=px, exit_time=t, exit_reason=reason,
                    ft=ft, net=round((px - entry) * lot - COST, 2))
    for (t, o, h, l, cl) in bs:
        if t > sq:
            break
        if l <= stop:
            return out(stop, "stop", t, 0)
        if h >= target:
            return out(target, "target", t, 1)
        if t == sq:
            return out(cl, "square_off", t, 0)
    lb = bs[-1]
    return out(lb[4], "square_off", lb[0], 0)

# equivalence check vs the frozen G0 replay (anchor 09:20), as the
# frozen scorer runs it — first complete day with a 09:15-starting
# ATM CE series.
_probe = None
for d in COMPLETE_DAYS:
    r = ds[d]
    b = contract_bars(r["expiry"], int(r["atm"]), "CE", d)
    if b and b[0][0] == "09:15":
        _probe = b
        break
assert _probe is not None
assert replay_entry(_probe, "09:20") == replay_g0(_probe, LOT), \
    "replay_entry != frozen replay_g0 at the 09:20 anchor"
print("replay equivalence vs frozen replay_g0: OK", flush=True)

# ---------------- signals (score.py, verbatim) --------------------------
def direction(family, ce_q, pe_q):
    if family == "IOI-1":
        if ce_q == "LONG_BUILDUP" and pe_q != "LONG_BUILDUP":
            return "CE"
        if pe_q == "LONG_BUILDUP" and ce_q != "LONG_BUILDUP":
            return "PE"
    else:  # IOI-2
        if ce_q == "SHORT_COVERING" and pe_q != "LONG_BUILDUP":
            return "CE"
        if pe_q == "SHORT_COVERING" and ce_q != "LONG_BUILDUP":
            return "PE"
    return None

def score_day(family, day, dirn):
    """score.py's score_day (real mode, 11:00 entry), plus the task's
    cache-coverage verification: the traded contract's cached series
    must contain the 15:10 bar (full-day coverage) or the trade is
    NC — never fetched, never replayed on a truncated series."""
    r = ds[day]
    strike = int(r["atm"])
    bars = contract_bars(r["expiry"], strike, dirn, day)
    if not bars:
        return None, "no_premium_candles"
    if bars[0][0] > "09:20":
        return None, "series_starts_after_0920"
    if "15:10" not in {b[0] for b in bars}:
        return None, "no_1510_bar_in_cache"
    rep = replay_entry(bars, "11:00")
    if rep is None:
        return None, "no_11:00_bar"
    # timing audit: signal inputs are the day's 09:15 / 10:55 bars;
    # the entry bar's OHLC is never an input.
    viol = 0 if "11:00" > "10:55" else 1
    return dict(family=family, mode="real", window=r["window"], date=day,
                direction=dirn, strike=strike, expiry=r["expiry"],
                ce_q=r["ce_q"], pe_q=r["pe_q"], spot1055=r["spot1055"],
                entry_time="11:00", timing_violation=viol, **rep), None

def day_counts(day_net, all_days):
    g = sum(1 for d in all_days if day_net.get(d, 0.0) > 0)
    r = sum(1 for d in all_days if day_net.get(d, 0.0) < 0)
    return dict(green=g, red=r, flat_or_no_trade=len(all_days) - g - r,
                total_days=len(all_days))

def fam_stats(trades, fired):
    total = round(sum(t["net"] for t in trades), 2)
    months = {}
    for t in trades:
        months[t["date"][:7]] = round(months.get(t["date"][:7], 0.0)
                                      + t["net"], 2)
    h1 = round(sum(t["net"] for t in trades if t["date"] <= MEDIAN_DAY), 2)
    h2 = round(sum(t["net"] for t in trades if t["date"] > MEDIAN_DAY), 2)
    q1 = round(sum(t["net"] for t in trades if t["date"] <= "2026-03-31"), 2)
    q2 = round(sum(t["net"] for t in trades if t["date"] > "2026-03-31"), 2)
    top3 = sorted((t["net"] for t in trades), reverse=True)[:3]
    wins = sum(1 for t in trades if t["net"] > 0)
    day_net = {}
    for t in trades:
        day_net[t["date"]] = round(day_net.get(t["date"], 0.0) + t["net"], 2)
    return dict(
        legs=len(trades), fired_days=len(fired),
        total=total,
        per_trade_day=round(total / len(fired), 2) if fired else None,
        wins=wins,
        win_rate=round(wins / len(trades), 4) if trades else None,
        months=months,
        halves_median_split=dict(split_day=MEDIAN_DAY, first=h1, second=h2,
                                 first_legs=sum(1 for t in trades
                                                if t["date"] <= MEDIAN_DAY),
                                 second_legs=sum(1 for t in trades
                                                 if t["date"] > MEDIAN_DAY)),
        quarters=dict(q1_jan_mar=q1, q2_apr_jun=q2,
                      q1_legs=sum(1 for t in trades
                                  if t["date"] <= "2026-03-31"),
                      q2_legs=sum(1 for t in trades
                                  if t["date"] > "2026-03-31")),
        ex_top3=round(total - sum(top3), 2), top3=top3,
        ft=sum(t["ft"] for t in trades),
        day_counts_104=day_counts(day_net, COMPLETE_DAYS),
        day_counts_120=day_counts(day_net, ALL_DAYS))

# ---------------- score both families on the 104 days ------------------
results = {"label": TITLE, "window": "PARTIAL_JANJUN",
           "complete_days": len(COMPLETE_DAYS),
           "complete_by_month": dict(sorted(comp_by_month.items())),
           "nc_band_days": NC_BAND_DAYS,
           "nc_band_by_month": dict(sorted(nc_by_month.items())),
           "median_complete_day": MEDIAN_DAY, "families": {}}
all_trades = []
fam_trades = {}
for family in ("IOI-1", "IOI-2"):
    fired, trades, nc = [], [], []
    for d in COMPLETE_DAYS:
        r = ds[d]
        dirn = direction(family, r["ce_q"], r["pe_q"])
        if not dirn:
            continue
        fired.append((d, dirn))
        tr, why = score_day(family, d, dirn)
        if tr is None:
            nc.append(dict(date=d, direction=dirn, why=why))
        else:
            trades.append(tr)
    s = fam_stats(trades, fired)
    viol = sum(t["timing_violation"] for t in trades)
    results["families"][family] = dict(
        **s, scoring_nc=nc, timing_violations=viol)
    fam_trades[family] = trades
    all_trades += trades
    print(f"{family}: fired={len(fired)} legs={s['legs']} "
          f"total={s['total']} perTD={s['per_trade_day']} "
          f"WR={s['win_rate']} halves=({s['halves_median_split']['first']},"
          f"{s['halves_median_split']['second']}) "
          f"Q=({s['quarters']['q1_jan_mar']},{s['quarters']['q2_apr_jun']}) "
          f"ex3={s['ex_top3']} NC={len(nc)} viol={viol}", flush=True)

# ---------------- write trades + independent re-sum --------------------
with open(TR / "round5_ioi_partial_trades.csv", "w", newline="") as f:
    if all_trades:
        w = csv.DictWriter(f, fieldnames=list(all_trades[0].keys()))
        w.writeheader()
        w.writerows(all_trades)
chk = {}
with open(TR / "round5_ioi_partial_trades.csv") as f:
    for r in csv.DictReader(f):
        if r["mode"] == "real":
            chk[r["family"]] = round(chk.get(r["family"], 0.0)
                                     + float(r["net"]), 2)
resum_ok = all(chk.get(fam) == results["families"][fam]["total"]
               for fam in ("IOI-1", "IOI-2"))
results["resum_check"] = ("EXACT for both families" if resum_ok
                          else f"MISMATCH {chk}")
print("re-sum:", results["resum_check"], flush=True)

# ---------------- merge READ vs stack, same 104 days -------------------
stack_rows = list(csv.DictReader(
    open(TR / "solid60_programme_2026-11-13_bank_A_stack_features.csv")))
stack_day_net_all = {}
for r in stack_rows:
    stack_day_net_all[r["date"]] = round(
        stack_day_net_all.get(r["date"], 0.0) + float(r["x1_net"]), 2)
stack_total_all = round(sum(stack_day_net_all.values()), 2)
assert len(stack_rows) == 111 and stack_total_all == 127351.50, \
    f"stack anchor failed: {len(stack_rows)} legs, {stack_total_all}"
stack_days_all = set(stack_day_net_all)
win_set = set(COMPLETE_DAYS)
stack_win_days = {d: n for d, n in stack_day_net_all.items() if d in win_set}
stack_win_legs = sum(1 for r in stack_rows if r["date"] in win_set)
stack_win_total = round(sum(stack_win_days.values()), 2)
results["stack_on_104"] = dict(
    legs=stack_win_legs, total=stack_win_total,
    trade_days=len(stack_win_days),
    per_trade_day=round(stack_win_total / len(stack_win_days), 2)
    if stack_win_days else None,
    full_ledger_anchor=dict(legs=len(stack_rows),
                            total=stack_total_all, trade_days=89))
merges = {}
for family in ("IOI-1", "IOI-2"):
    trades = fam_trades[family]
    incr = [t for t in trades if t["date"] not in stack_days_all]
    incr_total = round(sum(t["net"] for t in incr), 2)
    merged_day_net = dict(stack_win_days)
    for t in incr:
        merged_day_net[t["date"]] = round(
            merged_day_net.get(t["date"], 0.0) + t["net"], 2)
    merged_total = round(stack_win_total + incr_total, 2)
    merged_months = {}
    for d, n in merged_day_net.items():
        merged_months[d[:7]] = round(merged_months.get(d[:7], 0.0) + n, 2)
    merges[family] = dict(
        increment_legs=len(incr), increment_total=incr_total,
        merged_total=merged_total,
        merged_trade_days=len(merged_day_net),
        merged_per_trade_day=round(merged_total / len(merged_day_net), 2)
        if merged_day_net else None,
        merged_months=merged_months,
        merged_red_months=[m for m, v in merged_months.items() if v < 0],
        merged_day_counts_104=day_counts(merged_day_net, COMPLETE_DAYS),
        increment_positive=incr_total > 0,
        merged_beats_stack_window=merged_total > stack_win_total)
    print(f"MERGE READ {family} (PARTIAL WINDOW): incr "
          f"{len(incr)} legs {incr_total} | merged {merged_total} on "
          f"{len(merged_day_net)} TD", flush=True)
results["merge_reads_partial_window"] = merges
results["not_computed"] = [
    "Jan-Oct gate verdict (window incomplete: Jul-Oct unfetched)",
    "any Jul-Oct figure",
    "November counterfactual (November contracts unfetched)",
    "placebos / gate legs (Part 7 gate runs only on the full window)"]
(TR / "round5_ioi_partial_results.json").write_text(json.dumps(results,
                                                               indent=1))
print("results -> round5_ioi_partial_results.json", flush=True)
