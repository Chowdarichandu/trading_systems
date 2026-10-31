"""Build four_column_jan2025_oct2026.csv + month/grand aggregates.
Paper only, no orders. Sources (frozen, no re-tuning):
- Bank V4, Skill Bank, Skill Nifty: capped_v2_summary_YYYY-MM.json
  v4_capped_trades / skill_capped_trades slices (now complete Jan 2025-Oct 2026;
  Dec 2025 was run fresh with progressive_capped_v2.py, (lA) 2025 was run
  fresh with four_column_la_2025.py after exact Jan-2026 validation).
- Nifty (lA): merged_skill_la_summary_YYYY-MM.json la_capped_trades, NIFTY slice
  (2026 existing; 2025 newly run, same frozen definition).
- 29 Oct 2026: four_column_29oct_candidates.json — no-trade in all four
  columns, so the CSV row is 0/empty and October-with-29-Oct = October 1-28.
Cap convention: within each calendar month, prospective target >= Rs500,
max 3 index/week, max 1/symbol/week (capped-v2 precedent). Columns are
separate systems, not deduped across columns.
"""
import os, json, csv
from collections import defaultdict

BASE = os.path.expanduser("~/workspace/trading")
PROG = os.path.join(BASE, "data/progressive")

def fmt_trade(t, kind):
    if t is None:
        return ""
    if kind == "la":
        return f"PE rescan {t['exit_reason']} {t['net_rs']:+.0f}"
    return f"{t['setup']} {t['direction']} {t['exit_reason']} {t['net_rs']:+.0f}"

