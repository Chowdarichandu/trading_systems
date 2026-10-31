#!/usr/bin/env python3
"""Stocks EQUITY — Workstream A: EVENT-AXIS invention.
Spec: stocks_event_axis_frozen.md (FROZEN 2026-10-31 before scoring).
EQUITY CASH intraday only (EA2 is a flagged 2-day hold — see spec).
LONG/SHORT. Paper only. Per 100 shares provisional, Rs40 per round trip.

EA1: event-window restriction (WIDE = calendar +-7td tag as frozen in the
     source CSVs; NARROW = reaction +-2td, same eff rule) of three frozen
     pools: ladder+volume V3, full P2 @T125, INV1 @T125.
EA2: pre-results drift: direction = sign of previous results event's
     reaction-day close-vs-open; enter open of R-2, exit close of R-1.
EA3: N4-V3 trades split by reaction-day volume pace by 09:30 >= 1.0x.
"""
import csv, json, sys
from collections import defaultdict
from datetime import date, timedelta

OUT = "/home/hatch/workspace/trading"
sys.path.insert(0, OUT)
import stocks_hunt1 as H   # loads stocks, DAYS, WINDOWS (OHLC cache)

SYMBOLS = H.SYMBOLS
QTY, COST = 100, 40.0
H1_HI, H2_LO, OCT_LO = "2026-05-31", "2026-06-01", "2026-10-01"
WIN_LO, WIN_HI = "2026-01-01", "2026-10-28"

# ---------------------------------------------------------------- windows
def build_window_sets(sym):
    """Mirror stocks_hunt1.build_windows exactly for WIDE; NARROW uses the
    same eff-reaction rule with +-2 trading days around eff."""
    _, daily = H.stocks[sym]
    tdays = [d["date"] for d in daily]; idx = {d: i for i, d in enumerate(tdays)}
    wide, narrow = set(), set()
    with open(f"{OUT}/stock_event_calendar_jan_oct_2026.csv") as f:
        for r in csv.DictReader(f):
            if r["stock"] != sym: continue
            ev = date.fromisoformat(r["event_date"][:10]) if r["event_date"] else None
            react = date.fromisoformat(r["reaction_date"][:10]) if r["reaction_date"] else None
            if ev is None: continue
            eff = react if (react and ev <= react <= ev + timedelta(days=7)) else ev
            if ev.isoformat() not in idx or eff.isoformat() not in idx: continue
            a = max(0, idx[ev.isoformat()] - 7); b = min(len(tdays) - 1, idx[eff.isoformat()] + 7)
            wide.update(tdays[a:b + 1])
            a2 = max(0, idx[eff.isoformat()] - 2); b2 = min(len(tdays) - 1, idx[eff.isoformat()] + 2)
            narrow.update(tdays[a2:b2 + 1])
    return wide, narrow

WIN = {s: build_window_sets(s) for s in SYMBOLS}

# ---------------------------------------------------------------- metrics
def metrics(ts):
    """ts: list of dicts with stock, date, net."""
    def agg(rows):
        n = len(rows); net = sum(t["net"] for t in rows)
        return {"n": n, "win_pct": round(100.0 * sum(1 for t in rows if t["net"] > 0) / n, 1) if n else None,
                "net": round(net, 2),
                "gross_exp": round(net / n + COST, 2) if n else None}
    by_stock = defaultdict(float)
    for t in ts: by_stock[t["stock"]] += t["net"]
    total = sum(t["net"] for t in ts)
    pos = sorted((v for v in by_stock.values() if v > 0), reverse=True)
    return {
        "all": agg(ts),
        "jan_may": agg([t for t in ts if t["date"] <= H1_HI]),
        "jun_oct": agg([t for t in ts if t["date"] >= H2_LO]),
        "oct": agg([t for t in ts if t["date"] >= OCT_LO]),
        "breadth_pos_stocks": sum(1 for v in by_stock.values() if v > 0),
        "top3_share_pct": round(100.0 * sum(pos[:3]) / total, 1) if total > 0 and pos else None,
        "per_stock_net": {k: round(v, 2) for k, v in sorted(by_stock.items(), key=lambda kv: -kv[1])},
    }

