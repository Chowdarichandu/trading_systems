#!/usr/bin/env python3
"""
SPEED TRACK C — GREEN-DAY BOOK (formal scoring run, 2026-11-14).

The construction was frozen in writing in round5_greenday_book_2026-11-14.md
BEFORE this run:
  Book P = TUNED STACK v2 legs + at most ONE increment leg per stack-idle
           day, priority D1 > V3 > B1, increments from the rounds' own leg
           files with each round driver's own extraction rule.
  Book D = TUNED STACK v2 legs + D1 increment only.
  No other combinations, no parameter tuning, November sets no rule.
Gate: Jan-Oct totals / legs / trade-days / Rs-per-trade-day vs Rs 900 /
win rate / month table (no red month) / halves / ex-top-3 DAYS /
independent re-sum / green-red-no-trade day counts and green-day shares
(of trade-days and of all 205 days), each vs the stack alone.
Verdict (pre-registered): THE CANDIDATE only if a book beats the stack on
total AND green-day share, keeps zero red months, and improves November's
day-count. Paper only, real money Rs 0, Bank Nifty options per 1 lot (30),
Rs 220/trade inside every stored net, UNIQUE-ONCE.
"""
import csv, json
from collections import defaultdict
from pathlib import Path

TR = Path(__file__).resolve().parent
MONTHS = [f"2026-{i:02d}" for i in range(1, 11)]
TD = {"2026-01": 20, "2026-02": 21, "2026-03": 19, "2026-04": 20,
      "2026-05": 19, "2026-06": 21, "2026-07": 23, "2026-08": 21,
      "2026-09": 21, "2026-10": 20}
assert sum(TD.values()) == 205
H1 = MONTHS[:5]; H2 = MONTHS[5:]
PRIORITY = ["D1", "V3", "B1"]

# ---------- loaders (pass 1) ----------
def load_stack():
    legs = []
    with open(TR / "solid60_programme_2026-11-13_bank_A_stack_features.csv",
              newline="") as f:
        for r in csv.DictReader(f):
            legs.append({"date": r["date"], "net": float(r["x1_net"]),
                         "source": "STACK", "direction": r["direction"],
                         "detail": r["rep"]})
    return legs

def load_increments(stack_days):
    inc = {s: [] for s in PRIORITY}
    with open(TR / "oi_buildup_trades.csv", newline="") as f:
        for r in csv.DictReader(f):
            if (r["index"] == "BANKNIFTY" and r["variant"] == "V3"
                    and r["mode"] == "real" and r["trade_date"] <= "2026-10-31"
                    and r["trade_date"] not in stack_days):
                inc["V3"].append({"date": r["trade_date"],
                                  "net": float(r["net"]), "source": "V3",
                                  "direction": r["direction"],
                                  "detail": f"{r['direction']} {r['strike']} "
                                            f"{r['entry']}->{r['exit']} "
                                            f"{r['exit_reason']}"})
    with open(TR / "round2_trades.csv", newline="") as f:
        for r in csv.DictReader(f):
            if (r["index"] == "BANKNIFTY" and r["variant"] == "B1"
                    and r["mode"] == "real" and r["trade_date"] <= "2026-10-31"
                    and r["trade_date"] not in stack_days):
                inc["B1"].append({"date": r["trade_date"],
                                  "net": float(r["net"]), "source": "B1",
                                  "direction": r["direction"],
                                  "detail": f"{r['direction']} {r['strike']} "
                                            f"{r['entry']}->{r['exit']} "
                                            f"{r['exit_reason']}"})
    with open(TR / "round4_trades.csv", newline="") as f:
        for r in csv.DictReader(f):
            if (r["index"] == "BANKNIFTY" and r["family"] == "D1"
                    and r["mode"] == "real" and r["trade_date"] <= "2026-10-31"
                    and r["trade_date"] not in stack_days):
                inc["D1"].append({"date": r["trade_date"],
                                  "net": float(r["net"]), "source": "D1",
                                  "direction": r["direction"],
                                  "detail": f"{r['direction']} {r['strike']} "
                                            f"{r['entry']}->{r['exit']} "
                                            f"{r['exit_reason']}"})
    return inc

# ---------- independent re-sum (pass 2: raw column sums, separate code) ----
def resum_stack():
    tot = 0.0; n = 0
    with open(TR / "solid60_programme_2026-11-13_bank_A_stack_features.csv",
              newline="") as f:
        for r in csv.DictReader(f):
            tot += float(r["x1_net"]); n += 1
    return n, round(tot, 2)

