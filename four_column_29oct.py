"""29 Oct 2026 four-column computation from Upstox intraday 5-min data.
Paper only, no orders. Frozen definitions, same as the cache runs:
- V4/Skill: progressive_capped_v2.candidates_for_month logic, single day.
- (lA): merged_skill_la_october day_la_nifty / day_la_bank, same as merged jan_oct.
Prior-day (28 Oct 2026) PD levels come from the progressive cache daily files.
Intraday raw JSONs saved at /tmp/bn_29oct.json and /tmp/nf_29oct.json (fetched
29 Oct 2026 after close via the Upstox helper intraday subcommand).
Also recomputes the October (1-28) capped slices and the October (1-29)
re-cap, so any cap displacement in ISO week W44 is visible, not hidden.
"""
import os, sys, json, math
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
import pandas as pd
from progressive_capped import load as load_sym, room_ratio, skill_or_outcome, SETUP_RANK
from progressive_capped_v2 import candidates_for_month as v2_candidates, cap_select_v2
from daytrader_cash_backtest import find_signal, run_day, bias_of
from daytrader_skill_run import find_skill_signal
from timing_sweep import day_data as day_data_nifty
from reentry_filter_sweep import day_data_bn
from merged_skill_la_october import (cap_select as la_cap_select, metrics,
                                     day_la_nifty, day_la_bank, day_data_bank)

QTY, COST = 100, 40.0
DS = "2026-10-29"

def intraday_df(path):
    d = json.load(open(path))
    cs = sorted(d["data"]["candles"], key=lambda x: x[0])
    rows = []
    for ts, o, h, l, c, *_ in cs:
        t = pd.Timestamp(ts).tz_localize(None)
        rows.append({"timestamp": t, "open": float(o), "high": float(h), "low": float(l), "close": float(c)})
    df = pd.DataFrame(rows).sort_values("timestamp")
    df["date"] = df["timestamp"].dt.normalize()
    df["time"] = df["timestamp"].dt.strftime("%H:%M")
    return df

def day_tuple(df, daily_prev):
    pdh, pdc, pdl = float(daily_prev["high"]), float(daily_prev["close"]), float(daily_prev["low"])
    rng = pdh - pdl
    cs = (pdc - pdl) / rng * 100 if rng else 50.0
    bias = "bearish" if cs < 35 else "bullish" if cs >= 80 else "neutral"
    scale = pdc / 55000.0 if pdc else 1.0
    return df, pdh, pdc, pdl, bias, scale

