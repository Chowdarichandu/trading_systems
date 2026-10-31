#!/usr/bin/env python3
"""PEAK LAB CYCLE 4 - DIAGNOSIS at the Cycle-3 banked basis
(F4-minus-setup3 @ T150/S125, RF-1 book-wide).
Anchors: T150/S125 rebuild == cycle3 dump; union == cycle3 month table.
Profiles:
 - F4 Oct stop-outs vs -1.40% (fresh recoverable pool for S140? pool-proof rule)
 - F4 Oct losers by setup/dir/round (+ Lesson-5 both-neg scan at new basis)
 - INV-LONG Oct losers (raw T125/S050 dump): exit structure, stop MAE vs
   -0.65%/-0.80%, winners' within-holding reach of +1.50% (T150 pool)
 - N4-V3 / P2F Oct structure
 - F4 round-3 structural pool: stock-days where a third qualifying pick
   exists after the round-2 exit (counted WITHOUT replaying its P&L)
Paper, real Rs0, per 100 shares, Rs40/tr."""
import csv, sys, json, datetime
from collections import defaultdict
sys.path.insert(0, "/home/hatch/workspace/trading")
import importlib.util
BASE = "/home/hatch/workspace/trading"
def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
M1 = load_mod("M1", f"{BASE}/stocks_M1.py")
_argv = sys.argv; sys.argv = ["M2F"]
M2F = load_mod("M2F", f"{BASE}/stocks_M2_fix.py"); sys.argv = _argv
H1 = M2F.H1; M = H1.M
def wk(d): return datetime.date.fromisoformat(d).weekday() >= 5
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))
CFG = {"band_hi": 1.0, "regime": "below50"}
ALL_MONTHS = [f"2026-{i:02d}" for i in range(1, 11)]
PEAK = {"2026-01":9173.84,"2026-02":4939.87,"2026-03":21673.47,"2026-04":-632.4,
        "2026-05":26032.03,"2026-06":-817.99,"2026-07":1962.07,"2026-08":739.35,
        "2026-09":14970.43,"2026-10":53290.52}
H1.ensure_prep()
days = M2F.days_of(ALL_MONTHS)
def build_f4(tp, sp):
    M2F.TP, M2F.SP = tp, sp
    a0 = dict(M2F._AUDIT)
    raw = M2F.collect2(days, CFG)
    audit = {"trades": M2F._AUDIT["trades"]-a0["trades"], "violations": M2F._AUDIT["violations"]-a0["violations"]}
    return raw, audit
key = lambda t: (t["date"], t["symbol"], int(t["round"]), float(t["net"]), t["entry_time"])
raw, aud = build_f4(1.50, 1.25)
dump = rd("stocks_peak_oct_cycle3_f4s125_trades.csv")
a_ok = sorted(key(t) for t in raw) == sorted((r["date"], r["symbol"], int(r["round"]), float(r["net"]), r["entry_time"]) for r in dump)
print("ANCHOR A: T150/S125 rebuild == cycle3 dump:", a_ok, f"| {len(raw)} tr | audit {aud}")
inv = [t for t in M1.load_inv_long() if not wk(t["date"])]
n4  = [t for t in M1.load_n4() if not wk(t["date"])]
p2f = [t for t in M1.load_p2f(2.5) if not wk(t["date"])]
def filt_f4(raw):
    return [{"date": t["date"], "stock": t["symbol"], "comp": "F4", "net": float(t["net"]),
             "dir": t["dir"], "setup": t["setup"], "entry": float(t["entry"]),
             "entry_time": t["entry_time"], "exit_time": t["exit_time"],
             "exit_reason": t["exit_reason"], "round": int(t["round"]),
             "sig_time": t.get("sig_time",""), "gross": float(t["gross"])}
            for t in raw if not wk(t["date"]) and t["setup"] != "setup3_bounce_rejection"]
