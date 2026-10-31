#!/usr/bin/env python3
"""ENGINE SAT-33 SCORE: R2-LOWBAND as 6th component, frozen in
stocks_engine_frozen.md (SAT-33 section) BEFORE this ran. Anchors:
(A) incumbent union == state (656 tr / +196,346.96 / month table /
ex-top-3 71,257.47), per book law; (B) frozen R2-lowband set == the
diagnosis set (sat33_diag.json) exactly, with the construction
anchor re-verified (lag+2 >=2.5% == SAT-13 R2 dump 34/34);
(C) timing audit 0 + overlap vs P2F == 0 + vs P2F-R2 == 0 + vs
P2F-LOWBAND (SAT-32 frozen set) == 0; (D) placebo on the frozen
subset (Lesson 18/21: expectancy first, vs placebo AND vs zero).
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
a_ok = (bt == STATE and round(sum(t["net"] for t in book), 2) == STATE_TOTAL
        and len(book) == STATE_TRADES and ex0 == STATE_EXTOP3)
print(f"ANCHOR A: incumbent == state: {a_ok} | {len(book)} tr / "
      f"{round(sum(t['net'] for t in book),2)} / ex-top-3 {ex0}")
print(f"  components: INV {len(inv)} / N4 {len(n4)} / P2F {len(p2f)} / "
      f"F4 {len(f4)} / R2 {len(r2)}")
assert a_ok, "ANCHOR A FAILED -- do not judge"

# ---------- R2-lowband rebuild (verbatim diag machinery) ----------
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

def replay(candles, entry, direction, tgt_pct, stp_pct):
    sign = 1 if direction == "LONG" else -1
    target = entry * (1 + sign * tgt_pct / 100)
    stop = entry * (1 - sign * stp_pct / 100)
    last = None
    for j in range(1, len(candles)):
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

cands_low, cands_ge25 = [], []
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
    c = {"symbol": sym, "announce": e["announce"], "R": R,
         "reaction_ret_pct": reaction_ret, "ri": ri,
         "direction": "LONG" if reaction_ret > 0 else "SHORT"}
    if abs(reaction_ret) >= 2.5: cands_ge25.append(c)
    elif 2.0 <= abs(reaction_ret) < 2.5: cands_low.append(c)

def score_lag2(cand, flip=False):
    sym = cand["symbol"]; spot, daily = stocks[sym]
    ri = cand["ri"]
    if ri + 2 >= len(daily): return None
    d2 = daily[ri + 2]["date"]
    bars = spot.get(d2, [])
    if not bars: return None
    direction = cand["direction"]
    if flip: direction = "SHORT" if direction == "LONG" else "LONG"
    entry = bars[0]["open"]
    r = replay(bars, entry, direction, 1.25, 0.5)
    if r is None: return None
    er, ep, et = r
    return {"symbol": sym, "date": d2, "direction": direction,
            "entry_time": "09:15", "entry": round(entry, 2),
            "exit_reason": er, "exit_price": round(ep, 2), "exit_time": et,
            "net_rs": net_of(direction, entry, ep), "R": cand["R"],
            "reaction_ret_pct": cand["reaction_ret_pct"],
            "note": f"R2-LOWBAND reaction {cand['R']} {cand['reaction_ret_pct']:+.2f}%"}

def frozen_filter(raw):
    return [t for t in raw
            if not wk(t["date"]) and t["symbol"] not in ("ASTRAL", "HINDUNILVR")
            and not (t["symbol"] == "HINDALCO" and t["direction"] == "LONG")]

# construction anchor re-verified in the score pass
dump = {}
for r in rd("stocks_engine_sat13_p2fr2_trades.csv"):
    dump[(r["date"], r["symbol"], r["direction"])] = (
        round(float(r["net_rs"]), 2), r["exit_reason"])
b25 = frozen_filter([t for t in (score_lag2(c) for c in cands_ge25) if t])
# SAT-13 filter had no HINDALCO clause; its frozen set is ASTRAL/HINDUNILVR+wk only
b25_sat13 = [t for t in (score_lag2(c) for c in cands_ge25) if t]
b25_sat13 = [t for t in b25_sat13
             if not wk(t["date"]) and t["symbol"] not in ("ASTRAL", "HINDUNILVR")]
match = sum(1 for t in b25_sat13
            if dump.get((t["date"], t["symbol"], t["direction"]), (None, None))[0] is not None
            and abs(dump[(t["date"], t["symbol"], t["direction"])][0] - t["net_rs"]) < 0.011
            and dump[(t["date"], t["symbol"], t["direction"])][1] == t["exit_reason"])
ca_ok = len(b25_sat13) == len(dump) == 34 and match == 34
print(f"CONSTRUCTION ANCHOR (score pass): lag+2 >=2.5% matches SAT-13 "
      f"R2 dump {match}/{len(dump)} -> {ca_ok}")
assert ca_ok, "CONSTRUCTION ANCHOR FAILED -- do not judge"

low = frozen_filter([t for t in (score_lag2(c) for c in cands_low) if t])
diag = json.load(open(f"{BASE}/stocks_engine_sat33_diag.json"))
diag_set = sorted((t["date"], t["symbol"], t["direction"], t["net_rs"])
                  for t in diag["lowband_trades"])
score_set = sorted((t["date"], t["symbol"], t["direction"], t["net_rs"])
                   for t in low)
b_ok = len(cands_low) == 9 and score_set == diag_set and len(low) == 7 \
    and diag["construction_anchor"]["matches"] == 34
print(f"ANCHOR B: lowband candidates {len(cands_low)} (==9), frozen set "
      f"== diagnosis set: {score_set == diag_set} | frozen trades {len(low)}")
assert b_ok, "ANCHOR B FAILED -- do not judge"

bad = []
for t in low:
    _, daily = stocks[t["symbol"]]
    didx = {d["date"]: i for i, d in enumerate(daily)}
    if didx[t["R"]] + 2 >= len(daily) or daily[didx[t["R"]] + 2]["date"] != t["date"]:
        bad.append((t["symbol"], t["R"], t["date"]))
p2f_keys = {(t["stock"], t["date"]) for t in p2f}
r2_keys = {(t["stock"], t["date"]) for t in r2}
d32 = json.load(open(f"{BASE}/stocks_engine_sat32_diag.json"))
lb_keys = {(t["symbol"], t["date"]) for t in d32["lowband_trades"]}
ov_p2f = [(t["symbol"], t["date"]) for t in low if (t["symbol"], t["date"]) in p2f_keys]
ov_r2 = [(t["symbol"], t["date"]) for t in low if (t["symbol"], t["date"]) in r2_keys]
ov_lb = [(t["symbol"], t["date"]) for t in low if (t["symbol"], t["date"]) in lb_keys]
c_ok = len(bad) == 0 and len(ov_p2f) == 0 and len(ov_r2) == 0 and len(ov_lb) == 0
print(f"ANCHOR C: timing audit violations={len(bad)}, P2F overlap="
      f"{len(ov_p2f)}, P2F-R2 overlap={len(ov_r2)}, P2F-LOWBAND overlap={len(ov_lb)}")
assert c_ok, "ANCHOR C FAILED -- do not judge"

plac = frozen_filter([t for t in (score_lag2(c, flip=True) for c in cands_low) if t])
pl_tot = round(sum(t["net_rs"] for t in plac), 2)
pl_exp = round(pl_tot / len(plac), 2) if plac else 0
print(f"placebo (frozen subset): {len(plac)} tr / {pl_tot} (exp {pl_exp})")
for t in sorted(plac, key=lambda x: (x["date"], x["symbol"])):
    print(f"   placebo {t['date']} {t['symbol']:10s} {t['direction']:5s} "
          f"{t['net_rs']:+9.2f} {t['exit_reason']}")

def halves(trades):
    return (round(sum(t["net_rs"] for t in trades if t["date"] <= "2026-05-31"), 2),
            round(sum(t["net_rs"] for t in trades if t["date"] > "2026-05-31"), 2))

lb_tot = round(sum(t["net_rs"] for t in low), 2)
lb_h1, lb_h2 = halves(low)
lb_exp = round(lb_tot / len(low), 2)
lb_aug = round(sum(t["net_rs"] for t in low if t["date"][:7] == "2026-08"), 2)
lb_oct = round(sum(t["net_rs"] for t in low if t["date"][:7] == "2026-10"), 2)
lb_breadth = len({t["symbol"] for t in low
                  if sum(x["net_rs"] for x in low if x["symbol"] == t["symbol"]) > 0})
print(f"\nR2-LOWBAND (frozen): {len(low)} tr / {lb_tot} | H1 {lb_h1} / "
      f"H2 {lb_h2} | exp {lb_exp} | win "
      f"{sum(1 for t in low if t['net_rs'] > 0)}/{len(low)} | breadth "
      f"{lb_breadth} | August slice {lb_aug} | October slice {lb_oct} | "
      f"placebo {pl_tot} (exp {pl_exp}) -> beaten per-trade: {lb_exp > pl_exp}")
for t in sorted(low, key=lambda x: (x["date"], x["symbol"])):
    print(f"   real {t['date']} {t['symbol']:10s} {t['direction']:5s} "
          f"{t['net_rs']:+9.2f} {t['exit_reason']}")

union = book + [{"date": t["date"], "stock": t["symbol"],
                 "comp": "R2-LOWBAND", "dir": t["direction"],
                 "net": t["net_rs"]} for t in low]
nt, nc = mt(union)
tot_new = round(sum(t["net"] for t in union), 2)
ex1, top3_1 = extop3(union)
print(f"\n{'month':8} {'incumbent':>10} {'union':>10} {'delta':>10} {'trades':>7}")
for k in sorted(STATE):
    print(f"{k:8} {STATE[k]:>10.2f} {nt[k]:>10.2f} "
          f"{round(nt[k]-STATE[k],2):>10.2f} {nc[k]:>7}")
print(f"{'TOTAL':8} {STATE_TOTAL:>10.2f} {tot_new:>10.2f} "
      f"{round(tot_new-STATE_TOTAL,2):>10.2f} {len(union):>7}")
print(f"union ex-top-3: {ex1} (top3 {top3_1}) | incumbent {ex0} (top3 {top3_0})")
print(f"August union: Rs{nt['2026-08']} (incumbent Rs1,111.86, slice Rs{lb_aug})")
print(f"October union: Rs{nt['2026-10']} | headroom Rs{round(nt['2026-10']-50000,2)}")

print("\n=== SATURATION GATE (frozen SAT-33) ===")
ga = tot_new > STATE_TOTAL
gb = all(v > 0 for v in nt.values())
gc = nt["2026-10"] >= 50000
gd = ex1 >= ex0
ge = a_ok and b_ok and c_ok and ca_ok and lb_tot > pl_tot and lb_exp > pl_exp
print(f"(a) total rises: {tot_new} > {STATE_TOTAL} -> {ga}")
print(f"(b) all ten months > 0: {gb} (min {min(nt.values())} in "
      f"{min(nt, key=nt.get)})")
print(f"(c) October >= 50,000: {nt['2026-10']} -> {gc}")
print(f"(d) ex-top-3 not worse: {ex1} >= {ex0} -> {gd}")
print(f"(e) anchors/audit/placebo: A {a_ok}, B {b_ok}, C {c_ok}, CA {ca_ok}, "
      f"component {lb_tot} > placebo {pl_tot} and exp {lb_exp} > "
      f"{pl_exp} -> {ge}")
banked = all([ga, gb, gc, gd, ge])
print("BANKED:", banked)

if banked:
    with open(f"{BASE}/stocks_engine_sat33_r2lowband_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["leg", "symbol", "date", "direction",
                           "entry_time", "entry", "exit_reason", "exit_price",
                           "exit_time", "net_rs", "R", "reaction_ret_pct", "note"])
        w.writeheader()
        for t in sorted(low, key=lambda x: (x["date"], x["symbol"])):
            w.writerow(dict(t, leg="R2-LOWBAND"))
    print("wrote stocks_engine_sat33_r2lowband_trades.csv (new component dump)")

json.dump({"anchors": {"A": a_ok, "B": b_ok, "C": c_ok, "CA": ca_ok},
           "fix": "SAT-33-R2-LOWBAND (6th component candidate: reaction "
                  "band [2.0%,2.5%) follow at R+2, T125/S050, RF-1, P2F "
                  "exclusions ASTRAL/HINDUNILVR + HINDALCO-LONG)",
           "fix_id": "SAT-33-R2-LOWBAND",
           "component": {"trades": len(low), "net": lb_tot, "h1": lb_h1,
                         "h2": lb_h2, "exp": lb_exp,
                         "win": sum(1 for t in low if t["net_rs"] > 0),
                         "breadth": lb_breadth, "august_slice": lb_aug,
                         "october_slice": lb_oct,
                         "placebo_frozen_subset": pl_tot,
                         "placebo_exp": pl_exp,
                         "placebo_beaten_per_trade": lb_exp > pl_exp},
           "new_month_table": nt, "new_total": tot_new,
           "new_trades": len(union), "banked": banked,
           "deltas": {k: round(nt[k] - STATE[k], 2) for k in STATE},
           "ex_top3_before": ex0, "ex_top3_after": ex1,
           "top3_before": top3_0, "top3_after": top3_1,
           "legs": {"a_total": ga, "b_all_green": gb, "c_oct": gc,
                    "d_extop3": gd, "e_controls": ge},
           "oct_headroom_after": round(nt["2026-10"] - 50000, 2),
           "august_after": nt["2026-08"]},
          open(f"{BASE}/stocks_engine_sat33_result.json", "w"), indent=1)
print("\nwrote stocks_engine_sat33_result.json")
