#!/usr/bin/env python3
"""Round 8 — exit sweep on structured V5 re-entry pools (P1=R5a, P2=M5).
Spec: stocks_equity_round8_frozen.md (frozen before scoring).
Chains are rebuilt per exit cell from the frozen V5 signal stream of
stocks_equity_reentry.py (its context/detector section is exec'd, its
scoring section is not). Gross per 100 shares; net = gross - 40.
"""
import csv, json, collections, os

BASE = "/home/hatch/workspace/trading"
COST = 40.0

# ---- load the frozen signal machinery (everything above the scoring section)
src = open(f"{BASE}/stocks_equity_reentry_ext.py").read()
head = src.split("# ---------- score both modes")[0]
NS = {}
exec(compile(head, "stocks_equity_reentry_head", "exec"), NS)
DAYCTX = NS["DAYCTX"]; SYMBOLS = NS["SYMBOLS"]; ALL_DAYS = NS["ALL_DAYS"]
v4_head = NS["v4_head"]; skor_head = NS["skor_head"]; pool_pick = NS["pool_pick"]
QTY = 100

def adr_map():
    out = {}
    for sym in sorted(os.listdir(f"{BASE}/data/progressive_ext")):
        p = f"{BASE}/data/progressive_ext/{sym}/spot_daily.csv"
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

ADR = adr_map()
def adr3(sym, day):
    return (ADR.get((sym, day)) or 0) >= 3.0

# ---- exit replays ----
def replay_plain(candles, entry_idx, sign, entry, tgt_pct, stp_pct):
    target = entry * (1 + sign * tgt_pct / 100); stop = entry * (1 - sign * stp_pct / 100)
    for j in range(entry_idx, len(candles)):
        c = candles[j]
        if sign == 1:
            if c["low"] <= stop: er, ep = "stop", stop
            elif c["high"] >= target: er, ep = "target", target
            elif c["time"] == "15:10": er, ep = "square_off", c["close"]
            else: continue
        else:
            if c["high"] >= stop: er, ep = "stop", stop
            elif c["low"] <= target: er, ep = "target", target
            elif c["time"] == "15:10": er, ep = "square_off", c["close"]
            else: continue
        return er, ep, c["time"], j, 100.0 * sign * (ep - entry)
    c = candles[-1]
    return "square_off", c["close"], c["time"], len(candles) - 1, 100.0 * sign * (c["close"] - entry)

def replay_runner(candles, entry_idx, sign, entry):
    """Spec bar order: pre-partial stop(-0.5%) first, then +1.0% partial
    (50 sh booked, remainder stop -> breakeven, remainder NOT evaluated
    on that candle); post-partial: BE stop first, then +2.0% target,
    then 15:10 square-off of the remainder."""
    stop = entry * (1 - sign * 0.5 / 100)
    part_px = entry * (1 + sign * 1.0 / 100)
    target = entry * (1 + sign * 2.0 / 100)
    def hit_stop(c, px): return c["low"] <= px if sign == 1 else c["high"] >= px
    def hit_up(c, px): return c["high"] >= px if sign == 1 else c["low"] <= px
    partial_done = False
    for j in range(entry_idx, len(candles)):
        c = candles[j]
        if not partial_done:
            if hit_stop(c, stop):
                return "stop", stop, c["time"], j, 100.0 * sign * (stop - entry)
            if hit_up(c, part_px):
                partial_done = True
                continue
            if c["time"] == "15:10":
                return "square_off", c["close"], c["time"], j, 100.0 * sign * (c["close"] - entry)
        else:
            if hit_stop(c, entry):
                g = 50.0 * sign * (part_px - entry) + 50.0 * sign * (entry - entry)
                return "stop_be_after_partial", entry, c["time"], j, g
            if hit_up(c, target):
                g = 50.0 * sign * (part_px - entry) + 50.0 * sign * (target - entry)
                return "target_after_partial", target, c["time"], j, g
            if c["time"] == "15:10":
                g = 50.0 * sign * (part_px - entry) + 50.0 * sign * (c["close"] - entry)
                return "squareoff_after_partial", c["close"], c["time"], j, g
    c = candles[-1]
    if partial_done:
        g = 50.0 * sign * (part_px - entry) + 50.0 * sign * (c["close"] - entry)
        return "squareoff_after_partial", c["close"], c["time"], len(candles) - 1, g
    return "square_off", c["close"], c["time"], len(candles) - 1, 100.0 * sign * (c["close"] - entry)

