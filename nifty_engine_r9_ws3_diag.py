#!/usr/bin/env python3
"""ROUND 9 Cycle 153 — WS3 causal-May diagnosis (DIAGNOSIS ONLY; no
candidate is scored here). Path-by-path on the standing book's May legs;
separator scan over the wound (negative legs in the two worst months,
May + Jun) under the Bank WS1 frozen separator test, feature list F1-F12
as frozen in the ROUND 9 freeze. Writes nifty_engine_r9_ws3_diag.json.
Nifty only, paper, real Rs0."""
import sys, json
from pathlib import Path
from datetime import date as ddate
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import nifty_engine_r7_harness as R7
import nifty_engine_r6_harness as R6
import nifty_engine_r9_harness as R9
from nifty_engine_r2_harness import candles_exact
from nifty_engine_r4_harness import spot5m, DAILY, PREV, pdret_prior

TR = Path.home() / "workspace/trading"

def gap_of(d):
    p = PREV.get(d)
    if not p: return None
    return DAILY[d]["o"] / DAILY[p]["c"] - 1.0

def spot_ctx(d, entry_time):
    bars = spot5m().get(d, [])
    if not bars: return None, None
    day_open = bars[0][1]
    eo = None
    for b in bars:
        if b[0] == entry_time: eo = b[1]; break
    return day_open, eo