def main():
    days = []
    import pandas as pd
    n = pd.read_csv(os.path.join(PROG, "NIFTY/spot_5m.csv"), parse_dates=["timestamp"])
    days = sorted(n["timestamp"].dt.strftime("%Y-%m-%d").unique().tolist())
    days.append("2026-10-29")
    per_day = {d: {"nifty_la": None, "bank_v4": None, "skill_bank": None, "skill_nifty": None} for d in days}
    # also collect (lA) Bank mirror + V4 Nifty for reconciliation appendix
    extra = {d: {"la_bank": None, "v4_nifty": None} for d in days}
    months = []
    for y in (2025, 2026):
        for m in range(1, 13):
            if y == 2026 and m > 10:
                continue
            months.append(f"{y}-{m:02d}")
    for k in months:
        cv = json.load(open(os.path.join(PROG, f"capped_v2_summary_{k}.json")))
        for t in cv["v4_capped_trades"]:
            if t["symbol"] == "BANKNIFTY":
                per_day[t["date"]]["bank_v4"] = t
            elif t["symbol"] == "NIFTY":
                extra[t["date"]]["v4_nifty"] = t
        for t in cv["skill_capped_trades"]:
            if t["symbol"] == "BANKNIFTY":
                per_day[t["date"]]["skill_bank"] = t
            elif t["symbol"] == "NIFTY":
                per_day[t["date"]]["skill_nifty"] = t
        mg = json.load(open(os.path.join(PROG, f"merged_skill_la_summary_{k}.json")))
        for t in mg["la_capped_trades"]:
            if t["symbol"] == "NIFTY":
                per_day[t["date"]]["nifty_la"] = t
            elif t["symbol"] == "BANKNIFTY":
                extra[t["date"]]["la_bank"] = t
    # 29 Oct: verified no-trade in all four columns (four_column_29oct.py);
    # per_day row stays None/0. Assert no capped trade was loaded for it.
    assert all(v is None for v in per_day["2026-10-29"].values())
    rows = []
    for d in days:
        r = {"date": d}
        for col, key in (("nifty_la", "nifty_la"), ("bank_v4", "bank_v4"),
                         ("skill_bank", "skill_bank"), ("skill_nifty", "skill_nifty")):
            t = per_day[d][key]
            r[f"{col}_net"] = int(t["net_rs"]) if t else 0
            r[f"{col}_trade"] = fmt_trade(t, "la" if col == "nifty_la" else "other")
        rows.append(r)
    out_csv = os.path.join(BASE, "four_column_jan2025_oct2026.csv")
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "nifty_la_net", "nifty_la_trade", "bank_v4_net", "bank_v4_trade",
                                          "skill_bank_net", "skill_bank_trade", "skill_nifty_net", "skill_nifty_trade"])
        w.writeheader()
        w.writerows(rows)
    print(f"CSV rows={len(rows)} (plus header) first={rows[0]['date']} last={rows[-1]['date']}")
    # month aggregates
    cols = ["nifty_la", "bank_v4", "skill_bank", "skill_nifty"]
    print("\nMONTH | " + " | ".join(cols))
    cum = {c: 0 for c in cols}
    grand = {}
    for k in months:
        line = [k]
        for c in cols:
            ts = [per_day[d][c] for d in days if d.startswith(k) and per_day[d][c]]
            net = sum(t["net_rs"] for t in ts); green = sum(1 for t in ts if t["net_rs"] > 0)
            cum[c] += net
            line.append(f"{len(ts)}t {green}g {net:+.0f} cum{cum[c]:+.0f}")
        print(" | ".join(line))
    print("\nGRAND (Jan 2025-Oct 2026 incl 29 Oct):")
    for c in cols:
        ts = [per_day[d][c] for d in days if per_day[d][c]]
        net = sum(t["net_rs"] for t in ts); green = sum(1 for t in ts if t["net_rs"] > 0)
        # max DD from date-ordered cumulative
        cumv = peak = dd = 0
        for t in sorted(ts, key=lambda x: x["date"]):
            cumv += t["net_rs"]; peak = max(peak, cumv); dd = max(dd, peak - cumv)
        grand[c] = (len(ts), green, net)
        print(f"{c}: trades={len(ts)} green={green} ({100*green/len(ts):.1f}%) net={net:+.0f} expectancy={net/len(ts):+.2f} maxDD={dd:.0f}")
    print("\nSUBTOTALS:")
    for label, pred in (("2025", lambda d: d.startswith("2025")),
                        ("Jan-Oct 2026 (1-28 Oct + 29 Oct no-trade)", lambda d: d.startswith("2026")),
                        ("Oct 2026 (1-29)", lambda d: d.startswith("2026-10"))):
        print(label)
        for c in cols:
            ts = [per_day[d][c] for d in days if pred(d) and per_day[d][c]]
            print(f"  {c}: {len(ts)}t {sum(1 for t in ts if t['net_rs']>0)}g {sum(t['net_rs'] for t in ts):+.0f}")
    print("\nRECONCILIATION APPENDIX (not CSV columns):")
    for label, pred in (("Jan-Oct 2026", lambda d: d.startswith("2026")), ("2025", lambda d: d.startswith("2025"))):
        v4n = [extra[d]["v4_nifty"] for d in days if pred(d) and extra[d]["v4_nifty"]]
        lab = [extra[d]["la_bank"] for d in days if pred(d) and extra[d]["la_bank"]]
        bv = [per_day[d]["bank_v4"] for d in days if pred(d) and per_day[d]["bank_v4"]]
        lan = [per_day[d]["nifty_la"] for d in days if pred(d) and per_day[d]["nifty_la"]]
        print(f"{label}: V4 Nifty {len(v4n)} {sum(t['net_rs'] for t in v4n):+.0f} | V4 index (Bank+Nifty) {len(bv)+len(v4n)} {sum(t['net_rs'] for t in bv)+sum(t['net_rs'] for t in v4n):+.0f} | (lA) Bank mirror {len(lab)} {sum(t['net_rs'] for t in lab):+.0f} | (lA)-only (Nifty+Bank) {len(lab)+len(lan)} {sum(t['net_rs'] for t in lab)+sum(t['net_rs'] for t in lan):+.0f}")
    # ISO weeks count
    import datetime
    weeks = set()
    for d in days:
        y, m, dd = map(int, d.split("-"))
        iso = datetime.date(y, m, dd).isocalendar()
        weeks.add((iso[0], iso[1]))
    print(f"\nTrading days={len(days)} ISO weeks spanned={len(weeks)}")
    for c in cols:
        print(f"{c} trades/week = {grand[c][0]/len(weeks):.2f}")

if __name__ == "__main__":
    main()