def resum_increment(source, stack_days):
    tot = 0.0; n = 0
    if source == "V3":
        fn, key = "oi_buildup_trades.csv", ("variant", "V3")
    elif source == "B1":
        fn, key = "round2_trades.csv", ("variant", "B1")
    else:
        fn, key = "round4_trades.csv", ("family", "D1")
    with open(TR / fn, newline="") as f:
        for r in csv.DictReader(f):
            if (r["index"] == "BANKNIFTY" and r[key[0]] == key[1]
                    and r["mode"] == "real" and r["trade_date"] <= "2026-10-31"
                    and r["trade_date"] not in stack_days):
                tot += float(r["net"]); n += 1
    return n, round(tot, 2)

# ---------- metrics ----------
def day_map(legs):
    d = defaultdict(float); c = defaultdict(int)
    for l in legs:
        d[l["date"]] += l["net"]; c[l["date"]] += 1
    return dict(d), dict(c)

def status(net, traded):
    if not traded: return "NO_TRADE"
    return "GREEN" if net > 0 else ("RED" if net < 0 else "FLAT")

def metrics(legs, cal_dates=None):
    total = round(sum(l["net"] for l in legs), 2)
    dm, lc = day_map(legs)
    td = len(dm)
    green = sum(1 for v in dm.values() if v > 0)
    red = sum(1 for v in dm.values() if v < 0)
    flat = sum(1 for v in dm.values() if v == 0)
    months = {}
    for m in MONTHS:
        ml = [l for l in legs if l["date"][:7] == m]
        md = {d: v for d, v in dm.items() if d[:7] == m}
        mtot = round(sum(l["net"] for l in ml), 2)
        months[m] = {
            "total": mtot, "legs": len(ml), "trade_days": len(md),
            "per_trade_day": round(mtot / len(md), 2) if md else None,
            "per_cal_day": round(mtot / TD[m], 2),
            "green": sum(1 for v in md.values() if v > 0),
            "red": sum(1 for v in md.values() if v < 0),
            "flat": sum(1 for v in md.values() if v == 0),
            "no_trade": TD[m] - len(md)}
    halves = {}
    for name, ms in (("H1", H1), ("H2", H2)):
        hl = [l for l in legs if l["date"][:7] in ms]
        hd = {d: v for d, v in dm.items() if d[:7] in ms}
        ht = round(sum(l["net"] for l in hl), 2)
        halves[name] = {"total": ht, "legs": len(hl), "trade_days": len(hd),
                        "per_trade_day": round(ht / len(hd), 2) if hd else None,
                        "green": sum(1 for v in hd.values() if v > 0),
                        "red": sum(1 for v in hd.values() if v < 0)}
    top3 = sorted(dm.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
    ex_total = round(total - sum(v for _, v in top3), 2)
    ex_td = td - len(top3)
    return {
        "legs": len(legs), "total": total, "trade_days": td,
        "per_trade_day": round(total / td, 2) if td else None,
        "per_leg": round(total / len(legs), 2),
        "per_cal_day": round(total / 205, 2),
        "win_rate_pct": round(100 * sum(1 for l in legs if l["net"] > 0)
                              / len(legs), 1),
        "green_days": green, "red_days": red, "flat_days": flat,
        "no_trade_days": 205 - td,
        "green_share_trade_days_pct": round(100 * green / td, 1) if td else None,
        "green_share_all_days_pct": round(100 * green / 205, 1),
        "red_months": [m for m in MONTHS if months[m]["total"] < 0],
        "months": months, "halves": halves,
        "ex_top3_days": {"removed": [{"date": d, "net": round(v, 2)}
                                     for d, v in top3],
                         "total_after": ex_total, "trade_days_after": ex_td,
                         "per_trade_day_after": round(ex_total / ex_td, 2)
                         if ex_td else None}}

# ---------- build ----------
stack = load_stack()
stack_days = {l["date"] for l in stack}
assert len(stack) == 111 and round(sum(l["net"] for l in stack), 2) == 127351.50
assert resum_stack() == (111, 127351.50)
inc = load_increments(stack_days)
anchors = {"D1": (27, 8973.00), "V3": (42, 3360.00), "B1": (12, 4560.00)}
for s, (n, t) in anchors.items():
    got = (len(inc[s]), round(sum(l["net"] for l in inc[s]), 2))
    assert got == (n, t), (s, got)
    assert resum_increment(s, stack_days) == (n, t), (s, "resum")
    assert len({l["date"] for l in inc[s]}) == len(inc[s]), (s, "dup date")

# extraction validation: each single-increment merge must reproduce its round
validation = {}
for s, (tot, td) in {"D1": (136324.50, 116), "V3": (130711.50, 131),
                     "B1": (131911.50, 101)}.items():
    m = metrics(stack + inc[s])
    assert (m["total"], m["trade_days"]) == (tot, td), (s, m["total"], m["trade_days"])
    validation[s] = {"merged_total": m["total"], "merged_trade_days": td,
                     "matches_round_report": True}

# priority choice on stack-idle days
by_date = defaultdict(list)
for s in PRIORITY:
    for l in inc[s]:
        by_date[l["date"]].append(l)
chosen, skipped = [], []
for d in sorted(by_date):
    lst = sorted(by_date[d], key=lambda l: PRIORITY.index(l["source"]))
    chosen.append(lst[0])
    for l in lst[1:]:
        skipped.append({**l, "chosen_source": lst[0]["source"]})
assert len(chosen) == 61 and round(sum(l["net"] for l in chosen), 2) == 13493.00

book_p = stack + chosen
book_d = stack + inc["D1"]
m_stack = metrics(stack); m_p = metrics(book_p); m_d = metrics(book_d)

# ---------- November counterfactual (Nov 2-13 trading days) ----------
NOV_DAYS = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05",
            "2026-11-06", "2026-11-09", "2026-11-11", "2026-11-12",
            "2026-11-13"]
