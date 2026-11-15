"""BANK v22 PHASE 2 — BANK-EVE-06 population (pre-registered 2026-11-03,
november_rsi_bank_log.md) scored as an increment on the v22 assembled book.

(a) RE-ENTRY: on a day with a v22 leg stopped at the full -50 stop, if spot
    closes back through the morning-range extreme (stopped leg's side) on a
    5-min bar at/after 12:00 and at/after the stop's exit bar -> re-enter
    same side, ATM at next bar open, G0 exits, max 1/day. Skipped if the
    day's realised v22 net (legs exited on/before the trigger bar) is
    already <= -Rs 3,000 at the trigger.
(b) AFTERNOON SLEEVE: first fresh day-range break (spot close beyond the
    running day high/low built from strictly earlier bars) at/after 12:30,
    ATM at next bar open, G0 exits, max 1/day. Combined book: sleeve only
    on days with NO re-entry taken (pre-registered day-level rule).

Morning range = day's 09:15-11:59 spot high/low (documented approximation;
the stopped legs' own setup ranges are not in the leg record).
G0 exits (frozen November convention): intrabar on premium bars, stop
before target, entry bar included, fills at the level (stop -> net
-Rs 1,720, target -> +Rs 2,480 per 1 lot of 30, Rs 220/trade); square-off
at the 15:10 bar open if untouched through the 15:05 bar.
ATM = nearest 100 to the entry bar's spot open (score_hunt convention).
Expiry = store-derived monthly calendar (chains trading on >=10 dates),
first expiry >= entry date — the same chain the store carries that day.
Basis: Bank Nifty option premiums per 1 lot (30), Rs 220/trade, UNIQUE-ONCE.
"""
import json, csv
from collections import defaultdict

TR = "/home/hatch/workspace/trading"
LOT, COST = 30, 220.0
STOP_PTS, TGT_PTS = 50.0, 90.0
DAY_CAP = -3000.0

spot_raw = json.load(open(f"{TR}/daily2leg/spot.json"))["BANKNIFTY"]
prem = json.load(open(f"{TR}/daily2leg/prem_bank.json"))

DAYS = sorted(d for d in spot_raw
              if "2026-01-01" <= d <= "2026-10-31" and len(spot_raw[d]) >= 74)
SPOT = {d: {b[0]: (b[1], b[2], b[3], b[4]) for b in spot_raw[d]} for d in DAYS}
TIMES = {d: [b[0] for b in spot_raw[d]] for d in DAYS}

# ---- store-derived monthly expiry calendar -------------------------------
chain_days = defaultdict(set)
for k, v in prem.items():
    for d in v:
        chain_days[k.split("|")[0]].add(d)
MONTHLY = sorted(e for e, ds in chain_days.items() if len(ds) >= 10)

def expiry_for(d):
    for e in MONTHLY:
        if d <= e:
            return e
    # dates after the last in-window monthly (2026-10-28..30): the store
    # carries exactly one chain those days (2026-11-23, the next monthly —
    # the same tail entry as score_hunt's BANK_MONTHLY). Use it iff unique.
    present = {k.split("|")[0] for k, v in prem.items() if d in v}
    return next(iter(present)) if len(present) == 1 else None

