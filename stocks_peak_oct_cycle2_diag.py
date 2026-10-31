#!/usr/bin/env python3
"""PEAK LAB CYCLE 2 - DIAGNOSIS at the Cycle-1 banked basis
(F4-minus-setup3 @ T150/S095, RF-1 book-wide).
Anchors: T150/S095 rebuild == cycle1 dump; union == cycle1 month table.
Profiles: F4 Oct excursions (+1.75/+2.00 within holding), stop-outs vs
-1.10%, Oct losers by component, and F4 loser surgery scan (setup/dir/
round/setup x dir) requiring negativity in BOTH Oct AND full period.
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
H1 = M2F.H1
def wk(d): return datetime.date.fromisoformat(d).weekday() >= 5
def rd(p):
    with open(f"{BASE}/{p}") as f: return list(csv.DictReader(f))
CFG = {"band_hi": 1.0, "regime": "below50"}
ALL_MONTHS = [f"2026-{i:02d}" for i in range(1, 11)]
PEAK = {"2026-01":12923.39,"2026-02":6241.4,"2026-03":21695.7,"2026-04":-194.06,
        "2026-05":26255.2,"2026-06":764.77,"2026-07":1992.38,"2026-08":-1495.9,
        "2026-09":15723.18,"2026-10":51413.61}
H1.ensure_prep()
days = M2F.days_of(ALL_MONTHS)
def build_f4(tp, sp):
    M2F.TP, M2F.SP = tp, sp
    a0 = dict(M2F._AUDIT)
    raw = M2F.collect2(days, CFG)
    audit = {"trades": M2F._AUDIT["trades"]-a0["trades"], "violations": M2F._AUDIT["violations"]-a0["violations"]}
    return raw, audit
key = lambda t: (t["date"], t["symbol"], int(t["round"]), float(t["net"]), t["entry_time"])
raw, aud = build_f4(1.50, 0.95)
dump = rd("stocks_peak_oct_cycle1_f4s095_trades.csv")
a_ok = sorted(key(t) for t in raw) == sorted((r["date"], r["symbol"], int(r["round"]), float(r["net"]), r["entry_time"]) for r in dump)
print("ANCHOR A: T150/S095 rebuild == cycle1 dump:", a_ok, f"| {len(raw)} tr | audit {aud}")
inv = [t for t in M1.load_inv_long() if not wk(t["date"])]
n4  = [t for t in M1.load_n4() if not wk(t["date"])]
p2f = [t for t in M1.load_p2f(2.5) if not wk(t["date"])]
def filt_f4(raw):
    return [{"date": t["date"], "stock": t["symbol"], "comp": "F4", "net": float(t["net"]),
             "dir": t["dir"], "setup": t["setup"], "entry": float(t["entry"]),
             "entry_time": t["entry_time"], "exit_time": t["exit_time"],
             "exit_reason": t["exit_reason"], "round": int(t["round"]), "leg": t.get("leg","")}
            for t in raw if not wk(t["date"]) and t["setup"] != "setup3_bounce_rejection"]
f4 = filt_f4(raw)
book = inv + n4 + p2f + f4
mt_ = defaultdict(float)
for t in book: mt_[t["date"][:7]] += t["net"]
mt_ = {k: round(v,2) for k,v in sorted(mt_.items())}
tot = round(sum(t["net"] for t in book),2)
print("ANCHOR B: union == cycle1 peak table:", mt_ == PEAK, "| trades:", len(book), "| total:", tot)

print("\n=== OCTOBER by component (losers) ===")
comp_oct = {}
for comp, rows in [("INV-LONG", inv), ("N4-V3", n4), ("P2F", p2f), ("F4", f4)]:
    o = [t for t in rows if t["date"].startswith("2026-10")]
    los = [t for t in o if t["net"] < 0]
    comp_oct[comp] = {"trades": len(o), "net": round(sum(t['net'] for t in o),2),
                      "losers": len(los), "loser_net": round(sum(t['net'] for t in los),2)}
    print(f"{comp:9} Oct {len(o):3} tr net {comp_oct[comp]['net']:>10.2f} | losers {len(los):2} net {comp_oct[comp]['loser_net']:>10.2f}")

print("\n=== F4 OCTOBER excursion profile @ T150/S095 ===")
ns = H1.M.get_ns(H1.WHICH)
oct_f4 = [t for t in f4 if t["date"].startswith("2026-10")]
stats = defaultdict(int); reach175 = reach200 = post175 = post200 = 0
stop_band110 = stop_deep110 = stop_rec110 = 0
stop_list = []
for t in oct_f4:
    ctx = ns["DAYCTX"].get((t["stock"], t["date"])); candles = ctx["candles"]
    ei = next(i for i,c in enumerate(candles) if c["time"] == t["entry_time"])
    xi = next(i for i,c in enumerate(candles) if c["time"] == t["exit_time"])
    sgn = 1 if t["dir"] == "LONG" else -1; e = t["entry"]
    def fav(c): return (c["high"]-e)/e*100 if sgn>0 else (e-c["low"])/e*100
    def adv(c): return (e-c["low"])/e*100 if sgn>0 else (c["high"]-e)/e*100
    hold = candles[ei:xi+1]; mfe = max(fav(c) for c in hold)
    stats[t["exit_reason"]] += 1
    if mfe >= 1.75: reach175 += 1
    if mfe >= 2.00: reach200 += 1
    rest = candles[xi+1:]
    if rest:
        pmfe = max(fav(c) for c in rest)
        if pmfe >= 1.75: post175 += 1
        if pmfe >= 2.00: post200 += 1
    if t["exit_reason"] == "stop":
        mae_day = max(adv(c) for c in candles[ei:])
        if mae_day >= 1.10: stop_deep110 += 1
        else:
            stop_band110 += 1
            if rest and max(fav(c) for c in rest) >= 1.50: stop_rec110 += 1
        stop_list.append({"date": t["date"], "stock": t["stock"], "dir": t["dir"], "setup": t["setup"], "net": t["net"], "mae_day": round(mae_day,3)})
print(f"F4 Oct trades: {len(oct_f4)} | exits: {dict(stats)}")
print(f"reached +1.75% WITHIN holding: {reach175} | +2.00%: {reach200}")
print(f"reached +1.75% only AFTER exit: {post175} | +2.00%: {post200}")
print(f"stop-outs full-day MAE < 1.10% (would survive S110): {stop_band110}, of which later hit +1.50%: {stop_rec110}")
print(f"stop-outs fell through -1.10% anyway: {stop_deep110}")
print(f"F4 Oct net {round(sum(t['net'] for t in oct_f4),2)} | losers {sum(1 for t in oct_f4 if t['net']<0)} net {round(sum(t['net'] for t in oct_f4 if t['net']<0),2)}")

print("\n=== F4 surgery scan: group net Oct vs Full (filtered book, setup3 already out) ===")
def scan(field):
    out = {}
    groups = defaultdict(list)
    for t in f4: groups[t[field] if field!="setup_dir" else f"{t['setup']}|{t['dir']}"].append(t)
    for g, rows in sorted(groups.items()):
        o = [t for t in rows if t["date"].startswith("2026-10")]
        out[g] = {"full_n": len(rows), "full_net": round(sum(t['net'] for t in rows),2),
                  "oct_n": len(o), "oct_net": round(sum(t['net'] for t in o),2) if o else 0.0,
                  "both_neg": bool(o) and sum(t['net'] for t in o) < 0 and sum(t['net'] for t in rows) < 0}
        print(f"{field}={g:45} full {len(rows):3} net {out[g]['full_net']:>10.2f} | Oct {len(o):3} net {out[g]['oct_net']:>10.2f} | both_neg={out[g]['both_neg']}")
    return out
scan_res = {}
for f in ["setup", "dir", "round", "setup_dir"]:
    print(f"-- by {f} --"); scan_res[f] = scan(f)
# also leg, meas/symbol checks for completeness: symbols both-neg small-n flagged
print("-- by symbol (both_neg only) --")
sym = {}
groups = defaultdict(list)
for t in f4: groups[t["stock"]].append(t)
for g, rows in sorted(groups.items()):
    o = [t for t in rows if t["date"].startswith("2026-10")]
    if o and sum(t['net'] for t in o) < 0 and sum(t['net'] for t in rows) < 0:
        sym[g] = {"full_n": len(rows), "full_net": round(sum(t['net'] for t in rows),2), "oct_n": len(o), "oct_net": round(sum(t['net'] for t in o),2)}
        print(f"symbol={g:15} full {len(rows):3} net {sym[g]['full_net']:>10.2f} | Oct {len(o):3} net {sym[g]['oct_net']:>10.2f}")
json.dump({"anchorA": a_ok, "anchorB": mt_==PEAK, "total": tot, "trades": len(book), "audit": aud,
           "comp_oct": comp_oct,
           "exc": {"reach175_hold": reach175, "reach200_hold": reach200, "post175": post175, "post200": post200,
                   "stop_band110": stop_band110, "stop_recover110": stop_rec110, "stop_deep110": stop_deep110,
                   "exits": dict(stats), "oct_f4_trades": len(oct_f4), "stop_list": stop_list},
           "scan": scan_res, "symbols_both_neg": sym},
          open(f"{BASE}/stocks_peak_oct_cycle2_diag.json","w"), indent=1)
print("\nwrote stocks_peak_oct_cycle2_diag.json")
