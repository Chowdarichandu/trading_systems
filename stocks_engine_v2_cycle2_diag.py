#!/usr/bin/env python3
"""V2 CYCLE 2 DIAGNOSIS — per component x year x (stock x dir) slices on the
combined two-year incumbent book (post-Cycle-1). Read-only: no fix is scored
here. Anchors asserted against the state file's v2 best.
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade,
paper only, real Rs0.
"""
import csv, json
from collections import defaultdict

WS = "/home/hatch/workspace/trading"

def load(fn):
    return [{**t, "net": float(t["net"])} for t in csv.DictReader(open(f"{WS}/{fn}"))]

b25 = load("stocks_engine_v2_c1_book2025_trades.csv")
b26 = load("stocks_engine_v2_c1_book2026_trades.csv")
st = json.load(open(f"{WS}/stocks_engine_state.json"))["v2"]
t25 = round(sum(t["net"] for t in b25), 2)
t26 = round(sum(t["net"] for t in b26), 2)
assert (len(b25), t25) == (st["best_trades"]["2025"], st["best_by_year"]["2025"]), (len(b25), t25)
assert (len(b26), t26) == (st["best_trades"]["2026"], st["best_by_year"]["2026"]), (len(b26), t26)
print(f"ANCHOR OK: 2025 {len(b25)} tr / {t25} | 2026 {len(b26)} tr / {t26} | "
      f"combined {round(t25+t26,2)} == state best {st['combined_best']}")

def comp_year(book):
    d = defaultdict(lambda: [0, 0.0, 0])
    for t in book:
        e = d[t["comp"]]; e[0] += 1; e[1] += t["net"]; e[2] += t["net"] > 0
    return d

c25, c26 = comp_year(b25), comp_year(b26)
print("\n== COMPONENT x YEAR (post-C1 incumbent) ==")
print(f"{'comp':<11} {'2025 tr':>7} {'2025 net':>11} {'2025 w':>6} | {'2026 tr':>7} {'2026 net':>11} {'2026 w':>6} | worse-year")
for comp in sorted(set(c25) | set(c26), key=lambda c: min(c25[c][1], c26[c][1])):
    a, b = c25[comp], c26[comp]
    print(f"{comp:<11} {a[0]:>7} {a[1]:>11.2f} {a[2]:>6} | {b[0]:>7} {b[1]:>11.2f} {b[2]:>6} | {min(a[1], b[1]):>10.2f}")

# slices: comp x stock x dir, both years
def slices(book):
    d = defaultdict(lambda: [0, 0.0, 0])
    for t in book:
        e = d[(t["comp"], t["stock"], t["dir"])]; e[0] += 1; e[1] += t["net"]; e[2] += t["net"] > 0
    return d
s25, s26 = slices(b25), slices(b26)
keys = set(s25) | set(s26)

print("\n== SLICES NEGATIVE IN BOTH YEARS (cross-year rot candidates) ==")
both = []
for k in keys:
    a, b = s25.get(k, [0, 0.0, 0]), s26.get(k, [0, 0.0, 0])
    if a[1] < 0 and b[1] < 0:
        both.append((k, a, b, a[1] + b[1]))
both.sort(key=lambda x: x[3])
for k, a, b, tot in both:
    print(f"{k[0]:<11} {k[1]:<12} {k[2]:<5} | 2025 {a[0]:>3} tr {a[1]:>9.2f} ({a[2]}w) | "
          f"2026 {b[0]:>3} tr {b[1]:>9.2f} ({b[2]}w) | combined {tot:>9.2f}")
print(f"count: {len(both)} | total combined net of both-negative slices: "
      f"{round(sum(x[3] for x in both), 2)}")

print("\n== WEAKEST COMPONENT (P2F-R2) — all slices, by 2025 net ==")
for comp in ("P2F-R2", "R2-LOWBAND", "N4-V3"):
    print(f"-- {comp} --")
    rows = []
    for k in keys:
        if k[0] != comp:
            continue
        a, b = s25.get(k, [0, 0.0, 0]), s26.get(k, [0, 0.0, 0])
        rows.append((k, a, b))
    rows.sort(key=lambda x: x[1][1])
    for k, a, b in rows:
        print(f"  {k[1]:<12} {k[2]:<5} | 2025 {a[0]:>3} tr {a[1]:>9.2f} ({a[2]}w) | "
              f"2026 {b[0]:>3} tr {b[1]:>9.2f} ({b[2]}w)")

print("\n== 2025 MONTH TABLE PER COMPONENT (post-C1) ==")
def comp_months(book, comp):
    m = defaultdict(float)
    for t in book:
        if t["comp"] == comp:
            m[t["date"][:7]] += t["net"]
    return {f"2025-{i:02d}": round(m.get(f"2025-{i:02d}", 0.0), 2) for i in range(1, 13)}
for comp in sorted(set(c25)):
    print(f"{comp:<11}", comp_months(b25, comp))

json_out = {
    "anchor": {"y2025": [len(b25), t25], "y2026": [len(b26), t26]},
    "both_negative_slices": [
        {"comp": k[0], "stock": k[1], "dir": k[2],
         "y2025": [a[0], round(a[1], 2), a[2]], "y2026": [b[0], round(b[1], 2), b[2]],
         "combined": round(tot, 2)} for k, a, b, tot in both],
}
json.dump(json_out, open(f"{WS}/v2_out/v2_cycle2_diag.json", "w"), indent=1)
print("\nwrote v2_out/v2_cycle2_diag.json")
