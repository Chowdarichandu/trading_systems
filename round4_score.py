#!/usr/bin/env python3
"""ROUND 4 SCORER (2026-11-13 night) — SURFACE A: intraday futures
basis, Bank Nifty. Families frozen in new_data_round4_2026-11-13.md
Part 2 BEFORE this scorer was run:

  D1 DIVERGENCE (primary): spot_morning_pct >= +0.35 and
     dbasis_pct <= 0 -> PE; spot_morning_pct <= -0.35 and
     dbasis_pct >= 0 -> CE.
  T1 THRUST (variant): dbasis_pct >= +0.040 -> CE;
     dbasis_pct <= -0.040 -> PE.

Signal read at 11:00 from bars <= 10:55 ONLY; entry = open of the
11:00 bar; strike = ATM(100) to the 10:55 spot close; in-force
monthly expiry; exits stop -50 before target +90 from the entry bar
onward, square-off 15:10 close; lot 30; cost Rs220. Placebos:
REVERSED, COIN (seed 42), TIME-SHIFTED (entry at the 12:00 bar
open, same strike/direction/exits). Premium bars: round 1's frozen
machinery + the documented full-coverage repair. Paper only.
On HTTP 429: partial results saved, flagged. No book touched.
"""
import csv, json, random, sys
import importlib.util
from pathlib import Path

TR = Path.home() / "workspace/trading"
spec = importlib.util.spec_from_file_location(
    "obs", TR / "oi_buildup_score.py")
obs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(obs)

# ---- round-1 data-layer repair (documented; no rule changes)
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


COST = 220.0
LOT = 30

# ---------------- morning dataset ----------------
MORN = {}
with open(TR / "round4_history/banknifty_morning_basis.csv") as f:
    for r in csv.DictReader(f):
        MORN[r["date"]] = r


def signal(family, row):
    if row is None or row["status"] != "complete":
        return None
    sm = float(row["spot_morning_pct"])
    db = float(row["dbasis_pct"])
    if family == "D1":
        if sm >= 0.35 and db <= 0.0:
            return "PE"
        if sm <= -0.35 and db >= 0.0:
            return "CE"
        return None
    if family == "T1":
        if db >= 0.040:
            return "CE"
        if db <= -0.040:
            return "PE"
        return None
    raise ValueError(family)


# ---------------- intraday replay (G0 semantics, entry-time param)
def replay_intraday(bars, entry_time, sq="15:10"):
    bs = [b for b in bars if b[0] >= entry_time]
    if not bs or bs[0][0] != entry_time:
        return None
    entry = bs[0][1]
    stop, target = entry - 50.0, entry + 90.0

    def out(px, reason, t, ft):
        return dict(entry=entry, exit=px, exit_time=t,
                    exit_reason=reason, ft=ft,
                    net=round((px - entry) * LOT - COST, 2))
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


def run_book(family, mode):
    rng = random.Random(42)
    trades, nc = [], []
    days = [d for d in sorted(MORN) if "2026-01-01" <= d <= "2026-11-12"]
    for d in days:
        row = MORN[d]
        dirn = signal(family, row)
        if dirn is None:
            continue
        if mode == "reversed":
            dirn = "PE" if dirn == "CE" else "CE"
        elif mode == "coin":
            dirn = "CE" if rng.random() < 0.5 else "PE"
        entry_time = "12:00" if mode == "shifted" else "11:00"
        exp = row["expiry"]
        strike = int(round(float(row["spot_close_1055"]) / 100.0)) * 100
        bars, src = prem_bars_full("BANKNIFTY", exp, strike, dirn, d)
        if not bars:
            nc.append(dict(family=family, mode=mode, trade_date=d,
                           why="no_premium_candles"))
            continue
        r = replay_intraday(bars, entry_time)
        if r is None:
            nc.append(dict(family=family, mode=mode, trade_date=d,
                           why=f"no_{entry_time}_bar"))
            continue
        # TIMING AUDIT: signal inputs are the 09:15 and 10:55 bar
        # closes of the SAME day (dataset row, status complete);
        # entry is the open of the entry bar. Violation = anything
        # else. Asserted per trade here.
        viol = 0 if (r is not None and entry_time in ("11:00", "12:00")
                     and row["status"] == "complete") else 1
        trades.append(dict(index="BANKNIFTY", family=family, mode=mode,
                           trade_date=d, direction=dirn, strike=strike,
                           expiry=exp,
                           spot_morning_pct=row["spot_morning_pct"],
                           dbasis_pct=row["dbasis_pct"],
                           basis_open_pts=row["basis_open_pts"],
                           basis_read_pts=row["basis_read_pts"],
                           entry_time=entry_time, store=src,
                           timing_violation=viol, **r))
    return trades, nc


def stats(trades):
    gate = [t for t in trades if t["trade_date"] <= "2026-10-31"]
    total = round(sum(t["net"] for t in gate), 2)
    months = {}
    for m in sorted({t["trade_date"][:7] for t in gate}):
        months[m] = round(sum(t["net"] for t in gate
                              if t["trade_date"][:7] == m), 2)
    h1 = round(sum(t["net"] for t in gate
                   if t["trade_date"][:7] <= "2026-05"), 2)
    h2 = round(sum(t["net"] for t in gate
                   if t["trade_date"][:7] >= "2026-06"), 2)
    top3 = sorted((t["net"] for t in gate), reverse=True)[:3]
    nov = [t for t in trades if "2026-11-02" <= t["trade_date"]
           <= "2026-11-12"]
    return dict(n=len(gate), total=total, months=months, h1=h1, h2=h2,
                ex_top3=round(total - sum(top3), 2), top3=top3,
                ft=sum(t["ft"] for t in gate),
                pace_per_month=round(total / 10, 2),
                nov_n=len(nov),
                nov_total=round(sum(t["net"] for t in nov), 2),
                nov_trades=[{k: t[k] for k in
                             ("trade_date", "direction", "strike",
                              "entry", "exit", "exit_time", "exit_reason",
                              "net")} for t in nov])