nov_stack = {}
with open(TR / "november_shadow_stack_bank_log.csv", newline="") as f:
    for r in csv.DictReader(f):
        if r.get("net_inr"):
            nov_stack[r["date"]] = float(r["net_inr"])
assert round(sum(nov_stack.values()), 2) == -2680.00 and len(nov_stack) == 4
nov_stack_days = set(nov_stack)

def nov_increments(source):
    out = []
    if source == "V3":
        with open(TR / "oi_buildup_trades.csv", newline="") as f:
            for r in csv.DictReader(f):
                if (r["index"] == "BANKNIFTY" and r["variant"] == "V3"
                        and r["mode"] == "real" and r["trade_date"] in NOV_DAYS
                        and r["trade_date"] not in nov_stack_days):
                    out.append({"date": r["trade_date"],
                                "net": float(r["net"]), "source": "V3"})
    if source == "B1":
        with open(TR / "round2_trades.csv", newline="") as f:
            for r in csv.DictReader(f):
                if (r["index"] == "BANKNIFTY" and r["variant"] == "B1"
                        and r["mode"] == "real" and r["trade_date"] in NOV_DAYS
                        and r["trade_date"] not in nov_stack_days):
                    out.append({"date": r["trade_date"],
                                "net": float(r["net"]), "source": "B1"})
    if source == "D1":
        with open(TR / "round4_trades.csv", newline="") as f:
            for r in csv.DictReader(f):
                if (r["index"] == "BANKNIFTY" and r["family"] == "D1"
                        and r["mode"] == "real" and r["trade_date"] in NOV_DAYS
                        and r["trade_date"] not in nov_stack_days):
                    out.append({"date": r["trade_date"],
                                "net": float(r["net"]), "source": "D1"})
    return out

nov_inc = {s: nov_increments(s) for s in PRIORITY}
assert [(l["date"], l["net"]) for l in nov_inc["V3"]] == [("2026-11-02", 2480.00)]
assert nov_inc["B1"] == [] and nov_inc["D1"] == []
nov_by_date = defaultdict(list)
for s in PRIORITY:
    for l in nov_inc[s]:
        nov_by_date[l["date"]].append(l)
nov_chosen = {}
for d, lst in nov_by_date.items():
    nov_chosen[d] = sorted(lst, key=lambda l: PRIORITY.index(l["source"]))[0]