def gate(m):
    return (m["jan_may"]["net"] > 0 and m["jun_oct"]["net"] > 0
            and m["breadth_pos_stocks"] >= 10
            and (m["all"]["net"] <= 0 or (m["top3_share_pct"] is not None and m["top3_share_pct"] <= 75.0)))

# ---------------------------------------------------------------- EA1
def load_pool(path, stock_col, net_col, tag_col):
    # tag vocabulary differs by engine vintage: ladder files use "event",
    # round8/9/10 files use "event_window" — both mean WIDE-window membership.
    ts = []
    with open(f"{OUT}/{path}") as f:
        for r in csv.DictReader(f):
            ts.append({"stock": r[stock_col], "date": r["date"],
                       "net": float(r[net_col]),
                       "tag": "event" if r[tag_col] in ("event", "event_window") else "no_event"})
    return ts

POOLS = {
    "P-V3-ladder": ("newstratvol_V3_trades.csv", "symbol", "net", "event",
                    3275, -16284.00),
    "P-P2-full": ("eq_round8_P2_T125_S050.csv", "stock", "net_rs_provisional_per100", "event_status",
                  918, 10657.81),
    "P-INV1": ("eq_round10_INV1_trades_T125.csv", "stock", "net_rs_provisional_per100", "event_status",
               694, 22964.30),
}

ea1 = {"validation": {}, "families": {}, "complements": {}}
family_trades = {}
for pname, (path, sc, nc, tc, exp_n, exp_net) in POOLS.items():
    ts = load_pool(path, sc, nc, tc)
    tot = round(sum(t["net"] for t in ts), 2)
    # validation 1: published totals
    v = {"file": path, "n": len(ts), "expected_n": exp_n, "total_net": tot,
         "expected_total_net": exp_net,
         "totals_match": (len(ts) == exp_n and abs(tot - exp_net) < 0.05)}
    # validation 2: re-derived WIDE == frozen CSV tag
    mism = sum(1 for t in ts if (t["date"] in WIN[t["stock"]][0]) != (t["tag"] == "event"))
    v["wide_tag_mismatches"] = mism
    ea1["validation"][pname] = v
    for wname, wset_i in (("WIDE", 0), ("NARROW", 1)):
        sub = [t for t in ts if t["date"] in WIN[t["stock"]][wset_i]]
        fam = f"{pname}|{wname}"
        m = metrics(sub)
        m["gate_pass"] = gate(m)
        m["narrow_not_in_wide"] = sum(1 for t in sub if t["tag"] != "event") if wname == "NARROW" else 0
        ea1["families"][fam] = m
        family_trades[fam] = sub
    comp = [t for t in ts if t["tag"] != "event"]
    ea1["complements"][pname] = metrics(comp)

# ---------------------------------------------------------------- EA2
def eff_reaction(r):
    ev = date.fromisoformat(r["event_date"][:10]) if r["event_date"] else None
    react = date.fromisoformat(r["reaction_date"][:10]) if r["reaction_date"] else None
    if ev is None: return None
    return react if (react and ev <= react <= ev + timedelta(days=7)) else ev

cal = defaultdict(list)
with open(f"{OUT}/stock_event_calendar_jan_oct_2026.csv") as f:
    for r in csv.DictReader(f):
        if r["event_type"] == "results" and r["stock"] in SYMBOLS and r["event_date"]:
            cal[r["stock"]].append(r)
for s in cal: cal[s].sort(key=lambda r: r["event_date"])

