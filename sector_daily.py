#!/usr/bin/env python3
"""SECTOR-ADDITIONS TEST — EKAM-Daily (EKAM-2c) on the enlarged 37-name
universe vs the official-close frozen-25 control. Machinery imported
verbatim from wide_daily_build (prep_parquet / liquid_mask /
sim2c_gated / stats_wide / nov_slice): official-close parquet basis,
Rs 1-crore / 60-session liquidity screen on entries, both sides.
Control check: the RAW 25-name parquet run must reproduce the published
official-close control (+Rs63,621.50 / +Rs1,50,777.40); the SCREENED
25-name run is reported beside it and is the operative control for the
verdict (same screen both sides). Research only.
Basis: equity cash, per 100 shares PROVISIONAL, Rs40/trade."""
import json, sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/trading")
import wide_daily_build as W

WS = W.WS if hasattr(W, "WS") else "/home/hatch/workspace/trading"
FROZEN25 = ["ASTRAL", "BDL", "GLENMARK", "GODREJCP", "HDFCBANK",
            "HINDALCO", "HINDCOPPER", "HINDUNILVR", "HINDZINC",
            "INDUSTOWER", "IRCTC", "ITC", "KALYANKJIL", "NATIONALUM",
            "NHPC", "NTPC", "OBEROIRLTY", "OIL", "PFC", "RECLTD",
            "TATASTEEL", "TVSMOTOR", "UNITDSPR", "VEDL", "WIPRO"]
ADD12 = ["ULTRACEMCO", "LT", "SBILIFE", "APOLLOHOSP", "ICICIBANK", "SBIN",
         "RELIANCE", "INFY", "M&M", "BHARTIARTL", "SUNPHARMA", "TITAN"]
PUBLISHED = {2025: 63621.50, 2026: 150777.40}


def run_universe(syms, screened):
    trades, last_by_sym = [], {}
    for sym in syms:
        d = W.prep_parquet(sym)
        last_by_sym[sym] = d["dates"][-1]
        if screened:
            liq = W.liquid_mask(d)
        else:
            liq = np.ones(d["n"], dtype=bool)
        trades += W.sim2c_gated(d, liq)
    return trades, last_by_sym


def added_block(trades, year):
    sel = [t for t in W.year_sel(trades, year) if t["sym"] in ADD12]
    by_name = {}
    for t in sel:
        by_name[t["sym"]] = round(by_name.get(t["sym"], 0.0) + t["net"], 2)
    return dict(trades=len(sel), net=round(sum(t["net"] for t in sel), 2),
                wr=(round(100.0 * sum(1 for t in sel if t["net"] > 0)
                          / len(sel), 2) if sel else None),
                names_traded=len(by_name), by_name=by_name)


def pack(trades, last_by_sym):
    out = {"years": {}}
    for y in (2025, 2026):
        s = W.stats_wide(trades, y)
        out["years"][y] = dict(
            stats=dict(trades=s["trades"], net=s["total"], wr=s["wr"],
                       ex_top3=s["ex_top3"], max_drawdown=s["max_dd"],
                       distinct_names=s["distinct_names"]),
            added=added_block(trades, y))
    out["november"] = W.nov_slice(trades, last_by_sym)
    return out


def main():
    raw25, last25 = run_universe(FROZEN25, screened=False)
    raw_pack = pack(raw25, last25)
    ok = all(raw_pack["years"][y]["stats"]["net"] == PUBLISHED[y]
             for y in (2025, 2026))
    print("RAW-25 vs published official-close control:",
          "PASS" if ok else "MISMATCH",
          {y: raw_pack["years"][y]["stats"]["net"] for y in (2025, 2026)},
          flush=True)
    scr25, _ = run_universe(FROZEN25, screened=True)
    scr_pack = pack(scr25, last25)
    print("SCREENED-25:", {y: scr_pack["years"][y]["stats"]
                           for y in (2025, 2026)}, flush=True)
    enl, last37 = run_universe(FROZEN25 + ADD12, screened=True)
    enl_pack = pack(enl, last37)
    print("ENLARGED-37 screened:", {y: enl_pack["years"][y]["stats"]
                                    for y in (2025, 2026)}, flush=True)
    print("ENLARGED added-names:", {y: enl_pack["years"][y]["added"]
                                    for y in (2025, 2026)}, flush=True)
    out = {"control25_raw_published_basis": raw_pack,
           "control25_screened": scr_pack,
           "enlarged37_screened": enl_pack,
           "control_check_raw25_vs_published": "PASS" if ok else "MISMATCH",
           "trades": [dict(book="EKAM-Daily", run="enlarged37",
                           sym=t["sym"], entry_date=t["entry_date"],
                           exit_date=t["exit_date"], entry=t["entry"],
                           exit=t["exit"], net=t["net"],
                           added=t["sym"] in ADD12)
                      for t in enl]}
    json.dump(out, open(f"{WS}/sector_daily_results.json", "w"), indent=1,
              default=str)
    print("WROTE sector_daily_results.json", flush=True)
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
