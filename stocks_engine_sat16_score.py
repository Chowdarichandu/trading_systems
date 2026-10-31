#!/usr/bin/env python3
"""ENGINE SAT-16 SCORE: P2F-R3 as 6th component, frozen in
stocks_engine_frozen.md (SAT-16 section) AFTER the diagnosis
(sat16_diag) and BEFORE this ran. Anchors: (A) incumbent union ==
state (812 tr / +176,231.95 / month table / ex-top-3 56,308.12),
N4 anchored on the SAT-15 T150/S080 dump (book law -- M1.load_n4()
is the stale T125/S050 dump and is NOT used); (B) candidate
population == 39 and frozen 34-trade set == diagnosis set;
(C) timing audit 0 + P2F overlap 0 + P2F-R2 overlap 0;
(D) placebo on the frozen subset (reported; Lesson 18: beaten
per-trade by its placebo is disqualifying evidence).
Paper, real Rs0, per 100 shares, Rs40/trade, home 25."""
import csv, sys, json
from collections import defaultdict
sys.path.insert(0, "/home/hatch/workspace/trading")
import importlib.util
from datetime import date, timedelta

BASE = "/home/hatch/workspace/trading"
def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m
M1 = load_mod("M1", f"{BASE}/stocks_M1.py")

def wk(d): return date.fromisoformat(d).weekday() >= 5
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))

STATE = {"2026-01": 25923.78, "2026-02": 17465.71, "2026-03": 19259.91,
         "2026-04": 7534.13, "2026-05": 33304.29, "2026-06": 1382.01,
         "2026-07": 1262.53, "2026-08": 309.08, "2026-09": 17542.75,
         "2026-10": 52247.76}
STATE_TOTAL, STATE_TRADES, STATE_EXTOP3 = 176231.95, 812, 56308.12

# ---------- incumbent book (SAT-15 construction; N4 from SAT-15 dump) ----------
inv = [{"date": t["date"], "stock": t["stock"], "comp": "INV-LONG",
        "dir": t["dir"], "net": t["net"]}
       for t in M1.load_inv_long()
       if not wk(t["date"]) and t["stock"] != "BDL"]
n4 = [{"date": r["date"], "stock": r["stock"], "comp": "N4-V3",
       "dir": r["direction"], "net": float(r["net"])}
      for r in rd("stocks_engine_sat15_n4_t150s080_trades.csv")
      if not wk(r["date"]) and r["stock"] != "ASTRAL"]
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
book = inv + n4 + p2f + f4 + r2

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
print(f"ANCHOR A: incumbent union == state: {a_ok} | {len(book)} tr / "
      f"{round(sum(t['net'] for t in book),2)} / ex-top-3 {ex0}")
assert a_ok, "ANCHOR A FAILED — do not judge"

# ---------- P2F-R3 rebuild (verbatim machinery, lag +3) ----------
DATA = f"{BASE}/data/progressive"
SYMBOLS = M1.HOME25
QTY, COST = 100, 40.0
ALL_LO, ALL_HI = "2026-01-01", "2026-10-28"

def load_stock(sym):
    spot, daily = {}, []
    with open(f"{DATA}/{sym}/spot_5m.csv") as f:
        for r in csv.DictReader(f):
            d = r["timestamp"][:10]
            spot.setdefault(d, []).append(
                {"timestamp": r["timestamp"][:19], "time": r["timestamp"][11:16],
                 "open": float(r["open"]), "high": float(r["high"]),
                 "low": float(r["low"]), "close": float(r["close"])})
    with open(f"{DATA}/{sym}/spot_daily.csv") as f:
        for r in csv.DictReader(f):
            daily.append({"date": r["date"][:10], "open": float(r["open"]),
                          "high": float(r["high"]), "low": float(r["low"]),
                          "close": float(r["close"])})
    daily.sort(key=lambda x: x["date"])
    for d in spot: spot[d].sort(key=lambda x: x["timestamp"])
    return spot, daily

stocks = {s: load_stock(s) for s in SYMBOLS}

def replay(candles, ei, entry, direction, tgt_pct, stp_pct):
    sign = 1 if direction == "LONG" else -1
    target = entry * (1 + sign * tgt_pct / 100)
    stop = entry * (1 - sign * stp_pct / 100)
    last = None
    for j in range(ei + 1, len(candles)):
        c = candles[j]
        if c["time"] > "15:10": break
        last = c
        if sign == 1:
            if c["low"] <= stop: return "stop", stop, c["time"]
            if c["high"] >= target: return "target", target, c["time"]
        else:
            if c["high"] >= stop: return "stop", stop, c["time"]
            if c["low"] <= target: return "target", target, c["time"]
        if c["time"] == "15:10":
            return "square_off", c["close"], c["time"]
    if last is not None:
        return "square_off", last["close"], last["time"]
    return None

def net_of(direction, entry, exit_price):
    sign = 1 if direction == "LONG" else -1
    return round(sign * (exit_price - entry) * QTY - COST, 2)

