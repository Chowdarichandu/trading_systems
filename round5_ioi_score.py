#!/usr/bin/env python3
"""ROUND 5 — intraday-OI gate scorer (2026-11-14).

Scores IOI-1 / IOI-2 exactly as frozen in oi_buildup_programme
Part 7 under the spec mapping in round5_ioi_gate_2026-11-14.md §1:
signal from the day's 09:15-bar and 10:55-bar OI/premium reads
(round5_ioi_dataset.csv), entry at the OPEN of the 11:00 premium
bar, stop -50 before target +90 from the entry bar onward, fills
at the level, square-off at the 15:10 bar close, 1 lot of 30,
Rs220/trade, buying only. Placebos: REVERSED, COIN-FLIP (seed 42),
TIME-SHIFTED (12:00 entry). Gate legs per Part 7 (halves split at
the Jan-Oct window's median trading day). Then the registered
merge test vs TUNED STACK v2 + the November counterfactual.
Paper only, real money Rs0. Reads only round5 files + the frozen
stack ledgers; writes round5_ioi_trades.csv and
round5_ioi_gate_results.json; modifies nothing else.
"""
import csv, json, random
from pathlib import Path
from collections import Counter

TR = Path.home() / "workspace/trading"
OUT = TR / "round5_ioi_data"
CH = OUT / "chunks"
LOT, COST = 30, 220.0

# ---------------- dataset ---------------------------------------------
ds = {}
with open(TR / "round5_ioi_dataset.csv") as f:
    for r in csv.DictReader(f):
        ds[r["date"]] = r
JAN_DAYS = sorted(d for d, r in ds.items() if r["window"] == "JANOCT")
NOV_DAYS = sorted(d for d, r in ds.items() if r["window"] == "NOV")
MEDIAN_DAY = JAN_DAYS[len(JAN_DAYS) // 2]  # 103rd of 205

# ---------------- raw bars ---------------------------------------------
_cache = {}
def contract_bars(exp, strike, typ, day):
    ck = (exp, strike, typ)
    if ck not in _cache:
        days = {}
        for fn in sorted(CH.glob(f"chunk_{exp}_{strike}{typ}_*.json")):
            body = json.loads(fn.read_text())
            for c in ((body.get("data") or {}).get("candles") or []):
                days.setdefault(c[0][:10], {})[c[0][11:16]] = (
                    float(c[1]), float(c[2]), float(c[3]), float(c[4]),
                    float(c[5]), float(c[6]))
        _cache[ck] = days
    bars = _cache[ck].get(day)
    if not bars:
        return None
    return sorted((t, v[0], v[1], v[2], v[3]) for t, v in bars.items())

# ---------------- exit replay (Part 7 geometry, anchored entry) --------
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

# equivalence check vs the frozen G0 replay (anchor 09:20)
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "obs", TR / "oi_buildup_score.py")
obs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(obs)
_probe = None
for d in JAN_DAYS:
    r = ds[d]
    if r["status"] != "complete":
        continue
    b = contract_bars(r["expiry"], int(r["atm"]), "CE", d)
    if b and b[0][0] == "09:15":
        _probe = b
        break
assert _probe is not None
assert replay_entry(_probe, "09:20") == obs.replay_g0(_probe, LOT), \
    "replay_entry != frozen replay_g0 at the 09:20 anchor"
print("replay equivalence vs frozen replay_g0: OK", flush=True)

# ---------------- signals -----------------------------------------------
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

def score_day(family, mode, day, dirn, entry_time):
    r = ds[day]
    strike = int(r["atm"])
    bars = contract_bars(r["expiry"], strike, dirn, day)
    if not bars:
        return None, "no_premium_candles"
    if bars[0][0] > "09:20":
        return None, "series_starts_after_0920"
    rep = replay_entry(bars, entry_time)
    if rep is None:
        return None, f"no_{entry_time}_bar"
    # timing audit: signal inputs are the day's 09:15 / 10:55 bars;
    # the entry bar's OHLC is never an input.
    viol = 0 if entry_time > "10:55" else 1
    return dict(family=family, mode=mode, window=r["window"], date=day,
                direction=dirn, strike=strike, expiry=r["expiry"],
                ce_q=r["ce_q"], pe_q=r["pe_q"], spot1055=r["spot1055"],
                entry_time=entry_time, timing_violation=viol, **rep), None

def run_family(family, days):
    fired = []
    for d in days:
        r = ds[d]
        if r["status"] != "complete":
            continue
        dirn = direction(family, r["ce_q"], r["pe_q"])
        if dirn:
            fired.append((d, dirn))
    books = {}
    rng = random.Random(42)
    coin_dirs = {d: ("CE" if rng.random() < 0.5 else "PE")
                 for d, _ in fired}
    for mode in ("real", "reversed", "coin", "shifted"):
        trades, nc = [], []
        for d, dirn in fired:
            if mode == "reversed":
                use, et = ("PE" if dirn == "CE" else "CE"), "11:00"
            elif mode == "coin":
                use, et = coin_dirs[d], "11:00"
            elif mode == "shifted":
                use, et = dirn, "12:00"
            else:
                use, et = dirn, "11:00"
            tr, why = score_day(family, mode, d, use, et)
            if tr is None:
                nc.append(dict(date=d, direction=use, why=why))
            else:
                trades.append(tr)
        books[mode] = (trades, nc)
    return fired, books

