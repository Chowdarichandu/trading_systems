"""Merged backtest: Day Trader Skill + (lA), NIFTY + BANKNIFTY, October 2026 only.
Paper only, no orders. Provisional merged definition, frozen before scoring (see report).
- Skill: OR-only, V4-style filters, from progressive_capped_v2.candidates_for_month(2026,10), index only.
- (lA) Nifty: rescan_trade + scan_reentry variant 'lA' from extended_window_sweep.py (v4 mode).
- (lA) Bank mirror (PROVISIONAL adaptation, not original (lA)): roles swapped —
  confirming index = NIFTY (first Nifty bar 09:30-11:30 close < Nifty OR low),
  rescan = first Bank bar >= Nifty break, <=11:30, close < Bank OR low AND < Bank PDL,
  OR width <=360*scale_bank, room >=200*scale_bank, scale_bank = Bank prev close/55000.
  Re-entry: candidates close < Bank OR low, band risk in [10, rescan risk],
  morning scan-skip to 11:30, afternoon stop-on-first-fail to 15:05, PE replay.
- (lA) day result = morning net + re-entry net if re-entry trades (each leg Rs40 in replay_pe),
  counted as ONE candidate per symbol+date. Prospective target net = morning target net.
- (lA) setup_rank = 1 (provisional: morning is a setup2-class breakdown; Skill OR = 0).
- Dedup same symbol+date: (lA) wins over Skill. Cap: max 3 index/week, max 1/symbol/week,
  filter prospective net target >= Rs500. Rank: setup_rank, bias_strong, room_ratio, target_net_rs.
- Win rate in this report = net > 0 (green) for ALL series, so (lA) day greens are comparable
  to Skill targets; target/stop/square-off counts are also shown for Skill, and morning/re-entry
  exits are shown for (lA) in the trade list.
"""
import os, sys, json, math
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
import pandas as pd
from progressive_capped_v2 import candidates_for_month as v2_candidates
from progressive_capped import load as load_sym, room_ratio
from timing_sweep import load as load_nifty, day_data as day_data_nifty
from reentry_filter_sweep import load_bn, day_data_bn, bn_break_time
from combined_confirm_sweep import rescan_trade
from extended_window_sweep import scan_reentry
from close_reentry_sweep import replay_pe

QTY, COST = 100, 40.0
INDEX = ("NIFTY", "BANKNIFTY")

def metrics(trades):
    if not trades:
        return {"trades": 0, "targets": 0, "stops": 0, "square_offs": 0, "wins_green": 0,
                "win_rate_pct": 0.0, "net_rs": 0.0, "expectancy_rs": 0.0, "max_drawdown_rs": 0.0}
    net = sum(t["net_rs"] for t in trades); cum = peak = dd = 0.0
    for t in sorted(trades, key=lambda x: (x["date"], x["symbol"])):
        cum += t["net_rs"]; peak = max(peak, cum); dd = max(dd, peak - cum)
    return {"trades": len(trades),
            "targets": sum(1 for t in trades if t.get("exit_reason") == "target"),
            "stops": sum(1 for t in trades if t.get("exit_reason") == "stop"),
            "square_offs": sum(1 for t in trades if t.get("exit_reason") == "square_off"),
            "wins_green": sum(1 for t in trades if t["net_rs"] > 0),
            "win_rate_pct": round(100 * sum(1 for t in trades if t["net_rs"] > 0) / len(trades), 1),
            "net_rs": round(net, 2), "expectancy_rs": round(net / len(trades), 2),
            "max_drawdown_rs": round(dd, 2)}

def cap_select(cands, min_target=500.0):
    pool = [t for t in cands if t["target_net_rs"] >= min_target]
    ranked = sorted(pool, key=lambda t: (-t["setup_rank"], -t["bias_strong"], -t["room_ratio"],
                                         -t["target_net_rs"], t["date"], t["symbol"]))
    picked, week_idx, sym_week = [], {}, set()
    for t in ranked:
        w = t["week"]
        if week_idx.get(w, 0) >= 3:
            continue
        if (t["symbol"], w) in sym_week:
            continue
        picked.append(t); week_idx[w] = week_idx.get(w, 0) + 1; sym_week.add((t["symbol"], w))
    return picked, ranked

