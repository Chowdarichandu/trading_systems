#!/usr/bin/env python3
"""ENGINE SE-1: verify September on the banked book (INV-LONG + N4-V3
+ P2F 2.5% + F4-minus-setup3 @ T150/S080, RF-1 book-wide) and diagnose
September's weak spots. Anchor: rebuilt union must == state table
(+131,646.79 / 934 tr / Sep +17,413.79 / Oct +50,029.72) exactly.
Paper, real Rs0, per 100 shares, Rs40/tr."""
import csv, sys, json, datetime
from collections import defaultdict
sys.path.insert(0, "/home/hatch/workspace/trading")
import importlib.util

BASE = "/home/hatch/workspace/trading"
def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m
M1 = load_mod("M1", f"{BASE}/stocks_M1.py")

def wk(d): return datetime.date.fromisoformat(d).weekday() >= 5
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))

STATE = {"2026-01": 12433.74, "2026-02": 4173.49, "2026-03": 20322.06,
         "2026-04": 50.73, "2026-05": 27844.38, "2026-06": -1233.49,
         "2026-07": 2096.63, "2026-08": -1484.26, "2026-09": 17413.79,
         "2026-10": 50029.72}

inv = [t for t in M1.load_inv_long() if not wk(t["date"])]
n4  = [t for t in M1.load_n4() if not wk(t["date"])]
p2f = [t for t in M1.load_p2f(2.5) if not wk(t["date"])]
f4  = [{"date": r["date"], "stock": r["symbol"], "comp": "F4",
        "dir": r["dir"], "setup": r["setup"], "leg": r["leg"],
        "net": float(r["net"]), "entry_time": r["entry_time"],
        "exit_reason": r["exit_reason"], "event_status": r["event"],
        "premove_pct": float(r["premove_pct"])}
       for r in rd("stocks_engine_oc4_f4s080_trades.csv")
       if not wk(r["date"]) and r["setup"] != "setup3_bounce_rejection"]
for t in inv + n4 + p2f:
    t.setdefault("setup", None); t.setdefault("leg", None)
    t.setdefault("premove_pct", None)
book = inv + n4 + p2f + f4

def mt(trades):
    m = defaultdict(float); c = defaultdict(int)
    for t in trades: m[t["date"][:7]] += t["net"]; c[t["date"][:7]] += 1
    return ({k: round(m[k], 2) for k in sorted(m)},
            {k: c[k] for k in sorted(c)})

bt, bc = mt(book)
tot = round(sum(t["net"] for t in book), 2)
anchor_ok = bt == STATE and tot == 131646.79 and len(book) == 934
print("ANCHOR: rebuilt union == state table:", anchor_ok,
      f"| trades {len(book)} | total {tot}")
if not anchor_ok:
    for k in sorted(STATE):
        if bt.get(k) != STATE[k]:
            print("  MISMATCH", k, "state", STATE[k], "rebuilt", bt.get(k))
    sys.exit("ANCHOR FAILED — stop, do not diagnose on an unverified book")

sep = [t for t in book if t["date"].startswith("2026-09")]
print(f"\nSEPTEMBER VERIFIED: {len(sep)} trades, net "
      f"{round(sum(t['net'] for t in sep), 2)}")

def split(trades, keyfn, label):
    g = defaultdict(lambda: [0, 0.0, 0.0, 0.0])  # n, net, gross_win, gross_loss
    for t in trades:
        k = keyfn(t); g[k][0] += 1; g[k][1] += t["net"]
        if t["net"] > 0: g[k][2] += t["net"]
        else: g[k][3] += t["net"]
    print(f"\n--- September by {label} ---")
    for k, v in sorted(g.items(), key=lambda kv: kv[1][1]):
        print(f"  {str(k):28} n={v[0]:3} net={v[1]:10.2f} "
              f"win={v[2]:10.2f} loss={v[3]:10.2f}")
    return g

split(sep, lambda t: t["comp"], "component")
split(sep, lambda t: t["stock"], "stock")
split(sep, lambda t: t["dir"], "direction")
split(sep, lambda t: t["exit_reason"], "exit_reason")
split([t for t in sep if t["comp"] == "F4"], lambda t: t["setup"], "F4 setup")
split([t for t in sep if t["comp"] == "INV-LONG"], lambda t: t["setup"], "INV setup")
split([t for t in sep if t["comp"] == "F4"], lambda t: t["leg"], "F4 leg")
split([t for t in sep if t["comp"] == "F4"],
      lambda t: "[0.5,0.75)" if t["premove_pct"] < 0.75 else "[0.75,1.0)",
      "F4 premove sub-band")
