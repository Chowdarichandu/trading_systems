#!/usr/bin/env python3
"""Daily Earner — Milestone 3 (Stocks verification) + §4 Combined.
Stocks: NO new book — the Stock Book's existing verified ledgers only:
adopted Variant C dumps (stocks_engine_adoptedC_book2026_trades.csv) and the
November forward paper log (stocks_sarvaritu_paper_log.csv).
Combined: arithmetic day-line sums of the PASSING segment books —
Bank = legacy frame alone (Milestone 1 B1), Nifty = TUNED v2 (best passing
single, §2) with the TUNED v1 variant also computed, Stocks = Stock Book.
All figures labelled by segment; the combined figure is an arithmetic total
against the owner's bar, never a merged verdict.
"""
import csv, json
from collections import defaultdict
from pathlib import Path

TR = Path.home() / "workspace/trading"
def fnum(x): return float(x) if x not in ("", None) else 0.0
MONTHS = [f"2026-{m:02d}" for m in range(1, 11)]
NOV_DAYS = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05", "2026-11-06",
            "2026-11-09", "2026-11-11", "2026-11-12", "2026-11-13"]

# ---------- Stocks Jan-Oct 2026 ----------
book = list(csv.DictReader(open(TR / "stocks_engine_adoptedC_book2026_trades.csv")))
total = sum(fnum(r["net"]) for r in book)
assert len(book) == 1363 and abs(total - 247178.79) < 0.01, total
months = {m: 0.0 for m in MONTHS}
day_net = defaultdict(float)
for r in book:
    months[r["date"][:7]] += fnum(r["net"]); day_net[r["date"]] += fnum(r["net"])
srt = sorted((fnum(r["net"]) for r in book), reverse=True)
wins = sum(1 for r in book if fnum(r["net"]) > 0)

daily = list(csv.DictReader(open(TR / "volrix/nifty_daily_2019_2026.csv")))
trading_days = [r["date"] for r in daily if "2026-01-01" <= r["date"] <= "2026-10-31"]
series = [day_net.get(d, 0.0) for d in trading_days]
stocks = {
    "total": total, "trades": len(book), "win_rate_pct": round(wins / len(book) * 100, 1),
    "months": months, "red_months": [m for m, v in months.items() if v < 0],
    "best_month": max(months, key=months.get), "worst_month": min(months, key=months.get),
    "ex_top3_trades": total - sum(srt[:3]), "top3_trades": srt[:3],
    "days_with_trades": len(day_net),
    "avg_per_trading_day": round(total / len(trading_days), 2),
    "avg_per_active_day": round(total / len(day_net), 2),
    "days_ge2000": sum(1 for v in series if v >= 2000),
    "days_in_zone": sum(1 for v in series if 2000 <= v <= 3000),
    "days_gt3000": sum(1 for v in series if v > 3000),
    "pos_days": sum(1 for v in series if v > 0),
    "day_net": {d: day_net.get(d, 0.0) for d in trading_days},
}
book25 = [r for r in csv.DictReader(open(TR / "stocks_engine_adoptedC_book2025_trades.csv"))
          if r["date"] <= "2025-10-31"]
stocks["y2025_janoct_total"] = sum(fnum(r["net"]) for r in book25)
stocks["y2025_janoct_trades"] = len(book25)
assert abs(stocks["y2025_janoct_total"] - 119813.44) < 0.01

# ---------- Stocks November (paper log, final through Nov 12) ----------
nov = list(csv.DictReader(open(TR / "stocks_sarvaritu_paper_log.csv")))
nov_total = sum(fnum(r["net"]) for r in nov)
assert len(nov) == 30 and abs(nov_total - 7965.74) < 0.01, nov_total
nov_day = defaultdict(float)
for r in nov: nov_day[r["date"]] += fnum(r["net"])
stocks_nov_series = [[d, nov_day.get(d, 0.0)] for d in NOV_DAYS]

# ---------- Combined Jan-Oct ----------
bank_legs = list(csv.DictReader(open(TR / "daily_earner_bank_janoct_trades.csv")))
bank_day = defaultdict(float)
for r in bank_legs:
    if r["stream"] == "LEGACY": bank_day[r["date"]] += fnum(r["net_inr"])
