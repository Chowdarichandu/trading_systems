#!/usr/bin/env python3
"""V3 DELETION REGISTRY — re-derived at the CURRENT v3 book (Lesson 16:
re-derive from scratch before use). For every (comp x stock x dir) slice
with full-period net <= -500 and each-year net <= 0, compute the FULL
month-leg map and the post-deletion sorted 22-month vector; report which
slices lexicographically BEAT the incumbent vector (a slice with a
positive leg in a month below its lifted months is a rotation, not a
lift — Lesson 38 corollary (iii)). Incumbent's own trades only — no
challenger P&L. Read-only.
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade,
paper only, real Rs0.
"""
import json, sys
from collections import defaultdict
sys.path.insert(0, "/home/hatch/workspace/trading")
from stocks_engine_v3_lib import boot, load_books, score, lexi_beats, WS

g, LABELS = boot()
state = json.load(open(f"{WS}/stocks_engine_state.json"))["v3"]
books = load_books(state["book_files"])
old = score(books, LABELS)
assert old["vector_sorted"] == state["month_vector_sorted_asc"]
print(f"incumbent asserted: combined {old['combined']} | worst {old['bottom5'][0]}")

slices = defaultdict(lambda: {"years": defaultdict(float), "months": defaultdict(float),
                              "n": 0, "rows": []})
for yr in ("2025", "2026"):
    for t in books[yr]:
        s = slices[(t["comp"], t["stock"], t["dir"])]
        s["years"][yr] += t["net"]; s["months"][t["date"][:7]] += t["net"]
        s["n"] += 1; s["rows"].append((yr, t))

cands = []
for k, s in slices.items():
    full = round(s["years"]["2025"] + s["years"]["2026"], 2)
    if full <= -500 and s["years"]["2025"] <= 0 and s["years"]["2026"] <= 0:
        new_months = dict(old["months"])
        for m, v in s["months"].items():
            new_months[m] = round(new_months[m] - v, 2)
        new_vec = sorted(new_months.values())
        cands.append({"slice": k, "n": s["n"], "full": full,
                      "y2025": round(s["years"]["2025"], 2),
                      "y2026": round(s["years"]["2026"], 2),
                      "month_legs": {m: round(v, 2) for m, v in sorted(s["months"].items())},
                      "beats": lexi_beats(new_vec, old["vector_sorted"]),
                      "new_bottom5": sorted(new_months.items(), key=lambda kv: kv[1])[:5]})
cands.sort(key=lambda r: (not r["beats"], r["full"]))
print(f"{len(cands)} qualifying slices (full <= -500, each year <= 0):")
for c in cands:
    print(f"  {c['slice']} n={c['n']} full {c['full']} (25 {c['y2025']} / 26 {c['y2026']}) "
          f"beats={c['beats']} legs={c['month_legs']}")
    if c["beats"]:
        print(f"      new bottom5: {c['new_bottom5']}")
json.dump({"incumbent_bottom5": old["bottom5"], "candidates": [
    {**c, "slice": list(c["slice"])} for c in cands]},
    open(f"{WS}/v3_out/v3_registry.json", "w"), indent=1)
print("wrote v3_out/v3_registry.json")