events = []
with open(f"{BASE}/stock_event_calendar_jan_oct_2026.csv") as f:
    for r in csv.DictReader(f):
        if r["event_type"] != "results" or r["stock"] not in SYMBOLS: continue
        ev = date.fromisoformat(r["event_date"][:10])
        react = date.fromisoformat(r["reaction_date"][:10]) if r["reaction_date"] else None
        eff = react if (react and ev <= react <= ev + timedelta(days=7)) else ev
        ds = eff.isoformat()
        if ALL_LO <= ds <= ALL_HI:
            events.append({"symbol": r["stock"], "announce": r["event_date"][:10], "R": ds})
events.sort(key=lambda e: (e["symbol"], e["R"]))

cands25 = []
for e in events:
    sym, R = e["symbol"], e["R"]
    spot, daily = stocks[sym]
    didx = {d["date"]: i for i, d in enumerate(daily)}
    if R not in didx: continue
    ri = didx[R]
    if ri == 0 or ri + 1 >= len(daily): continue
    reaction_ret = round((daily[ri]["close"] / daily[ri - 1]["close"] - 1) * 100, 2)
    nd = daily[ri + 1]["date"]
    if nd > ALL_HI: continue
    if not spot.get(nd): continue
    if abs(reaction_ret) < 2.5: continue
    cands25.append({"symbol": sym, "announce": e["announce"], "R": R,
                    "reaction_ret_pct": reaction_ret, "ri": ri,
                    "direction": "LONG" if reaction_ret > 0 else "SHORT"})

def score_r3(cand, flip=False):
    sym = cand["symbol"]; spot, daily = stocks[sym]
    ri = cand["ri"]
    if ri + 3 >= len(daily): return None
    d3 = daily[ri + 3]["date"]
    bars = spot.get(d3, [])
    if not bars: return None
    direction = cand["direction"]
    if flip: direction = "SHORT" if direction == "LONG" else "LONG"
    entry = bars[0]["open"]
    r = replay(bars, 0, entry, direction, 1.25, 0.5)
    if r is None: return None
    er, ep, et = r
    return {"symbol": sym, "date": d3, "direction": direction,
            "entry_time": "09:15", "entry": round(entry, 2),
            "exit_reason": er, "exit_price": round(ep, 2), "exit_time": et,
            "net_rs": net_of(direction, entry, ep), "R": cand["R"],
            "reaction_ret_pct": cand["reaction_ret_pct"],
            "note": f"P2F-R3 reaction {cand['R']} {cand['reaction_ret_pct']:+.2f}%"}

r3_all = [t for t in (score_r3(c) for c in cands25) if t]
r3 = [t for t in r3_all
      if not wk(t["date"]) and t["symbol"] not in ("ASTRAL", "HINDUNILVR")]
diag = json.load(open(f"{BASE}/stocks_engine_sat16_diag.json"))
diag_set = sorted((t["date"], t["symbol"], t["direction"], t["net_rs"])
                  for t in diag["r3_trades"])
score_set = sorted((t["date"], t["symbol"], t["direction"], t["net_rs"])
                   for t in r3)
b_ok = len(cands25) == 39 and score_set == diag_set and len(r3) == 34
print(f"ANCHOR B: candidates {len(cands25)} (==39), frozen set == diagnosis "
      f"set: {score_set == diag_set} | frozen trades {len(r3)}")
bad = []
for t in r3:
    _, daily = stocks[t["symbol"]]
    didx = {d["date"]: i for i, d in enumerate(daily)}
    if didx[t["R"]] + 3 >= len(daily) or daily[didx[t["R"]] + 3]["date"] != t["date"]:
        bad.append((t["symbol"], t["R"], t["date"]))
p2f_keys = {(t["stock"], t["date"]) for t in p2f}
r2_keys = {(t["stock"], t["date"]) for t in r2}
ov_p2f = [(t["symbol"], t["date"]) for t in r3 if (t["symbol"], t["date"]) in p2f_keys]
ov_r2 = [(t["symbol"], t["date"]) for t in r3 if (t["symbol"], t["date"]) in r2_keys]
c_ok = len(bad) == 0 and len(ov_p2f) == 0 and len(ov_r2) == 0
print(f"ANCHOR C: timing audit violations={len(bad)}, P2F overlap="
      f"{len(ov_p2f)}, P2F-R2 overlap={len(ov_r2)}")
assert b_ok and c_ok, "ANCHOR B/C FAILED — do not judge"

plac = [t for t in (score_r3(c, flip=True) for c in cands25
                    if c["symbol"] not in ("ASTRAL", "HINDUNILVR")) if t]
plac = [t for t in plac if not wk(t["date"])]
pl_tot = round(sum(t["net_rs"] for t in plac), 2)
pl_exp = round(pl_tot / len(plac), 2) if plac else 0
print(f"ANCHOR D (disclosed): placebo on frozen subset: {len(plac)} tr / "
      f"{pl_tot} (exp {pl_exp})")

