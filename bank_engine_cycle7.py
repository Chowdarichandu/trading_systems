#!/usr/bin/env python3
"""Cycle 7 challenger: premium-gated runner on book v3 (BANKNIFTY ONLY).
Legs with entry premium <400 use runner_lock50 exits; >=400 use plain G0.
Full controls: timing audit, placebo (+30min, same gated assembly), halves,
month table, ex-top-3, independent re-sum."""
import csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import candles, score_legs, agg, month_end_reds
from bank_engine_repro import build_v1_legs
from bank_engine_cycle import FILTERS, _entry_premium

TR = Path.home() / "workspace/trading"; SYM = "BANKNIFTY"

def book_v3_legs():
    legs, _, _ = build_v1_legs()
    legs = FILTERS["drop_ns1_ce"](legs)
    legs = FILTERS["drop_prem_400_550"](legs)
    return legs

def score_gated(legs, delay=0):
    res, nc = [], 0
    for l in legs:
        ep = _entry_premium(l)
        mode = "runner_lock50" if (ep is not None and ep < 400.0) else "plain"
        r, n1 = score_legs([l], mode=mode, delay=delay)
        nc += n1; res.extend(r)
    return res, nc

def main():
    legs = book_v3_legs()
    res, nc = score_gated(legs)
    a = agg(res, 40.6); reds, tot, table = month_end_reds(res)
    oct_res = [r for r in res if r["date"][5:7] == "10"]
    aug_res = [r for r in res if r["date"][5:7] == "08"]
    sep_res = [r for r in res if r["date"][5:7] == "09"]
    viol = []; checked = 0
    legmap = {(l["date"], l["direction"], l["entry_time"]): l for l in legs}
    for r in res:
        if r["exit_time"] < r["entry_time"]: viol.append((r["date"], r["entry_time"], "exit before entry"))
        l = legmap.get((r["date"], r["direction"], r["entry_time"]))
        if l is None: viol.append((r["date"], r["entry_time"], "no leg")); continue
        cs = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        bars = [b for b in (cs or []) if b[0] == l["entry_time"]]
        if not bars: viol.append((r["date"], r["entry_time"], "entry bar missing")); continue
        checked += 1
        if abs(bars[0][1] - r["entry"]) > 0.005: viol.append((r["date"], r["entry_time"], "entry premium mismatch"))
    pres, pnc = score_gated(legs, delay=6)
    p_agg = agg(pres, 40.6)
    top3 = sorted(res, key=lambda x: -x["net"])[:3]
    ex_top3 = round(tot - sum(r["net"] for r in top3), 2)
    h1 = round(sum(r["net"] for r in res if r["date"] < "2026-06-01"), 2)
    h2 = round(sum(r["net"] for r in res if r["date"] >= "2026-06-01"), 2)
    out_csv = TR / "bank_engine_cycle7_trades.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date","direction","family","rep","entry_time","entry_premium","exit_time","exit_premium","exit_reason","full_target","net_inr"])
        for r in sorted(res, key=lambda x: (x["date"], x["entry_time"])):
            w.writerow([r["date"], r["direction"], r["family"], r["rep"], r["entry_time"], r["entry"], r["exit_time"], r["exit"], r["exit_reason"], r["ft"], r["net"]])
    s = 0.0; n = 0
    for r in csv.DictReader(open(out_csv)): s += float(r["net_inr"]); n += 1
    summary = dict(cycle="cycle7_challenger_premium_gated_runner", n=a["n"], net=a["net"], ft_pct=a["ft_pct"],
                   per_week=a["per_week"], not_computed=nc,
                   oct_net=round(sum(r["net"] for r in oct_res), 2), aug_net=round(sum(r["net"] for r in aug_res), 2),
                   sep_net=round(sum(r["net"] for r in sep_res), 2),
                   red_month_ends=reds, month_table=table, halves=dict(jan_may=h1, jun_oct=h2),
                   timing_violations=viol, timing_entry_bars_checked=checked,
                   placebo=dict(n=p_agg["n"], net=p_agg["net"], not_computed=pnc),
                   ex_top3_total=ex_top3, top3=[(r["date"], r["direction"], r["net"]) for r in top3],
                   independent_resum=dict(n=n, net=round(s, 2)),
                   resum_matches=(n == a["n"] and abs(round(s, 2) - a["net"]) < 0.005))
    print(json.dumps(summary, indent=1))
    (TR / "bank_engine_cycle7_summary.json").write_text(json.dumps(summary, indent=1))

if __name__ == "__main__":
    main()