def stats(trades):
    total = round(sum(t["net"] for t in trades), 2)
    months = {}
    for t in trades:
        months[t["date"][:7]] = round(months.get(t["date"][:7], 0.0)
                                      + t["net"], 2)
    h1 = round(sum(t["net"] for t in trades if t["date"] <= MEDIAN_DAY), 2)
    h2 = round(sum(t["net"] for t in trades if t["date"] > MEDIAN_DAY), 2)
    top3 = sorted((t["net"] for t in trades), reverse=True)[:3]
    wins = sum(1 for t in trades if t["net"] > 0)
    return dict(n=len(trades), total=total, months=months, h1=h1, h2=h2,
                ex_top3=round(total - sum(top3), 2), top3=top3,
                wins=wins, win_rate=round(wins / len(trades), 4)
                if trades else None,
                ft=sum(t["ft"] for t in trades))

def day_counts(day_net, all_days):
    g = sum(1 for d in all_days if day_net.get(d, 0.0) > 0)
    r = sum(1 for d in all_days if day_net.get(d, 0.0) < 0)
    return dict(green=g, red=r, flat_or_no_trade=len(all_days) - g - r,
                total_days=len(all_days))

results = {"median_day": MEDIAN_DAY, "families": {}}
all_trades = []
jan_fired, jan_books = {}, {}
for family in ("IOI-1", "IOI-2"):
    fired, books = run_family(family, JAN_DAYS)
    jan_fired[family], jan_books[family] = fired, books
    real, real_nc = books["real"]
    s = stats(real)
    e = {m: stats(books[m][0]) for m in ("reversed", "coin", "shifted")}
    viol = sum(t["timing_violation"] for t in real)
    legs = dict(
        total_pos=s["total"] > 0,
        halves_pos=s["h1"] > 0 and s["h2"] > 0,
        ex_top3_pos=s["ex_top3"] > 0,
        beats_reversed=s["total"] > e["reversed"]["total"],
        beats_coin=s["total"] > e["coin"]["total"],
        beats_shifted=s["total"] > e["shifted"]["total"],
        timing_clean=viol == 0,
        nc_ok=len(real_nc) <= 0.05 * max(1, len(fired)) if fired else True)
    fam_day_net = {}
    for t in real:
        fam_day_net[t["date"]] = round(fam_day_net.get(t["date"], 0.0)
                                       + t["net"], 2)
    results["families"][family] = dict(
        fired_days=len(fired), scored=len(real), scoring_nc=real_nc,
        real=s, placebos=e, timing_violations=viol, gate_legs=legs,
        gate_pass=all(legs.values()),
        per_trade_day=round(s["total"] / len(fired), 2) if fired else None,
        day_counts=day_counts(fam_day_net, JAN_DAYS))
    for m, (tr, _) in books.items():
        all_trades += tr
    print(f"{family}: fired={len(fired)} n={s['n']} total={s['total']} "
          f"H=({s['h1']},{s['h2']}) ex3={s['ex_top3']} "
          f"placebos rev={e['reversed']['total']} "
          f"coin={e['coin']['total']} shift={e['shifted']['total']} "
          f"NC={len(real_nc)} PASS={all(legs.values())} legs={legs}",
          flush=True)

band_nc = [d for d in JAN_DAYS if ds[d]["status"] == "NC_BAND"]
no_spot = [d for d in JAN_DAYS if ds[d]["status"] == "NC_NO_SPOT"]
results["window"] = dict(jan_days=len(JAN_DAYS), band_nc_days=len(band_nc),
                         band_nc_list=band_nc, no_spot_days=no_spot,
                         complete_days=sum(1 for d in JAN_DAYS
                                           if ds[d]["status"] == "complete"))

# ---------------- write trades + independent re-sum ---------------------
with open(TR / "round5_ioi_trades.csv", "w", newline="") as f:
    if all_trades:
        w = csv.DictWriter(f, fieldnames=list(all_trades[0].keys()))
        w.writeheader()
        w.writerows(all_trades)
chk = {}
with open(TR / "round5_ioi_trades.csv") as f:
    for r in csv.DictReader(f):
        if r["mode"] == "real" and r["window"] == "JANOCT":
            chk[r["family"]] = round(chk.get(r["family"], 0.0)
                                     + float(r["net"]), 2)
resum_ok = all(chk.get(fam) == results["families"][fam]["real"]["total"]
               for fam in ("IOI-1", "IOI-2"))
results["resum_check"] = ("EXACT for both families" if resum_ok
                          else f"MISMATCH {chk}")
print("re-sum:", results["resum_check"], flush=True)

# ---------------- merge vs TUNED STACK v2 -------------------------------
stack_rows = list(csv.DictReader(
    open(TR / "solid60_programme_2026-11-13_bank_A_stack_features.csv")))
