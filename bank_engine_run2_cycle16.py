#!/usr/bin/env python3
"""Run-2 Cycle 16: RUNNER LOCK +75 on book v6 (BANKNIFTY ONLY).
Book v6 stream = book v4 assembly + cold-(lA) stand-aside; exits per leg:
entry premium <400 -> runner-lock50 with second target +180 (banked C13);
>=400 -> plain G0 plus, when arm=True, break-even arm: from the bar after
the first bar with high >= entry+50, the stop moves entry-50 -> entry.
Sanity: arm=False reproduces book v6 exactly (+61,896.50, 82 trades).
Controls: timing audit, placebo (+30 min), halves, month table, ex-top-3,
independent re-sum. Premiums only, lot 30, cost Rs220, UNIQUE-ONCE.
"""
import csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import candles, score_legs, agg, month_end_reds
from bank_engine_run2 import book_v4_legs, score_all, apply_rules
from bank_engine_run2_cycle13 import ratchet_replay
from bank_engine_cycle import _entry_premium

TR = Path.home() / "workspace/trading"
COST, LOT = 220.0, 30


def runner_replay(cs, entry_time, delay=0, lock_pts=50.0, target2_pts=180.0):
    if not cs: return None
    idxs = [i for i, b in enumerate(cs) if b[0] >= entry_time]
    if not idxs: return None
    i0 = idxs[0] + delay
    if i0 >= len(cs): return None
    bars = cs[i0:]
    if bars[0][0] > "15:10": return None
    entry = bars[0][1]
    stop, target = entry - 50.0, entry + 90.0
    def sq(b):
        return dict(net=round((b[4] - entry) * LOT - COST, 2), exit_reason="square_off",
                    exit_time=b[0], ft=0, entry=entry, exit=b[4])
    for i, b in enumerate(bars):
        t, o, h, l, cl, v = b
        if t > "15:10": break
        if l <= stop:
            return dict(net=round((stop - entry) * LOT - COST, 2), exit_reason="stop",
                        exit_time=t, ft=0, entry=entry, exit=stop)
        if h >= target:
            stop2, target2 = entry + lock_pts, entry + target2_pts
            rest = None
            for b2 in bars[i + 1:]:
                t2, o2, h2, l2, cl2, v2 = b2
                if t2 > "15:10": break
                if l2 <= stop2:
                    rest = (stop2, "runner_stop", t2); break
                if h2 >= target2:
                    rest = (target2, "runner_target180", t2); break
                if t2 == "15:10":
                    rest = (cl2, "runner_square_off", t2); break
            if rest is None:
                lb = bars[-1]; rest = (lb[4], "runner_square_off", lb[0])
            return dict(net=round((rest[0] - entry) * LOT - COST, 2), exit_reason=rest[1],
                        exit_time=rest[2], ft=1, entry=entry, exit=rest[0])
        if t == "15:10":
            return sq(b)
    lb = bars[-1]
    return sq(lb)

def be_replay(cs, entry_time, delay=0, arm=True):
    if not cs: return None
    idxs = [i for i, b in enumerate(cs) if b[0] >= entry_time]
    if not idxs: return None
    i0 = idxs[0] + delay
    if i0 >= len(cs): return None
    bars = cs[i0:]
    if bars[0][0] > "15:10": return None
    entry = bars[0][1]
    target = entry + 90.0
    armed = False
    def sq(b):
        return dict(net=round((b[4] - entry) * LOT - COST, 2), exit_reason="square_off",
                    exit_time=b[0], ft=0, entry=entry, exit=b[4])
    for b in bars:
        t, o, h, l, cl, v = b
        if t > "15:10": break
        cur_stop = entry if (arm and armed) else entry - 50.0
        if l <= cur_stop:
            reason = "be_arm_stop" if (arm and armed) else "stop"
            return dict(net=round((cur_stop - entry) * LOT - COST, 2), exit_reason=reason,
                        exit_time=t, ft=0, entry=entry, exit=cur_stop)
        if h >= target:
            return dict(net=round((target - entry) * LOT - COST, 2), exit_reason="target",
                        exit_time=t, ft=1, entry=entry, exit=target)
        if arm and h >= entry + 50.0:
            armed = True
        if t == "15:10":
            return sq(b)
    lb = bars[-1]
    return sq(lb)

def stream_keys(delay=0):
    legs = book_v4_legs()
    scored, _ = score_all(legs, delay=delay)
    stream = sorted(scored.values(), key=lambda x: (x["date"], x["entry_time"]))
    taken, _ = apply_rules(stream, ["cold_la"])
    return [r["leg_key"] for r in taken]

def rescore(keys, legs_by_key, delay=0, arm=True):
    lock_pts = 75.0 if arm else 50.0
    out, nc = [], 0
    for key in keys:
        l = legs_by_key[key]
        ep = _entry_premium(l)
        cs = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        if ep is not None and ep < 400.0:
            r = runner_replay(cs, l["entry_time"], delay=delay, lock_pts=lock_pts, target2_pts=180.0)
        else:
            r = be_replay(cs, l["entry_time"], delay=delay, arm=False)
        if r is None: nc += 1; continue
        r = {**r, "date": l["date"], "direction": l["direction"], "family": l["family"],
             "rep": l["rep"], "entry_time": l["entry_time"], "leg_key": key}
        out.append(r)
    return sorted(out, key=lambda x: (x["date"], x["entry_time"])), nc

def main():
    legs = book_v4_legs()
    legs_by_key = {(l["date"], l["direction"], l["entry_time"]): l for l in legs}
    keys = stream_keys(delay=0)
    off, _ = rescore(keys, legs_by_key, delay=0, arm=False)
    off_agg = agg(off, 40.6)
    assert off_agg["n"] == 82 and abs(off_agg["net"] - 61896.5) < 0.005, f"sanity failed: {off_agg}"
    res, nc = rescore(keys, legs_by_key, delay=0, arm=True)
    a = agg(res, 40.6); reds, tot, table = month_end_reds(res)
    p_keys = stream_keys(delay=6)
    pres, pnc = rescore(p_keys, legs_by_key, delay=6, arm=True)
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
    offmap = {r["leg_key"]: r for r in off}
    changed = [(r["date"], r["direction"], offmap[r["leg_key"]]["exit_reason"], offmap[r["leg_key"]]["net"],
                r["exit_reason"], r["net"]) for r in res
               if abs(offmap[r["leg_key"]]["net"] - r["net"]) > 0.005]
    out_csv = TR / "bank_engine_cycle16_trades.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "direction", "family", "rep", "entry_time", "entry_premium",
                    "exit_time", "exit_premium", "exit_reason", "full_target", "net_inr"])
        for r in sorted(res, key=lambda x: (x["date"], x["entry_time"])):
            w.writerow([r["date"], r["direction"], r["family"], r["rep"], r["entry_time"],
                        r["entry"], r["exit_time"], r["exit"], r["exit_reason"], r["ft"], r["net"]])
    rs, rn = 0.0, 0
    for r in csv.DictReader(open(out_csv)):
        rs += float(r["net_inr"]); rn += 1
    s = dict(cycle="cycle16_runner_lock75", sanity_lock50=off_agg,
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
    (TR / "bank_engine_cycle16_summary.json").write_text(json.dumps(s, indent=1))

if __name__ == "__main__":
    main()