def main():
    bn_df = intraday_df("/tmp/bn_29oct.json")
    nf_df = intraday_df("/tmp/nf_29oct.json")
    print(f"BN bars={len(bn_df)} open={bn_df.iloc[0]['open']} high={bn_df['high'].max()} low={bn_df['low'].min()} close={bn_df.iloc[-1]['close']}")
    print(f"NF bars={len(nf_df)} open={nf_df.iloc[0]['open']} high={nf_df['high'].max()} low={nf_df['low'].min()} close={nf_df.iloc[-1]['close']}")
    _, bn_daily = load_sym("BANKNIFTY")
    _, nf_daily = load_sym("NIFTY")
    bn_prev = bn_daily[bn_daily["date"] == pd.Timestamp("2026-10-28")].iloc[0]
    nf_prev = nf_daily[nf_daily["date"] == pd.Timestamp("2026-10-28")].iloc[0]
    print("BN prev28", dict(bn_prev), "NF prev28", dict(nf_prev))
    wk = pd.Timestamp(DS).isocalendar(); wkstr = f"{wk[0]}-W{wk[1]:02d}"
    print("ISO week", wkstr)
    out = {"date": DS, "week": wkstr}
    # ---- V4 + Skill single day, per symbol ----
    for sym, df, prev in (("BANKNIFTY", bn_df, bn_prev), ("NIFTY", nf_df, nf_prev)):
        pdh, pdc, pdl = float(prev["high"]), float(prev["close"]), float(prev["low"])
        bias, cs = bias_of(prev)
        scale = pdc / 55000.0 if pdc else 1.0
        allowed = {"PE"} if bias == "bearish" else {"CE"} if bias == "bullish" else {"CE", "PE"}
        print(f"\n{sym}: PDH={pdh} PDC={pdc} PDL={pdl} bias={bias} cs={cs:.1f} scale={scale:.4f} allowed={allowed}")
        or_c = df[df["time"] < "09:30"]
        print(f"  OR high={or_c['high'].max()} low={or_c['low'].min()} width={or_c['high'].max()-or_c['low'].min():.2f}")
        r = run_day(df, pdh, pdc, pdl, bias, scale, QTY, COST)
        setup, direction, sig = find_signal(df, pdh, pdc, pdl, bias, scale)
        print(f"  V4 run_day={r} find_signal={setup} {direction} sig={None if sig is None else dict(sig)}")
        v4cand = None
        if r["exit_reason"] in ("target", "stop", "square_off"):
            sig_close = float(sig["close"]) if sig is not None else float(r["entry_price"])
            rr, room = room_ratio(sig_close, direction, pdh, pdc, pdl, scale)
            dirc = 1 if direction == "CE" else -1
            tnet = round(dirc * (float(r["target_price"]) - float(r["entry_price"])) * QTY - COST, 2)
            v4cand = {"method": "V4", "symbol": sym, "date": DS, "week": wkstr, "setup": setup,
                      "direction": direction, "exit_reason": r["exit_reason"], "net_rs": round(float(r["net_rs"]), 2),
                      "target_net_rs": tnet, "setup_rank": SETUP_RANK.get(setup, 0),
                      "room_ratio": round(min(rr, 5.0), 3) if rr != float("inf") else 1.0,
                      "bias_strong": 1 if bias != "neutral" else 0, "results_pass": 0,
                      "entry": r["entry_price"], "stop": r["stop_price"], "target": r["target_price"],
                      "signal_time": None if sig is None else str(sig["time"]) if "time" in sig else None}
            print("  V4 candidate:", v4cand)
        raw = df.to_dict("records")
        for c in raw:
            c["timestamp"] = str(c["timestamp"])
        ssetup, sdirection, ssig = find_skill_signal(raw, ("or",))
        print(f"  Skill find_signal={ssetup} {sdirection} sig={ssig}")
        skillcand = None
        if ssetup is not None:
            filt = []
            if sdirection not in allowed: filt.append("bias-not-allowed")
            sig_close = float(ssig["close"])
            if sdirection == "CE" and not (sig_close < pdh): filt.append("CE close>=PDH")
            if sdirection == "PE" and not (sig_close < pdl): filt.append("PE close>=PDL")
            rr, room = room_ratio(sig_close, sdirection, pdh, pdc, pdl, scale)
            if rr < 1.0: filt.append(f"room_ratio {rr:.3f}<1")
            print(f"  Skill filters: sig_close={sig_close} room={room:.2f} rr={rr:.3f} fail={filt}")
            if not filt:
                o = skill_or_outcome(raw, ssig, sdirection)
                print("  Skill outcome:", o)
                if o is not None:
                    dirc = 1 if sdirection == "CE" else -1
                    tnet = round(dirc * (o["target"] - o["entry"]) * QTY - COST, 2)
                    skillcand = {"method": "Skill", "symbol": sym, "date": DS, "week": wkstr, "setup": ssetup,
                                 "direction": sdirection, "exit_reason": o["exit_reason"], "net_rs": o["net_rs"],
                                 "target_net_rs": tnet, "setup_rank": 0,
                                 "room_ratio": round(min(rr, 5.0), 3) if rr != float("inf") else 1.0,
                                 "bias_strong": 1 if bias != "neutral" else 0, "results_pass": 0,
                                 "entry": o["entry"], "stop": o["stop"], "target": o["target"],
                                 "signal_time": ssig["time"] if "time" in ssig else None}
                    print("  Skill candidate:", skillcand)
        out[f"v4_{sym}"] = v4cand
        out[f"skill_{sym}"] = skillcand
    # ---- (lA) single day ----
    dd_n = day_tuple(nf_df, nf_prev)
    dd_b = day_tuple(bn_df, bn_prev)
    # day_data_bn tuple for Nifty confirmation is (spot, pdh, pdc, pdl) only
    dbn = (bn_df, dd_b[1], dd_b[2], dd_b[3])
    rn = day_la_nifty(dd_n, dbn)
    rb = day_la_bank(dd_b, (dd_n[0], dd_n[1], dd_n[2], dd_n[3]))
    print("\n(lA) Nifty:", rn)
    print("(lA) Bank mirror:", rb)
    la_cands = []
    for sym, res, dd in (("NIFTY", rn, dd_n), ("BANKNIFTY", rb, dd_b)):
        m = res["morning"]
        if m is None or res["day_net"] is None:
            print(f"(lA) {sym}: no candidate (morning={m})"); continue
        bias, scale = dd[4], dd[5]
        pdh, pdc, pdl = dd[1], dd[2], dd[3]
        cand = dd[0][dd[0]["time"] >= "09:30"]
        sig_row = cand[cand["time"] == m["signal"]]
        sig_close = float(sig_row.iloc[0]["close"]) if len(sig_row) else float(m["entry"])
        rr, room = room_ratio(sig_close, "PE", pdh, pdc, pdl, scale)
        morning_target_net = round(2 * float(m["risk"]) * QTY - COST, 2) if m.get("risk") else 0.0
        cand_d = {"method": "(lA)", "symbol": sym, "date": DS, "week": wkstr, "setup": "la_pe_rescan_reentry",
                  "direction": "PE",
                  "exit_reason": ("target" if res["day_net"] > 0 and res["re"] is None and m["exit"] == "target"
                                  else "day_green" if res["day_net"] > 0 else "day_loss"),
                  "net_rs": round(float(res["day_net"]), 2), "target_net_rs": morning_target_net,
                  "setup_rank": 1, "room_ratio": round(min(rr, 5.0), 3) if rr != float("inf") else 1.0,
                  "bias_strong": 1 if bias != "neutral" else 0, "results_pass": 0,
                  "morning_signal": m["signal"], "morning_exit": m["exit"], "morning_net": m["net"],
                  "re_signal": res["re"]["re_signal"] if res["re"] else None,
                  "re_exit": res["re"]["exit"] if res["re"] else None,
                  "re_net": res["re"]["net"] if res["re"] else None}
        la_cands.append(cand_d); print("(lA) candidate:", cand_d)
    out["la_candidates"] = la_cands
    with open(os.path.expanduser("~/workspace/trading/four_column_29oct_candidates.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("\nwrote four_column_29oct_candidates.json")
    # ---- October re-cap ----
    print("\n--- October re-cap (regenerating Oct 2026 candidates from cache) ---")
    ndays, v4_all, skill_raw, skill_filt = v2_candidates(2026, 10)
    print(f"Oct cache days={ndays} v4_all={len(v4_all)} skill_filt={len(skill_filt)}")
    mg = json.load(open(os.path.expanduser("~/workspace/trading/data/progressive/merged_skill_la_summary_2026-10.json")))
    la_oct = mg["la_candidates"]
    def idx_slice(trades, sym): return [t for t in trades if t["symbol"] == sym]
    for name, cands, capfn in (("V4", v4_all, cap_select_v2), ("Skill", skill_filt, cap_select_v2)):
        for sym in ("BANKNIFTY", "NIFTY"):
            pool = [t for t in cands if t["symbol"] == sym]
            capped, _ = capfn(pool)
            print(f"Oct1-28 {name} {sym}: {len(capped)} trades net {sum(t['net_rs'] for t in capped)} -> {[(t['date'],t['net_rs']) for t in sorted(capped,key=lambda x:x['date'])]}")
    la_cap28, _ = la_cap_select(la_oct)
    print(f"Oct1-28 (lA) Nifty: {[(t['date'],t['net_rs']) for t in sorted(idx_slice(la_cap28,'NIFTY'),key=lambda x:x['date'])]} net {sum(t['net_rs'] for t in idx_slice(la_cap28,'NIFTY'))}")
    # Add 29 Oct candidates and re-cap
    v4_29 = [out["v4_BANKNIFTY"], out["v4_NIFTY"]]
    sk_29 = [out["skill_BANKNIFTY"], out["skill_NIFTY"]]
    for name, allc, c29, capfn in (("V4", v4_all, v4_29, cap_select_v2), ("Skill", skill_filt, sk_29, cap_select_v2)):
        for sym in ("BANKNIFTY", "NIFTY"):
            pool = [t for t in allc if t["symbol"] == sym] + [t for t in c29 if t and t["symbol"] == sym]
            capped, _ = capfn(pool)
            print(f"Oct1-29 {name} {sym}: {len(capped)} trades net {sum(t['net_rs'] for t in capped)} -> {[(t['date'],t['net_rs']) for t in sorted(capped,key=lambda x:x['date'])]}")
    la_cap29, _ = la_cap_select(la_oct + la_cands)
    print(f"Oct1-29 (lA) Nifty: {[(t['date'],t['net_rs']) for t in sorted(idx_slice(la_cap29,'NIFTY'),key=lambda x:x['date'])]} net {sum(t['net_rs'] for t in idx_slice(la_cap29,'NIFTY'))}")
    print(f"Oct1-29 (lA) Bank: {[(t['date'],t['net_rs']) for t in sorted(idx_slice(la_cap29,'BANKNIFTY'),key=lambda x:x['date'])]} net {sum(t['net_rs'] for t in idx_slice(la_cap29,'BANKNIFTY'))}")

if __name__ == "__main__":
    main()
