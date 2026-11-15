#!/usr/bin/env python3
"""ROUND 4 DIAGNOSIS (no candidate scoring): NS3 admitted-leg distributions,
near-miss conversion audit on the flagged stack, entry-state feature splits.
Outputs bank_r4_diag.json + prints the tables the frozen appendix cites."""
import json, sys, statistics
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import candles
from bank_r4_core import build_stack, V17_ROWS, enrich
from bank_r3_core import admit, state_at
from bank_r3_ws1 import build as build_ws1
from bank_r3_setups import SPOT, DAILY, DAYS

TR = Path.home() / "workspace/trading"
out = {}

# ---------- flagged stack rows + MFE ----------
rows, nc, lbk, detail = build_stack(delay=0)
assert len(rows) == 108 and nc == 0
def mfe_of(row):
    leg = lbk[row["leg_key"]]
    cs = candles(leg["index"], leg["strike"], leg["direction"], leg["date"], leg["expiry"])
    if not cs: return None
    times = [b[0] for b in cs]
    if row["entry_time"] not in times or row["exit_time"] not in times: return None
    i0, i1 = times.index(row["entry_time"]), times.index(row["exit_time"])
    return round(max(b[2] for b in cs[i0:i1 + 1]) - row["entry"], 2)

for r in rows:
    r["_mfe"] = mfe_of(r)
    leg = lbk[r["leg_key"]]
    r["_dte"] = (leg["expiry"] - leg["date"]) if False else None
import datetime as _dt
for r in rows:
    leg = lbk[r["leg_key"]]
    r["_dte"] = (_dt.date.fromisoformat(leg["expiry"]) - _dt.date.fromisoformat(r["date"])).days
    r["_fam"] = ("BASE" if r["leg_key"] in {(x["date"], x["direction"], x["entry_time"]) for x in V17_ROWS}
                 else r["family"])
out["stack_detail"] = detail

# ---------- WS4: near-miss audit ----------
conv = [r for r in rows if r.get("ft90")]
near = [r for r in rows if not r.get("ft90") and r["_mfe"] is not None and 75.0 <= r["_mfe"] < 90.0]
out["ft90_legs"] = len(conv)
out["near_miss"] = [dict(date=r["date"], direction=r["direction"], family=r["_fam"],
                          entry_time=r["entry_time"], entry=r["entry"], mfe=r["_mfe"],
                          net=r["net"], exit_reason=r["exit_reason"], dte=r["_dte"])
                     for r in near]
print(f"stack: n=108 ft90={len(conv)} near-miss(MFE in [75,90), ft90=0)={len(near)}")
for nm in out["near_miss"]:
    print("  NM", nm["date"], nm["direction"], nm["family"], nm["entry_time"],
          "entry", nm["entry"], "MFE", nm["mfe"], "net", nm["net"], nm["exit_reason"], "DTE", nm["dte"])

def enrichment(name, pred):
    cp = sum(1 for r in conv if pred(r)); np_ = sum(1 for r in near if pred(r))
    cn = len(conv) - cp; nn = len(near) - np_
    rate_p = np_ / (np_ + cp) if (np_ + cp) else None
    rate_n = nn / (nn + cn) if (nn + cn) else None
    print(f"  feat {name}: pos n={np_+cp} (NM {np_}, conv {cp}) neg n={nn+cn} (NM {nn}, conv {cn})")
    return dict(feature=name, pos_nm=np_, pos_conv=cp, neg_nm=nn, neg_conv=cn)

print("enrichment (feature+ share of near-misses vs converted):")
feats = {
    "family==NS3": lambda r: r["_fam"] == "NS3_gapclass",
    "family==BASE": lambda r: r["_fam"] == "BASE",
    "entry<400": lambda r: r["entry"] < 400.0,
    "entry>=550": lambda r: r["entry"] >= 550.0,
    "entry_time<11:00": lambda r: r["entry_time"] < "11:00",
    "entry_time>=13:00": lambda r: r["entry_time"] >= "13:00",
    "DTE==0": lambda r: r["_dte"] == 0,
    "DTE>=14": lambda r: r["_dte"] >= 14,
    "CE": lambda r: r["direction"] == "CE",
    "PE": lambda r: r["direction"] == "PE",
    "exit==stop": lambda r: r["exit_reason"] == "stop",
    "month>=Jun": lambda r: r["date"] >= "2026-06-01",
}
out["enrichment"] = [enrichment(k, v) for k, v in feats.items()]

