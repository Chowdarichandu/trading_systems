#!/usr/bin/env python3
"""ENGINE SAT-13 DIAGNOSIS (no scoring, no banking — diagnosis only).
Two candidate directions weighed at the CURRENT book:
(1) BOOK-WIDE direction-slice scan — every (comp x stock x dir) slice
    across all four components, negative in a thin month (Apr/Jun/Jul/
    Aug) AND negative full-period, October slice <= Rs917.03 (headroom).
(2) P2F-R2 — P2F's information axis extended one day: enter at the
    R+2 open in the reaction direction (2.5% band, T125/S050, 15:10),
    built with the audited stocks_tuning_event.py machinery verbatim
    (same candidate generation, replay, net_of). Controls: halves +
    opposite-direction placebo on identical entries.
Anchor: incumbent union == state (779 tr / +153,263.52 / month table /
ex-top-3 38,278.28). Paper, real Rs0, per 100 shares, Rs40/trade."""
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

STATE = {"2026-01": 14722.77, "2026-02": 7816.34, "2026-03": 18739.16,
         "2026-04": 7744.23, "2026-05": 27400.76, "2026-06": 4105.67,
         "2026-07": 3092.38, "2026-08": 1182.43, "2026-09": 17542.75,
         "2026-10": 50917.03}
STATE_TOTAL, STATE_TRADES, STATE_EXTOP3 = 153263.52, 779, 38278.28
HEADROOM = 917.03
THIN = ["2026-04", "2026-06", "2026-07", "2026-08"]

# ---------- incumbent book ----------
inv = [{"date": t["date"], "stock": t["stock"], "comp": "INV-LONG",
        "dir": t["dir"], "net": t["net"]}
       for t in M1.load_inv_long()
       if not wk(t["date"]) and t["stock"] != "BDL"]
n4 = [{"date": t["date"], "stock": t["stock"], "comp": "N4-V3",
       "dir": t["dir"], "net": t["net"]}
      for t in M1.load_n4()
      if not wk(t["date"]) and t["stock"] != "ASTRAL"]
p2f = [{"date": t["date"], "stock": t["stock"], "comp": "P2F",
        "dir": t["dir"], "net": t["net"], "R": t["R"]}
       for t in M1.load_p2f(2.5)
       if not wk(t["date"]) and t["stock"] != "ASTRAL"
       and t["stock"] != "HINDUNILVR"]
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
book = inv + n4 + p2f + f4

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
anchor_ok = (bt == STATE
             and round(sum(t["net"] for t in book), 2) == STATE_TOTAL
             and len(book) == STATE_TRADES and ex0 == STATE_EXTOP3)
print(f"ANCHOR: union == state: {anchor_ok} | trades {len(book)} total "
      f"{round(sum(t['net'] for t in book),2)} ex-top-3 {ex0} (top3 {top3_0})")
for comp, rows in (("INV-LONG", inv), ("N4-V3", n4), ("P2F", p2f), ("F4", f4)):
    print(f"  {comp}: {len(rows)} tr / {round(sum(t['net'] for t in rows),2)}")
assert anchor_ok, "ANCHOR FAILED"

# ---------- (1) book-wide direction-slice scan ----------
slices = defaultdict(lambda: {"n": 0, "net": 0.0, "win": 0,
                              "months": defaultdict(lambda: [0, 0.0])})
for t in book:
    s = slices[(t["comp"], t["stock"], t["dir"])]
    s["n"] += 1; s["net"] += t["net"]; s["win"] += 1 if t["net"] > 0 else 0
    s["months"][t["date"][:7]][0] += 1
    s["months"][t["date"][:7]][1] += t["net"]
cands = []
for (comp, stock, d), s in sorted(slices.items()):
    full = round(s["net"], 2)
    if full >= 0: continue
    oct_slice = round(s["months"]["2026-10"][1], 2)
    if oct_slice > HEADROOM: continue
    for th in THIN:
        tn, tv = s["months"][th]
        tv = round(tv, 2)
        if tn >= 1 and tv < 0:
            cands.append({"comp": comp, "stock": stock, "dir": d,
                          "thin_month": th, "thin_n": tn, "thin_net": tv,
                          "full_n": s["n"], "full_net": full,
                          "win": s["win"], "oct_slice": oct_slice})
