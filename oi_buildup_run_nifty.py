#!/usr/bin/env python3
"""OI BUILD-UP — Nifty run (2026-11-13 evening, Part 5 of the programme).

Mirrors oi_buildup_run_bank.py exactly: the FROZEN scorer imported
unmodified; V3 via the same direction() extension (frozen in Part 2B
before any scoring); the same data-layer repair (a premium series
whose first bar is later than 09:20 is treated as missing and the
frozen fetch route supplies full-day candles). Nifty specifics come
from the frozen scorer itself: front-weekly expiry per the dataset,
S5 exit geometry, lot 65, cost Rs220/trade. Merge incumbent = TUNED v1
(EVE-07), anchor 74 legs / +Rs103,050.25, verified in-run.
Outputs: oi_buildup_trades_nifty.csv; NIFTY + merge_nifty blocks are
merged into oi_buildup_results.json alongside the Bank blocks.
Paper only, real money Rs0. HTTP 429 -> partial results, flagged.
"""
import csv, json
import importlib.util
from pathlib import Path

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

results_path = TR / "oi_buildup_results.json"
results = json.loads(results_path.read_text()) if results_path.exists() else {}
results["NIFTY"] = {}
all_trades = []
oi = obs.load_oi("NIFTY")
try:
    for variant in ("V1", "V2", "V3"):
        entry = {}
        real, nc = obs.run_book("NIFTY", variant, "real", oi)
        entry["real"] = obs.stats(real)
        entry["nc"] = nc
        entry["timing_violations"] = sum(
            1 for t in real if not t["signal_date"] < t["trade_date"])
        for mode in ("reversed", "coin", "shifted"):
            pl, _ = obs.run_book("NIFTY", variant, mode, oi)
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
        results["NIFTY"][variant] = entry
        print(f"NIFTY {variant}: n={s['n']} total={s['total']} "
              f"H=({s['h1']},{s['h2']}) ex3={s['ex_top3']} "
              f"pace={s['pace_per_month']} NC={len(nc)} "
              f"PASS={entry['gate_pass']} legs={legs}", flush=True)
        print(f"   placebos: rev={e['reversed']['total']} "
              f"coin={e['coin']['total']} shift={e['shifted']['total']} "
              f"| NOV n={s['nov_n']} total={s['nov_total']}", flush=True)
except obs.RateLimited:
    print("RATE_LIMIT_STOP during Nifty scoring — partial results",
          flush=True)
    results["rate_limited_nifty"] = True

with open(TR / "oi_buildup_trades_nifty.csv", "w", newline="") as f:
    if all_trades:
        w = csv.DictWriter(f, fieldnames=list(all_trades[0].keys()))
        w.writeheader()
        w.writerows(all_trades)
chk = {}
with open(TR / "oi_buildup_trades_nifty.csv") as f:
    for r in csv.DictReader(f):
        if r["mode"] == "real" and r["trade_date"] <= "2026-10-31":
            k = (r["index"], r["variant"])
            chk[k] = round(chk.get(k, 0.0) + float(r["net"]), 2)
resum_ok = True
for variant in ("V1", "V2", "V3"):
    if variant in results.get("NIFTY", {}):
        mine = results["NIFTY"][variant]["real"]["total"]
        if chk.get(("NIFTY", variant)) != mine:
            resum_ok = False
            print(f"RESUM MISMATCH NIFTY {variant}", flush=True)
results["resum_check_nifty"] = \
    "EXACT for all scored Nifty books" if resum_ok else "MISMATCH — see log"

# ---- MERGE vs TUNED v1 (same registered protocol as Bank Part 2B)
tv1_rows = list(csv.DictReader(
    open(TR / "solid60_programme_2026-11-13_nifty_v1_ALL_X-1_trades.csv")))
tv1 = [{"date": r["date"], "net": float(r["net_inr"])} for r in tv1_rows]
tv1_days = {l["date"] for l in tv1}
tv1_total = round(sum(l["net"] for l in tv1), 2)
assert len(tv1) == 74 and tv1_total == 103050.25, \
    f"TUNED v1 anchor failed: {len(tv1)} legs, {tv1_total}"
NOV_TV1_TOTAL = 3036.50
NOV_TV1_DAYS = {"2026-11-03"}  # its single forward leg (failure audit)
merge = {"tv1_anchor": dict(legs=len(tv1), total=tv1_total,
                            trade_days=len(tv1_days),
                            per_trade_day=round(tv1_total / len(tv1_days), 2))}
real_by_variant = {}
with open(TR / "oi_buildup_trades_nifty.csv") as f:
    for r in csv.DictReader(f):
        if r["mode"] == "real":
            real_by_variant.setdefault(r["variant"], []).append(r)
for variant in ("V1", "V2", "V3"):
    trades = real_by_variant.get(variant, [])
    gate_trades = [t for t in trades if t["trade_date"] <= "2026-10-31"]
    incr = [t for t in gate_trades if t["trade_date"] not in tv1_days]
    incr_total = round(sum(float(t["net"]) for t in incr), 2)
    merged_total = round(tv1_total + incr_total, 2)
    merged_days = tv1_days | {t["trade_date"] for t in incr}
    months = {}
    all_legs = [(l["date"], l["net"]) for l in tv1] + \
               [(t["trade_date"], float(t["net"])) for t in incr]
    for d, n in all_legs:
        months[d[:7]] = round(months.get(d[:7], 0.0) + n, 2)
    nov_legs = [t for t in trades
                if "2026-11-02" <= t["trade_date"] <= "2026-11-12"]
    nov_incr = [t for t in nov_legs if t["trade_date"] not in NOV_TV1_DAYS]
    nov_merged = round(NOV_TV1_TOTAL +
                       sum(float(t["net"]) for t in nov_incr), 2)
    merge[variant] = dict(
        increment_legs=len(incr), increment_total=incr_total,
        merged_total=merged_total,
        merged_trade_days=len(merged_days),
        merged_per_trade_day=round(merged_total / len(merged_days), 2),
        merged_months=months,
        merged_red_months=[m for m, v in months.items() if v < 0],
        merge_pass=bool(incr_total > 0 and merged_total > tv1_total),
        november_family_legs=[{k: t[k] for k in
                               ("signal_date", "trade_date", "direction",
                                "strike", "entry", "exit", "exit_reason",
                                "net")} for t in nov_legs],
        november_increment_legs=[{k: t[k] for k in
                                  ("signal_date", "trade_date", "direction",
                                   "strike", "entry", "exit", "exit_reason",
                                   "net")} for t in nov_incr],
        november_merged_total=nov_merged)
    print(f"MERGE-N {variant}: incr {len(incr)} legs {incr_total} | merged "
          f"{merged_total} on {len(merged_days)} TD = "
          f"{merge[variant]['merged_per_trade_day']}/TD | Nov merged "
          f"{nov_merged} (family Nov legs {len(nov_legs)}, incr "
          f"{len(nov_incr)})", flush=True)
results["merge_nifty"] = merge

results_path.write_text(json.dumps(results, indent=1))
print("re-sum NIFTY:", results["resum_check_nifty"],
      "| results -> oi_buildup_results.json", flush=True)