def nov_table(book):
    rows = []
    for d in NOV_DAYS:
        s_net = nov_stack.get(d)
        if book == "STACK":
            inc_l = None; net = s_net
        elif book == "D1":
            inc_l = next((l for l in nov_inc["D1"] if l["date"] == d), None)
            net = s_net if inc_l is None else (s_net or 0.0) + inc_l["net"]
            if s_net is None and inc_l is None: net = None
        else:
            inc_l = nov_chosen.get(d)
            net = s_net if inc_l is None else (s_net or 0.0) + inc_l["net"]
            if s_net is None and inc_l is None: net = None
        traded = net is not None
        rows.append({"date": d, "stack_net": s_net,
                     "increment_source": (inc_l or {}).get("source"),
                     "increment_net": (inc_l or {}).get("net"),
                     "book_net": round(net, 2) if traded else None,
                     "status": status(net or 0.0, traded)})
    tot = round(sum(r["book_net"] for r in rows if r["book_net"] is not None), 2)
    return {"rows": rows, "total": tot,
            "green": sum(1 for r in rows if r["status"] == "GREEN"),
            "red": sum(1 for r in rows if r["status"] == "RED"),
            "no_trade": sum(1 for r in rows if r["status"] == "NO_TRADE"),
            "trade_days": sum(1 for r in rows if r["status"] != "NO_TRADE")}

nov = {b: nov_table(b) for b in ("STACK", "D1", "PRIORITY")}
def nov_improves(b):
    a, c = nov["STACK"], nov[b]
    return (c["green"] > a["green"] and c["red"] <= a["red"]
            and c["no_trade"] < a["no_trade"] and c["total"] > a["total"])

# ---------- verdicts (pre-registered rule) ----------
def verdict(m, nov_book):
    checks = {
        "total_beats_stack": m["total"] > m_stack["total"],
        "per_trade_day_ge_900": (m["per_trade_day"] or 0) >= 900,
        "green_share_trade_days_beats_stack":
            m["green_share_trade_days_pct"] > m_stack["green_share_trade_days_pct"],
        "green_share_all_days_beats_stack":
            m["green_share_all_days_pct"] > m_stack["green_share_all_days_pct"],
        "zero_red_months": m["red_months"] == [],
        "halves_positive": all(m["halves"][h]["total"] > 0 for h in ("H1", "H2")),
        "ex_top3_days_positive": m["ex_top3_days"]["total_after"] > 0,
        "november_day_count_improves": nov_improves(nov_book)}
    cand = all([checks["total_beats_stack"],
                checks["green_share_trade_days_beats_stack"],
                checks["green_share_all_days_beats_stack"],
                checks["zero_red_months"],
                checks["november_day_count_improves"]])
    return {"checks": checks, "is_candidate": cand}

v_p = verdict(m_p, "PRIORITY"); v_d = verdict(m_d, "D1")

# ---------- day-level CSV (Jan-Oct gate window + November) ----------
cal = []
with open(TR / "round4_history" / "banknifty_morning_basis.csv", newline="") as f:
    for r in csv.DictReader(f):
        if r["date"] <= "2026-10-31":
            cal.append(r["date"])
assert len(cal) == 205
sdm, slc = day_map(stack)
pdm, plc = day_map(book_p); ddm, dlc = day_map(book_d)
chosen_by_date = {l["date"]: l for l in chosen}
d1_by_date = {l["date"]: l for l in inc["D1"]}
csv_rows = []
for d in cal:
    csv_rows.append({
        "period": "JAN_OCT", "date": d,
        "stack_legs": slc.get(d, 0), "stack_net": round(sdm.get(d, 0.0), 2),
        "stack_status": status(sdm.get(d, 0.0), d in sdm),
        "priority_increment_source": (chosen_by_date.get(d) or {}).get("source"),
        "priority_increment_net": round((chosen_by_date.get(d) or {})
                                        .get("net", 0.0), 2),
        "priority_book_legs": plc.get(d, 0),
        "priority_book_net": round(pdm.get(d, 0.0), 2),
        "priority_status": status(pdm.get(d, 0.0), d in pdm),
        "d1_increment_net": round((d1_by_date.get(d) or {}).get("net", 0.0), 2),
        "stack_d1_book_legs": dlc.get(d, 0),
        "stack_d1_book_net": round(ddm.get(d, 0.0), 2),
        "stack_d1_status": status(ddm.get(d, 0.0), d in ddm)})
