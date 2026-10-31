#!/usr/bin/env python3
"""Round 7 — morning re-entry filters (M1-M5) on the frozen V5 re-entry pool.
Spec: stocks_equity_round7_frozen.md (frozen before scoring).
Gross per trade = net + 40 (frozen flat cost per trade per 100 shares).
"""
import csv, json, collections, os

BASE = "/home/hatch/workspace/trading"
COST = 40.0

def load(exit_):
    rows = list(csv.DictReader(open(f"{BASE}/eq_reentry_v5_trades_{exit_}_janoct.csv")))
    for r in rows:
        r["round"] = int(r["round"])
        r["net"] = float(r["net_rs_provisional_per100"])
        r["gross"] = r["net"] + COST
        r["half"] = "jan_may" if r["date"] < "2026-06-01" else "jun_oct"
        r["oct"] = r["date"] >= "2026-10-01"
        r["month"] = r["date"][:7]
    rows.sort(key=lambda r: (r["date"], r["stock"], r["round"]))
    return rows

def stats(rows):
    n = len(rows)
    if n == 0:
        return {"trades": 0, "gross_total": 0.0, "net_total": 0.0, "gross_exp": None,
                "net_exp": None, "win_pct": None}
    g = sum(r["gross"] for r in rows); nt = sum(r["net"] for r in rows)
    wins = sum(1 for r in rows if r["net"] > 0)
    return {"trades": n, "gross_total": round(g, 2), "net_total": round(nt, 2),
            "gross_exp": round(g / n, 2), "net_exp": round(nt / n, 2),
            "win_pct": round(100.0 * wins / n, 1)}

def both(rows):
    return {"all": stats(rows),
            "jan_may": stats([r for r in rows if r["half"] == "jan_may"]),
            "jun_oct": stats([r for r in rows if r["half"] == "jun_oct"]),
            "october": stats([r for r in rows if r["oct"]])}

def adr_map():
    """Round-3/6 formula: prior-10-day mean daily range % (min 5 prior rows), day excluded."""
    out = {}
    for sym in sorted(os.listdir(f"{BASE}/data/progressive")):
        p = f"{BASE}/data/progressive/{sym}/spot_daily.csv"
        if not os.path.exists(p):
            continue
        daily = []
        with open(p) as f:
            for r in csv.DictReader(f):
                try:
                    daily.append({"date": r["date"][:10], "high": float(r["high"]),
                                  "low": float(r["low"]), "close": float(r["close"])})
                except Exception:
                    pass
        daily.sort(key=lambda x: x["date"])
        idx = {d["date"]: i for i, d in enumerate(daily)}
        for d in daily:
            i = idx[d["date"]]
            if i < 5:
                out[(sym, d["date"])] = None
                continue
            prior = daily[max(0, i - 10):i]
            if len(prior) < 5:
                out[(sym, d["date"])] = None
                continue
            vals = [(x["high"] - x["low"]) / x["close"] * 100 for x in prior if x["close"]]
            out[(sym, d["date"])] = round(sum(vals) / len(vals), 3) if vals else None
    return out

def before1030(r):
    return r["entry_time"] < "10:30"

def variants_for(rows, ADR):
    adr3 = lambda r: (ADR.get((r["stock"], r["date"])) or 0) >= 3.0
    v = {}
    v["M1_reentries_before1030"] = [r for r in rows if r["round"] == 1 or before1030(r)]
    v["M2_morning_cap2"] = [r for r in rows if r["round"] <= 2 and before1030(r)]
    v["M3_round2_only"] = [r for r in rows if r["round"] == 2]
    r5a = [r for r in rows if r["round"] <= 2 and adr3(r)]
    v["M4_M1_on_R5a"] = [r for r in r5a if r["round"] == 1 or before1030(r)]
    v["M5_M2_adr3"] = [r for r in rows if r["round"] <= 2 and before1030(r) and adr3(r)]
    return v

