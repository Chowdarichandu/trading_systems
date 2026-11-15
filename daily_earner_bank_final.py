#!/usr/bin/env python3
"""Daily Earner — Bank final: corrected Volrix November scan + final November CSV
(all rows, duplicates flagged). Jan-Oct numbers from daily_earner_bank_build*.py."""
import csv, json
from pathlib import Path
TR = Path.home() / "workspace/trading"
def fnum(x): return float(x) if x not in ("", None) else 0.0

closes = {r["date"]: float(r["close"]) for r in csv.DictReader(open(TR / "volrix_banknifty/banknifty_daily_2019_2026.csv"))}
for r in csv.DictReader(open(TR / "data/banknifty-2026-11/spot_daily.csv")):
    if r["date"] != "2026-11-08":  # phantom Sunday row in that file — not a trading day
        closes[r["date"]] = float(r["close"])
closes["2026-11-12"] = 61518.50  # progressive spot_5m 15:25 bar close, verified in-file
TD = ["2026-10-26", "2026-10-27", "2026-10-28", "2026-10-29", "2026-10-30",
      "2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05", "2026-11-06",
      "2026-11-09", "2026-11-11", "2026-11-12", "2026-11-13"]
scan, last = [], 0  # TD[0] = 2026-10-26, the last (b) entry
for i, d in enumerate(TD):
    if d < "2026-11-02": continue
    pc = (closes[TD[i - 1]] / closes[TD[i - 2]] - 1) * 100
    blocked = (i - last) <= 10
    fired = pc <= -1.0 and not blocked
    scan.append({"entry_day": d, "prev_day": TD[i - 1], "prev_change_pct": round(pc, 2),
                 "cooldown_blocked": blocked, "fired": fired})
    if fired: last = i
print(json.dumps(scan, indent=1))

# November CSV: every logged row from both books, duplicates flagged both ways
legacy_log = [r for r in csv.DictReader(open(TR / "november_paper_bank_log.csv"))
              if r["channel"] == "PRIMARY" and r["system_source"] != "none"]
skill_log = list(csv.DictReader(open(TR / "november_shadow_skill_bank_log.csv")))
legacy_dd = {(r["date"], r["direction"]) for r in legacy_log}
legacy_full = {(r["date"], r["direction"], r["strike"], r["entry_time"]) for r in legacy_log}
rows = []
for r in legacy_log:
    rows.append({"date": r["date"], "book": "LEGACY (BNF-PAPER-V1)", "direction": r["direction"],
                 "strike": r["strike"], "entry_time": r["entry_time"], "entry_premium": r["entry_premium"],
                 "exit_time": r["exit_time"], "exit_premium": r["exit_premium"],
                 "exit_reason": r["exit_reason"], "net_inr": fnum(r["net_inr"]),
                 "counted_in_preregistered_assembly": "YES", "counted_in_identical_leg_assembly": "YES",
                 "note": r["system_source"]})
for r in skill_log:
    same_dd = (r["date"], r["direction"]) in legacy_dd
    same_leg = (r["date"], r["direction"], r["strike"], r["entry_time"]) in legacy_full
    rows.append({"date": r["date"], "book": "SKILL (shadow)", "direction": r["direction"],
                 "strike": r["strike"], "entry_time": r["entry_time"], "entry_premium": r["entry_premium"],
                 "exit_time": r["exit_time"], "exit_premium": r["exit_premium"],
                 "exit_reason": r["exit_reason"], "net_inr": fnum(r["net_inr"]),
                 "counted_in_preregistered_assembly": "NO — same (date,direction) as a legacy leg" if same_dd else "YES",
                 "counted_in_identical_leg_assembly": "NO — identical leg already in legacy" if same_leg else "YES",
                 "note": "Skill V3 standalone"})
rows.sort(key=lambda x: (x["date"], x["entry_time"]))
with open(TR / "daily_earner_bank_november_trades.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print("november csv rows:", len(rows))
