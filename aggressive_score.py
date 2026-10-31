#!/usr/bin/env python3
"""AGGRESSIVE TUNING — October 2026 premiums first, per index separately.
Paper only, no orders, no stocks. Real money Rs0.
Frozen candidate definitions are in aggressive_oct_bank.md / aggressive_oct_nifty.md
(written before results are read). This script only scores them.
Overlay conventions: entry = open of option candle at entry bar; stop checked
before target on every bar incl. entry bar; square-off 15:10 close; cost Rs220;
net = (exit-entry)*lot - 220. Lots: NIFTY 65, BANKNIFTY 30.
October weeks = 18 trading days / 5 = 3.6. Jan-Oct weeks = 203/5 = 40.6.
"""
import csv, json, glob
from pathlib import Path
from collections import defaultdict

TR = Path.home() / "workspace/trading"
DIRS = [TR / "aggressive_data", TR / "v4_options_oct_data", TR / "historical_proof_data"]
COST = 220.0
LOT = {"NIFTY": 65, "BANKNIFTY": 30}
EXPIRIES = ["2026-01-27","2026-02-24","2026-03-30","2026-04-28","2026-05-26",
            "2026-06-30","2026-07-28","2026-08-25","2026-09-29","2026-10-27"]

_cache = {}
def candles(sym, strike, typ, day, exp):
    tag = f"{sym}_{int(strike)}{typ}_{day}_{exp}"
    if tag in _cache: return _cache[tag]
    cs = None
    cands = []
    for d in DIRS:
        p = d / f"candles_{tag}.json"
        if p.exists(): cands.append(p)
        p2 = d / f"candles_premium_{tag}.json"
        if p2.exists(): cands.append(p2)
    if not cands:
        for d in DIRS:
            cands += [Path(x) for x in glob.glob(str(d / f"candles_*{int(strike)}{typ}_{day}*.json"))]
    for p in cands:
        try:
            data = json.loads(p.read_text()).get("data", {}).get("candles", [])
        except Exception:
            continue
        rows = [(c[0][11:16], float(c[1]), float(c[2]), float(c[3]), float(c[4]),
                 float(c[5]) if len(c) > 5 else 0.0) for c in sorted(data, key=lambda c: c[0])
                if c[0][:10] == day]
        if rows: cs = rows; break
    _cache[tag] = cs
    return cs

def replay(cs, entry_time, lot, stop_pts=50.0, target_pts=90.0, mode="plain", delay=0):
    """mode: plain | runner_be | runner_lock50 | partial. Returns dict or None."""
    if not cs: return None
    idxs = [i for i, b in enumerate(cs) if b[0] >= entry_time]
    if not idxs: return None
    i0 = idxs[0] + delay
    if i0 >= len(cs): return None
    bars = cs[i0:]
    if bars[0][0] > "15:10": return None
    entry = bars[0][1]
    stop, target = entry - stop_pts, entry + target_pts
    def sq(b):
        return dict(net=round((b[4] - entry) * lot - COST, 2), exit_reason="square_off",
                    exit_time=b[0], ft=0, entry=entry, exit=b[4])
    for i, b in enumerate(bars):
        t, o, h, l, cl, v = b
        if t > "15:10": break
        if l <= stop:
            return dict(net=round((stop - entry) * lot - COST, 2), exit_reason="stop",
                        exit_time=t, ft=0, entry=entry, exit=stop)
        if h >= target:
            if mode == "plain":
                return dict(net=round((target - entry) * lot - COST, 2), exit_reason="target",
                            exit_time=t, ft=1, entry=entry, exit=target)
            # runner / partial second phase: stop2 = entry (be) or entry+50 (lock50; partial uses be)
            stop2 = entry + 50.0 if mode == "runner_lock50" else entry
            target2 = entry + 150.0
            rest = None
            for b2 in bars[i+1:]:
                t2, o2, h2, l2, cl2, v2 = b2
                if t2 > "15:10": break
                if l2 <= stop2:
                    rest = (stop2, "runner_stop", t2); break
                if h2 >= target2:
                    rest = (target2, "runner_target150", t2); break
                if t2 == "15:10":
                    rest = (cl2, "runner_square_off", t2); break
            if rest is None:
                lb = bars[-1]; rest = (lb[4], "runner_square_off", lb[0])
            if mode == "partial":
                net = round(((target - entry) * 0.5 + (rest[0] - entry) * 0.5) * lot - COST, 2)
                return dict(net=net, exit_reason="partial+" + rest[1], exit_time=rest[2],
                            ft=1, entry=entry, exit=rest[0])
            return dict(net=round((rest[0] - entry) * lot - COST, 2), exit_reason=rest[1],
                        exit_time=rest[2], ft=1, entry=entry, exit=rest[0])
        if t == "15:10":
            return sq(b)
    lb = bars[-1]
    return sq(lb)