f4 = filt_f4(raw)
book = inv + n4 + p2f + f4
mt_ = defaultdict(float)
for t in book: mt_[t["date"][:7]] += t["net"]
mt_ = {k: round(v,2) for k,v in sorted(mt_.items())}
tot = round(sum(t["net"] for t in book),2)
print("ANCHOR B: union == cycle3 peak table:", mt_ == PEAK, "| trades:", len(book), "| total:", tot)
assert a_ok and mt_ == PEAK and aud["violations"] == 0

ns = H1.M.get_ns(H1.WHICH)
def excursions(t, sgn):
    """(mfe_hold, mae_day_after_entry) in % for a LONG/SHORT trade dict
    with stock/date/entry/entry_time/exit_time keys."""
    ctx = ns["DAYCTX"].get((t["stock"], t["date"])); candles = ctx["candles"]
    ei = next(i for i,c in enumerate(candles) if c["time"] == t["entry_time"])
    xi = next(i for i,c in enumerate(candles) if c["time"] == t["exit_time"])
    e = float(t["entry"])
    def fav(c): return (c["high"]-e)/e*100 if sgn>0 else (e-c["low"])/e*100
    def adv(c): return (e-c["low"])/e*100 if sgn>0 else (c["high"]-e)/e*100
    mfe = max(fav(c) for c in candles[ei:xi+1])
    mae_day = max(adv(c) for c in candles[ei:])
    mae_hold = max(adv(c) for c in candles[ei:xi+1])
    return mfe, mae_day, mae_hold

print("\n=== OCTOBER by component (losers) ===")
comp_oct = {}
for comp, rows in [("INV-LONG", inv), ("N4-V3", n4), ("P2F", p2f), ("F4", f4)]:
    o = [t for t in rows if t["date"].startswith("2026-10")]
    los = [t for t in o if t["net"] < 0]
    comp_oct[comp] = {"trades": len(o), "net": round(sum(t['net'] for t in o),2),
                      "losers": len(los), "loser_net": round(sum(t['net'] for t in los),2),
                      "loser_exits": dict(__import__("collections").Counter(t["exit_reason"] for t in los))}
    print(f"{comp:9} Oct {len(o):3} tr net {comp_oct[comp]['net']:>10.2f} | losers {len(los):2} net {comp_oct[comp]['loser_net']:>10.2f} | loser exits {comp_oct[comp]['loser_exits']}")

print("\n=== F4 OCTOBER @ T150/S125: exits + stop pool vs -1.40% ===")
oct_f4 = [t for t in f4 if t["date"].startswith("2026-10")]
exits = defaultdict(int); stop_list = []
band140 = deep140 = rec140 = 0
for t in oct_f4:
    exits[t["exit_reason"]] += 1
    if t["exit_reason"] == "stop":
        mfe, mae_day, _ = excursions(t, 1 if t["dir"]=="LONG" else -1)
        ctx = ns["DAYCTX"].get((t["stock"], t["date"])); candles = ctx["candles"]
        xi = next(i for i,c in enumerate(candles) if c["time"] == t["exit_time"])
        e = t["entry"]; sgn = 1 if t["dir"]=="LONG" else -1
        rest = candles[xi+1:]
        later_tgt = bool(rest) and max(((c["high"]-e)/e*100 if sgn>0 else (e-c["low"])/e*100) for c in rest) >= 1.50
        if mae_day >= 1.40: deep140 += 1
        else:
            band140 += 1
            if later_tgt: rec140 += 1
        stop_list.append({"date": t["date"], "stock": t["stock"], "dir": t["dir"], "setup": t["setup"],
                          "round": t["round"], "net": t["net"], "mae_day": round(mae_day,3),
                          "survives_S140": mae_day < 1.40, "later_hit_target": later_tgt})
