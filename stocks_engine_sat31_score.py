#!/usr/bin/env python3
"""ENGINE SAT-31 SCORE: NEW COMPONENT F4-UPBAND -- F4's joint state
(below-50DMA gate, FOLLOW, V5 sig machinery, first-signal-only) on
the band's upper complement slice [1.0%, 1.25%) by 10:00, exits
T150/S095 (the book's current F4 exits), RF-1, book F4 exclusions
applied symmetrically. Spec frozen in stocks_engine_frozen.md
(SAT-31 section) BEFORE this ran. DISCLOSED PRIOR: M2 found the
>=1% region was the ungated cell's loss driver; this tests whether
the JOINT STATE on this slice only rescues it.
Controls in the same pass: timing audit (H1._AUDIT deltas, both
builds), sign-flip placebo on identical entries (fade), halves,
breadth, ex-top-3, mechanical overlap vs incumbent F4 == 0.
Anchor: incumbent rebuild == state (656 tr / +196,346.96 / Oct
+52,844.37 / ex-top-3 71,257.47) asserted first, per book law
(N4 = SAT-15 dump minus SAT-17/SAT-24 exclusions; F4 = SAT-10 dump
minus all F4 exclusions through SAT-30; INV-LONG minus
BDL+VEDL+HINDZINC+INDUSTOWER+KALYANKJIL; P2F-R2 minus SAT-21).
Paper, real Rs0, per 100 shares, Rs40/trade, home 25, Jan-Oct 2026."""
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
M = H1.M
T, TP, SP = "10:00", 1.50, 0.95
BAND_LO, BAND_HI = 0.010, 0.0125

def wk(d): return datetime.date.fromisoformat(d).weekday() >= 5
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))

STATE = {"2026-01": 28536.25, "2026-02": 18564.56, "2026-03": 20584.41,
         "2026-04": 9895.49, "2026-05": 34880.86, "2026-06": 3823.22,
         "2026-07": 6543.43, "2026-08": 1111.86, "2026-09": 19562.51,
         "2026-10": 52844.37}
STATE_TOTAL, STATE_TRADES, STATE_EXTOP3 = 196346.96, 656, 71257.47
EXCL_DIR = {("GODREJCP", "SHORT"), ("INDUSTOWER", "LONG"),
            ("HINDUNILVR", "SHORT"), ("UNITDSPR", "SHORT"),
            ("HINDCOPPER", "SHORT"), ("OIL", "SHORT"),
            ("IRCTC", "SHORT"), ("HINDALCO", "LONG"),
            ("TATASTEEL", "LONG"), ("NHPC", "SHORT"),
            ("PFC", "SHORT"), ("RECLTD", "SHORT")}

# ---------------- incumbent rebuild (anchor) ----------------
inv = [{"date": t["date"], "stock": t["stock"], "comp": "INV-LONG",
        "dir": t["dir"], "net": t["net"]}
       for t in M1.load_inv_long()
       if not wk(t["date"]) and t["stock"] != "BDL"
       and t["stock"] != "VEDL" and t["stock"] != "HINDZINC"
       and t["stock"] != "INDUSTOWER" and t["stock"] != "KALYANKJIL"]
n4 = [{"date": r["date"], "stock": r["stock"], "comp": "N4-V3",
       "dir": r["direction"], "net": float(r["net"])}
      for r in rd("stocks_engine_sat15_n4_t150s080_trades.csv")
      if not wk(r["date"]) and r["stock"] != "ASTRAL"
      and not (r["stock"] == "TVSMOTOR" and r["direction"] == "LONG")
      and not (r["stock"] == "OIL" and r["direction"] == "LONG")]
p2f = [{"date": t["date"], "stock": t["stock"], "comp": "P2F",
        "dir": t["dir"], "net": t["net"]}
       for t in M1.load_p2f(2.5)
       if not wk(t["date"]) and t["stock"] != "ASTRAL"
       and t["stock"] != "HINDUNILVR"
       and not (t["stock"] == "HINDALCO" and t["dir"] == "LONG")]
f4 = []
for r in rd("stocks_engine_sat10_f4s095_trades.csv"):
    if wk(r["date"]) or r["setup"] == "setup3_bounce_rejection" \
            or r["leg"] == "round2" or (r["symbol"], r["dir"]) in EXCL_DIR:
        continue
    f4.append({"date": r["date"], "stock": r["symbol"], "comp": "F4",
               "dir": r["dir"], "net": float(r["net"])})
r2 = [{"date": r["date"], "stock": r["symbol"], "comp": "P2F-R2",
       "dir": r["direction"], "net": float(r["net_rs"])}
      for r in rd("stocks_engine_sat13_p2fr2_trades.csv")
      if not (r["symbol"] == "TVSMOTOR" and r["direction"] == "LONG")]
