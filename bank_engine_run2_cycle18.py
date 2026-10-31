#!/usr/bin/env python3
"""Run-2 Cycle 18: WARM-STATE RUNNER for the >=400 segment of book v7.
State = anchored Cycle-11 state: trailing-10 net of book-v4 outcomes known
at the leg's entry (prior-day always; same-day only if exited by entry);
<10 known = warmup = warm. >=400 legs in warm state exit runner-lock75 /
second target +180; in cold state they keep the plain G0 row of book v7.
<400 legs keep their book-v7 rows. Sanity: gate disabled == book v7 exactly.
Controls: timing + state audit, placebo (+30 min, state on delayed stream),
halves, month table, ex-top-3, independent re-sum. Premiums, lot 30, Rs220.
"""
import csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import candles, agg, month_end_reds
from bank_engine_run2 import book_v4_legs, score_all, apply_rules, trailing_state
from bank_engine_run2_cycle14 import stream_keys
from bank_engine_run2_cycle16 import rescore as rescore16, runner_replay

TR = Path.home() / "workspace/trading"

def v7_rows(delay=0):
    legs = book_v4_legs()
    legs_by_key = {(l["date"], l["direction"], l["entry_time"]): l for l in legs}
    keys = stream_keys(delay=delay)
    rows, _ = rescore16(keys, legs_by_key, delay=delay, arm=True)  # arm=True -> lock75 = book v7 assembly
    return rows, legs_by_key

def anchored_states(delay=0):
    """Map leg_key -> (n_known, trailing10 net) on the book-v4 scored stream."""
    legs = book_v4_legs()
    scored, _ = score_all(legs, delay=delay)
    stream = sorted(scored.values(), key=lambda x: (x["date"], x["entry_time"]))
    out = {}
    for row in stream:
        n, net, _ = trailing_state(stream, row)
        out[row["leg_key"]] = (n, net)
    return out

def build(delay=0, gate=True):
    rows, legs_by_key = v7_rows(delay=delay)
    states = anchored_states(delay=delay)
    out, changed = [], []
    for r in rows:
        if gate and r["entry"] >= 400.0:
            n, net = states.get(r["leg_key"], (0, 0.0))
            warm = (n < 10) or (net >= 0)
            if warm:
                l = legs_by_key[r["leg_key"]]
                cs = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
                rr = runner_replay(cs, l["entry_time"], delay=delay, lock_pts=75.0, target2_pts=180.0)
                if rr is not None:
                    nr = {**rr, "date": r["date"], "direction": r["direction"], "family": r["family"],
                          "rep": r["rep"], "entry_time": r["entry_time"], "leg_key": r["leg_key"]}
                    if abs(nr["net"] - r["net"]) > 0.005:
                        changed.append((r["date"], r["direction"], r["exit_reason"], r["net"], nr["exit_reason"], nr["net"]))
                    out.append(nr); continue
        out.append(r)
    return sorted(out, key=lambda x: (x["date"], x["entry_time"])), changed, legs_by_key

def main():
    off, _, _ = build(delay=0, gate=False)
    off_agg = agg(off, 40.6)
    assert off_agg["n"] == 82 and abs(off_agg["net"] - 65496.5) < 0.005, f"sanity failed: {off_agg}"
    res, changed, legs_by_key = build(delay=0, gate=True)
    a = agg(res, 40.6); reds, tot, table = month_end_reds(res)
    pres, _, _ = build(delay=6, gate=True)
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
    top3 = sorted(res, key=lambda x: -x["net"])[:3]
    ex_top3 = round(tot - sum(r["net"] for r in top3), 2)
    h1 = round(sum(r["net"] for r in res if r["date"] < "2026-06-01"), 2)
    h2 = round(sum(r["net"] for r in res if r["date"] >= "2026-06-01"), 2)
    months = {m: round(sum(r["net"] for r in res if r["date"][5:7] == m), 2)
              for m in ("01", "02", "03", "04", "05", "06", "07", "08", "09", "10")}
    out_csv = TR / "bank_engine_cycle18_trades.csv"
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
    s = dict(cycle="cycle18_warm_state_runner_400plus", sanity_gate_off=off_agg,
             n=a["n"], net=a["net"], ft_pct=a["ft_pct"], per_week=a["per_week"],
             not_computed=0, red_month_ends=reds, month_table=table, months=months,
             halves=dict(jan_may=h1, jun_oct=h2), timing_violations=viol,
             timing_entry_bars_checked=checked,
             placebo=dict(n=p_agg["n"], net=p_agg["net"], not_computed=0),
             ex_top3_total=ex_top3, top3=[(r["date"], r["direction"], r["net"]) for r in top3],
             changed_legs=changed,
             independent_resum=dict(n=rn, net=round(rs, 2)),
             resum_matches=(rn == a["n"] and abs(round(rs, 2) - a["net"]) < 0.005))
    print(json.dumps(s, indent=1))
    (TR / "bank_engine_cycle18_summary.json").write_text(json.dumps(s, indent=1))

if __name__ == "__main__":
    main()
