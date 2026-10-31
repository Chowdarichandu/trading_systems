#!/usr/bin/env python3
"""Run-2 Cycle 15 CHALLENGER: Blue-Line v4 add-on legs on book v6 (BANKNIFTY ONLY).
Base book v6 is reproduced exactly (cycle14 rescore with arm=False). Blue-Line
legs come from the month trade logs (entries only); they are re-scored under
book conventions from the Blue-Line dataset's option_5m.csv premium candles:
entry = open of the entry bar; exits = book v6 assembly (entry premium <400 ->
runner-lock50 + second target 180; >=400 -> plain G0 -50/+90); lot 30, cost
Rs220, UNIQUE-ONCE admission on keys unused by book v6, premium outside
[400,550). Controls: timing audit (incl. entry >= signal_time for add-ons and
entry-premium cross-check vs the log), placebo (+30 min combined), halves,
month table, ex-top-3, independent re-sum, NOT_COMPUTED counted.
"""
import csv, glob, json
from pathlib import Path
import sys
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import agg, month_end_reds
from bank_engine_run2_cycle14 import rescore as rescore14, stream_keys
from bank_engine_run2 import book_v4_legs
from bank_engine_run2_cycle13 import ratchet_replay
from bank_engine_run2_cycle14 import be_replay

TR = Path.home() / "workspace/trading"
DATA = TR / "data"

_opt_cache = {}
def opt_candles(month, strike, typ, day):
    key = (month, int(strike), typ, day)
    if key in _opt_cache: return _opt_cache[key]
    f = DATA / f"banknifty-2026-{month}" / "option_5m.csv"
    rows = []
    if f.exists():
        for r in csv.DictReader(open(f)):
            if int(r["strike"]) == int(strike) and r["option_type"] == typ and r["timestamp"][:10] == day:
                rows.append((r["timestamp"][11:16], float(r["open"]), float(r["high"]),
                             float(r["low"]), float(r["close"]), 0.0))
    rows.sort()
    _opt_cache[key] = rows or None
    return _opt_cache[key]

def blue_legs():
    out = []
    for m in range(1, 11):
        f = None
        for name in ("trade_log_v4_t90.csv", "trade_log_v4_t50.csv"):
            p = DATA / f"banknifty-2026-{m:02d}" / name
            if p.exists(): f = p; break
        if not f: continue
        for r in csv.DictReader(open(f)):
            if not r.get("direction") or not r.get("entry_time"): continue
            out.append(dict(date=r["date"], direction=r["direction"],
                            entry_time=r["entry_time"][11:16], signal_time=r["signal_time"][11:16],
                            strike=int(float(r["strike"])), setup=r["setup_type"],
                            log_entry_premium=float(r["entry_premium"]) if r["entry_premium"] else None,
                            month=f"{m:02d}"))
    return out

def score_blue(bl, delay=0):
    cs = opt_candles(bl["month"], bl["strike"], bl["direction"], bl["date"])
    if not cs: return None, None
    bars = [b for b in cs if b[0] == bl["entry_time"]]
    if not bars: return None, None
    ep = bars[0][1]
    if ep < 400.0:
        r = ratchet_replay(cs, bl["entry_time"], delay=delay, ratchet=False, target2_pts=180.0)
    else:
        r = be_replay(cs, bl["entry_time"], delay=delay, arm=False)
    if r is None: return None, ep
    r = {**r, "date": bl["date"], "direction": bl["direction"], "family": "BlueLine_v4",
         "rep": "BlueLine v4 " + (bl["setup"] or ""), "entry_time": bl["entry_time"],
         "leg_key": (bl["date"], bl["direction"], bl["entry_time"])}
    return r, ep

