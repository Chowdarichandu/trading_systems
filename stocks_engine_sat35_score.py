#!/usr/bin/env python3
"""ENGINE SAT-35 SCORE: P2F-MIDBAND as 7th component, frozen in
stocks_engine_frozen.md (SAT-35 section) BEFORE this ran. Anchors:
(A) incumbent union (SIX components) == state (663 tr / +197,607.74
/ month table / ex-top-3 72,518.25), per book law; (B) frozen
midband set == the diagnosis set (sat35_diag.json) exactly, with
the construction anchor re-verified (lag+1 machinery == tuning
dump P2F leg on BOTH verified slices: >=2.5% 39/39 AND [2.0%,2.5%)
9/9, start-offset 1); (C) timing audit 0 + overlap vs ALL incumbent
reaction components (P2F, P2F-R2, P2F-LOWBAND, R2-LOWBAND,
R2-MIDBAND, N4-V3) == 0; (D) placebo on the frozen subset + the
full Lesson 21 test (beat placebo in total AND per-trade AND clear
zero expectancy); ex-carrier = component net excluding its single
best trade.
Gate (frozen SAT-35): bank iff (a) union total > 197,607.74;
(b) all ten months > 0 AND August >= 100; (c) October >= 50,000;
(d) ex-top-3 not worse than 72,518.25; (e) anchors/audit pass AND
placebo beaten per (D). Paper, real Rs0, per 100 shares, Rs40/trade,
home 25."""
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
               "dir": r["dir"], "net": float(r["net"])})
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
            [(k, round(v, 2)) for k, v in top3])

bt, _ = mt(book)
ex0, top3_0 = extop3(book)
a_ok = (bt == STATE and round(sum(t["net"] for t in book), 2) == STATE_TOTAL
        and len(book) == STATE_TRADES and ex0 == STATE_EXTOP3)
print(f"ANCHOR A: incumbent == state: {a_ok} | {len(book)} tr / "
      f"{round(sum(t['net'] for t in book),2)} / ex-top-3 {ex0}")
print(f"  components: INV {len(inv)} / N4 {len(n4)} / P2F {len(p2f)} / "
      f"F4 {len(f4)} / R2 {len(r2)} / R2LOW {len(r2low)}")
assert a_ok, "ANCHOR A FAILED -- do not judge"

# ---------- midband rebuild (verbatim SAT-32 lag+1 machinery) ----------
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

def replay(candles, entry, direction, tgt_pct, stp_pct, start):
    sign = 1 if direction == "LONG" else -1
    target = entry * (1 + sign * tgt_pct / 100)
    stop = entry * (1 - sign * stp_pct / 100)
    last = None
    for j in range(start, len(candles)):
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

cands_ge25, cands_low, cands_mid = [], [], []
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
    elif abs(reaction_ret) >= 2.0: cands_low.append(c)
    elif abs(reaction_ret) >= 1.5: cands_mid.append(c)

def score_lag1(cand, start, flip=False):
    sym = cand["symbol"]; spot, daily = stocks[sym]
    d1 = daily[cand["ri"] + 1]["date"]
    bars = spot.get(d1, [])
    if not bars: return None
    direction = cand["direction"]
    if flip: direction = "SHORT" if direction == "LONG" else "LONG"
    entry = bars[0]["open"]
    r = replay(bars, entry, direction, 1.25, 0.5, start)
    if r is None: return None
    er, ep, et = r
    return {"symbol": sym, "date": d1, "direction": direction,
            "entry_time": "09:15", "entry": round(entry, 2),
            "exit_reason": er, "exit_price": round(ep, 2), "exit_time": et,
            "net_rs": net_of(direction, entry, ep), "R": cand["R"],
            "reaction_ret_pct": cand["reaction_ret_pct"],
            "note": f"P2F-MIDBAND reaction {cand['R']} {cand['reaction_ret_pct']:+.2f}%"}

def frozen_filter(raw):
    return [t for t in raw
            if not wk(t["date"]) and t["symbol"] not in ("ASTRAL", "HINDUNILVR")
            and not (t["symbol"] == "HINDALCO" and t["direction"] == "LONG")]

# construction anchor re-verified in the score pass (both slices)
dump = {}
for r in rd("stocks_tuning_event_V1_combined_trades.csv"):
    if r["leg"] == "P2F":
        dump[(r["date"], r["symbol"], r["direction"])] = (
            round(float(r["net_rs"]), 2), r["exit_reason"])

def matches(built):
    return sum(1 for t in built
               if dump.get((t["date"], t["symbol"], t["direction"]),
                           (None, None))[0] is not None
               and abs(dump[(t["date"], t["symbol"], t["direction"])][0]
                       - t["net_rs"]) < 0.011
               and dump[(t["date"], t["symbol"], t["direction"])][1]
               == t["exit_reason"])

b25 = [t for t in (score_lag1(c, 1) for c in cands_ge25) if t]
blow = [t for t in (score_lag1(c, 1) for c in cands_low) if t]
m25, mlow = matches(b25), matches(blow)
ca_ok = m25 == len(b25) == 39 and mlow == len(blow) == 9
print(f"CONSTRUCTION ANCHOR (score pass): lag+1 machinery == tuning "
      f"dump P2F leg: >=2.5% {m25}/{len(b25)}, [2.0,2.5) {mlow}/{len(blow)} "
      f"-> {ca_ok}")
