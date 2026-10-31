#!/usr/bin/env python3
"""Cycle 6 challenger: book v3 + NS4 or_rebreak add-on legs (BANKNIFTY ONLY).
Controls identical to bank_engine_cycle.py: timing audit (incl. NS4 signal times),
placebo +30min, halves, month table, ex-top-3, independent re-sum."""
import csv, json, sys
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import candles, score_legs, agg, month_end_reds, EXPIRIES
from bank_engine_repro import build_v1_legs
from bank_engine_cycle import FILTERS, _entry_premium

TR = Path.home() / "workspace/trading"; SYM = "BANKNIFTY"

def book_v3_legs():
    legs, _, _ = build_v1_legs()
    legs = FILTERS["drop_ns1_ce"](legs)
    legs = FILTERS["drop_prem_400_550"](legs)
    return legs

def ns4_addons(v3keys):
    out, nc_legs, band_dropped, key_dropped = [], 0, 0, 0
    sigmap = {}
    for r in csv.DictReader(open(TR / "index_options_newsetup_ns4_trades_jan_oct_2026.csv")):
        if r["index"] != SYM: continue
        sigmap[(r["date"], r["direction"], r["entry_time"])] = r["signal_time"]
        if (r["date"], r["direction"]) in v3keys: key_dropped += 1; continue
        strike = int(round(float(r["entry_spot"]) / 100.0) * 100)
        exp = next(e for e in EXPIRIES if e >= r["date"])
        leg = dict(date=r["date"], index=SYM, direction=r["direction"], entry_time=r["entry_time"],
                   strike=strike, expiry=exp, lot=30, rep="NS4", sources="NS4_or_rebreak",
                   family="NS4_or_rebreak", base_net=None, base_reason=None)
        ep = _entry_premium(leg)
        if ep is None: nc_legs += 1; continue
        if 400.0 <= ep < 550.0: band_dropped += 1; continue
        out.append(leg)
    return out, nc_legs, band_dropped, key_dropped, sigmap

def main():
    v3 = book_v3_legs()
    v3keys = {(l["date"], l["direction"]) for l in v3}
    addons, nc_legs, band_dropped, key_dropped, sigmap = ns4_addons(v3keys)
    legs = sorted(v3 + addons, key=lambda x: (x["date"], x["entry_time"]))
    print(f"v3 legs={len(v3)} ns4 addons admitted={len(addons)} (key-dropped={key_dropped}, band-dropped={band_dropped}, no-candles={nc_legs})")
    res, nc = score_legs(legs)
    a = agg(res, 40.6); reds, tot, table = month_end_reds(res)
    oct_res = [r for r in res if r["date"][5:7] == "10"]
    aug_res = [r for r in res if r["date"][5:7] == "08"]
    # timing audit
    viol = []
    legmap = {(l["date"], l["direction"], l["entry_time"]): l for l in legs}
    checked = 0
    for r in res:
        if r["exit_time"] < r["entry_time"]: viol.append((r["date"], r["entry_time"], "exit before entry"))
        l = legmap.get((r["date"], r["direction"], r["entry_time"]))
        if l is None: viol.append((r["date"], r["entry_time"], "no leg")); continue
        cs = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        bars = [b for b in (cs or []) if b[0] == l["entry_time"]]
        if not bars: viol.append((r["date"], r["entry_time"], "entry bar missing")); continue
        checked += 1
        if abs(bars[0][1] - r["entry"]) > 0.005: viol.append((r["date"], r["entry_time"], "entry premium mismatch"))
        if l["family"] == "NS4_or_rebreak":
            sig = sigmap.get((l["date"], l["direction"], l["entry_time"]))
            if sig is None: viol.append((r["date"], r["entry_time"], "NS4 signal not found"))
            elif l["entry_time"] < sig: viol.append((r["date"], r["entry_time"], "NS4 entry before signal"))
    pres, pnc = score_legs(legs, delay=6)
    p_agg = agg(pres, 40.6)
    top3 = sorted(res, key=lambda x: -x["net"])[:3]
    ex_top3 = round(tot - sum(r["net"] for r in top3), 2)
    h1 = round(sum(r["net"] for r in res if r["date"] < "2026-06-01"), 2)
    h2 = round(sum(r["net"] for r in res if r["date"] >= "2026-06-01"), 2)
    ns4_res = [r for r in res if r["family"] == "NS4_or_rebreak"]
    out_csv = TR / "bank_engine_cycle6_trades.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date","direction","family","rep","entry_time","entry_premium","exit_time","exit_premium","exit_reason","full_target","net_inr"])
        for r in sorted(res, key=lambda x: (x["date"], x["entry_time"])):
            w.writerow([r["date"], r["direction"], r["family"], r["rep"], r["entry_time"], r["entry"], r["exit_time"], r["exit"], r["exit_reason"], r["ft"], r["net"]])
    s = 0.0; n = 0
    for r in csv.DictReader(open(out_csv)): s += float(r["net_inr"]); n += 1
    summary = dict(cycle="cycle6_challenger_ns4", n=a["n"], net=a["net"], ft_pct=a["ft_pct"], per_week=a["per_week"],
                   oct_net=round(sum(r["net"] for r in oct_res), 2), aug_net=round(sum(r["net"] for r in aug_res), 2),
                   red_month_ends=reds, month_table=table, halves=dict(jan_may=h1, jun_oct=h2),
                   timing_violations=viol, timing_entry_bars_checked=checked,
                   placebo=dict(n=p_agg["n"], net=p_agg["net"], not_computed=pnc),
                   ex_top3_total=ex_top3, independent_resum=dict(n=n, net=round(s, 2)),
                   resum_matches=(n == a["n"] and abs(round(s, 2) - a["net"]) < 0.005),
                   ns4_addon_results=dict(n=len(ns4_res), net=round(sum(r["net"] for r in ns4_res), 2),
                                          ft=sum(r["ft"] for r in ns4_res)),
                   ns4_not_computed_legs=nc_legs, score_not_computed=nc)
    print(json.dumps(summary, indent=1))
    (TR / "bank_engine_cycle6_summary.json").write_text(json.dumps(summary, indent=1))

if __name__ == "__main__":
    main()
