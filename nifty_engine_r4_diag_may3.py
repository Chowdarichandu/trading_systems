#!/usr/bin/env python3
"""ROUND 4 WS1 diagnosis, definitive pass — CLEAN adopted book, CAUSAL
features only (every feature computable at the entry bar's open).
Pass 1 was run on the retracted Cycle-40 book with the own-day 'pdret'
feature; May's 4 legs are identical in both books, but the book-wide
scan population differs, so the scan is redone here. Diagnosis only."""
import sys, json
from pathlib import Path
from datetime import date
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_r4_harness import (candidate_legs, score_r4, candles_exact,
                                     DAILY, DORDER, DIDX, PREV, pdret_prior,
                                     spot5m)
from nifty_engine_score import nsrc

legs = candidate_legs()
res, nc, _ = score_r4(legs)
by_key = {(r["date"], r["direction"]): r for r in res}
S5 = spot5m()

def features(l, r):
    d = l["date"]; i = DIDX[d]
    cs = candles_exact(l["index"], l["strike"], l["direction"], d, l["expiry"])
    bars = [b for b in cs if b[0] >= l["entry_time"]] if cs else []
    entry = bars[0][1] if bars else None
    mfe = max((b[2] - entry) for b in bars) if bars else None
    mae = min((b[3] - entry) for b in bars) if bars else None
    sb = S5.get(d, [])
    day_open = sb[0][1] if sb else DAILY[d]["o"]
    prev_close = DAILY[PREV[d]]["c"]
    pre = [b for b in sb if b[0] < l["entry_time"]]
    spot_at_entry = pre[-1][4] if pre else day_open
    p = PREV[d]
    rng = DAILY[p]["h"] - DAILY[p]["l"]
    rets = []
    for k in range(max(1, i - 3), i):
        rets.append(abs(DAILY[DORDER[k]]["c"] / DAILY[DORDER[k - 1]]["c"] - 1) * 100)
    y, m, dd = l["expiry"].split("-"); e = date(int(y), int(m), int(dd))
    y, m, dd = d.split("-"); t = date(int(y), int(m), int(dd))
    return dict(date=d, dir=l["direction"], rep=l["rep"], nsrc=nsrc(l),
                entry_time=l["entry_time"], strike=l["strike"], dte=(e - t).days,
                entry_prem=entry, net=r["net"], exit_reason=r["exit_reason"],
                exit_time=r["exit_time"], prem_mfe=round(mfe, 1), prem_mae=round(mae, 1),
                gap_pct=round((day_open / prev_close - 1) * 100, 3),
                pre_move_pct=round((spot_at_entry / day_open - 1) * 100, 3),
                pre_range_pct=round((max(b[2] for b in pre) - min(b[3] for b in pre)) / day_open * 100, 3) if pre else None,
                pdret_prior=round(pdret_prior(d), 3),
                pd_range=round(rng / DAILY[p]["c"] * 100, 3),
                bias_pos=round((DAILY[p]["c"] - DAILY[p]["l"]) / rng * 100, 1) if rng else None,
                vol3_prior=round(sum(rets) / len(rets), 3) if rets else None,
                weekday=t.strftime("%a"))

feats = [features(l, by_key[(l["date"], l["direction"])]) for l in legs]
may = [f for f in feats if f["date"].startswith("2026-05")]
losers = [f for f in may if f["net"] < 0]; winner = [f for f in may if f["net"] > 0][0]
print(f"MAY (clean book): {len(may)} legs, net {sum(f['net'] for f in may):+,.2f}")
for f in sorted(may, key=lambda x: x["date"]): print(json.dumps(f))

FEATS = ["gap_pct", "pre_move_pct", "pre_range_pct", "pdret_prior", "pd_range",
         "bias_pos", "vol3_prior", "entry_prem", "dte"]
print("\nSingle-feature bands (span of the 3 losers):")
for k in FEATS:
    lo = min(f[k] for f in losers); hi = max(f[k] for f in losers)
    inside = [f for f in feats if lo <= f[k] <= hi]
    print(f"  {k:14s} [{lo}, {hi}] -> {len(inside)} legs net {sum(f['net'] for f in inside):+,.2f} "
          f"winner_in={any(f['date'] == winner['date'] for f in inside)}")

print("\nConjunction scan: PE-only x single-feature band (losers are all PE):")
pe = [f for f in feats if f["dir"] == "PE"]
for k in FEATS:
    lo = min(f[k] for f in losers); hi = max(f[k] for f in losers)
    inside = [f for f in pe if lo <= f[k] <= hi]
    print(f"  PE & {k:14s} [{lo}, {hi}] -> {len(inside)} legs net {sum(f['net'] for f in inside):+,.2f} "
          f"winner_in={any(f['date'] == winner['date'] for f in inside)}")

print("\nThreshold scan: PE & entry_prem >= T, for T in the losers' premium range:")
for T in (280, 290, 294.65, 300, 304.25, 310, 320):
    inside = [f for f in pe if f["entry_prem"] >= T]
    print(f"  T={T}: {len(inside)} legs net {sum(f['net'] for f in inside):+,.2f} "
          f"legs={[(f['date'], f['entry_prem'], f['net']) for f in inside]}")
print("\nBook premium distribution (44 legs):")
ps = sorted(f["entry_prem"] for f in feats)
print("  min", ps[0], "p10", ps[4], "median", ps[22], "p90", ps[39], "max", ps[-1])
print("  top-5 premiums:", [(f["date"], f["dir"], f["entry_prem"], f["net"]) for f in
      sorted(feats, key=lambda x: -x["entry_prem"])[:5]])
print("  bottom-5 premiums:", [(f["date"], f["dir"], f["entry_prem"], f["net"]) for f in
      sorted(feats, key=lambda x: x["entry_prem"])[:5]])
Path("nifty_engine_r4_diag_may.json").write_text(json.dumps(feats, indent=1))
print("\nwrote nifty_engine_r4_diag_may.json (clean book, causal features)")
