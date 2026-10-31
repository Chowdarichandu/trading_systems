"""S12 candidate engine — exactly Family E combo F3 (see
new_stock_system_s12_frozen.md and stocks_oct_familyE_combos_frozen.md).
STOCKS ONLY cash intraday, paper only, no orders.
All figures provisional per 100 shares, Rs40/trade — NOT premiums, NOT a lot profit.
Reuses the frozen tuning-harness functions so the definition cannot drift.
"""
import sys, os, json, csv
sys.path.insert(0, "/home/hatch/workspace/trading")
import importlib.util
spec = importlib.util.spec_from_file_location("stocks_oct_tuning", "/home/hatch/workspace/trading/stocks_oct_tuning.py")
tun = importlib.util.module_from_spec(spec); spec.loader.exec_module(tun)
from stock_system_s9 import build_events, trading_days_list

def run_s12():
    events = build_events(trading_days_list())
    pool = tun.gen_candidates(tnet_min=250.0, room_min=1.25, or_lo=0.0015, or_hi=0.040, second_close=False)
    pe_pool = [t for t in pool if t["direction"] == "PE"]
    surv, capped = tun.gate_variant(pe_pool, events, "D1_s9")
    out = []
    for t in capped:
        candles = tun.day_candles(t["symbol"], t["date"])
        idx = next(j for j, c in enumerate(candles) if c["time"] == t["entry_time"])
        crecs = [{"time": c["time"], "high": float(c["high"]), "low": float(c["low"]), "close": float(c["close"])} for c in candles]
        r = tun.replay_variant(crecs, idx, float(t["entry"]), float(t["stop"]), t["direction"],
                               target_mult=3.0, partial_frac=0.5, lock_R=0.0)
        nt = dict(t); nt.update(r); out.append(nt)
    return out

if __name__ == "__main__":
    capped = run_s12()
    m = tun.split_metrics(capped)
    print(json.dumps(m, indent=2, default=str))
    tun.write_csv(os.path.expanduser("~/workspace/trading/s12_trades_jan_oct_2026.csv"), capped)
    tun.write_csv(os.path.expanduser("~/workspace/trading/stocks_oct_best_s12_oct_trades.csv"),
                  [t for t in capped if t["month"] == 10])
    with open(os.path.expanduser("~/workspace/trading/data/progressive/s12_summary_2026-jan-oct.json"), "w") as f:
        json.dump(m, f, indent=2, default=str)
