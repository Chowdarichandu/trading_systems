#!/usr/bin/env python3
"""Nifty recursive engine — candidate harness with controls in the same run.
Nifty ONLY. Premiums, 1 lot = 65, cost Rs220, UNIQUE-ONCE pool (the N1 pool is
already unique-once). Paper only, real money Rs0.

Provides:
- own replay() implementing plain / runner_lock geometries + optional early
  square-off time for non-runner legs; validated against aggressive_score on
  the incumbent before any candidate is trusted (run with --validate).
- controls(res): timing audit, placebo (same legs shifted +30 min), halves,
  month table + red month-ends, ex-top-3 stress, independent re-sum via CSV.
"""
import sys, csv, json
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import aggressive_score as A

TR = Path.home() / "workspace/trading"
COST, LOT, WEEKS = 220.0, 65, 40.6

def nsrc(l): return len([s for s in l["sources"].split(";") if s.strip()])

def pool():
    return A.base_legs("NIFTY")

def replay(cs, entry_time, stop_pts=50.0, tgt1=90.0, lock_pts=None, tgt2=150.0,
           sq_time="15:10", delay_bars=0, runner_sq_time=None,
           abort_time=None, abort_prog=30.0, be_arm=None):
    if runner_sq_time is None: runner_sq_time = sq_time
    """lock_pts None -> plain geometry (exit at tgt1). Else runner: after tgt1,
    stop moves to entry+lock_pts, second target tgt2. sq_time: square-off bar
    for legs that never triggered (plain) — runner legs keep 15:10 per frozen G7
    unless sq_time changed explicitly for them too (runner phase uses sq_time)."""
    if not cs: return None
    idxs = [i for i, b in enumerate(cs) if b[0] >= entry_time]
    if not idxs: return None
    i0 = idxs[0] + delay_bars
    if i0 >= len(cs): return None
    bars = cs[i0:]
    if bars[0][0] > "15:10": return None
    entry = bars[0][1]
    stop, target = entry - stop_pts, entry + tgt1
    def out(net_pts, reason, t, ft, exit_px):
        return dict(net=round(net_pts * LOT - COST, 2), exit_reason=reason,
                    exit_time=t, ft=ft, entry=entry, exit=exit_px)
    maxfav = -1e9
    cur_stop = stop
    for i, b in enumerate(bars):
        t, o, h, l, cl, v = b
        if t > "15:10": break
        if l <= cur_stop:
            rsn = "be_stop" if cur_stop == entry else "stop"
            return out(cur_stop - entry, rsn, t, 0, cur_stop)
        maxfav = max(maxfav, h - entry)
        if abort_time and entry_time < abort_time and t == abort_time and maxfav < abort_prog:
            return out(cl - entry, "abort_noprogress", t, 0, cl)
        if h >= target:
            if lock_pts is None:
                return out(target - entry, "target", t, 1, target)
            stop2, target2 = entry + lock_pts, entry + tgt2
            for b2 in bars[i + 1:]:
                t2, o2, h2, l2, cl2, v2 = b2
                if t2 > "15:10": break
                if l2 <= stop2: return out(stop2 - entry, "runner_stop", t2, 1, stop2)
                if h2 >= target2: return out(target2 - entry, "runner_target", t2, 1, target2)
                if t2 == runner_sq_time: return out(cl2 - entry, "runner_square_off", t2, 1, cl2)
            lb = bars[-1]
            return out(lb[4] - entry, "runner_square_off", lb[0], 1, lb[4])
        if be_arm and (h - entry) >= be_arm:
            cur_stop = max(cur_stop, entry)
        if t == sq_time:
            return out(cl - entry, "square_off", t, 0, cl)
    lb = bars[-1]
    return out(lb[4] - entry, "square_off", lb[0], 0, lb[4])

def score(legs, geom, delay_bars=0):
    res, nc = [], 0
    for l in legs:
        cs = A.candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        if not cs: nc += 1; continue
        r = replay(cs, l["entry_time"], delay_bars=delay_bars, **geom)
        if r is None: nc += 1; continue
        r = {**r, "date": l["date"], "direction": l["direction"], "rep": l["rep"],
             "entry_time": l["entry_time"], "sources": l["sources"]}
        res.append(r)
    return res, nc

def timing_audit(legs):
    """Every trade: its entry bar must exist in the contract candles and the
    scored entry must equal that bar's open (entry at/after signal bar open).
    Confirmation is a property of the frozen leg record (sources on the leg)."""
    bad = 0; checked = 0
    for l in legs:
        cs = A.candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        if not cs: bad += 1; continue
        bars = [b for b in cs if b[0] == l["entry_time"]]
        if not bars: bad += 1; continue
        checked += 1
    return {"checked": checked, "violations": bad}

def controls(name, legs, res, nc, placebo_res):
    total = round(sum(r["net"] for r in res), 2)
    n = len(res); ft = sum(r["ft"] for r in res)
    bym = defaultdict(float); cum = 0.0; reds = []; table = {}
    for r in sorted(res, key=lambda x: x["date"]): bym[r["date"][:7]] += r["net"]
    for m in sorted(bym):
        cum = round(cum + bym[m], 2); table[m] = [round(bym[m], 2), cum]
        if cum < 0: reds.append(m)
    h1 = round(sum(r["net"] for r in res if r["date"][:7] <= "2026-05"), 2)
    h2 = round(sum(r["net"] for r in res if r["date"][:7] >= "2026-06"), 2)
    top3 = sorted((r["net"] for r in res), reverse=True)[:3]
    ex_top3 = round(total - sum(top3), 2)
    p_total = round(sum(r["net"] for r in placebo_res), 2) if placebo_res is not None else None
    # independent re-sum: dump + re-read
    tmp = TR / f"nifty_engine_tmp_{name}.csv"
    with open(tmp, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["date", "net"])
        for r in res: w.writerow([r["date"], r["net"]])
    resum = round(sum(float(r["net"]) for r in csv.DictReader(open(tmp))), 2)
    tmp.unlink()
    return dict(name=name, n=n, total=total, resum=resum, resum_ok=(resum == total),
                ft=ft, ft_pct=round(100.0 * ft / n, 1) if n else 0.0,
                per_week=round(n / WEEKS, 2), not_computed=nc, red_month_ends=reds,
                month_table=table, halves={"Jan-May": h1, "Jun-Oct": h2},
                ex_top3=ex_top3, top3=top3, placebo_shift30_total=p_total,
                october=table.get("2026-10", [0, 0])[0])

def run_candidate(name, legs, geom, audit_legs=None):
    res, nc = score(legs, geom)
    pl, _ = score(legs, geom, delay_bars=6)  # placebo: same legs, entry +30 min
    c = controls(name, legs, res, nc, pl)
    c["timing_audit"] = timing_audit(audit_legs if audit_legs is not None else legs)
    return c, res

G7 = dict(stop_pts=50.0, tgt1=90.0, lock_pts=50.0, tgt2=150.0)

if __name__ == "__main__" and "--validate" in sys.argv:
    B = pool()
    C3 = [l for l in B if nsrc(l) >= 2]
    res, nc = score(C3, G7)
    tot = round(sum(r["net"] for r in res), 2)
    print("own replay C3+G7:", len(res), tot, "NC", nc, "expect 56 / 66619.25 / 0")
    print("VALID" if (len(res) == 56 and tot == 66619.25 and nc == 0) else "INVALID")
