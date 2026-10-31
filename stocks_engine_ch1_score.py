#!/usr/bin/env python3
"""ENGINE CH-1: challenger P2F-PROFILE vs incumbent.
Spec frozen FIRST in stocks_engine_frozen.md (section CH-1).
Steps: (1) incumbent rebuild anchor == state (138,631.32 / 906);
(2) P2F construction anchor: follow-direction T125/S050 on the
>=2.0% event set == T2 anchor (48 trades / +12,835.88);
(3) P2F-PROFILE (causal profile direction, T125/S065) + permutation
placebo; (4) assembly swap, frozen gate (a)-(e), ex-top-3 both books.
Paper only, real Rs0, per 100 shares provisional, Rs40/trade."""
import csv, json, random, sys
from collections import defaultdict
from datetime import date, timedelta
import importlib.util

BASE = "/home/hatch/workspace/trading"
sys.path.insert(0, BASE)
def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m
M1 = load_mod("M1", f"{BASE}/stocks_M1.py")

QTY, COST = 100, 40.0
ALL_LO, ALL_HI = "2026-01-01", "2026-10-28"
HOME_BASE = f"{BASE}/data/progressive"
HOME_SYMBOLS = ["GODREJCP","GLENMARK","ITC","RECLTD","TVSMOTOR","UNITDSPR","OBEROIRLTY",
           "NTPC","INDUSTOWER","KALYANKJIL","HDFCBANK","NHPC","PFC","IRCTC","WIPRO",
           "NATIONALUM","VEDL","HINDCOPPER","HINDZINC","HINDALCO","TATASTEEL",
           "ASTRAL","BDL","OIL","HINDUNILVR"]
MONTHS = [f"2026-{i:02d}" for i in range(1, 11)]
STATE_MONTHS = {"2026-01": 11378.22, "2026-02": 5125.86, "2026-03": 19116.26,
                "2026-04": 1464.36, "2026-05": 29377.98, "2026-06": 172.76,
                "2026-07": 3196.63, "2026-08": 185.69, "2026-09": 18041.54,
                "2026-10": 50572.02}

def wk(d): return date.fromisoformat(d).weekday() >= 5
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))

# ---------- (1) incumbent anchor ----------
inv = [t for t in M1.load_inv_long() if not wk(t["date"]) and t["stock"] != "BDL"]
n4  = [t for t in M1.load_n4() if not wk(t["date"]) and t["stock"] != "ASTRAL"]
p2f25 = [t for t in M1.load_p2f(2.5) if not wk(t["date"])
         and t["stock"] != "ASTRAL" and t["stock"] != "HINDUNILVR"]
f4  = [{"date": r["date"], "stock": r["symbol"], "comp": "F4", "net": float(r["net"])}
       for r in rd("stocks_engine_oc4_f4s080_trades.csv")
       if not wk(r["date"]) and r["setup"] != "setup3_bounce_rejection"]

def month_table(trades):
    m = {k: 0.0 for k in MONTHS}
    for t in trades: m[t["date"][:7]] = round(m.get(t["date"][:7], 0.0) + t["net"], 2)
    return m

def per_stock(trades):
    ps = defaultdict(float)
    for t in trades: ps[t["stock"]] += t["net"]
    return {k: round(v, 2) for k, v in ps.items()}

def ex_top3(trades):
    ps = per_stock(trades)
    tot = round(sum(ps.values()), 2)
    top = sorted(((v, k) for k, v in ps.items() if v > 0), reverse=True)[:3]
    return {"total": tot, "ex_top3": round(tot - sum(v for v, _ in top), 2),
            "top3": [(k, v) for v, k in top]}

incumbent = inv + n4 + p2f25 + f4
im = month_table(incumbent)
inc_tot = round(sum(t["net"] for t in incumbent), 2)
anchor_inc = (im == STATE_MONTHS and inc_tot == 138631.32 and len(incumbent) == 906)
print("INCUMBENT ANCHOR:", anchor_inc, f"| trades {len(incumbent)} total {inc_tot}")
assert anchor_inc, f"incumbent anchor FAIL: {im} {inc_tot} {len(incumbent)}"
inc_x3 = ex_top3(incumbent)
print("incumbent ex-top3:", inc_x3)

