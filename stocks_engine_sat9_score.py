#!/usr/bin/env python3
"""ENGINE SAT-9 SCORE: CHALLENGER F4-MIRROR — capped-band signal-fade
on ABOVE-50DMA days. Spec frozen in stocks_engine_frozen.md (SAT-9
section) BEFORE this ran. Construction = H1.build_cell sig-mode with
dirmode="fade" (the identical audited machinery that builds F4, with
the direction flipped and the regime gate complemented), T150/S080,
first-signal-only, RF-1, book F4 exclusions applied symmetrically.
Controls in the same pass: timing audit (H1._AUDIT), Placebo A
(sign-flip = follow on the same above50 days), Placebo B (lag =
previous trading day's premove, regime on the actual day).
Anchor: incumbent rebuild == state (779 tr / +149,365.15 / Oct
+50,349.79) asserted first. Paper, real Rs0, per 100 shares,
Rs40/trade, home 25, Jan-Oct 2026."""
import csv, sys, json, datetime
from collections import defaultdict
sys.path.insert(0, "/home/hatch/workspace/trading")
import importlib.util

BASE = "/home/hatch/workspace/trading"
def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    _a = sys.argv; sys.argv = [name]
    spec.loader.exec_module(m); sys.argv = _a
    return m
H1 = load_mod("H1", f"{BASE}/stocks_H1.py")
M1 = load_mod("M1", f"{BASE}/stocks_M1.py")
M, U = H1.M, H1.U
T, TP, SP = "10:00", 1.50, 0.80

def wk(d): return datetime.date.fromisoformat(d).weekday() >= 5
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))

STATE = {"2026-01": 12497.27, "2026-02": 3611.69, "2026-03": 22321.47,
         "2026-04": 3671.26, "2026-05": 28317.69, "2026-06": 3941.51,
         "2026-07": 3196.63, "2026-08": 1735.16, "2026-09": 19722.68,
         "2026-10": 50349.79}
STATE_TOTAL, STATE_TRADES, STATE_EXTOP3 = 149365.15, 779, 30773.31
EXCL_DIR = {("GODREJCP", "SHORT"), ("INDUSTOWER", "LONG"),
            ("HINDUNILVR", "SHORT"), ("UNITDSPR", "SHORT"),
            ("HINDCOPPER", "SHORT")}

# ---------------- incumbent rebuild (anchor) ----------------
inv = [t for t in M1.load_inv_long()
       if not wk(t["date"]) and t["stock"] != "BDL"]
n4  = [t for t in M1.load_n4()
       if not wk(t["date"]) and t["stock"] != "ASTRAL"]
p2f = [t for t in M1.load_p2f(2.5)
       if not wk(t["date"]) and t["stock"] != "ASTRAL"
       and t["stock"] != "HINDUNILVR"]
f4  = [{"date": r["date"], "stock": r["symbol"], "comp": "F4",
        "dir": r["dir"], "setup": r["setup"], "leg": r["leg"],
        "net": float(r["net"])}
       for r in rd("stocks_engine_oc4_f4s080_trades.csv")
       if not wk(r["date"]) and r["setup"] != "setup3_bounce_rejection"
       and r["leg"] != "round2"
       and not (r["symbol"] == "GODREJCP" and r["dir"] == "SHORT")
       and not (r["symbol"] == "INDUSTOWER" and r["dir"] == "LONG")
       and not (r["symbol"] == "HINDUNILVR" and r["dir"] == "SHORT")
       and not (r["symbol"] == "UNITDSPR" and r["dir"] == "SHORT")
       and not (r["symbol"] == "HINDCOPPER" and r["dir"] == "SHORT")]
for t in inv: t.setdefault("comp", "INV-LONG")
for t in n4:  t.setdefault("comp", "N4-V3")
for t in p2f: t.setdefault("comp", "P2F")

def mt(trades):
    m = defaultdict(float); c = defaultdict(int)
    for t in trades: m[t["date"][:7]] += t["net"]; c[t["date"][:7]] += 1
    return ({k: round(m[k], 2) for k in sorted(m)},
            {k: c[k] for k in sorted(c)})

def extop3(trades):
    per = defaultdict(float)
    for t in trades: per[t["stock"]] += t["net"]
    top3 = sorted(per.items(), key=lambda kv: -kv[1])[:3]
    return (round(sum(t["net"] for t in trades
                      if t["stock"] not in {k for k, _ in top3}), 2),
            [k for k, _ in top3])

base = inv + n4 + p2f + f4
bt, _ = mt(base)
anchor_ok = (bt == STATE
             and round(sum(t["net"] for t in base), 2) == STATE_TOTAL
             and len(base) == STATE_TRADES)
print("ANCHOR (incumbent == state):", anchor_ok,
      f"| trades {len(base)} total {round(sum(t['net'] for t in base),2)}")
