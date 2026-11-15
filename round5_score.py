#!/usr/bin/env python3
"""ROUND 5 SCORER (2026-11-14) — FLOW-VOL and OPT-FLOW, frozen in
new_data_round5_2026-11-14.md BEFORE this run. (IOI-1/IOI-2 are
gated by a dedicated track per the 05:37 coordination steer and are
NOT scored here.)

Construction (both books): entry at the OPEN of the 11:00 bar of the
ATM contract (nearest 100 to the 10:55 spot close) on the signal
side; stop -50 / target +90 (stop first inside a bar, entry bar
included); square-off at the close of the 15:10 bar; 1 lot = 30;
Rs 220/trade; buying only; at most one leg/day.
Gate per the freeze: total>0 and >= Rs 900/trade-day; >=40 trades and
>=20 trade-days; NC <= 5% of 205; both halves (Jan-May / Jun-Oct) > 0;
every month >= -5,000; ex-top-3 > 0; beats COIN (95th pct, 200 draws,
seed 20261113), REVERSED and TIME-SHIFTED (12:00) placebos; timing
asserted per trade; independent re-sum from the trades CSVs.
Merge: increment on TUNED STACK v2 idle days (ledger =
solid60_programme_2026-11-13_bank_A_stack_features.csv, anchored at
111 legs / Rs 127,351.50 / 89 trade-days). November counterfactual
from the same frozen rules. Offline research only.
"""
import csv, json, random
from collections import defaultdict
from pathlib import Path

TR = Path.home() / "workspace/trading"
R5H = TR / "round5_history"
COST, LOT = 220.0, 30
STOP, TARGET, SQ = 50.0, 90.0, "15:10"
SEED = 20261113
ALL_EXP = ["2026-01-27", "2026-02-24", "2026-03-30", "2026-04-28",
           "2026-05-26", "2026-06-30", "2026-07-28", "2026-08-25",
           "2026-09-29", "2026-10-27", "2026-11-23"]
MORN_TIMES = [f"{9 + (15 + 5 * i) // 60:02d}:{(15 + 5 * i) % 60:02d}"
              for i in range(21)]  # 09:15 .. 10:55


def in_force(day):
    for e in ALL_EXP:
        if e >= day:
            return e
    return None


# ---------------- datasets ----------------
MF = {}
with open(R5H / "morning_flow.csv") as f:
    for r in csv.DictReader(f):
        MF[r["date"]] = r
JAN_OCT = sorted(d for d in MF if d <= "2026-10-31")
NOV = [d for d in ("2026-11-02", "2026-11-03", "2026-11-04",
                   "2026-11-05", "2026-11-06", "2026-11-09",
                   "2026-11-11", "2026-11-12", "2026-11-13") if d in MF]
assert len(JAN_OCT) == 205, len(JAN_OCT)
ALL_DAYS = JAN_OCT + NOV
PRIOR = {}
for i, d in enumerate(ALL_DAYS):
    PRIOR[d] = ALL_DAYS[i - 1] if i > 0 else "2025-12-31"

SPOT = {}
_raw = json.load(open(TR / "daily2leg/spot.json"))
for d, bars in _raw["BANKNIFTY"].items():
    SPOT[d] = {b[0]: float(b[4]) for b in bars}
for fn in (TR / "oi_history/spot_nov_bars.json",
           TR / "round4_history/spot_extra.json"):
    if fn.exists():
        data = json.loads(fn.read_text())
        if isinstance(data, dict) and "BANKNIFTY" in data:
            data = data["BANKNIFTY"]
        if isinstance(data, dict):
            for d, bars in data.items():
                if d not in SPOT and isinstance(bars, list) and bars:
                    SPOT[d] = {b[0]: float(b[4]) for b in bars}
_prog = TR / "data/progressive/BANKNIFTY/spot_5m.csv"
if _prog.exists():
    with open(_prog) as f:
        for r in csv.DictReader(f):
            SPOT.setdefault(r["timestamp"][:10], {})[
                r["timestamp"][11:16]] = float(r["close"])

FUT = {}
for exp in ALL_EXP:
    fn = R5H / f"FUT7_{exp}.json"
    if not fn.exists():
        continue
    byd = {}
    for r in json.loads(fn.read_text()):
        byd.setdefault(r[0], {})[r[1]] = r
    FUT[exp] = byd


def fut_morning(day):
    """(V_morn, basis0915, basis1055) or None if incomplete."""
    exp = in_force(day)
    bars = FUT.get(exp, {}).get(day, {})
    if any(t not in bars for t in MORN_TIMES):
        return None
    if any(bars[t][6] is None for t in MORN_TIMES):
        return None
    sday = SPOT.get(day, {})
    if "09:15" not in sday or "10:55" not in sday:
        return None
    v = sum(bars[t][6] for t in MORN_TIMES)
    b0915 = bars["09:15"][5] - sday["09:15"]
    b1055 = bars["10:55"][5] - sday["10:55"]
    return v, b0915, b1055