def main():
    legs = R7.standing_legs()
    res, nc, _ = R6.score_r6(legs, geom=R9.STANDING_GEOM)
    assert nc == 0 and round(sum(r["net"] for r in res), 2) == 54102.00
    by_key = {(r["date"], r["direction"], r["entry_time"], int(r["strike"])): r for r in res}
    rows = []
    for l in legs:
        r = by_key[(l["date"], l["direction"], l["entry_time"], int(l["strike"]))]
        d = l["date"]
        # premium path: MFE over bars from entry bar to exit bar inclusive
        cs = candles_exact(l["index"], l["strike"], l["direction"], d, l["expiry"])
        seg = [b for b in cs if l["entry_time"] <= b[0] <= r["exit_time"]]
        mfe, mfe_t = None, None
        for b in seg:
            if mfe is None or b[2] - r["entry"] > mfe:
                mfe, mfe_t = b[2] - r["entry"], b[0]
        do, eo = spot_ctx(d, l["entry_time"])
        g = gap_of(d); pr = pdret_prior(d)
        dte = (ddate.fromisoformat(l["expiry"]) - ddate.fromisoformat(d)).days
        srcs = R6.sources_of(l)
        against = False
        if do is not None and eo is not None:
            if l["direction"] == "PE" and eo > do: against = True
            if l["direction"] == "CE" and eo < do: against = True
        rows.append(dict(
            date=d, direction=l["direction"], sources=l["sources"], nsrc=len(srcs),
            rep=l["rep"], entry_time=l["entry_time"], strike=int(l["strike"]),
            expiry=l["expiry"], dte=dte, entry_premium=r["entry"], net=r["net"],
            ft=int(r["ft"]), exit_reason=r["exit_reason"], exit_time=r["exit_time"],
            exit_px=r["exit"], mfe_pts=round(mfe, 2) if mfe is not None else None,
            mfe_time=mfe_t, gap=g, pdret_prior=pr, spot_open=do, spot_at_entry=eo,
            spot_against=against))
    # ---------- May path-by-path ----------
    may = [x for x in rows if x["date"].startswith("2026-05")]
    print(f"=== MAY LEGS ({len(may)}) — path by path ===")
    for x in may:
        print(f"{x['date']} {x['direction']} src={x['sources']} entry {x['entry_time']} "
              f"strike {x['strike']} exp {x['expiry']} DTE {x['dte']} prem {x['entry_premium']:.2f} | "
              f"net {x['net']:+,.2f} exit {x['exit_reason']} @ {x['exit_time']} px {x['exit_px']:.2f} | "
              f"MFE {x['mfe_pts']:+.2f} pts @ {x['mfe_time']} | gap {x['gap']*100:+.3f}% "
              f"pdret_prior {x['pdret_prior']*100:+.3f}% spot {x['spot_open']}->{x['spot_at_entry']} "
              f"against={x['spot_against']}")
    print(f"May total: {sum(x['net'] for x in may):+,.2f}")
    # ---------- wound + separator scan ----------
    wound = [x for x in rows if x["date"][:7] in ("2026-05", "2026-06") and x["net"] < 0]
    ft_legs = [x for x in rows if x["ft"] == 1]
    print(f"\n=== WOUND: {len(wound)} negative legs in May+Jun ===")
    for x in wound:
        print(f"  {x['date']} {x['direction']} net {x['net']:+,.2f} ({x['exit_reason']}) src={x['sources']} entry {x['entry_time']}")
    F = {
        "F1_dir_PE": lambda x: x["direction"] == "PE",
        "F2_dir_CE": lambda x: x["direction"] == "CE",
        "F3_confirmed": lambda x: x["nsrc"] >= 2,
        "F4_solo_lA": lambda x: x["nsrc"] == 1 and x["rep"] == "(lA) v2",
        "F5_entry<=0940": lambda x: x["entry_time"] <= "09:40",
        "F6_pdret_prior<0": lambda x: x["pdret_prior"] is not None and x["pdret_prior"] < 0,
        "F7_gap<0": lambda x: x["gap"] is not None and x["gap"] < 0,
        "F8_|gap|>=0.50%": lambda x: x["gap"] is not None and abs(x["gap"]) >= 0.005,
        "F9_DTE<=7": lambda x: x["dte"] <= 7,
        "F10_DTE>=21": lambda x: x["dte"] >= 21,
        "F11_prem>=300": lambda x: x["entry_premium"] >= 300,
        "F12_spot_against": lambda x: x["spot_against"],
    }
    print(f"\n=== SEPARATOR SCAN (Bank WS1 test): book {len(rows)} legs, wound {len(wound)}, FT legs {len(ft_legs)} ===")
    print(f"{'feature':18s} {'wound':>10s} {'book':>8s} {'ratio':>6s} {'half':>5s} {'FTshr':>6s}  separates")
    results = {}
    for name, f in F.items():
        w_in = sum(1 for x in wound if f(x)); b_in = sum(1 for x in rows if f(x))
        ft_in = sum(1 for x in ft_legs if f(x))
        wshr = w_in / len(wound) if wound else 0.0
        bshr = b_in / len(rows) if rows else 0.0
        ratio = (wshr / bshr) if bshr > 0 else float("inf")
        half = w_in >= (len(wound) + 1) // 2 if wound else False
        ftshr = ft_in / len(ft_legs) if ft_legs else 0.0
        sep = (ratio >= 2.0) and half and (ftshr < 0.60)
        results[name] = dict(wound_in=w_in, book_in=b_in, wound_share=round(wshr, 4),
                             book_share=round(bshr, 4), ratio=round(ratio, 3) if ratio != float("inf") else "inf",
                             holds_half=half, ft_share=round(ftshr, 4), separates=bool(sep))
        print(f"{name:18s} {w_in}/{len(wound)} ({wshr:4.0%}) {b_in:3d} ({bshr:4.0%}) {ratio:6.2f} {str(half):>5s} {ftshr:6.0%}  {sep}")
    seps = [k for k, v in results.items() if v["separates"]]
    print("\nSEPARATING FEATURES:", seps if seps else "NONE — no conditional candidate (freeze rule)")
    out = dict(may_legs=may, wound=[{k: x[k] for k in ("date", "direction", "net", "exit_reason", "sources", "entry_time")} for x in wound],
               features=results, separating=seps,
               book_n=len(rows), wound_n=len(wound), ft_n=len(ft_legs))
    (TR / "nifty_engine_r9_ws3_diag.json").write_text(json.dumps(out, indent=1, default=str))
    print("wrote nifty_engine_r9_ws3_diag.json")

if __name__ == "__main__":
    main()
