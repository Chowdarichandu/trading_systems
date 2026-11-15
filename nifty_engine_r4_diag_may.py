#!/usr/bin/env python3
"""ROUND 4 WS1 diagnosis — the candidate book's May (-2,323.00), path by
path, same discipline as the Round-3 August diagnosis. Diagnosis only:
no candidate is scored here."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_r4_harness import (candidate_legs, score_r4, candles_exact,
                                     DAILY, DORDER, DIDX, PREV, pdret, spot5m)
from nifty_engine_score import nsrc

legs = candidate_legs()
res, nc, _ = score_r4(legs)
by_key = {(r["date"], r["direction"]): r for r in res}
S5 = spot5m()

def leg_features(l, r):
    d = l["date"]; i = DIDX[d]
    cs = candles_exact(l["index"], l["strike"], l["direction"], d, l["expiry"])
    bars = [b for b in cs if b[0] >= l["entry_time"]] if cs else []
    entry = bars[0][1] if bars else None
    mfe = max((b[2] - entry) for b in bars) if bars else None
    mae = min((b[3] - entry) for b in bars) if bars else None
    sb = S5.get(d, [])
    et = l["entry_time"]
    pre = [b for b in sb if b[0] < et]
    post = [b for b in sb if b[0] >= et]
    spot0 = pre[-1][4] if pre else (sb[0][1] if sb else None)
    sgn = 1 if l["direction"] == "CE" else -1
    spot_mfe = max(sgn * (b[2] if sgn > 0 else b[3]) - sgn * spot0 for b in post) if post else None
    spot_mfe_pct = (max((b[2] for b in post)) - spot0) / spot0 * 100 if (post and sgn > 0) else \
                   (spot0 - min((b[3] for b in post))) / spot0 * 100 if post else None
    morn = [b for b in sb if b[0] < "09:45"]
    morn_rng = (max(b[2] for b in morn) - min(b[3] for b in morn)) / DAILY[d]["c"] * 100 if morn else None
    p = PREV[d]
    pd_range = (DAILY[p]["h"] - DAILY[p]["l"]) / DAILY[p]["c"] * 100
    rets = []
    for k in range(max(1, i - 3), i):
        rets.append(abs(DAILY[DORDER[k]]["c"] / DAILY[DORDER[k - 1]]["c"] - 1) * 100)
    vol3 = sum(rets) / len(rets) if rets else None
    from datetime import date
    y, m, dd = l["expiry"].split("-"); e = date(int(y), int(m), int(dd))
    y, m, dd = d.split("-"); t = date(int(y), int(m), int(dd))
    return dict(date=d, dir=l["direction"], rep=l["rep"], nsrc=nsrc(l),
                entry_time=et, strike=l["strike"], expiry=l["expiry"], dte=(e - t).days,
                entry_prem=entry, net=r["net"], exit_reason=r["exit_reason"],
                exit_time=r["exit_time"], ft=r["ft"], prem_mfe=round(mfe, 1) if mfe is not None else None,
                prem_mae=round(mae, 1) if mae is not None else None,
                spot_mfe_pct=round(spot_mfe_pct, 3) if spot_mfe_pct is not None else None,
                pdret=round(pdret(d), 3), pd_range=round(pd_range, 3),
                morn_rng=round(morn_rng, 3) if morn_rng else None,
                vol3=round(vol3, 3) if vol3 else None,
                weekday=t.strftime("%a"))

feats = []
for l in legs:
    r = by_key[(l["date"], l["direction"])]
    feats.append(leg_features(l, r))

may = [f for f in feats if f["date"].startswith("2026-05")]
print(f"MAY legs in candidate book: {len(may)}  net {sum(f['net'] for f in may):+,.2f}")
for f in sorted(may, key=lambda x: x["date"]):
    print(json.dumps(f))
print("\nAll other months' leg counts/nets:")
from collections import defaultdict
bym = defaultdict(float); cnt = defaultdict(int)
for f in feats:
    bym[f["date"][:7]] += f["net"]; cnt[f["date"][:7]] += 1
for m in sorted(bym): print(m, cnt[m], f"{bym[m]:+,.2f}")
Path("nifty_engine_r4_diag_may.json").write_text(json.dumps(feats, indent=1))
print("\nwrote nifty_engine_r4_diag_may.json (all 44 legs)")
