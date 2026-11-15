#!/usr/bin/env python3
"""STOCK OPTIONS FAR-EXPIRY — PREP (SPEC stock_options_far_SPEC.md s.1).
Builds the EKAM-daily 2c trade list (identical rows to the first run's
prep, source EKAM2C only) and asserts counts + cash totals against the
published lines. Local files only — no API calls.
Output: stock_options_far_trades.csv (cash fields; option fields blank)."""
import csv, os

WS = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(WS, "stock_options_far_trades.csv")
FIELDS = ["source", "year", "sym", "comp", "dir", "signal_date",
          "entry_date", "exit_date", "cash_entry", "cash_exit", "cash_net",
          "cash_exit_kind", "expiry", "days_to_expiry", "strike",
          "opt_type", "lot_size", "opt_entry", "opt_exit",
          "opt_exit_date_used", "opt_exit_kind", "net_per_lot",
          "net_per100", "status", "nc_reason"]

rows = []
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
    print(f"EKAM2C {y}: {len(sel)} trades, cash net {tot} == published")

with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS)
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in FIELDS})
print(f"wrote {OUT}: {len(rows)} rows")
