#!/usr/bin/env python3
"""Round 9 — ex-ante regime gates on the P2 (M5) V5 re-entry pool.
Spec: stocks_equity_round9_frozen.md (frozen before scoring).
Pool machinery is Round 8's, exec'd verbatim (chains rebuilt per exit
cell). Gates use daily bars strictly before the trade day only.
Gross per 100 shares; net = gross - 40.
"""
import csv, json, collections, os, bisect

BASE = "/home/hatch/workspace/trading"
COST = 40.0

# ---- Round 8 machinery (functions + globals; its main() is __main__-guarded)
NS8 = {}
exec(compile(open(f"{BASE}/stocks_equity_round8.py").read(), "round8", "exec"), NS8)
run_chain = NS8["run_chain"]; pools = NS8["pools"]; stats = NS8["stats"]
periods = NS8["periods"]; concentration = NS8["concentration"]
SYMBOLS = NS8["SYMBOLS"]; ALL_DAYS = NS8["ALL_DAYS"]

CELLS = {"T125": ("PLAIN", 1.25, 0.5), "T10": ("PLAIN", 1.0, 0.5)}
GATE_EXPECT = {"T125": (918, 10657.81), "T10": (947, 5772.37)}

# ---------- daily series + ex-ante regime values ----------
def load_daily(sym):
    p = f"{BASE}/data/progressive/{sym}/spot_daily.csv"
    rows = []
    with open(p) as f:
        for r in csv.DictReader(f):
            try:
                rows.append({"date": r["date"][:10], "high": float(r["high"]),
                             "low": float(r["low"]), "close": float(r["close"])})
            except Exception:
                pass
    rows.sort(key=lambda x: x["date"])
    return rows

def regime_maps(sym):
    """For every date D in the series: values from bars strictly before D.
    Returns {D: {prev_close, ma20, ma50, atr_pct, atr_pctile}} (Nifty gets
    atr fields; stocks use prev_close/ma20). atr_pctile = expanding
    percentile (share of prior computable ATR% values <= today's), None
    until 60 prior values exist."""
    daily = load_daily(sym)
    dates = [d["date"] for d in daily]
    closes = [d["close"] for d in daily]
    out = {}
    atr_series = []  # (date, atr_pct) in date order, computable values only
    atr_vals_sorted = []
    for i, d in enumerate(daily):
        if i == 0:
            continue
        prev_close = closes[i - 1]
        def ma(n):
            if i < n:
                return None
            return sum(closes[i - n:i]) / n
        atr = None
        if i >= 10:
            seg = daily[i - 10:i]
            atr = sum((x["high"] - x["low"]) / x["close"] * 100 for x in seg) / 10.0
        pctile = None
        if atr is not None:
            if len(atr_vals_sorted) >= 60:
                k = bisect.bisect_right(atr_vals_sorted, atr)
                pctile = 100.0 * k / len(atr_vals_sorted)
            atr_series.append((d["date"], atr))
            bisect.insort(atr_vals_sorted, atr)
        out[d["date"]] = {"prev_close": prev_close, "ma20": ma(20), "ma50": ma(50),
                          "atr_pct": atr, "atr_pctile": pctile}
    return out

print("building regime maps...")
NIFTY_REG = regime_maps("NIFTY")
STOCK_REG = {sym: regime_maps(sym) for sym in SYMBOLS}

# ---------- gates (row -> True keep / False drop) ----------
def g1(row):
    r = NIFTY_REG.get(row["date"])
    return bool(r and r["ma50"] is not None and r["prev_close"] > r["ma50"])

def g2(row):
    r = NIFTY_REG.get(row["date"])
    return bool(r and r["ma20"] is not None and r["prev_close"] > r["ma20"])

def g3(row):
    r = STOCK_REG[row["stock"]].get(row["date"])
    if not r or r["ma20"] is None:
        return False
    if row["direction"] == "LONG":
        return r["prev_close"] > r["ma20"]
    return r["prev_close"] < r["ma20"]

