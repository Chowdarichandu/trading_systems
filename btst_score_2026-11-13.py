#!/usr/bin/env python3
"""BTST PROGRAMME — GATE RUN (2026-11-13). Frozen spec: btst_programme_2026-11-13.md.
Arm 1: Bank Nifty options BTST (V1 full-day-move sign PRIMARY, V2 stack
day-direction; placebos P-REV / P-RANDDIR per variant; EXIT-TS primary,
EXIT-0920 lens). Arm 2: stocks BTST on the frozen 25 (strength rule;
placebos P-REV mirror-weak, P-RANDSEL count-matched random selection;
EXIT-TS primary, EXIT-OPEN lens). Jan-Oct 2026 gate + November lens.
Paper only, real money ₹0. Segments/variants never pooled."""
import csv, json, random, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path.home() / "workspace/trading"))
import pandas as pd
from btst_common import (TR, PremStore, load_bank_spot, load_stock_bars, spot_bar,
                         btst_expiry, atm_strike, trading_days, day_ohlc,
                         EXIT_BARS, WATCHLIST25)

SEED = 20261113
OUTJ = TR / "btst_programme_2026-11-13_results.json"

# ---------------------------------------------------------------- ARM 1 ----
spot = load_bank_spot()
cal = [d for d in trading_days(spot) if "2026-01-01" <= d <= "2026-11-12"]
next_day = {cal[i]: cal[i + 1] for i in range(len(cal) - 1)}
store = PremStore()

def v1_side(day, bars):
    """Full-day move sign from bars with start <= 15:10 ONLY.
    bars: the day's spot bar list (already truncated by caller)."""
    o = next(b for b in bars if b[0] == "09:15")[1]
    ref = next(b for b in bars if b[0] == "15:10")[4]
    move = (ref - o) / o
    if abs(move) < 0.0005:
        return None
    return "CE" if move > 0 else "PE"

def day_sides_v1(day):
    bars = [b for b in spot[day] if b[0] <= "15:10"]
    return v1_side(day, bars)

# truncation / leak audit: corrupt every spot bar after 15:10 (x3 prices)
audit_diffs = 0
for d in cal:
    if d > "2026-11-12":
        continue
    clean = day_sides_v1(d)
    corrupt_bars = [[b[0]] + [x * 3 for x in b[1:]] if b[0] > "15:10" else b for b in spot[d]]
    dirty = v1_side(d, [b for b in corrupt_bars if b[0] <= "15:10"])
    if clean != dirty:
        audit_diffs += 1

# stack day-directions (first leg of the day)
stack_dir = {}
sdf = pd.read_csv(TR / "tuning_bank_fast_2026-11-12_a_stack_fe4_trades.csv")
sdf = sdf.sort_values(["date", "entry_time"])
for d, g in sdf.groupby("date"):
    stack_dir[d] = g.iloc[0]["direction"]
with open(TR / "november_shadow_stack_bank_log.csv") as f:
    for row in csv.DictReader(f):
        if row["direction"] and row["date"] not in stack_dir:
            stack_dir[row["date"]] = row["direction"]

def exit_ts_opt(bars, entry, tgt=60.0, stp=40.0):
    """Sequential close-based target/stop over EXIT_BARS. Returns
    (exit_price, exit_hm, reason) or None if a needed bar is missing
    before any trigger (NC)."""
    for hm in EXIT_BARS:
        if hm not in bars:
            return None
        c = bars[hm][3]
        if c >= entry + tgt:
            return c, hm, "TARGET"
        if c <= entry - stp:
            return c, hm, "STOP"
    return bars["10:25"][3], "10:25", "HARD_1030"

