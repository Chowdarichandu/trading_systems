#!/usr/bin/env python3
"""RECURSIVE ENGINE — CYCLE 1. Families RF-1/RF-2/RF-3 frozen in
stocks_engine_frozen.md BEFORE this ran. Full-book rebuilds from the
audited M1 loaders; day-level stand-asides applied to all components.
Paper only, real Rs0, provisional per 100 shares, Rs40/trade (in dumps).
"""
import json, sys
from datetime import date
from collections import defaultdict
sys.path.insert(0, "/home/hatch/workspace/trading")
import importlib.util
spec = importlib.util.spec_from_file_location("M1", "/home/hatch/workspace/trading/stocks_M1.py")
M1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M1)

BASE = "/home/hatch/workspace/trading"
MONTHS = M1.MONTHS

book = M1.load_book()
base_t = M1.month_table(book)
n_tot, tot = M1.fmt_table(base_t, "BASE BOOK (anchor: 344 / +47665.24, Feb -5533.46)")
assert (n_tot, tot) == (344, 47665.24), "ANCHOR FAIL"
assert base_t["2026-02"] == (57, -5533.46), "FEB ANCHOR FAIL"
print("ANCHOR OK: base book reproduces +47665.24 and the M1 month table exactly.")

# ---- timing audit re-asserted (same checks as M1 anchor mode) ----
n4, p2f, inv = M1.load_n4(), M1.load_p2f(), M1.load_inv_long()
assert all(x["entry_time"] == "09:35" for x in n4)
assert all(x["entry_time"] == "09:15" for x in p2f)
reg = M1.nifty_regime()
inv_dates = sorted({x["date"] for x in inv})
assert all(d in reg and reg[d][0] <= reg[d][1] for d in inv_dates)
print(f"TIMING AUDIT CLEAN: N4 09:35 x{len(n4)}, P2F 09:15 x{len(p2f)}, "
      f"INV-LONG below50 recomputed on {len(inv_dates)} dates — 0 violations.")

# ---- trading calendar from NIFTY daily series ----
cal = M1.daily_series("NIFTY")  # [(date, close)] sorted
cal_dates = [d for d, _ in cal]
closes = dict(cal)
win = [d for d in cal_dates if "2026-01-01" <= d <= "2026-10-31"]

# RF-1: weekend dates present in the calendar (non-standard sessions)
def weekday(d):
    y, m, dd = map(int, d.split("-"))
    return date(y, m, dd).weekday()  # Mon=0 .. Sun=6
special = sorted(d for d in win if weekday(d) >= 5)
print("\nRF-1 special-session (Sat/Sun) dates in Jan-Oct 2026 calendar:", special)
for d in special:
    i = cal_dates.index(d)
    mv = (closes[d] / closes[cal_dates[i - 1]] - 1) * 100 if i > 0 else 0.0
    print(f"   {d} weekday={weekday(d)} (5=Sat,6=Sun) Nifty close {closes[d]} day-move {mv:+.2f}%")

# RF-2: days whose PRIOR trading day had |Nifty close-to-close| >= 2%
postshock = []
for i in range(2, len(cal_dates)):
    d = cal_dates[i]
    if not ("2026-01-01" <= d <= "2026-10-31"):
        continue
    prev, prev2 = cal_dates[i - 1], cal_dates[i - 2]
    mv = abs(closes[prev] / closes[prev2] - 1) * 100
    if mv >= 2.0:
        postshock.append(d)
postshock = sorted(postshock)
print(f"\nRF-2 post-shock dates (|prior-day Nifty move| >= 2%): {len(postshock)}")
for d in postshock:
    i = cal_dates.index(d)
    prev, prev2 = cal_dates[i - 1], cal_dates[i - 2]
    mv = (closes[prev] / closes[prev2] - 1) * 100
    print(f"   {d} (prior day {prev} moved {mv:+.2f}%)")

def judge(filtered, label, excluded):
    t = M1.month_table(filtered)
    feb_n, feb_v = t["2026-02"]
    flips = [m for m in MONTHS if m != "2026-02" and base_t[m][1] > 0 and t[m][1] <= 0]
    legs = {"feb_positive": feb_v > 0,
            "no_green_flips": not flips,
            "feb_activity_ok": feb_n >= 0.6 * 57,
            "audit_clean": True}
    accept = all(legs.values())
    print(f"\n===== {label} =====")
    print(f"excluded dates ({len(excluded)}): {excluded}")
    del_by_month = defaultdict(lambda: [0, 0.0])
    kept = {(x['date'], x['stock'], x['comp'], x['net']) for x in filtered}
    for x in book:
        if x["date"] in excluded:
            del_by_month[x["date"][:7]][0] += 1
            del_by_month[x["date"][:7]][1] += x["net"]
    for m in MONTHS:
        dn, dv = del_by_month.get(m, [0, 0.0])
        print(f"  {m}: base {base_t[m][0]:3d} tr {base_t[m][1]:10.2f} -> "
              f"new {t[m][0]:3d} tr {t[m][1]:10.2f}  (delta {t[m][1]-base_t[m][1]:+.2f}; "
              f"deleted {dn} tr net {dv:+.2f})")
    tn = sum(v[0] for v in t.values()); tv = round(sum(v[1] for v in t.values()), 2)
    print(f"  TOTAL: {tn} trades, {tv} (base 344 / 47665.24, delta {tv-47665.24:+.2f})")
    print(f"  Feb: {feb_n} trades (base 57, floor 34.2) net {feb_v:+.2f}")
    print(f"  green flips: {flips} | legs: {legs} | ACCEPT: {accept}")
    return {"label": label, "excluded": excluded, "table": t, "total": tv,
            "trades": tn, "legs": legs, "accept": accept, "flips": flips,
            "deleted_by_month": {m: del_by_month.get(m, [0, 0.0]) for m in MONTHS}}

results = {}
results["RF-1"] = judge([x for x in book if x["date"] not in set(special)],
                        "RF-1 special-session stand-aside", special)
results["RF-2"] = judge([x for x in book if x["date"] not in set(postshock)],
                        "RF-2 post-shock stand-aside", postshock)
both = sorted(set(special) | set(postshock))
results["RF-3"] = judge([x for x in book if x["date"] not in set(both)],
                        "RF-3 RF-1 + RF-2", both)

# February detail for the record
for d in ("2026-02-01", "2026-02-02"):
    rows = [x for x in book if x["date"] == d]
    print(f"Feb detail {d}: {len(rows)} book trades net {round(sum(x['net'] for x in rows),2)} "
          f"(in RF-1 set: {d in special}, in RF-2 set: {d in postshock})")

json.dump({k: {"excluded": v["excluded"], "table": v["table"], "total": v["total"],
               "trades": v["trades"], "legs": v["legs"], "accept": v["accept"],
               "flips": v["flips"]} for k, v in results.items()},
          open(f"{BASE}/stocks_engine_cycle1_results.json", "w"), indent=1)
print("\nWROTE stocks_engine_cycle1_results.json")
print("ACCEPTED:", [k for k, v in results.items() if v["accept"]])