def halves(trades, key="net_rs"):
    return (round(sum(t[key] for t in trades if t["date"] <= "2026-05-31"), 2),
            round(sum(t[key] for t in trades if t["date"] > "2026-05-31"), 2))

r3_tot = round(sum(t["net_rs"] for t in r3), 2)
r3_h1, r3_h2 = halves(r3)
r3_exp = round(r3_tot / len(r3), 2)
r3_aug = round(sum(t["net_rs"] for t in r3 if t["date"][:7] == "2026-08"), 2)
r3_breadth = len({t["symbol"] for t in r3})
print(f"\nP2F-R3 (frozen): {len(r3)} tr / {r3_tot} | H1 {r3_h1} / H2 {r3_h2} | "
      f"exp {r3_exp} | win {sum(1 for t in r3 if t['net_rs'] > 0)}/{len(r3)} "
      f"| breadth {r3_breadth} | August slice {r3_aug} | placebo {pl_tot} "
      f"(exp {pl_exp}) -> placebo beaten per-trade: {r3_exp > pl_exp}")

new_book = book + [{"date": t["date"], "stock": t["symbol"], "comp": "P2F-R3",
                    "dir": t["direction"], "net": t["net_rs"]} for t in r3]
nt, nc = mt(new_book)
tot_new = round(sum(t["net"] for t in new_book), 2)
print(f"\n{'month':8} {'current':>10} {'SAT-16':>10} {'delta':>10} {'trades':>7}")
for k in sorted(STATE):
    print(f"{k:8} {STATE[k]:>10.2f} {nt.get(k,0.0):>10.2f} "
          f"{round(nt.get(k,0.0)-STATE[k],2):>10.2f} {nc.get(k,0):>7}")
print(f"{'TOTAL':8} {STATE_TOTAL:>10.2f} {tot_new:>10.2f} "
      f"{round(tot_new-STATE_TOTAL,2):>10.2f} {len(new_book):>7}")
ex1, top3_1 = extop3(new_book)
print(f"new ex-top-3: {ex1} (top3 {top3_1}) | delta {round(ex1-ex0,2)}")
print(f"August after: Rs{nt['2026-08']} (incumbent razor Rs309.08, R3 slice "
      f"Rs{r3_aug})")
print(f"October after: Rs{nt['2026-10']} | headroom "
      f"Rs{round(nt['2026-10']-50000,2)}")

print("\n=== SATURATION GATE (frozen SAT-16) ===")
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
print(f"(e) anchors + audit clean: -> {ge} (A {a_ok}, B {b_ok}, C {c_ok})")
banked = all([ga, gb, gc, gd, ge])
print("BANKED:", banked)
print(f"controls note: placebo exp {pl_exp} vs component exp {r3_exp} — "
      f"placebo beaten per-trade: {r3_exp > pl_exp} (Lesson 18)")

if banked:
    with open(f"{BASE}/stocks_engine_sat16_p2fr3_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["leg", "symbol", "date", "direction",
                           "entry_time", "entry", "exit_reason", "exit_price",
                           "exit_time", "net_rs", "R", "reaction_ret_pct", "note"])
        w.writeheader()
        for t in sorted(r3, key=lambda x: (x["date"], x["symbol"])):
            w.writerow(dict(t, leg="P2F-R3"))
    print("wrote stocks_engine_sat16_p2fr3_trades.csv (new component dump)")

json.dump({"anchors": {"A": a_ok, "B": b_ok, "C": c_ok},
           "fix": "SAT-16-P2F-R3 (6th component: R+3 reaction follow, 2.5% band, "
                  "T125/S050, RF-1, AU-1/JU-1 name exclusions)",
           "fix_id": "SAT-16-P2F-R3",
           "component": {"trades": len(r3), "net": r3_tot, "h1": r3_h1,
                         "h2": r3_h2, "exp": r3_exp,
                         "win": sum(1 for t in r3 if t["net_rs"] > 0),
                         "breadth": r3_breadth, "august_slice": r3_aug,
                         "placebo_frozen_subset": pl_tot,
                         "placebo_exp": pl_exp,
                         "placebo_beaten_per_trade": r3_exp > pl_exp},
           "new_month_table": nt, "new_total": tot_new,
           "new_trades": len(new_book), "banked": banked,
           "deltas": {k: round(nt.get(k, 0.0) - STATE[k], 2) for k in STATE},
           "ex_top3_before": ex0, "ex_top3_after": ex1,
           "legs": {"a_total": ga, "b_all_green": gb, "c_oct": gc,
                    "d_extop3": gd, "e_anchors_audit": ge},
           "oct_headroom_after": round(nt["2026-10"] - 50000, 2),
           "august_after": nt["2026-08"]},
          open(f"{BASE}/stocks_engine_sat16_result.json", "w"), indent=1)
print("\nwrote stocks_engine_sat16_result.json")