def arm1_trips(side_map, days):
    """side_map: day->side (only days to trade). Returns (trips, nc_days)."""
    trips, nc = [], []
    for D in days:
        side = side_map.get(D)
        if side is None:
            continue
        exp, strike = btst_expiry(D), atm_strike(spot_bar(spot, D, "15:10")[4])
        eb = store.bars(exp, strike, side, D)
        if "15:15" not in eb:
            nc.append((D, "entry bar missing")); continue
        entry = eb["15:15"][3]
        D1 = next_day.get(D)
        xb = store.bars(exp, strike, side, D1) if D1 else {}
        r = exit_ts_opt(xb, entry) if D1 else None
        if r is None:
            nc.append((D, "exit bars missing")); continue
        xp, xhm, reason = r
        lens = xb.get("09:20", (None,) * 4)[3]
        gap_first = xb["09:15"][3] - entry
        spot_gap = None
        if D1 and spot_bar(spot, D1, "09:15") and spot_bar(spot, D, "15:25"):
            sgn = 1 if side == "CE" else -1
            spot_gap = sgn * (spot_bar(spot, D1, "09:15")[1] - spot_bar(spot, D, "15:25")[4]) \
                / spot_bar(spot, D, "15:25")[4] * 100
        trips.append(dict(entry_day=D, exit_day=D1, expiry=exp, strike=strike, side=side,
                          entry=entry, exit=xp, exit_time=xhm, reason=reason,
                          net=round((xp - entry) * 30 - 220, 2),
                          net_lens0920=(round((lens - entry) * 30 - 220, 2) if lens else None),
                          gap_first_pts=round(gap_first, 2),
                          spot_gap_dir_pct=(round(spot_gap, 3) if spot_gap is not None else None)))
    return trips, nc

def stats(trips, lens_key="net"):
    if not trips:
        return dict(total=0.0, n=0, wr=None, months={}, h1=0.0, h2=0.0, ex_top3=0.0, worst=None)
    nets = sorted(t[lens_key] for t in trips)
    months = defaultdict(float)
    for t in trips:
        months[t["entry_day"][:7]] += t[lens_key]
    h1 = sum(t[lens_key] for t in trips if t["entry_day"][:7] <= "2026-05")
    h2 = sum(t[lens_key] for t in trips if t["entry_day"][:7] >= "2026-06")
    return dict(total=round(sum(nets), 2), n=len(nets),
                wr=round(sum(1 for x in nets if x > 0) / len(nets), 3),
                months={k: round(v, 2) for k, v in sorted(months.items())},
                red_months=sum(1 for v in months.values() if v < 0),
                h1=round(h1, 2), h2=round(h2, 2),
                ex_top3=round(sum(nets) - sum(nets[-3:]), 2),
                worst=round(nets[0], 2), best=round(nets[-1], 2))

def gate(st, rev_total, rand_total, nc_n, eligible_n, audit_clean):
    legs = {
        "G1_total>0": st["total"] > 0,
        "G2_halves>0": st["h1"] > 0 and st["h2"] > 0,
        "G3_red_months<=3": st.get("red_months", 99) <= 3,
        "G4_ex_top3>0": st["ex_top3"] > 0,
        "G5_beats_placebos": st["total"] > rev_total and st["total"] > rand_total,
        "G6_timing_audit": audit_clean,
        "G7_NC<=10%": (nc_n / eligible_n <= 0.10) if eligible_n else False,
    }
    return legs, all(legs.values())

gate_days = [d for d in cal if d <= "2026-10-29" and next_day.get(d, "9999") <= "2026-10-30"]
v1_map = {d: day_sides_v1(d) for d in gate_days}
v1_elig = [d for d in gate_days if v1_map[d]]
v2_map = {d: stack_dir[d] for d in gate_days if d in stack_dir}
rev1_map = {d: ("PE" if s == "CE" else "CE") for d, s in v1_map.items() if s}
rev2_map = {d: ("PE" if s == "CE" else "CE") for d, s in v2_map.items()}
rng = random.Random(SEED)
rand1_map = {d: rng.choice(["CE", "PE"]) for d in v1_elig}
rng = random.Random(SEED + 1)
rand2_map = {d: rng.choice(["CE", "PE"]) for d in sorted(v2_map)}

A1 = {}
for name, smap, elig in [("V1", v1_map, len(v1_elig)), ("V2", v2_map, len(v2_map)),
                         ("P-REV-V1", rev1_map, len(v1_elig)), ("P-REV-V2", rev2_map, len(v2_map)),
                         ("P-RANDDIR-V1", rand1_map, len(v1_elig)), ("P-RANDDIR-V2", rand2_map, len(v2_map))]:
    trips, nc = arm1_trips(smap, gate_days)
    A1[name] = dict(trips=trips, nc=nc, stats=stats(trips), stats_lens=stats(trips, "net_lens0920"))
