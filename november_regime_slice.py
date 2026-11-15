#!/usr/bin/env python3
"""NOVEMBER REGIME FIX — Phase C: regime classification + book slices.

Regime definition FROZEN from november_failure_audit_2026-11-13.md's
own measurements (H2), computed with the audit's exact formulas:
  gap_pct(d)   = (first-bar open - prior session close) / prior close * 100
                 (prior close = previous stored session's last close)
  morning      = close of last bar with time <= 11:00  minus  first-bar open
  reversal(d)  = post-11:00 extreme moves >= 0.7% of the 11:00 close
                 AGAINST the morning direction
REGIME-LIKE(d) = |gap_pct(d)| in the top quartile of the index's own
                 Jan-Oct |gap| distribution  OR  reversal(d).
Arithmetic on stored legs only. No API calls. No book is modified.
"""
import csv, json
from pathlib import Path
import pandas as pd
import numpy as np

TR = Path.home() / "workspace/trading"

# ---------------- classification ----------------
def load_spot(sym, extra=None):
    s = pd.read_csv(TR / f"data/progressive/{sym}/spot_5m.csv")
    s["timestamp"] = pd.to_datetime(s["timestamp"]).dt.tz_localize(None)
    s = s[(s["timestamp"] >= "2026-01-01") & (s["timestamp"] <= "2026-10-31")]
    if extra:
        e = pd.read_csv(extra)
        e["timestamp"] = pd.to_datetime(e["timestamp"]).dt.tz_localize(None)
        s = pd.concat([s, e])
    s["date"] = s["timestamp"].dt.normalize()
    s["time"] = s["timestamp"].dt.strftime("%H:%M")
    return s.sort_values("timestamp")

def classify(spot):
    dmap = {d: g for d, g in spot.groupby("date") if len(g) >= 70}
    rows = []
    prev_close = None
    for d in sorted(dmap):
        g = dmap[d]
        o = g.iloc[0]["open"]; c = g.iloc[-1]["close"]
        pclose = prev_close; prev_close = c
        g11 = g[g["time"] <= "11:00"]
        c11 = g11.iloc[-1]["close"] if len(g11) else np.nan
        morn = c11 - o if not np.isnan(c11) else np.nan
        after = g[g["time"] > "11:00"]
        rev = False
        if len(after) and not np.isnan(c11) and morn != 0:
            if morn > 0:
                rev = (c11 - after["low"].min()) / c11 * 100 >= 0.7
            else:
                rev = (after["high"].max() - c11) / c11 * 100 >= 0.7
        rows.append(dict(date=str(d)[:10],
                         gap_pct=(o - pclose) / pclose * 100 if pclose else np.nan,
                         morning_pct=(morn / o * 100) if not np.isnan(morn) else np.nan,
                         reversal=bool(rev)))
    return pd.DataFrame(rows)

def regime_frame(sym, extra=None):
    df = classify(load_spot(sym, extra))
    jo = df[df.date <= "2026-10-31"].copy()
    q3 = float(jo["gap_pct"].abs().quantile(0.75))
    df["gap_topq"] = df["gap_pct"].abs() >= q3
    df["regime_like"] = df["gap_topq"] | df["reversal"]
    df["reason"] = np.where(df["gap_topq"] & df["reversal"], "both",
                    np.where(df["gap_topq"], "gap",
                    np.where(df["reversal"], "reversal", "")))
    jo = df[df.date <= "2026-10-31"].copy()
    stats = dict(index=sym, sessions=len(jo),
                 median_abs_gap=round(float(jo["gap_pct"].abs().median()), 3),
                 q3_abs_gap=round(q3, 3),
                 reversal_share_pct=round(float(jo["reversal"].mean() * 100), 1),
                 regime_days=int(jo["regime_like"].sum()),
                 gap_only=int(((jo.reason) == "gap").sum()),
                 reversal_only=int(((jo.reason) == "reversal").sum()),
                 both=int(((jo.reason) == "both").sum()),
                 non_regime_days=int((~jo["regime_like"]).sum()))
    return df, stats

bank, bank_stats = regime_frame("BANKNIFTY", TR / "data/banknifty-2026-11/spot_5m.csv")
nifty, nifty_stats = regime_frame("NIFTY")
print("BANK:", bank_stats)
print("NIFTY:", nifty_stats)

# November Bank days classified on the Jan-Oct threshold (descriptive)
bank_all = bank.copy()
nov = bank_all[bank_all.date >= "2026-11-01"]
print("BANK NOVEMBER regime-like days:", int(nov["regime_like"].sum()),
      "of", len(nov), "->", list(nov[nov.regime_like].date))

bank_jo = bank[bank.date <= "2026-10-31"]
nifty_jo = nifty[nifty.date <= "2026-10-31"]
bank_regime = set(bank_jo[bank_jo.regime_like].date)
bank_nonreg = set(bank_jo[~bank_jo.regime_like].date)
bank_classified = set(bank_jo.date)
nifty_regime = set(nifty_jo[nifty_jo.regime_like].date)
nifty_nonreg = set(nifty_jo[~nifty_jo.regime_like].date)
nifty_classified = set(nifty_jo.date)

bank[["date", "gap_pct", "morning_pct", "reversal", "gap_topq",
      "regime_like", "reason"]].to_csv(
    TR / "november_regime_days_bank.csv", index=False)
nifty[["date", "gap_pct", "morning_pct", "reversal", "gap_topq",
       "regime_like", "reason"]].to_csv(
    TR / "november_regime_days_nifty.csv", index=False)

# ---------------- book leg loading ----------------
def rd(fn):
    with open(TR / fn) as f:
        return list(csv.DictReader(f))

