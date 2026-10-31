#!/usr/bin/env python3
"""ENGINE SAT-16 DIAGNOSIS: P2F-R3 candidate (R+3 reaction follow).
Incumbent anchored from the CURRENT component dumps (book law SAT-15:
N4 from stocks_engine_sat15_n4_t150s080_trades.csv, NOT M1.load_n4()).
R3 built with the SAT-13 machinery verbatim, entry lag ri+3 instead of
ri+2. Diagnosis only -- the freeze happens after this runs, the score
script re-verifies everything. Paper, real Rs0, per 100 shares,
Rs40/trade, home 25."""
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
counts = {c: sum(1 for t in book if t["comp"] == c)
          for c in ("INV-LONG", "N4-V3", "P2F", "F4", "P2F-R2")}
print("component counts:", counts)

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
print(f"ANCHOR A: incumbent == state: {a_ok} | {len(book)} tr / "
      f"{round(sum(t['net'] for t in book),2)} / ex-top-3 {ex0} (top3 {top3_0})")
assert a_ok, "ANCHOR A FAILED"

# ---------- R3 build (SAT-13 machinery verbatim, lag +3) ----------
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
print(f"candidate population: {len(cands25)} (construction anchor == 39: "
      f"{len(cands25) == 39})")

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
dropped = [c for c in cands25 if score_r3(c) is None]
print(f"R3 raw built: {len(r3_all)} | dropped (no R+3/bars): "
      f"{[(c['symbol'], c['R']) for c in dropped]}")
r3 = [t for t in r3_all
      if not wk(t["date"]) and t["symbol"] not in ("ASTRAL", "HINDUNILVR")]
excl_trades = [t for t in r3_all if t not in r3]
print(f"R3 frozen (RF-1 + AU-1/JU-1 names): {len(r3)} | excluded: "
      f"{[(t['symbol'], t['date'], t['net_rs']) for t in excl_trades]}")

# timing audit: every frozen trade date == daily[didx[R]+3]
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
self_keys = [(t["symbol"], t["date"]) for t in r3]
print(f"timing audit violations: {len(bad)} | overlap vs P2F: {len(ov_p2f)} "
      f"| overlap vs P2F-R2: {len(ov_r2)} | within-R3 dup (sym,date): "
      f"{len(self_keys) - len(set(self_keys))}")

plac = [t for t in (score_r3(c, flip=True) for c in cands25
                    if c["symbol"] not in ("ASTRAL", "HINDUNILVR")) if t]
plac = [t for t in plac if not wk(t["date"])]

def halves(trades, key="net_rs"):
    return (round(sum(t[key] for t in trades if t["date"] <= "2026-05-31"), 2),
            round(sum(t[key] for t in trades if t["date"] > "2026-05-31"), 2))

def summ(trades, key="net_rs"):
    tot = round(sum(t[key] for t in trades), 2)
    h1, h2 = halves(trades, key)
    return {"trades": len(trades), "net": tot, "h1": h1, "h2": h2,
            "exp": round(tot / len(trades), 2) if trades else 0,
            "win": sum(1 for t in trades if t[key] > 0),
            "breadth": len({t["symbol"] for t in trades})}

r3_s, pl_s = summ(r3), summ(plac)
r3_m, _ = mt([{"date": t["date"], "net": t["net_rs"]} for t in r3])
print(f"\nR3 frozen standalone: {r3_s}")
print(f"R3 month nets: {r3_m}")
print(f"R3 August slice: {r3_m.get('2026-08', 0.0)} | October slice: "
      f"{r3_m.get('2026-10', 0.0)}")
print(f"placebo (flip, frozen subset): {pl_s}")

new_book = book + [{"date": t["date"], "stock": t["symbol"], "comp": "P2F-R3",
                    "dir": t["direction"], "net": t["net_rs"]} for t in r3]
nt, nc = mt(new_book)
tot_new = round(sum(t["net"] for t in new_book), 2)
ex1, top3_1 = extop3(new_book)
print(f"\n{'month':8} {'current':>10} {'union':>10} {'delta':>10}")
for k in sorted(STATE):
    print(f"{k:8} {STATE[k]:>10.2f} {nt.get(k,0.0):>10.2f} "
          f"{round(nt.get(k,0.0)-STATE[k],2):>10.2f}")
print(f"TOTAL {STATE_TOTAL} -> {tot_new} | trades {len(new_book)} | "
      f"ex-top-3 {ex0} -> {ex1} (top3 {top3_1})")
print(f"GATE preview: (a) total up {tot_new > STATE_TOTAL} | (b) all green "
      f"{all(v > 0 for v in nt.values())} (min {min(nt.values())} in "
      f"{min(nt, key=nt.get)}) | (c) Oct {nt['2026-10']} >= 50000 "
      f"{nt['2026-10'] >= 50000} | (d) ex-top-3 {ex1 >= ex0} | "
      f"August union value: {nt['2026-08']}")

json.dump({"anchor_a": a_ok, "candidates": len(cands25),
           "r3_raw_trades": len(r3_all), "r3_frozen_trades": len(r3),
           "dropped": [(c["symbol"], c["R"]) for c in dropped],
           "excluded": [{"symbol": t["symbol"], "date": t["date"],
                         "net": t["net_rs"]} for t in excl_trades],
           "timing_violations": len(bad), "overlap_p2f": len(ov_p2f),
           "overlap_r2": len(ov_r2),
           "r3_standalone": r3_s, "r3_months": r3_m,
           "placebo": pl_s,
           "r3_trades": r3,
           "union_months": nt, "union_total": tot_new,
           "union_trades": len(new_book),
           "ex_top3_before": ex0, "ex_top3_after": ex1},
          open(f"{BASE}/stocks_engine_sat16_diag.json", "w"), indent=1)
print("\nwrote stocks_engine_sat16_diag.json")