for name, rev, rnd in [("V1", "P-REV-V1", "P-RANDDIR-V1"), ("V2", "P-REV-V2", "P-RANDDIR-V2")]:
    legs, ok = gate(A1[name]["stats"], A1[rev]["stats"]["total"], A1[rnd]["stats"]["total"],
                    len(A1[name]["nc"]), len(v1_elig) if name == "V1" else len(v2_map),
                    audit_diffs == 0)
    A1[name]["gate"] = legs; A1[name]["PASS"] = ok

# Arm 1 November lens (entries Nov 2-11 scored; Nov 12 pending)
nov_days = [d for d in cal if "2026-11-02" <= d <= "2026-11-11"]
nov_v1 = {d: day_sides_v1(d) for d in nov_days}
nov_v2 = {d: stack_dir[d] for d in nov_days if d in stack_dir}
nov = {}
for name, smap in [("V1", nov_v1), ("V2", nov_v2)]:
    trips, nc = arm1_trips(smap, nov_days)
    nov[name] = dict(trips=trips, nc=nc, total=round(sum(t["net"] for t in trips), 2))
pend = {}
for name, smap in [("V1", {d: day_sides_v1(d) for d in ["2026-11-12"]}),
                   ("V2", {"2026-11-12": stack_dir.get("2026-11-12")})]:
    D = "2026-11-12"; side = smap.get(D)
    if side:
        exp, strike = btst_expiry(D), atm_strike(spot_bar(spot, D, "15:10")[4])
        eb = store.bars(exp, strike, side, D)
        pend[name] = dict(entry_day=D, expiry=exp, strike=strike, side=side,
                          entry=(eb["15:15"][3] if "15:15" in eb else None),
                          status="PENDING — exit is the morning of 2026-11-13")

# worst overnight gaps (Arm 1, V1+V2)
def worst_gaps(trips):
    if not trips:
        return {}
    wg = min(trips, key=lambda t: t["gap_first_pts"])
    ws = min((t for t in trips if t["spot_gap_dir_pct"] is not None),
             key=lambda t: t["spot_gap_dir_pct"], default=None)
    return dict(worst_first_bar_pts=wg["gap_first_pts"], worst_first_bar_inr=round(wg["gap_first_pts"] * 30, 2),
                worst_first_bar_day=wg["entry_day"],
                worst_spot_gap_dir_pct=(ws["spot_gap_dir_pct"] if ws else None),
                worst_spot_gap_day=(ws["entry_day"] if ws else None))

# entry-bar cross-store agreement audit (option_5m vs prem_bank, 15:15 close)
agree = diff = 0; maxdiff = 0.0
for D in gate_days:
    exp, strike = btst_expiry(D), atm_strike(spot_bar(spot, D, "15:10")[4])
    for side in ("CE", "PE"):
        k = (exp, strike, side, D)
        pk = f"{exp}|{strike}|{side}"
        if k in store.opt and pk in store.prem and D in store.prem[pk] and "15:15" in store.prem[pk][D]:
            a = store.opt[k]["15:15"][3]; b = float(store.prem[pk][D]["15:15"][3])
            if abs(a - b) < 1e-9: agree += 1
            else:
                diff += 1; maxdiff = max(maxdiff, abs(a - b))

# ---------------------------------------------------------------- ARM 2 ----
stocks = {s: load_stock_bars(s) for s in WATCHLIST25}
cal2 = [d for d in cal]  # index calendar (full sessions) as the shared calendar
def stock_signal(sym, D):
    bars = stocks[sym].get(D)
    if not bars or len(bars) < 70:
        return None
    days = sorted(stocks[sym].keys())
    i = days.index(D)
    if i == 0:
        return None
    prev = day_ohlc(stocks[sym][days[i - 1]])[3]
    o, h, l, c = day_ohlc(bars)
    if h == l or prev <= 0:
        return None
    return dict(gain=c / prev - 1, cs=(c - l) / (h - l) * 100, close=c)

def select(D, mode):
    scored = []
    for s in WATCHLIST25:
        sig = stock_signal(s, D)
        if sig is None:
            continue
        if mode == "REAL" and sig["gain"] >= 0.01 and sig["cs"] >= 75:
            scored.append((s, sig))
        elif mode == "MIRROR" and sig["gain"] <= -0.01 and sig["cs"] <= 25:
            scored.append((s, sig))
    if mode == "REAL":
        scored.sort(key=lambda x: (-x[1]["gain"], x[0]))
    else:
        scored.sort(key=lambda x: (x[1]["gain"], x[0]))
    return scored[:5]

