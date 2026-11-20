#!/usr/bin/env python3
"""SECTOR-CAP RETEST — EKAM-Daily (EKAM-2c) on the capped enlarged
universe (frozen 25 + 12 capped additions) vs the official-close
frozen-25 control. Machinery imported verbatim from wide_daily_build
(prep_parquet / liquid_mask / sim2c_gated / stats_wide / nov_slice):
official-close parquet basis, Rs 1-crore / 60-session liquidity
screen on entries, both sides — PLUS the owner's Rs3,000 cap as a
second entry gate, applied to ALL names: a position may open only
if the entry price itself (next session's open, the E sim2c_gated
fills at) is <= Rs3,000. The gate is folded into the mask array
sim2c_gated already accepts; the sim is untouched.

Controls (identical to the additions test): the RAW 25-name parquet
run must reproduce the published official-close control
(+Rs63,621.50 / +Rs1,50,777.40); the SCREENED 25-name run is the
operative control for the verdict. The uncapped screened enlarged
run is scored beside the capped run to count blocked entries.
Research only. Basis: equity cash, per 100 shares PROVISIONAL,
Rs40/trade."""
import json, sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/trading")
import wide_daily_build as W

WS = "/home/hatch/workspace/trading"
CAP = 3000.0
FROZEN25 = ["ASTRAL", "BDL", "GLENMARK", "GODREJCP", "HDFCBANK",
            "HINDALCO", "HINDCOPPER", "HINDUNILVR", "HINDZINC",
            "INDUSTOWER", "IRCTC", "ITC", "KALYANKJIL", "NATIONALUM",
            "NHPC", "NTPC", "OBEROIRLTY", "OIL", "PFC", "RECLTD",
            "TATASTEEL", "TVSMOTOR", "UNITDSPR", "VEDL", "WIPRO"]
ADD_CAP = ["SBILIFE", "ICICIBANK", "SBIN", "RELIANCE", "INFY",
           "BHARTIARTL", "SUNPHARMA", "AMBUJACEM", "BHEL", "MAXHEALTH",
           "TMPV", "ASIANPAINT"]
PUBLISHED = {2025: 63621.50, 2026: 150777.40}


def capped_mask(d, liq):
    """Entry gate = liquidity AND entry price (next open) <= CAP."""
    g = np.zeros(d["n"], dtype=bool)
    o = d["o"]
    for i in range(d["n"] - 1):
        g[i] = bool(liq[i]) and float(o[i + 1]) <= CAP
    return g


def run_universe(syms, mode):
    trades, last_by_sym = [], {}
    for sym in syms:
        d = W.prep_parquet(sym)
        last_by_sym[sym] = d["dates"][-1]
        if mode == "raw":
            gate = np.ones(d["n"], dtype=bool)
        elif mode == "screened":
            gate = W.liquid_mask(d)
        elif mode == "capped":
            gate = capped_mask(d, W.liquid_mask(d))
        else:
            raise ValueError(mode)
        trades += W.sim2c_gated(d, gate)
    return trades, last_by_sym


def added_block(trades, year):
    sel = [t for t in W.year_sel(trades, year) if t["sym"] in ADD_CAP]
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


def blocked_from(unc_trades, year=None):
    if year is None:
        sel = [t for t in unc_trades
               if W.NOV_LO <= t["entry_date"] <= W.NOV_HI
               and t["entry"] > CAP]
    else:
        sel = [t for t in W.year_sel(unc_trades, year)
               if t["entry"] > CAP]
    by_name = {}
    for t in sel:
        by_name[t["sym"]] = by_name.get(t["sym"], 0) + 1
    return dict(entries_blocked=len(sel), by_name=by_name,
                net_of_blocked=round(sum(t["net"] for t in sel), 2))


def main():
    raw25, last25 = run_universe(FROZEN25, "raw")
    raw_pack = pack(raw25, last25)
    ok = all(raw_pack["years"][y]["stats"]["net"] == PUBLISHED[y]
             for y in (2025, 2026))
    print("RAW-25 vs published official-close control:",
          "PASS" if ok else "MISMATCH",
          {y: raw_pack["years"][y]["stats"]["net"] for y in (2025, 2026)},
          flush=True)
    if not ok:
        return 2
    scr25, _ = run_universe(FROZEN25, "screened")
    scr_pack = pack(scr25, last25)
    print("SCREENED-25 (operative control):",
          {y: scr_pack["years"][y]["stats"] for y in (2025, 2026)},
          flush=True)
    names = FROZEN25 + ADD_CAP
    unc, last_all = run_universe(names, "screened")
    unc_pack = pack(unc, last_all)
    print("ENLARGED-37 screened UNCAPPED:",
          {y: unc_pack["years"][y]["stats"] for y in (2025, 2026)},
          flush=True)
    capd, _ = run_universe(names, "capped")
    cap_pack = pack(capd, last_all)
    print("ENLARGED-37 CAPPED:",
          {y: cap_pack["years"][y]["stats"] for y in (2025, 2026)},
          flush=True)
    print("CAPPED added-names:",
          {y: cap_pack["years"][y]["added"] for y in (2025, 2026)},
          flush=True)
    blocked = {str(y): blocked_from(unc, y) for y in (2025, 2026)}
    blocked["november"] = blocked_from(unc, None)
    print("BLOCKED by cap:", blocked, flush=True)
    out = {"cap": CAP, "additions": ADD_CAP,
           "control25_raw_published_basis": raw_pack,
           "control25_screened": scr_pack,
           "enlarged37_screened_uncapped": unc_pack,
           "enlarged37_capped": cap_pack,
           "blocked": blocked,
           "control_check_raw25_vs_published": "PASS",
           "trades": [dict(book="EKAM-Daily", run="enlarged37_capped",
                           sym=t["sym"], entry_date=t["entry_date"],
                           exit_date=t["exit_date"], entry=t["entry"],
                           exit=t["exit"], net=t["net"],
                           added=t["sym"] in ADD_CAP)
                      for t in capd]}
    json.dump(out, open(f"{WS}/sector_cap_daily_results.json", "w"),
              indent=1, default=str)
    print("WROTE sector_cap_daily_results.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