def concentration(rows):
    """Per-month net table + concentration shares for a passing variant."""
    months = collections.defaultdict(list)
    for r in rows:
        months[r["month"]].append(r)
    table = {}
    for m in sorted(months):
        s = stats(months[m])
        table[m] = s
    total_net = sum(r["net"] for r in rows)
    pos_months = {m: s["net_total"] for m, s in table.items() if s["net_total"] > 0}
    largest_month = None
    if total_net > 0 and pos_months:
        lm = max(pos_months, key=pos_months.get)
        largest_month = {"month": lm, "net": pos_months[lm],
                         "share_pct_of_janoct_net": round(100.0 * pos_months[lm] / total_net, 1)}
    largest_trade = None
    if rows and total_net > 0:
        bt = max(rows, key=lambda r: r["net"])
        largest_trade = {"date": bt["date"], "stock": bt["stock"], "round": bt["round"],
                         "net": round(bt["net"], 2),
                         "share_pct_of_janoct_net": round(100.0 * bt["net"] / total_net, 1)}
    return {"per_month": table, "largest_month": largest_month, "largest_trade": largest_trade}

def main():
    ADR = adr_map()
    results, survivors = {}, []
    for ex in ["T10", "T125"]:
        rows = load(ex)
        results[ex] = {}
        for name, vrows in variants_for(rows, ADR).items():
            s = both(vrows)
            be_all = s["all"]["gross_exp"]
            be_jm = s["jan_may"]["gross_exp"]
            be_jo = s["jun_oct"]["gross_exp"]
            passes = (s["jan_may"]["net_total"] > 0 and s["jun_oct"]["net_total"] > 0)
            entry = {"stats": s,
                     "breakeven_cost_all": be_all,
                     "breakeven_cost_jan_may": be_jm,
                     "breakeven_cost_jun_oct": be_jo,
                     "breakeven_cost_both_halves": (min(be_jm, be_jo)
                                                    if be_jm is not None and be_jo is not None else None),
                     "survivor_both_halves_net_pos": passes}
            if passes:
                entry["concentration"] = concentration(vrows)
                entry["october_trades"] = [
                    {"date": r["date"], "stock": r["stock"], "direction": r["direction"],
                     "setup": r["setup"], "round": r["round"], "entry_time": r["entry_time"],
                     "entry": r["entry"], "exit_reason": r["exit_reason"],
                     "exit_time": r["exit_time"],
                     "net_rs_provisional_per100": round(r["net"], 2),
                     "event_status": r["event_status"]}
                    for r in vrows if r["oct"]]
                survivors.append(f"{ex}:{name}")
            results[ex][name] = entry
            # dump kept trades
            with open(f"{BASE}/eq_round7_v5_{ex}_{name}.csv", "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["date", "stock", "direction", "setup", "round", "entry_time", "entry",
                            "exit_reason", "exit_time", "net_rs_provisional_per100", "event_status"])
                for r in sorted(vrows, key=lambda r: (r["date"], r["stock"], r["round"])):
                    w.writerow([r["date"], r["stock"], r["direction"], r["setup"], r["round"],
                                r["entry_time"], r["entry"], r["exit_reason"], r["exit_time"],
                                round(r["net"], 2), r["event_status"]])
            a, jm, jo, oc = s["all"], s["jan_may"], s["jun_oct"], s["october"]
            print(f"{ex} {name}: n={a['trades']} gExp={a['gross_exp']} net={a['net_total']} | "
                  f"JanMay n={jm['trades']} gExp={jm['gross_exp']} net={jm['net_total']} | "
                  f"JunOct n={jo['trades']} gExp={jo['gross_exp']} net={jo['net_total']} | "
                  f"Oct n={oc['trades']} net={oc['net_total']} | "
                  f"BE all={be_all} jm={be_jm} jo={be_jo} | SURVIVOR={passes}")
    json.dump({"results": results, "survivors": survivors},
              open(f"{BASE}/stocks_equity_round7_results.json", "w"), indent=1)
    print("\nSurvivors:", survivors if survivors else "NONE")

if __name__ == "__main__":
    main()
