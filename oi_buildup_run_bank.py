#!/usr/bin/env python3
"""OI BUILD-UP — Bank-only closing run (2026-11-13 evening).

Executes the FROZEN scorer oi_buildup_score.py (imported, unmodified)
for BANKNIFTY V1/V2, plus V3 (frozen in the programme file Part 2B
before this run) via a direction() extension that delegates V1/V2 to
the frozen function. Then: the supplementary Nov-13 check (Nov 12
signal read from the archived chain) and the registered MERGE test
against TUNED STACK v2 (increment = family legs on stack-idle days).
Outputs: oi_buildup_trades.csv, oi_buildup_results.json (+ merge and
supplementary blocks). Paper only, real money Rs0. On HTTP 429 the
frozen scorer raises RateLimited -> partial results saved, flagged.
"""
import csv, json, sys
import importlib.util
from pathlib import Path
from urllib.parse import quote

TR = Path.home() / "workspace/trading"
spec = importlib.util.spec_from_file_location(
    "obs", TR / "oi_buildup_score.py")
obs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(obs)

_orig_direction = obs.direction


def direction3(variant, q):
    if variant == "V3":
        if q is None:
            return None
        ce, pe = q
        if ce == "SHORT_COVERING" and pe != "LONG_BUILDUP":
            return "CE"
        if pe == "SHORT_COVERING" and ce != "LONG_BUILDUP":
            return "PE"
        return None
    return _orig_direction(variant, q)


obs.direction = direction3

# ---- DATA-LAYER REPAIR (documented in the programme file, Part 2B):
# a stored premium series whose first bar is later than 09:20 is a
# truncated fetch window, not a scorable series for a 09:20-entry book.
# Treat it as missing and use the frozen scorer's own fetch route
# (full-day candles, cached). No rule of the frozen scorer changes.
_orig_prem_bars = obs.prem_bars


def prem_bars_full(idx, exp, strike, typ, day):
    bars, src = _orig_prem_bars(idx, exp, strike, typ, day)
    if bars and bars[0][0] <= "09:20":
        return bars, src
    fn = obs.FETCH_DIR / f"candles_{idx}_{int(strike)}{typ}_{exp}_{day}.json"
    if fn.exists():
        body = json.loads(fn.read_text())
        cd = [c for c in ((body.get("data") or {}).get("candles") or [])
              if c[0][:10] == day]
        if cd:
            fb = sorted((c[0][11:16], float(c[1]), float(c[2]),
                         float(c[3]), float(c[4])) for c in cd)
            if fb[0][0] <= "09:20":
                return fb, "fetched_cache"
    fb = obs.fetch_bars(idx, exp, strike, typ, day)
    if fb:
        return fb, "fetched_full"
    return bars, src


obs.prem_bars = prem_bars_full

results = {"scope": "BANKNIFTY only — Nifty daily OI dataset not built; "
                    "Part 5 gated on this run's mechanical validation"}
all_trades = []
oi = obs.load_oi("BANKNIFTY")
results["BANKNIFTY"] = {}
try:
    for variant in ("V1", "V2", "V3"):
        entry = {}
        real, nc = obs.run_book("BANKNIFTY", variant, "real", oi)
        entry["real"] = obs.stats(real)
        entry["nc"] = nc
        entry["timing_violations"] = sum(
            1 for t in real if not t["signal_date"] < t["trade_date"])
        for mode in ("reversed", "coin", "shifted"):
            pl, _ = obs.run_book("BANKNIFTY", variant, mode, oi)
            entry[mode] = obs.stats(pl)
            all_trades += pl
        all_trades += real
        s, e = entry["real"], entry
        legs = dict(
            total_pos=s["total"] > 0,
            halves_pos=s["h1"] > 0 and s["h2"] > 0,
            ex_top3_pos=s["ex_top3"] > 0,
            beats_reversed=s["total"] > e["reversed"]["total"],
            beats_coin=s["total"] > e["coin"]["total"],
            beats_shifted=s["total"] > e["shifted"]["total"],
            timing_clean=e["timing_violations"] == 0,
            nc_ok=len(nc) <= max(1, int(0.05 * (s["n"] + len(nc)))),
        )
        entry["gate_legs"] = legs
        entry["gate_pass"] = all(legs.values())
        results["BANKNIFTY"][variant] = entry
        print(f"BANKNIFTY {variant}: n={s['n']} total={s['total']} "
              f"H=({s['h1']},{s['h2']}) ex3={s['ex_top3']} "
              f"pace={s['pace_per_month']} NC={len(nc)} "
              f"PASS={entry['gate_pass']} legs={legs}", flush=True)
        print(f"   placebos: rev={e['reversed']['total']} "
              f"coin={e['coin']['total']} shift={e['shifted']['total']} "
              f"| NOV n={s['nov_n']} total={s['nov_total']}", flush=True)
