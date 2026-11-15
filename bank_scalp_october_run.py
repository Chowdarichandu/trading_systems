#!/usr/bin/env python3
"""October-only scoring of the FROZEN Bank Scalp charter (measurement only).
Mirrors bank_scalp_engine_charter.run_variant and cycle2 (PV1) mechanics verbatim,
iterating October 2026 trade dates only. Prior-day levels resolve via the FULL
calendar inside charter.levels_for (untouched). Placebos restricted to October."""
import sys, json, csv, random
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/trading")
import bank_scalp_engine_core as C
import bank_scalp_engine_charter as H

TR = "/home/hatch/workspace/trading"
OCT = [d for d in C.days() if d.startswith("2026-10")]
CAP = H.CAP  # 8

# ---------- October random placebos (copies with ds restricted to October) ----------
def rand_placebo_spec_oct(n, spec, seed=42, draws=20):
    rng = random.Random(seed); spot = C.load_spot(); totals = []
    for _ in range(draws):
        tot = 0.0; got = 0; tries = 0
        while got < n and tries < n * 30:
            tries += 1
            d = OCT[rng.randrange(len(OCT))]; e = rng.randrange(15, 351)
            direction = rng.choice(("CE", "PE"))
            ref = spot[d]["c"][e - 1]
            if not np.isfinite(ref): continue
            bars = C.opt_day(C.exp_for(d), C.atm(ref), direction, d)
            if bars is None: continue
            r = H.replay_spec(bars, e, spec)
            if r is None: continue
            tot += (r[1] - r[0]) * C.LOT - C.COST; got += 1
        totals.append(round(tot, 2))
    return {"mean": round(sum(totals) / len(totals), 2), "min": min(totals), "max": max(totals)}

def rand_placebo_core_oct(n, tgt, stp, seed=42, draws=20):
    rng = random.Random(seed); spot = C.load_spot(); totals = []
    for _ in range(draws):
        tot = 0.0; got = 0; tries = 0
        while got < n and tries < n * 30:
            tries += 1
            d = OCT[rng.randrange(len(OCT))]; e = rng.randrange(15, 351)
            direction = rng.choice(("CE", "PE"))
            ref = spot[d]["c"][e - 1]
            if not np.isfinite(ref): continue
            bars = C.opt_day(C.exp_for(d), C.atm(ref), direction, d)
            if bars is None: continue
            r = C.replay(bars, e, tgt, stp)
            if r is None: continue
            tot += (r[1] - r[0]) * C.LOT - C.COST; got += 1
        totals.append(round(tot, 2))
    return {"mean": round(sum(totals) / len(totals), 2), "min": min(totals), "max": max(totals)}

# ---------- October summarise (mirrors summarise_charter stats) ----------
def stats_block(trades, sig_ends, lag_tot, rp):
    tot = round(sum(t["net_inr"] for t in trades), 2)
    daynet = {}
    for t in trades: daynet[t["date"]] = daynet.get(t["date"], 0.0) + t["net_inr"]
    dv = sorted(daynet.values())
    wins = sum(1 for t in trades if t["net_inr"] > 0)
    top3 = sorted((t["net_inr"] for t in trades), reverse=True)[:3]
    audit_v = sum(1 for t, se in zip(trades, sig_ends)
                  if t["entry_bar"] != se or not (0 <= t["exit_bar"] - t["entry_bar"] <= 5))
    gross = round(tot + len(trades) * C.COST, 2)
    return {"trades": len(trades), "gross_inr": gross,
            "gross_pts_per_trade": round(gross / (len(trades) * C.LOT), 3) if trades else 0.0,
            "total_inr": tot,
            "win_rate": round(wins / len(trades), 4) if trades else 0.0,
            "days_traded": len(dv),
            "days_green_pct": round(sum(1 for v in dv if v > 0) / len(dv), 4) if dv else 0.0,
            "median_day_inr": round(float(np.median(dv)), 2) if dv else 0.0,
            "worst_day_inr": round(min(dv), 2) if dv else 0.0,
            "best_day_inr": round(max(dv), 2) if dv else 0.0,
            "ex_top3_inr": round(tot - sum(top3), 2),
            "audit_violations": audit_v,
            "lag_placebo_inr": lag_tot, "random_placebo": rp}

