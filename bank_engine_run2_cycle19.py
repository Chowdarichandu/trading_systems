#!/usr/bin/env python3
"""Run-2 Cycle 19: RUNNER SECOND TARGET +210 (book-wide) on book v8.
Assembly rebuilt at a parameterised second target T: <400 legs ->
runner-lock75/T; >=400 legs -> warm-state (anchored Cycle-11 state on the
book-v4 stream) runner-lock75/T, cold-state plain G0. Sanity: T=180 must
reproduce book v8 exactly (+77,196.50, 82 trades). Controls: timing audit,
placebo (+30 min), halves, month table, ex-top-3, independent re-sum.
Premiums only, lot 30, cost Rs220, UNIQUE-ONCE.
"""
import csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import candles, agg, month_end_reds
from bank_engine_run2 import book_v4_legs
from bank_engine_run2_cycle14 import stream_keys
from bank_engine_run2_cycle16 import runner_replay
from bank_engine_run2_cycle14 import be_replay
from bank_engine_run2_cycle18 import anchored_states
from bank_engine_cycle import _entry_premium

TR = Path.home() / "workspace/trading"

def build(delay=0, target2=210.0):
    legs = book_v4_legs()
    legs_by_key = {(l["date"], l["direction"], l["entry_time"]): l for l in legs}
    keys = stream_keys(delay=delay)
    states = anchored_states(delay=delay)
    out, nc, changed = [], 0, []
    for key in keys:
        l = legs_by_key[key]
        ep = _entry_premium(l)
        cs = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        if ep is not None and ep < 400.0:
            r = runner_replay(cs, l["entry_time"], delay=delay, lock_pts=75.0, target2_pts=target2)
        else:
            n, net = states.get(key, (0, 0.0))
            warm = (n < 10) or (net >= 0)
            if warm:
                r = runner_replay(cs, l["entry_time"], delay=delay, lock_pts=75.0, target2_pts=target2)
            else:
                r = be_replay(cs, l["entry_time"], delay=delay, arm=False)
        if r is None: nc += 1; continue
        r = {**r, "date": l["date"], "direction": l["direction"], "family": l["family"],
             "rep": l["rep"], "entry_time": l["entry_time"], "leg_key": key}
        out.append(r)
    return sorted(out, key=lambda x: (x["date"], x["entry_time"])), nc, legs_by_key

def main():
    off, _, _ = build(delay=0, target2=180.0)
    off_agg = agg(off, 40.6)
    assert off_agg["n"] == 82 and abs(off_agg["net"] - 77196.5) < 0.005, f"sanity failed: {off_agg}"
    res, nc, legs_by_key = build(delay=0, target2=210.0)
    a = agg(res, 40.6); reds, tot, table = month_end_reds(res)
    pres, pnc, _ = build(delay=6, target2=210.0)
    p_agg = agg(pres, 40.6)
    viol, checked = [], 0
    for r in res:
        if r["exit_time"] < r["entry_time"]:
            viol.append((r["date"], r["entry_time"], "exit before entry"))
        l = legs_by_key[r["leg_key"]]
        cs = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        bars = [b for b in (cs or []) if b[0] == r["entry_time"]]
        if not bars: viol.append((r["date"], r["entry_time"], "entry bar missing")); continue
        checked += 1
        if abs(bars[0][1] - r["entry"]) > 0.005:
            viol.append((r["date"], r["entry_time"], "entry premium mismatch"))
    offmap = {r["leg_key"]: r for r in off}
    changed = [(r["date"], r["direction"], offmap[r["leg_key"]]["exit_reason"], offmap[r["leg_key"]]["net"],
                r["exit_reason"], r["net"]) for r in res
               if abs(offmap[r["leg_key"]]["net"] - r["net"]) > 0.005]
    top3 = sorted(res, key=lambda x: -x["net"])[:3]
    ex_top3 = round(tot - sum(r["net"] for r in top3), 2)
    h1 = round(sum(r["net"] for r in res if r["date"] < "2026-06-01"), 2)
    h2 = round(sum(r["net"] for r in res if r["date"] >= "2026-06-01"), 2)
    months = {m: round(sum(r["net"] for r in res if r["date"][5:7] == m), 2)
              for m in ("01", "02", "03", "04", "05", "06", "07", "08", "09", "10")}
    out_csv = TR / "bank_engine_cycle19_trades.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "direction", "family", "rep", "entry_time", "entry_premium",
                    "exit_time", "exit_premium", "exit_reason", "full_target", "net_inr"])
        for r in res:
            w.writerow([r["date"], r["direction"], r["family"], r["rep"], r["entry_time"],
                        r["entry"], r["exit_time"], r["exit"], r["exit_reason"], r["ft"], r["net"]])
    rs, rn = 0.0, 0
    for r in csv.DictReader(open(out_csv)):
        rs += float(r["net_inr"]); rn += 1
    s = dict(cycle="cycle19_runner_tgt2_210", sanity_tgt180=off_agg,
             n=a["n"], net=a["net"], ft_pct=a["ft_pct"], per_week=a["per_week"],
             not_computed=nc, red_month_ends=reds, month_table=table, months=months,
             halves=dict(jan_may=h1, jun_oct=h2), timing_violations=viol,
             timing_entry_bars_checked=checked,
             placebo=dict(n=p_agg["n"], net=p_agg["net"], not_computed=pnc),
             ex_top3_total=ex_top3, top3=[(r["date"], r["direction"], r["net"]) for r in top3],
             changed_legs=changed,
             independent_resum=dict(n=rn, net=round(rs, 2)),
             resum_matches=(rn == a["n"] and abs(round(rs, 2) - a["net"]) < 0.005))
    print(json.dumps(s, indent=1))
    (TR / "bank_engine_cycle19_summary.json").write_text(json.dumps(s, indent=1))

if __name__ == "__main__":
    main()
