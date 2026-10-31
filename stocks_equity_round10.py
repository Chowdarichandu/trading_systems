#!/usr/bin/env python3
"""Round 10 — Part A: quantify the INVERTED trend-gate hypothesis in-sample.

INV sets are EXACTLY Round 9's dropped sets on the P2 pool
(V5 re-entry, chain round <= 2, entry < 10:30, ADR>=3% stock-days):
  INV1 = G1 dropped  (Nifty prev close <= 50DMA)
  INV2 = G2 dropped  (Nifty prev close <= 20DMA)
  INV3 = G3 dropped  (counter-trend per stock; includes rare
                      equality/unclassifiable rows from G3's drop rule)
Source CSVs: eq_round9_P2_{G1_nifty50,G2_nifty20,G3_stock_align}_dropped_{T125,T10}.csv
Pool totals (validated Round 8/9): T125 918 (Jan-May 678, Jun-Oct 240);
T10 947. HYPOTHESIS-GENERATION ONLY — no survivor language.
All figures provisional per 100 shares; net = gross - Rs40/trade.
"""
import csv, json
from pathlib import Path

BASE = Path.home() / "workspace/trading"
FILES = {
    "INV1": ("G1_nifty50", "Nifty prev close <= 50DMA (inverted G1)"),
    "INV2": ("G2_nifty20", "Nifty prev close <= 20DMA (inverted G2)"),
    "INV3": ("G3_stock_align", "Counter-trend per stock (inverted G3)"),
}
POOL = {"T125": {"total": 918, "JM": 678, "JO": 240},
        "T10": {"total": 947, "JM": None, "JO": None}}  # JM/JO for T10 read from kept+dropped

def load(tag, exit_):
    p = BASE / f"eq_round9_P2_{tag}_dropped_{exit_}.csv"
    with open(p) as f:
        return list(csv.DictReader(f))

def half_of(d):
    m = int(d[5:7])
    return "JM" if m <= 5 else "JO"

def stats(rows):
    n = len(rows)
    gross = sum(float(r["gross_rs_provisional_per100"]) for r in rows)
    net = sum(float(r["net_rs_provisional_per100"]) for r in rows)
    wins = sum(1 for r in rows if float(r["net_rs_provisional_per100"]) > 0)
    tgts = sum(1 for r in rows if r["exit_reason"] == "target")
    return {"n": n, "gross": round(gross, 2), "net": round(net, 2),
            "gross_exp": round(gross / n, 2) if n else 0.0,
            "win_pct": round(100 * wins / n, 1) if n else 0.0,
            "target_pct": round(100 * tgts / n, 1) if n else 0.0}

def key(r):
    return (r["date"], r["stock"], r["direction"], r["entry_time"], r["round"])

out = {"basis": "provisional per 100 shares, net = gross - Rs40/trade",
       "label": "HYPOTHESIS-GENERATION ONLY — data-suggested, not a survivor",
       "variants": {}}

sets125 = {}
for inv, (tag, defn) in FILES.items():
    v = {"definition": defn, "exits": {}}
    for exit_ in ("T125", "T10"):
        rows = load(tag, exit_)
        if exit_ == "T125":
            sets125[inv] = {key(r) for r in rows}
        jm = [r for r in rows if half_of(r["date"]) == "JM"]
        jo = [r for r in rows if half_of(r["date"]) == "JO"]
        oct_ = [r for r in rows if r["date"].startswith("2026-10")]
        pool = POOL[exit_]
        share = {}
        if pool["JM"]:
            share = {"JM_pct": round(100 * len(jm) / pool["JM"], 1),
                     "JO_pct": round(100 * len(jo) / pool["JO"], 1),
                     "total_pct": round(100 * len(rows) / pool["total"], 1)}
        v["exits"][exit_] = {
            "all": stats(rows), "JM": stats(jm), "JO": stats(jo), "OCT": stats(oct_),
            "share_of_P2": share,
            "long": stats([r for r in rows if r["direction"] == "LONG"]),
            "short": stats([r for r in rows if r["direction"] == "SHORT"]),
            "by_month": {m: stats([r for r in rows if r["date"][5:7] == m])
                         for m in [f"{i:02d}" for i in range(1, 11)]},
        }
    out["variants"][inv] = v

# Overlap on T125 trade keys
ov = {}
names = list(sets125)
for i, a in enumerate(names):
    for b in names[i + 1:]:
        inter = len(sets125[a] & sets125[b])
        union = len(sets125[a] | sets125[b])
        ov[f"{a}|{b}"] = {"shared": inter, "union": union,
                          "jaccard": round(inter / union, 3) if union else 0.0,
                          "shared_pct_of_smaller": round(100 * inter / min(len(sets125[a]), len(sets125[b])), 1)}
ov["all_three_shared"] = len(sets125["INV1"] & sets125["INV2"] & sets125["INV3"])
ov["sizes"] = {k: len(v) for k, v in sets125.items()}
out["overlap_T125"] = ov

with open(BASE / "stocks_equity_round10_results.json", "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps(out, indent=1))
