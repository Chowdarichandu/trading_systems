#!/usr/bin/env python3
"""Bank recursive engine — one cycle scorer with full controls (BANKNIFTY ONLY).
Usage: python3 bank_engine_cycle.py <cycle_id> <stop> <target> <mode> <filter_name>
Controls in the same run: timing audit (every trade), placebo (same legs/geometry,
entry +30 min), halves Jan-May/Jun-Oct, month table + month-end closes, ex-top-3
stress, independent re-sum from the written trades CSV. Premiums only, lot 30,
cost Rs220, UNIQUE-ONCE (inherited from the V1 leg construction)."""
import csv, json, sys
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import candles, score_legs, agg, month_end_reds
from bank_engine_repro import build_v1_legs

TR = Path.home() / "workspace/trading"
SYM = "BANKNIFTY"
JANOCT_WEEKS = 40.6

FILTERS = {
    "none": lambda legs: legs,
    "entries_le_1330": lambda legs: [l for l in legs if l["entry_time"] <= "13:30"],
    "entries_le_1230": lambda legs: [l for l in legs if l["entry_time"] <= "12:30"],
    "no_09_entries": lambda legs: [l for l in legs if l["entry_time"] >= "10:00"],
    "drop_ns1_ce": lambda legs: [l for l in legs if not (l["family"].startswith("NS1") and l["direction"] == "CE")],
}

def _entry_premium(leg):
    cs = candles(leg["index"], leg["strike"], leg["direction"], leg["date"], leg["expiry"])
    if not cs: return None
    bars = [b for b in cs if b[0] == leg["entry_time"]]
    return bars[0][1] if bars else None

def _drop_prem_band(legs):
    out = []
    for l in legs:
        ep = _entry_premium(l)
        if ep is not None and 400.0 <= ep < 550.0: continue
        out.append(l)
    return out

FILTERS["drop_prem_400_550"] = _drop_prem_band

def signal_map():
    m = {}
    for r in csv.DictReader(open(TR / "index_options_newsetup_premium_october_trades.csv")):
        if r["index"] == SYM and r["family"] == "NS1" and r["leg"] == "second":
            m[(r["date"], r["direction"], r["entry_time"])] = r["signal_time"]
    for r in csv.DictReader(open(TR / "index_options_newsetup_ns1_trades_jan_oct_2026.csv")):
        if r["index"] == SYM and r["leg"] == "second" and r["date"] < "2026-10-01":
            m[(r["date"], r["direction"], r["entry_time"])] = r["signal_time"]
    return m

def timing_audit(legs, res):
    smap = signal_map()
    viol = []
    checked_entry_bar = 0
    for r in res:
        if r["exit_time"] < r["entry_time"]:
            viol.append((r["date"], r["entry_time"], "exit before entry"))
    legmap = {(l["date"], l["direction"], l["entry_time"]): l for l in legs}
    for r in res:
        l = legmap.get((r["date"], r["direction"], r["entry_time"]))
        if l is None:
            viol.append((r["date"], r["entry_time"], "result has no leg")); continue
        cs = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        bars = [b for b in (cs or []) if b[0] == l["entry_time"]]
        if not bars:
            viol.append((r["date"], r["entry_time"], "entry bar missing from candles")); continue
        checked_entry_bar += 1
        if abs(bars[0][1] - r["entry"]) > 0.005:
            viol.append((r["date"], r["entry_time"], "entry premium != open of entry bar"))
        if l["family"].startswith("NS1"):
            sig = smap.get((l["date"], l["direction"], l["entry_time"]))
            if sig is None:
                viol.append((r["date"], r["entry_time"], "NS1 signal time not found"))
            elif l["entry_time"] < sig:
                viol.append((r["date"], r["entry_time"], "NS1 entry before signal"))
    return viol, checked_entry_bar

def halves(res):
    h1 = round(sum(r["net"] for r in res if r["date"] < "2026-06-01"), 2)
    h2 = round(sum(r["net"] for r in res if r["date"] >= "2026-06-01"), 2)
    return h1, h2

def run(cycle_id, stop, target, mode, filter_name, base_filter="none"):
    legs_all, _, _ = build_v1_legs()
    legs_all = FILTERS[base_filter](legs_all)
    legs = FILTERS[filter_name](legs_all)
    dropped = len(legs_all) - len(legs)
    res, nc = score_legs(legs, stop=stop, target=target, mode=mode)
    a = agg(res, JANOCT_WEEKS)
    reds, tot, table = month_end_reds(res)
    oct_res = [r for r in res if r["date"][5:7] == "10"]
    oct_agg = agg(oct_res, 3.6)
    viol, checked = timing_audit(legs, res)
    pres, pnc = score_legs(legs, stop=stop, target=target, mode=mode, delay=6)
    p_agg = agg(pres, JANOCT_WEEKS)
    p_oct = round(sum(r["net"] for r in pres if r["date"][5:7] == "10"), 2)
    top3 = sorted(res, key=lambda x: -x["net"])[:3]
    ex_top3 = round(tot - sum(r["net"] for r in top3), 2)
    h1, h2 = halves(res)
    out_csv = TR / f"bank_engine_{cycle_id}_trades.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date","direction","family","rep","entry_time","entry_premium","exit_time","exit_premium","exit_reason","full_target","net_inr"])
        for r in sorted(res, key=lambda x: (x["date"], x["entry_time"])):
            w.writerow([r["date"], r["direction"], r["family"], r["rep"], r["entry_time"],
                        r["entry"], r["exit_time"], r["exit"], r["exit_reason"], r["ft"], r["net"]])
    s = 0.0; n = 0
    for r in csv.DictReader(open(out_csv)):
        s += float(r["net_inr"]); n += 1
    summary = dict(cycle=cycle_id, stop=stop, target=target, mode=mode, filter=filter_name,
                   legs_in=len(legs), legs_dropped_by_filter=dropped, not_computed=nc,
                   n=a["n"], net=a["net"], ft_pct=a["ft_pct"], per_week=a["per_week"],
                   oct_n=oct_agg["n"], oct_net=round(sum(r["net"] for r in oct_res), 2),
                   oct_ft_pct=oct_agg["ft_pct"], red_month_ends=reds, month_table=table,
                   halves=dict(jan_may=h1, jun_oct=h2),
                   timing_violations=viol, timing_entry_bars_checked=checked,
                   placebo=dict(n=p_agg["n"], net=p_agg["net"], oct_net=p_oct, not_computed=pnc),
                   ex_top3_total=ex_top3, top3=[(r["date"], r["direction"], r["net"]) for r in top3],
                   independent_resum=dict(n=n, net=round(s, 2)),
                   resum_matches=(n == a["n"] and abs(round(s, 2) - a["net"]) < 0.005))
    print(json.dumps(summary, indent=1))
    (TR / f"bank_engine_{cycle_id}_summary.json").write_text(json.dumps(summary, indent=1))
    return summary

if __name__ == "__main__":
    cid = sys.argv[1]; stop = float(sys.argv[2]); target = float(sys.argv[3])
    mode = sys.argv[4]; filt = sys.argv[5]
    base = sys.argv[6] if len(sys.argv) > 6 else "none"
    run(cid, stop, target, mode, filt, base)
