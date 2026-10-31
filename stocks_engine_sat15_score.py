#!/usr/bin/env python3
"""ENGINE SAT-15 SCORE: RE-MEASURE + RE-APPLY the CH-2 N4-V3 exit
rebuild (T125/S050 -> T150/S080) at the current five-component book.
Frozen in stocks_engine_frozen.md (SAT-15 section) BEFORE this ran.
Lesson 16: CH-2's deltas are stale -- everything is re-measured here.
Anchors: (A) current book == state (812 tr / +166,748.50 / month
table / ex-top-3 52,426.36); (B) N4 replay at T125/S050 reproduces
the source dump 56/56 AND the book's N4 component per-trade after
identical filtering; (C) timing/entry audit on the T150/S080 build
(entries identical, exit_time >= entry_time, 0 violations).
Saturation gate: (a) total rises; (b) all ten months > 0;
(c) October >= 50,000; (d) ex-top-3 not worse; (e) anchors.
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

QTY, COST = 100, 40.0
def wk(d): return date.fromisoformat(d).weekday() >= 5
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))

STATE = {"2026-01": 18656.70, "2026-02": 12689.65, "2026-03": 18739.16,
         "2026-04": 7602.73, "2026-05": 32207.10, "2026-06": 2036.67,
         "2026-07": 2022.79, "2026-08": 4143.93, "2026-09": 17542.75,
         "2026-10": 51107.02}
STATE_TOTAL, STATE_TRADES, STATE_EXTOP3 = 166748.50, 812, 52426.36

# ---------- current book (sat14 construction + SAT-14 banked fix) ----------
inv = [{"date": t["date"], "stock": t["stock"], "comp": "INV-LONG",
        "dir": t["dir"], "net": t["net"]}
       for t in M1.load_inv_long()
       if not wk(t["date"]) and t["stock"] != "BDL"]
n4_book = [{"date": t["date"], "stock": t["stock"], "comp": "N4-V3",
            "dir": t["dir"], "net": t["net"]}
           for t in M1.load_n4()
           if not wk(t["date"]) and t["stock"] != "ASTRAL"]
p2f = [{"date": t["date"], "stock": t["stock"], "comp": "P2F",
        "dir": t["dir"], "net": t["net"]}
       for t in M1.load_p2f(2.5)
       if not wk(t["date"]) and t["stock"] != "ASTRAL"
       and t["stock"] != "HINDUNILVR"
       and not (t["stock"] == "HINDALCO" and t["dir"] == "LONG")]
EXCL = {("GODREJCP", "SHORT"), ("INDUSTOWER", "LONG"),
        ("HINDUNILVR", "SHORT"), ("UNITDSPR", "SHORT"),
        ("HINDCOPPER", "SHORT")}
f4 = []
for r in rd("stocks_engine_sat10_f4s095_trades.csv"):
    if wk(r["date"]) or r["setup"] == "setup3_bounce_rejection" \
            or r["leg"] == "round2" or (r["symbol"], r["dir"]) in EXCL:
        continue
    f4.append({"date": r["date"], "stock": r["symbol"], "comp": "F4",
               "dir": r["dir"], "net": float(r["net"])})
r2 = [{"date": r["date"], "stock": r["symbol"], "comp": "P2F-R2",
       "dir": r["direction"], "net": float(r["net_rs"])}
      for r in rd("stocks_engine_sat13_p2fr2_trades.csv")]
book = inv + n4_book + p2f + f4 + r2
comp_counts = {c: sum(1 for t in book if t["comp"] == c)
               for c in ("INV-LONG", "N4-V3", "P2F", "F4", "P2F-R2")}
print("component counts:", comp_counts)

def mt(trades):
    m = defaultdict(float); c = defaultdict(int)
    for t in trades: m[t["date"][:7]] += t["net"]; c[t["date"][:7]] += 1
    return {k: round(m[k], 2) for k in sorted(m)}, {k: c[k] for k in sorted(c)}

def extop3(trades):
    per = defaultdict(float)
    for t in trades: per[t["stock"]] += t["net"]
    top3 = sorted(per.items(), key=lambda kv: -kv[1])[:3]
    return (round(sum(t["net"] for t in trades
                      if t["stock"] not in {k for k, _ in top3}), 2),
            [k for k, _ in top3])

bt, _ = mt(book)
ex0, top3_0 = extop3(book)
a_ok = (bt == STATE and round(sum(t["net"] for t in book), 2) == STATE_TOTAL
        and len(book) == STATE_TRADES and ex0 == STATE_EXTOP3)
print(f"ANCHOR A: current book == state: {a_ok} | {len(book)} tr / "
      f"{round(sum(t['net'] for t in book),2)} / ex-top-3 {ex0}")
assert a_ok, "ANCHOR A FAILED -- do not judge"

# ---------- candle store + replay (CH-2 machinery verbatim) ----------
def load_candles(sym):
    days = {}
    with open(f"{BASE}/data/progressive/{sym}/spot_5m.csv") as f:
        for r in csv.DictReader(f):
            d = r["timestamp"][:10]
            days.setdefault(d, []).append({"time": r["timestamp"][11:16],
                "open": float(r["open"]), "high": float(r["high"]),
                "low": float(r["low"]), "close": float(r["close"])})
    for d in days: days[d].sort(key=lambda c: c["time"])
    return days
CAND = {}
def candles_for(sym, day):
    if sym not in CAND: CAND[sym] = load_candles(sym)
    return CAND[sym].get(day, [])

def replay(candles, ei, entry, direction, tgt_pct, stp_pct, start_offset):
    sign = 1 if direction == "LONG" else -1
    target = entry * (1 + sign * tgt_pct / 100)
    stop = entry * (1 - sign * stp_pct / 100)
    last = None
    for j in range(ei + start_offset, len(candles)):
        c = candles[j]
        if c["time"] > "15:10": break
        last = c
        if sign == 1:
            if c["low"] <= stop: return "stop", stop, c["time"]
            if c["high"] >= target: return "target", target, c["time"]
        else:
            if c["high"] >= stop: return "stop", stop, c["time"]
            if c["low"] <= target: return "target", target, c["time"]
        if c["time"] == "15:10": return "square_off", c["close"], c["time"]
    if last is not None: return "square_off", last["close"], last["time"]
    return None

def net_of(direction, entry, exit_price):
    sign = 1 if direction == "LONG" else -1
    return round(sign * (exit_price - entry) * QTY - COST, 2)

raw = rd("eq_n4deep_v3_trades_T125_janoct.csv")
def replay_all(tgt, stp, offset):
    out, bad = [], 0
    for r in raw:
        candles = candles_for(r["stock"], r["date"])
        ei = next(i for i, c in enumerate(candles) if c["time"] == r["entry_time"])
        res = replay(candles, ei, float(r["entry"]), r["direction"], tgt, stp, offset)
        if res is None: bad += 1; continue
        er, ep, et = res
        out.append({"date": r["date"], "stock": r["stock"], "direction": r["direction"],
                    "entry_time": r["entry_time"], "entry": float(r["entry"]),
                    "exit_reason": er, "exit_price": round(ep, 2), "exit_time": et,
                    "net": net_of(r["direction"], float(r["entry"]), ep),
                    "src_net": float(r["net_rs_provisional_per100"]),
                    "src_reason": r["exit_reason"]})
    return out, bad

# ---------- ANCHOR B: replay at T125/S050 reproduces the dump + book N4 ----------
conv = None
for offset in (0, 1):
    out0, bad0 = replay_all(1.25, 0.50, offset)
    match = sum(1 for t in out0
                if abs(t["net"] - t["src_net"]) < 0.011
                and t["exit_reason"] == t["src_reason"])
    print(f"replay convention offset={offset}: {match}/{len(raw)} match (bad={bad0})")
    if match == len(raw) and bad0 == 0: conv = offset
assert conv is not None, "ANCHOR B FAIL -- no convention reproduces the dump"
replay_old, _ = replay_all(1.25, 0.50, conv)
filt_old = sorted((t["date"], t["stock"], t["direction"], t["net"])
                  for t in replay_old
                  if not wk(t["date"]) and t["stock"] != "ASTRAL")
book_n4_set = sorted((t["date"], t["stock"], t["dir"], t["net"]) for t in n4_book)
b_ok = filt_old == book_n4_set
print(f"ANCHOR B: replay(T125/S050) filtered == book N4 per-trade: {b_ok} "
      f"| {len(filt_old)} tr, convention offset={conv}")
assert b_ok, "ANCHOR B FAILED -- replay does not regenerate the book's N4"

# ---------- rebuild at T150/S080 + ANCHOR C ----------
new_all, bad_new = replay_all(1.50, 0.80, conv)
audit_v = 0
same_bar = 0
for t, r in zip(new_all, raw):
    if not (t["date"] == r["date"] and t["stock"] == r["stock"]
            and t["direction"] == r["direction"]
            and t["entry_time"] == r["entry_time"] and t["entry_time"] == "09:35"
            and abs(t["entry"] - float(r["entry"])) < 0.001
            and t["exit_time"] >= t["entry_time"]):
        audit_v += 1
    if t["exit_time"] == t["entry_time"]: same_bar += 1
c_ok = (audit_v == 0 and bad_new == 0 and len(new_all) == len(raw))
print(f"ANCHOR C: entry/timing audit on T150/S080 build: {c_ok} | "
      f"violations {audit_v}, bad {bad_new}, same-bar exits {same_bar}")
assert c_ok, "ANCHOR C FAILED"

n4_new = [{"date": t["date"], "stock": t["stock"], "comp": "N4-V3",
           "dir": t["direction"], "net": t["net"]}
          for t in new_all if not wk(t["date"]) and t["stock"] != "ASTRAL"]
n4_old_net = round(sum(t["net"] for t in n4_book), 2)
n4_new_net = round(sum(t["net"] for t in n4_new), 2)
print(f"N4 component at THIS book: {len(n4_book)} tr / {n4_old_net} -> "
      f"{len(n4_new)} tr / {n4_new_net} (delta {round(n4_new_net-n4_old_net,2)})")
n4_old_m, _ = mt(n4_book); n4_new_m, _ = mt(n4_new)
n4_delta_m = {k: round(n4_new_m.get(k, 0.0) - n4_old_m.get(k, 0.0), 2)
              for k in STATE}

# ---------- union + gate ----------
union = inv + n4_new + p2f + f4 + r2
nt, nc = mt(union)
tot_new = round(sum(t["net"] for t in union), 2)
ex1, top3_1 = extop3(union)
print(f"\n{'month':8} {'current':>10} {'SAT-15':>10} {'delta':>10} {'trades':>7}")
for k in sorted(STATE):
    print(f"{k:8} {STATE[k]:>10.2f} {nt.get(k,0.0):>10.2f} "
          f"{round(nt.get(k,0.0)-STATE[k],2):>10.2f} {nc.get(k,0):>7}")
print(f"{'TOTAL':8} {STATE_TOTAL:>10.2f} {tot_new:>10.2f} "
      f"{round(tot_new-STATE_TOTAL,2):>10.2f} {len(union):>7}")
print(f"new ex-top-3: {ex1} (top3 {top3_1}) | delta {round(ex1-ex0,2)}")
print(f"August after: Rs{nt['2026-08']} | June after: Rs{nt['2026-06']} | "
      f"October after: Rs{nt['2026-10']} (headroom "
      f"Rs{round(nt['2026-10']-50000,2)})")

print("\n=== SATURATION GATE (frozen SAT-15) ===")
ga = tot_new > STATE_TOTAL
gb = all(v > 0 for v in nt.values())
gc = nt["2026-10"] >= 50000
gd = ex1 >= ex0
ge = a_ok and b_ok and c_ok
print(f"(a) total rises: {tot_new} > {STATE_TOTAL} -> {ga}")
print(f"(b) all ten months > 0: {gb} (min {min(nt.values())} in "
      f"{min(nt, key=nt.get)})")
print(f"(c) October >= 50,000: {nt['2026-10']} -> {gc}")
print(f"(d) ex-top-3 not worse: {ex1} >= {ex0} -> {gd}")
print(f"(e) anchors pass: -> {ge} (A {a_ok}, B {b_ok}, C {c_ok})")
banked = all([ga, gb, gc, gd, ge])
print("BANKED:", banked)

# revisit arithmetic (recorded either way; binding if rejected)
revisit = {}
for k in sorted(STATE):
    if nt.get(k, 0.0) <= 0:
        revisit[k] = {
            "challenger_value": nt[k], "rebuild_delta": n4_delta_m[k],
            "current_balance": STATE[k],
            "must_gain_by_other_means": round(-nt[k], 2),
            "required_pre_rebuild_balance_gt": round(-n4_delta_m[k], 2)}
if revisit:
    print("REVISIT ARITHMETIC (months red under the rebuild at THIS book):",
          revisit)

with open(f"{BASE}/stocks_engine_sat15_n4_t150s080_trades.csv", "w",
          newline="") as f:
    w = csv.DictWriter(f, fieldnames=["date", "stock", "direction",
                                      "entry_time", "entry", "exit_reason",
                                      "exit_price", "exit_time", "net",
                                      "src_net_T125S050", "src_reason"])
    w.writeheader()
    for t in sorted(new_all, key=lambda x: (x["date"], x["stock"])):
        w.writerow({**{k: t[k] for k in ("date", "stock", "direction",
                                         "entry_time", "entry", "exit_reason",
                                         "exit_price", "exit_time", "net")},
                    "src_net_T125S050": t["src_net"], "src_reason": t["src_reason"]})

json.dump({"anchors": {"A": a_ok, "B": b_ok, "C": c_ok,
                       "replay_convention_offset": conv,
                       "audit_violations": audit_v, "same_bar_exits": same_bar},
           "fix": "SAT-15-N4-T150S080-REAPPLY (N4-V3 exits T125/S050 -> "
                  "T150/S080, entries frozen verbatim; re-measured at "
                  "the current five-component book)",
           "fix_id": "SAT-15-N4-T150S080-REAPPLY",
           "n4_old": {"trades": len(n4_book), "net": n4_old_net},
           "n4_new": {"trades": len(n4_new), "net": n4_new_net},
           "n4_component_delta": round(n4_new_net - n4_old_net, 2),
           "n4_month_deltas": n4_delta_m,
           "ch2_stale_deltas_for_comparison": {
               "component": 9483.45, "august": -3834.85},
           "new_month_table": nt, "new_total": tot_new,
           "new_trades": len(union), "banked": banked,
           "deltas": {k: round(nt.get(k, 0.0) - STATE[k], 2) for k in STATE},
           "ex_top3_before": ex0, "ex_top3_after": ex1,
           "top3_after": top3_1,
           "legs": {"a_total": ga, "b_all_green": gb, "c_oct": gc,
                    "d_extop3": gd, "e_anchors": ge},
           "oct_headroom_after": round(nt["2026-10"] - 50000, 2),
           "august_after": nt["2026-08"], "june_after": nt["2026-06"],
           "revisit_arithmetic": revisit},
          open(f"{BASE}/stocks_engine_sat15_result.json", "w"), indent=1)
print("\nwrote stocks_engine_sat15_result.json + "
      "stocks_engine_sat15_n4_t150s080_trades.csv")