ea2_trades, ea2_skips = [], defaultdict(int)
for sym in SYMBOLS:
    _, daily = H.stocks[sym]
    dmap = {d["date"]: i for i, d in enumerate(daily)}
    rows = cal.get(sym, [])
    for k, r in enumerate(rows):
        eff = eff_reaction(r)
        if eff is None: continue
        ds = eff.isoformat()
        if not (WIN_LO <= ds <= WIN_HI):
            continue  # predecessor-only row (e.g. 2025 event); not scored as current
        if k == 0:
            ea2_skips["no_previous_in_file"] += 1; continue
        prev_eff = eff_reaction(rows[k - 1])
        if prev_eff is None or prev_eff.isoformat() not in dmap:
            ea2_skips["prev_reaction_day_missing"] += 1; continue
        prow = daily[dmap[prev_eff.isoformat()]]
        sign = 0
        if prow["close"] > prow["open"]: sign = 1
        elif prow["close"] < prow["open"]: sign = -1
        if sign == 0:
            ea2_skips["prev_reaction_zero_sign"] += 1; continue
        if ds not in dmap or dmap[ds] < 2:
            ea2_skips["anchor_days_missing"] += 1; continue
        ri = dmap[ds]
        e_row, x_row = daily[ri - 2], daily[ri - 1]
        gross = sign * (x_row["close"] - e_row["open"]) * QTY
        ea2_trades.append({"stock": sym, "date": e_row["date"], "exit_date": x_row["date"],
                           "reaction_date": ds, "event_date": r["event_date"],
                           "direction": "LONG" if sign > 0 else "SHORT",
                           "entry_open": e_row["open"], "exit_close": x_row["close"],
                           "prev_event_date": rows[k - 1]["event_date"],
                           "prev_reaction_date": prev_eff.isoformat(),
                           "net": round(gross - COST, 2)})
ea2 = {"metrics": metrics(ea2_trades), "skips": dict(ea2_skips),
       "n_events_in_window": sum(1 for s in SYMBOLS for r in cal.get(s, [])
                                 if eff_reaction(r) and WIN_LO <= eff_reaction(r).isoformat() <= WIN_HI)}
ea2["metrics"]["gate_pass"] = gate(ea2["metrics"])
family_trades["EA2-drift"] = ea2_trades

# ---------------------------------------------------------------- EA3
def load_vol(sym):
    days = {}
    path = f"{OUT}/data/progressive_vol/{sym}/spot_5m_vol.csv"
    with open(path) as f:
        for r in csv.DictReader(f):
            d = r["timestamp"][:10]; t = r["timestamp"][11:16]
            days.setdefault(d, {})[t] = float(r["volume"])
    return days

PACE_BARS = ("09:15", "09:20", "09:25")
def pace(sym, day, vdays):
    dates = sorted(vdays.keys())
    if day not in vdays: return None, "day_missing_in_vol"
    today = vdays[day]
    if any(b not in today for b in PACE_BARS): return None, "pace_bars_missing"
    num = sum(today[b] for b in PACE_BARS)
    i = dates.index(day)
    priors = []
    for d in dates[max(0, i - 20):i]:
        pd = vdays[d]
        if all(b in pd for b in PACE_BARS): priors.append(sum(pd[b] for b in PACE_BARS))
    if len(priors) < 10: return None, f"only_{len(priors)}_prior_days"
    den = sum(priors) / len(priors)
    if den <= 0: return None, "zero_denominator"
    return num / den, f"ok_{len(priors)}_priors"

