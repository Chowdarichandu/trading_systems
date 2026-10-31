#!/usr/bin/env python3
"""ENGINE SAT-4: NEW COMPONENT N4-LOWBAND (reaction band [0.75%, 1.0%)).
Spec frozen in stocks_engine_frozen.md (section SAT-4) BEFORE scoring.
Steps: (1) incumbent rebuild anchor == state (878 tr / +143,747.36 /
state month table); (2) CONSTRUCTION ANCHOR: the identical N4 pipeline
at |move| >= 1.0% must reproduce eq_n4deep_v3_trades_T125_janoct.csv
per-trade (net + exit_reason, 56/56) under the CH-2 replay convention
(scan from the 09:35 bar, stop-first, 15:10 square-off); (3) LOWBAND
build [0.75, 1.0), T125/S050, timing audit asserted, mechanical
zero-overlap vs the N4-V3 dump on (date, stock); (4) standalone +
union + saturation gate: (a) union total > 143,747.36, (b) all ten
months > 0, (c) October >= 50,000. RF-1 (weekend drop) applied to the
component as book-wide convention, count reported.
Paper only, real Rs0, per 100 shares provisional, Rs40/trade."""
import csv, json, sys
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
MONTHS = [f"2026-{i:02d}" for i in range(1, 11)]
STATE_MONTHS = {"2026-01": 11378.22, "2026-02": 6130.34, "2026-03": 20269.77,
                "2026-04": 2043.12, "2026-05": 28714.75, "2026-06": 1853.72,
                "2026-07": 3196.63, "2026-08": 878.69, "2026-09": 17917.38,
                "2026-10": 51364.74}
STATE_TOTAL, STATE_TRADES = 143747.36, 878
AUG_REVISIT_NEED = 4020.54  # 878.69 + 3,141.85 (CH-2 N4-rebuild condition)

def wk(d): return date.fromisoformat(d).weekday() >= 5
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))
def month_table(trades):
    m = {k: 0.0 for k in MONTHS}
    for t in trades: m[t["date"][:7]] = round(m.get(t["date"][:7], 0.0) + t["net"], 2)
    return m
def per_stock(trades):
    ps = defaultdict(float)
    for t in trades: ps[t["stock"]] += t["net"]
    return {k: round(v, 2) for k, v in sorted(ps.items(), key=lambda kv: -kv[1])}

# ---------- (1) incumbent anchor ----------
inv = [t for t in M1.load_inv_long() if not wk(t["date"]) and t["stock"] != "BDL"]
n4v3_book = [t for t in M1.load_n4() if not wk(t["date"]) and t["stock"] != "ASTRAL"]
p2f25 = [t for t in M1.load_p2f(2.5) if not wk(t["date"])
         and t["stock"] != "ASTRAL" and t["stock"] != "HINDUNILVR"]
f4 = [{"date": r["date"], "stock": r["symbol"], "comp": "F4", "net": float(r["net"])}
      for r in rd("stocks_engine_oc4_f4s080_trades.csv")
      if not wk(r["date"]) and r["setup"] != "setup3_bounce_rejection"
      and not (r["symbol"] == "GODREJCP" and r["dir"] == "SHORT")
      and not (r["symbol"] == "INDUSTOWER" and r["dir"] == "LONG")]
incumbent = inv + n4v3_book + p2f25 + f4
im = month_table(incumbent)
inc_tot = round(sum(t["net"] for t in incumbent), 2)
anchor_inc = (im == STATE_MONTHS and inc_tot == STATE_TOTAL and len(incumbent) == STATE_TRADES)
print("INCUMBENT ANCHOR:", anchor_inc, f"| trades {len(incumbent)} total {inc_tot}")
assert anchor_inc, f"incumbent anchor FAIL: {im} {inc_tot} {len(incumbent)}"

# ---------- N4 signal construction (n4deep mechanics, replicated) ----------
SYMBOLS = ["GODREJCP","GLENMARK","ITC","RECLTD","TVSMOTOR","UNITDSPR","OBEROIRLTY",
           "NTPC","INDUSTOWER","KALYANKJIL","HDFCBANK","NHPC","PFC","IRCTC","WIPRO",
           "NATIONALUM","VEDL","HINDCOPPER","HINDZINC","HINDALCO","TATASTEEL",
           "ASTRAL","BDL","OIL","HINDUNILVR"]
SINGLE_NEWS = {"management_change","large_order","fda_approval","block_deal",
               "sector_policy","pricing","corporate_action"}
DATA = f"{BASE}/data/progressive"

