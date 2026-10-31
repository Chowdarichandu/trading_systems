#!/usr/bin/env python3
"""ENGINE SAT-34 DIAGNOSIS: R2-MIDBAND candidate -- reaction band
[1.5%,2.0%) entered at R+2 (the next grid cell down the band axis at
the lag where both living low cells sit). Diagnosis only: build the
candidate set with the verbatim SAT-13/33 event machinery, verify the
construction anchor (lag+2 >=2.5% == SAT-13 R2 dump 34/34), anchor
the SIX-component incumbent == state, score the frozen subset +
opposite-direction placebo, timing audit, mechanical overlaps vs
ALL incumbent reaction components (P2F, P2F-R2, P2F-LOWBAND frozen
set, R2-LOWBAND, N4-V3). NO gate verdict here -- the score pass
re-derives everything and asserts set equality with this diagnosis.
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
print(f"ANCHOR A: incumbent (6 comps) == state: {a_ok} | {len(book)} tr / "
      f"{round(sum(t['net'] for t in book),2)} / ex-top-3 {ex0}")
print(f"  components: INV {len(inv)} / N4 {len(n4)} / P2F {len(p2f)} / "
      f"F4 {len(f4)} / R2 {len(r2)} / R2LOW {len(r2low)}")
assert a_ok, "ANCHOR A FAILED -- do not judge"

# ---------- midband build (verbatim SAT-33 machinery) ----------
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

cands_mid, cands_ge25 = [], []
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
    elif 1.5 <= abs(reaction_ret) < 2.0: cands_mid.append(c)

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
            "note": f"R2-MIDBAND reaction {cand['R']} {cand['reaction_ret_pct']:+.2f}%"}

def frozen_filter(raw):
    return [t for t in raw
            if not wk(t["date"]) and t["symbol"] not in ("ASTRAL", "HINDUNILVR")
            and not (t["symbol"] == "HINDALCO" and t["direction"] == "LONG")]

# construction anchor: lag+2 >=2.5% == SAT-13 R2 dump (SAT-13 filter)
dump = {}
for r in rd("stocks_engine_sat13_p2fr2_trades.csv"):
    dump[(r["date"], r["symbol"], r["direction"])] = (
        round(float(r["net_rs"]), 2), r["exit_reason"])
b25 = [t for t in (score_lag2(c) for c in cands_ge25) if t]
b25 = [t for t in b25
       if not wk(t["date"]) and t["symbol"] not in ("ASTRAL", "HINDUNILVR")]
match = sum(1 for t in b25
            if dump.get((t["date"], t["symbol"], t["direction"]), (None, None))[0] is not None
            and abs(dump[(t["date"], t["symbol"], t["direction"])][0] - t["net_rs"]) < 0.011
            and dump[(t["date"], t["symbol"], t["direction"])][1] == t["exit_reason"])
ca_ok = len(b25) == len(dump) == 34 and match == 34
print(f"CONSTRUCTION ANCHOR: lag+2 >=2.5% matches SAT-13 R2 dump "
      f"{match}/{len(dump)} -> {ca_ok}")
assert ca_ok, "CONSTRUCTION ANCHOR FAILED -- do not judge"

raw_mid = [t for t in (score_lag2(c) for c in cands_mid) if t]
mid = frozen_filter(raw_mid)
plac_raw = [t for t in (score_lag2(c, flip=True) for c in cands_mid) if t]
plac = frozen_filter(plac_raw)

bad = []
for t in mid:
    _, daily = stocks[t["symbol"]]
    didx = {d["date"]: i for i, d in enumerate(daily)}
    if didx[t["R"]] + 2 >= len(daily) or daily[didx[t["R"]] + 2]["date"] != t["date"]:
        bad.append((t["symbol"], t["R"], t["date"]))
p2f_keys = {(t["stock"], t["date"]) for t in p2f}
r2_keys = {(t["stock"], t["date"]) for t in r2}
d32 = json.load(open(f"{BASE}/stocks_engine_sat32_diag.json"))
lb_keys = {(t["symbol"], t["date"]) for t in d32["lowband_trades"]}
r2low_keys = {(t["stock"], t["date"]) for t in r2low}
n4_keys = {(t["stock"], t["date"]) for t in n4}
ov = {"P2F": [(t["symbol"], t["date"]) for t in mid if (t["symbol"], t["date"]) in p2f_keys],
      "P2F-R2": [(t["symbol"], t["date"]) for t in mid if (t["symbol"], t["date"]) in r2_keys],
      "P2F-LOWBAND": [(t["symbol"], t["date"]) for t in mid if (t["symbol"], t["date"]) in lb_keys],
      "R2-LOWBAND": [(t["symbol"], t["date"]) for t in mid if (t["symbol"], t["date"]) in r2low_keys],
      "N4-V3": [(t["symbol"], t["date"]) for t in mid if (t["symbol"], t["date"]) in n4_keys]}
print(f"timing violations={len(bad)} | overlaps: "
      + " ".join(f"{k}={len(v)}" for k, v in ov.items()))
assert len(bad) == 0 and all(len(v) == 0 for v in ov.values()), "AUDIT FAILED"

def stats(trades):
    tot = round(sum(t["net_rs"] for t in trades), 2)
    months = {k: round(sum(t["net_rs"] for t in trades if t["date"][:7] == k), 2)
              for k in sorted(STATE)}
    per = defaultdict(float)
    for t in trades: per[t["symbol"]] += t["net_rs"]
    return {"trades": len(trades), "net": tot,
            "exp": round(tot / len(trades), 2) if trades else 0,
            "win": sum(1 for t in trades if t["net_rs"] > 0),
            "breadth": len([k for k, v in per.items() if v > 0]),
            "h1": round(sum(t["net_rs"] for t in trades if t["date"] <= "2026-05-31"), 2),
            "h2": round(sum(t["net_rs"] for t in trades if t["date"] > "2026-05-31"), 2),
            "months": months,
            "per_stock": {k: round(v, 2) for k, v in per.items()}}

ms, ps = stats(mid), stats(plac)
print(f"\nmidband candidates: {len(cands_mid)} | raw {len(raw_mid)} | "
      f"frozen {len(mid)} (dropped "
      f"{sorted((t['date'], t['symbol'], t['direction'], t['net_rs']) for t in raw_mid if t not in mid)})")
print(f"MIDBAND frozen: {ms['trades']} tr / {ms['net']} | exp {ms['exp']} | "
      f"win {ms['win']} | breadth {ms['breadth']} | H1 {ms['h1']} / H2 {ms['h2']}")
print(f"  months: {ms['months']}")
print(f"  August slice {ms['months']['2026-08']} | October slice {ms['months']['2026-10']}")
print(f"placebo frozen: {ps['trades']} tr / {ps['net']} | exp {ps['exp']} | "
      f"win {ps['win']} | H1 {ps['h1']} / H2 {ps['h2']}")
for t in sorted(mid, key=lambda x: (x["date"], x["symbol"])):
    print(f"   real {t['date']} {t['symbol']:10s} {t['direction']:5s} "
          f"{t['net_rs']:+9.2f} {t['exit_reason']} (R {t['R']} {t['reaction_ret_pct']:+.2f}%)")

json.dump({"construction_anchor": {"ge25_candidates": len(cands_ge25),
                                   "r2_dump_trades": len(dump), "matches": match},
           "midband_candidates": len(cands_mid), "midband_raw": len(raw_mid),
           "placebo_raw": len(plac_raw),
           "midband_trades": sorted(mid, key=lambda x: (x["date"], x["symbol"])),
           "placebo_trades": sorted(plac, key=lambda x: (x["date"], x["symbol"])),
           "midband_stats": ms, "placebo_stats": ps,
           "timing_violations": len(bad),
           "overlaps": {k: len(v) for k, v in ov.items()}},
          open(f"{BASE}/stocks_engine_sat34_diag.json", "w"), indent=1)
print("\nwrote stocks_engine_sat34_diag.json")
