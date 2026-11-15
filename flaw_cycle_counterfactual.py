#!/usr/bin/env python3
"""FLAW-CYCLE counterfactuals: Nov 2 + Nov 3 Bank live trades under the
November primary's frozen G0 geometry (PLAIN -50/+90, square-off 15:10),
incumbent via the pipeline's own replay_x, overlays via flaw_cycle_run's
replay_overlay. Plus October fresh re-score flaw counts and the stocks
parallel count (provisional per 100 shares). Paper only."""
import csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from bank_r3_ws3 import replay_x
from flaw_cycle_run import replay_overlay

TR = Path.home() / "workspace/trading"
HF = Path.home() / "workspace/goals/3-blue-line-bank-nifty-backtest/hidden_files"
PLAIN = dict(stop=50.0, trig=90.0, lock=None, tgt2=None)
SQ = "15:10"

def load(p):
    d = json.loads(Path(p).read_text())
    return [(c[0][11:16], c[1], c[2], c[3], c[4], c[5] if len(c) > 5 else 0) for c in d["candles"]]

out = {}
# ---- Nov 2: Skill V3 PE 54800, entry 10:20 @ 681.95 (official log) ----
cs2 = load(TR / "flaw_cycle_candles_2026-11-02_54800PE.json")
# ---- Nov 3: NS1 second-leg CE 55500, entry 10:20 @ 867.60 (worker snapshot) ----
cs3 = load(HF / "prem_bank_55500CE_2026-11-03_1115.json")

for day, cs, entry_px in [("2026-11-02", cs2, 681.95), ("2026-11-03", cs3, 867.60)]:
    inc = replay_x(cs, "10:20", 0, PLAIN, "open", SQ)
    rec = {"candles": len(cs), "entry_check": inc["entry"] == entry_px, "incumbent": inc}
    for name, ov in [("FC-1", "fc1"), ("FC-2", "fc2"), ("FC-3", "fc3")]:
        rec[name] = replay_overlay(cs, "10:20", PLAIN, overlay=ov, sq=SQ)
    ent = [b for b in cs if b[0] >= "10:20"]
    rec["mfe_to_incumbent_exit"] = round(max(b[2] for b in cs
        if "10:20" <= b[0] <= inc["exit_time"]) - entry_px, 2)
    out[day] = rec
    print(day, "entry_ok:", rec["entry_check"], "| MFE to exit:", rec["mfe_to_incumbent_exit"])
    for k in ["incumbent", "FC-1", "FC-2", "FC-3"]:
        r = rec[k]
        print(f"   {k:9s} net={r['net']:>9} exit {r['exit_time']} @ {r['exit']} ({r['exit_reason']})")

# ---- October fresh re-score: same flaw count on primary legs ----
def mfe_of(cs, et, xt):
    bars = [b for b in cs if et <= b[0] <= xt]
    return round(max(b[2] for b in bars) - bars[0][1], 2) if bars else None

oct_rows = []
for f in ["oct2026_fresh/bank_oct2026_trades.csv", "oct2026_fresh/bank_oct29_30_trades.csv"]:
    for r in csv.DictReader(open(TR / f)):
        if r["channel"] != "PRIMARY": continue
        import re as _re
        m = _re.search(r"candles=([^;]+)", r["notes"])
        raw = json.loads(Path(m.group(1).strip()).read_text())
        if isinstance(raw, dict): raw = raw["data"]["candles"]
        cs = sorted([(c[0][11:16], c[1], c[2], c[3], c[4], 0) for c in raw])
        assert cs, r["date"]
        mfe = round(max(b[2] for b in cs if r["entry_time"] <= b[0] <= r["exit_time"])
                    - float(r["entry_premium"]), 2)
        oct_rows.append(dict(date=r["date"], fam=r["notes"].split("family=")[1].split(";")[0], dir=r["direction"],
                             et=r["entry_time"], xt=r["exit_time"], reason=r["exit_reason"],
                             net=float(r["net_inr"]), mfe=mfe))
stops = [r for r in oct_rows if r["reason"] == "stop"]
nd = [r for r in stops if r["mfe"] < 30]
print(f"OCTOBER fresh PRIMARY: {len(oct_rows)} legs, full stops {len(stops)} "
      f"({sum(r['net'] for r in stops):+.2f}), never-developed {len(nd)} "
      f"({sum(r['net'] for r in nd):+.2f}), dev-then-stop {len(stops)-len(nd)}")
out["october"] = oct_rows

# ---- Stocks parallel count (PROVISIONAL per 100 shares) ----
def dur(r):
    a = int(r["entry_time"][:2]) * 60 + int(r["entry_time"][3:5])
    b = int(r["exit_time"][:2]) * 60 + int(r["exit_time"][3:5])
    return b - a
oct_s = list(csv.DictReader(open(TR / "scratch_rerun_oct/sarvaritu_oct2026_entries.csv")))
s_stops = [r for r in oct_s if r["exit_reason"] == "stop"]
q5 = [r for r in s_stops if dur(r) <= 5]; q15 = [r for r in s_stops if dur(r) <= 15]
from collections import Counter
print(f"STOCKS Oct book: {len(oct_s)} trades net {sum(float(r['net']) for r in oct_s):+.2f} | "
      f"stops {len(s_stops)} ({sum(float(r['net']) for r in s_stops):+.2f}) | "
      f"<=5min {len(q5)} ({sum(float(r['net']) for r in q5):+.2f}) | "
      f"<=15min {len(q15)} ({sum(float(r['net']) for r in q15):+.2f})")
print("   <=15min stops by component:", dict(Counter(r["comp"] for r in q15)))
print("   all stops by component:", dict(Counter(r["comp"] for r in s_stops)))
out["stocks_october"] = {"trades": len(oct_s), "stops": len(s_stops),
                          "stop_drag": round(sum(float(r["net"]) for r in s_stops), 2),
                          "q5": len(q5), "q5_drag": round(sum(float(r["net"]) for r in q5), 2),
                          "q15": len(q15), "q15_drag": round(sum(float(r["net"]) for r in q15), 2),
                          "q15_by_component": dict(Counter(r["comp"] for r in q15))}
(TR / "flaw_cycle_counterfactual_2026-11-03.json").write_text(json.dumps(out, indent=1, default=str))
print("WROTE flaw_cycle_counterfactual_2026-11-03.json")