def lag_total(trades, sig_ends, scorefn):
    lt = []
    for t, se in zip(trades, sig_ends):
        x = scorefn(t, se)
        if x is not None: lt.append(x)
    return round(sum(x["net_inr"] for x in lt), 2), len(lt)

# ---------- charter variant runner, October days (mirrors run_variant) ----------
def run_oct(label, sigfn, spec):
    spot = C.load_spot(); trades, sig_ends, nc, busy = [], [], 0, 0
    for day in OCT:
        taken, busy_until = 0, -1
        for sig_end, direction in sigfn(day, spot[day]):
            if taken >= CAP: break
            if sig_end <= busy_until: busy += 1; continue
            t = H.score(day, sig_end, direction, spec)
            if t is None: nc += 1; continue
            t["mech"] = label; trades.append(t); sig_ends.append(sig_end)
            taken += 1; busy_until = t["exit_bar"]
    lag, lag_n = lag_total(trades, sig_ends,
                           lambda t, se: H.score(t["date"], se, t["direction"], spec, lag=1))
    rp = rand_placebo_spec_oct(len(trades), spec) if trades else {"mean": 0.0, "min": 0.0, "max": 0.0}
    s = stats_block(trades, sig_ends, lag, rp)
    s.update({"label": label, "not_computed": nc, "busy_skips": busy, "lag_placebo_n": lag_n})
    return s, trades

# ---------- PV1, October days (mirrors cycle2 loop verbatim) ----------
def run_pv1_oct():
    TGT, STP, CAP2, SPACING, VEL = 12.0, 9.0, 4, 10, 10.0
    spot = C.load_spot(); trades, sig_ends, nc = [], [], 0
    for day in OCT:
        sp = spot[day]; exp = C.exp_for(day)
        taken, last_entry = 0, -10**9
        for t in range(15, 341):
            if taken >= CAP2: break
            if (t + 1) - last_entry < SPACING: continue
            sc, sc2 = sp["c"][t], sp["c"][t-2]
            if not (np.isfinite(sc) and np.isfinite(sc2)): continue
            strike = C.atm(sc); fired = None
            for typ, agree in (("CE", sc > sc2), ("PE", sc < sc2)):
                bars = C.opt_day(exp, strike, typ, day)
                if bars is None: continue
                pc, pc2 = bars["c"][t], bars["c"][t-2]
                if np.isfinite(pc) and np.isfinite(pc2) and (pc - pc2) >= VEL and agree:
                    fired = typ; break
            if fired is None: continue
            tr = C.score_signal(day, t + 1, fired, TGT, STP)
            if tr is None: nc += 1; continue
            tr["mech"] = "PV1"; trades.append(tr); sig_ends.append(t + 1)
            taken += 1; last_entry = t + 1
    lag, lag_n = lag_total(trades, sig_ends,
                           lambda t, se: C.score_signal(t["date"], se, t["direction"], TGT, STP, lag=1))
    rp = rand_placebo_core_oct(len(trades), TGT, STP) if trades else {"mean": 0.0, "min": 0.0, "max": 0.0}
    s = stats_block(trades, sig_ends, lag, rp)
    s.update({"label": "PV1", "not_computed": nc, "lag_placebo_n": lag_n})
    return s, trades

COLS = ["variant", "date", "direction", "strike", "expiry", "entry_bar", "entry_premium",
        "exit_bar", "exit_premium", "exit_reason", "net_inr"]