# ---- chain builder (V5 pool_pick, re-entry, one exit cell) ----
def run_chain(sym, day, cell):
    ctx = DAYCTX.get((sym, day))
    if ctx is None: return []
    candles = ctx["candles"]
    trades, start = [], 0
    while True:
        chosen = pool_pick(ctx, v4_head(ctx, start), skor_head(ctx, start))
        if chosen is None: break
        setup, dirc, sig, idx = chosen
        if idx + 1 >= len(candles): break
        entry_idx = idx + 1
        entry = float(candles[entry_idx]["open"])
        direction = "LONG" if dirc == "CE" else "SHORT"
        sign = 1 if direction == "LONG" else -1
        if cell[0] == "RUNNER":
            er, ep, et, exit_idx, gross = replay_runner(candles, entry_idx, sign, entry)
        else:
            _, tp, sp = cell
            er, ep, et, exit_idx, gross = replay_plain(candles, entry_idx, sign, entry, tp, sp)
        trades.append({"date": day, "stock": sym, "direction": direction, "setup": setup,
                       "round": len(trades) + 1, "entry_time": candles[entry_idx]["time"],
                       "entry": round(entry, 2), "exit_reason": er, "exit_time": et,
                       "exit_price": round(ep, 2), "gross": round(gross, 2),
                       "net": round(gross - COST, 2), "event_status": ctx["event_status"]})
        start = exit_idx
    return trades

CELLS = [("PLAIN", 1.25, 0.4), ("PLAIN", 1.25, 0.5), ("PLAIN", 1.25, 0.75),
         ("PLAIN", 1.5, 0.4), ("PLAIN", 1.5, 0.5), ("PLAIN", 1.5, 0.75),
         ("PLAIN", 2.0, 0.4), ("PLAIN", 2.0, 0.5), ("PLAIN", 2.0, 0.75),
         ("RUNNER", 2.0, 0.5)]
GATE_CELLS = [("PLAIN", 1.0, 0.5), ("PLAIN", 1.25, 0.5)]
def cell_label(cell):
    if cell[0] == "RUNNER": return "RUNNER_T200_P100_S050"
    return f"T{int(cell[1]*100):03d}_S{int(cell[2]*100):03d}"

def stats(rows):
    n = len(rows)
    if n == 0:
        return {"trades": 0, "win_pct": None, "target_pct": None, "gross_total": 0.0,
                "gross_exp": None, "net_total": 0.0}
    g = sum(r["gross"] for r in rows); nt = sum(r["net"] for r in rows)
    wins = sum(1 for r in rows if r["net"] > 0)
    tgts = sum(1 for r in rows if r["exit_reason"] in ("target", "target_after_partial"))
    return {"trades": n, "win_pct": round(100.0 * wins / n, 1),
            "target_pct": round(100.0 * tgts / n, 1),
            "gross_total": round(g, 2), "gross_exp": round(g / n, 2),
            "net_total": round(nt, 2)}

def periods(rows):
    return {"all": stats(rows),
            "jan_may": stats([r for r in rows if r["date"] < "2026-06-01"]),
            "jun_oct": stats([r for r in rows if r["date"] >= "2026-06-01"]),
            "october": stats([r for r in rows if r["date"] >= "2026-10-01"])}

def concentration(rows):
    months = collections.defaultdict(list)
    for r in rows: months[r["date"][:7]].append(r)
    table = {m: stats(months[m]) for m in sorted(months)}
    total_net = sum(r["net"] for r in rows)
    out = {"per_month": table, "largest_month_share_pct": None, "top5_trades_share_pct": None,
           "largest_month": None}
    if total_net > 0:
        pos = {m: s["net_total"] for m, s in table.items() if s["net_total"] > 0}
        if pos:
            lm = max(pos, key=pos.get)
            out["largest_month"] = lm
            out["largest_month_share_pct"] = round(100.0 * pos[lm] / total_net, 1)
        top5 = sorted(rows, key=lambda r: -r["net"])[:5]
        out["top5_net"] = round(sum(r["net"] for r in top5), 2)
        out["top5_trades_share_pct"] = round(100.0 * out["top5_net"] / total_net, 1)
    return out

def pools(chain_rows):
    p1 = [r for r in chain_rows if r["round"] <= 2 and adr3(r["stock"], r["date"])]
    p2 = [r for r in p1 if r["entry_time"] < "10:30"]
    return {"P1_R5a": p1, "P2_M5": p2}

