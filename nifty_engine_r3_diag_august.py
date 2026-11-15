#!/usr/bin/env python3
"""ROUND 3 WS1 diagnosis: path-by-path features of the ADOPTED book's legs
(emphasis: its 3 August legs) + the 15 difference legs. Features are all
known at entry except MFE/MAE and post-entry spot moves, which are
diagnostic only. Premium paths under adopted geometry (lock50/TGT2-175,
BE arm +50)."""
import sys, csv
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_r3_harness import score_r3, adopted_set, candles_exact
from nifty_engine_score import nsrc
from datetime import date

TR = Path.home() / "workspace/trading"

# ---- spot data ----
spot5 = defaultdict(list)
with open(TR / "data/full_hist/NIFTY/spot_5m.csv") as f:
    for r in csv.DictReader(f):
        d = r["timestamp"][:10]
        if d.startswith("2026"):
            spot5[d].append((r["timestamp"][11:16], float(r["open"]), float(r["high"]),
                             float(r["low"]), float(r["close"])))
daily = {}
prev_close = {}
rows = list(csv.DictReader(open(TR / "data/full_hist/NIFTY/spot_daily.csv")))
for i, r in enumerate(rows):
    daily[r["date"]] = float(r["close"])
    if i > 0: prev_close[r["date"]] = float(rows[i - 1]["close"])

def d(s):
    y, m, dd = s.split("-"); return date(int(y), int(m), int(dd))

def leg_features(l, res_by_key):
    cs = candles_exact(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
    r = res_by_key[(l["date"], l["direction"])]
    entry = r["entry"]
    idxs = [i for i, b in enumerate(cs) if b[0] >= l["entry_time"]]
    bars = cs[idxs[0]:]
    bars = [b for b in bars if b[0] <= "15:10"]
    mfe = max(b[2] for b in bars) - entry
    mae = entry - min(b[3] for b in bars)
    sp = spot5.get(l["date"], [])
    se = next((b for b in sp if b[0] == l["entry_time"]), None)
    sopen = sp[0][1] if sp else None
    s1510 = next((b for b in sp if b[0] == "15:10"), sp[-1] if sp else None)
    sign = 1.0 if l["direction"] == "CE" else -1.0
    pre = (se[4] / sopen - 1) * 100 * sign if se and sopen else None      # directional spot move before entry, %
    post = ((s1510[4] / se[4] - 1) * 100 * sign) if se and s1510 else None  # directional spot move entry->15:10, %
    if se and sp:
        after = [b for b in sp if b[0] >= l["entry_time"]]
        fav = (max(b[2] for b in after) / se[4] - 1) * 100 if sign > 0 else (se[4] / min(b[3] for b in after) - 1) * 100
    else:
        fav = None
    pd = (daily[l["date"]] / prev_close[l["date"]] - 1) * 100 if l["date"] in prev_close and l["date"] in daily else None
    return dict(date=l["date"], dir=l["direction"], strike=l["strike"], et=l["entry_time"],
                exp=l["expiry"], dte=(d(l["expiry"]) - d(l["date"])).days, nsrc=nsrc(l),
                rep=l["rep"], src=l["sources"], entry=entry, net=r["net"], reason=r["exit_reason"],
                exit_time=r["exit_time"], ft=r["ft"], mfe=round(mfe, 1), mae=round(mae, 1),
                pre_dir_pct=(round(pre, 3) if pre is not None else None),
                post_dir_pct=(round(post, 3) if post is not None else None),
                spot_fav_pct=(round(fav, 3) if fav is not None else None),
                prior_day_pct=(round(pd, 3) if pd is not None else None))

EXP0, CH3R, DIFF = adopted_set()
_, resA = None, None
res_list, nc, _ = score_r3(CH3R, lock=50.0, tgt2=175.0, arm=50.0)
resA = {(r["date"], r["direction"]): r for r in res_list}
resD_list, _, _ = score_r3(DIFF, lock=50.0, tgt2=175.0, arm=50.0)
resD = {(r["date"], r["direction"]): r for r in resD_list}

FA = [leg_features(l, resA) for l in CH3R]
FD = [leg_features(l, resD) for l in DIFF]

print("=== ADOPTED BOOK — AUGUST LEGS (the wound: month net -5,187.25) ===")
for f in FA:
    if f["date"][:7] == "2026-08":
        print(f)
print("\n=== ADOPTED BOOK — ALL LEGS ===")
for f in sorted(FA, key=lambda x: x["date"]):
    print(f"{f['date']} {f['dir']} et={f['et']} dte={f['dte']:>2} nsrc={f['nsrc']} entry={f['entry']:>7.2f} "
          f"net={f['net']:>+10.2f} {f['reason']:<16} mfe={f['mfe']:>6.1f} mae={f['mae']:>6.1f} "
          f"pre={f['pre_dir_pct']} post={f['post_dir_pct']} fav={f['spot_fav_pct']} pd={f['prior_day_pct']} src={f['src']}")
print("\n=== DIFFERENCE LEGS (incumbent-only, adopted geometry) ===")
for f in sorted(FD, key=lambda x: x["date"]):
    print(f"{f['date']} {f['dir']} et={f['et']} dte={f['dte']:>2} nsrc={f['nsrc']} entry={f['entry']:>7.2f} "
          f"net={f['net']:>+10.2f} {f['reason']:<16} mfe={f['mfe']:>6.1f} mae={f['mae']:>6.1f} "
          f"pre={f['pre_dir_pct']} post={f['post_dir_pct']} fav={f['spot_fav_pct']} pd={f['prior_day_pct']} src={f['src']}")
print(f"\ndiff legs total under adopted geometry: {round(sum(f['net'] for f in FD), 2):+,.2f} (expect -16,712.75 by union arithmetic)")

# candidate signature scans (entry-known features only), book-wide on adopted legs
def scan(name, pred):
    hit = [f for f in FA if pred(f)]
    rest = [f for f in FA if not pred(f)]
    print(f"SIG {name}: hits {len(hit)} net {round(sum(f['net'] for f in hit),2):+,.2f} | "
          f"dates {[f['date'] for f in hit]} | rest {len(rest)} net {round(sum(f['net'] for f in rest),2):+,.2f}")
print("\n=== SIGNATURE SCANS (adopted book) ===")
scan("PE & pre_dir<=-0.15% (spot already fell before entry)", lambda f: f["dir"] == "PE" and f["pre_dir_pct"] is not None and f["pre_dir_pct"] <= -0.15)
scan("PE & pre_dir>=+0.15% (spot rose before PE entry)", lambda f: f["dir"] == "PE" and f["pre_dir_pct"] is not None and f["pre_dir_pct"] >= 0.15)
scan("entry premium <= 120", lambda f: f["entry"] <= 120)
scan("entry premium >= 250", lambda f: f["entry"] >= 250)
scan("DTE >= 14", lambda f: f["dte"] >= 14)
scan("DTE <= 7", lambda f: f["dte"] <= 7)
scan("PE & DTE>=14", lambda f: f["dir"] == "PE" and f["dte"] >= 14)
scan("entry 09:30-09:55 & PE", lambda f: f["dir"] == "PE" and "09:30" <= f["et"] <= "09:55")
scan("(lA) in sources & PE", lambda f: f["dir"] == "PE" and "(lA) v2" in f["src"])
scan("prior_day_pct <= -0.5 (after a down day)", lambda f: f["prior_day_pct"] is not None and f["prior_day_pct"] <= -0.5)
scan("prior_day_pct >= +0.5 (after an up day)", lambda f: f["prior_day_pct"] is not None and f["prior_day_pct"] >= 0.5)
