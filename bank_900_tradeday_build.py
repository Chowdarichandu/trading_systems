#!/usr/bin/env python3
"""
BANK NIFTY — Rs 900 PER TRADE-DAY VERIFICATION (owner bar 2026-11-13 18:31 IST)

Owner's bar: least minimum AVERAGE return Rs 900/day counted ONLY on days a
trade happens (trade-days). No-trade days excluded from the average entirely.
Pure option BUYING books only. Paper only, real money Rs 0. 1 lot (30),
Rs 220/trade inside every stored net. Offline verification — nothing armed,
nothing modified.

PRE-REGISTRATION (fixed before scoring):
- Books: TUNED STACK v2 (primary), LEGACY BNF-PAPER-V1, PB1, PB3, PB4
  (gated premium-band books of the bank_2000 programme). Annex: PB0, PB2, U1.
- Parents (frozen, read-only) + anchors asserted exact in-run:
  STACK  solid60_programme_2026-11-13_bank_A_stack_features.csv  111 legs +127,351.50
  LEGACY bank_engine_r6_v21_trades.csv                            99 legs  +83,650.50
  PB1    bank_2000_PB1_stack_lt500_trades.csv                     32 legs  +69,749.50
  PB3    bank_2000_PB3_union_lt500_trades.csv                     35 legs  +75,989.50
  PB4    bank_2000_PB4_union_lt650_trades.csv                     52 legs  +82,611.50
  PB0 27/+59,902.50 · PB2 49/+76,371.50 · U1 123/+118,111.50 (annex)
- Calendar denominator: 205 trading days Jan-Oct 2026; month trading days
  Jan20 Feb21 Mar19 Apr20 May19 Jun21 Jul23 Aug21 Sep21 Oct20 (workspace
  convention, bank_max_report_2026-11-13). Halves: H1=Jan-May, H2=Jun-Oct.
- GATE (all legs, same run):
  G1 trade-day average >= Rs 900
  G2 total > 0
  G3 both halves > 0 on the calendar basis AND on the trade-day basis
  G4 no red month on the calendar basis (every month total > 0)
  G5 ex-top-3 (3 largest legs removed) total > 0, trade-day basis stated
  G6 placebo: 2,000 random same-count subsets (seed 42) of the book's
     parent pool (bank_2000 s0G pools: PB1->STACK, PB3/PB4->UNION,
     PB0->LEGACY, PB2->STACK); statistic = subset total / subset distinct
     trade-days; book's statistic must rank >= 95th percentile.
     For STACK and LEGACY the own-pool draw is the book itself (degenerate
     by construction): their binding placebo/timing evidence is the
     standing gate on record; a UNION-pool percentile is computed and
     reported as a supplementary check, not a binding leg.
  G7 independent re-sum: every CSV re-read in a separate pass; totals must
     match to the paisa.
- November forward (stack): november_shadow_stack_bank_log.csv, verified
  in-run, never taken on trust.
"""
import csv, json, random, statistics
from collections import defaultdict

TD = {"2026-01":20,"2026-02":21,"2026-03":19,"2026-04":20,"2026-05":19,
      "2026-06":21,"2026-07":23,"2026-08":21,"2026-09":21,"2026-10":20}
assert sum(TD.values()) == 205
MONTHS = sorted(TD.keys())
H1 = [m for m in MONTHS if m <= "2026-05"]; H2 = [m for m in MONTHS if m >= "2026-06"]

def load(path, netcol):
    legs = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if row.get(netcol) in (None, ""): continue
            legs.append({"date": row["date"], "net": float(row[netcol]),
                         "prem": float(row["entry_premium"]) if row.get("entry_premium") else None})
    return legs

def resum(path, netcol):
    tot = 0.0; n = 0
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if row.get(netcol) in (None, ""): continue
            tot += float(row[netcol]); n += 1
    return n, round(tot, 2)

def day_map(legs):
    d = defaultdict(float)
    for l in legs: d[l["date"]] += l["net"]
    return dict(d)