cands.sort(key=lambda c: c["thin_net"])
print(f"\n(1) SLICE SCAN: {len(cands)} qualifying (comp x stock x dir) "
      f"slices [thin-month<0 AND full<0 AND Oct slice <= {HEADROOM}]:")
for c in cands:
    print(f"  {c['comp']:8} {c['stock']:12} {c['dir']:5} thin {c['thin_month']} "
          f"{c['thin_n']} tr {c['thin_net']:>10.2f} | full {c['full_n']} tr "
          f"{c['full_net']:>10.2f} (win {c['win']}) | Oct slice {c['oct_slice']}")

# ---------- (2) P2F-R2 build (audited machinery, copied verbatim) ----------
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

# candidate generation — identical to stocks_tuning_event.py
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

cands25 = []   # incumbent-population candidates at the 2.5% band
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
    bars = spot.get(nd, [])
    if not bars: continue
    if abs(reaction_ret) < 2.5: continue
    cands25.append({"symbol": sym, "announce": e["announce"], "R": R,
                    "reaction_ret_pct": reaction_ret, "ri": ri,
                    "direction": "LONG" if reaction_ret > 0 else "SHORT"})

print(f"\n(2) P2F-R2: incumbent-population candidates at 2.5% band: "
      f"{len(cands25)} (incumbent P2F book trades: {len(p2f)})")
# construction anchor: the same candidate set must reproduce the
# incumbent P2F *candidate* population (39 book trades after wk/excl —
# here compare against M1 raw 2.5 subset before book filters)
raw25 = [t for t in M1.load_p2f(2.5)]
print(f"    M1 raw P2F@2.5 (pre-filter): {len(raw25)} trades")

def score_r2(cand, flip=False):
    sym = cand["symbol"]; spot, daily = stocks[sym]
    ri = cand["ri"]
    if ri + 2 >= len(daily): return None, "no R+2 in daily series"
    d2 = daily[ri + 2]["date"]
    bars = spot.get(d2, [])
    if not bars: return None, "no R+2 bars"
    direction = cand["direction"]
    if flip: direction = "SHORT" if direction == "LONG" else "LONG"
    entry = bars[0]["open"]
    r = replay(bars, 0, entry, direction, 1.25, 0.5)
    if r is None: return None, "replay failed"
    er, ep, et = r
    return {"symbol": sym, "date": d2, "direction": direction,
            "entry_time": "09:15", "entry": round(entry, 2),
            "exit_reason": er, "exit_price": round(ep, 2), "exit_time": et,
            "net_rs": net_of(direction, entry, ep), "R": cand["R"],
            "reaction_ret_pct": cand["reaction_ret_pct"],
            "note": f"P2F-R2 reaction {cand['R']} {cand['reaction_ret_pct']:+.2f}%"}, None

r2, r2_drop, plac, plac_drop = [], [], [], []
for c in cands25:
    t, why = score_r2(c)
    if t: r2.append(t)
    else: r2_drop.append({"symbol": c["symbol"], "R": c["R"], "why": why})
    t, why = score_r2(c, flip=True)
    if t: plac.append(t)
    else: plac_drop.append({"symbol": c["symbol"], "R": c["R"], "why": why})

def halves(trades, key="net_rs"):
    h1 = round(sum(t[key] for t in trades if t["date"] <= "2026-05-31"), 2)
    h2 = round(sum(t[key] for t in trades if t["date"] > "2026-05-31"), 2)
    return h1, h2