print(f"F4 Oct trades: {len(oct_f4)} net {round(sum(t['net'] for t in oct_f4),2)} | exits: {dict(exits)}")
print(f"stop-outs: {len(stop_list)} net {round(sum(s['net'] for s in stop_list),2)}")
print(f"  never fell through -1.40% (survive S140): {band140} | fell through anyway: {deep140} | survivors later hit +1.50%: {rec140}")
for s in stop_list: print(f"  STOP {s['date']} {s['stock']:12} {s['dir']:5} {s['setup']:22} r{s['round']} net {s['net']:>9.2f} MAEday {s['mae_day']:6.3f}% surv140={s['survives_S140']} laterTgt={s['later_hit_target']}")
pool140 = [s for s in stop_list if s["survives_S140"]]
pool140_net = round(sum(s["net"] for s in pool140),2)
print(f"S140 recoverable pool: {len(pool140)} tr, pool net {pool140_net}")

print("\n=== F4 OCTOBER losers by setup / dir / round (at S125) + full-period scan ===")
def scan(rows_all, rows_oct, field, keyfn):
    out = {}
    groups = defaultdict(list); go = defaultdict(list)
    for t in rows_all: groups[keyfn(t)].append(t)
    for t in rows_oct: go[keyfn(t)].append(t)
    for g in sorted(groups, key=str):
        o = go.get(g, [])
        out[str(g)] = {"full_n": len(groups[g]), "full_net": round(sum(t['net'] for t in groups[g]),2),
                       "oct_n": len(o), "oct_net": round(sum(t['net'] for t in o),2) if o else 0.0,
                       "oct_losers": sum(1 for t in o if t['net']<0)}
        print(f"{field}={str(g):42} full {len(groups[g]):3} net {out[str(g)]['full_net']:>10.2f} | Oct {len(o):3} net {out[str(g)]['oct_net']:>10.2f} (losers {out[str(g)]['oct_losers']})")
    return out
scan_res = {}
scan_res["setup"] = scan(f4, oct_f4, "setup", lambda t: t["setup"])
scan_res["dir"] = scan(f4, oct_f4, "dir", lambda t: t["dir"])
scan_res["round"] = scan(f4, oct_f4, "round", lambda t: t["round"])
scan_res["setup_dir"] = scan(f4, oct_f4, "setup_dir", lambda t: f"{t['setup']}|{t['dir']}")

print("\n=== INV-LONG OCTOBER (raw T125/S050 dump): exit structure ===")
inv_raw = [r for r in rd("tuning_inv_T1_T125_S050_trades.csv")
           if r["direction"] == "LONG" and not wk(r["date"])]
inv_oct = [r for r in inv_raw if r["date"].startswith("2026-10")]
inv_rows = []
for r in inv_oct:
    t = {"stock": r["stock"], "date": r["date"], "entry": float(r["entry"]),
         "entry_time": r["entry_time"], "exit_time": r["exit_time"]}
    mfe, mae_day, mae_hold = excursions(t, 1)
    inv_rows.append({"date": r["date"], "stock": r["stock"], "setup": r["setup"], "round": r["round"],
                     "entry_time": r["entry_time"], "exit_time": r["exit_time"],
                     "exit_reason": r["exit_reason"], "net": float(r["net_rs_provisional_per100"]),
                     "entry": float(r["entry"]), "mfe_hold": round(mfe,3),
                     "mae_hold": round(mae_hold,3), "mae_day": round(mae_day,3)})
inv_oct_net = round(sum(x["net"] for x in inv_rows),2)
inv_los = [x for x in inv_rows if x["net"] < 0]
print(f"INV-LONG Oct: {len(inv_rows)} tr net {inv_oct_net} | exits: {dict(__import__('collections').Counter(x['exit_reason'] for x in inv_rows))}")
print(f"losers: {len(inv_los)} net {round(sum(x['net'] for x in inv_los),2)} | loser exits: {dict(__import__('collections').Counter(x['exit_reason'] for x in inv_los))}")
for x in inv_rows:
    print(f"  INV {x['date']} {x['stock']:12} {x['setup']:20} r{x['round']} {x['exit_reason']:10} net {x['net']:>9.2f} MFEhold {x['mfe_hold']:6.3f}% MAEhold {x['mae_hold']:6.3f}% MAEday {x['mae_day']:6.3f}%")
