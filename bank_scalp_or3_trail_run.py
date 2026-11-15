#!/usr/bin/env python3
"""OR3-TRAIL cell — trailing stop on 3-MIN opening-range bursts.
Frozen Charter v2 mechanics (bank_scalp_engine_charter.py verbatim): act +8,
initial stop -9, flat-only re-entry, cap 8/day, exits on 1-min premium candles,
hard max hold 5 min. Trail distances 7/5/4/3. Trail 5 = Cycle 7-8's OR3-TRAIL
(cross-checked row-for-row); 7/4/3 are the untested ridge cells.
Controls in the same run: timing audit, lag placebo at +1 decision bar (+3
1-min bars; task spec) AND at +1 1-min bar (engine convention, comparability),
count-matched random placebo (seed 42, 20 draws), halves (trading-day split,
first 96 of 192 days), month table, ex-top-3, independent re-sum, October slice.
"""
import sys, json, csv
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/trading")
import bank_scalp_engine_core as C
import bank_scalp_engine_charter as H

TRAILS = [(7.0, "OR3-TRAILT7"), (5.0, "OR3-TRAIL"), (4.0, "OR3-TRAILT4"), (3.0, "OR3-TRAILT3")]
OUT_CSV = "/home/hatch/workspace/trading/bank_scalp_or3_trail_trades.csv"
OLD_T5_CSV = "/home/hatch/workspace/trading/bank_scalp_engine_OR3-TRAIL_trades.csv"


def run(label, spec):
    spot = C.load_spot()
    trades, sig_ends, nc, busy = [], [], 0, 0
    for day in C.days():
        taken, busy_until = 0, -1
        for sig_end, direction in H.or_signals_3m(day, spot[day]):
            if taken >= H.CAP: break
            if sig_end <= busy_until: busy += 1; continue
            t = H.score(day, sig_end, direction, spec)
            if t is None: nc += 1; continue
            t["variant"] = label; trades.append(t); sig_ends.append(sig_end)
            taken += 1; busy_until = t["exit_bar"]
    s = H.summarise_charter(trades, sig_ends, spec, label)
    # lag placebo at +1 decision bar = +3 1-min bars (task spec for 3-min signals)
    lag3 = []
    for t, se in zip(trades, sig_ends):
        lt = H.score(t["date"], se, t["direction"], spec, lag=3)
        if lt is not None: lag3.append(lt)
    s["lag_placebo_decisionbar_inr"] = round(sum(t["net_inr"] for t in lag3), 2)
    s["lag_placebo_decisionbar_n"] = len(lag3)
    s["gross_pts_per_trade"] = round(s["gross_inr"] / (C.LOT * s["trades"]), 3) if s["trades"] else 0.0
    # October slice
    oct_tr = [t for t in trades if t["date"].startswith("2026-10")]
    oct_days = {}
    for t in oct_tr: oct_days[t["date"]] = oct_days.get(t["date"], 0.0) + t["net_inr"]
    oct_gross = round(sum(t["net_inr"] for t in oct_tr) + len(oct_tr) * C.COST, 2)
    s["october"] = {
        "trades": len(oct_tr), "net_inr": round(sum(t["net_inr"] for t in oct_tr), 2),
        "gross_inr": oct_gross,
        "gross_pts_per_trade": round(oct_gross / (C.LOT * len(oct_tr)), 3) if oct_tr else 0.0,
        "days_traded": len(oct_days),
        "days_green_pct": round(sum(1 for v in oct_days.values() if v > 0) / len(oct_days), 4) if oct_days else 0.0,
    }
    s.update({"not_computed": nc, "busy_skips": busy})
    return trades, s


def main():
    ds = C.days()
    print(f"window: {ds[0]} .. {ds[-1]}  days={len(ds)}  H1={ds[0]}..{ds[len(ds)//2 - 1]}  H2={ds[len(ds)//2]}..{ds[-1]}", flush=True)
    all_trades, out = [], {}
    for trail, label in TRAILS:
        spec = ("T", 8.0, trail, 9.0)
        trades, s = run(label, spec)
        all_trades += trades; out[label] = s
        print(f"{label}: n={s['trades']} net={s['total_inr']} gross={s['gross_inr']} "
              f"({s['gross_pts_per_trade']} pts/tr) H1={s['h1_inr']} H2={s['h2_inr']} "
              f"WR={s['win_rate']} DG={s['days_green_pct']} audit={s['audit_violations']} "
              f"lagDB={s['lag_placebo_decisionbar_inr']} lag1m={s['lag_placebo_inr']} "
              f"rand={s['random_placebo']['mean']} NC={s['not_computed']} "
              f"OCT net={s['october']['net_inr']} gpts={s['october']['gross_pts_per_trade']} DG={s['october']['days_green_pct']}", flush=True)
    # combined CSV + independent re-sum per variant
    cols = ["variant", "date", "direction", "strike", "expiry", "entry_bar",
            "entry_premium", "exit_bar", "exit_premium", "exit_reason", "net_inr"]
    with open(OUT_CSV, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader()
        for t in all_trades: w.writerow({c: t[c] for c in cols})
    back = list(csv.DictReader(open(OUT_CSV)))
    for label, s in out.items():
        rs = round(sum(float(r["net_inr"]) for r in back if r["variant"] == label), 2)
        s["resum_inr"] = rs; s["resum_match"] = bool(abs(rs - s["total_inr"]) < 0.01)
    # cross-check trail-5 trades row-for-row vs Cycle 7-8's original CSV
    old = list(csv.DictReader(open(OLD_T5_CSV)))
    new5 = [r for r in back if r["variant"] == "OR3-TRAIL"]
    keys = ["date", "direction", "strike", "entry_bar", "exit_bar", "net_inr"]
    same = len(old) == len(new5) and all(
        all(str(o[k]) == str(n[k]) for k in keys) for o, n in zip(old, new5))
    out["_trail5_crosscheck_vs_cycle78"] = {"old_rows": len(old), "new_rows": len(new5), "row_for_row_match": bool(same)}
    print("trail5 crosscheck:", out["_trail5_crosscheck_vs_cycle78"], flush=True)
    json.dump(out, open("/home/hatch/workspace/trading/bank_scalp_or3_trail_summary.json", "w"), indent=1)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