# ---------- P2F machinery (verbatim construction from stocks_T2.py) ----------
def load_stock(sym):
    spot, daily = {}, []
    with open(f"{HOME_BASE}/{sym}/spot_5m.csv") as f:
        for r in csv.DictReader(f):
            d = r["timestamp"][:10]
            spot.setdefault(d, []).append({"timestamp": r["timestamp"][:19], "time": r["timestamp"][11:16],
                "open": float(r["open"]), "high": float(r["high"]), "low": float(r["low"]), "close": float(r["close"])})
    with open(f"{HOME_BASE}/{sym}/spot_daily.csv") as f:
        for r in csv.DictReader(f):
            daily.append({"date": r["date"][:10], "open": float(r["open"]), "high": float(r["high"]),
                          "low": float(r["low"]), "close": float(r["close"])})
    daily.sort(key=lambda x: x["date"])
    for d in spot: spot[d].sort(key=lambda x: x["timestamp"])
    return spot, daily

STOCKS = {s: load_stock(s) for s in HOME_SYMBOLS}

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
        if r["event_type"] != "results" or r["stock"] not in HOME_SYMBOLS: continue
        ev = date.fromisoformat(r["event_date"][:10])
        react = date.fromisoformat(r["reaction_date"][:10]) if r["reaction_date"] else None
        eff = react if (react and ev <= react <= ev + timedelta(days=7)) else ev
        ds = eff.isoformat()
        if ALL_LO <= ds <= ALL_HI:
            events.append({"symbol": r["stock"], "announce": r["event_date"][:10], "R": ds})
events.sort(key=lambda e: (e["symbol"], e["R"]))

cands = []  # >=2.0% event set, with causal outcome fields
for e in events:
    sym, R = e["symbol"], e["R"]
    spot, daily = STOCKS[sym]
    didx = {d["date"]: i for i, d in enumerate(daily)}
    if R not in didx: continue
    ri = didx[R]
    if ri == 0 or ri + 1 >= len(daily): continue
    reaction_ret = round((daily[ri]["close"] / daily[ri - 1]["close"] - 1) * 100, 2)
    nd = daily[ri + 1]["date"]
    if nd > ALL_HI: continue
    bars = spot.get(nd, [])
    if not bars: continue
    if abs(reaction_ret) < 2.0: continue
    r1_ret = round((daily[ri + 1]["close"] / daily[ri]["close"] - 1) * 100, 2)
    outcome = None
    if r1_ret != 0:
        outcome = "CONTINUED" if (r1_ret > 0) == (reaction_ret > 0) else "FADED"
    cands.append({"symbol": sym, "announce": e["announce"], "R": R,
                  "reaction_ret_pct": reaction_ret, "trade_date": nd,
                  "entry": bars[0]["open"], "outcome": outcome, "r1_ret_pct": r1_ret})
cands.sort(key=lambda c: (c["symbol"], c["R"]))
print(f">=2.0% candidates: {len(cands)}")

def score(cand, direction, tgt, stp):
    spot, _ = STOCKS[cand["symbol"]]
    r = replay(spot[cand["trade_date"]], 0, cand["entry"], direction, tgt, stp)
    if r is None: return None
    er, ep, et = r
    return {"symbol": cand["symbol"], "date": cand["trade_date"], "R": cand["R"],
            "reaction_ret_pct": cand["reaction_ret_pct"], "direction": direction,
            "entry_time": "09:15", "entry": round(cand["entry"], 2),
            "exit_reason": er, "exit_price": round(ep, 2), "exit_time": et,
            "net": net_of(direction, cand["entry"], ep)}

# ---------- (2) construction anchor: follow @ T125/S050 == 48 / +12,835.88 ----------
anch = [t for c in cands for t in [score(c, "LONG" if c["reaction_ret_pct"] > 0 else "SHORT", 1.25, 0.5)] if t]
anch_net = round(sum(t["net"] for t in anch), 2)
print(f"CONSTRUCTION ANCHOR follow T125/S050: {len(anch)} trades / {anch_net} (expect 48 / 12835.88)")
assert len(anch) == 48 and abs(anch_net - 12835.88) < 0.01, "CONSTRUCTION ANCHOR FAIL"