def g4(row):
    r = NIFTY_REG.get(row["date"])
    return bool(r and r["atr_pctile"] is not None and r["atr_pctile"] <= 75.0)

def g5(row):
    r = NIFTY_REG.get(row["date"])
    if not r or r["ma50"] is None:
        return False
    if row["direction"] == "LONG":
        return r["prev_close"] > r["ma50"]
    return r["prev_close"] < r["ma50"]

GATES = {"G1_nifty50": g1, "G2_nifty20": g2, "G3_stock_align": g3,
         "G4_vol_midband": g4, "G5_dir_regime": g5}

def half_stats(rows):
    return {"all": stats(rows),
            "jan_may": stats([r for r in rows if r["date"] < "2026-06-01"]),
            "jun_oct": stats([r for r in rows if r["date"] >= "2026-06-01"]),
            "october": stats([r for r in rows if r["date"] >= "2026-10-01"])}

def dump(rows, fname):
    with open(f"{BASE}/{fname}", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "stock", "direction", "setup", "round", "entry_time", "entry",
                    "exit_reason", "exit_time", "exit_price",
                    "gross_rs_provisional_per100", "net_rs_provisional_per100", "event_status"])
        for r in sorted(rows, key=lambda r: (r["date"], r["stock"], r["round"])):
            w.writerow([r["date"], r["stock"], r["direction"], r["setup"], r["round"],
                        r["entry_time"], r["entry"], r["exit_reason"], r["exit_time"],
                        r["exit_price"], r["gross"], r["net"], r["event_status"]])