def write_family(rows, path):
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(COLS)
        for label, t in rows:
            w.writerow([label] + [t[c] for c in COLS[1:]])
    back = list(csv.DictReader(open(path)))
    return round(sum(float(r["net_inr"]) for r in back), 2), len(back)

def main():
    print(f"OCT days ({len(OCT)}): {OCT}", flush=True)
    results = {}
    ladder_rows, trail_rows = [], []

    ladder = []
    for base, fn in (("OR1", H.or_signals_1m), ("OR3", H.or_signals_3m),
                     ("LR1", H.lr_signals_1m), ("LR3", H.lr_signals_3m)):
        for tgt in (2.5, 10.0, 12.0, 15.0, 20.0):
            ladder.append((f"{base}-T{str(tgt).replace('.', 'p')}", fn, ("F", tgt, 9.0)))
    for label, fn, spec in ladder:
        s, tr = run_oct(label, fn, spec)
        results[label] = s; ladder_rows += [(label, t) for t in tr]
        print(f"{label}: n={s['trades']} gross={s['gross_inr']} ({s['gross_pts_per_trade']} pts/tr) "
              f"net={s['total_inr']} WR={s['win_rate']} DG={s['days_green_pct']} "
              f"lag={s['lag_placebo_inr']} rand={s['random_placebo']['mean']} "
              f"audit={s['audit_violations']} nc={s['not_computed']}", flush=True)

    for label, td in (("OR1-TRAIL", 5.0), ("OR1-TRAILW", 7.0),
                      ("OR1-TRAILT4", 4.0), ("OR1-TRAILT3", 3.0)):
        s, tr = run_oct(label, H.or_signals_1m, ("T", 8.0, td, 9.0))
        results[label] = s; trail_rows += [(label, t) for t in tr]
        print(f"{label}: n={s['trades']} gross={s['gross_inr']} ({s['gross_pts_per_trade']} pts/tr) "
              f"net={s['total_inr']} WR={s['win_rate']} DG={s['days_green_pct']} "
              f"lag={s['lag_placebo_inr']} rand={s['random_placebo']['mean']} "
              f"audit={s['audit_violations']} nc={s['not_computed']}", flush=True)

    s, tr = run_pv1_oct()
    results["PV1"] = s
    pv_rows = [("PV1", t) for t in tr]
    print(f"PV1: n={s['trades']} gross={s['gross_inr']} ({s['gross_pts_per_trade']} pts/tr) "
          f"net={s['total_inr']} WR={s['win_rate']} DG={s['days_green_pct']} "
          f"lag={s['lag_placebo_inr']} rand={s['random_placebo']['mean']} "
          f"audit={s['audit_violations']} nc={s['not_computed']}", flush=True)

    rs = {}
    rs["ladder"], _ = write_family(ladder_rows, f"{TR}/bank_scalp_oct_OR_ladder.csv")
    rs["trail"], _ = write_family(trail_rows, f"{TR}/bank_scalp_oct_trail.csv")
    rs["pv1"], _ = write_family(pv_rows, f"{TR}/bank_scalp_oct_PV1.csv")
    expect = {"ladder": round(sum(results[k]["total_inr"] for k in results
                                   if k.split("-")[0] in ("OR1", "OR3", "LR1", "LR3") and "TRAIL" not in k), 2),
              "trail": round(sum(results[k]["total_inr"] for k in
                                 ("OR1-TRAIL", "OR1-TRAILW", "OR1-TRAILT4", "OR1-TRAILT3")), 2),
              "pv1": results["PV1"]["total_inr"]}
    resum = {"written_resum": rs, "expected": expect,
             "match": all(abs(rs[k] - expect[k]) < 0.01 for k in rs)}
    print("RESUM:", json.dumps(resum), flush=True)
    json.dump({"oct_days": OCT, "results": results, "resum": resum},
              open(f"{TR}/bank_scalp_october_summary.json", "w"), indent=1)

if __name__ == "__main__":
    main()