# ---------- (3) profile decisions (causal) ----------
by_sym = defaultdict(list)
for c in cands: by_sym[c["symbol"]].append(c)
for s in by_sym: by_sym[s].sort(key=lambda c: c["R"])

def decide(hist_owner_cands, cand, upto_R, trade_date):
    """Profile decision for `cand` using hist_owner_cands' history (same rule
    for real=own history and placebo=donor history). Returns (mode, n_classified,
    n_cont, n_fade). Audit asserts live here: every history input strictly
    prior (R_prior < R) with outcome date (= prior trade_date) < trade_date."""
    cont = fade = 0
    for h in hist_owner_cands:
        if h["R"] >= upto_R: break
        assert h["trade_date"] < trade_date, "AUDIT FAIL: outcome not known before entry"
        if h["outcome"] == "CONTINUED": cont += 1
        elif h["outcome"] == "FADED": fade += 1
    n = cont + fade
    if n >= 2 and fade / n >= 2 / 3: return "FADE", n, cont, fade
    if n >= 2 and cont / n >= 2 / 3: return "FOLLOW", n, cont, fade
    return "DEFAULT_FOLLOW", n, cont, fade

perm_syms = sorted(HOME_SYMBOLS)
random.Random(20261031).shuffle(perm_syms)
DONOR = {s: perm_syms[i] for i, s in enumerate(sorted(HOME_SYMBOLS))}
print("placebo donor map:", DONOR)

def build_profile_trades(donor_map=None):
    trades, audit_v = [], 0
    for c in cands:
        hist = by_sym[c["symbol"]] if donor_map is None else by_sym[donor_map[c["symbol"]]]
        mode, n, cont, fade = decide(hist, c, c["R"], c["trade_date"])
        follow_dir = "LONG" if c["reaction_ret_pct"] > 0 else "SHORT"
        direction = follow_dir if mode != "FADE" else ("SHORT" if follow_dir == "LONG" else "LONG")
        t = score(c, direction, 1.25, 0.65)
        if t is None: continue
        t.update({"mode": mode, "n_prior": n, "n_cont": cont, "n_fade": fade,
                  "donor": c["symbol"] if donor_map is None else donor_map[c["symbol"]]})
        # independent audit of this trade
        ok = (t["date"] > t["R"] and t["entry_time"] == "09:15")
        re_mode, *_ = decide(hist, c, c["R"], c["trade_date"])
        ok = ok and re_mode == mode
        expect_dir = follow_dir if re_mode != "FADE" else ("SHORT" if follow_dir == "LONG" else "LONG")
        ok = ok and t["direction"] == expect_dir
        if not ok: audit_v += 1
        trades.append(t)
    return trades, audit_v

prof_all, audit_v = build_profile_trades()
plac_all, audit_vp = build_profile_trades(DONOR)
print(f"profile trades (pre-RF1): {len(prof_all)} audit_v={audit_v}; placebo: {len(plac_all)} audit_v={audit_vp}")
assert audit_v == 0 and audit_vp == 0

prof = [t for t in prof_all if not wk(t["date"])]
plac = [t for t in plac_all if not wk(t["date"])]
print(f"after RF-1 weekend drop: profile {len(prof)} (dropped {len(prof_all)-len(prof)}), "
      f"placebo {len(plac)} (dropped {len(plac_all)-len(plac)})")

def block(trades):
    tot = round(sum(t["net"] for t in trades), 2)
    h1 = round(sum(t["net"] for t in trades if t["date"] <= "2026-05-31"), 2)
    h2 = round(sum(t["net"] for t in trades if t["date"] > "2026-05-31"), 2)
    octv = round(sum(t["net"] for t in trades if t["date"][:7] == "2026-10"), 2)
    ps = per_stock([{"stock": t["symbol"], "net": t["net"], "date": t["date"]} for t in trades])
    return {"trades": len(trades), "net": tot, "H1": h1, "H2": h2, "october": octv,
            "breadth": sum(1 for v in ps.values() if v > 0), "stocks_traded": len(ps),
            "expectancy": round(tot / len(trades), 2) if trades else 0.0,
            "win_pct": round(100 * sum(1 for t in trades if t["net"] > 0) / len(trades), 1) if trades else 0.0,
            "months": month_table([{"date": t["date"], "net": t["net"]} for t in trades]),
            "per_stock": ps}