stack_rows = rd("solid60_programme_2026-11-13_bank_A_stack_features.csv")
stack_legs = [(r["date"], float(r["x1_net"])) for r in stack_rows]
stack_days = {d for d, _ in stack_legs}
assert len(stack_legs) == 111 and abs(sum(n for _, n in stack_legs) - 127351.50) < 0.01

legacy_rows = rd("bank_engine_r6_v21_trades.csv")
legacy_legs = [(r["date"], float(r["net_inr"])) for r in legacy_rows]
print("legacy anchor:", len(legacy_legs), round(sum(n for _, n in legacy_legs), 2),
      "(expect 99 / 83650.50)")

def increment(fn, keycol, keyval):
    out = []
    for r in rd(fn):
        if (r[keycol] == keyval and r["mode"] == "real"
                and r["trade_date"] not in stack_days
                and r["trade_date"] <= "2026-10-31"):
            out.append((r["trade_date"], float(r["net"])))
    return out

v3_inc = increment("oi_buildup_trades.csv", "variant", "V3")
b1_inc = increment("round2_trades.csv", "variant", "B1")
d1_inc = increment("round4_trades.csv", "family", "D1")
print("V3 increment:", len(v3_inc), round(sum(n for _, n in v3_inc), 2), "(expect 42 / 3360)")
print("B1 increment:", len(b1_inc), round(sum(n for _, n in b1_inc), 2), "(expect 12 / 4560)")
print("D1 increment:", len(d1_inc), round(sum(n for _, n in d1_inc), 2), "(expect 27 / 8973)")

books_bank = [("TUNED STACK v2", stack_legs), ("LEGACY v21 frame", legacy_legs),
              ("OI-V3 increment", v3_inc), ("VIX-B1 increment", b1_inc),
              ("R4-D1 increment", d1_inc)]

# IOI / round-5 families: added when their Phase B trade files exist
import os
if os.path.exists(TR / "round5_ioi_trades.csv"):
    for fam in ("IOI-1", "IOI-2"):
        legs = [(r["date"], float(r["net"])) for r in rd("round5_ioi_trades.csv")
                if r.get("family") == fam and r.get("mode") == "real"
                and r.get("window") == "JANOCT"]
        books_bank.append((fam, legs))
        print(fam, "legs:", len(legs), round(sum(n for _, n in legs), 2))
for fn, name in (("round5_trades_flow_vol.csv", "FLOW-VOL"),
                 ("round5_trades_opt_flow.csv", "OPT-FLOW")):
    if os.path.exists(TR / fn):
        rows = rd(fn)
        legs = [(r["date"], float(r["net_inr"])) for r in rows
                if r["date"] <= "2026-10-31"]
        books_bank.append((name, legs))
        print(name, "legs:", len(legs), round(sum(n for _, n in legs), 2))

# Nifty books from the frozen nifty_900 results (stored legs)
nj = json.load(open(TR / "nifty_900_tradeday_2026-11-13_results.json"))
books_nifty = []
for name, key in (("TUNED v1", "TUNED_v1"), ("DEC-S1 (control)", "DEC-S1")):
    det = nj["books"][key]["legs_detail"]
    legs = [(r["date"], float(r["net"])) for r in det]
    books_nifty.append((name, legs))
    print("NIFTY", name, "legs:", len(legs), round(sum(n for _, n in legs), 2))

# ---------------- slicing ----------------
def day_signs(legs, inset):
    byd = {}
    for d, n in legs:
        if d in inset:
            byd[d] = byd.get(d, 0.0) + n
    return (sum(1 for v in byd.values() if v > 0),
            sum(1 for v in byd.values() if v < 0),
            sum(1 for v in byd.values() if v == 0), len(byd))

def slice_book(legs, regime, nonreg, classified):
    out = {}
    for lab, inset in (("regime", regime), ("non_regime", nonreg)):
        sub = [(d, n) for d, n in legs if d in inset]
        g, r, z, td = day_signs(legs, inset)
        out[lab] = dict(legs=len(sub), total=round(sum(n for _, n in sub), 2),
                        trade_days=td, green_days=g, red_days=r, zero_days=z)
    unc = [(d, n) for d, n in legs if d not in classified]
    out["unclassified"] = dict(legs=len(unc), total=round(sum(n for _, n in unc), 2),
                               days=sorted({d for d, _ in unc}))
    out["all"] = dict(legs=len(legs), total=round(sum(n for _, n in legs), 2))
    return out

results = {"regime_stats": {"BANKNIFTY": bank_stats, "NIFTY": nifty_stats},
           "november_bank_regime_days": list(nov[nov.regime_like].date),
           "books": {}}
for name, legs in books_bank:
    results["books"][f"BANK {name}"] = slice_book(legs, bank_regime, bank_nonreg, bank_classified)
for name, legs in books_nifty:
    results["books"][f"NIFTY {name}"] = slice_book(legs, nifty_regime, nifty_nonreg, nifty_classified)

with open(TR / "november_regime_slice_results.json", "w") as f:
    json.dump(results, f, indent=1)
with open(TR / "november_regime_slice_books.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["book", "slice", "legs", "total", "trade_days", "green_days", "red_days", "zero_days"])
    for bname, s in results["books"].items():
        for lab in ("regime", "non_regime"):
            v = s[lab]
            w.writerow([bname, lab, v["legs"], v["total"], v["trade_days"],
                        v["green_days"], v["red_days"], v["zero_days"]])
        w.writerow([bname, "unclassified", s["unclassified"]["legs"],
                    s["unclassified"]["total"], "", "", "", ""])
        w.writerow([bname, "ALL", s["all"]["legs"], s["all"]["total"], "", "", "", ""])
print(json.dumps(results["books"], indent=1))
print("SLICE DONE")
