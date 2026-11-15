#!/usr/bin/env python3
"""FIX TEST 2026-11-02 — STOCKS P2F family: skip the opening bar.
Universe = the 87 stored component trades (P2F 46 + P2F-R2 34 + R2-LOWBAND 7).
Baseline engine (reverse-engineered and verified 87/87 exact on reason/price/time/net):
  entry = 09:15 bar open; exits = range-touch scan from the bar AFTER the entry bar,
  stop before target, fill at the level price, square-off at the 15:10 bar close;
  geometry per stored file: P2F(ch1) T125/S065, P2F-R2 T125/S050, R2-LOWBAND T125/S050;
  net = price diff x100 shares - Rs40.
Variant  = entry at the 09:20 bar open, ONLY if price is still on the trade's side of the
  original entry price (LONG: 09:20 open >= 09:15 open; SHORT: <=); else skipped.
  Exits identical, measured from the new entry, scan from 09:25.
DelayOnly= diagnostic: 09:20 open, no condition. Placebo = opposite direction at 09:20 open,
  unconditional. Candles: data/progressive/<SYM>/spot_5m.csv. Paper only, real money Rs0.
"""
import csv, json
from pathlib import Path
from collections import defaultdict

TR = Path.home() / "workspace/trading"
FILES = [("P2F", "stocks_engine_ch1_p2fprofile_trades.csv", 0.0125, 0.0065, "net"),
         ("P2F-R2", "stocks_engine_sat13_p2fr2_trades.csv", 0.0125, 0.005, "net_rs"),
         ("R2-LOWBAND", "stocks_engine_sat33_r2lowband_trades.csv", 0.0125, 0.005, "net_rs")]

