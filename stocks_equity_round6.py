#!/usr/bin/env python3
"""Round 6 — V5 re-entry chain diagnostic (Part A), filters (Part B), cost/size sensitivity (Part C).
Reads the frozen re-entry trade CSVs; gross per trade = net + 40 (frozen flat cost per trade per 100 shares).
Part A runs standalone:  python3 stocks_equity_round6.py partA
Part B/C run after the frozen spec exists: python3 stocks_equity_round6.py partBC
"""
import csv, json, sys, collections

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
    rows.sort(key=lambda r: (r["date"], r["stock"], r["round"]))
    return rows

def stats(rows):
    n = len(rows)
    if n == 0:
        return {"trades": 0, "gross_total": 0.0, "net_total": 0.0, "gross_exp": None, "net_exp": None, "win_pct": None}
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

def bucket_round(rd):
    return str(rd) if rd <= 4 else "5+"

def time_bucket(t):
    # t like '09:35'
    if t < "10:30": return "09:35-10:30"
    if t < "12:00": return "10:30-12:00"
    if t < "13:30": return "12:00-13:30"
    return "13:30-15:10"

def partA():
    out = {}
    for ex in ["T10", "T125"]:
        rows = load(ex)
        d = {}
        # by chain round
        d["by_round"] = {b: both([r for r in rows if bucket_round(r["round"]) == b])
                         for b in ["1", "2", "3", "4", "5+"]}
        # annotate chains with previous exit reason
        chains = collections.defaultdict(list)
        for r in rows: chains[(r["date"], r["stock"])].append(r)
        for k in chains: chains[k].sort(key=lambda r: r["round"])
        re_rows = []
        for k, ch in chains.items():
            for i, r in enumerate(ch):
                if i > 0:
                    r2 = dict(r); r2["prev_exit"] = ch[i - 1]["exit_reason"]; re_rows.append(r2)
        d["reentries_total"] = both(re_rows)
        d["by_prev_exit"] = {pe: both([r for r in re_rows if r["prev_exit"] == pe])
                             for pe in ["target", "stop", "square_off"]}
        d["by_reentry_time"] = {tb: both([r for r in re_rows if time_bucket(r["entry_time"]) == tb])
                                for tb in ["09:35-10:30", "10:30-12:00", "12:00-13:30", "13:30-15:10"]}
        out[ex] = d
    json.dump(out, open(f"{BASE}/stocks_equity_round6_partA.json", "w"), indent=1)
    # print compact tables
    for ex in ["T10", "T125"]:
        print(f"\n===== V5 re-entry {ex} — by chain round (gross exp / net exp, Rs per trade per 100 sh) =====")
        for b in ["1", "2", "3", "4", "5+"]:
            s = out[ex]["by_round"][b]
            print(f" round {b}: all n={s['all']['trades']} gExp={s['all']['gross_exp']} nExp={s['all']['net_exp']} | "
                  f"JanMay n={s['jan_may']['trades']} gExp={s['jan_may']['gross_exp']} nExp={s['jan_may']['net_exp']} | "
                  f"JunOct n={s['jun_oct']['trades']} gExp={s['jun_oct']['gross_exp']} nExp={s['jun_oct']['net_exp']}")
        print(f"--- by PREVIOUS exit (re-entries only) ---")
        for pe in ["target", "stop", "square_off"]:
            s = out[ex]["by_prev_exit"][pe]
            print(f" after {pe}: all n={s['all']['trades']} gExp={s['all']['gross_exp']} nExp={s['all']['net_exp']} | "
                  f"JanMay gExp={s['jan_may']['gross_exp']} | JunOct gExp={s['jun_oct']['gross_exp']}")
        print(f"--- by re-entry time of day ---")
        for tb in ["09:35-10:30", "10:30-12:00", "12:00-13:30", "13:30-15:10"]:
            s = out[ex]["by_reentry_time"][tb]
            print(f" {tb}: all n={s['all']['trades']} gExp={s['all']['gross_exp']} nExp={s['all']['net_exp']} | "
                  f"JanMay gExp={s['jan_may']['gross_exp']} | JunOct gExp={s['jun_oct']['gross_exp']}")

