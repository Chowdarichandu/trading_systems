#!/usr/bin/env python3
"""ROUND 4 SCORER — NIFTY (2026-11-13 night). Mirror of the Bank run:
families D1/T1 frozen identically in new_data_round4_2026-11-13.md
Part 2 (same thresholds — the family is the family; no per-index
retune). Signal read at 11:00 from bars <= 10:55 of the NIFTY
morning-basis dataset; entry = open of the 11:00 bar; strike = ATM
(nearest 50) to the 10:55 spot close; option contract = the front
weekly expiry in force on the trade day (round-1 convention, from
the OI dataset; Nov 12 carries Nov 11's front expiry 2026-11-17 —
the front contract is unchanged until it expires); exits = frozen
S5 with the entry bar moved to 11:00 (stop -50 / BE arm +50 ->
entry / tgt1 +90 -> lock +60 / tgt2 +175 / square-off 15:20);
lot 65; cost Rs220. Placebos: REVERSED / COIN(42) / TIME-SHIFTED
(12:00 entry). Merge incumbent: TUNED v1 (74 legs, +103,050.25).
Premium bars: round 1's machinery + full-coverage repair.
Paper only. On HTTP 429: partial results saved, flagged.
"""
import csv, json, random
import importlib.util
from pathlib import Path

TR = Path.home() / "workspace/trading"
spec = importlib.util.spec_from_file_location(
    "obs", TR / "oi_buildup_score.py")
obs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(obs)

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
LOT = 65

MORN = {}
with open(TR / "round4_history/nifty_morning_basis.csv") as f:
    for r in csv.DictReader(f):
        MORN[r["date"]] = r
OI = obs.load_oi("NIFTY")


def weekly_expiry(day):
    if day in OI:
        return OI[day]["expiry"]
    if day == "2026-11-12":
        return OI["2026-11-11"]["expiry"]
    return None


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


