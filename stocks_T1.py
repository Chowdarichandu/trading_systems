#!/usr/bin/env python3
"""Line T1 — combined real book. Rules: stocks_T1_frozen.md (frozen before run).
Reads the three component dumps, validates each subset against its published
total to the paisa, then computes the combination + stress battery once."""
import csv, json
from collections import defaultdict

BASE = "/home/hatch/workspace/trading"

def load_inv():
    rows = []
    with open(f"{BASE}/tuning_inv_T1_T125_S050_trades.csv") as f:
        for r in csv.DictReader(f):
            if r["direction"] == "LONG":
                rows.append({"sys": "INV-LONG", "date": r["date"],
                             "stock": r["stock"], "dir": r["direction"],
                             "net": float(r["net_rs_provisional_per100"])})
    return rows

def load_n4():
    rows = []
    with open(f"{BASE}/eq_n4deep_v3_trades_T125_janoct.csv") as f:
        for r in csv.DictReader(f):
            rows.append({"sys": "N4-V3", "date": r["date"],
                         "stock": r["stock"], "dir": r["direction"],
                         "net": float(r["net_rs_provisional_per100"])})
    return rows

def load_p2f():
    rows = []
    with open(f"{BASE}/stocks_tuning_event_V1_combined_trades.csv") as f:
        for r in csv.DictReader(f):
            if r["leg"] == "P2F" and abs(float(r["reaction_ret_pct"])) >= 2.5:
                rows.append({"sys": "P2F", "date": r["date"],
                             "stock": r["symbol"], "dir": r["direction"],
                             "net": float(r["net_rs"])})
    return rows

def rnd(x): return round(x + 0.0, 2)

def stats(rows):
    net = sum(r["net"] for r in rows)
    h1 = sum(r["net"] for r in rows if r["date"] <= "2026-05-31")
    h2 = sum(r["net"] for r in rows if r["date"] >= "2026-06-01")
    oct_ = sum(r["net"] for r in rows if r["date"][:7] == "2026-10")
    months = {}
    for m in range(1, 11):
        key = f"2026-{m:02d}"
        sel = [r for r in rows if r["date"][:7] == key]
        months[key] = {"trades": len(sel), "net": rnd(sum(r["net"] for r in sel))}
    per_stock = defaultdict(float)
    for r in rows: per_stock[r["stock"]] += r["net"]
    breadth_pos = sum(1 for v in per_stock.values() if v > 0)
    return {"trades": len(rows), "net": rnd(net), "h1": rnd(h1), "h2": rnd(h2),
            "oct": rnd(oct_), "months": months,
            "per_stock": {k: rnd(v) for k, v in
                          sorted(per_stock.items(), key=lambda kv: -kv[1])},
            "breadth_pos": breadth_pos, "stocks_traded": len(per_stock),
            "expectancy": rnd(net / len(rows)) if rows else 0.0}

out = {}
inv, n4, p2f = load_inv(), load_n4(), load_p2f()
pub = {"INV-LONG": (inv, 249, 24185.73), "N4-V3": (n4, 56, 7990.43),
       "P2F": (p2f, 39, 15489.08)}
out["validation"] = {}
for name, (rows, n_pub, net_pub) in pub.items():
    got = rnd(sum(r["net"] for r in rows))
    ok = len(rows) == n_pub and abs(got - net_pub) <= 0.01
    out["validation"][name] = {"trades": len(rows), "net": got,
                               "published_trades": n_pub,
                               "published_net": net_pub, "pass": ok}
    assert ok, f"VALIDATION FAILED {name}: {len(rows)} trades, {got} vs {n_pub}/{net_pub}"

book = inv + n4 + p2f
out["components"] = {k: stats(v[0]) for k, v in pub.items()}
out["combined"] = stats(book)

# collisions: (date, stock) traded by >=2 different systems
bykey = defaultdict(list)
for r in book: bykey[(r["date"], r["stock"])].append(r)
coll_pairs, coll_trades, coll_net, pair_break = [], 0, 0.0, defaultdict(int)
for k, rs in bykey.items():
    systems = sorted(set(r["sys"] for r in rs))
    if len(systems) >= 2:
        coll_pairs.append(k); coll_trades += len(rs)
        coll_net += sum(r["net"] for r in rs)
        for i in range(len(systems)):
            for j in range(i + 1, len(systems)):
                pair_break[f"{systems[i]} x {systems[j]}"] += 1
out["collisions"] = {"pairs": len(coll_pairs), "trades_involved": coll_trades,
                     "net_of_colliding": rnd(coll_net),
                     "by_system_pair": dict(pair_break),
                     "detail": sorted([f"{d} {s}" for d, s in coll_pairs])}

# stress 1: ex-top-3 stocks
per_stock = out["combined"]["per_stock"]
top3_stocks = list(per_stock.keys())[:3]
out["stress_ex_top3_stocks"] = {
    "removed": {s: per_stock[s] for s in top3_stocks},
    **stats([r for r in book if r["stock"] not in top3_stocks])}

# stress 2: winsorised at +2000/stock
cap_total = sum(min(v, 2000.0) for v in per_stock.values())
def half_cap(rows, lo, hi):
    ps = defaultdict(float)
    for r in rows:
        if lo <= r["date"] <= hi: ps[r["stock"]] += r["net"]
    return rnd(sum(min(v, 2000.0) for v in ps.values()))
out["stress_winsorised"] = {
    "net": rnd(cap_total),
    "h1": half_cap(book, "2026-01-01", "2026-05-31"),
    "h2": half_cap(book, "2026-06-01", "2026-10-31")}

# stress 3: ex-top-3 trades
top3_trades = sorted(book, key=lambda r: -r["net"])[:3]
rest = sorted(book, key=lambda r: -r["net"])[3:]
s3 = stats(rest)
out["stress_ex_top3_trades"] = {
    "removed": [{"sys": r["sys"], "date": r["date"], "stock": r["stock"],
                 "net": r["net"]} for r in top3_trades],
    "net": s3["net"], "h1": s3["h1"], "h2": s3["h2"], "oct": s3["oct"],
    "trades": s3["trades"]}

# per-component concentration diagnostics (share of combined net)
comb_net = out["combined"]["net"]
out["component_top_stocks"] = {}
for name, rows in (("INV-LONG", inv), ("N4-V3", n4), ("P2F", p2f)):
    ps = defaultdict(float)
    for r in rows: ps[r["stock"]] += r["net"]
    top = sorted(ps.items(), key=lambda kv: -kv[1])[:3]
    out["component_top_stocks"][name] = {
        "top3": {k: rnd(v) for k, v in top},
        "top3_share_of_combined_pct": rnd(100 * sum(v for _, v in top) / comb_net)}

print(json.dumps(out, indent=1))
with open(f"{BASE}/stocks_T1_results.json", "w") as f:
    json.dump(out, f, indent=1)
