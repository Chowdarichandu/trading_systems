#!/usr/bin/env python3
"""Cycle 8: book v4 (premium-gated runner assembly) + NS3 gap-class add-ons.
BANKNIFTY ONLY. Full controls as in cycles 6/7."""
import csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import candles, score_legs, agg, month_end_reds, EXPIRIES
from bank_engine_repro import build_v1_legs
from bank_engine_cycle import FILTERS, _entry_premium
from bank_engine_cycle7 import score_gated

TR = Path.home() / "workspace/trading"; SYM = "BANKNIFTY"

def book_v3_legs():
    legs, _, _ = build_v1_legs()
    legs = FILTERS["drop_ns1_ce"](legs)
    legs = FILTERS["drop_prem_400_550"](legs)
    return legs

def ns3_addons(v4keys):
    out, nc_legs, band_dropped, key_dropped, sigmap = [], 0, 0, 0, {}
    for r in csv.DictReader(open(TR / "index_options_newsetup_ns3_trades_jan_oct_2026.csv")):
        if r["index"] != SYM: continue
        sigmap[(r["date"], r["direction"], r["entry_time"])] = r["signal_time"]
        if (r["date"], r["direction"]) in v4keys: key_dropped += 1; continue
        strike = int(round(float(r["entry_spot"]) / 100.0) * 100)
        exp = next(e for e in EXPIRIES if e >= r["date"])
        leg = dict(date=r["date"], index=SYM, direction=r["direction"], entry_time=r["entry_time"],
                   strike=strike, expiry=exp, lot=30, rep="NS3_" + r["leg"], sources="NS3",
                   family="NS3_gapclass", base_net=None, base_reason=None)
        ep = _entry_premium(leg)
        if ep is None: nc_legs += 1; continue
        if 400.0 <= ep < 550.0: band_dropped += 1; continue
        out.append(leg)
    return out, nc_legs, band_dropped, key_dropped, sigmap

def score_gated_legs(legs, delay=0):
    res, nc = [], 0
    for l in legs:
        ep = _entry_premium(l)
        mode = "runner_lock50" if (ep is not None and ep < 400.0) else "plain"
        r, n1 = score_legs([l], mode=mode, delay=delay)
        nc += n1; res.extend(r)
    return res, nc

def main():
    v3 = book_v3_legs()
    v4keys = {(l["date"], l["direction"]) for l in v3}
    addons, nc_legs, band_dropped, key_dropped, sigmap = ns3_addons(v4keys)
    legs = sorted(v3 + addons, key=lambda x: (x["date"], x["entry_time"]))
    print(f"v3-pool legs={len(v3)} ns3 addons admitted={len(addons)} (key-dropped={key_dropped}, band-dropped={band_dropped}, no-candles={nc_legs})")
    res, nc = score_gated_legs(legs)
    a = agg(res, 40.6); reds, tot, table = month_end_reds(res)
    oct_res = [r for r in res if r["date"][5:7] == "10"]
    aug_res = [r for r in res if r["date"][5:7] == "08"]
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
        if l["family"] == "NS3_gapclass":
            sig = sigmap.get((l["date"], l["direction"], l["entry_time"]))
            if sig is None: viol.append((r["date"], r["entry_time"], "NS3 signal not found"))
            elif l["entry_time"] < sig: viol.append((r["date"], r["entry_time"], "NS3 entry before signal"))
    pres, pnc = score_gated_legs(legs, delay=6)
    p_agg = agg(pres, 40.6)
    top3 = sorted(res, key=lambda x: -x["net"])[:3]
    ex_top3 = round(tot - sum(r["net"] for r in top3), 2)
    h1 = round(sum(r["net"] for r in res if r["date"] < "2026-06-01"), 2)
    h2 = round(sum(r["net"] for r in res if r["date"] >= "2026-06-01"), 2)
    ns3_res = [r for r in res if r["family"] == "NS3_gapclass"]
    out_csv = TR / "bank_engine_cycle8_trades.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date","direction","family","rep","entry_time","entry_premium","exit_time","exit_premium","exit_reason","full_target","net_inr"])
        for r in sorted(res, key=lambda x: (x["date"], x["entry_time"])):
            w.writerow([r["date"], r["direction"], r["family"], r["rep"], r["entry_time"], r["entry"], r["exit_time"], r["exit"], r["exit_reason"], r["ft"], r["net"]])
    s = 0.0; n = 0
    for r in csv.DictReader(open(out_csv)): s += float(r["net_inr"]); n += 1
    summary = dict(cycle="cycle8_ns3_addons_on_v4", n=a["n"], net=a["net"], ft_pct=a["ft_pct"], per_week=a["per_week"],
                   oct_net=round(sum(r["net"] for r in oct_res), 2), aug_net=round(sum(r["net"] for r in aug_res), 2),
                   red_month_ends=reds, month_table=table, halves=dict(jan_may=h1, jun_oct=h2),
                   timing_violations=viol, timing_entry_bars_checked=checked,
                   placebo=dict(n=p_agg["n"], net=p_agg["net"], not_computed=pnc),
                   ex_top3_total=ex_top3, independent_resum=dict(n=n, net=round(s, 2)),
                   resum_matches=(n == a["n"] and abs(round(s, 2) - a["net"]) < 0.005),
                   ns3_addon_results=dict(n=len(ns3_res), net=round(sum(r["net"] for r in ns3_res), 2),
                                          ft=sum(r["ft"] for r in ns3_res),
                                          trades=[(r["date"], r["direction"], r["net"]) for r in ns3_res]),
                   ns3_not_computed_legs=nc_legs, score_not_computed=nc)
    print(json.dumps(summary, indent=1))
    (TR / "bank_engine_cycle8_summary.json").write_text(json.dumps(summary, indent=1))

if __name__ == "__main__":
    main()
