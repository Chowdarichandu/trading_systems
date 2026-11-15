#!/usr/bin/env python3
"""FLOOR SESSION (2026-11-02 directive) — BASELINE + VALIDATION.

Independent re-sum of the two candidate books (frozen v2 C24; v3 C16),
full scorecards per year, REGIME-CLASSIFIER-1 label replication validated
against the state's published C16/C24 cell totals, and N4-V3 move-by-09:30
recomputation validated against the fix-test's recorded 2026 moves.
Read-only: no book is modified. Basis: equity cash, home 25, provisional
per 100 shares, Rs40/trade, paper only, real Rs0.
"""
import csv, json
from collections import defaultdict

WS = "/home/hatch/workspace/trading"
FH = f"{WS}/data/full_hist"

def load(fn):
    rows = [{**t, "net": float(t["net"])} for t in csv.DictReader(open(f"{WS}/{fn}"))]
    return rows

state = json.load(open(f"{WS}/stocks_engine_state.json"))
books = {
    "v2_c24": (load("stocks_engine_v2_c24_book2025_trades.csv"),
               load("stocks_engine_v2_c24_book2026_trades.csv")),
    "v3_c16": (load("stocks_engine_v3_c16_book2025_trades.csv"),
               load("stocks_engine_v3_c16_book2026_trades.csv")),
}
# --- independent re-sum vs state records ---------------------------------
assert (len(books["v2_c24"][0]), round(sum(t["net"] for t in books["v2_c24"][0]), 2)) == \
       (state["v2"]["best_trades"]["2025"], state["v2"]["best_by_year"]["2025"]), "C24 2025 mismatch"
assert (len(books["v2_c24"][1]), round(sum(t["net"] for t in books["v2_c24"][1]), 2)) == \
       (state["v2"]["best_trades"]["2026"], state["v2"]["best_by_year"]["2026"]), "C24 2026 mismatch"
assert (len(books["v3_c16"][0]), round(sum(t["net"] for t in books["v3_c16"][0]), 2)) == \
       (state["v3"]["best_trades"]["2025"], state["v3"]["best_by_year"]["2025"]), "C16 2025 mismatch"
assert (len(books["v3_c16"][1]), round(sum(t["net"] for t in books["v3_c16"][1]), 2)) == \
       (state["v3"]["best_trades"]["2026"], state["v3"]["best_by_year"]["2026"]), "C16 2026 mismatch"
print("RE-SUM: all four dumps reproduce the state totals to the paisa.")

def scorecard(rows, year):
    tot = round(sum(t["net"] for t in rows), 2)
    months = defaultdict(float)
    for t in rows: months[t["date"][:7]] += t["net"]
    months = {k: round(v, 2) for k, v in sorted(months.items())}
    jo = [t for t in rows if t["date"] <= f"{year}-10-31"]
    jo_tot = round(sum(t["net"] for t in jo), 2)
    h1 = round(sum(t["net"] for t in jo if t["date"] <= f"{year}-05-31"), 2)
    h2 = round(jo_tot - h1, 2)
    by_stock = defaultdict(float)
    for t in rows: by_stock[t["stock"]] += t["net"]
    top3 = sorted(by_stock.items(), key=lambda kv: -kv[1])[:3]
    ex_top3 = round(tot - sum(v for _, v in top3), 2)
    by_comp = defaultdict(float)
    for t in rows: by_comp[t["comp"]] += t["net"]
    wins = sum(1 for t in rows if t["net"] > 0)
    return {"year": year, "total": tot, "trades": len(rows),
            "jan_oct_total": jo_tot, "jan_oct_trades": len(jo),
            "jan_oct_H1_jan_may": h1, "jan_oct_H2_jun_oct": h2,
            "months": months, "ex_top3_stocks": ex_top3,
            "top3_stocks": [(s, round(v, 2)) for s, v in top3],
            "by_comp": {k: round(v, 2) for k, v in sorted(by_comp.items())},
            "wins": wins}

cards = {}
for name, (b25, b26) in books.items():
    cards[name] = {"2025": scorecard(b25, 2025), "2026": scorecard(b26, 2026)}
    c = cards[name]
    print(f"{name}: 2025 {c['2025']['total']:+.2f} ({c['2025']['trades']} tr, Jan-Oct {c['2025']['jan_oct_total']:+.2f}) | "
          f"2026 {c['2026']['total']:+.2f} ({c['2026']['trades']} tr, Jan-Oct {c['2026']['jan_oct_total']:+.2f})")

# --- REGIME-CLASSIFIER-1 replication --------------------------------------
daily = []
with open(f"{FH}/NIFTY/spot_daily.csv") as f:
    for r in csv.DictReader(f):
        daily.append({"date": r["date"][:10], "close": float(r["close"])})