prof_b, plac_b = block(prof), block(plac)
prof_x3 = ex_top3([{"stock": t["symbol"], "net": t["net"], "date": t["date"]} for t in prof])
flips = [t for t in prof if t["mode"] == "FADE"]
print("P2F-PROFILE standalone:", {k: prof_b[k] for k in ("trades","net","H1","H2","october","breadth","expectancy","win_pct")})
print("  months:", prof_b["months"])
print("  flipped-to-FADE trades:", len(flips), "net", round(sum(t['net'] for t in flips), 2),
      "| rule-FOLLOW:", sum(1 for t in prof if t['mode']=='FOLLOW'),
      "| default:", sum(1 for t in prof if t['mode']=='DEFAULT_FOLLOW'))
print("PLACEBO standalone:", {k: plac_b[k] for k in ("trades","net","H1","H2","october")})
print("profile ex-top3:", prof_x3)

# ---------- (4) assembly + gate ----------
chal_comp = [{"date": t["date"], "stock": t["symbol"], "comp": "P2F-PROFILE", "net": t["net"]} for t in prof]
challenger = inv + n4 + f4 + chal_comp
cm = month_table(challenger)
c_tot = round(sum(t["net"] for t in challenger), 2)
chal_x3 = ex_top3(challenger)
plac_comp = [{"date": t["date"], "stock": t["symbol"], "comp": "P2F-PLACEBO", "net": t["net"]} for t in plac]
book_plac = inv + n4 + f4 + plac_comp
bp_tot = round(sum(t["net"] for t in book_plac), 2)

gate = {
 "a_all_months_green": all(v > 0 for v in cm.values()),
 "b_total_higher": c_tot > 138631.32,
 "c_october_floor": cm["2026-10"] >= 50000,
 "d_ex_top3_better": chal_x3["ex_top3"] > inc_x3["ex_top3"],
 "e_audit_and_placebo": (audit_v == 0 and prof_b["net"] > plac_b["net"]),
}
print("\nCHALLENGER month table:", cm)
print("challenger total:", c_tot, "trades:", len(challenger))
print("challenger ex-top3:", chal_x3, "| incumbent ex-top3:", inc_x3)
print("assembled-with-placebo total:", bp_tot)
print("GATE:", gate, "=> ADOPTED" if all(gate.values()) else "=> REJECTED")

with open(f"{BASE}/stocks_engine_ch1_p2fprofile_trades.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(prof[0].keys())); w.writeheader()
    for t in sorted(prof, key=lambda x: (x["date"], x["symbol"])): w.writerow(t)
with open(f"{BASE}/stocks_engine_ch1_p2fplacebo_trades.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(plac[0].keys())); w.writeheader()
    for t in sorted(plac, key=lambda x: (x["date"], x["symbol"])): w.writerow(t)

json.dump({"incumbent_anchor_ok": True, "construction_anchor": {"trades": len(anch), "net": anch_net},
           "donor_map": DONOR,
           "profile_standalone": prof_b, "placebo_standalone": plac_b,
           "profile_ex_top3": prof_x3, "flips": {"n": len(flips),
             "net": round(sum(t["net"] for t in flips), 2),
             "detail": [(t["symbol"], t["date"], t["net"]) for t in flips]},
           "incumbent_months": im, "incumbent_ex_top3": inc_x3,
           "challenger_months": cm, "challenger_total": c_tot,
           "challenger_trades": len(challenger), "challenger_ex_top3": chal_x3,
           "assembled_placebo_total": bp_tot,
           "audit_violations": audit_v, "gate": gate,
           "adopted": bool(all(gate.values()))},
          open(f"{BASE}/stocks_engine_ch1_result.json", "w"), indent=1)
print("wrote stocks_engine_ch1_result.json + trade dumps")