assert ca_ok, "CONSTRUCTION ANCHOR FAILED -- do not judge"

mid = frozen_filter([t for t in (score_lag1(c, 1) for c in cands_mid) if t])
diag = json.load(open(f"{BASE}/stocks_engine_sat35_diag.json"))
diag_set = sorted((t["date"], t["symbol"], t["direction"], t["net_rs"])
                  for t in diag["midband_trades"])
score_set = sorted((t["date"], t["symbol"], t["direction"], t["net_rs"])
                   for t in mid)
b_ok = len(cands_mid) == 7 and score_set == diag_set and len(mid) == 6 \
    and diag["construction_anchor"]["ge25_matches"] == 39 \
    and diag["construction_anchor"]["lowband_matches"] == 9
print(f"ANCHOR B: midband candidates {len(cands_mid)} (==7), frozen set "
      f"== diagnosis set: {score_set == diag_set} | frozen trades {len(mid)}")
assert b_ok, "ANCHOR B FAILED -- do not judge"

bad = []
for t in mid:
    _, daily = stocks[t["symbol"]]
    didx = {d["date"]: i for i, d in enumerate(daily)}
    if didx[t["R"]] + 1 >= len(daily) or daily[didx[t["R"]] + 1]["date"] != t["date"]:
        bad.append((t["symbol"], t["R"], t["date"]))
p2f_keys = {(t["stock"], t["date"]) for t in p2f}
r2_keys = {(t["stock"], t["date"]) for t in r2}
d32 = json.load(open(f"{BASE}/stocks_engine_sat32_diag.json"))
lb_keys = {(t["symbol"], t["date"]) for t in d32["lowband_trades"]}
r2low_keys = {(t["stock"], t["date"]) for t in r2low}
d34 = json.load(open(f"{BASE}/stocks_engine_sat34_diag.json"))
r2mid_keys = {(t["symbol"], t["date"]) for t in d34["midband_trades"]}
n4_keys = {(t["stock"], t["date"]) for t in n4}
ov = {"P2F": [(t["symbol"], t["date"]) for t in mid if (t["symbol"], t["date"]) in p2f_keys],
      "P2F-R2": [(t["symbol"], t["date"]) for t in mid if (t["symbol"], t["date"]) in r2_keys],
      "P2F-LOWBAND": [(t["symbol"], t["date"]) for t in mid if (t["symbol"], t["date"]) in lb_keys],
      "R2-LOWBAND": [(t["symbol"], t["date"]) for t in mid if (t["symbol"], t["date"]) in r2low_keys],
      "R2-MIDBAND": [(t["symbol"], t["date"]) for t in mid if (t["symbol"], t["date"]) in r2mid_keys],
      "N4-V3": [(t["symbol"], t["date"]) for t in mid if (t["symbol"], t["date"]) in n4_keys]}
c_ok = len(bad) == 0 and all(len(v) == 0 for v in ov.values())
print(f"ANCHOR C: timing audit violations={len(bad)}, overlaps: "
      + " ".join(f"{k}={len(v)}" for k, v in ov.items()))
assert c_ok, "ANCHOR C FAILED -- do not judge"

plac = frozen_filter([t for t in (score_lag1(c, 1, flip=True) for c in cands_mid) if t])
pl_tot = round(sum(t["net_rs"] for t in plac), 2)
pl_exp = round(pl_tot / len(plac), 2) if plac else 0
print(f"placebo (frozen subset): {len(plac)} tr / {pl_tot} (exp {pl_exp})")
for t in sorted(plac, key=lambda x: (x["date"], x["symbol"])):
    print(f"   placebo {t['date']} {t['symbol']:10s} {t['direction']:5s} "
          f"{t['net_rs']:+9.2f} {t['exit_reason']}")

def halves(trades):
    return (round(sum(t["net_rs"] for t in trades if t["date"] <= "2026-05-31"), 2),
            round(sum(t["net_rs"] for t in trades if t["date"] > "2026-05-31"), 2))

mb_tot = round(sum(t["net_rs"] for t in mid), 2)
mb_h1, mb_h2 = halves(mid)
mb_exp = round(mb_tot / len(mid), 2)
mb_aug = round(sum(t["net_rs"] for t in mid if t["date"][:7] == "2026-08"), 2)
mb_oct = round(sum(t["net_rs"] for t in mid if t["date"][:7] == "2026-10"), 2)
mb_breadth = len({t["symbol"] for t in mid
                  if sum(x["net_rs"] for x in mid if x["symbol"] == t["symbol"]) > 0})