def main():
    legs = book_v4_legs()
    legs_by_key = {(l["date"], l["direction"], l["entry_time"]): l for l in legs}
    keys = stream_keys(delay=0)
    base, _ = rescore14(keys, legs_by_key, delay=0, arm=False)
    base_agg = agg(base, 40.6)
    assert base_agg["n"] == 82 and abs(base_agg["net"] - 61896.5) < 0.005, f"sanity failed: {base_agg}"
    base_keys = {(r["date"], r["direction"]) for r in base}
    admitted, nc, dropped = [], 0, {"key": 0, "band": 0}
    mismatches, sig_viol = [], []
    for bl in blue_legs():
        if (bl["date"], bl["direction"]) in base_keys:
            dropped["key"] += 1; continue
        r, ep = score_blue(bl, delay=0)
        if r is None: nc += 1; continue
        if 400.0 <= ep < 550.0:
            dropped["band"] += 1; continue
        if bl["log_entry_premium"] is not None and abs(bl["log_entry_premium"] - ep) > 0.01:
            mismatches.append((bl["date"], bl["log_entry_premium"], ep))
        if bl["entry_time"] < bl["signal_time"]:
            sig_viol.append((bl["date"], bl["entry_time"], bl["signal_time"]))
        r["entry_premium_check"] = ep
        admitted.append(r)
    combined = sorted(base + admitted, key=lambda x: (x["date"], x["entry_time"]))
    a = agg(combined, 40.6); reds, tot, table = month_end_reds(combined)
    # placebo: base delayed + blue delayed (same admission, delayed stream keys from base delayed)
    p_base, _ = rescore14(stream_keys(delay=6), legs_by_key, delay=6, arm=False)
    p_base_keys = {(r["date"], r["direction"]) for r in p_base}
    p_admitted = []
    for bl in blue_legs():
        if (bl["date"], bl["direction"]) in p_base_keys: continue
        r, ep = score_blue(bl, delay=6)
        if r is None or ep is None: continue
        if 400.0 <= ep < 550.0: continue
        p_admitted.append(r)
    p_combined = sorted(p_base + p_admitted, key=lambda x: (x["date"], x["entry_time"]))
    p_agg = agg(p_combined, 40.6)
    top3 = sorted(combined, key=lambda x: -x["net"])[:3]
    ex_top3 = round(tot - sum(r["net"] for r in top3), 2)
    h1 = round(sum(r["net"] for r in combined if r["date"] < "2026-06-01"), 2)
    h2 = round(sum(r["net"] for r in combined if r["date"] >= "2026-06-01"), 2)
    months = {m: round(sum(r["net"] for r in combined if r["date"][5:7] == m), 2)
              for m in ("01", "02", "03", "04", "05", "06", "07", "08", "09", "10")}
    out_csv = TR / "bank_engine_cycle15_trades.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "direction", "family", "rep", "entry_time", "entry_premium",
                    "exit_time", "exit_premium", "exit_reason", "full_target", "net_inr"])
        for r in combined:
            w.writerow([r["date"], r["direction"], r["family"], r["rep"], r["entry_time"],
                        r["entry"], r["exit_time"], r["exit"], r["exit_reason"], r["ft"], r["net"]])
    rs, rn = 0.0, 0
    for r in csv.DictReader(open(out_csv)):
        rs += float(r["net_inr"]); rn += 1
    s = dict(cycle="cycle15_blueline_addons", sanity_base_v6=base_agg,
             blue_admitted=[(r["date"], r["direction"], r["entry_time"], r["rep"], r["net"]) for r in admitted],
             blue_not_computed=nc, blue_dropped=dropped,
             blue_entry_premium_mismatches=mismatches, blue_signal_violations=sig_viol,
             n=a["n"], net=a["net"], ft_pct=a["ft_pct"], per_week=a["per_week"],
             red_month_ends=reds, month_table=table, months=months,
             halves=dict(jan_may=h1, jun_oct=h2),
             placebo=dict(n=p_agg["n"], net=p_agg["net"]),
             ex_top3_total=ex_top3, top3=[(r["date"], r["direction"], r["net"]) for r in top3],
             independent_resum=dict(n=rn, net=round(rs, 2)),
             resum_matches=(rn == a["n"] and abs(round(rs, 2) - a["net"]) < 0.005))
    print(json.dumps(s, indent=1))
    (TR / "bank_engine_cycle15_summary.json").write_text(json.dumps(s, indent=1))

if __name__ == "__main__":
    main()
