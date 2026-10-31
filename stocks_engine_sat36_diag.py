#!/usr/bin/env python3
"""ENGINE SAT-36 DIAGNOSIS: F4 x GLENMARK x SHORT -- the one standing
item never judged on its merits, forced now as the formal argument.
Anchors: (A) incumbent union (SIX components) == state (663 tr /
+197,607.74 / month table / ex-top-3 72,518.25), per book law (N4 =
SAT-15 dump minus SAT-17/SAT-24; F4 = SAT-10 dump minus all F4
exclusions through SAT-30; INV-LONG minus BDL+VEDL+HINDZINC+
INDUSTOWER+KALYANKJIL; P2F-R2 minus SAT-21; R2-LOWBAND from the
SAT-33 dump). The slice is re-derived from the book's own F4
component (Lesson 16: recorded facts are stale until re-derived).
Reports: trades, winners, net, expectancy, month profile, halves,
August/October slices, ex-carrier (net excluding the single worst
trade -- for a deletion, the trade that carries the case), net
excluding August (the 'August story' decomposition), the F4
GLENMARK LONG half, GLENMARK's whole-book total and top-3 share.
Deletion-only on audited dumps; timing inherited.
Paper, real Rs0, per 100 shares, Rs40/trade, home 25."""
import csv, sys, json
from collections import defaultdict
sys.path.insert(0, "/home/hatch/workspace/trading")
import importlib.util
from datetime import date

BASE = "/home/hatch/workspace/trading"
def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m
M1 = load_mod("M1", f"{BASE}/stocks_M1.py")

def wk(d): return date.fromisoformat(d).weekday() >= 5
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))

STATE = {"2026-01": 28536.25, "2026-02": 18419.86, "2026-03": 20584.41,
         "2026-04": 9895.49, "2026-05": 34880.86, "2026-06": 3823.22,
         "2026-07": 6965.93, "2026-08": 666.78, "2026-09": 19562.51,
         "2026-10": 54272.43}
STATE_TOTAL, STATE_TRADES, STATE_EXTOP3 = 197607.74, 663, 72518.25
EXCL_DIR = {("GODREJCP", "SHORT"), ("INDUSTOWER", "LONG"),
            ("HINDUNILVR", "SHORT"), ("UNITDSPR", "SHORT"),
            ("HINDCOPPER", "SHORT"), ("OIL", "SHORT"),
            ("IRCTC", "SHORT"), ("HINDALCO", "LONG"),
            ("TATASTEEL", "LONG"), ("NHPC", "SHORT"),
            ("PFC", "SHORT"), ("RECLTD", "SHORT")}

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
               "dir": r["dir"], "net": float(r["net"]),
               "setup": r["setup"]})
r2 = [{"date": r["date"], "stock": r["symbol"], "comp": "P2F-R2",
       "dir": r["direction"], "net": float(r["net_rs"])}
      for r in rd("stocks_engine_sat13_p2fr2_trades.csv")
      if not (r["symbol"] == "TVSMOTOR" and r["direction"] == "LONG")]
r2low = [{"date": r["date"], "stock": r["symbol"], "comp": "R2-LOWBAND",
          "dir": r["direction"], "net": float(r["net_rs"])}
         for r in rd("stocks_engine_sat33_r2lowband_trades.csv")]
book = inv + n4 + p2f + f4 + r2 + r2low

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
            [(k, round(v, 2)) for k, v in top3],
            {k: round(v, 2) for k, v in per.items()})

bt, _ = mt(book)
ex0, top3_0, per_stock = extop3(book)
a_ok = (bt == STATE and round(sum(t["net"] for t in book), 2) == STATE_TOTAL
        and len(book) == STATE_TRADES and ex0 == STATE_EXTOP3)
print(f"ANCHOR A: incumbent == state: {a_ok} | {len(book)} tr / "
      f"{round(sum(t['net'] for t in book),2)} / ex-top-3 {ex0}")
print(f"  components: INV {len(inv)} / N4 {len(n4)} / P2F {len(p2f)} / "
      f"F4 {len(f4)} / R2 {len(r2)} / R2LOW {len(r2low)}")
assert a_ok, "ANCHOR A FAILED -- do not judge"

# ---------- the slice under formal judgement ----------
slice_tr = sorted([t for t in f4
                   if t["stock"] == "GLENMARK" and t["dir"] == "SHORT"],
                  key=lambda x: x["date"])