def chains_of(rows):
    ch = collections.defaultdict(list)
    for r in rows: ch[(r["date"], r["stock"])].append(r)
    for k in ch: ch[k].sort(key=lambda r: r["round"])
    return ch

def adr_map():
    """Round-3 adr10 formula, per stock-day, from spot_daily.csv."""
    import os
    out = {}
    for sym in sorted(os.listdir(f"{BASE}/data/progressive")):
        p = f"{BASE}/data/progressive/{sym}/spot_daily.csv"
        if not os.path.exists(p): continue
        daily = []
        with open(p) as f:
            for r in csv.DictReader(f):
                try: daily.append({"date": r["date"][:10], "high": float(r["high"]), "low": float(r["low"]), "close": float(r["close"])})
                except Exception: pass
        daily.sort(key=lambda x: x["date"])
        idx = {d["date"]: i for i, d in enumerate(daily)}
        for d in daily:
            i = idx[d["date"]]
            if i < 5: out[(sym, d["date"])] = None; continue
            prior = daily[max(0, i - 10):i]
            if len(prior) < 5: out[(sym, d["date"])] = None; continue
            vals = [(x["high"] - x["low"]) / x["close"] * 100 for x in prior if x["close"]]
            out[(sym, d["date"])] = round(sum(vals) / len(vals), 3) if vals else None
    return out

def gross_pos_both_halves(s):
    return (s["jan_may"]["gross_exp"] or -1) > 0 and (s["jun_oct"]["gross_exp"] or -1) > 0