def flowvol_signal(day):
    """('CE'/'PE'/None, nc_bool)."""
    cur = fut_morning(day)
    if cur is None:
        return None, True
    pday = PRIOR[day]
    pexp = in_force(pday)
    pbars = FUT.get(pexp, {}).get(pday, {})
    if any(t not in pbars for t in MORN_TIMES) or \
            any(pbars[t][6] is None for t in MORN_TIMES):
        return None, True
    pv = sum(pbars[t][6] for t in MORN_TIMES)
    if pv <= 0:
        return None, True
    v, b0915, b1055 = cur
    if v / pv < 1.25:
        return None, False
    db = b1055 - b0915
    if db > 0:
        return "CE", False
    if db < 0:
        return "PE", False
    return None, False


def quadrant(doi, dp):
    if doi == 0 or dp == 0:
        return "FLAT"
    if doi > 0 and dp > 0:
        return "LONG_BUILDUP"
    if doi > 0 and dp < 0:
        return "SHORT_BUILDUP"
    if doi < 0 and dp > 0:
        return "SHORT_COVERING"
    return "LONG_UNWINDING"


def optflow_signal(day):
    """('CE'/'PE'/None, nc_bool) from a morning_flow row."""
    row = MF[day]
    if row["complete"] != "True":
        return None, True
    share = float(row["vol_share_CE"])
    if share >= 0.60 and float(row["dp_CE"]) > 0:
        return "CE", False
    if share <= 0.40 and float(row["dp_PE"]) > 0:
        return "PE", False
    return None, False


# ---------------- premium replay ----------------
_cache = {}


def prem_bars(exp, strike, typ, day):
    ck = (exp, strike, typ)
    if ck not in _cache:
        fn = R5H / f"C5_{exp}_{strike}{typ}.json"
        byd = {}
        if fn.exists():
            for r in json.loads(fn.read_text()):
                byd.setdefault(r[0], {})[r[1]] = (float(r[2]), float(r[3]),
                                                  float(r[4]), float(r[5]))
        _cache[ck] = byd
    return _cache[ck].get(day, {})


def replay(bars, entry_time):
    if entry_time not in bars or SQ not in bars:
        return None
    win = [t for t in sorted(bars) if entry_time <= t <= SQ]
    need = 60 if entry_time == "11:00" else 45
    if len(win) < need:
        return None
    entry = bars[entry_time][0]
    for t in win:
        o, h, l, c = bars[t]
        if l <= entry - STOP:
            return t, round(entry - STOP, 2), "stop"
        if h >= entry + TARGET:
            return t, round(entry + TARGET, 2), "target"
    return SQ, bars[SQ][3], "squareoff"


SIGNAL_FN = {"FLOWVOL": flowvol_signal, "OPTFLOW": optflow_signal}


def run_legs(book, days):
    trades, nc = [], []
    for d in days:
        side, is_nc = SIGNAL_FN[book](d)
        if is_nc:
            nc.append(d)
            continue
        if side is None:
            continue
        row = MF[d]
        exp, strike = row["expiry"], int(row["atm"])
        bars = prem_bars(exp, strike, side, d)
        r = replay(bars, "11:00")
        if r is None:
            nc.append(d)
            continue
        et, ep, reason = r
        entry = bars["11:00"][0]
        assert et >= "11:00"
        trades.append({
            "date": d, "side": side, "strike": strike, "expiry": exp,
            "entry_time": "11:00", "entry_premium": entry,
            "exit_time": et, "exit_premium": ep, "exit_reason": reason,
            "net_inr": round((ep - entry) * LOT - COST, 2)})
    return trades, nc


def placebo_cells(book, days):
    cells = {}
    for d in days:
        side, is_nc = SIGNAL_FN[book](d)
        if is_nc or side is None:
            continue
        row = MF[d]
        exp, strike = row["expiry"], int(row["atm"])
        cell = {"signal_side": side}
        ok = True
        for s in ("CE", "PE"):
            bars = prem_bars(exp, strike, s, d)
            for et_name, et in (("1100", "11:00"), ("1200", "12:00")):
                r = replay(bars, et)
                if r is None:
                    cell[(s, et_name)] = None
                    if s == side and et_name == "1100":
                        ok = False
                else:
                    cell[(s, et_name)] = round(
                        (r[1] - bars[et][0]) * LOT - COST, 2)
        if ok:
            cells[d] = cell
    return cells