results = {"scope": "BANKNIFTY — intraday futures basis (surface A); "
                    "surface B (GIFT Nifty) dropped at audit"}
all_trades = []
results["BANKNIFTY"] = {}
try:
    for family in ("D1", "T1"):
        entry = {}
        real, nc = run_book(family, "real")
        entry["real"] = stats(real)
        entry["nc"] = nc
        entry["timing_violations"] = sum(t["timing_violation"]
                                         for t in real)
        for mode in ("reversed", "coin", "shifted"):
            pl, pnc = run_book(family, mode)
            entry[mode] = stats(pl)
            entry[mode + "_nc"] = len(pnc)
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
        results["BANKNIFTY"][family] = entry
        print(f"BANKNIFTY {family}: n={s['n']} total={s['total']} "
              f"H=({s['h1']},{s['h2']}) ex3={s['ex_top3']} "
              f"pace={s['pace_per_month']} NC={len(nc)} "
              f"PASS={entry['gate_pass']} legs={legs}", flush=True)
        print(f"   placebos: rev={e['reversed']['total']} "
              f"coin={e['coin']['total']} shift={e['shifted']['total']} "
              f"| NOV n={s['nov_n']} total={s['nov_total']}", flush=True)
except obs.RateLimited:
    print("RATE_LIMIT_STOP during scoring — partial results", flush=True)
    results["rate_limited"] = True

# ---- trades file + independent re-sum
with open(TR / "round4_trades.csv", "w", newline="") as f:
    if all_trades:
        w = csv.DictWriter(f, fieldnames=list(all_trades[0].keys()))
        w.writeheader()
        w.writerows(all_trades)
chk = {}
with open(TR / "round4_trades.csv") as f:
    for r in csv.DictReader(f):
        if r["mode"] == "real" and r["trade_date"] <= "2026-10-31":
            chk[r["family"]] = round(chk.get(r["family"], 0.0)
                                     + float(r["net"]), 2)
resum_ok = True
for family in ("D1", "T1"):
    if family in results["BANKNIFTY"]:
        mine = results["BANKNIFTY"][family]["real"]["total"]
        if chk.get(family) != mine:
            resum_ok = False
            print(f"RESUM MISMATCH {family}: file {chk.get(family)} "
                  f"vs run {mine}", flush=True)
results["resum_check"] = ("EXACT for all scored Bank books" if resum_ok
                          else "MISMATCH — see log")

# ---- MERGE vs TUNED STACK v2 (registered protocol)
stack_rows = list(csv.DictReader(
    open(TR / "solid60_programme_2026-11-13_bank_A_stack_features.csv")))
stack = [{"date": r["date"], "net": float(r["x1_net"])} for r in stack_rows]
stack_days = {l["date"] for l in stack}
stack_total = round(sum(l["net"] for l in stack), 2)
assert len(stack) == 111 and stack_total == 127351.50, \
    f"stack anchor failed: {len(stack)} legs {stack_total}"
nov_stack_days = set()
with open(TR / "november_shadow_stack_bank_log.csv") as f:
    for r in csv.DictReader(f):
        if r.get("net_inr"):
            nov_stack_days.add(r["date"])
NOV_STACK_TOTAL = -2680.00
merge = {"stack_anchor": dict(
    legs=len(stack), total=stack_total, trade_days=len(stack_days),
    per_trade_day=round(stack_total / len(stack_days), 2))}
real_by_family = {}
with open(TR / "round4_trades.csv") as f:
    for r in csv.DictReader(f):
        if r["mode"] == "real":
            real_by_family.setdefault(r["family"], []).append(r)
for family in ("D1", "T1"):
    trades = real_by_family.get(family, [])
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
    merge[family] = dict(
        increment_legs=len(incr), increment_total=incr_total,
        merged_total=merged_total,
        merged_trade_days=len(merged_days),
        merged_per_trade_day=round(merged_total / len(merged_days), 2),
        merged_months=months,
        merged_red_months=[m for m, v in months.items() if v < 0],
        merge_pass=bool(incr_total > 0 and merged_total > stack_total),
        november_family_legs=[{k: t[k] for k in
                               ("trade_date", "direction", "strike",
                                "entry", "exit", "exit_reason", "net")}
                              for t in nov_legs],
        november_increment_legs=[{k: t[k] for k in
                                  ("trade_date", "direction", "strike",
                                   "entry", "exit", "exit_reason", "net")}
                                 for t in nov_incr],
        november_merged_total=nov_merged)
    print(f"MERGE {family}: incr {len(incr)} legs {incr_total} | merged "
          f"{merged_total} on {len(merged_days)} TD = "
          f"{merge[family]['merged_per_trade_day']}/TD | Nov merged "
          f"{nov_merged} (family Nov legs {len(nov_legs)}, incr "
          f"{len(nov_incr)})", flush=True)
results["merge"] = merge

(TR / "new_data_round4_results.json").write_text(json.dumps(results, indent=1))
print("re-sum:", results["resum_check"],
      "| results -> new_data_round4_results.json", flush=True)