def main():
    results = {"gate": {}, "cells": {}, "survivors": []}
    # ---- gate first: cells T10 and T125 at stop 0.5
    GATE_EXPECT = {("P1_R5a", "PLAIN", 1.0): (1471, -27493.49),
                   ("P1_R5a", "PLAIN", 1.25): (1421, -19541.85),
                   ("P2_M5", "PLAIN", 1.0): (947, 5772.37),
                   ("P2_M5", "PLAIN", 1.25): (918, 10657.81)}
    chains = {}
    for cell in GATE_CELLS + CELLS:
        if cell_label(cell) in chains: continue
        rows = []
        for sym in SYMBOLS:
            for day in ALL_DAYS:
                rows.extend(run_chain(sym, day, cell))
        chains[cell_label(cell)] = rows
        pl = pools(rows)
        if cell in GATE_CELLS:
            for pname, prows in pl.items():
                s = stats(prows)
                exp_n, exp_net = GATE_EXPECT[(pname, "PLAIN", cell[1])]
                ok = (s["trades"] == exp_n and abs(s["net_total"] - exp_net) < 0.01)
                results["gate"][f"{pname}_{cell_label(cell)}"] = {
                    "expected_trades": exp_n, "got_trades": s["trades"],
                    "expected_net": exp_net, "got_net": s["net_total"], "pass": ok}
                print(f"GATE {pname} {cell_label(cell)}: trades {s['trades']} vs {exp_n}, "
                      f"net {s['net_total']} vs {exp_net} -> {'PASS' if ok else 'FAIL'}")
    results["gate_all_pass"] = all(g["pass"] for g in results["gate"].values())
    if not results["gate_all_pass"]:
        json.dump(results, open(f"{BASE}/stocks_equity_round8_results.json", "w"), indent=1)
        print("GATE FAILED — stopping per frozen spec.")
        return
    # ---- cost-realism pool entry prices (gate cell T125 chains)
    gate_rows = chains[cell_label(("PLAIN", 1.25, 0.5))]
    gate_pools = pools(gate_rows)
    results["cost_realism"] = {}
    for pname, prows in gate_pools.items():
        avg = sum(r["entry"] for r in prows) / len(prows) if prows else None
        results["cost_realism"][pname] = {
            "pool_trades_gate_cell": len(prows),
            "avg_entry_price": round(avg, 2) if avg else None,
            "one_side_value_100sh": round(avg * 100, 2) if avg else None,
            "cost40_pct_of_one_side": round(100.0 * 40.0 / (avg * 100), 3) if avg else None,
            "cost40_pct_of_roundtrip_turnover": round(100.0 * 40.0 / (2 * avg * 100), 3) if avg else None}
    # ---- score all cells
    for cell in CELLS:
        label = cell_label(cell)
        pl = pools(chains[label])
        results["cells"][label] = {}
        for pname, prows in pl.items():
            s = periods(prows)
            surv = s["jan_may"]["net_total"] > 0 and s["jun_oct"]["net_total"] > 0
            entry = {"periods": s, "survivor_both_halves_net_pos": surv}
            if surv:
                entry["concentration"] = concentration(prows)
                results["survivors"].append(f"{pname}:{label}")
            results["cells"][label][pname] = entry
            with open(f"{BASE}/eq_round8_{pname.split('_')[0]}_{label}.csv", "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["date", "stock", "direction", "setup", "round", "entry_time", "entry",
                            "exit_reason", "exit_time", "exit_price",
                            "gross_rs_provisional_per100", "net_rs_provisional_per100", "event_status"])
                for r in sorted(prows, key=lambda r: (r["date"], r["stock"], r["round"])):
                    w.writerow([r["date"], r["stock"], r["direction"], r["setup"], r["round"],
                                r["entry_time"], r["entry"], r["exit_reason"], r["exit_time"],
                                r["exit_price"], r["gross"], r["net"], r["event_status"]])
            a, jm, jo, oc = s["all"], s["jan_may"], s["jun_oct"], s["october"]
            print(f"{pname} {label}: n={a['trades']} win={a['win_pct']} tgt={a['target_pct']} "
                  f"gExp={a['gross_exp']} net={a['net_total']} | JM net={jm['net_total']} (n={jm['trades']}, gExp={jm['gross_exp']}) | "
                  f"JO net={jo['net_total']} (n={jo['trades']}, gExp={jo['gross_exp']}) | Oct net={oc['net_total']} (n={oc['trades']}) | SURV={surv}")
    json.dump(results, open(f"{BASE}/stocks_equity_round8_results.json", "w"), indent=1)
    print("\nSurvivors:", results["survivors"] if results["survivors"] else "NONE")
    print("Cost realism:", json.dumps(results["cost_realism"]))

if __name__ == "__main__":
    main()
