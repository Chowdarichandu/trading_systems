"""(lA) candidates + capped series for a given year/month, frozen definition from
merged_skill_la_jan_oct.py / merged_skill_la_october.py. Paper only, no orders.
Used here ONLY to fill the 2025 gap: (lA) month JSONs existed for Jan-Oct 2026
only. Validation mode: run with year=2026 month=1 and compare la_capped_trades
to data/progressive/merged_skill_la_summary_2026-01.json before trusting 2025.
For 2025 it writes data/progressive/merged_skill_la_summary_2025-MM.json
(same schema subset: la_candidates, la_capped, la_capped_trades, la_nifty,
la_banknifty, la_diag, days). It does NOT overwrite any 2026 file.
"""
import os, sys, json
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
import pandas as pd
from progressive_capped import room_ratio
from timing_sweep import load as load_nifty, day_data as day_data_nifty
from reentry_filter_sweep import load_bn, day_data_bn
from merged_skill_la_october import (cap_select, metrics, load_bank, day_data_bank,
                                     day_la_nifty, day_la_bank)

QTY, COST = 100, 40.0
OUT = os.path.expanduser("~/workspace/trading/data/progressive")

def leg(trades, sym):
    return metrics([t for t in trades if t["symbol"] == sym])

def run(year, month):
    spot_n, daily_n = load_nifty()
    bn_spot, bn_daily = load_bn()
    bank_spot, bank_daily = load_bank()
    month_days = [d.date().isoformat() for d in daily_n["date"]
                  if d.year == year and d.month == month]
    la, la_diag = [], []
    for ds in month_days:
        dd_n = day_data_nifty(spot_n, daily_n, ds)
        dbn = day_data_bn(bn_spot, bn_daily, ds)
        dd_b = day_data_bank(bank_spot, bank_daily, ds)
        rn = day_la_nifty(dd_n, dbn) if (dd_n and dbn) else {"morning": None, "re": None, "day_net": None}
        day_nifty_tuple = (dd_n[0], dd_n[1], dd_n[2], dd_n[3]) if dd_n else None
        rb = day_la_bank(dd_b, day_nifty_tuple) if (dd_b and day_nifty_tuple) else {"morning": None, "re": None, "day_net": None}
        for sym, res, dd in (("NIFTY", rn, dd_n), ("BANKNIFTY", rb, dd_b)):
            m = res["morning"]
            la_diag.append({"date": ds, "symbol": sym, "morning": m, "re": res["re"], "day_net": res["day_net"]})
            if m is None or res["day_net"] is None:
                continue
            bias, scale = dd[4], dd[5]
            pdh, pdc, pdl = dd[1], dd[2], dd[3]
            day_spot = dd[0]
            cand = day_spot[day_spot["time"] >= "09:30"]
            sig_row = cand[cand["time"] == m["signal"]]
            sig_close = float(sig_row.iloc[0]["close"]) if len(sig_row) else float(m["entry"])
            rr, room = room_ratio(sig_close, "PE", pdh, pdc, pdl, scale)
            morning_target_net = round(2 * float(m["risk"]) * QTY - COST, 2) if m.get("risk") else 0.0
            wk = pd.Timestamp(ds).isocalendar()
            la.append({"method": "(lA)", "symbol": sym, "date": ds, "week": f"{wk[0]}-W{wk[1]:02d}",
                       "setup": "la_pe_rescan_reentry", "direction": "PE",
                       "exit_reason": ("target" if res["day_net"] > 0 and res["re"] is None and m["exit"] == "target"
                                       else "day_green" if res["day_net"] > 0 else "day_loss"),
                       "net_rs": round(float(res["day_net"]), 2), "target_net_rs": morning_target_net,
                       "setup_rank": 1, "room_ratio": round(min(rr, 5.0), 3) if rr != float("inf") else 1.0,
                       "bias_strong": 1 if bias != "neutral" else 0, "results_pass": 0,
                       "morning_signal": m["signal"], "morning_exit": m["exit"],
                       "morning_net": m["net"],
                       "re_signal": res["re"]["re_signal"] if res["re"] else None,
                       "re_exit": res["re"]["exit"] if res["re"] else None,
                       "re_net": res["re"]["net"] if res["re"] else None})
    la_cap, _ = cap_select(la)
    out = {"year": year, "month": month, "days": len(month_days),
           "la_candidates": la, "la_diag": la_diag,
           "la_capped": metrics(la_cap), "la_capped_trades": la_cap,
           "la_nifty": leg(la_cap, "NIFTY"), "la_banknifty": leg(la_cap, "BANKNIFTY")}
    return out

if __name__ == "__main__":
    y, m = int(sys.argv[1]), int(sys.argv[2])
    out = run(y, m)
    print(f"{y}-{m:02d} days={out['days']} la_cand={len(out['la_candidates'])} la_cap={out['la_capped']} la_nifty={out['la_nifty']} la_bank={out['la_banknifty']}")
    if y == 2025:
        with open(f"{OUT}/merged_skill_la_summary_{y}-{m:02d}.json", "w") as f:
            json.dump(out, f, indent=2, default=str)
        print("wrote", f"{OUT}/merged_skill_la_summary_{y}-{m:02d}.json")
    else:
        # validation mode: do not overwrite; print trades for comparison
        for t in sorted(out["la_capped_trades"], key=lambda x: (x["date"], x["symbol"])):
            print("LA", t["date"], t["symbol"], t["net_rs"], t["exit_reason"])