nov_rows_p = {r["date"]: r for r in nov["PRIORITY"]["rows"]}
nov_rows_d = {r["date"]: r for r in nov["D1"]["rows"]}
for d in NOV_DAYS:
    rp, rd = nov_rows_p[d], nov_rows_d[d]
    csv_rows.append({
        "period": "NOVEMBER", "date": d,
        "stack_legs": 1 if d in nov_stack else 0,
        "stack_net": round(nov_stack.get(d, 0.0), 2),
        "stack_status": status(nov_stack.get(d, 0.0), d in nov_stack),
        "priority_increment_source": rp["increment_source"],
        "priority_increment_net": round(rp["increment_net"] or 0.0, 2),
        "priority_book_legs": (1 if d in nov_stack else 0)
                              + (1 if rp["increment_net"] is not None else 0),
        "priority_book_net": round(rp["book_net"] or 0.0, 2),
        "priority_status": rp["status"],
        "d1_increment_net": round(rd["increment_net"] or 0.0, 2),
        "stack_d1_book_legs": (1 if d in nov_stack else 0)
                              + (1 if rd["increment_net"] is not None else 0),
        "stack_d1_book_net": round(rd["book_net"] or 0.0, 2),
        "stack_d1_status": rd["status"]})
with open(TR / "round5_greenday_book_days.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
    w.writeheader(); w.writerows(csv_rows)

# re-sum the written CSV independently of the in-memory books
chk = {"stack": 0.0, "priority": 0.0, "d1": 0.0}
with open(TR / "round5_greenday_book_days.csv", newline="") as f:
    for r in csv.DictReader(f):
        if r["period"] == "JAN_OCT":
            chk["stack"] += float(r["stack_net"])
            chk["priority"] += float(r["priority_book_net"])
            chk["d1"] += float(r["stack_d1_book_net"])
assert round(chk["stack"], 2) == m_stack["total"]
assert round(chk["priority"], 2) == m_p["total"]
assert round(chk["d1"], 2) == m_d["total"]

out = {
    "meta": {"book": "Bank Nifty only", "basis": "option premiums per 1 lot (30)",
             "cost": "Rs 220/trade inside stored nets", "counting": "UNIQUE-ONCE",
             "real_money_inr": 0, "window": "Jan-Oct 2026 (205 trading days)",
             "november_window": "Nov 2-13 2026 (9 trading days)"},
    "extraction_validation": validation,
    "increment_anchors": {s: {"legs": len(inc[s]),
                              "total": round(sum(l["net"] for l in inc[s]), 2)}
                          for s in PRIORITY},
    "priority_choice": {
        "chosen_legs": len(chosen),
        "chosen_total": round(sum(l["net"] for l in chosen), 2),
        "by_source": {s: {"legs": sum(1 for l in chosen if l["source"] == s),
                          "total": round(sum(l["net"] for l in chosen
                                             if l["source"] == s), 2)}
                      for s in PRIORITY},
        "skipped_legs": len(skipped),
        "skipped_total": round(sum(l["net"] for l in skipped), 2),
        "skipped": skipped},
    "stack": m_stack, "book_priority": m_p, "book_stack_d1": m_d,
    "verdicts": {"PRIORITY": v_p, "STACK_D1": v_d},
    "november": nov,
    "resum": {"stack": resum_stack(),
              "increments": {s: resum_increment(s, stack_days) for s in PRIORITY},
              "day_csv": {k: round(v, 2) for k, v in chk.items()},
              "ok": True}}
with open(TR / "round5_greenday_book_results.json", "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps({
    "STACK": {k: m_stack[k] for k in ("legs", "total", "trade_days",
              "per_trade_day", "win_rate_pct", "green_days", "red_days",
              "no_trade_days", "green_share_trade_days_pct",
              "green_share_all_days_pct", "red_months")},
    "PRIORITY": {k: m_p[k] for k in ("legs", "total", "trade_days",
                 "per_trade_day", "win_rate_pct", "green_days", "red_days",
                 "no_trade_days", "green_share_trade_days_pct",
                 "green_share_all_days_pct", "red_months")},
    "STACK_D1": {k: m_d[k] for k in ("legs", "total", "trade_days",
                 "per_trade_day", "win_rate_pct", "green_days", "red_days",
                 "no_trade_days", "green_share_trade_days_pct",
                 "green_share_all_days_pct", "red_months")},
    "verdicts": v_p, "verdicts_d1": v_d,
    "november": {b: {k: nov[b][k] for k in ("total", "green", "red",
                    "no_trade", "trade_days")} for b in nov}}, indent=1))