book = inv + n4 + p2f + f4 + r2

def mt(trades):
    m = defaultdict(float); c = defaultdict(int)
    for t in trades: m[t["date"][:7]] += t["net"]; c[t["date"][:7]] += 1
    return ({k: round(m.get(k, 0.0), 2) for k in sorted(STATE)},
            {k: c[k] for k in sorted(c)})

def extop3(trades):
    per = defaultdict(float)
    for t in trades: per[t["stock"]] += t["net"]
    top3 = sorted(per.items(), key=lambda kv: -kv[1])[:3]
    return (round(sum(t["net"] for t in trades
                      if t["stock"] not in {k for k, _ in top3}), 2),
            [(k, round(v, 2)) for k, v in top3])

bt, _ = mt(book)
ex0, top3_0 = extop3(book)
anchor_ok = (bt == STATE
             and round(sum(t["net"] for t in book), 2) == STATE_TOTAL
             and len(book) == STATE_TRADES and ex0 == STATE_EXTOP3)
print(f"ANCHOR: incumbent == state: {anchor_ok} | {len(book)} tr / "
      f"{round(sum(t['net'] for t in book),2)} / ex-top-3 {ex0} "
      f"(top3 {top3_0})")
print(f"  components: INV {len(inv)} / N4 {len(n4)} / P2F {len(p2f)} / "
      f"F4 {len(f4)} / R2 {len(r2)}")
assert anchor_ok, "ANCHOR FAILED -- do not judge"

# ---------------- UPBAND + placebo builds ----------------
H1.ensure_prep()
ns = M.get_ns(H1.WHICH)
all_days = sorted({d for (s, d) in ns["DAYCTX"]
                   if "2026-01-01" <= d <= "2026-10-31"})
below_days = [d for d in all_days if H1.below50(d) and not wk(d)]
print(f"\ntrading days {len(all_days)} | below50 non-weekend days "
      f"{len(below_days)} | October below50 days "
      f"{len([d for d in below_days if d.startswith('2026-10')])}")

def excluded(tr):
    return (tr["setup"] == "setup3_bounce_rejection"
            or (tr["symbol"], tr["dir"]) in EXCL_DIR)

def build_family(dirmode):
    """First-signal-only build over below50 days, premove band
    [BAND_LO, BAND_HI) at 10:00; returns raw trades + audit delta."""
    a0 = dict(H1._AUDIT)
    out = []
    for sym in ns["SYMBOLS"]:
        for day in below_days:
            ctx = ns["DAYCTX"].get((sym, day))
            if ctx is None:
                continue
            pm = M.premove(ctx["candles"], T)
            if pm is None:
                continue
            if not (BAND_LO <= abs(pm) < BAND_HI):
                continue
            trs = H1.build_cell(ns, sym, day, T, 0.005, dirmode, "sig",
                                TP, SP)
            if trs:
                out.append(trs[0])   # first-signal-only (SAT-6 rule)
    audit = {"trades": H1._AUDIT["trades"] - a0["trades"],
             "violations": H1._AUDIT["violations"] - a0["violations"]}
    return out, audit

def apply_excl(trades):
    kept = [t for t in trades if not excluded(t)]
    return kept, len(trades) - len(kept)

up_raw, aud_u = build_family("follow")
up, n_excl_u = apply_excl(up_raw)
pl_raw, aud_p = build_family("fade")
pl, n_excl_p = apply_excl(pl_raw)
print(f"audits: upband {aud_u} | placebo {aud_p}")
print(f"built (raw -> after exclusions): upband {len(up_raw)} -> "
      f"{len(up)} | placebo {len(pl_raw)} -> {len(pl)}")

def summarize(trades):
    months, _ = mt([{"date": t["date"], "net": t["net"]} for t in trades])
    per = defaultdict(float)
    for t in trades: per[t["symbol"]] += t["net"]
    net = round(sum(t["net"] for t in trades), 2)
    return {"trades": len(trades), "net": net,
            "months": months,
            "jan_may": round(sum(v for m, v in months.items()
                                 if m <= "2026-05"), 2),
            "jun_oct": round(sum(v for m, v in months.items()
                                 if m >= "2026-06"), 2),
            "win": sum(1 for t in trades if t["net"] > 0),
            "breadth": sum(1 for v in per.values() if v > 0),
            "exp": round(net / len(trades), 2) if trades else None,
            "per_stock": {k: round(v, 2) for k, v in
                          sorted(per.items(), key=lambda kv: -kv[1])}}