def main():
    results = {"gate_validation": {}, "pools": {}, "gates": {}, "diagnosis": {}}
    pool_rows = {}
    for label, cell in CELLS.items():
        rows = []
        for sym in SYMBOLS:
            for day in ALL_DAYS:
                rows.extend(run_chain(sym, day, cell))
        p2 = pools(rows)["P2_M5"]
        pool_rows[label] = p2
        s = stats(p2)
        en, enet = GATE_EXPECT[label]
        ok = (s["trades"] == en and abs(s["net_total"] - enet) < 0.01)
        results["gate_validation"][label] = {"expected_trades": en, "got_trades": s["trades"],
                                             "expected_net": enet, "got_net": s["net_total"], "pass": ok}
        results["pools"][label] = half_stats(p2)
        print(f"VALIDATION {label}: trades {s['trades']} vs {en}, net {s['net_total']} vs {enet} -> {'PASS' if ok else 'FAIL'}")
    if not all(g["pass"] for g in results["gate_validation"].values()):
        json.dump(results, open(f"{BASE}/stocks_equity_round9_results.json", "w"), indent=1)
        print("VALIDATION FAILED — stopping per frozen spec.")
        return

    # ---- score gates at both exits; rank by primary-exit min-half net
    gate_scores = {}
    for label in CELLS:
        p2 = pool_rows[label]
        gate_scores[label] = {}
        for gname, gfn in GATES.items():
            kept = [r for r in p2 if gfn(r)]
            dropped = [r for r in p2 if not gfn(r)]
            gate_scores[label][gname] = (kept, dropped)
    rank = {}
    for gname in GATES:
        ks = half_stats(gate_scores["T125"][gname][0])
        rank[gname] = min(ks["jan_may"]["net_total"], ks["jun_oct"]["net_total"])
    top2 = sorted(GATES, key=lambda g: -rank[g])[:2]
    results["stack_top2"] = top2
    print("gate ranking by min-half net (T125):", {g: round(rank[g], 2) for g in GATES}, "-> stack:", top2)

    def score_block(name, kept, dropped, p2, label):
        ks, ds = half_stats(kept), half_stats(dropped)
        jm_pool = sum(1 for r in p2 if r["date"] < "2026-06-01")
        jo_pool = sum(1 for r in p2 if r["date"] >= "2026-06-01")
        entry = {"kept": ks, "dropped": ds,
                 "kept_share_jan_may_pct": round(100.0 * ks["jan_may"]["trades"] / jm_pool, 1) if jm_pool else None,
                 "kept_share_jun_oct_pct": round(100.0 * ks["jun_oct"]["trades"] / jo_pool, 1) if jo_pool else None,
                 "kept_share_all_pct": round(100.0 * ks["all"]["trades"] / len(p2), 1) if p2 else None}
        if label == "T125":
            surv = (ks["jan_may"]["net_total"] > 0 and ks["jun_oct"]["net_total"] > 0
                    and entry["kept_share_jan_may_pct"] >= 40.0 and entry["kept_share_jun_oct_pct"] >= 40.0)
            entry["survivor"] = surv
            if surv:
                entry["concentration"] = concentration(kept)
        results["gates"].setdefault(name, {})[label] = entry
        print(f"{name} {label}: kept n={ks['all']['trades']} net={ks['all']['net_total']} "
              f"(JM {ks['jan_may']['net_total']}, JO {ks['jun_oct']['net_total']}, Oct {ks['october']['net_total']}, "
              f"gExp {ks['all']['gross_exp']}) | dropped n={ds['all']['trades']} net={ds['all']['net_total']} "
              f"(JM {ds['jan_may']['net_total']}, JO {ds['jun_oct']['net_total']}, gExp {ds['all']['gross_exp']})"
              + (f" | SURVIVOR={entry.get('survivor')}" if label == "T125" else ""))
        return entry

    for gname in GATES:
        for label in CELLS:
            kept, dropped = gate_scores[label][gname]
            score_block(gname, kept, dropped, pool_rows[label], label)
            dump(kept, f"eq_round9_P2_{gname}_kept_{label}.csv")
            dump(dropped, f"eq_round9_P2_{gname}_dropped_{label}.csv")
    # stack of top-2
    for label in CELLS:
        p2 = pool_rows[label]
        fns = [GATES[g] for g in top2]
        kept = [r for r in p2 if all(f(r) for f in fns)]
        dropped = [r for r in p2 if not all(f(r) for f in fns)]
        sname = "STACK_" + "+".join(top2)
        score_block(sname, kept, dropped, p2, label)
        dump(kept, f"eq_round9_P2_STACK_kept_{label}.csv")
        dump(dropped, f"eq_round9_P2_STACK_dropped_{label}.csv")

    results["survivors"] = [n for n, v in results["gates"].items()
                            if v.get("T125", {}).get("survivor")]
    # ---- diagnosis: P2 Jan-May hole at T125/S050 (report only)
    jm = [r for r in pool_rows["T125"] if r["date"] < "2026-06-01"]
    diag = {"by_month": {}, "by_direction": {}, "by_stock": {}}
    for r in jm:
        diag["by_month"].setdefault(r["date"][:7], []).append(r)
        diag["by_direction"].setdefault(r["direction"], []).append(r)
        diag["by_stock"].setdefault(r["stock"], []).append(r)
    results["diagnosis"] = {k: {kk: stats(vv) for kk, vv in sorted(v.items())}
                            for k, v in diag.items()}
    jm_s = stats(jm)
    print(f"\nDIAGNOSIS P2 Jan-May T125: n={jm_s['trades']} net={jm_s['net_total']} gExp={jm_s['gross_exp']}")
    for kk, vv in sorted(results["diagnosis"]["by_month"].items()):
        print(f"  month {kk}: n={vv['trades']} net={vv['net_total']} gExp={vv['gross_exp']}")
    for kk, vv in sorted(results["diagnosis"]["by_direction"].items()):
        print(f"  dir {kk}: n={vv['trades']} net={vv['net_total']} gExp={vv['gross_exp']}")
    print("\nSurvivors:", results["survivors"] if results["survivors"] else "NONE")
    json.dump(results, open(f"{BASE}/stocks_equity_round9_results.json", "w"), indent=1)

if __name__ == "__main__":
    main()