bank_total = sum(bank_day.values())
assert abs(bank_total - 83650.50) < 0.01, bank_total
nifty = json.load(open(TR / "daily_earner_nifty_results.json"))
v2_day = nifty["daily_stats"]  # placeholder, replaced below
import json as _json
# TUNED v2 / v1 day nets were stored in the nifty results under frame/v1 only;
# recompute v2 day net from the stored frame legs file (nifty_next_phase_trades.csv)
frame = list(csv.DictReader(open(TR / "nifty_next_phase_trades.csv")))
def frame_day(rows):
    dn = defaultdict(float)
    for r in rows: dn[r["date"]] += fnum(r["net_inr"])
    return {d: dn.get(d, 0.0) for d in trading_days}
v1_rows = [r for r in frame if not (r["component"] == "B" and r["direction"] == "PE")]
v2_rows = [r for r in v1_rows if not (r["component"] in ("A", "C") and r["direction"] == "CE")]
v1_day, v2_day = frame_day(v1_rows), frame_day(v2_rows)
bank_day_full = {d: bank_day.get(d, 0.0) for d in trading_days}
stocks_day = stocks["day_net"]

def combined_stats(nifty_day):
    ser = [bank_day_full[d] + nifty_day[d] + stocks_day[d] for d in trading_days]
    tot = sum(ser)
    return {"total": tot, "avg_per_day": round(tot / len(ser), 2),
            "days_ge2000": sum(1 for v in ser if v >= 2000),
            "days_in_zone": sum(1 for v in ser if 2000 <= v <= 3000),
            "days_gt3000": sum(1 for v in ser if v > 3000),
            "days_ge5000": sum(1 for v in ser if v >= 5000),
            "pos_days": sum(1 for v in ser if v > 0),
            "worst_day": min(ser), "best_day": max(ser)}
comb_v2 = combined_stats(v2_day)
comb_v1 = combined_stats(v1_day)

# ---------- Combined November ----------
bank_nov_rows = list(csv.DictReader(open(TR / "daily_earner_bank_november_trades.csv")))
bank_legacy_nov = defaultdict(float)
for r in bank_nov_rows:
    if r["book"].startswith("LEGACY"): bank_legacy_nov[r["date"]] += fnum(r["net_inr"])
# Nifty TUNED v2 November: DEC-S1 shadow legs surviving v2's drop rule
decs1_log = [r for r in csv.DictReader(open(TR / "november_shadow_decs1_nifty_log.csv"))
             if r["system_source"] not in ("", "none") and r["net_inr"] not in ("", None)]
def comp_of(src): return src.replace("DEC-S1 ", "").strip()
v2_nov_legs = [r for r in decs1_log
               if not (comp_of(r["system_source"]) == "B" and r["direction"] == "PE")
               and not (comp_of(r["system_source"]) in ("A", "C") and r["direction"] == "CE")]
v1_nov_legs = [r for r in decs1_log if not (comp_of(r["system_source"]) == "B" and r["direction"] == "PE")]
comb_nov, cum = [], 0.0
for d in NOV_DAYS:
    b = bank_legacy_nov.get(d, 0.0)
    n2 = sum(fnum(r["net_inr"]) for r in v2_nov_legs if r["date"] == d)
    s = nov_day.get(d, 0.0)
    cum += b + n2 + s
    comb_nov.append([d, b, n2, s, b + n2 + s, cum])
comb_nov_v1_total = sum(bank_legacy_nov.get(d, 0.0) + sum(fnum(r["net_inr"]) for r in v1_nov_legs if r["date"] == d) + nov_day.get(d, 0.0) for d in NOV_DAYS)

out = {"stocks": {k: v for k, v in stocks.items() if k != "day_net"},
       "stocks_nov_series": stocks_nov_series,
       "combined_v2": comb_v2, "combined_v1": comb_v1,
       "combined_nov_series": comb_nov,
       "combined_nov_total_v2line": cum, "combined_nov_total_v1line": comb_nov_v1_total,
       "bank_legacy_nov_total": sum(bank_legacy_nov.values()),
       "nifty_v2_nov_legs": len(v2_nov_legs), "nifty_v1_nov_total": sum(fnum(r["net_inr"]) for r in v1_nov_legs),
       "trading_days": len(trading_days)}
with open(TR / "daily_earner_combined_results.json", "w") as fh: json.dump(out, fh, indent=1)
print(json.dumps(out, indent=1))