split([t for t in sep if t.get("event_status")],
      lambda t: t["event_status"], "event status (F4+INV)")

# September by day
byday = defaultdict(lambda: [0, 0.0])
for t in sep: byday[t["date"]][0] += 1; byday[t["date"]][1] += t["net"]
print("\n--- September days (worst first) ---")
neg_days = []
for d, v in sorted(byday.items(), key=lambda kv: kv[1][1]):
    flag = ""
    if v[1] < 0:
        neg_days.append(d); flag = " <-- NEGATIVE"
    print(f"  {d}  n={v[0]:3} net={v[1]:10.2f}{flag}")
print(f"September trading days with book trades: {len(byday)}, "
      f"negative days: {len(neg_days)}, negative-day sum: "
      f"{round(sum(byday[d][1] for d in neg_days), 2)}")
# component split of the negative days
for d in neg_days:
    parts = defaultdict(float)
    for t in sep:
        if t["date"] == d: parts[t["comp"]] += t["net"]
    print(f"  {d}: " + ", ".join(f"{k} {v:+.2f}" for k, v in
                                  sorted(parts.items(), key=lambda kv: kv[1])))

# STRUCTURAL DRAG TEST: slice negative in September AND negative full-period
print("\n--- STRUCTURAL DRAG TEST (Sep < 0 AND full-period < 0) ---")
def drag_test(trades_all, trades_sep, keyfn, label, min_sep_n=3):
    full = defaultdict(lambda: [0, 0.0]); sp = defaultdict(lambda: [0, 0.0])
    for t in trades_all:
        k = keyfn(t)
        if k is None: continue
        full[k][0] += 1; full[k][1] += t["net"]
    for t in trades_sep:
        k = keyfn(t)
        if k is None: continue
        sp[k][0] += 1; sp[k][1] += t["net"]
    hits = []
    for k, v in sp.items():
        if v[1] < 0 and v[0] >= min_sep_n and full[k][1] < 0:
            hits.append((k, v, full[k]))
    print(f"[{label}] " + ("; ".join(
        f"{k}: Sep n={v[0]} net={v[1]:.2f} | full n={f[0]} net={f[1]:.2f}"
        for k, v, f in hits) if hits else "no structural drag"))
    return hits

drags = []
drags += drag_test(book, sep, lambda t: t["comp"], "component")
drags += drag_test(book, sep, lambda t: t["stock"], "stock")
drags += drag_test(book, sep, lambda t: t["dir"], "direction")
drags += drag_test([t for t in book if t["comp"] == "F4"],
                   [t for t in sep if t["comp"] == "F4"],
                   lambda t: t["setup"], "F4 setup")
drags += drag_test([t for t in book if t["comp"] == "INV-LONG"],
                   [t for t in sep if t["comp"] == "INV-LONG"],
                   lambda t: t["setup"], "INV setup")
drags += drag_test([t for t in book if t["comp"] == "F4"],
                   [t for t in sep if t["comp"] == "F4"],
                   lambda t: t["leg"], "F4 leg")
drags += drag_test([t for t in book if t["comp"] == "F4"],
                   [t for t in sep if t["comp"] == "F4"],
                   lambda t: "[0.5,0.75)" if t["premove_pct"] < 0.75 else "[0.75,1.0)",
                   "F4 premove sub-band")
drags += drag_test([t for t in book if t.get("event_status")],
                   [t for t in sep if t.get("event_status")],
                   lambda t: t["event_status"], "event status")
drags += drag_test(book, sep, lambda t: t["exit_reason"], "exit_reason")

# biggest September losers
print("\n--- September's 12 biggest losing trades ---")
for t in sorted(sep, key=lambda x: x["net"])[:12]:
    print(f"  {t['date']} {t['stock']:12} {t['comp']:8} {t['dir']:5} "
          f"setup={t.get('setup')} entry={t['entry_time']} "
          f"exit={t['exit_reason']} net={t['net']:.2f}")
winners = sum(t["net"] for t in sep if t["net"] > 0)
losers = sum(t["net"] for t in sep if t["net"] <= 0)
print(f"\nSeptember gross wins {winners:.2f} / gross losses {losers:.2f} / "
      f"win rate {sum(1 for t in sep if t['net'] > 0)}/{len(sep)}")

json.dump({"anchor_ok": anchor_ok, "sep_trades": len(sep),
           "sep_net": round(sum(t["net"] for t in sep), 2),
           "negative_days": neg_days,
           "neg_day_sum": round(sum(byday[d][1] for d in neg_days), 2)},
          open(f"{BASE}/stocks_engine_se1_diag.json", "w"), indent=1)
print("\nwrote stocks_engine_se1_diag.json")