def summ(trades, label, key="net_rs"):
    tot = round(sum(t[key] for t in trades), 2)
    h1, h2 = halves(trades, key)
    win = sum(1 for t in trades if t[key] > 0)
    per = defaultdict(float)
    for t in trades: per[t["symbol"]] += t[key]
    breadth = sum(1 for v in per.values() if v > 0)
    mm, _ = mt([{"date": t["date"], "net": t[key]} for t in trades])
    print(f"  {label}: {len(trades)} tr / {tot} | H1 {h1} / H2 {h2} | "
          f"win {win}/{len(trades)} | exp "
          f"{round(tot/len(trades),2) if trades else 0} | breadth {breadth}")
    print(f"    months: {mm}")
    return tot, h1, h2, mm

print(f"  R2 built: {len(r2)} trades; dropped: {r2_drop}")
r2_tot, r2_h1, r2_h2, r2_months = summ(r2, "P2F-R2 standalone (raw)")
pl_tot, pl_h1, pl_h2, _ = summ(plac, "PLACEBO (opposite dir, same entries)")
r2_wk = [t for t in r2 if wk(t["date"])]
print(f"  R2 weekend-dated trades (RF-1 would drop): {len(r2_wk)} "
      f"{[(t['symbol'], t['date']) for t in r2_wk]}")
r2f = [t for t in r2 if not wk(t["date"])]
r2f_tot, _, _, r2f_months = summ(r2f, "P2F-R2 standalone (RF-1 filtered)")
p2f_keys = {(t["stock"], t["date"]) for t in p2f}
ov = [(t["symbol"], t["date"]) for t in r2f if (t["symbol"], t["date"]) in p2f_keys]
print(f"  overlap (date,stock) vs incumbent P2F book: {len(ov)} {ov}")
# timing audit: every R2 date is exactly the 2nd trading day after R
bad = []
for t in r2:
    _, daily = stocks[t["symbol"]]
    didx = {d["date"]: i for i, d in enumerate(daily)}
    if didx[t["R"]] + 2 >= len(daily) or daily[didx[t["R"]] + 2]["date"] != t["date"]:
        bad.append((t["symbol"], t["R"], t["date"]))
print(f"  timing audit (date == R+2 trading day, entry 09:15 open): "
      f"violations={len(bad)} {bad[:5]}")
# exclusions-scoped variant (disclosed): ASTRAL + HINDUNILVR out, as P2F
r2x = [t for t in r2f if t["symbol"] not in ("ASTRAL", "HINDUNILVR")]
r2x_tot, r2x_h1, r2x_h2, r2x_months = summ(r2x, "P2F-R2 (RF-1 + P2F-scoped name excl)")

def union_months(extra):
    u = book + [{"date": t["date"], "stock": t["symbol"], "comp": "P2F-R2",
                 "dir": t["direction"], "net": t["net_rs"]} for t in extra]
    um, _ = mt(u)
    exu, _ = extop3(u)
    return um, round(sum(t["net"] for t in u), 2), len(u), exu

for label, extra in (("union + R2 (RF-1)", r2f),
                     ("union + R2 (RF-1 + name excl)", r2x)):
    um, ut, un, ux = union_months(extra)
    print(f"  {label}: total {ut} ({un} tr), ex-top-3 {ux}, "
          f"min month {min(um.values())}, Oct {um['2026-10']}, Aug {um['2026-08']}")

json.dump({"anchor_ok": anchor_ok,
           "slice_candidates": cands,
           "r2": {"n": len(r2), "total": r2_tot, "h1": r2_h1, "h2": r2_h2,
                  "months": r2_months, "dropped": r2_drop,
                  "placebo_total": pl_tot, "placebo_h1": pl_h1,
                  "placebo_h2": pl_h2,
                  "rf1_n": len(r2f), "rf1_total": r2f_tot,
                  "rf1_months": r2f_months,
                  "overlap_vs_p2f": ov, "audit_violations": len(bad),
                  "excl_variant_total": r2x_tot,
                  "excl_variant_months": r2x_months,
                  "trades": r2f}},
          open(f"{BASE}/stocks_engine_sat13_diag.json", "w"), indent=1)
print("\nwrote stocks_engine_sat13_diag.json")