s_net = round(sum(t["net"] for t in slice_tr), 2)
s_win = sum(1 for t in slice_tr if t["net"] > 0)
s_months = {}
for t in slice_tr:
    s_months[t["date"][:7]] = round(s_months.get(t["date"][:7], 0.0)
                                    + t["net"], 2)
s_h1 = round(sum(t["net"] for t in slice_tr if t["date"] <= "2026-05-31"), 2)
s_h2 = round(sum(t["net"] for t in slice_tr if t["date"] > "2026-05-31"), 2)
worst = min(slice_tr, key=lambda t: t["net"])
best = max(slice_tr, key=lambda t: t["net"])
ex_carrier = round(s_net - worst["net"], 2)
aug_slice = s_months.get("2026-08", 0.0)
oct_slice = s_months.get("2026-10", 0.0)
ex_august = round(s_net - aug_slice, 2)
non_aug_months_neg = sum(1 for k, v in s_months.items()
                         if k != "2026-08" and v < 0)
neg_months = sum(1 for v in s_months.values() if v < 0)
f4_gl_long = [t for t in f4 if t["stock"] == "GLENMARK" and t["dir"] == "LONG"]
gl_f4 = round(sum(t["net"] for t in f4 if t["stock"] == "GLENMARK"), 2)
gl_book = per_stock.get("GLENMARK", 0.0)

print(f"\nF4 x GLENMARK x SHORT (re-derived at the current book):")
print(f"  trades {len(slice_tr)} | winners {s_win} | net {s_net} | "
      f"expectancy {round(s_net/len(slice_tr),2) if slice_tr else 0}")
print(f"  halves: H1 {s_h1} / H2 {s_h2}")
print(f"  months: {dict(sorted(s_months.items()))}")
print(f"  negative months: {neg_months} of {len(s_months)} traded "
      f"(ex-August: {non_aug_months_neg})")
print(f"  August slice {aug_slice} | October slice {oct_slice}")
print(f"  worst trade {worst['date']} {worst['net']:+.2f} "
      f"({worst['setup']}) | ex-carrier (net ex-worst) {ex_carrier}")
print(f"  best trade {best['date']} {best['net']:+.2f} ({best['setup']})")
print(f"  net excluding August {ex_august}  <-- the 'August story' test")
print(f"  F4 GLENMARK LONG half: {len(f4_gl_long)} tr / "
      f"{round(sum(t['net'] for t in f4_gl_long),2)} (kept either way)")
print(f"  GLENMARK inside F4 total: {gl_f4}; whole-book GLENMARK: "
      f"{gl_book}; top-3 {top3_0}; GLENMARK share of book total: "
      f"{round(100*gl_book/STATE_TOTAL,2)}%")
print(f"\nQUALITY BAR (Lesson 5 rot-everywhere registry standard): "
      f"full-period <= -500 -> {s_net <= -500} (slice net {s_net})")

json.dump({"anchorA": a_ok,
           "slice": {"comp": "F4", "stock": "GLENMARK", "dir": "SHORT",
                     "trades": len(slice_tr), "win": s_win, "net": s_net,
                     "exp": round(s_net/len(slice_tr), 2) if slice_tr else 0,
                     "h1": s_h1, "h2": s_h2, "months": s_months,
                     "negative_months": neg_months,
                     "months_traded": len(s_months),
                     "neg_months_ex_august": non_aug_months_neg,
                     "aug_slice": aug_slice, "oct_slice": oct_slice,
                     "worst_trade": {"date": worst["date"],
                                     "net": worst["net"],
                                     "setup": worst["setup"]},
                     "best_trade": {"date": best["date"],
                                    "net": best["net"],
                                    "setup": best["setup"]},
                     "ex_carrier": ex_carrier,
                     "net_ex_august": ex_august,
                     "deleted_set": sorted((t["date"], t["stock"],
                                             t["dir"], t["net"])
                                            for t in slice_tr)},
           "context": {"f4_glenmark_long_trades": len(f4_gl_long),
                       "f4_glenmark_long_net":
                           round(sum(t["net"] for t in f4_gl_long), 2),
                       "f4_glenmark_total": gl_f4,
                       "book_glenmark_total": gl_book,
                       "glenmark_share_pct":
                           round(100*gl_book/STATE_TOTAL, 2),
                       "top3": top3_0, "ex_top3": ex0},
           "quality_bar": {"standard": "full-period <= -500",
                           "slice_net": s_net,
                           "passes": s_net <= -500}},
          open(f"{BASE}/stocks_engine_sat36_diag.json", "w"), indent=1)
print("\nwrote stocks_engine_sat36_diag.json")