_cache = {}
def bars(sym):
    if sym not in _cache:
        d = {}
        for r in csv.DictReader(open(TR / f"data/progressive/{sym}/spot_5m.csv")):
            d.setdefault(r["timestamp"][:10], {})[r["timestamp"][11:16]] = (
                float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"]))
        _cache[sym] = d
    return _cache[sym]

def simulate(day, direction, entry, entry_bar, tp, sp):
    """Range-touch exits from the bar after entry_bar; stop before target; 15:10 close square-off."""
    if direction == "LONG": stop, tgt = entry * (1 - sp), entry * (1 + tp)
    else: stop, tgt = entry * (1 + sp), entry * (1 - tp)
    for t in sorted(day):
        if t <= entry_bar or t > "15:10": continue
        o, h, l, c = day[t]
        if direction == "LONG":
            if l <= stop: return ("stop", round(stop, 2), t)
            if h >= tgt: return ("target", round(tgt, 2), t)
        else:
            if h >= stop: return ("stop", round(stop, 2), t)
            if l <= tgt: return ("target", round(tgt, 2), t)
        if t == "15:10": return ("square_off", c, "15:10")
    return (None, None, None)

def net_of(direction, entry, exit_price):
    diff = (exit_price - entry) if direction == "LONG" else (entry - exit_price)
    return round(diff * 100 - 40, 2)

def mins(t): return int(t[:2]) * 60 + int(t[3:5])

rows = []
audit_bad = []
for comp, fname, tp, sp, netcol in FILES:
    for r in csv.DictReader(open(TR / fname)):
        day = bars(r["symbol"]).get(r["date"])
        base = dict(comp=comp, symbol=r["symbol"], date=r["date"], direction=r["direction"],
                    stored_net=float(r[netcol]), stored_reason=r["exit_reason"], stored_exit=r["exit_time"])
        if not day or "09:20" not in day or "09:15" not in day:
            base["status"] = "EXCLUDED_NO_CANDLES"; rows.append(base); continue
        e0 = float(r["entry"])
        # baseline re-derivation (audit)
        rsn, px, t = simulate(day, r["direction"], e0, "09:15", tp, sp)
        re_net = net_of(r["direction"], e0, px)
        if not (rsn == r["exit_reason"] and t == r["exit_time"] and abs(re_net - float(r[netcol])) < 0.51):
            audit_bad.append((comp, r["symbol"], r["date"]))
        base.update(base_net=float(r[netcol]), base_reason=r["exit_reason"], base_exit=r["exit_time"])
        # variant
        o15, o20 = day["09:15"][0], day["09:20"][0]
        cond = (o20 >= o15) if r["direction"] == "LONG" else (o20 <= o15)
        base["cond_pass"] = cond
        if cond:
            rsn, px, t = simulate(day, r["direction"], o20, "09:20", tp, sp)
            base.update(variant_net=net_of(r["direction"], o20, px), variant_reason=rsn, variant_exit=t,
                        variant_entry=o20)
        else:
            base.update(variant_net=0.0, variant_reason="skipped", variant_exit="", variant_entry="")
        # delay-only diagnostic
        rsn, px, t = simulate(day, r["direction"], o20, "09:20", tp, sp)
        base.update(delay_net=net_of(r["direction"], o20, px), delay_reason=rsn, delay_exit=t)
        # placebo: opposite direction at 09:20 open
        opp = "SHORT" if r["direction"] == "LONG" else "LONG"
        rsn, px, t = simulate(day, opp, o20, "09:20", tp, sp)
        base.update(placebo_net=net_of(opp, o20, px), placebo_reason=rsn)
        base["status"] = "OK"
        rows.append(base)

ok = [r for r in rows if r["status"] == "OK"]
excl = [r for r in rows if r["status"] != "OK"]
print(f"AUDIT baseline re-derivation: {len(ok)-len(audit_bad)}/{len(ok)} exact; mismatches {audit_bad}")
print(f"UNIVERSE: stored {len(rows)} | excluded (no candles) {len(excl)} | scored {len(ok)}")
json.dump(rows, open(TR / "fix_tests_2026-11-02_cache/p2f_results.json", "w"), indent=1, default=str)

def S(rs, k): return round(sum(r[k] for r in rs), 2)
def quickstops(rs, nk, rk, ek, ref):
    return sum(1 for r in rs if r[rk] == "stop" and r[ek] and mins(r[ek]) - mins(ref) <= 15)
taken = [r for r in ok if r["variant_reason"] != "skipped"]
print(f"VARIANT: condition passed {len(taken)}/{len(ok)} (skipped {len(ok)-len(taken)})")
print(f"NETS: baseline {S(ok,'base_net')} | variant {S(ok,'variant_net')} | delay-only {S(ok,'delay_net')} | placebo(opposite) {S(ok,'placebo_net')}")
print(f"Baseline on variant-taken subset {S(taken,'base_net')} -> variant {S(taken,'variant_net')} | Baseline on skipped subset {S([r for r in ok if r['variant_reason']=='skipped'],'base_net')}")
print(f"QUICK STOPS (exit stamp within 15 min of entry): baseline {quickstops(ok,'','base_reason','base_exit','09:15')} -> variant {quickstops(ok,'','variant_reason','variant_exit','09:20')} | delay-only {quickstops(ok,'','delay_reason','delay_exit','09:20')}")
print(f"First-scanned-bar stops: baseline(stamp 09:20) {sum(1 for r in ok if r['base_reason']=='stop' and r['base_exit']=='09:20')} -> variant(stamp 09:25) {sum(1 for r in ok if r['variant_reason']=='stop' and r['variant_exit']=='09:25')}")
for name, k in (("baseline", "base_net"), ("variant", "variant_net")):
    rs = ok if name == "baseline" else taken
    wr = sum(1 for r in rs if r[k] > 0) / len(rs)
    print(f"{name}: trades {len(rs)} winrate {wr:.3f}")
for label, sel in (("H1 Jan-May", lambda r: r["date"] <= "2026-05-31"), ("H2 Jun-Oct", lambda r: r["date"] >= "2026-06-01")):
    rs = [r for r in ok if sel(r)]
    print(f"{label}: baseline {S(rs,'base_net')} -> variant {S(rs,'variant_net')} (delay-only {S(rs,'delay_net')}, placebo {S(rs,'placebo_net')})")
print("MONTHS: baseline -> variant")
for m in range(1, 11):
    rs = [r for r in ok if r["date"][5:7] == f"{m:02d}"]
    if rs: print(f"  2026-{m:02d}: {S(rs,'base_net')} -> {S(rs,'variant_net')} (n {len(rs)} -> {sum(1 for r in rs if r['variant_reason']!='skipped')})")
for name, k in (("baseline", "base_net"), ("variant", "variant_net")):
    top3 = sorted(ok, key=lambda r: -r[k])[:3]
    print(f"EX-TOP3 {name}: {S(ok,k)} - {[round(r[k],2) for r in top3]} = {round(S(ok,k)-sum(r[k] for r in top3),2)}")
bysym = defaultdict(lambda: [0.0, 0.0, 0, 0])
for r in ok:
    bysym[r["symbol"]][0] += r["base_net"]; bysym[r["symbol"]][2] += 1
    if r["variant_reason"] != "skipped": bysym[r["symbol"]][1] += r["variant_net"]; bysym[r["symbol"]][3] += 1
print(f"BREADTH: symbols net-positive baseline {sum(1 for v in bysym.values() if v[0]>0)}/{len(bysym)} | variant {sum(1 for v in bysym.values() if v[1]>0)}/{len(bysym)}")
print("Per-component: baseline -> variant (quick stops base -> variant)")
for comp in ("P2F", "P2F-R2", "R2-LOWBAND"):
    rs = [r for r in ok if r["comp"] == comp]
    print(f"  {comp}: {S(rs,'base_net')} -> {S(rs,'variant_net')} (n {len(rs)} -> {sum(1 for r in rs if r['variant_reason']!='skipped')}; quick {quickstops(rs,'','base_reason','base_exit','09:15')} -> {quickstops(rs,'','variant_reason','variant_exit','09:20')})")
