#!/usr/bin/env python3
"""Run-2 Cycle 12: RATCHET-LOCK on book v5 (BANKNIFTY ONLY).
Book v5 = book v4 assembly + Cycle-11 cold-(lA) stand-aside (signal-stream
state). Runner-eligible legs (entry premium <400) get the ratchet: after the
+90 trigger, lock = entry+50; once a later bar's high >= entry+120, the lock
ratchets to entry+90 for subsequent bars; second target entry+150; square-off
15:10; stop before target on every bar. >=400 legs keep plain G0 (their
Cycle-11 scored rows). Sanity: ratchet OFF reproduces book v5 exactly.
Controls: timing audit, placebo (+30 min, same assembly), halves, month
table, ex-top-3, independent re-sum. Premiums only, lot 30, cost Rs220.
"""
import csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import candles, agg, month_end_reds
from bank_engine_run2 import book_v4_legs, score_all, apply_rules
from bank_engine_cycle import _entry_premium

TR = Path.home() / "workspace/trading"
COST, LOT = 220.0, 30

def ratchet_replay(cs, entry_time, delay=0, ratchet=True):
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
            stop2, target2 = entry + 50.0, entry + 150.0
            armed = False
            rest = None
            for b2 in bars[i + 1:]:
                t2, o2, h2, l2, cl2, v2 = b2
                if t2 > "15:10": break
                cur_stop = entry + 90.0 if (ratchet and armed) else stop2
                if l2 <= cur_stop:
                    rest = (cur_stop, "ratchet_stop" if (ratchet and armed) else "runner_stop", t2); break
                if h2 >= target2:
                    rest = (target2, "runner_target150", t2); break
                if ratchet and h2 >= entry + 120.0:
                    armed = True
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

def build_stream(delay=0):
    legs = book_v4_legs()
    scored, nc = score_all(legs, delay=delay)
    stream = sorted(scored.values(), key=lambda x: (x["date"], x["entry_time"]))
    taken, skipped = apply_rules(stream, ["cold_la"])
    return legs, taken, nc

def rescore(taken_legs_keys, legs_by_key, delay=0, ratchet=True):
    out, nc = [], 0
    for key in taken_legs_keys:
        l = legs_by_key[key]
        ep = _entry_premium(l)
        if ep is not None and ep < 400.0:
            cs = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
            r = ratchet_replay(cs, l["entry_time"], delay=delay, ratchet=ratchet)
            if r is None: nc += 1; continue
            r = {**r, "date": l["date"], "direction": l["direction"], "family": l["family"],
                 "rep": l["rep"], "entry_time": l["entry_time"], "leg_key": key}
            out.append(r)
        else:
            # >=400 legs: plain G0 — take from the standard scorer at this delay
            from aggressive_score import score_legs
            r, n1 = score_legs([l], mode="plain", delay=delay)
            nc += n1
            if not r: continue
            row = dict(r[0]); row["leg_key"] = key
            out.append(row)
    return sorted(out, key=lambda x: (x["date"], x["entry_time"])), nc

def main():
    legs = book_v4_legs()
    legs_by_key = {(l["date"], l["direction"], l["entry_time"]): l for l in legs}
    _, taken5, _ = build_stream(delay=0)
    keys5 = [r["leg_key"] for r in taken5]
    # sanity: ratchet OFF on the v5 stream must equal book v5
    off, _ = rescore(keys5, legs_by_key, delay=0, ratchet=False)
    off_agg = agg(off, 40.6)
    assert off_agg["n"] == 82 and abs(off_agg["net"] - 56796.5) < 0.005, f"sanity failed: {off_agg}"
    res, nc = rescore(keys5, legs_by_key, delay=0, ratchet=True)
    a = agg(res, 40.6); reds, tot, table = month_end_reds(res)
    # placebo: delayed stream (cold_la applied on delayed stream), ratchet on
    _, p_taken5, _ = build_stream(delay=6)
    p_keys = [r["leg_key"] for r in p_taken5]
    pres, pnc = rescore(p_keys, legs_by_key, delay=6, ratchet=True)
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
    changed = []
    offmap = {r["leg_key"]: r for r in off}
    for r in res:
        o = offmap.get(r["leg_key"])
        if o and abs(o["net"] - r["net"]) > 0.005:
            changed.append((r["date"], r["direction"], o["exit_reason"], o["net"], r["exit_reason"], r["net"]))
    out_csv = TR / "bank_engine_cycle12_trades.csv"
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
    s = dict(cycle="cycle12_ratchet_lock", sanity_ratchet_off=off_agg,
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
    (TR / "bank_engine_cycle12_summary.json").write_text(json.dumps(s, indent=1))

if __name__ == "__main__":
    main()