def load_stock(sym):
    spot, daily = {}, []
    with open(f"{DATA}/{sym}/spot_5m.csv") as f:
        for r in csv.DictReader(f):
            d = r["timestamp"][:10]
            spot.setdefault(d, []).append({"timestamp": r["timestamp"][:19], "time": r["timestamp"][11:16],
                "open": float(r["open"]), "high": float(r["high"]),
                "low": float(r["low"]), "close": float(r["close"])})
    with open(f"{DATA}/{sym}/spot_daily.csv") as f:
        for r in csv.DictReader(f):
            daily.append({"date": r["date"][:10], "close": float(r["close"])})
    daily.sort(key=lambda x: x["date"])
    for d in spot: spot[d].sort(key=lambda x: x["timestamp"])
    return spot, daily

stocks = {s: load_stock(s) for s in SYMBOLS}
_, nifty_daily = load_stock("NIFTY")
ALL_DAYS = sorted(d["date"] for d in nifty_daily if "2026-01-01" <= d["date"] <= "2026-10-28")

def combined_days():
    out = {s: set() for s in SYMBOLS}
    with open(f"{BASE}/stock_event_calendar_jan_oct_2026.csv") as f:
        for r in csv.DictReader(f):
            sym = r["stock"]
            if sym not in out: continue
            et = r["event_type"]
            if et != "results" and et not in SINGLE_NEWS: continue
            if not r["event_date"]: continue
            ev = date.fromisoformat(r["event_date"][:10])
            react = date.fromisoformat(r["reaction_date"][:10]) if r["reaction_date"] else None
            eff = react if (react and ev <= react <= ev + timedelta(days=7)) else ev
            ds = eff.isoformat()
            if "2026-01-01" <= ds <= "2026-10-28": out[sym].add(ds)
    return out
COMBINED = combined_days()

SIGNALS = []  # all combined-day signals with their |move|
for sym in SYMBOLS:
    spot, daily = stocks[sym]
    dmap = {d["date"]: i for i, d in enumerate(daily)}
    for day in ALL_DAYS:
        if day not in COMBINED[sym]: continue
        if day not in dmap or dmap[day] == 0: continue
        raw = spot.get(day, [])
        if not raw: continue
        prev_close = daily[dmap[day] - 1]["close"]
        if not prev_close: continue
        by_time = {c["time"]: c for c in raw}
        b0925, b0930 = by_time.get("09:25"), by_time.get("09:30")
        if b0925 is None or b0930 is None: continue
        move_pct = (b0925["close"] / prev_close - 1) * 100
        SIGNALS.append({"symbol": sym, "date": day,
                        "direction": "LONG" if move_pct > 0 else "SHORT",
                        "entry": b0930["close"], "move_pct": move_pct,
                        "prev_close": prev_close})

# ---------- replay (CH-2 convention, verbatim) ----------
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

def score_signals(sigs, tgt_pct=1.25, stp_pct=0.50):
    out, bad, audit_v = [], 0, 0
    for s in sigs:
        candles = stocks[s["symbol"]][0][s["date"]]
        ei = next((i for i, c in enumerate(candles) if c["time"] == "09:35"), None)
        if ei is None: bad += 1; continue
        # timing audit: qualifier uses prev close + bars through the 09:25
        # close (known at 09:30); entry is the 09:30 bar close (09:35 label)
        b0930 = next(c for c in candles if c["time"] == "09:30")
        if abs(b0930["close"] - s["entry"]) > 1e-9: audit_v += 1
        res = replay(candles, ei, s["entry"], s["direction"], tgt_pct, stp_pct, 0)
        if res is None: bad += 1; continue
        er, ep, et = res
        if et < "09:35": audit_v += 1
        sign = 1 if s["direction"] == "LONG" else -1
        out.append({"date": s["date"], "stock": s["symbol"], "comp": "N4-LOWBAND",
                    "dir": s["direction"], "entry_time": "09:35",
                    "entry": round(s["entry"], 2), "exit_reason": er,
                    "exit_price": round(ep, 2), "exit_time": et,
                    "move_pct": round(s["move_pct"], 3),
                    "net": round(sign * (ep - s["entry"]) * QTY - COST, 2)})
    return out, bad, audit_v

# ---------- (2) construction anchor: >= 1.0% band must reproduce the V3 dump ----------
v3_sigs = [s for s in SIGNALS if abs(s["move_pct"]) >= 1.0]
v3_mine, v3_bad, v3_audit = score_signals(v3_sigs)
dump = rd("eq_n4deep_v3_trades_T125_janoct.csv")
dump_map = {(r["date"], r["stock"]): (float(r["net_rs_provisional_per100"]), r["exit_reason"], r["direction"]) for r in dump}
mine_map = {(t["date"], t["stock"]): (t["net"], t["exit_reason"], t["dir"]) for t in v3_mine}
match = sum(1 for k, v in mine_map.items()
            if k in dump_map and abs(v[0] - dump_map[k][0]) < 0.011
            and v[1] == dump_map[k][1] and v[2] == dump_map[k][2])
print(f"CONSTRUCTION ANCHOR: {match}/{len(dump)} dump trades reproduced "
      f"(mine {len(v3_mine)}, bad={v3_bad}, audit_v={v3_audit})")