def entry_bar_stats(cs, entry_time):
    if not cs: return None
    bars = [b for b in cs if b[0] <= entry_time]
    if not bars or bars[-1][0] != entry_time: return None
    b = bars[-1]
    num = sum(((x[2] + x[3] + x[4]) / 3.0) * x[5] for x in bars)
    den = sum(x[5] for x in bars)
    vwap = num / den if den > 0 else sum(x[4] for x in bars) / len(bars)
    hi = max(x[2] for x in bars); lo = min(x[3] for x in bars)
    return dict(bar=b, vwap=vwap, day_hi=hi, day_lo=lo)

# ---------- leg universes ----------
def base_legs(sym, months=None):
    f = "historical_proof_bank_B2_trades.csv" if sym == "BANKNIFTY" else "historical_proof_nifty_N1_trades.csv"
    out = []
    for r in csv.DictReader(open(TR / f)):
        if months and r["date"][5:7] not in months: continue
        out.append(dict(date=r["date"], index=sym, direction=r["direction"],
                        entry_time=r["entry_time"], strike=int(float(r["strike"])),
                        expiry=r["expiry"], lot=LOT[sym], rep=r["representative_system"],
                        sources=r["source_systems"], family="BASE",
                        base_net=float(r["net_rs"]), base_reason=r["exit_reason"]))
    return out

def ns_oct_legs(sym):
    out = []
    for r in csv.DictReader(open(TR / "index_options_newsetup_premium_october_trades.csv")):
        if r["index"] != sym: continue
        if (r["family"], r["leg"]) not in (("NS1", "second"), ("NS2", "afternoon_rescan")): continue
        if r["premium_status"] != "COMPUTED": continue
        out.append(dict(date=r["date"], index=sym, direction=r["direction"],
                        entry_time=r["entry_time"], strike=int(float(r["strike"])),
                        expiry=r["expiry"], lot=LOT[sym], rep=r["family"],
                        sources=r["family"], family=r["family"] + "_" + r["leg"],
                        base_net=float(r["premium_net_per_1_lot_rs"]),
                        base_reason=r["prem_exit_reason"]))
    return out

def ns_jansep_legs(sym):
    out = []
    for f, legname, fam in (("index_options_newsetup_ns1_trades_jan_oct_2026.csv", "second", "NS1_second"),
                            ("index_options_newsetup_ns2_trades_jan_oct_2026.csv", "afternoon_rescan", "NS2_afternoon")):
        for r in csv.DictReader(open(TR / f)):
            if r["index"] != sym or r["leg"] != legname or r["date"] >= "2026-10-01": continue
            strike = int(round(float(r["entry_spot"]) / 100.0) * 100)
            exp = next(e for e in EXPIRIES if e >= r["date"])
            out.append(dict(date=r["date"], index=sym, direction=r["direction"],
                            entry_time=r["entry_time"], strike=strike, expiry=exp,
                            lot=LOT[sym], rep=fam, sources=fam, family=fam,
                            base_net=None, base_reason=None))
    return out

def unique_once(legs):
    """Pool legs, keep earliest entry per (date,index,direction). Base wins ties."""
    by = {}
    for l in legs:
        k = (l["date"], l["index"], l["direction"])
        if k not in by or l["entry_time"] < by[k]["entry_time"] or \
           (l["entry_time"] == by[k]["entry_time"] and l["family"] == "BASE"):
            by[k] = l
    return sorted(by.values(), key=lambda x: (x["date"], x["entry_time"]))

def score_legs(legs, stop=50.0, target=90.0, mode="plain", gate=None, delay=0, strike_shift=0):
    """Returns (results list, n_not_computed). gate: fn(stats, leg)->bool keep."""
    res, nc = [], 0
    for l in legs:
        strike = l["strike"] + strike_shift if strike_shift else l["strike"]
        if strike_shift:  # ITM: CE lower strike, PE higher strike
            strike = l["strike"] - 100 if l["direction"] == "CE" else l["strike"] + 100
        cs = candles(l["index"], strike, l["direction"], l["date"], l["expiry"])
        if not cs: nc += 1; continue
        if gate:
            st = entry_bar_stats(cs, l["entry_time"])
            if st is None: nc += 1; continue
            if not gate(st, l): continue
        r = replay(cs, l["entry_time"], l["lot"], stop, target, mode, delay)
        if r is None: nc += 1; continue
        r = {**r, "date": l["date"], "direction": l["direction"], "family": l["family"],
             "rep": l["rep"], "entry_time": l["entry_time"]}
        res.append(r)
    return res, nc

def agg(res, weeks):
    n = len(res); net = round(sum(r["net"] for r in res), 2)
    ft = sum(r["ft"] for r in res)
    return dict(n=n, net=net, ft=ft, ft_pct=round(100.0 * ft / n, 1) if n else 0.0,
                per_week=round(n / weeks, 2) if weeks else 0.0)

def month_end_reds(res):
    """res: Jan-Oct results with date+net. Returns (red_month_ends list, total, month table)."""
    bym = defaultdict(float); cum = 0.0; reds = []; table = {}
    for r in sorted(res, key=lambda x: x["date"]):
        bym[r["date"][:7]] += r["net"]
    for m in sorted(bym):
        cum = round(cum + bym[m], 2); table[m] = (round(bym[m], 2), cum)
        if cum < 0: reds.append(m)
    return reds, round(cum, 2), table
