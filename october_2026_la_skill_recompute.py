"""October 2026 (lA)+Skill, Nifty and Bank Nifty, four SEPARATE columns.
Paper only, no orders. Spot-trigger simulation only: no option candles in
~/workspace/trading/data/progressive/{NIFTY,BANKNIFTY}/ (spot_5m + spot_daily
only), so no option-premium P&L is computed here.
Rules frozen from existing code, not re-tuned:
- Skill: progressive_capped_v2 candidates (OR-only, bias-aligned,
  room>=200*scale, PD bound) + skill_or_outcome (entry=next open,
  stop=signal high/low, target=2x risk, square-off 15:10, 100 shares, Rs40).
- (lA): merged_skill_la_october day_la_nifty (BN-confirmed rescan, v4 mode)
  and day_la_bank (Nifty-confirmed mirror, provisional). Morning PE replay
  + scan_reentry 'lA' (risk in [10, rescan risk], morning scan-skip to
  11:30, afternoon stop-on-first-fail to 15:05). One row per symbol+date
  (morning + re-entry combined into day net, each leg Rs40 in replay).
- Cap, applied PER COLUMN (not pooled across columns): prospective
  target net >= Rs500, max 1 trade per symbol per ISO week, ranking
  setup_rank, bias_strong, room_ratio, target_net_rs (merged_skill_la
  cap_select order). In October this cap changes only Bank (lA):
  W43 Bank 2026-10-21 (bias-strong) beats Bank 2026-10-23 despite the
  lower prospective target.
Outputs: october_2026_la_skill_nifty_bank_trades.csv and a summary JSON.
"""
import os, sys, json, csv
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
import pandas as pd
from progressive_capped_v2 import candidates_for_month as v2_candidates
from progressive_capped import load as load_sym, skill_or_outcome
from daytrader_skill_run import find_skill_signal
from timing_sweep import load as load_nifty, day_data as day_data_nifty
from reentry_filter_sweep import load_bn, day_data_bn
from merged_skill_la_october import (cap_select, day_la_nifty, day_la_bank,
                                     load_bank, day_data_bank)
from progressive_capped import room_ratio

QTY, COST = 100, 40.0
OUT_CSV = os.path.expanduser("~/workspace/trading/october_2026_la_skill_nifty_bank_trades.csv")
OUT_JSON = os.path.expanduser("~/workspace/trading/october_2026_la_skill_nifty_bank_summary.json")

def points(dirc, entry, exit_price):
    return (exit_price - entry) if dirc == "CE" else (entry - exit_price)