# ---------- WS1/WS2: NS3 admitted-leg distributions ----------
ns3 = build_ws1("index_options_newsetup_ns3_trades_jan_oct_2026.csv", "NS3_gapclass", "NS3")
enr = [enrich(l) for l in ns3]
adm, kd, bd, ncl = admit(enr, {(r["date"], r["direction"]) for r in V17_ROWS})
print(f"\nNS3 candidates={len(enr)} admitted_vs_v17={len(adm)} key_drop={len(kd)} band_drop={len(bd)} NC={len(ncl)}")
ns3_rows = {r["leg_key"]: r for r in rows if r["_fam"] == "NS3_gapclass"}
dist = []
for l in adm:
    r = ns3_rows.get((l["date"], l["direction"], l["entry_time"]))
    dist.append(dict(date=l["date"], direction=l["direction"], entry_time=l["entry_time"],
                     premium=l["_ep"], dte=l["_dte"], subleg=l["_subleg"],
                     net=(r["net"] if r else None), ft90=(r.get("ft90") if r else None),
                     exit_reason=(r["exit_reason"] if r else None)))
out["ns3_admitted"] = dist
for d in dist: print("  NS3", d)
def split(name, pred):
    a = [d for d in dist if pred(d)]; b = [d for d in dist if not pred(d)]
    fa = lambda s: (len(s), round(sum(x["net"] for x in s), 2), sum(x["ft90"] for x in s))
    print(f"  split {name}: pos {fa(a)} neg {fa(b)}")
print("NS3 axis splits (n, net, ft90 legs):")
split("premium<400", lambda d: d["premium"] < 400.0)
split("premium>=550", lambda d: d["premium"] >= 550.0)
split("DTE==0", lambda d: d["dte"] == 0)
split("DTE<=7", lambda d: d["dte"] <= 7)
split("subleg GD", lambda d: d["subleg"] == "NS3-GD")
split("subleg GU", lambda d: d["subleg"] == "NS3-GU")
split("subleg FLAT", lambda d: d["subleg"] == "NS3-FLAT")
split("CE", lambda d: d["direction"] == "CE")
split("entry<11:00", lambda d: d["entry_time"] < "11:00")

# ---------- WS5: entry-state features ----------
first30, gaps = {}, {}
prev_close = None
for d in DAYS:
    bars = SPOT[SPOT["date"] == d]
    if bars.empty: continue
    b30 = bars[bars["time"] < "09:45"]
    first30[d] = float(b30["high"].max() - b30["low"].min())
    day_open = float(bars.iloc[0]["open"])
    pc = float(DAILY[d]["close"]) if d in DAILY else None
    if prev_close is not None:
        gaps[d] = round((day_open - prev_close) / prev_close * 100.0, 3)
    if pc is not None: prev_close = pc
med30 = {}
for i, d in enumerate(DAYS):
    prior = [first30[x] for x in DAYS[max(0, i - 20):i] if x in first30]
    if len(prior) >= 10: med30[d] = statistics.median(prior)
gvals = sorted(gaps.values())
q1, q2 = gvals[len(gvals) // 3], gvals[2 * len(gvals) // 3]
out["ws5_feature_meta"] = dict(gap_tercile_cuts=[q1, q2], n_days=len(DAYS))
print(f"\nWS5 features: gap tercile cuts {q1:.3f}% / {q2:.3f}% over {len(gaps)} days")
def terc(d):
    g = gaps.get(d)
    return None if g is None else ("T1_low" if g <= q1 else ("T3_high" if g > q2 else "T2_mid"))
def split_rows(name, pred, rows_):
    a = [r for r in rows_ if pred(r)]; b = [r for r in rows_ if not pred(r)]
    fa = lambda s: (len(s), round(sum(x["net"] for x in s), 2), sum(x.get("ft90", 0) for x in s))
    print(f"  {name}: pos {fa(a)} neg {fa(b)}")
late = [r for r in rows if r["entry_time"] >= "09:45"]
print("WS5 splits on the flagged stack (n, net, ft90):")
split_rows("range30>trailMed (legs>=09:45 only)", lambda r: r["date"] in med30 and first30[r["date"]] > med30[r["date"]], late)
for t in ("T1_low", "T2_mid", "T3_high"):
    split_rows(f"gap tercile=={t}", lambda r, t=t: terc(r["date"]) == t, rows)
out["ws5_first30"] = first30; out["ws5_med30"] = med30; out["ws5_gaps"] = gaps

(TR / "bank_r4_diag.json").write_text(json.dumps(out, indent=1, default=str))
print("\ndiag -> bank_r4_diag.json")