daily.sort(key=lambda x: x["date"])
# The audited machinery extends NIFTY to 2026-10-30 (raw daily ends 10-28);
# the extension closes live in the forward logger's cache — take them there.
have = {d["date"] for d in daily}
with open(f"{WS}/data/sarvaritu_fwd/NIFTY/spot_daily.csv") as f:
    for r in csv.DictReader(f):
        d = r["date"][:10]
        if d not in have:
            daily.append({"date": d, "close": float(r["close"])})
daily.sort(key=lambda x: x["date"])
closes = [d["close"] for d in daily]
idx = {d["date"]: i for i, d in enumerate(daily)}
def ma50_asof(i):  # mean of the 50 closes strictly before day i
    if i < 50: return None
    return sum(closes[i - 50:i]) / 50
labels = {}
for i, d in enumerate(daily):
    m = ma50_asof(i)
    if m is None or i < 55: continue
    m5 = ma50_asof(i - 5)
    if m5 is None: continue
    pc, slope = closes[i - 1], m - m5
    labels[d["date"]] = "UP" if (pc > m and slope >= 0) else ("DOWN" if (pc <= m and slope <= 0) else "FLAT")

def cells(rows):
    out = defaultdict(float); missing = 0
    for t in rows:
        lab = labels.get(t["date"])
        if lab is None: missing += 1; continue
        out[lab] += t["net"]
    return {k: round(v, 2) for k, v in sorted(out.items())}, missing

for name, pub in (("v3_c16", state["v3"]["cells"]), ("v2_c24", None)):
    b25, b26 = books[name]
    c25, m25 = cells(b25); c26, m26 = cells(b26)
    print(f"{name} cells (replicated): 2025 {c25} (unlabelled {m25}) | 2026 {c26} (unlabelled {m26})")
    if pub:
        print(f"{name} cells (state-published): 2025 {pub['2025']} | 2026 {pub['2026']}")
        ok = all(abs(c25[k] - pub["2025"][k]) < 0.011 for k in pub["2025"]) and \
             all(abs(c26[k] - pub["2026"][k]) < 0.011 for k in pub["2026"])
        print("REGIME LABELS VALIDATED vs state cells:", ok)
        cards[name]["cells_replicated"] = {"2025": c25, "2026": c26}
        cards[name]["cells_validated"] = ok

# --- N4-V3 move-by-09:30 recomputation ------------------------------------
# move = close of the 09:25 5-min bar on the trade (reaction) day / prior
# trading day's daily close - 1, in percent (stocks_equity_n4deep.py).
_spot_cache, _daily_cache = {}, {}
def stock_data(sym):
    if sym not in _spot_cache:
        spot = {}
        with open(f"{FH}/{sym}/spot_5m.csv") as f:
            for r in csv.DictReader(f):
                spot.setdefault(r["timestamp"][:10], {})[r["timestamp"][11:16]] = float(r["close"])
        dl = []
        with open(f"{FH}/{sym}/spot_daily.csv") as f:
            for r in csv.DictReader(f):
                dl.append((r["date"][:10], float(r["close"])))
        dl.sort()
        _spot_cache[sym] = spot; _daily_cache[sym] = dl
    return _spot_cache[sym], _daily_cache[sym]

def n4_move(sym, day):
    spot, dl = stock_data(sym)
    dates = [d for d, _ in dl]
    if day not in spot or day not in dates: return None
    i = dates.index(day)
    if i == 0: return None
    prev_close = dl[i - 1][1]
    b = spot[day].get("09:25")
    if b is None: return None
    return round((b / prev_close - 1) * 100, 2)

rec = {(r["date"], r["stock"], r["dir"]): r for r in
       json.load(open(f"{WS}/fix_tests_2026-11-02_cache/n4_rows.json"))}
mism, checked = [], 0
for (d, s, dr), r in rec.items():
    mv = n4_move(s, d)
    if mv is None: mism.append((d, s, "NO DATA")); continue
    checked += 1
    if abs(mv - r["move"]) > 0.05: mism.append((d, s, f"rec {r['move']} vs comp {mv}"))
print(f"N4 MOVE RECOMPUTE vs recorded 2026 standalone: {checked}/{len(rec)} checked, "
      f"{len(mism)} mismatches {mism[:6]}")

# join check: C16 book 2026 N4 rows vs recorded book-basis nets
b26 = books["v3_c16"][1]
n4_26 = [t for t in b26 if t["comp"] == "N4-V3"]
join_ok, join_bad = 0, []
for t in n4_26:
    r = rec.get((t["date"], t["stock"], t["dir"]))
    if r is None: join_bad.append((t["date"], t["stock"], "not in standalone"))
    elif abs(r["bk"] - t["net"]) > 0.011: join_bad.append((t["date"], t["stock"], f"book {t['net']} vs bk {r['bk']}"))
    else: join_ok += 1
print(f"C16 2026 N4 join: {len(n4_26)} book rows, {join_ok} exact net matches, exceptions: {join_bad[:8]}")

out = {"books": cards}
json.dump(out, open(f"{WS}/stocks_engine_floor_baseline.json", "w"), indent=1)
print("WROTE stocks_engine_floor_baseline.json")