def month_table(trades):
    mt = defaultdict(float)
    for t in trades:
        mt[t["date"][:7]] += t["net_inr"]
    return {f"2026-{i:02d}": round(mt.get(f"2026-{i:02d}", 0.0), 2)
            for i in range(1, 11)}


def stats_block(trades, all_days):
    total = round(sum(t["net_inr"] for t in trades), 2)
    tdays = sorted({t["date"] for t in trades})
    day_net = defaultdict(float)
    for t in trades:
        day_net[t["date"]] += t["net_inr"]
    green = sum(1 for v in day_net.values() if v > 0)
    red = sum(1 for v in day_net.values() if v < 0)
    h1 = round(sum(t["net_inr"] for t in trades
                   if t["date"] <= "2026-05-31"), 2)
    top3 = sorted((t["net_inr"] for t in trades), reverse=True)[:3]
    wins = sum(1 for t in trades if t["net_inr"] > 0)
    return {
        "legs": len(trades), "total": total, "trade_days": len(tdays),
        "per_trade_day": round(total / len(tdays), 2) if tdays else 0.0,
        "win_rate_pct": round(100.0 * wins / len(trades), 1)
        if trades else 0.0,
        "months": month_table(trades),
        "halves": {"H1_Jan_May": h1, "H2_Jun_Oct": round(total - h1, 2)},
        "ex_top3": round(total - sum(top3), 2),
        "day_counts_trade_days": {"green": green, "red": red},
        "day_counts_all_days": {"green": green, "red": red,
                                "no_trade": len(all_days) - len(tdays)},
    }


def gate_block(trades, nc_days, cells, real_total):
    sig_days = sorted(cells)
    rng = random.Random(SEED)
    coin_totals = []
    for _ in range(200):
        tot = 0.0
        for d in sig_days:
            v = cells[d][(rng.choice(("CE", "PE")), "1100")]
            if v is not None:
                tot += v
        coin_totals.append(round(tot, 2))
    coin_totals.sort()
    pct = round(100.0 * sum(1 for x in coin_totals if x < real_total)
                / len(coin_totals), 1) if coin_totals else 0.0
    p95 = coin_totals[int(0.95 * len(coin_totals)) - 1] if coin_totals \
        else None
    rev = round(sum(cells[d][("PE" if cells[d]["signal_side"] == "CE"
                              else "CE", "1100")] or 0.0
                    for d in sig_days), 2)
    shifted = round(sum(cells[d][(cells[d]["signal_side"], "1200")]
                        or 0.0 for d in sig_days), 2)
    st = stats_block(trades, JAN_OCT)
    legs = {
        "total_pos_and_900_td": st["total"] > 0
        and st["per_trade_day"] >= 900,
        "min_sample": st["legs"] >= 40 and st["trade_days"] >= 20,
        "nc_le_5pct": len(nc_days) <= 0.05 * 205,
        "halves_both_pos": st["halves"]["H1_Jan_May"] > 0
        and st["halves"]["H2_Jun_Oct"] > 0,
        "months_floor": all(v >= -5000 for v in st["months"].values()),
        "ex_top3_pos": st["ex_top3"] > 0,
        "coin_ge95": pct >= 95.0,
        "beats_reversed": real_total > rev,
        "beats_time_shifted": real_total > shifted,
    }
    return {"legs_detail": legs, "gate_pass": all(legs.values()),
            "placebos": {"coin_pct": pct, "coin_p95": p95,
                         "reversed_total": rev,
                         "time_shifted_total": shifted}}


# ---------------- stack ledger (merge base) ----------------
stack_rows = list(csv.DictReader(
    open(TR / "solid60_programme_2026-11-13_bank_A_stack_features.csv")))
STACK = [{"date": r["date"], "net": float(r["x1_net"])} for r in stack_rows]
STACK_DAYS = {l["date"] for l in STACK}
STACK_TOTAL = round(sum(l["net"] for l in STACK), 2)
assert len(STACK) == 111 and STACK_TOTAL == 127351.50 \
    and len(STACK_DAYS) == 89, (len(STACK), STACK_TOTAL, len(STACK_DAYS))
STACK_DAY_NET = defaultdict(float)
for l in STACK:
    STACK_DAY_NET[l["date"]] += l["net"]
STACK_MONTH = {f"2026-{i:02d}": round(sum(
    l["net"] for l in STACK if l["date"][:7] == f"2026-{i:02d}"), 2)
    for i in range(1, 11)}

nov_stack = {}
with open(TR / "november_shadow_stack_bank_log.csv") as f:
    for r in csv.DictReader(f):
        if r["net_inr"]:
            nov_stack[r["date"]] = float(r["net_inr"])
NOV_STACK_TOTAL = round(sum(nov_stack.values()), 2)
assert NOV_STACK_TOTAL == -2680.0, NOV_STACK_TOTAL