assert anchor_ok, "ANCHOR FAILED"
ex0, top3_0 = extop3(base)
print(f"incumbent ex-top-3: {ex0} (top3 {top3_0})")
assert ex0 == STATE_EXTOP3, "EX-TOP-3 ANCHOR FAILED"

# ---------------- mirror + placebo builds ----------------
H1.ensure_prep()
ns = M.get_ns(H1.WHICH)
all_days = sorted({d for (s, d) in ns["DAYCTX"]
                   if "2026-01-01" <= d <= "2026-10-31"})
prev_of = {d: all_days[i - 1] for i, d in enumerate(all_days) if i > 0}
above_days = [d for d in all_days if not H1.below50(d) and not wk(d)]
print(f"\ntrading days {len(all_days)} | above50 non-weekend days "
      f"{len(above_days)} | October above50 days "
      f"{len([d for d in above_days if d.startswith('2026-10')])}")

def excluded(tr):
    return (tr["setup"] == "setup3_bounce_rejection"
            or (tr["symbol"], tr["dir"]) in EXCL_DIR)

def build_family(dirmode, lag=False):
    """First-signal-only build over above50 days; returns raw trades
    (pre-exclusion) plus the audit delta for this family."""
    a0 = dict(H1._AUDIT)
    out = []
    for sym in ns["SYMBOLS"]:
        for day in above_days:
            ctx = ns["DAYCTX"].get((sym, day))
            if ctx is None:
                continue
            pm_o = None
            if lag:
                pd = prev_of.get(day)
                pctx = ns["DAYCTX"].get((sym, pd)) if pd else None
                if pctx is None:
                    continue
                pm_o = M.premove(pctx["candles"], T)
                if pm_o is None:
                    continue
                pm_use = pm_o
            else:
                pm_use = M.premove(ctx["candles"], T)
                if pm_use is None:
                    continue
            if not (0.005 <= abs(pm_use) < 0.010):
                continue
            trs = H1.build_cell(ns, sym, day, T, 0.005, dirmode, "sig",
                                TP, SP, pm_override=pm_o)
            if trs:
                out.append(trs[0])   # first-signal-only (F4R1 rule)
    audit = {"trades": H1._AUDIT["trades"] - a0["trades"],
             "violations": H1._AUDIT["violations"] - a0["violations"]}
    return out, audit

def apply_excl(trades):
    kept = [t for t in trades if not excluded(t)]
    return kept, len(trades) - len(kept)

mirror_raw, aud_m = build_family("fade")
mirror, n_excl_m = apply_excl(mirror_raw)
placA_raw, aud_a = build_family("follow")
placA, n_excl_a = apply_excl(placA_raw)
placB_raw, aud_b = build_family("fade", lag=True)
placB, n_excl_b = apply_excl(placB_raw)
print(f"audits: mirror {aud_m} | placeboA {aud_a} | placeboB {aud_b}")
print(f"built (raw -> after exclusions): mirror {len(mirror_raw)} -> "
      f"{len(mirror)} | placeboA {len(placA_raw)} -> {len(placA)} | "
      f"placeboB {len(placB_raw)} -> {len(placB)}")

def summarize(trades):
    months, _ = mt([{"date": t["date"], "net": t["net"]} for t in trades])
    per = defaultdict(float)
    for t in trades: per[t["symbol"]] += t["net"]
    net = round(sum(t["net"] for t in trades), 2)
    return {"trades": len(trades), "net": net,
            "months": {m: months.get(m, 0.0)
                       for m in [f"2026-{i:02d}" for i in range(1, 11)]},
            "jan_may": round(sum(v for m, v in months.items()
                                 if m <= "2026-05"), 2),
            "jun_oct": round(sum(v for m, v in months.items()
                                 if m >= "2026-06"), 2),
            "jan_sep": round(sum(t["net"] for t in trades
                                 if not t["date"].startswith("2026-10")), 2),
            "october": months.get("2026-10", 0.0),
            "breadth": sum(1 for v in per.values() if v > 0),
            "exp": round(net / len(trades), 2) if trades else None,
            "per_stock": {k: round(v, 2) for k, v in
                          sorted(per.items(), key=lambda kv: -kv[1])}}

sm, sa, sb = summarize(mirror), summarize(placA), summarize(placB)
for nm, s in (("MIRROR", sm), ("PLACEBO-A sign-flip", sa),
              ("PLACEBO-B lag", sb)):
    print(f"\n== {nm}: trades={s['trades']} net={s['net']} "
          f"JanMay={s['jan_may']} JunOct={s['jun_oct']} "
          f"Oct={s['october']} breadth={s['breadth']}/25 exp={s['exp']}")
    print(f"   months={s['months']}")
print(f"\nplacebo margins (full period): vs A "
      f"{round(sm['net'] - sa['net'], 2)} | vs B "
      f"{round(sm['net'] - sb['net'], 2)}")
print(f"placebo margins (Jan-Sep):     vs A "
      f"{round(sm['jan_sep'] - sa['jan_sep'], 2)} | vs B "
      f"{round(sm['jan_sep'] - sb['jan_sep'], 2)}")