def atm(s):
    lo = int(s // 100 * 100)
    return lo if (s - lo) <= (lo + 100 - s) else lo + 100

def add_min(t, m):
    h, mm = int(t[:2]), int(t[3:])
    mm += m
    h += mm // 60
    mm %= 60
    return f"{h:02d}:{mm:02d}"

def prem_day(exp, strike, typ, d):
    cd = prem.get(f"{exp}|{int(strike)}|{typ}", {}).get(d)
    if cd is None:
        return None
    return {t: tuple(float(x) for x in v) for t, v in cd.items()}

def sim_g0(pd, entry_time, entry_prem):
    """G0 exits on premium bars. Returns (exit_time, exit_prem, reason)."""
    stop_lvl, tgt_lvl = entry_prem - STOP_PTS, entry_prem + TGT_PTS
    for t in sorted(pd):
        if t < entry_time or t > "15:05":
            continue
        o, h, l, c = pd[t]
        if l <= stop_lvl:
            return t, stop_lvl, "stop"
        if h >= tgt_lvl:
            return t, tgt_lvl, "target"
    if "15:10" in pd:
        return "15:10", pd["15:10"][0], "square_off"
    last = max(t for t in pd if t <= "15:05")
    return last, pd[last][3], "path_end"

def build_leg(d, side, trig_time, entry_time, set_name):
    """Returns (leg_dict, status) — status 'ok' or an NC reason."""
    exp = expiry_for(d)
    s_open = SPOT[d][entry_time][0]
    strike = atm(s_open)
    pd = prem_day(exp, strike, side, d)
    if pd is None:
        return None, f"NC:no_contract {exp}|{strike}|{side}"
    if entry_time not in pd:
        return None, f"NC:no_entry_bar {exp}|{strike}|{side}@{entry_time}"
    entry_prem = pd[entry_time][0]
    xt, xp, reason = sim_g0(pd, entry_time, entry_prem)
    net = round((xp - entry_prem) * LOT - COST, 2)
    leg = {"date": d, "set": set_name, "direction": side,
           "expiry": exp, "strike": strike,
           "trigger_time": trig_time, "entry_time": entry_time,
           "entry_premium": entry_prem, "exit_time": xt,
           "exit_premium": xp, "exit_reason": reason, "net_inr": net}
    return leg, "ok"

def next_bar(d, t):
    ts = TIMES[d]
    i = ts.index(t)
    return ts[i + 1] if i + 1 < len(ts) else None

# ---- v22 base book ---------------------------------------------------------
base = list(csv.DictReader(open(f"{TR}/bank_v22_phase1_trades.csv")))
base_by_day = defaultdict(list)
for r in base:
    base_by_day[r["date"]].append(r)
BASE_TOTAL = round(sum(float(r["net_inr"]) for r in base), 2)
assert BASE_TOTAL == 91450.50 and len(base) == 90, (BASE_TOTAL, len(base))

def realised_before(d, trig_time):
    """v22 nets of legs exited on/before the trigger bar (known when the
    re-entry decision executes at the next bar open)."""
    return round(sum(float(r["net_inr"]) for r in base_by_day.get(d, [])
                     if r["exit_time"] <= trig_time), 2)

# ---- (a) RE-ENTRY ----------------------------------------------------------
def find_reentry(d, shift_min=0):
    stops = [r for r in base_by_day.get(d, []) if r["exit_reason"] == "stop"]
    if not stops:
        return None
    leg0 = sorted(stops, key=lambda r: r["exit_time"])[0]
    side = leg0["direction"]
    b, ts = SPOT[d], TIMES[d]
    mh = max(b[t][1] for t in ts if t <= "11:55")
    ml = min(b[t][2] for t in ts if t <= "11:55")
    start = add_min(max("12:00", leg0["exit_time"]), shift_min)
    for t in ts:
        if t < start:
            continue
        c = b[t][3]
        if (side == "CE" and c > mh) or (side == "PE" and c < ml):
            return {"side": side, "trig": t, "stop_exit": leg0["exit_time"],
                    "extreme": mh if side == "CE" else ml}
    return None

A_legs, A_blocked, A_nc = [], [], []
A_shift_legs, A_shift_nc = [], []
for d in DAYS:
    for shift, legs_out, nc_out, name in (
            (0, A_legs, A_nc, "A_reentry"), (60, A_shift_legs, A_shift_nc, "A_shift60")):
        f = find_reentry(d, shift)
        if not f:
            continue
        if realised_before(d, f["trig"]) <= DAY_CAP:
            if shift == 0:
                A_blocked.append({"date": d, "trigger": f["trig"],
                                   "realised": realised_before(d, f["trig"])})
            continue
        et = next_bar(d, f["trig"])
        if et is None or et > "15:05":
            nc_out.append({"date": d, "why": "trigger_no_time", "trigger": f["trig"]})
            continue
        leg, st = build_leg(d, f["side"], f["trig"], et, name)
        if leg:
            leg["stop_exit_time"] = f["stop_exit"]
            legs_out.append(leg)
        else:
            nc_out.append({"date": d, "why": st, "trigger": f["trig"]})

# ---- (b) AFTERNOON SLEEVE ---------------------------------------------------
def find_sleeve(d):
    b, ts = SPOT[d], TIMES[d]
    for t in ts:
        if t < "12:30":
            continue
        prior = [x for x in ts if x < t]
        rh = max(b[x][1] for x in prior)
        rl = min(b[x][2] for x in prior)
        c = b[t][3]
        if c > rh:
            return {"side": "CE", "trig": t}
        if c < rl:
            return {"side": "PE", "trig": t}
    return None

B_std_legs, B_nc = [], []
B_flip_legs, B_flip_nc = [], []
for d in DAYS:
    f = find_sleeve(d)
    if not f:
        continue
    et = next_bar(d, f["trig"])
    if et is None or et > "15:05":
        B_nc.append({"date": d, "why": "trigger_no_time", "trigger": f["trig"]})
        continue
    leg, st = build_leg(d, f["side"], f["trig"], et, "B_sleeve")
    if leg:
        B_std_legs.append(leg)
    else:
        B_nc.append({"date": d, "why": st, "trigger": f["trig"]})
    flip = "PE" if f["side"] == "CE" else "CE"
    leg2, st2 = build_leg(d, flip, f["trig"], et, "B_flip")
    if leg2:
        B_flip_legs.append(leg2)
    else:
        B_flip_nc.append({"date": d, "why": st2, "trigger": f["trig"]})

A_days = {l["date"] for l in A_legs}
B_comb_legs = [dict(l, **{"set": "B_sleeve_combined"})
               for l in B_std_legs if l["date"] not in A_days]

# chronological single-afternoon-trade sensitivity
chrono_legs = []
for d in DAYS:
    fa = find_reentry(d, 0)
    fb = find_sleeve(d)
    cands = []
    if fa and realised_before(d, fa["trig"]) > DAY_CAP:
        cands.append(("A", fa))
    if fb:
        cands.append(("B", fb))
    if not cands:
        continue
    kind, f = min(cands, key=lambda kv: kv[1]["trig"])
    et = next_bar(d, f["trig"])
    if et is None or et > "15:05":
        continue
    leg, st = build_leg(d, f["side"], f["trig"], et, f"chrono_{kind}")
    if leg:
        chrono_legs.append(leg)

# ---- book statistics ---------------------------------------------------------
def day_series(legs):
    s = {d: 0.0 for d in DAYS}
    for l in legs:
        s[l["date"]] += float(l["net_inr"])
    return s

def book_stats(legs):
    tot = round(sum(float(l["net_inr"]) for l in legs), 2)
    months = defaultdict(float)
    for l in legs:
        months[l["date"][:7]] += float(l["net_inr"])
    h1 = round(sum(float(l["net_inr"]) for l in legs if l["date"] < "2026-06-01"), 2)
    h2 = round(tot - h1, 2)
    top3 = sorted((float(l["net_inr"]) for l in legs), reverse=True)[:3]
    ds = day_series(legs)
    legdays = {d: v for d, v in ds.items()
               if any(l["date"] == d for l in legs)}
    top3d = sorted(legdays.values(), reverse=True)[:3]
    cal = [ds[d] for d in DAYS]
    worst_day = min(legdays.items(), key=lambda kv: kv[1]) if legdays else None
    worst3, cur = None, 0.0
    for i in range(len(cal) - 2):
        v = cal[i] + cal[i + 1] + cal[i + 2]
        if worst3 is None or v < worst3[0]:
            worst3 = (round(v, 2), DAYS[i])
    eq, peak, dd = 0.0, 0.0, 0.0
    for v in cal:
        eq += v
        peak = max(peak, eq)
        dd = min(dd, eq - peak)
    return {"legs": len(legs), "total": tot, "per_month": round(tot / 10, 2),
            "per_leg": round(tot / len(legs), 2) if legs else 0.0,
            "months": {k: round(v, 2) for k, v in sorted(months.items())},
            "H1": h1, "H2": h2,
            "ex_top3_legs": round(tot - sum(top3), 2),
            "ex_top3_days": round(tot - sum(top3d), 2),
            "worst_day": (worst_day[0], round(worst_day[1], 2)) if worst_day else None,
            "worst_3day": worst3, "worst_drawdown": round(dd, 2),
            "pos_days": sum(1 for v in legdays.values() if v > 0),
            "leg_days": len(legdays)}

base_legs_norm = [{"date": r["date"], "net_inr": float(r["net_inr"])} for r in base]
books = {}
books["base"] = book_stats(base_legs_norm)
books["A"] = book_stats(A_legs)
books["A_shift60"] = book_stats(A_shift_legs)
books["B_standalone"] = book_stats(B_std_legs)
books["B_combined_set"] = book_stats(B_comb_legs)
books["B_flip"] = book_stats(B_flip_legs)
books["chrono"] = book_stats(chrono_legs)
books["base+A"] = book_stats(base_legs_norm + A_legs)
books["base+B"] = book_stats(base_legs_norm + B_std_legs)
books["combined"] = book_stats(base_legs_norm + A_legs + B_comb_legs)
books["base+chrono"] = book_stats(base_legs_norm + chrono_legs)

# whipsaw accounting
def whipsaw(legs):
    st = [l for l in legs if l["exit_reason"] == "stop"]
    return {"stops": len(st), "stops_rs": round(sum(l["net_inr"] for l in st), 2),
            "targets": sum(1 for l in legs if l["exit_reason"] == "target"),
            "square_offs": sum(1 for l in legs if l["exit_reason"] == "square_off"),
            "path_ends": sum(1 for l in legs if l["exit_reason"] == "path_end")}

whip = {"A": whipsaw(A_legs), "B_standalone": whipsaw(B_std_legs),
        "B_combined_set": whipsaw(B_comb_legs)}

# ---- timing audit ----------------------------------------------------------
viol = []
for l in A_legs + A_shift_legs:
    if l["trigger_time"] < "12:00" or l["trigger_time"] < l["stop_exit_time"]:
        viol.append(("A_window", l["date"]))
    if l["exit_time"] < l["entry_time"]:
        viol.append(("A_exit_before_entry", l["date"]))
for l in B_std_legs + B_flip_legs:
    if l["trigger_time"] < "12:30":
        viol.append(("B_window", l["date"]))
    b, ts = SPOT[l["date"]], TIMES[l["date"]]
    prior = [x for x in ts if x < l["trigger_time"]]
    rh = max(b[x][1] for x in prior)
    rl = min(b[x][2] for x in prior)
    c = b[l["trigger_time"]][3]
    real_side = "CE" if c > rh else ("PE" if c < rl else None)
    if real_side is None:
        viol.append(("B_break_check", l["date"]))
    elif l["set"] == "B_sleeve" and l["direction"] != real_side:
        viol.append(("B_break_side", l["date"]))
    elif l["set"] == "B_flip" and l["direction"] == real_side:
        viol.append(("B_flip_side", l["date"]))
    if l["exit_time"] < l["entry_time"]:
        viol.append(("B_exit_before_entry", l["date"]))
for l in A_legs + B_std_legs + A_shift_legs + B_flip_legs:
    if l["exit_reason"] == "stop" and abs(l["exit_premium"] - (l["entry_premium"] - 50)) > 1e-9:
        viol.append(("stop_fill", l["date"]))
    if l["exit_reason"] == "target" and abs(l["exit_premium"] - (l["entry_premium"] + 90)) > 1e-9:
        viol.append(("target_fill", l["date"]))
    et = next_bar(l["date"], l["trigger_time"])
    if et != l["entry_time"]:
        viol.append(("entry_not_next_bar", l["date"]))

results = {"monthly_calendar": MONTHLY, "base_total_check": BASE_TOTAL,
           "books": books, "whipsaw": whip,
           "A_blocked_cap": A_blocked, "A_nc": A_nc, "A_shift_nc": A_shift_nc,
           "B_nc": B_nc, "B_flip_nc": B_flip_nc, "timing_violations": viol}
json.dump(results, open(f"{TR}/bank_v22_phase2_results.json", "w"), indent=1)

# ---- write trades ------------------------------------------------------------
inc_fields = ["date", "set", "direction", "expiry", "strike", "trigger_time",
              "entry_time", "entry_premium", "exit_time", "exit_premium",
              "exit_reason", "net_inr"]
with open(f"{TR}/bank_v22_phase2_increments.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=inc_fields)
    w.writeheader()
    for l in A_legs + B_std_legs + B_comb_legs + A_shift_legs + B_flip_legs + chrono_legs:
        w.writerow({k: l.get(k, "") for k in inc_fields})

with open(f"{TR}/bank_v22_phase2_trades.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["date", "direction", "family", "rep",
                                      "entry_time", "entry_premium", "exit_time",
                                      "exit_premium", "exit_reason", "net_inr"])
    w.writeheader()
    for r in base:
        w.writerow(r)
    for l in A_legs + B_comb_legs:
        w.writerow({"date": l["date"], "direction": l["direction"],
                    "family": "EVE06_REENTRY" if l["set"] == "A_reentry" else "EVE06_SLEEVE",
                    "rep": l["set"], "entry_time": l["entry_time"],
                    "entry_premium": l["entry_premium"], "exit_time": l["exit_time"],
                    "exit_premium": l["exit_premium"],
                    "exit_reason": l["exit_reason"], "net_inr": l["net_inr"]})

print("monthly calendar:", MONTHLY)
print("timing violations:", viol)
for name, s in books.items():
    print(f"{name:16s} legs {s['legs']:4d}  total {s['total']:12.2f}  /mo {s['per_month']:10.2f}  /leg {s['per_leg']:9.2f}")
print("whipsaw:", json.dumps(whip))
print("A cap-blocked:", A_blocked)
print("A nc:", A_nc, "| B nc:", B_nc)
print("combined months:", books["combined"]["months"])
print("combined bleed: worst_day", books["combined"]["worst_day"],
      "worst3", books["combined"]["worst_3day"], "dd", books["combined"]["worst_drawdown"])
print("base bleed:     worst_day", books["base"]["worst_day"],
      "worst3", books["base"]["worst_3day"], "dd", books["base"]["worst_drawdown"])