BOOKS = ("FLOWVOL", "OPTFLOW")
FN = {"FLOWVOL": "round5_trades_flow_vol.csv",
      "OPTFLOW": "round5_trades_opt_flow.csv"}
results = {"stack_anchor": {"legs": 111, "total": STACK_TOTAL,
                            "trade_days": 89}, "books": {}}

for book in BOOKS:
    trades, nc_days = run_legs(book, JAN_OCT)
    cells = placebo_cells(book, JAN_OCT)
    st = stats_block(trades, JAN_OCT)
    gb = gate_block(trades, nc_days, cells, st["total"])
    incr = [t for t in trades if t["date"] not in STACK_DAYS]
    incr_total = round(sum(t["net_inr"] for t in incr), 2)
    merged_days = STACK_DAYS | {t["date"] for t in incr}
    merged_total = round(STACK_TOTAL + incr_total, 2)
    m_day_net = dict(STACK_DAY_NET)
    for t in incr:
        m_day_net[t["date"]] = m_day_net.get(t["date"], 0.0) + t["net_inr"]
    mgreen = sum(1 for v in m_day_net.values() if v > 0)
    mred = sum(1 for v in m_day_net.values() if v < 0)
    incr_months = month_table(incr)
    merged_months = {m: round(STACK_MONTH[m] + incr_months[m], 2)
                     for m in STACK_MONTH}
    merge = {
        "increment_legs": len(incr), "increment_total": incr_total,
        "increment_days": len({t['date'] for t in incr}),
        "merged_total": merged_total,
        "merged_trade_days": len(merged_days),
        "merged_per_trade_day": round(merged_total / len(merged_days), 2),
        "merged_months": merged_months,
        "merged_red_months": [m for m, v in merged_months.items()
                              if v < 0],
        "merged_day_counts_trade_days": {"green": mgreen, "red": mred},
        "merged_day_counts_all_days": {
            "green": mgreen, "red": mred,
            "no_trade": 205 - len(merged_days)},
    }
    ntrades, nnc = run_legs(book, NOV)
    n_incr = [t for t in ntrades if t["date"] not in nov_stack]
    n_incr_total = round(sum(t["net_inr"] for t in n_incr), 2)
    nov_days = {}
    for d in NOV:
        base = nov_stack.get(d)
        inc = round(sum(t["net_inr"] for t in n_incr
                        if t["date"] == d), 2)
        fam = round(sum(t["net_inr"] for t in ntrades
                        if t["date"] == d), 2)
        nov_days[d] = {
            "stack": base, "family_all_legs": fam,
            "family_increment_on_idle": inc,
            "merged_day": (round(base + inc, 2) if base is not None
                           else (inc if inc else None))}
    mg = sum(1 for v in nov_days.values()
             if v["merged_day"] is not None and v["merged_day"] > 0)
    mr = sum(1 for v in nov_days.values()
             if v["merged_day"] is not None and v["merged_day"] < 0)
    november = {
        "family_trades": ntrades, "family_nc_days": nnc,
        "family_total_all_legs": round(
            sum(t["net_inr"] for t in ntrades), 2),
        "increment_total_on_stack_idle": n_incr_total,
        "merged_november_total": round(NOV_STACK_TOTAL + n_incr_total, 2),
        "stack_baseline": {"total": NOV_STACK_TOTAL,
                           "green": 1, "red": 3, "no_trade": 5},
        "merged_day_counts": {"green": mg, "red": mr,
                              "no_trade": 9 - mg - mr},
        "days": nov_days,
    }
    with open(TR / FN[book], "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "date", "side", "strike", "expiry", "entry_time",
            "entry_premium", "exit_time", "exit_premium", "exit_reason",
            "net_inr"])
        w.writeheader()
        w.writerows(trades)
    results["books"][book] = {"stats": st, "nc_days": nc_days,
                              "gate": gb, "merge": merge,
                              "november": november}
    print(f"{book}: legs={st['legs']} total={st['total']} "
          f"TD={st['trade_days']} perTD={st['per_trade_day']} "
          f"gate={'PASS' if gb['gate_pass'] else 'FAIL'} "
          f"incr={incr_total} merged={merged_total} "
          f"nov_incr={n_incr_total}", flush=True)

for book in BOOKS:
    with open(TR / FN[book]) as f:
        rows = list(csv.DictReader(f))
    s = round(sum(float(r["net_inr"]) for r in rows), 2)
    assert s == results["books"][book]["stats"]["total"], (book, s)
    results["books"][book]["resum_ok"] = True
    print(f"{book}: re-sum OK ({s})", flush=True)

(TR / "new_data_round5_results.json").write_text(
    json.dumps(results, indent=1))
print("results written", flush=True)