assert match == len(dump) == len(v3_mine) and v3_bad == 0 and v3_audit == 0, \
    "construction anchor FAIL — pipeline does not reproduce N4-V3"

# ---------- (3) LOWBAND build ----------
lb_sigs = [s for s in SIGNALS if 0.75 <= abs(s["move_pct"]) < 1.0]
lb_all, lb_bad, lb_audit = score_signals(lb_sigs)
print(f"LOWBAND raw: {len(lb_all)} trades (bad={lb_bad}, audit violations={lb_audit})")
assert lb_bad == 0 and lb_audit == 0
overlap = {(t["date"], t["stock"]) for t in lb_all} & set(dump_map)
print("OVERLAP vs N4-V3 dump (date,stock):", len(overlap))
assert not overlap, f"OVERLAP FAIL: {overlap}"
wk_dropped = [t for t in lb_all if wk(t["date"])]
lb = [t for t in lb_all if not wk(t["date"])]
print(f"RF-1 weekend drops: {len(wk_dropped)}"
      + (f" ({[(t['date'], t['stock'], t['net']) for t in wk_dropped]})" if wk_dropped else ""))

# ---------- (4) standalone + union + gate ----------
def stats(trades):
    tot = round(sum(t["net"] for t in trades), 2)
    h1 = round(sum(t["net"] for t in trades if t["date"] <= "2026-05-31"), 2)
    h2 = round(sum(t["net"] for t in trades if t["date"] >= "2026-06-01"), 2)
    ps = per_stock(trades)
    return {"trades": len(trades), "net": tot, "jan_may": h1, "jun_oct": h2,
            "october": round(sum(t["net"] for t in trades if t["date"].startswith("2026-10")), 2),
            "august": round(sum(t["net"] for t in trades if t["date"].startswith("2026-08")), 2),
            "win_pct": round(100 * sum(1 for t in trades if t["net"] > 0) / len(trades), 1) if trades else 0.0,
            "expectancy": round(tot / len(trades), 2) if trades else 0.0,
            "breadth": sum(1 for v in ps.values() if v > 0),
            "months": month_table(trades), "per_stock": ps}
lb_stats = stats(lb)
astral = [t for t in lb if t["stock"] == "ASTRAL"]
print("\nLOWBAND standalone:", {k: lb_stats[k] for k in
      ("trades", "net", "jan_may", "jun_oct", "october", "august", "win_pct", "expectancy", "breadth")})
print("LOWBAND months:", lb_stats["months"])
print("LOWBAND per-stock:", lb_stats["per_stock"])
print("ASTRAL slice in LOWBAND:", len(astral), "trades, net",
      round(sum(t["net"] for t in astral), 2))

union = incumbent + lb
um = month_table(union)
u_tot = round(sum(t["net"] for t in union), 2)
gate = {"a_total_rises": u_tot > STATE_TOTAL,
        "b_all_months_green": all(v > 0 for v in um.values()),
        "c_october_floor": um["2026-10"] >= 50000}
banked = all(gate.values())
print("\nUNION months:", um)
print("union total:", u_tot, "trades:", len(union))
print("GATE:", gate, "=> BANKED" if banked else "=> REJECTED")
aug_union = um["2026-08"]
print(f"August: incumbent 878.69 -> union {aug_union} | revisit need {AUG_REVISIT_NEED} | "
      f"remaining shortfall {round(max(0.0, AUG_REVISIT_NEED - aug_union), 2)}")

with open(f"{BASE}/stocks_engine_sat4_lowband_trades.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["date", "stock", "dir", "entry_time", "entry",
                                      "move_pct", "exit_reason", "exit_price", "exit_time", "net"])
    w.writeheader()
    for t in sorted(lb, key=lambda x: (x["date"], x["stock"])):
        w.writerow({k: t[k] for k in ("date", "stock", "dir", "entry_time", "entry",
                                      "move_pct", "exit_reason", "exit_price", "exit_time", "net")})
json.dump({"construction_anchor": {"matched": match, "dump_trades": len(dump)},
           "audit_violations": lb_audit, "overlap_with_n4v3": len(overlap),
           "rf1_weekend_dropped": len(wk_dropped),
           "lowband_standalone": lb_stats,
           "astral_slice": {"trades": len(astral),
                            "net": round(sum(t["net"] for t in astral), 2)},
           "incumbent_months": im, "union_months": um, "union_total": u_tot,
           "union_trades": len(union), "gate": gate, "banked": banked,
           "august_union": aug_union,
           "august_revisit_remaining": round(max(0.0, AUG_REVISIT_NEED - aug_union), 2)},
          open(f"{BASE}/stocks_engine_sat4_result.json", "w"), indent=1)
print("wrote stocks_engine_sat4_result.json + stocks_engine_sat4_lowband_trades.csv")
