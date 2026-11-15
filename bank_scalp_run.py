#!/usr/bin/env python3
"""Bank Nifty SCALPING feasibility study — first scoring WITH full controls in the same run.
Definitions frozen in bank_scalp_study.md (2026-10-31 15:54 IST) BEFORE this script ran.
Bank Nifty ONLY. Paper, real Rs0. Premiums per 1 lot (30), cost Rs220/trade.
Data: data/banknifty-2026-*/spot_5m.csv + option_5m.csv (local, pre-existing);
Red bands: data/banknifty-2026-jul-oct/red_bands_v2.json (Jul-Oct only)."""
import csv, json, glob, random, sys
from pathlib import Path
from collections import defaultdict

TR = Path.home() / "workspace/trading"
DATA = TR / "data"
LOT, COST = 30, 220.0
EXPIRIES = ["2026-01-27","2026-02-24","2026-03-30","2026-04-28","2026-05-26",
            "2026-06-30","2026-07-28","2026-08-25","2026-09-29","2026-10-27"]

def expiry_for(day):
    for e in EXPIRIES:
        if e >= day: return e
    return None

def tmin(t):  # "HH:MM" -> minutes
    return int(t[:2]) * 60 + int(t[3:5])

# ---------------- load spot ----------------
spot = {}  # date -> list of (time,o,h,l,c)
conflicts = 0
for p in sorted(glob.glob(str(DATA / "banknifty-2026-*" / "spot_5m.csv"))):
    for r in csv.DictReader(open(p)):
        d, t = r["timestamp"][:10], r["timestamp"][11:16]
        bar = (t, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"]))
        day = spot.setdefault(d, {})
        if t in day and day[t] != bar: conflicts += 1
        day.setdefault(t, bar)
spot = {d: [day[t] for t in sorted(day)] for d, day in spot.items()}
DAYS = sorted(spot)
print(f"spot days: {len(DAYS)} {DAYS[0]}..{DAYS[-1]} conflicts={conflicts}")

# ---------------- load options ----------------
opt = {}  # (date, strike, type, expiry) -> list of (time,o,h,l,c)
for p in sorted(glob.glob(str(DATA / "banknifty-2026-*" / "option_5m.csv"))):
    for r in csv.DictReader(open(p)):
        d, t = r["timestamp"][:10], r["timestamp"][11:16]
        key = (d, int(r["strike"]), r["option_type"], r["expiry"])
        bar = (t, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"]))
        day = opt.setdefault(key, {})
        if t not in day: day[t] = bar
opt = {k: [day[t] for t in sorted(day)] for k, day in opt.items()}
print(f"option series: {len(opt)}")

# ---------------- load red bands (Jul-Oct) ----------------
bands = {}
bp = DATA / "banknifty-2026-jul-oct" / "red_bands_v2.json"
if bp.exists():
    raw = json.loads(bp.read_text()).get("per_date", {})
    for d, v in raw.items():
        lv = []
        for b in v.get("master_bands", []) + v.get("tactical_ledges", []):
            lv.append((float(b["low"]), float(b["high"])))
        bands[d] = lv
print(f"red band days: {len(bands)}")

# ---------------- prior-day levels ----------------
def pd_levels(day):
    i = DAYS.index(day)
    if i == 0: return None
    prev = spot[DAYS[i - 1]]
    return max(b[2] for b in prev), min(b[3] for b in prev), prev[-1][4]

# ---------------- exit replay ----------------
def replay(bars, entry_time, target_pts, stop_pts, ts_bars):
    """bars: option bars for the day. Returns dict or None (NOT_COMPUTED)."""
    idx = {b[0]: i for i, b in enumerate(bars)}
    if entry_time not in idx: return None
    i0 = idx[entry_time]
    entry = bars[i0][1]
    stop, target = entry - stop_pts, entry + target_pts
    for i in range(i0, len(bars)):
        t, o, h, l, c = bars[i]
        if t > "15:10": return None  # data past square-off without exit -> NC
        if l <= stop:
            return dict(exit_time=t, exit=stop, reason="stop", hold=i - i0 + 1, entry=entry)
        if h >= target:
            return dict(exit_time=t, exit=target, reason="target", hold=i - i0 + 1, entry=entry)
        if i - i0 + 1 >= ts_bars:
            return dict(exit_time=t, exit=c, reason="time_stop", hold=i - i0 + 1, entry=entry)
        if t == "15:10":
            return dict(exit_time=t, exit=c, reason="square_off", hold=i - i0 + 1, entry=entry)
    return None  # series ended before any exit rule fired

def score_signal(day, direction, signal_time, entry_time, target_pts, stop_pts, ts_bars,
                 spot_close_ref):
    strike = int(round(spot_close_ref / 100.0) * 100)
    exp = expiry_for(day)
    bars = opt.get((day, strike, direction, exp))
    if not bars: return None, strike, exp
    r = replay(bars, entry_time, target_pts, stop_pts, ts_bars)
    if r is None: return None, strike, exp
    net = round((r["exit"] - r["entry"]) * LOT - COST, 2)
    return dict(date=day, direction=direction, signal_time=signal_time, entry_time=entry_time,
                strike=strike, expiry=exp, entry_premium=r["entry"], exit_time=r["exit_time"],
                exit_premium=r["exit"], exit_reason=r["reason"], hold_bars=r["hold"],
                gross_pts=round(r["exit"] - r["entry"], 2), net_inr=net,
                ft=1 if r["reason"] == "target" else 0), strike, exp

# ---------------- signal generation ----------------
def gen_S1(day):
    bars = spot[day]
    if len(bars) < 4 or [b[0] for b in bars[:3]] != ["09:15", "09:20", "09:25"]: return []
    orh = max(b[2] for b in bars[:3]); orl = min(b[3] for b in bars[:3])
    out, last_entry = [], None
    for i in range(3, len(bars) - 1):
        t, o, h, l, c = bars[i]
        if t < "09:30" or t > "13:30": continue
        pc = bars[i - 1][4]
        side = None
        if c > orh and pc <= orh: side = "CE"
        elif c < orl and pc >= orl: side = "PE"
        if not side: continue
        entry_time = bars[i + 1][0]
        if last_entry is not None and tmin(entry_time) - tmin(last_entry) < 30: continue
        out.append(dict(direction=side, signal_time=t, entry_time=entry_time,
                        trigger=f"OR{'H' if side=='CE' else 'L'}", spot_ref=c))
        last_entry = entry_time
        if len(out) >= 3: break
    return out

def gen_S2(day):
    bars = spot[day]
    lv = pd_levels(day)
    if lv is None: return []
    pdh, pdl, pdc = lv
    levels = [("PDH", pdh, "R"), ("PDL", pdl, "S"), ("PDC", pdc, "B")]
    for lo, hi in bands.get(day, []):
        levels.append((f"BAND_hi_{hi:.2f}", hi, "R"))
        levels.append((f"BAND_lo_{lo:.2f}", lo, "S"))
    raw = []
    for i in range(1, len(bars) - 1):
        t, o, h, l, c = bars[i]
        if t < "09:35" or t > "14:50": continue
        pc = bars[i - 1][4]
        for lid, L, side in levels:
            if side in ("R", "B") and h > L and pc <= L and c <= L + (h - L) / 2.0:
                raw.append((t, lid, "PE"))
            if side in ("S", "B") and l < L and pc >= L and c >= L - (L - l) / 2.0:
                raw.append((t, lid, "CE"))
    raw.sort()
    out, last_trig = [], {}
    idx = {b[0]: i for i, b in enumerate(bars)}
    for t, lid, side in raw:
        if lid in last_trig and tmin(t) - tmin(last_trig[lid]) < 60: continue
        i = idx[t]
        out.append(dict(direction=side, signal_time=t, entry_time=bars[i + 1][0],
                        trigger=lid, spot_ref=bars[i][4]))
        last_trig[lid] = t
        if len(out) >= 3: break
    return out

def gen_S3(day):
    bars = spot[day]
    out, last_entry = [], None
    for i in range(3, len(bars) - 1):
        t, o, h, l, c = bars[i]
        if t < "09:45" or t > "14:30": continue
        body = c - o
        if abs(body) < 0.0015 * o: continue
        ph = max(b[2] for b in bars[i - 3:i]); pl = min(b[3] for b in bars[i - 3:i])
        side = None
        if body > 0 and c > ph: side = "CE"
        elif body < 0 and c < pl: side = "PE"
        if not side: continue
        entry_time = bars[i + 1][0]
        if last_entry is not None and tmin(entry_time) - tmin(last_entry) < 20: continue
        out.append(dict(direction=side, signal_time=t, entry_time=entry_time,
                        trigger="IMPULSE", spot_ref=c))
        last_entry = entry_time
        if len(out) >= 4: break
    return out

TECH = {
    "S1": dict(gen=gen_S1, target=25.0, stop=20.0, ts=3),
    "S2": dict(gen=gen_S2, target=22.0, stop=18.0, ts=4),
    "S3": dict(gen=gen_S3, target=22.0, stop=18.0, ts=2),
}

def run_technique(name, delay_bars=0):
    cfg = TECH[name]
    trades, nc, signals = [], 0, 0
    for day in DAYS:
        bars = spot[day]
        idx = {b[0]: i for i, b in enumerate(bars)}
        for s in cfg["gen"](day):
            signals += 1
            et = s["entry_time"]
            if delay_bars:
                j = idx.get(et)
                if j is None or j + delay_bars >= len(bars): nc += 1; continue
                et = bars[j + delay_bars][0]
            r, strike, exp = score_signal(day, s["direction"], s["signal_time"], et,
                                          cfg["target"], cfg["stop"], cfg["ts"], s["spot_ref"])
            if r is None: nc += 1; continue
            r["technique"] = name; r["trigger"] = s["trigger"]
            trades.append(r)
    return trades, nc, signals

def stats(trades):
    n = len(trades)
    net = round(sum(t["net_inr"] for t in trades), 2)
    gross_money = round(sum(t["gross_pts"] for t in trades) * LOT, 2)
    wins = sum(1 for t in trades if t["net_inr"] > 0)
    ft = sum(t["ft"] for t in trades)
    return dict(n=n, net=net, net_cost0=round(net + COST * n, 2), gross_money=gross_money,
                win_pct=round(100.0 * wins / n, 1) if n else 0.0,
                ft_pct=round(100.0 * ft / n, 1) if n else 0.0,
                expectancy=round(net / n, 2) if n else 0.0,
                avg_hold=round(sum(t["hold_bars"] for t in trades) / n, 2) if n else 0.0,
                cost_pct_of_gross=(round(100.0 * COST * n / gross_money, 1)
                                   if gross_money > 0 else None))

def halves(trades):
    h1 = [t for t in trades if t["date"] <= "2026-05-31"]
    h2 = [t for t in trades if t["date"] >= "2026-06-01"]
    return stats(h1), stats(h2)

def month_table(trades):
    bym = defaultdict(float); cum = 0.0; out = {}
    for t in trades: bym[t["date"][:7]] += t["net_inr"]
    for m in [f"2026-{i:02d}" for i in range(1, 11)]:
        cum = round(cum + bym.get(m, 0.0), 2)
        out[m] = (round(bym.get(m, 0.0), 2), cum)
    return out

def random_placebo(name, n_target):
    cfg = TECH[name]
    rng = random.Random(42)
    totals = []
    for _ in range(20):
        tot, got, tries = 0.0, 0, 0
        while got < n_target and tries < n_target * 12:
            tries += 1
            day = rng.choice(DAYS)
            bars = spot[day]
            cand = [i for i, b in enumerate(bars) if "09:35" <= b[0] <= "14:55" and i >= 1]
            if not cand: continue
            i = rng.choice(cand)
            direction = rng.choice(["CE", "PE"])
            r, _, _ = score_signal(day, direction, bars[i - 1][0], bars[i][0],
                                   cfg["target"], cfg["stop"], cfg["ts"], bars[i - 1][4])
            if r is None: continue
            tot += r["net_inr"]; got += 1
        totals.append(round(tot, 2))
    return dict(mean=round(sum(totals) / len(totals), 2), min=min(totals), max=max(totals))

results = {}
for name in ("S1", "S2", "S3"):
    trades, nc, signals = run_technique(name)
    # timing audit: entry strictly after signal on every trade
    violations = sum(1 for t in trades if t["entry_time"] <= t["signal_time"])
    # write CSV
    cols = ["date","technique","direction","trigger","signal_time","entry_time","strike",
            "expiry","entry_premium","exit_time","exit_premium","exit_reason","hold_bars",
            "gross_pts","net_inr"]
    with open(TR / f"bank_scalp_{name}_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for t in sorted(trades, key=lambda x: (x["date"], x["entry_time"])):
            w.writerow({k: t[k] for k in cols})
    # independent re-sum from the written CSV
    resum = round(sum(float(r["net_inr"]) for r in
                      csv.DictReader(open(TR / f"bank_scalp_{name}_trades.csv"))), 2)
    lag, lag_nc, _ = run_technique(name, delay_bars=1)
    st = stats(trades); h1, h2 = halves(trades)
    top3 = sorted((t["net_inr"] for t in trades), reverse=True)[:3]
    plac = random_placebo(name, st["n"]) if st["n"] else {"mean": 0.0, "min": 0.0, "max": 0.0}
    results[name] = dict(stats=st, halves=[h1, h2], months=month_table(trades),
                         signals=signals, not_computed=nc, audit_violations=violations,
                         resum=resum, resum_match=abs(resum - st["net"]) < 0.01,
                         ex_top3=round(st["net"] - sum(top3), 2),
                         lag_placebo=dict(stats(lag), nc=lag_nc),
                         random_placebo=plac)
    print(f"== {name}: {json.dumps(results[name], indent=1)}")

json.dump(results, open(TR / "bank_scalp_summary.json", "w"), indent=1)
print("DONE")