ea3 = {}
for combo, path in (("T125", "eq_n4deep_v3_trades_T125_janoct.csv"),
                    ("T10", "eq_n4deep_v3_trades_T10_janoct.csv")):
    trades = []
    with open(f"{OUT}/{path}") as f:
        for r in csv.DictReader(f):
            trades.append({"stock": r["stock"], "date": r["date"],
                           "net": float(r["net_rs_provisional_per100"]),
                           "direction": r["direction"]})
    volcache = {}
    for t in trades:
        if t["stock"] not in volcache: volcache[t["stock"]] = load_vol(t["stock"])
        p, why = pace(t["stock"], t["date"], volcache[t["stock"]])
        t["pace"] = round(p, 3) if p is not None else None
        t["pace_status"] = why
    kept = [t for t in trades if t["pace"] is not None and t["pace"] >= 1.0]
    dropped = [t for t in trades if t not in kept]
    unclass = [t for t in trades if t["pace"] is None]
    full_m, kept_m = metrics(trades), metrics(kept)
    ea3[combo] = {"full": full_m, "kept": metrics(kept), "dropped": metrics(dropped),
                  "unclassifiable_n": len(unclass),
                  "unclassifiable": [{"stock": t["stock"], "date": t["date"], "why": t["pace_status"]}
                                     for t in unclass],
                  "trades": trades}
    if combo == "T125":
        ea3[combo]["pass_bar"] = {
            "kept_both_halves_net_positive": kept_m["jan_may"]["net"] > 0 and kept_m["jun_oct"]["net"] > 0,
            "kept_exp_ge_full_each_half": (
                kept_m["jan_may"]["gross_exp"] is not None and full_m["jan_may"]["gross_exp"] is not None
                and kept_m["jan_may"]["gross_exp"] >= full_m["jan_may"]["gross_exp"]
                and kept_m["jun_oct"]["gross_exp"] is not None and full_m["jun_oct"]["gross_exp"] is not None
                and kept_m["jun_oct"]["gross_exp"] >= full_m["jun_oct"]["gross_exp"]),
            "kept_sample_floor": kept_m["all"]["n"] >= 20 and kept_m["jan_may"]["n"] >= 5 and kept_m["jun_oct"]["n"] >= 5}
        ea3[combo]["pass_bar"]["PASS"] = all(ea3[combo]["pass_bar"].values())

results = {"EA1": ea1, "EA2": ea2,
           "EA3": {c: {k: v for k, v in ea3[c].items() if k != "trades"} for c in ea3}}
with open(f"{OUT}/stocks_event_axis_results.json", "w") as f:
    json.dump(results, f, indent=1)

# per-family trade CSVs (audit)
def dump(name, rows, cols):
    with open(f"{OUT}/{name}", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for t in rows: w.writerow({c: t.get(c, "") for c in cols})

for fam, rows in family_trades.items():
    if fam == "EA2-drift": continue
    dump(f"eq_eventaxis_{fam.replace('|', '_')}_trades.csv",
         [{"stock": t["stock"], "date": t["date"], "net": t["net"]} for t in rows],
         ["stock", "date", "net"])
dump("eq_eventaxis_EA2_drift_trades.csv", ea2_trades,
     ["stock", "date", "exit_date", "reaction_date", "event_date", "direction",
      "entry_open", "exit_close", "prev_event_date", "prev_reaction_date", "net"])
for combo in ("T125", "T10"):
    dump(f"eq_eventaxis_EA3_{combo}_trades.csv", ea3[combo]["trades"],
         ["stock", "date", "direction", "net", "pace", "pace_status"])

print(json.dumps({"EA1_validation": ea1["validation"],
                  "EA1_families": {k: {"n": v["all"]["n"], "JM": v["jan_may"]["net"],
                                       "JO": v["jun_oct"]["net"], "pass": v["gate_pass"]}
                                   for k, v in ea1["families"].items()},
                  "EA2": {"n": ea2["metrics"]["all"]["n"], "JM": ea2["metrics"]["jan_may"]["net"],
                          "JO": ea2["metrics"]["jun_oct"]["net"], "pass": ea2["metrics"]["gate_pass"],
                          "skips": ea2["skips"]},
                  "EA3_T125": {"full_n": ea3["T125"]["full"]["all"]["n"],
                               "kept_n": ea3["T125"]["kept"]["all"]["n"],
                               "kept_JM": ea3["T125"]["kept"]["jan_may"]["net"],
                               "kept_JO": ea3["T125"]["kept"]["jun_oct"]["net"],
                               "unclass": ea3["T125"]["unclassifiable_n"],
                               "pass_bar": ea3["T125"].get("pass_bar")}}, indent=1))