except obs.RateLimited:
    print("RATE_LIMIT_STOP during scoring — partial results", flush=True)
    results["rate_limited"] = True

# ---- write trades + independent re-sum (frozen main()'s check, Bank scope)
with open(TR / "oi_buildup_trades.csv", "w", newline="") as f:
    if all_trades:
        w = csv.DictWriter(f, fieldnames=list(all_trades[0].keys()))
        w.writeheader()
        w.writerows(all_trades)
chk = {}
with open(TR / "oi_buildup_trades.csv") as f:
    for r in csv.DictReader(f):
        if r["mode"] == "real" and r["trade_date"] <= "2026-10-31":
            k = (r["index"], r["variant"])
            chk[k] = round(chk.get(k, 0.0) + float(r["net"]), 2)
resum_ok = True
for variant in ("V1", "V2", "V3"):
    if variant in results["BANKNIFTY"]:
        mine = results["BANKNIFTY"][variant]["real"]["total"]
        if chk.get(("BANKNIFTY", variant)) != mine:
            resum_ok = False
            print(f"RESUM MISMATCH {variant}: file {chk.get(('BANKNIFTY', variant))} vs run {mine}", flush=True)
results["resum_check"] = "EXACT for all scored Bank books" if resum_ok else "MISMATCH — see log"

# ---- supplementary Nov-13 check: Nov 12 signal from the archived chain
# (pre-open bucket 2026-11-13T05:35 = Nov 12 closes; band @61500 same-band
# deltas from prev_oi; spot +726.10 -> CE LONG_BUILDUP, PE SHORT_BUILDUP)
supp = {"signal_date": "2026-11-12", "source": "option_chain_archive pre-open bucket 2026-11-13T05:35",
        "quadrants": {"CE": "LONG_BUILDUP", "PE": "SHORT_BUILDUP"},
        "directions": {"V1": "CE", "V2": "CE", "V3": None}}
try:
    # 09:20-bar open proxied by the archive's 09:15-bucket spot (the day
    # open, 61,094.55): the ATM strike it selects (61100) is >=44 pts
    # from the rounding boundary, so the strike choice is unaffected.
    arch = {}
    with open(TR / "option_chain_archive/banknifty_2026-11-13.csv") as f:
        for r in csv.DictReader(f):
            if r["bucket_ist"].startswith("2026-11-13T09:15"):
                arch = r
                break
    open920 = float(arch["spot"]) if arch else None
    supp["spot_open_0920"] = open920
    supp["spot_proxy"] = "archive 09:15 bucket spot (day open)"
    if open920:
        strike = int(round(open920 / 100.0)) * 100
        supp["strike"] = strike
        pb, src = obs.prem_bars("BANKNIFTY", "2026-11-23", strike, "CE",
                                "2026-11-13")
        if pb:
            r = obs.replay_g0(pb, 30)
            supp["trade"] = dict(entry=r["entry"], exit=r["exit"],
                                 exit_time=r["exit_time"],
                                 exit_reason=r["exit_reason"],
                                 net=r["net"], store=src)
        else:
            supp["trade"] = "NC — no premium candles"