def metrics(legs):
    total = round(sum(l["net"] for l in legs), 2)
    dm = day_map(legs)
    tdays = len(dm)
    daynets = [dm[d] for d in sorted(dm)]
    wins = sum(1 for l in legs if l["net"] > 0)
    mt = {}
    for m in MONTHS:
        ml = [l for l in legs if l["date"][:7] == m]
        mtot = round(sum(l["net"] for l in ml), 2)
        mtd_ = len({l["date"] for l in ml})
        mt[m] = {"total": mtot, "cal_days": TD[m], "per_cal_day": round(mtot/TD[m], 2),
                 "trade_days": mtd_, "per_trade_day": (round(mtot/mtd_, 2) if mtd_ else None),
                 "legs": len(ml)}
    def half(ms):
        hl = [l for l in legs if l["date"][:7] in ms]
        ht = round(sum(l["net"] for l in hl), 2)
        hd = len({l["date"] for l in hl})
        return {"total": ht, "trade_days": hd,
                "per_trade_day": (round(ht/hd, 2) if hd else None)}
    srt = sorted(legs, key=lambda l: -l["net"])
    ex = srt[3:]
    ex_tot = round(sum(l["net"] for l in ex), 2)
    ex_td = len({l["date"] for l in ex})
    return {
        "legs": len(legs), "total": total, "trade_days": tdays,
        "no_trade_days": 205 - tdays,
        "per_trade_day": round(total/tdays, 2) if tdays else None,
        "per_leg": round(total/len(legs), 2),
        "per_cal_day": round(total/205, 2),
        "win_rate_pct": round(100*wins/len(legs), 1),
        "months": mt,
        "red_months": [m for m in MONTHS if mt[m]["total"] < 0],
        "zero_months": [m for m in MONTHS if mt[m]["total"] == 0],
        "halves": {"H1": half(H1), "H2": half(H2)},
        "day_dist": {
            "share_ge900_pct": round(100*sum(1 for v in daynets if v >= 900)/tdays, 1) if tdays else None,
            "share_pos_pct": round(100*sum(1 for v in daynets if v > 0)/tdays, 1) if tdays else None,
            "median": round(statistics.median(daynets), 2) if daynets else None,
            "worst": round(min(daynets), 2) if daynets else None,
            "best": round(max(daynets), 2) if daynets else None},
        "ex_top3": {"total": ex_tot, "trade_days": ex_td,
                    "per_trade_day": (round(ex_tot/ex_td, 2) if ex_td else None),
                    "removed": [round(l["net"], 2) for l in srt[:3]]},
    }

def placebo(book_legs, pool_legs, draws=2000, seed=42):
    rng = random.Random(seed)
    k = len(book_legs)
    dm = day_map(book_legs)
    stat = sum(l["net"] for l in book_legs) / len(dm)
    below = 0; stats = []
    for _ in range(draws):
        sub = rng.sample(pool_legs, k)
        sd = defaultdict(float)
        for l in sub: sd[l["date"]] += l["net"]
        s = sum(sd.values()) / len(sd)
        stats.append(s)
        if s < stat: below += 1
    stats.sort()
    return {"statistic": round(stat, 2),
            "percentile": round(100*below/draws, 1),
            "p95_of_draws": round(stats[int(0.95*draws)], 2),
            "draws": draws, "seed": seed}

BOOKS = {
    "STACK":  ("solid60_programme_2026-11-13_bank_A_stack_features.csv", "x1_net", 111, 127351.50),
    "LEGACY": ("bank_engine_r6_v21_trades.csv", "net_inr", 99, 83650.50),
    "PB1":    ("bank_2000_PB1_stack_lt500_trades.csv", "net_inr", 32, 69749.50),
    "PB3":    ("bank_2000_PB3_union_lt500_trades.csv", "net_inr", 35, 75989.50),
    "PB4":    ("bank_2000_PB4_union_lt650_trades.csv", "net_inr", 52, 82611.50),
    "PB0":    ("bank_2000_PB0_legacy_lt500_trades.csv", "net_inr", 27, 59902.50),
    "PB2":    ("bank_2000_PB2_stack_lt650_trades.csv", "net_inr", 49, 76371.50),
    "U1":     ("bank_2000_U1_union_all_trades.csv", "net_inr", 123, 118111.50),
}
POOLS = {"PB1": "STACK", "PB2": "STACK", "PB0": "LEGACY", "PB3": "U1", "PB4": "U1"}

legs = {}; out = {"books": {}}
for name, (path, col, n_anchor, tot_anchor) in BOOKS.items():
    L = load(path, col)
    n2, tot2 = resum(path, col)   # G7 independent re-sum
    assert len(L) == n_anchor, (name, len(L), n_anchor)
    assert abs(round(sum(l["net"] for l in L), 2) - tot_anchor) < 0.01, (name, "anchor")
    assert n2 == len(L) and abs(tot2 - tot_anchor) < 0.01, (name, "resum")
    legs[name] = L
    out["books"][name] = {"metrics": metrics(L), "resum_ok": True}

