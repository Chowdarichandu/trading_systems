#!/usr/bin/env python3
"""ROUND 9 — diagnosis 2 (audit): cross-tabs behind the frozen
separators for WS1/WS3. CERT rows by (regime cell x NIFTY-state
bucket) per year; IDX rows by cell per year; and the exact
full-population effect of the three candidate state rules:
  NOTCH:   drop CERT rows with NIFTY 10:25 move in (-0.30%, 0)
  UPGUARD: drop CERT rows on UP-cell days with NIFTY 10:25 move < 0
  IDXCELL: drop IDX rows on UP-cell days
No candidate is scored here — sleeve-level arithmetic only.
"""
import sys
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r8_builders as B8
import stocks_engine_r9_lib as R9
import stocks_engine_r9_ingredients as ING

ing = ING.build_all()
cert, idx = ing["cert"], ing["idx_r"]

def nb(x):
    if x is None:
        return "?"
    return "<=-0.30" if x <= -0.30 else ("(-0.30,0)" if x < 0
                                         else ">=0")

for yr in (2025, 2026):
    print(f"\n##### {yr} CERT by cell x NIFTY bucket")
    agg = {}
    for t in cert[yr]:
        k = (R9.LABELS.get(t["date"]), nb(B8.nifty_move(
            t["date"], "10:25")))
        a = agg.setdefault(k, [0, 0.0])
        a[0] += 1
        a[1] = round(a[1] + t["net"], 2)
    for cell in ("DOWN", "FLAT", "UP"):
        parts = [f"{b}: {agg.get((cell, b), [0, 0.0])[0]} tr "
                 f"{agg.get((cell, b), [0, 0.0])[1]:+.2f}"
                 for b in ("<=-0.30", "(-0.30,0)", ">=0")]
        print(f"  {cell:5} " + " | ".join(parts))
    print(f"##### {yr} IDX by cell")
    agg = {}
    for t in idx[yr]:
        k = R9.LABELS.get(t["date"])
        a = agg.setdefault(k, [0, 0.0])
        a[0] += 1
        a[1] = round(a[1] + t["net"], 2)
    print("  " + " | ".join(f"{k}: {v[0]} tr {v[1]:+.2f}"
                            for k, v in sorted(agg.items())))

def effect(rows, dropfn, yr):
    kept = [t for t in rows[yr] if not dropfn(t)]
    dropped = [t for t in rows[yr] if dropfn(t)]
    return (len(dropped), round(sum(t["net"] for t in dropped), 2),
            round(sum(t["net"] for t in kept), 2))

rules = {
    "NOTCH": lambda t: (lambda x: x is not None and -0.30 < x < 0)(
        B8.nifty_move(t["date"], "10:25")),
    "UPGUARD": lambda t: R9.LABELS.get(t["date"]) == "UP" and (
        lambda x: x is not None and x < 0)(
        B8.nifty_move(t["date"], "10:25")),
}
for name, fn in rules.items():
    for yr in (2025, 2026):
        nd, sd, kept = effect(cert, fn, yr)
        print(f"{name} {yr}: drops {nd} rows net {sd:+.2f}; sleeve "
              f"kept net {kept:+.2f}")
    both = [t for yr in (2025, 2026) for t in cert[yr] if fn(t)]
    print(f"{name} combined dropped net: "
          f"{round(sum(t['net'] for t in both), 2):+.2f} "
          f"({len(both)} rows)")
nd = {yr: effect(idx, lambda t: R9.LABELS.get(t["date"]) == "UP",
                 yr) for yr in (2025, 2026)}
for yr in (2025, 2026):
    print(f"IDXCELL {yr}: drops {nd[yr][0]} UP rows net "
          f"{nd[yr][1]:+.2f}; IDX sleeve kept net {nd[yr][2]:+.2f}")

# Stack-month check for the two CERT rules (arithmetic on the
# R8-02 stack months; the gate itself runs in the WS1 scripts).
base_jan, base_dec = 2200.31, 1207.95
others_jan = 64.16 - 29.01        # R2-26 + R5-03-clean Jan deltas
others_dec = 532.91               # R2-26 Dec delta; others 0
cert_jan = [t for t in cert[2025] if t["date"][:7] == "2025-01"]
cert_dec = [t for t in cert[2025] if t["date"][:7] == "2025-12"]
for name, fn in rules.items():
    kj = round(sum(t["net"] for t in cert_jan if not fn(t)), 2)
    kd = round(sum(t["net"] for t in cert_dec if not fn(t)), 2)
    print(f"{name}: stack Jan -> {round(base_jan + others_jan + kj, 2)}"
          f" | stack Dec -> {round(base_dec + others_dec + kd, 2)}")
both_fn = lambda t: rules["NOTCH"](t) or rules["UPGUARD"](t)
kj = round(sum(t["net"] for t in cert_jan if not both_fn(t)), 2)
kd = round(sum(t["net"] for t in cert_dec if not both_fn(t)), 2)
print(f"NOTCH+UPGUARD: stack Jan -> "
      f"{round(base_jan + others_jan + kj, 2)} | stack Dec -> "
      f"{round(base_dec + others_dec + kd, 2)}")
for yr in (2025, 2026):
    kept = round(sum(t["net"] for t in cert[yr] if not both_fn(t)), 2)
    print(f"NOTCH+UPGUARD {yr}: sleeve kept net {kept:+.2f}")