# ---------- Bank (lA) mirror ----------
def load_bank():
    spot = pd.read_csv(os.path.expanduser("~/workspace/trading/data/progressive/BANKNIFTY/spot_5m.csv"), parse_dates=["timestamp"])
    daily = pd.read_csv(os.path.expanduser("~/workspace/trading/data/progressive/BANKNIFTY/spot_daily.csv"), parse_dates=["date"])
    spot["timestamp"] = pd.to_datetime(spot["timestamp"]).dt.tz_localize(None)
    daily["date"] = pd.to_datetime(daily["date"]).dt.tz_localize(None).dt.normalize()
    spot["date"] = spot["timestamp"].dt.normalize()
    spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
    return spot.sort_values("timestamp"), daily.sort_values("date")

def day_data_bank(spot, daily, datestr):
    d = pd.Timestamp(datestr)
    day_spot = spot[spot["date"] == d]
    prev = daily[daily["date"] < d]
    if day_spot.empty or prev.empty:
        return None
    y = prev.iloc[-1]
    pdh, pdc, pdl = float(y["high"]), float(y["close"]), float(y["low"])
    rng = pdh - pdl
    cs = (pdc - pdl) / rng * 100 if rng else 50.0
    bias = "bearish" if cs < 35 else "bullish" if cs >= 80 else "neutral"
    scale = pdc / 55000.0 if pdc else 1.0
    return day_spot, pdh, pdc, pdl, bias, scale

def nifty_break_time(day_nifty):
    """First Nifty bar 09:30-11:30 close < Nifty OR low. Returns (time, orl, orh) or (None,...)."""
    day_spot, pdh, pdc, pdl = day_nifty
    or_c = day_spot[day_spot["time"] < "09:30"]
    orh = float(or_c["high"].max()); orl = float(or_c["low"].min())
    cand = day_spot[(day_spot["time"] >= "09:30") & (day_spot["time"] <= "11:30")]
    for _, c in cand.iterrows():
        if float(c["close"]) < orl:
            return c["time"], orl, orh
    return None, orl, orh

def rescan_bank(dd_bank, day_nifty):
    day_spot, pdh, pdc, pdl, bias, scale = dd_bank
    bt, nf_orl, nf_orh = nifty_break_time(day_nifty)
    if bt is None:
        return None
    or_c = day_spot[day_spot["time"] < "09:30"]
    orh = float(or_c["high"].max()); orl = float(or_c["low"].min())
    or_width = orh - orl
    cand = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True)
    levels = sorted(set([pdh, pdc, pdl]))
    sig = None
    for i, (_, c) in enumerate(cand.iterrows()):
        t = c["time"]
        if t > "11:30" or t < bt:
            continue
        cl = float(c["close"])
        if cl < orl and cl < pdl:
            nxt = [l for l in levels if l < cl]
            room = (cl - max(nxt)) if nxt else math.inf
            if or_width <= 360 * scale and room >= 200 * scale:
                sig = i; break
    if sig is None or sig + 1 >= len(cand):
        return None
    s = cand.iloc[sig]
    entry = float(cand.iloc[sig + 1]["open"]); stop = float(s["high"]); risk = stop - entry
    target = entry - 2 * risk
    tr = replay_pe(cand, sig + 1, entry, stop, target)
    tr.update({"signal": s["time"], "nifty_break": bt, "orl": orl})
    return {"candles": cand, "orl": orl, "orh": orh, "sig_idx": sig, "info": {"risk": risk, "signal": s["time"]}, "trade": tr}

def day_la_bank(dd_bank, day_nifty):
    r = rescan_bank(dd_bank, day_nifty)
    if r is None:
        return {"morning": None, "re": None, "day_net": None, "skipped": []}
    tr = r["trade"]
    if tr is None or tr.get("net") is None:
        return {"morning": tr, "re": None, "day_net": None, "skipped": []}
    if tr.get("exit") != "stop":
        return {"morning": tr, "re": None, "day_net": tr["net"], "skipped": []}
    re, skipped = scan_reentry(r["candles"], r["orl"], tr["exit_idx"], r["info"]["risk"], "lA", tr["net"])
    day_net = round(tr["net"] + re["net"], 2) if (re and re["net"] is not None) else tr["net"]
    return {"morning": tr, "re": re, "day_net": day_net, "skipped": skipped}

