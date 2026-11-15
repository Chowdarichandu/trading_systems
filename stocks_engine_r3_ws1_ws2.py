#!/usr/bin/env python3
"""ROUND 3 — baseline verification, WS1 wound decomposition + gated basket,
WS2 event-layer audit. Run order fixed; the basket rule is frozen in code
BEFORE the gate runs (members: wound-month net < 0 AND whole-book net in
(-500, 0] — the individually sub-bar rows)."""
import sys, pickle, csv
from collections import defaultdict
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r3_lib as R3
import stocks_engine_floor_lib as FL

books = R3.load_books()
# ---------------- baseline verification (independent re-sum) -------------
for yr, exp in ((2025, (54957.57, 56336.30, 776)), (2026, (221801.13, 221801.13, 680))):
    tot = round(sum(t["net"] for t in books[yr]), 2)
    jo = round(sum(t["net"] for t in books[yr] if t["date"] <= f"{yr}-10-31"), 2)
    assert (tot, jo, len(books[yr])) == exp, (yr, tot, jo, len(books[yr]), exp)
    print(f"BASELINE {yr}: total {tot}  Jan-Oct {jo}  trades {len(books[yr])}  OK")
print("2025 gap to floor:", round(150000 - 56336.30, 2))

# ---------------- WS1: wound decomposition -------------------------------
WOUND = ("2025-06", "2025-07", "2025-10")
w25 = [t for t in books[2025] if t["date"][:7] in WOUND]
print(f"\nWS1 wound trades (2025 Jun+Jul+Oct): {len(w25)}  net "
      f"{round(sum(t['net'] for t in w25), 2)}")
by_comp = defaultdict(lambda: [0, 0.0])
for t in w25:
    by_comp[t["comp"]][0] += 1
    by_comp[t["comp"]][1] += t["net"]
print(" by component:", {c: (n, round(v, 2)) for c, (n, v)
                         in sorted(by_comp.items())})
by_cell = defaultdict(lambda: [0, 0.0])
for t in w25:
    by_cell[FL.LABELS.get(t["date"], "?")][0] += 1
    by_cell[FL.LABELS.get(t["date"], "?")][1] += t["net"]
print(" by regime cell:", {c: (n, round(v, 2)) for c, (n, v)
                           in sorted(by_cell.items())})

def row_stats(books):
    """(comp, stock, dir) -> whole-book net, wound net, count."""
    whole, wound, cnt = defaultdict(float), defaultdict(float), defaultdict(int)
    for yr in (2025, 2026):
        for t in books[yr]:
            k = (t["comp"], t["stock"], t["dir"])
            whole[k] += t["net"]
            cnt[k] += 1
            if t["date"][:7] in WOUND:
                wound[k] += t["net"]
    return whole, wound, cnt

whole, wound, cnt = row_stats(books)
neg_rows = sorted(((k, round(wound[k], 2), round(whole[k], 2), cnt[k])
                   for k in whole if wound[k] < 0),
                  key=lambda x: x[1])
print(f"\n (comp x stock x dir) rows with negative wound net: {len(neg_rows)}")
for k, w, wh, n in neg_rows:
    print(f"   {k}: wound {w}  whole-book {wh}  trades {n}")

def basket(books, wound_months):
    whole, wound, cnt = defaultdict(float), defaultdict(float), defaultdict(int)
    for yr in (2025, 2026):
        for t in books[yr]:
            k = (t["comp"], t["stock"], t["dir"])
            whole[k] += t["net"]
            cnt[k] += 1
            if t["date"][:7] in wound_months:
                wound[k] += t["net"]
    members = {k for k in whole
               if wound[k] < 0 and -500.0 < whole[k] <= 0.0}
    out, n = {}, 0
    for yr in (2025, 2026):
        out[yr] = [t for t in books[yr]
                   if (t["comp"], t["stock"], t["dir"]) not in members]
        n += len(books[yr]) - len(out[yr])
    return out, members, n

var_books, members, n_removed = basket(books, WOUND)
print(f"\nBASKET members ({len(members)} rows, {n_removed} trades removed book-wide):")
for k in sorted(members):
    print(f"   {k}: wound {round(wound[k],2)}  whole {round(whole[k],2)}  n {cnt[k]}")

