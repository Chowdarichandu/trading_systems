#!/usr/bin/env python3
"""IMPROVEMENT AUDIT 2026-11-17 — assembly: Thread 3(a)/(b)/(d) from
on-disk records + merge of T1 and T2/T3 outputs into the final
improvement_audit_results.json and improvement_audit_trades.csv."""
import csv, json, collections
WS = "/home/hatch/workspace/trading"

t1 = json.load(open(f"{WS}/improvement_audit_t1_results.json"))
t23 = json.load(open(f"{WS}/improvement_audit_t23_results.json"))
bfix = json.load(open(f"{WS}/bank_fix_results.json"))

# ---------------------------------------------------------------- T3(a)
d1log = [r for r in csv.DictReader(open(f"{WS}/november_shadow_d1_bank_log.csv"))
         if r["row_type"] != "HEADER" and r["date"].startswith("2026-11")]
nov_legs = [{"date": r["date"], "rep": r["rep"], "stack_net": float(r["stack_net_inr"]),
             "score": r["score_nov_basis"], "bfix1_cell": r["bfix1_cell"],
             "decision": r["decision"]} for r in d1log if r["stack_net_inr"] not in ("", None)]
ctl = bfix["anchors"]["control"]
d1_anchor = bfix["anchors"].get("d1") or bfix["anchors"].get("D1") or {}
t3a = {
    "jan_oct_stack": {"legs": ctl["legs"], "net": ctl["total"],
                      "trade_days": ctl["trade_days"]},
    "jan_oct_d1_kept_legs": 71,
    "jan_oct_d1_net": 126496.0,
    "jan_oct_skipped_legs": ctl["legs"] - 71,
    "jan_oct_skipped_net": round(ctl["total"] - 126496.0, 2),
    "november_stack_legs": nov_legs,
    "november_stack_net": round(sum(x["stack_net"] for x in nov_legs), 2),
    "november_d1_kept": 0,
    "november_bfix1_cf_net": -3440.0,
    "supply_per_day_jan_oct": round(ctl["legs"] / 205, 3),
    "supply_per_day_november": round(len(nov_legs) / 11, 3),
}

# ---------------------------------------------------------------- T3(b)
paper = list(csv.DictReader(open(f"{WS}/stocks_sarvaritu_paper_log.csv")))
live17 = [r for r in csv.DictReader(open(f"{WS}/stocks_sarvaritu_live_shadow_log.csv"))
          if r["date"] == "2026-11-17"]
nov_rows = [dict(comp=r["comp"], net=float(r["net"])) for r in paper]
nov_rows += [dict(comp=r["comp"], net=float(r["net"])) for r in live17]
comps = ["F4", "INV-LONG", "INV-ABOVE", "N4-V3", "P2F", "P2F-R2", "R2-LOWBAND"]
nov_by_comp = {}
for c in comps:
    xs = [r["net"] for r in nov_rows if r["comp"] == c]
    nov_by_comp[c] = {"trades": len(xs), "net": round(sum(xs), 2),
                      "wr": (round(100.0 * sum(1 for x in xs if x > 0) / len(xs), 1) if xs else None)}
sb25 = list(csv.DictReader(open(f"{WS}/wide100_stockbook_sector25w_trades.csv")))
janoct_by_comp = {}
for c in comps:
    e = {}
    for y in ("2025", "2026"):
        xs = [float(r["net"]) for r in sb25 if r["comp"] == c and r["window"] == y
              and r["date"] <= f"{y}-10-31"]
        e[y] = {"trades": len(xs), "net": round(sum(xs), 2),
                "wr": (round(100.0 * sum(1 for x in xs if x > 0) / len(xs), 1) if xs else None)}
    janoct_by_comp[c] = e
nov_total = round(sum(r["net"] for r in nov_rows), 2)
t3b = {"november_by_comp": nov_by_comp,
       "november_total": nov_total,
       "november_trades": len(nov_rows),
       "jan_oct_by_comp_machinery_basis": janoct_by_comp,
       "floor": 15000.0, "gap_to_floor": round(15000.0 - nov_total, 2),
       "trading_days_elapsed": 11, "trading_days_left": 8,
       "pace_per_day_so_far": round(nov_total / 11, 2),
       "pace_needed_per_day": round((15000.0 - nov_total) / 8, 2)}