stack_day_net = {}
for r in stack_rows:
    stack_day_net[r["date"]] = round(stack_day_net.get(r["date"], 0.0)
                                     + float(r["x1_net"]), 2)
stack_total = round(sum(stack_day_net.values()), 2)
stack_days = set(stack_day_net)
assert len(stack_rows) == 111 and stack_total == 127351.50, \
    f"stack anchor failed: {len(stack_rows)} legs, {stack_total}"
passes = [f for f in ("IOI-1", "IOI-2")
          if results["families"][f]["gate_pass"]]
if passes:
    merge_family, merge_label = passes[0], "GATE PASSER"
else:
    merge_family = max(("IOI-1", "IOI-2"),
                       key=lambda f: results["families"][f]["real"]["total"])
    merge_label = "STRONGEST FAILING FAMILY — merge-only evidence"
real_trades = jan_books[merge_family]["real"][0]
incr = [t for t in real_trades if t["date"] not in stack_days]
incr_total = round(sum(t["net"] for t in incr), 2)
merged_total = round(stack_total + incr_total, 2)
merged_day_net = dict(stack_day_net)
for t in incr:
    merged_day_net[t["date"]] = round(merged_day_net.get(t["date"], 0.0)
                                      + t["net"], 2)
merged_days = set(merged_day_net)
merged_months = {}
for d, n in merged_day_net.items():
    merged_months[d[:7]] = round(merged_months.get(d[:7], 0.0) + n, 2)
merge = dict(
    family=merge_family, label=merge_label,
    stack_anchor=dict(legs=len(stack_rows), total=stack_total,
                      trade_days=len(stack_days),
                      per_trade_day=round(stack_total / len(stack_days), 2),
                      day_counts=day_counts(stack_day_net, JAN_DAYS)),
    increment_legs=len(incr), increment_total=incr_total,
    merged_total=merged_total, merged_trade_days=len(merged_days),
    merged_per_trade_day=round(merged_total / len(merged_days), 2),
    merged_months=merged_months,
    merged_red_months=[m for m, v in merged_months.items() if v < 0],
    merged_day_counts=day_counts(merged_day_net, JAN_DAYS),
    merge_pass=bool(incr_total > 0 and merged_total > stack_total))
results["merge"] = merge
print(f"MERGE ({merge_family}, {merge_label}): incr {len(incr)} legs "
      f"{incr_total} | merged {merged_total} on {len(merged_days)} TD = "
      f"{merge['merged_per_trade_day']}/TD | pass={merge['merge_pass']}",
      flush=True)

# ---------------- November counterfactual --------------------------------
nov_stack_net = {}
with open(TR / "november_shadow_stack_bank_log.csv") as f:
    for r in csv.DictReader(f):
        if r.get("net_inr"):
            nov_stack_net[r["date"]] = float(r["net_inr"])
NOV_STACK_TOTAL = round(sum(nov_stack_net.values()), 2)
nov = {"stack_total": NOV_STACK_TOTAL, "stack_days": nov_stack_net,
       "family": merge_family, "rows": []}
_, nov_books = run_family(merge_family, NOV_DAYS)
nov_real, nov_nc = nov_books["real"]
nov_by_day = {t["date"]: t for t in nov_real}
nov_incr_total = 0.0
merged_nov_net = {}
for d in NOV_DAYS:
    t = nov_by_day.get(d)
    snet = nov_stack_net.get(d)
    row = dict(date=d, dataset_status=ds[d]["status"],
               stack_net=snet,
               family=(dict(direction=t["direction"], strike=t["strike"],
                            entry=t["entry"], exit=t["exit"],
                            exit_time=t["exit_time"],
                            exit_reason=t["exit_reason"], net=t["net"])
                       if t else None),
               family_nc=next((n["why"] for n in nov_nc
                               if n["date"] == d), None))
    incr_net = 0.0
    if t is not None and snet is None:
        incr_net = t["net"]
        nov_incr_total = round(nov_incr_total + incr_net, 2)
    day_total = round((snet or 0.0) + incr_net, 2)
    if day_total != 0:
        merged_nov_net[d] = day_total
    row["increment_net"] = incr_net
    row["merged_day_net"] = day_total
    nov["rows"].append(row)
nov["increment_total"] = nov_incr_total
nov["merged_total"] = round(NOV_STACK_TOTAL + nov_incr_total, 2)
nov["merged_day_counts"] = day_counts(merged_nov_net, NOV_DAYS)
nov["family_legs"] = len(nov_real)
nov["family_nc"] = nov_nc
results["november"] = nov
all_trades += nov_real
with open(TR / "round5_ioi_trades.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(all_trades[0].keys()))
    w.writeheader()
    w.writerows(all_trades)
print(f"NOVEMBER ({merge_family}): family legs={len(nov_real)} "
      f"incr={nov_incr_total} | merged Nov {nov['merged_total']} "
      f"vs stack {NOV_STACK_TOTAL}", flush=True)

(TR / "round5_ioi_gate_results.json").write_text(json.dumps(results,
                                                           indent=1))
print("results -> round5_ioi_gate_results.json", flush=True)
