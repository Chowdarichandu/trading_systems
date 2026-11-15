#!/usr/bin/env python3
"""STOCK OPTIONS — PREP. Builds the frozen trade lists for sources (a)
EKAM-daily 2c and (b) HOLD L35-H15 from their published trade files and
verifies counts + cash totals against the published lines (SPEC s.1).
Source (c) rows are appended by stock_options_prep_c.py once its sleeve
verification passes. Local files only — no API calls.
Output: stock_options_trades.csv (cash fields; option fields blank)."""
import csv, os, sys

WS = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(WS, "stock_options_trades.csv")
FIELDS = ["source", "year", "sym", "comp", "dir", "signal_date",
          "entry_date", "exit_date", "cash_entry", "cash_exit", "cash_net",
          "cash_exit_kind", "expiry", "strike", "opt_type", "lot_size",
          "opt_entry", "opt_exit", "opt_exit_date_used", "opt_exit_kind",
          "net_per_lot", "net_per100", "status", "nc_reason"]

def inf(x):
    return float(x) if x not in ("", None) else None

rows = []

# ---- (a) EKAM-daily 2c
ekam = [r for r in csv.DictReader(open(os.path.join(WS, "ekam2c_trades.csv")))
        if r["book"] == "EKAM2c"]
def in_win(d, y):
    return d[:4] == str(y) and 1 <= int(d[5:7]) <= 10
for y, pub_n, pub_net in ((2025, 74, 42954.60), (2026, 102, 141328.40)):
    sel = [r for r in ekam if in_win(r["entry_date"], y)]
    tot = round(sum(float(r["net"]) for r in sel), 2)
    assert len(sel) == pub_n and tot == pub_net, (y, len(sel), tot)
    for r in sel:
        rows.append(dict(source="EKAM2C", year=y, sym=r["sym"],
                         comp=r["comps"], dir="LONG",
                         signal_date=r["signal_date"],
                         entry_date=r["entry_date"], exit_date=r["exit_date"],
                         cash_entry=r["entry"], cash_exit=r["exit"],
                         cash_net=r["net"], cash_exit_kind=r["exit_kind"],
                         status="PENDING_FETCH"))
    print(f"(a) EKAM2C {y}: {len(sel)} trades, cash net {tot} == published")

# ---- (b) HOLD L35-H15
hold = list(csv.DictReader(open(os.path.join(
    WS, "hold_programme_r2_best_cell_trades.csv"))))
for y, pub_n, pub_net in ((2025, 83, 42163.0), (2026, 103, 83963.0)):
    sel = [r for r in hold if r["window"] == str(y)]
    tot = round(sum(float(r["net_inr"]) for r in sel), 2)
    assert len(sel) == pub_n and tot == pub_net, (y, len(sel), tot)
    for r in sel:
        rows.append(dict(source="HOLD", year=y, sym=r["sym"], comp="L35-H15",
                         dir="LONG", signal_date="",
                         entry_date=r["entry_date"], exit_date=r["exit_date"],
                         cash_entry=r["entry"], cash_exit=r["exit"],
                         cash_net=r["net_inr"],
                         cash_exit_kind=r["exit_kind"],
                         status="PENDING_FETCH"))
    print(f"(b) HOLD {y}: {len(sel)} trades, cash net {tot} == published")

with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS)
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in FIELDS})
print(f"wrote {OUT}: {len(rows)} rows")