# overlap vs incumbent F4 (disjoint day-states, verified mechanically)
f4_days = {t["date"] for t in f4}
mir_days = {t["date"] for t in mirror}
f4_pairs = {(t["date"], t["stock"]) for t in f4}
mir_pairs = {(t["date"], t["symbol"]) for t in mirror}
overlap_days = f4_days & mir_days
overlap_pairs = f4_pairs & mir_pairs
print(f"\noverlap vs incumbent F4: shared dates {len(overlap_days)}, "
      f"shared (date,symbol) {len(overlap_pairs)}")
assert not overlap_days and not overlap_pairs, "OVERLAP NOT ZERO"

# ---------------- union + gate ----------------
mir_book = [{"date": t["date"], "stock": t["symbol"], "comp": "F4-MIRROR",
             "dir": t["dir"], "setup": t["setup"], "leg": t["leg"],
             "net": float(t["net"])} for t in mirror]
union = base + mir_book
nt, nc = mt(union)
tot_new = round(sum(t["net"] for t in union), 2)
ex1, top3_1 = extop3(union)
print(f"\n{'month':8} {'incumbent':>10} {'union':>10} {'delta':>10} "
      f"{'trades':>7}")
for k in sorted(STATE):
    print(f"{k:8} {STATE[k]:>10.2f} {nt.get(k,0.0):>10.2f} "
          f"{round(nt.get(k,0.0)-STATE[k],2):>10.2f} {nc.get(k,0):>7}")
print(f"{'TOTAL':8} {STATE_TOTAL:>10.2f} {tot_new:>10.2f} "
      f"{round(tot_new-STATE_TOTAL,2):>10.2f} {len(union):>7}")
print(f"union ex-top-3: {ex1} (top3 {top3_1}) | incumbent {ex0}")
aug_after = nt["2026-08"]
n4_shortfall = round(4020.54 - aug_after, 2)
print(f"August union: Rs{aug_after} | mirror August slice: "
      f"Rs{sm['months']['2026-08']} | N4-revisit shortfall: "
      f"Rs{n4_shortfall} (was Rs2,285.38)")
print(f"October union: Rs{nt['2026-10']} | mirror October slice: "
      f"{sm['october']} ({sm['months'] and len([t for t in mirror if t['date'].startswith('2026-10')])} tr)")

print("\n=== SATURATION GATE (frozen SAT-9) ===")
ga = tot_new > STATE_TOTAL
gb = all(v > 0 for v in nt.values())
gc = nt["2026-10"] >= 50000
gd = ex1 >= ex0
ge = (aud_m["violations"] == 0 and sm["net"] > sa["net"]
      and sm["net"] > sb["net"])
print(f"(a) total rises: {tot_new} > {STATE_TOTAL} -> {ga}")
print(f"(b) all ten months > 0: {gb} (min {min(nt.values())} in "
      f"{min(nt, key=nt.get)})")
print(f"(c) October >= 50,000: {nt['2026-10']} -> {gc}")
print(f"(d) ex-top-3 not worse: {ex1} >= {ex0} -> {gd}")
print(f"(e) controls: audit violations {aud_m['violations']}, mirror "
      f"{sm['net']} > placeboA {sa['net']} and > placeboB {sb['net']} "
      f"-> {ge}")
banked = all([ga, gb, gc, gd, ge])
print("BANKED:", banked)

with open(f"{BASE}/stocks_engine_sat9_mirror_trades.csv", "w",
          newline="") as f:
    if mirror:
        w = csv.DictWriter(f, fieldnames=list(mirror[0].keys()))
        w.writeheader()
        for t in sorted(mirror, key=lambda x: (x["date"], x["symbol"])):
            w.writerow(t)
json.dump({"anchor_ok": anchor_ok, "fix": "SAT-9-F4-MIRROR",
           "mirror": sm, "placeboA_signflip": sa, "placeboB_lag": sb,
           "audits": {"mirror": aud_m, "placeboA": aud_a,
                      "placeboB": aud_b},
           "exclusions_dropped": {"mirror": n_excl_m, "placeboA": n_excl_a,
                                  "placeboB": n_excl_b},
           "overlap": {"shared_dates": len(overlap_days),
                       "shared_pairs": len(overlap_pairs)},
           "new_month_table": nt, "new_total": tot_new,
           "new_trades": len(union), "banked": banked,
           "deltas": {k: round(nt.get(k, 0.0) - STATE[k], 2)
                      for k in STATE},
           "ex_top3_before": ex0, "ex_top3_after": ex1,
           "legs": {"a_total": ga, "b_all_green": gb, "c_oct": gc,
                    "d_extop3": gd, "e_controls": ge},
           "august_after": aug_after,
           "n4_revisit_august_shortfall_after": n4_shortfall},
          open(f"{BASE}/stocks_engine_sat9_result.json", "w"), indent=1)
print("\nwrote stocks_engine_sat9_result.json + mirror trades csv")