except obs.RateLimited:
    supp["trade"] = "RATE_LIMIT_STOP"
    results["rate_limited"] = True
except Exception as ex:
    supp["trade"] = f"ERROR {type(ex).__name__}: {ex}"
results["nov13_supplementary"] = supp
print(f"Nov13 supplementary: {supp}", flush=True)

# ---- MERGE test vs TUNED STACK v2 (registered protocol, Part 2B)
stack_rows = list(csv.DictReader(
    open(TR / "solid60_programme_2026-11-13_bank_A_stack_features.csv")))
stack = [{"date": r["date"], "net": float(r["x1_net"])} for r in stack_rows]
stack_days = {l["date"] for l in stack}
stack_total = round(sum(l["net"] for l in stack), 2)
stack_td = len(stack_days)
assert len(stack) == 111 and stack_total == 127351.50, \
    f"stack ledger anchor failed: {len(stack)} legs, {stack_total}"
nov_stack_days = set()
with open(TR / "november_shadow_stack_bank_log.csv") as f:
    for r in csv.DictReader(f):
        if r.get("net_inr"):
            nov_stack_days.add(r["date"])
NOV_STACK_TOTAL = -2680.00
merge = {"stack_anchor": dict(legs=len(stack), total=stack_total,
                              trade_days=stack_td,
                              per_trade_day=round(stack_total / stack_td, 2))}
real_by_variant = {}
with open(TR / "oi_buildup_trades.csv") as f:
    for r in csv.DictReader(f):
        if r["mode"] == "real":
            real_by_variant.setdefault(r["variant"], []).append(r)
for variant in ("V1", "V2", "V3"):
    trades = real_by_variant.get(variant, [])
    gate_trades = [t for t in trades if t["trade_date"] <= "2026-10-31"]
    incr = [t for t in gate_trades if t["trade_date"] not in stack_days]
    incr_total = round(sum(float(t["net"]) for t in incr), 2)
    merged_total = round(stack_total + incr_total, 2)
    merged_days = stack_days | {t["trade_date"] for t in incr}
    months = {}
    all_legs = [(l["date"], l["net"]) for l in stack] + \
               [(t["trade_date"], float(t["net"])) for t in incr]
    for d, n in all_legs:
        months[d[:7]] = round(months.get(d[:7], 0.0) + n, 2)
    nov_legs = [t for t in trades
                if "2026-11-02" <= t["trade_date"] <= "2026-11-12"]
    nov_incr = [t for t in nov_legs if t["trade_date"] not in nov_stack_days]
    nov_merged = round(NOV_STACK_TOTAL +
                       sum(float(t["net"]) for t in nov_incr), 2)
    merge[variant] = dict(
        increment_legs=len(incr), increment_total=incr_total,
        merged_total=merged_total,
        merged_trade_days=len(merged_days),
        merged_per_trade_day=round(merged_total / len(merged_days), 2),
        merged_months=months,
        merged_red_months=[m for m, v in months.items() if v < 0],
        merge_pass=bool(incr_total > 0 and merged_total > stack_total),
        november_family_legs=[{k: t[k] for k in
                               ("signal_date", "trade_date", "direction",
                                "strike", "entry", "exit", "exit_reason",
                                "net")} for t in nov_legs],
        november_increment_legs=[{k: t[k] for k in
                                  ("signal_date", "trade_date", "direction",
                                   "strike", "entry", "exit", "exit_reason",
                                   "net")} for t in nov_incr],
        november_merged_total=nov_merged)
    print(f"MERGE {variant}: incr {len(incr)} legs {incr_total} | merged "
          f"{merged_total} on {len(merged_days)} TD = "
          f"{merge[variant]['merged_per_trade_day']}/TD | Nov merged "
          f"{nov_merged} (family Nov legs {len(nov_legs)}, incr "
          f"{len(nov_incr)})", flush=True)
results["merge"] = merge

(TR / "oi_buildup_results.json").write_text(json.dumps(results, indent=1))
print("re-sum:", results["resum_check"],
      "| results -> oi_buildup_results.json", flush=True)