# placebos (pre-registered): mirror-wound basket (green months Feb+Mar+Aug
# 2025, identical rule) + chrono first-N removal.
mirror_books, mirror_members, mirror_n = basket(books, ("2025-02", "2025-03", "2025-08"))
mirror_total = round(sum(R3.FL_scorecard(mirror_books[yr])["jan_oct_total"]
                         for yr in (2025, 2026)), 2) if hasattr(R3, "FL_scorecard") else \
    round(sum(FL.scorecard(mirror_books[yr], yr)["jan_oct_total"]
              for yr in (2025, 2026)), 2)
chrono_total = R3.chrono_placebo_total(books, n_removed)
print(f"placebos: mirror-wound basket combined JO {mirror_total} "
      f"({len(mirror_members)} rows, {mirror_n} trades); "
      f"chrono first-{n_removed} combined JO {chrono_total}")

out = R3.gate(books, var_books, [mirror_total, chrono_total])
R3.record("R3-01", "WS1 wound basket: delete (comp x stock x dir) rows with "
                   "2025 Jun/Jul/Oct net < 0 AND whole-book net in (-500, 0]",
          out, note=f"members {sorted(members)}; removed {n_removed} trades; "
                    f"placebos: mirror-wound basket {mirror_total}, "
                    f"chrono first-N {chrono_total}")
if out["verdict"]:
    books = var_books
    R3.save_books(books)
    print("    -> BANKED")

# ---------------- WS2: event-layer audit ---------------------------------
print("\nWS2 AUDIT — calendar coverage")
for yr, fn in ((2025, "stock_event_calendar_2025.csv"),
               (2026, "stock_event_calendar_jan_oct_2026.csv")):
    rows = list(csv.DictReader(open(f"{WS}/{fn}")))
    res = [r for r in rows if r["event_type"] == "results"]
    news = [r for r in rows if r["event_type"] != "results"]
    from datetime import date, timedelta
    bad_react = 0
    for r in res:
        ev = date.fromisoformat(r["event_date"][:10])
        ok = False
        if r["reaction_date"]:
            rd = date.fromisoformat(r["reaction_date"][:10])
            ok = ev <= rd <= ev + timedelta(days=7)
        if not ok:
            bad_react += 1
    print(f" {yr}: rows {len(rows)} (results {len(res)}, news {len(news)}); "
          f"results rows with reaction_date missing/outside +7d window: {bad_react}; "
          f"results per stock min/max: "
          f"{min(sum(1 for r in res if r['stock']==s) for s in {r['stock'] for r in res})}/"
          f"{max(sum(1 for r in res if r['stock']==s) for s in {r['stock'] for r in res})}")

cache = pickle.load(open(f"{WS}/r2_cache.pkl", "rb"))
EV = cache["events"]
for yr in (2025, 2026):
    cands = EV[yr]["cands"]
    bands = {"<2.0": 0, "[2.0,2.5)": 0, "[2.5,3.0)": 0, ">=3.0": 0}
    for c in cands:
        a = abs(c["reaction_ret_pct"])
        bands["<2.0" if a < 2 else "[2.0,2.5)" if a < 2.5
              else "[2.5,3.0)" if a < 3 else ">=3.0"] += 1
    s1 = len(EV[yr]["scored"][(1, False)])
    s2 = len(EV[yr]["scored"][(2, False)])
    n4 = cache["n4_signals"][yr]
    print(f" {yr}: reaction candidates {len(cands)}; band histogram {bands}; "
          f"scored lag1 {s1}, lag2 {s2}; N4 signal-days (|move|>=0.5 superset) "
          f"{len(n4)}, >=0.8: {sum(1 for s in n4 if abs(s['move_pct']) >= 0.8)}")
fam25 = {c: (len([t for t in books[2025] if t['comp'] == c]),
             round(sum(t['net'] for t in books[2025] if t['comp'] == c), 2))
         for c in ("P2F", "P2F-R2", "R2-LOWBAND", "N4-V3")}
fam26 = {c: (len([t for t in books[2026] if t['comp'] == c]),
             round(sum(t['net'] for t in books[2026] if t['comp'] == c), 2))
         for c in ("P2F", "P2F-R2", "R2-LOWBAND", "N4-V3")}
print(" in-book family (full-year rows in current book):")
print("  2025:", fam25)
print("  2026:", fam26)
print("done ws1/ws2")
