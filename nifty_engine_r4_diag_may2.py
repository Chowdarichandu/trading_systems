#!/usr/bin/env python3
"""ROUND 4 WS1 diagnosis, pass 2 — entry-known feature scan book-wide.
For every entry-known feature, report the band spanned by the 3 May losers
and the book-wide composition of that band (legs, net, whether the May
winner falls inside). Entry-known = computable at the entry bar's open."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_r4_harness import DAILY, DORDER, DIDX, PREV, pdret, spot5m

feats = json.loads(Path("nifty_engine_r4_diag_may.json").read_text())
S5 = spot5m()
for f in feats:
    d = f["date"]; i = DIDX[d]; sb = S5.get(d, [])
    day_open = sb[0][1] if sb else DAILY[d]["o"]
    prev_close = DAILY[PREV[d]]["c"]
    f["gap_pct"] = round((day_open / prev_close - 1) * 100, 3)
    pre = [b for b in sb if b[0] < f["entry_time"]]
    if pre:
        spot_at_entry = pre[-1][4]
        f["pre_move_pct"] = round((spot_at_entry / day_open - 1) * 100, 3)
        f["pre_range_pct"] = round((max(b[2] for b in pre) - min(b[3] for b in pre)) / day_open * 100, 3)
    p = PREV[d]
    f["bias_pos"] = round((DAILY[p]["c"] - DAILY[p]["l"]) / (DAILY[p]["h"] - DAILY[p]["l"]) * 100, 1) \
        if DAILY[p]["h"] > DAILY[p]["l"] else None
    f["pd2ret"] = round((DAILY[p]["c"] / DAILY[PREV[p]]["c"] - 1) * 100, 3) if PREV.get(p) else None

may_losers = [f for f in feats if f["date"].startswith("2026-05") and f["net"] < 0]
may_winner = [f for f in feats if f["date"].startswith("2026-05") and f["net"] > 0]
print("May losers entry-known features:")
for f in may_losers:
    print({k: f[k] for k in ("date", "gap_pct", "pre_move_pct", "pre_range_pct",
                             "bias_pos", "pdret", "pd2ret", "entry_prem", "dte")})
print("May winner:", {k: may_winner[0][k] for k in ("date", "gap_pct", "pre_move_pct",
      "pre_range_pct", "bias_pos", "pdret", "pd2ret", "entry_prem", "dte")})

FEATURES = ["gap_pct", "pre_move_pct", "pre_range_pct", "bias_pos", "pdret",
            "pd2ret", "entry_prem", "dte", "pd_range", "vol3"]
print("\nBand scan (band = [min,max] over the 3 May losers):")
for k in FEATURES:
    vals = [f[k] for f in may_losers if f.get(k) is not None]
    lo, hi = min(vals), max(vals)
    inside = [f for f in feats if f.get(k) is not None and lo <= f[k] <= hi]
    net = sum(f["net"] for f in inside)
    win_in = any(f["date"] == may_winner[0]["date"] for f in inside)
    print(f"{k:14s} band [{lo}, {hi}] -> {len(inside)} legs, net {net:+,.2f}, "
          f"May winner inside: {win_in}")
Path("nifty_engine_r4_diag_may.json").write_text(json.dumps(feats, indent=1))