def exit_ts_stock(bars, entry):
    for hm in EXIT_BARS:
        if hm not in bars:
            return None
        c = bars[hm][3]
        if c >= entry * 1.010:
            return c, hm, "TARGET"
        if c <= entry * 0.993:
            return c, hm, "STOP"
    return bars["10:25"][3], "10:25", "HARD_1030"

def arm2_run(pickfn, days):
    trips, nc = [], []
    for D in days:
        picks = pickfn(D)
        D1 = next_day.get(D)
        for s, sig in picks:
            entry = day_ohlc(stocks[s][D])[3]
            b1 = {b[0]: b for b in stocks[s].get(D1, [])} if D1 else {}
            r = exit_ts_stock(b1, entry) if D1 else None
            if r is None:
                nc.append((D, s)); continue
            xp, xhm, reason = r
            open_px = b1["09:15"][4]
            trips.append(dict(entry_day=D, exit_day=D1, stock=s, gain_pct=round(sig["gain"] * 100, 2),
                              cs=round(sig["cs"], 1), entry=entry, exit=xp, exit_time=xhm,
                              reason=reason, net=round((xp - entry) * 100 - 40, 2),
                              net_lens_open=round((open_px - entry) * 100 - 40, 2),
                              gap_first_pct=round((open_px / entry - 1) * 100, 3)))
    return trips, nc

gate_days2 = [d for d in cal if d <= "2026-10-29" and next_day.get(d, "9999") <= "2026-10-30"]
real_picks = {D: select(D, "REAL") for D in gate_days2}
def rand_picks(D):
    n = len(real_picks[D])
    if n == 0:
        return []
    r = random.Random(f"btst-randsel-{SEED}-{D}")
    return [(s, stock_signal(s, D) or dict(gain=0.0, cs=0.0)) for s in r.sample(WATCHLIST25, n)]

A2 = {}
for name, fn in [("REAL", lambda D: real_picks[D]), ("P-REV-MIRROR", lambda D: select(D, "MIRROR")),
                 ("P-RANDSEL", rand_picks)]:
    trips, nc = arm2_run(fn, gate_days2)
    A2[name] = dict(trips=trips, nc=nc, stats=stats(trips), stats_lens=stats(trips, "net_lens_open"))
elig2 = sum(len(v) for v in real_picks.values())
# Arm-2 leak audit: corrupt all bars after day D (x3) -> selection must not change
a2_diffs = 0
for D in gate_days2[::17]:
    before = [s for s, _ in real_picks[D]]
    saved = {}
    for s in WATCHLIST25:
        saved[s] = stocks[s]
        stocks[s] = {d: ([[b[0]] + [x * 3 for x in b[1:]] for b in bars] if d > D else bars)
                     for d, bars in saved[s].items()}
    after = [s for s, _ in select(D, "REAL")]
    stocks.update(saved)
    if before != after:
        a2_diffs += 1
legs2, ok2 = gate(A2["REAL"]["stats"], A2["P-REV-MIRROR"]["stats"]["total"],
                  A2["P-RANDSEL"]["stats"]["total"], len(A2["REAL"]["nc"]), max(elig2, 1),
                  a2_diffs == 0)
A2["REAL"]["gate"] = legs2; A2["REAL"]["PASS"] = ok2

# Arm 2 November lens
nov2 = {}
trips_n, nc_n = arm2_run(lambda D: select(D, "REAL"), nov_days)
nov2["REAL"] = dict(trips=trips_n, nc=nc_n, total=round(sum(t["net"] for t in trips_n), 2))
pend2 = [dict(stock=s, gain_pct=round(sig["gain"] * 100, 2), cs=round(sig["cs"], 1),
              entry=day_ohlc(stocks[s]["2026-11-12"])[3], status="PENDING — exit morning of 2026-11-13")
         for s, sig in select("2026-11-12", "REAL")]

# cross-store validation (sarvaritu_fwd vs period stores), 3 stocks
xval = {}
for s in ["ASTRAL", "HDFCBANK", "TATASTEEL"]:
    ref = pd.read_csv(TR / f"stocks_october/data/{s}_spot_5m.csv")
    ref["d"] = ref["timestamp"].str[:10]
    nd = same = 0
    for d, g in ref.groupby("d"):
        if d in stocks[s]:
            a = day_ohlc(stocks[s][d]); b = (g["open"].iloc[0], g["high"].max(), g["low"].min(), g["close"].iloc[-1])
            nd += 1; same += int(all(abs(x - y) < 1e-6 for x, y in zip(a, b)))
    xval[s] = dict(days_compared=nd, days_identical=same)