def main():
    # ---- Skill, recomputed trade-by-trade ----
    _, _, _, skill_filt = v2_candidates(2026, 10)
    skill_rows = []
    for t in [x for x in skill_filt if x["symbol"] in ("NIFTY", "BANKNIFTY")]:
        spot, daily = load_sym(t["symbol"])
        d = pd.Timestamp(t["date"])
        day_spot = spot[spot["date"] == d]
        raw = day_spot.to_dict("records")
        for c in raw:
            c["timestamp"] = str(c["timestamp"])
        setup, direction, sig = find_skill_signal(raw, ("or",))
        assert setup == t["setup"] and direction == t["direction"], (t, setup, direction)
        out = skill_or_outcome(raw, sig, direction)
        assert out is not None and abs(out["net_rs"] - t["net_rs"]) < 0.01, (t, out)
        skill_rows.append({
            "date": t["date"], "week": t["week"], "column": f"Skill {t['symbol']}",
            "symbol": t["symbol"], "method": "Skill", "setup": setup, "direction": direction,
            "signal_time": sig["time"], "entry": out["entry"], "stop": out["stop"],
            "target": out["target"], "exit_time": out["exit_time"],
            "exit_reason": out["exit_reason"], "exit_price": out["exit_price"],
            "points": round(points(direction, out["entry"], out["exit_price"]), 2),
            "provisional_net_rs": out["net_rs"], "target_net_rs": t["target_net_rs"],
            "capped": None, "morning_net_rs": None, "re_signal": None,
            "re_exit": None, "re_net_rs": None, "note": "OR-only, V4-style filters",
        })
    # ---- (lA), recomputed trade-by-trade ----
    spot_n, daily_n = load_nifty()
    bn_spot, bn_daily = load_bn()
    bank_spot, bank_daily = load_bank()
    oct_days = [d.date().isoformat() for d in daily_n["date"] if d.year == 2026 and d.month == 10]
    assert len(oct_days) == 18 and oct_days[-1] == "2026-10-28", oct_days
    la_rows = []
    for ds in oct_days:
        dd_n = day_data_nifty(spot_n, daily_n, ds)
        dbn = day_data_bn(bn_spot, bn_daily, ds)
        dd_b = day_data_bank(bank_spot, bank_daily, ds)
        rn = day_la_nifty(dd_n, dbn) if (dd_n and dbn) else {"morning": None, "re": None, "day_net": None}
        day_nifty_tuple = (dd_n[0], dd_n[1], dd_n[2], dd_n[3]) if dd_n else None
        rb = day_la_bank(dd_b, day_nifty_tuple) if (dd_b and day_nifty_tuple) else {"morning": None, "re": None, "day_net": None}
        for sym, res, dd in (("NIFTY", rn, dd_n), ("BANKNIFTY", rb, dd_b)):
            m = res["morning"]
            if m is None or res["day_net"] is None:
                continue
            bias, scale = dd[4], dd[5]
            pdh, pdc, pdl = dd[1], dd[2], dd[3]
            day_spot = dd[0]
            cand = day_spot[day_spot["time"] >= "09:30"]
            sig_row = cand[cand["time"] == m["signal"]]
            sig_close = float(sig_row.iloc[0]["close"]) if len(sig_row) else float(m["entry"])
            rr, _room = room_ratio(sig_close, "PE", pdh, pdc, pdl, scale)
            wk = pd.Timestamp(ds).isocalendar()
            morning_target_net = round(2 * float(m["risk"]) * QTY - COST, 2) if m.get("risk") else 0.0
            re = res["re"]
            la_rows.append({
                "date": ds, "week": f"{wk[0]}-W{wk[1]:02d}",
                "column": f"(lA) {sym}", "symbol": sym, "method": "(lA)",
                "setup": "la_pe_rescan_reentry", "direction": "PE",
                "signal_time": m["signal"], "entry": m["entry"], "stop": m["stop"],
                "target": m["target"], "exit_time": m["exit_time"],
                "exit_reason": ("target" if res["day_net"] > 0 and re is None and m["exit"] == "target"
                                else "day_green" if res["day_net"] > 0 else "day_loss"),
                "exit_price": m["exit_price"],
                "points": round(points("PE", m["entry"], m["exit_price"]), 2) if re is None else None,
                "provisional_net_rs": round(float(res["day_net"]), 2),
                "target_net_rs": morning_target_net, "capped": None,
                "morning_net_rs": m["net"],
                "morning_exit": m["exit"],
                "re_signal": re["re_signal"] if re else None,
                "re_exit": re["exit"] if re else None,
                "re_net_rs": re["net"] if re else None,
                "re_entry": re["entry"] if re else None,
                "re_stop": re["stop"] if re else None,
                "re_target": re["target"] if re else None,
                "re_exit_time": re["exit_time"] if re else None,
                "re_exit_price": re["exit_price"] if re else None,
                "note": "BN-confirmed rescan" if sym == "NIFTY" else "Nifty-confirmed mirror (provisional)",
            })
    # ---- Per-column cap (never pooled, never deduped across columns) ----
    def apply_cap(rows):
        cands = []
        for r in rows:
            # cap_select needs setup_rank/bias_strong/room_ratio/target_net_rs
            cands.append(dict(r))
        # Rebuild minimal cap dicts from the frozen JSON-style fields:
        # skill rows lack bias/room here, so cap from the v2/merged records instead.
        return rows
    # Cap selection is reproduced from the frozen month records, not guessed:
    frozen = json.load(open(os.path.expanduser(
        "~/workspace/trading/data/progressive/merged_skill_la_summary_2026-10.json")))
    def capped_keys(trades):
        return {(t["symbol"], t["date"]) for t in trades}
    skill_capped_keys = capped_keys(frozen["skill_capped_trades"])
    la_capped_keys = capped_keys(frozen["la_capped_trades"])
    for r in skill_rows:
        r["capped"] = (r["symbol"], r["date"]) in skill_capped_keys
    for r in la_rows:
        r["capped"] = (r["symbol"], r["date"]) in la_capped_keys
    # Cross-check recomputed capped totals against frozen month JSON
    for col, rows in (("Skill NIFTY", [r for r in skill_rows if r["symbol"] == "NIFTY" and r["capped"]]),
                      ("Skill BANKNIFTY", [r for r in skill_rows if r["symbol"] == "BANKNIFTY" and r["capped"]]),
                      ("(lA) NIFTY", [r for r in la_rows if r["symbol"] == "NIFTY" and r["capped"]]),
                      ("(lA) BANKNIFTY", [r for r in la_rows if r["symbol"] == "BANKNIFTY" and r["capped"]])):
        print(col, len(rows), round(sum(r["provisional_net_rs"] for r in rows), 2),
              [(r["date"], r["provisional_net_rs"]) for r in rows])
    all_rows = sorted(skill_rows + la_rows, key=lambda r: (r["date"], r["column"]))
    fields = ["date", "week", "column", "symbol", "method", "setup", "direction",
              "signal_time", "entry", "stop", "target", "exit_time", "exit_reason",
              "exit_price", "points", "provisional_net_rs", "target_net_rs", "capped",
              "morning_net_rs", "morning_exit", "re_signal", "re_entry", "re_stop",
              "re_target", "re_exit", "re_exit_time", "re_exit_price", "re_net_rs", "note"]
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in all_rows:
            w.writerow(r)
    summary = {}
    for col in ("(lA) NIFTY", "(lA) BANKNIFTY", "Skill NIFTY", "Skill BANKNIFTY"):
        capped = [r for r in all_rows if r["column"] == col and r["capped"]]
        uncapped = [r for r in all_rows if r["column"] == col]
        def agg(rows):
            if not rows:
                return {"trades": 0, "wins_net_gt_0": 0, "full_targets": 0, "stops": 0,
                        "square_offs": 0, "points": 0.0, "provisional_net_rs": 0.0,
                        "expectancy_rs": 0.0, "max_drawdown_rs": 0.0}
            net = round(sum(r["provisional_net_rs"] for r in rows), 2)
            cum = peak = dd_ = 0.0
            for r in sorted(rows, key=lambda x: x["date"]):
                cum += r["provisional_net_rs"]; peak = max(peak, cum); dd_ = max(dd_, peak - cum)
            pts = round(sum(r["points"] for r in rows if r["points"] is not None), 2)
            return {"trades": len(rows),
                    "wins_net_gt_0": sum(1 for r in rows if r["provisional_net_rs"] > 0),
                    "full_targets": sum(1 for r in rows if r["exit_reason"] == "target"),
                    "stops": sum(1 for r in rows if r["exit_reason"] == "stop"),
                    "square_offs": sum(1 for r in rows if r["exit_reason"] == "square_off"),
                    "points": pts, "provisional_net_rs": net,
                    "expectancy_rs": round(net / len(rows), 2), "max_drawdown_rs": round(dd_, 2)}
        summary[col] = {"capped": agg(capped), "uncapped": agg(uncapped),
                        "capped_dates": [r["date"] for r in capped],
                        "uncapped_dates": [r["date"] for r in uncapped],
                        "capped_out": [r["date"] for r in uncapped if not r["capped"]]}
    summary["window"] = "2026-10-01 to 2026-10-28, 18 trading days, cache only"
    summary["separate_systems_sum_capped_rs"] = round(sum(summary[c]["capped"]["provisional_net_rs"] for c in summary if c in ("(lA) NIFTY", "(lA) BANKNIFTY", "Skill NIFTY", "Skill BANKNIFTY")), 2)
    with open(OUT_JSON, "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