# ---------------------------------------------------------------- T3(d)
loss = [r for r in csv.DictReader(open(f"{WS}/lossfix_trades.csv"))
        if r["variant"] == "CONTROL" and r["status"] == "CLOSED"]
def cost_row(book, year, trades, net, unit):
    costs = trades * unit
    gross = net + costs
    return {"book": book, "year": year, "trades": trades, "net": round(net, 2),
            "unit_cost": unit, "total_costs": round(costs, 2),
            "gross_before_costs": round(gross, 2),
            "cost_pct_of_gross": round(100.0 * costs / gross, 2) if gross > 0 else None}
costs = []
for book, lab in (("CAND-T5", "EKAM Cand-1"), ("S2", "EKAM Cand-2")):
    for y in (2025, 2026):
        xs = [r for r in loss if r["book"] == book and r["date"][:4] == str(y)
              and r["date"] <= f"{y}-10-31"]
        costs.append(cost_row(lab, y, len(xs), sum(float(r["net"]) for r in xs), 40))
costs.append(cost_row("Stock Book (adopted)", 2025, 1064, 119813.44, 40))
costs.append(cost_row("Stock Book (adopted)", 2026, 1363, 247178.79, 40))
costs.append(cost_row("Bank TUNED STACK v2", 2026, 111, 127351.50, 220))
costs.append(cost_row("Bank D1 (lead)", 2026, 71, 126496.0, 220))
costs.append(cost_row("Bank legacy v21", 2026, 99, 83650.50, 220))
costs.append(cost_row("Nifty TUNED v1", 2026, 74, 103050.25, 220))
costs.append(cost_row("Nifty repaired (N-FIX-1)", 2026, 66, 117170.0, 220))
costs.append(cost_row("EKAM Daily (screened control)", 2025, 79, 63621.50, 40))
costs.append(cost_row("EKAM Daily (screened control)", 2026, 102, 150777.40, 40))
t3d = {"rows": costs}

# ---------------------------------------------------------------- merge
final = {"audit": "improvement_audit_2026-11-17",
         "bases": {"index": "option premiums per 1 lot (Bank 30 / Nifty 65), Rs220/trade",
                   "stocks": "equity cash PROVISIONAL per 100 shares, Rs40/trade",
                   "money": "paper only, real money Rs0"},
         "thread1_cap2000": {k: v for k, v in t1.items() if k != "trades_out"},
         "thread2a_correlations": t23["thread2a"],
         "thread2b_november": t23["thread2b"],
         "thread2c_compensator": t23["thread2c"],
         "thread3a_d1": t3a,
         "thread3b_stockbook_november": t3b,
         "thread3c_ekam_capacity": t23["thread3c"],
         "thread3d_cost_drag": t3d,
         "thread3e_ekam_daily_excursion": t23["thread3e"]}
json.dump(final, open(f"{WS}/improvement_audit_results.json", "w"), indent=1, default=str)

rows_out = list(t1["trades_out"])
for r in csv.DictReader(open(f"{WS}/btst_ind_trades.csv")):
    if r["arm"] == "bank" and r["row"] == "VOTES":
        rows_out.append(dict(thread="T2c", book="BTST-IND Bank VOTES",
                             run="compensator_test", date=r["date"], sym="BANKNIFTY",
                             side=r["side"], entry=r["entry"], exit=r["exit"],
                             net=float(r["net"])))
rows_out += [dict(t) for t in t23["trades_out"]]
cols = ["thread", "book", "run", "window", "comp", "date", "sym", "side",
        "entry", "exit", "exit_date", "net", "entry_date",
        "worst_unrealised_per100"]
with open(f"{WS}/improvement_audit_trades.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    for r in rows_out:
        w.writerow(r)
print("T3a:", json.dumps(t3a, default=str)[:300])
print("T3b november_by_comp:", nov_by_comp)
print("T3b pace:", t3b["pace_per_day_so_far"], "needed:", t3b["pace_needed_per_day"], "gap:", t3b["gap_to_floor"])
print("T3d:")
for c in costs:
    print(f"  {c['book']} {c['year']}: {c['trades']} trades, costs Rs{c['total_costs']:,.0f} = {c['cost_pct_of_gross']}% of gross Rs{c['gross_before_costs']:,.0f}")
print("WROTE improvement_audit_results.json + improvement_audit_trades.csv rows:", len(rows_out))