def replay_s5_intraday(bars, entry_time, sq="15:20"):
    """obs.replay_s5 verbatim except the entry bar is a parameter."""
    if not bars:
        return None
    idxs = [i for i, b in enumerate(bars) if b[0] >= entry_time]
    if not idxs:
        return None
    bs = bars[idxs[0]:]
    if bs[0][0] > sq or bs[0][0] != entry_time:
        return None
    entry = bs[0][1]
    stop, target = entry - 50.0, entry + 90.0
    lock, tgt2, arm = 60.0, 175.0, 50.0

    def out(pts, reason, t, ft, px):
        return dict(entry=entry, exit=px, exit_time=t, exit_reason=reason,
                    ft=ft, net=round(pts * LOT - COST, 2))
    cur_stop = stop
    for i, (t, o, h, l, cl) in enumerate(bs):
        if t > sq:
            break
        if l <= cur_stop:
            return out(cur_stop - entry,
                       "be_stop" if cur_stop == entry else "stop", t, 0,
                       cur_stop)
        if h >= target:
            stop2, target2 = entry + lock, entry + tgt2
            for (t2, o2, h2, l2, cl2) in bs[i + 1:]:
                if t2 > sq:
                    break
                if l2 <= stop2:
                    return out(stop2 - entry, "runner_stop", t2, 1, stop2)
                if h2 >= target2:
                    return out(target2 - entry, "runner_target", t2, 1,
                               target2)
                if t2 == sq:
                    return out(cl2 - entry, "runner_square_off", t2, 1, cl2)
            lb = bs[-1]
            return out(lb[4] - entry, "runner_square_off", lb[0], 1, lb[4])
        if (h - entry) >= arm:
            cur_stop = max(cur_stop, entry)
        if t == sq:
            return out(cl - entry, "square_off", t, 0, cl)
    lb = bs[-1]
    return out(lb[4] - entry, "square_off", lb[0], 0, lb[4])


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
        exp = weekly_expiry(d)
        if exp is None:
            nc.append(dict(family=family, mode=mode, trade_date=d,
                           why="no_weekly_expiry"))
            continue
        strike = int(round(float(row["spot_close_1055"]) / 50.0)) * 50
        bars, src = prem_bars_full("NIFTY", exp, strike, dirn, d)
        if not bars:
            nc.append(dict(family=family, mode=mode, trade_date=d,
                           why="no_premium_candles"))
            continue
        r = replay_s5_intraday(bars, entry_time)
        if r is None:
            nc.append(dict(family=family, mode=mode, trade_date=d,
                           why=f"no_{entry_time}_bar"))
            continue
        viol = 0 if (entry_time in ("11:00", "12:00")
                     and row["status"] == "complete") else 1
        trades.append(dict(index="NIFTY", family=family, mode=mode,
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


results = {"scope": "NIFTY — intraday futures basis (surface A mirror)"}
all_trades = []
results["NIFTY"] = {}
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
        results["NIFTY"][family] = entry
        print(f"NIFTY {family}: n={s['n']} total={s['total']} "
              f"H=({s['h1']},{s['h2']}) ex3={s['ex_top3']} "
              f"pace={s['pace_per_month']} NC={len(nc)} "
              f"PASS={entry['gate_pass']} legs={legs}", flush=True)
        print(f"   placebos: rev={e['reversed']['total']} "
              f"coin={e['coin']['total']} shift={e['shifted']['total']} "
              f"| NOV n={s['nov_n']} total={s['nov_total']}", flush=True)
except obs.RateLimited:
    print("RATE_LIMIT_STOP during NIFTY scoring — partial results",
          flush=True)
    results["rate_limited"] = True

with open(TR / "round4_trades_nifty.csv", "w", newline="") as f:
    if all_trades:
        w = csv.DictWriter(f, fieldnames=list(all_trades[0].keys()))
        w.writeheader()
        w.writerows(all_trades)
chk = {}
with open(TR / "round4_trades_nifty.csv") as f:
    for r in csv.DictReader(f):
        if r["mode"] == "real" and r["trade_date"] <= "2026-10-31":
            chk[r["family"]] = round(chk.get(r["family"], 0.0)
                                     + float(r["net"]), 2)
resum_ok = True
for family in ("D1", "T1"):
    if family in results["NIFTY"]:
        mine = results["NIFTY"][family]["real"]["total"]
        if chk.get(family) != mine:
            resum_ok = False
            print(f"RESUM MISMATCH {family}: file {chk.get(family)} "
                  f"vs run {mine}", flush=True)
results["resum_check"] = ("EXACT for all scored Nifty books" if resum_ok
                          else "MISMATCH — see log")

# ---- MERGE vs TUNED v1 (registered protocol)
tv1_rows = list(csv.DictReader(
    open(TR / "solid60_programme_2026-11-13_nifty_v1_ALL_X-1_trades.csv")))
tv1 = [{"date": r["date"], "net": float(r["net_inr"])} for r in tv1_rows]
tv1_days = {l["date"] for l in tv1}
tv1_total = round(sum(l["net"] for l in tv1), 2)
assert len(tv1) == 74 and tv1_total == 103050.25, \
    f"TUNED v1 anchor failed: {len(tv1)} legs, {tv1_total}"
NOV_TV1_TOTAL = 3036.50
NOV_TV1_DAYS = {"2026-11-03"}   # v1's single November leg (round 1)
merge = {"tv1_anchor": dict(legs=len(tv1), total=tv1_total,
                            trade_days=len(tv1_days),
                            per_trade_day=round(tv1_total
                                                / len(tv1_days), 2))}
real_by_family = {}
with open(TR / "round4_trades_nifty.csv") as f:
    for r in csv.DictReader(f):
        if r["mode"] == "real":
            real_by_family.setdefault(r["family"], []).append(r)
for family in ("D1", "T1"):
    trades = real_by_family.get(family, [])
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
    merge[family] = dict(
        increment_legs=len(incr), increment_total=incr_total,
        merged_total=merged_total,
        merged_trade_days=len(merged_days),
        merged_per_trade_day=round(merged_total / len(merged_days), 2),
        merged_months=months,
        merged_red_months=[m for m, v in months.items() if v < 0],
        merge_pass=bool(incr_total > 0 and merged_total > tv1_total),
        november_family_legs=[{k: t[k] for k in
                               ("trade_date", "direction", "strike",
                                "entry", "exit", "exit_reason", "net")}
                              for t in nov_legs],
        november_increment_legs=[{k: t[k] for k in
                                  ("trade_date", "direction", "strike",
                                   "entry", "exit", "exit_reason", "net")}
                                 for t in nov_incr],
        november_merged_total=nov_merged)
    print(f"MERGE NIFTY {family}: incr {len(incr)} legs {incr_total} | "
          f"merged {merged_total} on {len(merged_days)} TD = "
          f"{merge[family]['merged_per_trade_day']}/TD | Nov merged "
          f"{nov_merged} (family Nov legs {len(nov_legs)}, incr "
          f"{len(nov_incr)})", flush=True)
results["merge"] = merge

(TR / "new_data_round4_nifty_results.json").write_text(
    json.dumps(results, indent=1))
print("re-sum:", results["resum_check"],
      "| results -> new_data_round4_nifty_results.json", flush=True)