inv_stops = [x for x in inv_los if x["exit_reason"] == "stop"]
surv65 = [x for x in inv_stops if x["mae_day"] < 0.65]
surv80 = [x for x in inv_stops if x["mae_day"] < 0.80]
surv95 = [x for x in inv_stops if x["mae_day"] < 0.95]
print(f"INV stop losers: {len(inv_stops)} net {round(sum(x['net'] for x in inv_stops),2)}")
print(f"  never fell through -0.65%: {len(surv65)} (net {round(sum(x['net'] for x in surv65),2)}) | -0.80%: {len(surv80)} | -0.95%: {len(surv95)}")
inv_tgt = [x for x in inv_rows if x["exit_reason"] == "target"]
inv_sq = [x for x in inv_rows if x["exit_reason"] == "square_off"]
reach150 = [x for x in inv_rows if x["mfe_hold"] >= 1.50 and x["exit_reason"] != "target"]
print(f"INV target exits: {len(inv_tgt)} | square-offs: {len(inv_sq)} net {round(sum(x['net'] for x in inv_sq),2)} | non-target trades reaching +1.50% within holding: {len(reach150)}")

print("\n=== F4 round-3 structural pool (third pick exists after round-2 exit; P&L NOT replayed) ===")
M2F.TP, M2F.SP = 1.50, 1.25
r3_oct = r3_full = 0; r3_oct_days = []
for sym in ns["SYMBOLS"]:
    for day in days:
        tr = M2F.build2(ns, sym, day, CFG)
        tf = [t for t in tr if not wk(t["date"]) and t["setup"] != "setup3_bounce_rejection"]
        if len(tf) < 2: continue
        ctx = ns["DAYCTX"].get((sym, day)); candles = ctx["candles"]
        pm = M.premove(candles, M2F.T)
        if pm is None or abs(pm) < 0.005: continue
        want = 1 if pm > 0 else -1
        xi = next(i for i,c in enumerate(candles) if c["time"] == tf[-1]["exit_time"])
        start = xi; found = False
        while True:
            chosen = M.pick(ns, sym, day, ctx, start)
            if chosen is None: break
            setup, dirc, sig, idx = chosen
            if idx + 1 >= len(candles): break
            sign = 1 if dirc == "CE" else -1
            if sign != want: start = idx + 1; continue
            if setup == "setup3_bounce_rejection": start = idx + 1; continue
            found = True; break
        if found:
            r3_full += 1
            if day.startswith("2026-10"):
                r3_oct += 1; r3_oct_days.append({"date": day, "stock": sym})
print(f"stock-days with a third qualifying pick after round-2 exit: full {r3_full} | October {r3_oct}")
for d in r3_oct_days: print(f"  R3 {d['date']} {d['stock']}")

json.dump({"anchorA": a_ok, "anchorB": mt_==PEAK, "total": tot, "trades": len(book), "audit": aud,
           "comp_oct": comp_oct,
           "f4_oct": {"trades": len(oct_f4), "net": round(sum(t['net'] for t in oct_f4),2), "exits": dict(exits),
                      "stop_n": len(stop_list), "stop_net": round(sum(s['net'] for s in stop_list),2),
                      "band140": band140, "deep140": deep140, "rec140": rec140,
                      "pool140_net": pool140_net, "stop_list": stop_list},
           "f4_scan": scan_res,
           "inv_oct": {"trades": len(inv_rows), "net": inv_oct_net, "rows": inv_rows,
                       "stop_losers": len(inv_stops), "stop_loser_net": round(sum(x['net'] for x in inv_stops),2),
                       "surv65": len(surv65), "surv65_net": round(sum(x['net'] for x in surv65),2),
                       "surv80": len(surv80), "surv95": len(surv95),
                       "reach150_nontarget": len(reach150)},
           "round3_pool": {"full": r3_full, "oct": r3_oct, "oct_days": r3_oct_days}},
          open(f"{BASE}/stocks_peak_oct_cycle4_diag.json","w"), indent=1)
print("\nwrote stocks_peak_oct_cycle4_diag.json")