def day_la_nifty(dd, day_bn):
    r = rescan_trade(dd, "v4", day_bn)
    if r is None:
        return {"morning": None, "re": None, "day_net": None, "skipped": []}
    tr = r["trade"]
    if tr is None or tr.get("net") is None:
        return {"morning": tr, "re": None, "day_net": None, "skipped": []}
    if tr.get("exit") != "stop":
        return {"morning": tr, "re": None, "day_net": tr["net"], "skipped": []}
    re, skipped = scan_reentry(r["candles"], r["orl"], tr["exit_idx"], r["info"]["risk"], "lA", tr["net"])
    day_net = round(tr["net"] + re["net"], 2) if (re and re["net"] is not None) else tr["net"]
    return {"morning": tr, "re": re, "day_net": day_net, "skipped": skipped}

def main():
    # Skill index candidates, October 2026
    ndays, v4_all, skill_raw, skill_filt = v2_candidates(2026, 10)
    skill_idx = [t for t in skill_filt if t["symbol"] in INDEX]
    print(f"cache days={ndays} skill_filtered_all={len(skill_filt)} skill_index={len(skill_idx)}")
    for t in sorted(skill_idx, key=lambda x: (x["date"], x["symbol"])):
        print("SKILL", t["date"], t["symbol"], t["direction"], t["exit_reason"], t["net_rs"], "tnet", t["target_net_rs"])

    # (lA) for every October day present in Nifty daily cache
    spot_n, daily_n = load_nifty()
    bn_spot, bn_daily = load_bn()
    bank_spot, bank_daily = load_bank()
    oct_days = [d.date().isoformat() for d in daily_n["date"] if d.year == 2026 and d.month == 10]
    print(f"october daily rows in Nifty cache: {len(oct_days)} {oct_days}")
    la = []
    la_diag = []
    for ds in oct_days:
        dd_n = day_data_nifty(spot_n, daily_n, ds)
        dbn = day_data_bn(bn_spot, bn_daily, ds)
        dd_b = day_data_bank(bank_spot, bank_daily, ds)
        # Nifty (lA): confirming = Bank, via day_data_bn (day_spot, pdh, pdc, pdl)
        rn = day_la_nifty(dd_n, dbn) if (dd_n and dbn) else {"morning": None, "re": None, "day_net": None}
        # Bank mirror: confirming = Nifty daily tuple (day_spot, pdh, pdc, pdl) from day_data_nifty
        day_nifty_tuple = (dd_n[0], dd_n[1], dd_n[2], dd_n[3]) if dd_n else None
        rb = day_la_bank(dd_b, day_nifty_tuple) if (dd_b and day_nifty_tuple) else {"morning": None, "re": None, "day_net": None}
        for sym, res, dd in (("NIFTY", rn, dd_n), ("BANKNIFTY", rb, dd_b)):
            m = res["morning"]
            print(f"(lA) {ds} {sym} morning={m} re={res['re']} day_net={res['day_net']}")
            la_diag.append({"date": ds, "symbol": sym, "morning": m, "re": res["re"], "day_net": res["day_net"]})
            if m is None or res["day_net"] is None:
                continue
            # bias/scale for ranking from dd
            bias = dd[4]; scale = dd[5]
            pdh, pdc, pdl = dd[1], dd[2], dd[3]
            sig_close = float(m.get("entry", 0))  # placeholder, replaced below if signal close known
            # rescan signal close: morning trade entry is next open; signal close is not in replay dict.
            # Recompute room from morning signal: use signal time from morning dict.
            # replay_pe dict has no sig close; rescan_trade info has signal time only in info, not trade.
            # So room_ratio here uses entry as proxy ONLY for ranking display? No — avoid fabrication:
            # set room_ratio from the morning signal close by re-reading the day candles at signal time.
            day_spot = dd[0]
            cand = day_spot[day_spot["time"] >= "09:30"]
            sig_row = cand[cand["time"] == m["signal"]]
            sig_close = float(sig_row.iloc[0]["close"]) if len(sig_row) else float(m["entry"])
            rr, room = room_ratio(sig_close, "PE", pdh, pdc, pdl, scale)
            morning_target_net = round(2 * float(m["risk"]) * QTY - COST, 2) if m.get("risk") else 0.0
            wk = pd.Timestamp(ds).isocalendar()
            la.append({"method": "(lA)", "symbol": sym, "date": ds, "week": f"{wk[0]}-W{wk[1]:02d}",
                       "setup": "la_pe_rescan_reentry", "direction": "PE",
                       "exit_reason": ("target" if res["day_net"] > 0 and res["re"] is None and m["exit"] == "target"
                                       else "day_green" if res["day_net"] > 0 else "day_loss"),
                       "net_rs": round(float(res["day_net"]), 2), "target_net_rs": morning_target_net,
                       "setup_rank": 1, "room_ratio": round(min(rr, 5.0), 3) if rr != float("inf") else 1.0,
                       "bias_strong": 1 if bias != "neutral" else 0, "results_pass": 0,
                       "morning_signal": m["signal"], "morning_exit": m["exit"],
                       "morning_net": m["net"],
                       "re_signal": res["re"]["re_signal"] if res["re"] else None,
                       "re_exit": res["re"]["exit"] if res["re"] else None,
                       "re_net": res["re"]["net"] if res["re"] else None})
    print(f"(lA) candidates: {len(la)}")
    for t in sorted(la, key=lambda x: (x["date"], x["symbol"])):
        print("(lA)", t["date"], t["symbol"], t["morning_signal"], t["morning_exit"], t["morning_net"],
              "re", t["re_signal"], t["re_exit"], t["re_net"], "day", t["net_rs"], "tnet", t["target_net_rs"])

    # Series
    skill_cap, _ = cap_select(skill_idx)
    la_cap, _ = cap_select(la)
    # Merged pool: dedup symbol+date, (lA) priority
    pool = {}
    for t in skill_idx:
        pool[(t["symbol"], t["date"])] = t
    for t in la:
        pool[(t["symbol"], t["date"])] = t  # (lA) overwrites Skill on conflict
    merged_cap, merged_ranked = cap_select(list(pool.values()))
    def leg(trades, sym):
        return metrics([t for t in trades if t["symbol"] == sym])
    out = {"year": 2026, "month": 10, "days": ndays,
           "skill_index_candidates": skill_idx, "la_candidates": la, "la_diag": la_diag,
           "skill_capped": metrics(skill_cap), "skill_capped_trades": skill_cap,
           "skill_nifty": leg(skill_cap, "NIFTY"), "skill_banknifty": leg(skill_cap, "BANKNIFTY"),
           "la_capped": metrics(la_cap), "la_capped_trades": la_cap,
           "la_nifty": leg(la_cap, "NIFTY"), "la_banknifty": leg(la_cap, "BANKNIFTY"),
           "merged_capped": metrics(merged_cap), "merged_capped_trades": merged_cap,
           "merged_nifty": leg(merged_cap, "NIFTY"), "merged_banknifty": leg(merged_cap, "BANKNIFTY"),
           "merged_ranked_pool": merged_ranked}
    print("\n=== SKILL capped ===", out["skill_capped"], "NIFTY", out["skill_nifty"], "BN", out["skill_banknifty"])
    print("=== (lA) capped ===", out["la_capped"], "NIFTY", out["la_nifty"], "BN", out["la_banknifty"])
    print("=== MERGED capped ===", out["merged_capped"], "NIFTY", out["merged_nifty"], "BN", out["merged_banknifty"])
    for t in sorted(merged_cap, key=lambda x: (x["date"], x["symbol"])):
        print("MERGED", t["date"], t["symbol"], t["method"], t["direction"], t["exit_reason"], t["net_rs"])
    with open(os.path.expanduser("~/workspace/trading/data/progressive/merged_skill_la_summary_2026-10.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)

if __name__ == "__main__":
    main()