su, spl = summarize(up), summarize(pl)
for nm, s in (("UPBAND (follow)", su), ("PLACEBO (fade)", spl)):
    print(f"\n== {nm}: trades={s['trades']} net={s['net']} "
          f"JanMay={s['jan_may']} JunOct={s['jun_oct']} "
          f"win={s['win']} breadth={s['breadth']}/25 exp={s['exp']}")
    print(f"   months={s['months']}")
print(f"\nplacebo margin: total {round(su['net']-spl['net'],2)} | "
      f"expectancy {None if su['exp'] is None or spl['exp'] is None else round(su['exp']-spl['exp'],2)}")

# overlap vs incumbent F4 (disjoint premove bands, verified mechanically)
f4_pairs = {(t["date"], t["stock"]) for t in f4}
up_pairs = {(t["date"], t["symbol"]) for t in up}
overlap = f4_pairs & up_pairs
print(f"overlap vs incumbent F4: shared (date,symbol) {len(overlap)}")
assert not overlap, "OVERLAP NOT ZERO"

# ---------------- union + gate ----------------
up_book = [{"date": t["date"], "stock": t["symbol"], "comp": "F4-UPBAND",
            "dir": t["dir"], "net": float(t["net"])} for t in up]
union = book + up_book
nt, nc = mt(union)
tot_new = round(sum(t["net"] for t in union), 2)
ex1, top3_1 = extop3(union)
print(f"\n{'month':8} {'incumbent':>10} {'union':>10} {'delta':>10} "
      f"{'trades':>7}")
for k in sorted(STATE):
    print(f"{k:8} {STATE[k]:>10.2f} {nt[k]:>10.2f} "
          f"{round(nt[k]-STATE[k],2):>10.2f} {nc[k]:>7}")
print(f"{'TOTAL':8} {STATE_TOTAL:>10.2f} {tot_new:>10.2f} "
      f"{round(tot_new-STATE_TOTAL,2):>10.2f} {len(union):>7}")
print(f"union ex-top-3: {ex1} (top3 {top3_1}) | incumbent {ex0}")
print(f"August union: Rs{nt['2026-08']} | upband August slice: "
      f"Rs{su['months']['2026-08']}")
print(f"October union: Rs{nt['2026-10']} | upband October slice: "
      f"Rs{su['months']['2026-10']}")

print("\n=== SATURATION GATE (frozen SAT-31) ===")
ga = tot_new > STATE_TOTAL
gb = all(v > 0 for v in nt.values())
gc = nt["2026-10"] >= 50000
gd = ex1 >= ex0
ge = (anchor_ok and aud_u["violations"] == 0
      and su["net"] > spl["net"]
      and (su["exp"] or 0) > (spl["exp"] or 0))
print(f"(a) total rises: {tot_new} > {STATE_TOTAL} -> {ga}")
print(f"(b) all ten months > 0: {gb} (min {min(nt.values())} in "
      f"{min(nt, key=nt.get)})")
print(f"(c) October >= 50,000: {nt['2026-10']} -> {gc}")
print(f"(d) ex-top-3 not worse: {ex1} >= {ex0} -> {gd}")
print(f"(e) anchors/audit/placebo: anchor {anchor_ok}, audit "
      f"violations {aud_u['violations']}, upband {su['net']} > placebo "
      f"{spl['net']} and exp {su['exp']} > {spl['exp']} -> {ge}")
banked = all([ga, gb, gc, gd, ge])
print("BANKED:", banked)

with open(f"{BASE}/stocks_engine_sat31_upband_trades.csv", "w",
          newline="") as f:
    if up:
        w = csv.DictWriter(f, fieldnames=list(up[0].keys()))
        w.writeheader()
        for t in sorted(up, key=lambda x: (x["date"], x["symbol"])):
            w.writerow(t)
json.dump({"anchor_ok": anchor_ok, "fix": "SAT-31-F4-UPBAND",
           "upband": su, "placebo_fade": spl,
           "audits": {"upband": aud_u, "placebo": aud_p},
           "exclusions_dropped": {"upband": n_excl_u,
                                  "placebo": n_excl_p},
           "overlap_pairs": len(overlap),
           "new_month_table": nt, "new_total": tot_new,
           "new_trades": len(union), "banked": banked,
           "deltas": {k: round(nt[k] - STATE[k], 2) for k in STATE},
           "ex_top3_before": ex0, "ex_top3_after": ex1,
           "top3_before": top3_0, "top3_after": top3_1,
           "legs": {"a_total": ga, "b_all_green": gb, "c_oct": gc,
                    "d_extop3": gd, "e_controls": ge},
           "august_after": nt["2026-08"],
           "october_after": nt["2026-10"]},
          open(f"{BASE}/stocks_engine_sat31_result.json", "w"), indent=1)
print("\nwrote stocks_engine_sat31_result.json + upband trades csv")