# ---------------------------------------------------------------- outputs ----
def dump_trips(name, trips):
    if not trips:
        return
    keys = list(trips[0].keys())
    with open(TR / f"btst_programme_2026-11-13_{name}_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(trips)

for n, v in A1.items():
    dump_trips(f"arm1_{n.lower().replace('-', '_')}", v["trips"])
for n, v in A2.items():
    dump_trips(f"arm2_{n.lower().replace('-', '_')}", v["trips"])
dump_trips("arm1_nov_v1", nov["V1"]["trips"]); dump_trips("arm1_nov_v2", nov["V2"]["trips"])
dump_trips("arm2_nov_real", nov2["REAL"]["trips"])

results = dict(
    arm1={n: dict(stats=v["stats"], stats_lens0920=v["stats_lens"], nc=len(v["nc"]),
                  gate=v.get("gate"), PASS=v.get("PASS"),
                  worst_gaps=worst_gaps(v["trips"])) for n, v in A1.items()},
    arm1_meta=dict(eligible_v1_days=len(v1_elig), stack_days=len(v2_map), gate_days=len(gate_days),
                   timing_audit_diffs=audit_diffs, cross_store_agree=agree, cross_store_diff=diff,
                   cross_store_maxdiff=maxdiff),
    arm1_november={n: dict(total=v["total"], n=len(v["trips"]), trips=v["trips"], nc=v["nc"])
                   for n, v in nov.items()},
    arm1_nov_pending=pend,
    arm2={n: dict(stats=v["stats"], stats_lens_open=v["stats_lens"], nc=len(v["nc"]),
                  gate=v.get("gate"), PASS=v.get("PASS")) for n, v in A2.items()},
    arm2_meta=dict(eligible_picks=elig2, leak_audit_sample_diffs=a2_diffs, xval=xval,
                   worst_gap=(min((t for t in A2["REAL"]["trips"]), key=lambda t: t["gap_first_pct"],
                                  default=None))),
    arm2_november=dict(total=nov2["REAL"]["total"], n=len(nov2["REAL"]["trips"]),
                       trips=nov2["REAL"]["trips"], nc=nov2["REAL"]["nc"]),
    arm2_nov_pending=pend2,
)
OUTJ.write_text(json.dumps(results, indent=1, default=str))

# independent re-sum from the written CSVs
chk = {}
for n in A1:
    p = TR / f"btst_programme_2026-11-13_arm1_{n.lower().replace('-', '_')}_trades.csv"
    if p.exists():
        chk[f"A1-{n}"] = round(pd.read_csv(p)["net"].sum(), 2)
for n in A2:
    p = TR / f"btst_programme_2026-11-13_arm2_{n.lower().replace('-', '_')}_trades.csv"
    if p.exists():
        chk[f"A2-{n}"] = round(pd.read_csv(p)["net"].sum(), 2)
exp = {**{f"A1-{n}": A1[n]["stats"]["total"] for n in A1},
       **{f"A2-{n}": A2[n]["stats"]["total"] for n in A2}}
assert chk == exp, (chk, exp)
print("RE-SUM OK:", chk)
print(json.dumps({k: results[k] for k in ("arm1_meta", "arm2_meta")}, indent=1, default=str))
for n in ("V1", "V2"):
    print("A1", n, A1[n]["stats"], "PASS:", A1[n]["PASS"], A1[n]["gate"])
for n in ("P-REV-V1", "P-RANDDIR-V1", "P-REV-V2", "P-RANDDIR-V2"):
    print("A1", n, A1[n]["stats"]["total"], A1[n]["stats"]["n"])
print("A1 NOV", {n: (nov[n]["total"], len(nov[n]["trips"])) for n in nov}, "PEND", pend)
print("A2 REAL", A2["REAL"]["stats"], "PASS:", A2["REAL"]["PASS"], A2["REAL"]["gate"])
for n in ("P-REV-MIRROR", "P-RANDSEL"):
    print("A2", n, A2[n]["stats"]["total"], A2[n]["stats"]["n"])
print("A2 NOV", nov2["REAL"]["total"], len(nov2["REAL"]["trips"]), "PEND", pend2)