for name in BOOKS:
    m = out["books"][name]["metrics"]
    entry = {"g1_avg_ge900": (m["per_trade_day"] is not None and m["per_trade_day"] >= 900),
             "g2_total_pos": m["total"] > 0,
             "g3_halves": all(m["halves"][h]["total"] > 0 and (m["halves"][h]["per_trade_day"] or 0) > 0 for h in ("H1", "H2")),
             "g4_no_red_month": len(m["red_months"]) == 0,
             "g5_extop3_pos": m["ex_top3"]["total"] > 0}
    if name in POOLS:
        pl = placebo(legs[name], legs[POOLS[name]])
        entry["placebo"] = pl
        entry["g6_placebo_ge95"] = pl["percentile"] >= 95.0
        entry["gate_pass"] = all(entry[k] for k in
            ("g1_avg_ge900","g2_total_pos","g3_halves","g4_no_red_month","g5_extop3_pos","g6_placebo_ge95"))
    else:  # incumbents: own-pool degenerate; supplementary union-pool percentile
        pl = placebo(legs[name], legs["U1"])
        entry["placebo"] = {"note": "own-pool draw is the book itself (degenerate); "
                                     "supplementary percentile vs UNION pool of 123 known Bank legs",
                            **pl}
        entry["g6_placebo_ge95"] = None
        entry["gate_pass"] = all(entry[k] for k in
            ("g1_avg_ge900","g2_total_pos","g3_halves","g4_no_red_month","g5_extop3_pos"))
    if name == "U1":
        # bank_2000 binding leg: a union must beat its best parent. U1 total
        # Rs 118,111.50 < STACK Rs 127,351.50 -> NOT a pass, whatever the
        # trade-day average says; it is packaging of the other books.
        entry["gate_pass"] = False
        entry["declared_note"] = ("NOT A PASS — bank_2000 binding leg failed: union total "
            "Rs 118,111.50 does not beat its best parent (STACK Rs 127,351.50); "
            "supplementary percentile 0.0 vs its own pool by construction (it is the pool).")
    out["books"][name]["gate"] = entry

# ---- November forward verification (stack), from the frozen log itself ----
nov = []
with open("november_shadow_stack_bank_log.csv", newline="") as f:
    for row in csv.DictReader(f):
        if row.get("net_inr") not in (None, ""):
            nov.append({"date": row["date"], "net": float(row["net_inr"]),
                        "prem": float(row["entry_premium"])})
nov_dm = day_map(nov)
nov_tot = round(sum(l["net"] for l in nov), 2)
expect = {"2026-11-04": 2480.00, "2026-11-09": -1720.00,
          "2026-11-12": -1720.00, "2026-11-13": -1720.00}
assert {d: round(v, 2) for d, v in nov_dm.items()} == expect, nov_dm
out["november_stack"] = {"legs": len(nov), "trade_days": len(nov_dm),
    "total": nov_tot, "per_trade_day": round(nov_tot/len(nov_dm), 2),
    "days": {d: round(v, 2) for d, v in sorted(nov_dm.items())},
    "entry_premiums": [l["prem"] for l in nov]}

# November band admission: legacy PRIMARY legs + stack legs, deduped (bank_2000 rule)
leg_nov = []
with open("november_paper_bank_log.csv", newline="") as f:
    for row in csv.DictReader(f):
        if row.get("channel") == "PRIMARY" and row.get("net_inr") not in (None, ""):
            leg_nov.append({"date": row["date"], "net": float(row["net_inr"]),
                            "prem": float(row["entry_premium"]),
                            "key": (row["date"], row["direction"], row["entry_time"], float(row["entry_premium"]))})
seen = {}
for l in nov: seen[(l["date"], None, None, l["prem"])] = l  # stack copies kept (band test uses premium only)
all_prems = sorted({l["prem"] for l in nov} | {l["prem"] for l in leg_nov})
out["november_bands"] = {"all_parent_entry_premiums": all_prems,
    "min_premium": min(all_prems),
    "PB1_admitted": sum(1 for p in all_prems if p < 500),
    "PB3_admitted": sum(1 for p in all_prems if p < 500),
    "PB4_admitted": sum(1 for p in all_prems if p < 650),
    "note": "distinct November parent entry premiums across stack log + legacy PRIMARY log; "
            "band books admit legs by entry premium only"}

with open("bank_900_tradeday_results.json", "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps({n: {"legs": b["metrics"]["legs"], "total": b["metrics"]["total"],
    "trade_days": b["metrics"]["trade_days"], "per_trade_day": b["metrics"]["per_trade_day"],
    "per_leg": b["metrics"]["per_leg"], "wr": b["metrics"]["win_rate_pct"],
    "red_months": b["metrics"]["red_months"],
    "placebo_pct": b["gate"]["placebo"]["percentile"],
    "gate_pass": b["gate"]["gate_pass"],
    "gate": {k: v for k, v in b["gate"].items() if k.startswith("g")}}
    for n, b in out["books"].items()}, indent=1))
print("NOVEMBER STACK:", json.dumps(out["november_stack"]))
print("NOVEMBER BANDS:", json.dumps(out["november_bands"]))