def partBC():
    ADR = adr_map()
    results = {}
    best = {}  # exit -> (name, rows, summary)
    for ex in ["T10", "T125"]:
        rows = load(ex)
        ch = chains_of(rows)
        variants = {}
        variants["unfiltered"] = rows
        variants["R1a_cap2"] = [r for r in rows if r["round"] <= 2]          # R2 == R1a by frozen spec
        variants["R1b_cap3"] = [r for r in rows if r["round"] <= 3]
        # R3 walk
        r3 = []
        for k, c in ch.items():
            last_taken_exit = None
            for i, r in enumerate(c):
                if i == 0:
                    r3.append(r); last_taken_exit = r["exit_reason"]
                elif last_taken_exit == "target":
                    r3.append(r); last_taken_exit = r["exit_reason"]
        variants["R3_after_target_only"] = r3
        # R4 ADR>=3 stock-days
        variants["R4_adr3"] = [r for r in rows if (ADR.get((r["stock"], r["date"])) or 0) >= 3.0]
        # R5 conditional stacks
        s_r3, s_r4 = both(variants["R3_after_target_only"]), both(variants["R4_adr3"])
        cap2 = variants["R1a_cap2"]
        if gross_pos_both_halves(s_r4):
            variants["R5a_cap2_adr3"] = [r for r in cap2 if (ADR.get((r["stock"], r["date"])) or 0) >= 3.0]
        if gross_pos_both_halves(s_r3):
            r3keys = {(r["date"], r["stock"], r["round"]) for r in r3}
            variants["R5b_cap2_r3"] = [r for r in cap2 if (r["date"], r["stock"], r["round"]) in r3keys]
        if gross_pos_both_halves(s_r3) and gross_pos_both_halves(s_r4):
            r3keys = {(r["date"], r["stock"], r["round"]) for r in r3}
            variants["R5c_cap2_r3_adr3"] = [r for r in variants["R5a_cap2_adr3"] if (r["date"], r["stock"], r["round"]) in r3keys]
        results[ex] = {name: both(vrows) for name, vrows in variants.items()}
        # best Part B variant by net Jan-Oct (excluding unfiltered), tie -> gross exp
        cand = [(v["all"]["net_total"], v["all"]["gross_exp"], name) for name, v in results[ex].items() if name != "unfiltered"]
        cand.sort(reverse=True)
        best[ex] = (cand[0][2], variants[cand[0][2]])
        print(f"\n===== Part B — V5 re-entry {ex} =====")
        for name, s in results[ex].items():
            a, jm, jo, oc = s["all"], s["jan_may"], s["jun_oct"], s["october"]
            print(f" {name}: n={a['trades']} gExp={a['gross_exp']} nExp={a['net_exp']} net={a['net_total']} | "
                  f"JanMay n={jm['trades']} gExp={jm['gross_exp']} net={jm['net_total']} | "
                  f"JunOct n={jo['trades']} gExp={jo['gross_exp']} net={jo['net_total']} | Oct n={oc['trades']} net={oc['net_total']}")
        # dump kept trades for best variant
        bname, brows = best[ex]
        with open(f"{BASE}/eq_round6_v5_{ex}_best_{bname}.csv", "w", newline="") as f:
            w = csv.writer(f); w.writerow(["date","stock","direction","setup","round","entry_time","entry","exit_reason","exit_time","net_rs_provisional_per100","event_status"])
            for r in sorted(brows, key=lambda r: (r["date"], r["stock"], r["round"])):
                w.writerow([r["date"], r["stock"], r["direction"], r["setup"], r["round"], r["entry_time"], r["entry"], r["exit_reason"], r["exit_time"], r["net"], r["event_status"]])
        print(f" best Part B variant ({ex}): {bname} (trades dumped)")
    # ---- Part C ----
    partC = {}
    c_targets = {}
    for ex in ["T10", "T125"]:
        c_targets[f"best_{ex}"] = best[ex]
    c_targets["unfiltered_T125"] = ("unfiltered", load("T125"))
    print("\n===== Part C — cost & size sensitivity =====")
    for label, (name, rows) in c_targets.items():
        n = len(rows); g = sum(r["gross"] for r in rows)
        jm = [r for r in rows if r["half"] == "jan_may"]; jo = [r for r in rows if r["half"] == "jun_oct"]
        gjm = sum(r["gross"] for r in jm); gjo = sum(r["gross"] for r in jo)
        entry = {"variant": name, "trades": n, "gross_total_per100": round(g, 2),
                 "breakeven_flat_cost_per_trade_at_100sh": round(g / n, 2) if n else None}
        for c in [40, 30, 20, 10]:
            entry[f"net_at_cost_{c}"] = {"all": round(g - c * n, 2),
                                         "jan_may": round(gjm - c * len(jm), 2),
                                         "jun_oct": round(gjo - c * len(jo), 2)}
        for size in [200, 500]:
            entry[f"net_at_{size}sh_flat40_per_trade"] = round(g * size / 100.0 - 40 * n, 2)
            entry[f"net_at_{size}sh_flat40_jan_may"] = round(gjm * size / 100.0 - 40 * len(jm), 2)
            entry[f"net_at_{size}sh_flat40_jun_oct"] = round(gjo * size / 100.0 - 40 * len(jo), 2)
        entry["breakeven_shares_at_flat40"] = round(4000.0 / (g / n), 0) if n and g > 0 else None
        partC[label] = entry
        print(f" {label} ({name}): n={n} gross={entry['gross_total_per100']} breakevenCost={entry['breakeven_flat_cost_per_trade_at_100sh']} "
              f"net@40={entry['net_at_cost_40']['all']} net@30={entry['net_at_cost_30']['all']} net@20={entry['net_at_cost_20']['all']} net@10={entry['net_at_cost_10']['all']} "
              f"| 200sh@40flat={entry['net_at_200sh_flat40_per_trade']} 500sh@40flat={entry['net_at_500sh_flat40_per_trade']} breakevenShares@40={entry['breakeven_shares_at_flat40']}")
    json.dump({"partB": results, "partC": partC}, open(f"{BASE}/stocks_equity_round6_results.json", "w"), indent=1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "partA":
        partA()
    elif len(sys.argv) > 1 and sys.argv[1] == "partBC":
        partBC()
