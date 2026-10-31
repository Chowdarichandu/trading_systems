#!/usr/bin/env python3
"""PEAK LAB CYCLE 3 - DIAGNOSIS at the Cycle-2 banked basis
(F4-minus-setup3 @ T150/S110, RF-1 book-wide).
Anchors: T150/S110 rebuild == cycle2 dump; union == cycle2 month table.
Profiles requested for Cycle 3:
 - F4 Oct within-holding reaches of +1.75% / +2.00% (re-measured at S110:
   wider stop keeps trades alive longer, so the pool may have GROWN)
 - F4 Oct stop-outs vs -1.25% (surviving recoverable pool for S125?)
 - F4 Oct square-off pool size + their excursion profile (MFE/MAE/give-back)
 - October losers by component
 - Lesson-5 surgery scan (setup/dir/round/setup x dir/symbol/sig_time):
   a group counts only if negative in BOTH October AND full period.
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
PEAK = {"2026-01":10605.83,"2026-02":6441.5,"2026-03":24862.22,"2026-04":-3577.04,
        "2026-05":25950.59,"2026-06":-1070.86,"2026-07":2002.22,"2026-08":-2949.53,
        "2026-09":17074.58,"2026-10":52428.5}
H1.ensure_prep()
days = M2F.days_of(ALL_MONTHS)
def build_f4(tp, sp):
    M2F.TP, M2F.SP = tp, sp
    a0 = dict(M2F._AUDIT)
    raw = M2F.collect2(days, CFG)
    audit = {"trades": M2F._AUDIT["trades"]-a0["trades"], "violations": M2F._AUDIT["violations"]-a0["violations"]}
    return raw, audit
key = lambda t: (t["date"], t["symbol"], int(t["round"]), float(t["net"]), t["entry_time"])
raw, aud = build_f4(1.50, 1.10)
dump = rd("stocks_peak_oct_cycle2_f4s110_trades.csv")
a_ok = sorted(key(t) for t in raw) == sorted((r["date"], r["symbol"], int(r["round"]), float(r["net"]), r["entry_time"]) for r in dump)
print("ANCHOR A: T150/S110 rebuild == cycle2 dump:", a_ok, f"| {len(raw)} tr | audit {aud}")
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
print("ANCHOR B: union == cycle2 peak table:", mt_ == PEAK, "| trades:", len(book), "| total:", tot)
assert a_ok and mt_ == PEAK and aud["violations"] == 0

print("\n=== OCTOBER by component (losers) ===")
comp_oct = {}
for comp, rows in [("INV-LONG", inv), ("N4-V3", n4), ("P2F", p2f), ("F4", f4)]:
    o = [t for t in rows if t["date"].startswith("2026-10")]
    los = [t for t in o if t["net"] < 0]
    comp_oct[comp] = {"trades": len(o), "net": round(sum(t['net'] for t in o),2),
                      "losers": len(los), "loser_net": round(sum(t['net'] for t in los),2)}
    print(f"{comp:9} Oct {len(o):3} tr net {comp_oct[comp]['net']:>10.2f} | losers {len(los):2} net {comp_oct[comp]['loser_net']:>10.2f}")

print("\n=== F4 OCTOBER excursion profile @ T150/S110 ===")
ns = H1.M.get_ns(H1.WHICH)
oct_f4 = [t for t in f4 if t["date"].startswith("2026-10")]
exits = defaultdict(int)
reach175 = reach200 = post175 = post200 = 0
reach_by_exit = defaultdict(lambda: {"n":0,"r175":0,"r200":0})
stop_band125 = stop_deep125 = stop_rec125 = 0
stop_list = []
sq = []           # square-off detail rows
sq_mfe_buckets = defaultdict(int)
for t in oct_f4:
    ctx = ns["DAYCTX"].get((t["stock"], t["date"])); candles = ctx["candles"]
    ei = next(i for i,c in enumerate(candles) if c["time"] == t["entry_time"])
    xi = next(i for i,c in enumerate(candles) if c["time"] == t["exit_time"])
    sgn = 1 if t["dir"] == "LONG" else -1; e = t["entry"]
    def fav(c): return (c["high"]-e)/e*100 if sgn>0 else (e-c["low"])/e*100
    def adv(c): return (e-c["low"])/e*100 if sgn>0 else (c["high"]-e)/e*100
    hold = candles[ei:xi+1]
    mfe = max(fav(c) for c in hold); mae = max(adv(c) for c in hold)
    exits[t["exit_reason"]] += 1
    rb = reach_by_exit[t["exit_reason"]]; rb["n"] += 1
    if mfe >= 1.75: reach175 += 1; rb["r175"] += 1
    if mfe >= 2.00: reach200 += 1; rb["r200"] += 1
    rest = candles[xi+1:]
    if rest:
        pmfe = max(fav(c) for c in rest)
        if pmfe >= 1.75: post175 += 1
        if pmfe >= 2.00: post200 += 1
    if t["exit_reason"] == "stop":
        mae_day = max(adv(c) for c in candles[ei:])
        if mae_day >= 1.25: stop_deep125 += 1
        else:
            stop_band125 += 1
            if rest and max(fav(c) for c in rest) >= 1.50: stop_rec125 += 1
        stop_list.append({"date": t["date"], "stock": t["stock"], "dir": t["dir"], "setup": t["setup"],
                          "net": t["net"], "mae_day": round(mae_day,3)})
    if t["exit_reason"] == "square_off":
        # give-back in Rs (per 100 sh): best favourable Rs minus realised gross
        giveback = round(e * mfe - t["gross"], 2)
        sq.append({"date": t["date"], "stock": t["stock"], "dir": t["dir"], "setup": t["setup"],
                   "net": t["net"], "gross": t["gross"], "mfe_pct": round(mfe,3), "mae_pct": round(mae,3),
                   "giveback_rs": giveback})
        b = ("<0" if mfe < 0 else "0-0.5" if mfe < 0.5 else "0.5-1.0" if mfe < 1.0
             else "1.0-1.25" if mfe < 1.25 else "1.25-1.5" if mfe < 1.5 else ">=1.5")
        sq_mfe_buckets[b] += 1
print(f"F4 Oct trades: {len(oct_f4)} | exits: {dict(exits)}")
print(f"reached +1.75% WITHIN holding: {reach175} | +2.00%: {reach200}")
print(f"  by exit_reason: { {k: dict(v) for k,v in reach_by_exit.items()} }")
print(f"reached +1.75% only AFTER exit: {post175} | +2.00%: {post200}")
print(f"stop-outs full-day MAE < 1.25% (would survive S125): {stop_band125}, of which later hit +1.50%: {stop_rec125}")
print(f"stop-outs fell through -1.25% anyway: {stop_deep125}")
print(f"F4 Oct net {round(sum(t['net'] for t in oct_f4),2)} | losers {sum(1 for t in oct_f4 if t['net']<0)} net {round(sum(t['net'] for t in oct_f4 if t['net']<0),2)}")

print("\n=== F4 OCTOBER square-off pool @ T150/S110 ===")
sq_net = round(sum(t["net"] for t in sq),2)
sq_los = [t for t in sq if t["net"] < 0]; sq_win = [t for t in sq if t["net"] >= 0]
sq_hi = [t for t in sq if t["mfe_pct"] >= 1.0]   # reached >=+1.0% within holding but did not bank target
print(f"square-offs: {len(sq)} | net {sq_net} | winners {len(sq_win)} net {round(sum(t['net'] for t in sq_win),2)} | losers {len(sq_los)} net {round(sum(t['net'] for t in sq_los),2)}")
print(f"MFE buckets: {dict(sq_mfe_buckets)}")
print(f"square-offs with MFE >= +1.00% (give-back pool): {len(sq_hi)} | their net {round(sum(t['net'] for t in sq_hi),2)} | total give-back Rs {round(sum(t['giveback_rs'] for t in sq_hi),2)}")
for t in sorted(sq, key=lambda x: -x["mfe_pct"]):
    print(f"  SQ {t['date']} {t['stock']:12} {t['dir']:5} {t['setup']:20} net {t['net']:>9.2f} MFE {t['mfe_pct']:6.3f}% MAE {t['mae_pct']:6.3f}% giveback {t['giveback_rs']:>9.2f}")

print("\n=== F4 surgery scan: group net Oct vs Full (Lesson 5: both-neg only) ===")
def scan(field, keyfn):
    out = {}
    groups = defaultdict(list)
    for t in f4: groups[keyfn(t)].append(t)
    for g, rows in sorted(groups.items(), key=lambda kv: str(kv[0])):
        o = [t for t in rows if t["date"].startswith("2026-10")]
        both = bool(o) and sum(t['net'] for t in o) < 0 and sum(t['net'] for t in rows) < 0
        out[str(g)] = {"full_n": len(rows), "full_net": round(sum(t['net'] for t in rows),2),
                       "oct_n": len(o), "oct_net": round(sum(t['net'] for t in o),2) if o else 0.0, "both_neg": both}
        if both or field in ("setup","dir","round"):
            print(f"{field}={str(g):45} full {len(rows):3} net {out[str(g)]['full_net']:>10.2f} | Oct {len(o):3} net {out[str(g)]['oct_net']:>10.2f} | both_neg={both}")
    return out
scan_res = {}
scan_res["setup"] = scan("setup", lambda t: t["setup"])
scan_res["dir"] = scan("dir", lambda t: t["dir"])
scan_res["round"] = scan("round", lambda t: t["round"])
scan_res["setup_dir"] = scan("setup_dir", lambda t: f"{t['setup']}|{t['dir']}")
scan_res["symbol"] = scan("symbol", lambda t: t["stock"])
scan_res["sig_time"] = scan("sig_time", lambda t: t["sig_time"])
json.dump({"anchorA": a_ok, "anchorB": mt_==PEAK, "total": tot, "trades": len(book), "audit": aud,
           "comp_oct": comp_oct,
           "exc": {"reach175_hold": reach175, "reach200_hold": reach200, "post175": post175, "post200": post200,
                   "reach_by_exit": {k: dict(v) for k,v in reach_by_exit.items()},
                   "stop_band125": stop_band125, "stop_recover125": stop_rec125, "stop_deep125": stop_deep125,
                   "exits": dict(exits), "oct_f4_trades": len(oct_f4), "stop_list": stop_list},
           "square_off": {"n": len(sq), "net": sq_net,
                          "losers": len(sq_los), "loser_net": round(sum(t['net'] for t in sq_los),2),
                          "winners": len(sq_win), "winner_net": round(sum(t['net'] for t in sq_win),2),
                          "mfe_buckets": dict(sq_mfe_buckets),
                          "mfe_ge_100": len(sq_hi),
                          "mfe_ge_100_net": round(sum(t['net'] for t in sq_hi),2) if sq_hi else 0.0,
                          "mfe_ge_100_giveback_rs": round(sum(t['giveback_rs'] for t in sq_hi),2) if sq_hi else 0.0,
                          "rows": sq},
           "scan": scan_res},
          open(f"{BASE}/stocks_peak_oct_cycle3_diag.json","w"), indent=1)
print("\nwrote stocks_peak_oct_cycle3_diag.json")