best = max(mid, key=lambda t: t["net_rs"])
mb_ex_carrier = round(mb_tot - best["net_rs"], 2)
print(f"\nP2F-MIDBAND (frozen): {len(mid)} tr / {mb_tot} | H1 {mb_h1} / "
      f"H2 {mb_h2} | exp {mb_exp} | win "
      f"{sum(1 for t in mid if t['net_rs'] > 0)}/{len(mid)} | breadth "
      f"{mb_breadth} | August slice {mb_aug} | October slice {mb_oct} | "
      f"best trade {best['symbol']} {best['date']} {best['net_rs']:+.2f} | "
      f"ex-carrier {mb_ex_carrier} | placebo {pl_tot} (exp {pl_exp}) "
      f"-> beaten total: {mb_tot > pl_tot}; beaten per-trade: "
      f"{mb_exp > pl_exp}; clears zero: {mb_exp > 0}")
for t in sorted(mid, key=lambda x: (x["date"], x["symbol"])):
    print(f"   real {t['date']} {t['symbol']:10s} {t['direction']:5s} "
          f"{t['net_rs']:+9.2f} {t['exit_reason']}")

union = book + [{"date": t["date"], "stock": t["symbol"],
                 "comp": "P2F-MIDBAND", "dir": t["direction"],
                 "net": t["net_rs"]} for t in mid]
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
print(f"August union: Rs{nt['2026-08']} (incumbent Rs666.78, slice Rs{mb_aug})")
print(f"October union: Rs{nt['2026-10']} | headroom Rs{round(nt['2026-10']-50000,2)}")

print("\n=== SATURATION GATE (frozen SAT-35) ===")
ga = tot_new > STATE_TOTAL
gb = all(v > 0 for v in nt.values()) and nt["2026-08"] >= 100
gc = nt["2026-10"] >= 50000
gd = ex1 >= ex0
ge = a_ok and b_ok and c_ok and ca_ok and mb_tot > pl_tot and mb_exp > pl_exp and mb_exp > 0
print(f"(a) total rises: {tot_new} > {STATE_TOTAL} -> {ga}")
print(f"(b) all ten months > 0 AND August >= 100: {gb} (min {min(nt.values())} in "
      f"{min(nt, key=nt.get)}; August {nt['2026-08']})")
print(f"(c) October >= 50,000: {nt['2026-10']} -> {gc}")
print(f"(d) ex-top-3 not worse: {ex1} >= {ex0} -> {gd}")
print(f"(e) anchors/audit/placebo (full L21 test): A {a_ok}, B {b_ok}, C {c_ok}, "
      f"CA {ca_ok}, component {mb_tot} > placebo {pl_tot}, exp {mb_exp} > "
      f"{pl_exp} and > 0 -> {ge}")
banked = all([ga, gb, gc, gd, ge])
print("BANKED:", banked)

if banked:
    with open(f"{BASE}/stocks_engine_sat35_p2fmidband_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["leg", "symbol", "date", "direction",
                           "entry_time", "entry", "exit_reason", "exit_price",
                           "exit_time", "net_rs", "R", "reaction_ret_pct", "note"])
        w.writeheader()
        for t in sorted(mid, key=lambda x: (x["date"], x["symbol"])):
            w.writerow(dict(t, leg="P2F-MIDBAND"))
    print("wrote stocks_engine_sat35_p2fmidband_trades.csv (new component dump)")

json.dump({"anchors": {"A": a_ok, "B": b_ok, "C": c_ok, "CA": ca_ok},
           "fix": "SAT-35-P2F-MIDBAND (7th component candidate: reaction "
                  "band [1.5%,2.0%) follow at R+1, T125/S050, RF-1, P2F "
                  "exclusions ASTRAL/HINDUNILVR + HINDALCO-LONG)",
           "fix_id": "SAT-35-P2F-MIDBAND",
           "component": {"trades": len(mid), "net": mb_tot, "h1": mb_h1,
                         "h2": mb_h2, "exp": mb_exp,
                         "win": sum(1 for t in mid if t["net_rs"] > 0),
                         "breadth": mb_breadth, "august_slice": mb_aug,
                         "october_slice": mb_oct,
                         "best_trade": {"date": best["date"],
                                        "symbol": best["symbol"],
                                        "direction": best["direction"],
                                        "net_rs": best["net_rs"]},
                         "ex_carrier": mb_ex_carrier,
                         "placebo_frozen_subset": pl_tot,
                         "placebo_exp": pl_exp,
                         "placebo_beaten_total": mb_tot > pl_tot,
                         "placebo_beaten_per_trade": mb_exp > pl_exp,
                         "clears_zero": mb_exp > 0},
           "new_month_table": nt, "new_total": tot_new,
           "new_trades": len(union), "banked": banked,
           "deltas": {k: round(nt[k] - STATE[k], 2) for k in STATE},
           "ex_top3_before": ex0, "ex_top3_after": ex1,
           "top3_before": top3_0, "top3_after": top3_1,
           "legs": {"a_total": ga, "b_all_green": gb, "c_oct": gc,
                    "d_extop3": gd, "e_controls": ge},
           "oct_headroom_after": round(nt["2026-10"] - 50000, 2),
           "august_after": nt["2026-08"]},
          open(f"{BASE}/stocks_engine_sat35_result.json", "w"), indent=1)
print("\nwrote stocks_engine_sat35_result.json")
