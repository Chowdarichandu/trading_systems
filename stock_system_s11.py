"""S11 stock system — S9 + no-event AND rule (room>=2.0 AND prospective>=1000). See new_stock_system_s11_frozen.md.
Original S9 docstring: — frozen spec in new_stock_system_s9_frozen.md.
Paper only, no orders, cash intraday only, NO options.
S9 = S8 price design (imported unchanged) + Event Gate v1 G-TIERED.
Gate mode frozen 2026-10-30 BEFORE scoring; no E-ONLY / E-BLOCK run.
Gate is applied to the UNCAPPED S8 pool, then gate-ranked cap.
All rupee totals are per 100 shares, provisional — NOT a lot profit.
"""
import sys, os, json, csv, bisect
sys.path.insert(0, "/home/hatch/workspace/trading")
import pandas as pd
from progressive_capped import load, SYMBOLS
from daytrader_cash_backtest import bias_of
from new_stock_system_s1 import nifty_day_map
from stock_system_s8 import (_pe_candidate, _ce_pullback_candidate,
                            run_s8, metrics, RANK_SETUP, STOCKS)

CAL = os.path.expanduser("~/workspace/trading/stock_event_calendar_jan_oct_2026.csv")
SINGLE_TYPES = {"management_change", "large_order", "fda_approval",
                "block_deal", "sector_policy"}
TIER_RANK = {"post_reaction": 4, "single_news": 3, "pre_announcement": 2,
             "no_event": 1}


def trading_days_list():
    _, daily = load("NIFTY")
    return sorted(set(d.date() for d in daily["date"]))


def _parse(s):
    if s is None or (isinstance(s, float) and pd.isna(s)) or str(s).strip() == "":
        return None
    return pd.to_datetime(s).date()


def build_events(tdays):
    cal = pd.read_csv(CAL, dtype=str)
    events = {}
    for _, r in cal.iterrows():
        sym = r["stock"]
        ev = _parse(r["event_date"])
        react = _parse(r["reaction_date"])
        if react is None:
            react = ev  # frozen: blank reaction -> event date (announcement_day)
        ws = _parse(r["window_start"])
        we = _parse(r["window_end"])
        if ws is None and ev is not None:
            # 7th trading day before event_date
            idx = bisect.bisect_left(tdays, ev)
            ws = tdays[idx - 7] if idx - 7 >= 0 else tdays[0]
        if we is None and react is not None:
            idx = bisect.bisect_right(tdays, react)
            we = tdays[idx + 6] if idx + 6 < len(tdays) else None  # open-ended past cache
        events.setdefault(sym, []).append({
            "event_date": ev, "reaction_date": react, "window_start": ws,
            "window_end": we, "event_type": r["event_type"],
            "detail": r.get("detail", "")})
    return events


def tag_candidate(cand, events):
    """Return (gate_tier, gate_pass, nearest_type, nearest_date, nearest_phase)."""
    sym, d = cand["symbol"], pd.to_datetime(cand["date"]).date()
    inwin = []
    for e in events.get(sym, []):
        ws, we = e["window_start"], e["window_end"]
        if ws is not None and d < ws:
            continue
        if we is not None and d > we:
            continue
        if d < e["event_date"]:
            phase = "pre_announcement"
        elif d == e["event_date"]:
            phase = "announcement_day"
        elif d >= e["reaction_date"]:
            phase = "reaction_or_post"
        else:  # between event and reaction (should not occur on a trading day)
            phase = "announcement_day"
        inwin.append((e, phase))
    if not inwin:
        tier = "no_event"
        passed = (cand["room_ratio"] >= 2.0 and cand["target_net_rs"] >= 1000)  # S11: AND, not OR
        return tier, passed, "", "", ""
    singles = [(e, p) for e, p in inwin if e["event_type"] in SINGLE_TYPES]
    if singles:
        tier = "single_news"
        passed = cand["room_ratio"] >= 2.0
        pool = singles
    else:
        posts = [(e, p) for e, p in inwin if p == "reaction_or_post"]
        if posts:
            tier, passed, pool = "post_reaction", True, posts
        else:
            tier, passed, pool = "pre_announcement", True, \
                [(e, p) for e, p in inwin if p in ("pre_announcement", "announcement_day")]
    # nearest: smallest |D-event_date|, tie earliest event_date
    pool_sorted = sorted(pool, key=lambda ep: (abs((d - ep[0]["event_date"]).days),
                                               ep[0]["event_date"]))
    e, phase = pool_sorted[0]
    return tier, passed, e["event_type"], e["event_date"].isoformat(), phase


def gate_filter(uncapped, events):
    """Return (survivors, blocked, tagged_all). Tagged fields added to copies."""
    survivors, blocked, tagged = [], [], []
    for c in uncapped:
        tier, passed, nt, nd, phase = tag_candidate(c, events)
        t = dict(c)
        t["gate_tier"] = tier
        t["gate_pass"] = passed
        t["nearest_event_type"] = nt
        t["nearest_event_date"] = nd
        t["event_phase"] = phase
        tagged.append(t)
        (survivors if passed else blocked).append(t)
    return survivors, blocked, tagged


def cap_select_gate(survivors):
    key = lambda t: (-TIER_RANK[t["gate_tier"]], -t["target_net_rs"],
                     -t["room_ratio"], -RANK_SETUP.get(t["setup"], 0),
                     t["date"], t["symbol"])
    ranked = sorted(survivors, key=key)
    picked, days, sym_week = [], set(), set()
    capped_out = 0
    for t in ranked:
        if t["date"] in days or (t["symbol"], t["week"]) in sym_week:
            capped_out += 1
            continue
        picked.append(t)
        days.add(t["date"])
        sym_week.add((t["symbol"], t["week"]))
    return picked, capped_out


def summarise_s9(capped, trading_days, s8_uncapped, gate_survivors, blocked):
    m = metrics(capped)
    cum, months = 0.0, {}
    for mo in range(1, 11):
        mt = [t for t in capped if t["month"] == mo]
        mm = metrics(mt)
        cum = round(cum + mm["net_rs"], 2)
        months[mo] = {**mm, "cumulative_rs": cum}
    per_stock = {s: metrics([t for t in capped if t["symbol"] == s]) for s in STOCKS}
    days_traded = sorted(set(t["date"] for t in capped))
    days_s8_cand = sorted(set(t["date"] for t in s8_uncapped))
    days_gate = sorted(set(t["date"] for t in gate_survivors))
    ce = [t for t in capped if t["direction"] == "CE"]
    pe = [t for t in capped if t["direction"] == "PE"]
    return {"total": m, "trading_days": len(trading_days),
            "days_traded": len(days_traded),
            "days_with_s8_candidate": len(days_s8_cand),
            "days_with_gate_passing_candidate": len(days_gate),
            "days_no_s8_candidate": len(trading_days) - len(days_s8_cand),
            "days_gate_blocked_all_candidates": len(days_s8_cand) - len(days_gate),
            "days_with_candidate_but_capped_out": len(days_gate) - len(days_traded),
            "freq_per_trading_day": round(m["trades"] / len(trading_days), 3) if trading_days else 0,
            "freq_per_week": round(m["trades"] / 44, 2),
            "months": months, "per_stock": per_stock,
            "ex_march_net_rs": round(sum(t["net_rs"] for t in capped if t["month"] != 3), 2),
            "ex_october_net_rs": round(sum(t["net_rs"] for t in capped if t["month"] != 10), 2),
            "direction": {"CE": len(ce), "PE": len(pe)},
            "setups": {k: sum(1 for t in capped if t["setup"] == k) for k in sorted(set(t["setup"] for t in capped))},
            "ce_leg": metrics(ce), "pe_leg": metrics(pe),
            "gate_tiers_capped": {k: sum(1 for t in capped if t["gate_tier"] == k) for k in sorted(set(t["gate_tier"] for t in capped))},
            "gate_tiers_capped_net": {k: round(sum(t["net_rs"] for t in capped if t["gate_tier"] == k), 2) for k in sorted(set(t["gate_tier"] for t in capped))},
            "gate_tiers_survivors": {k: sum(1 for t in gate_survivors if t["gate_tier"] == k) for k in sorted(set(t["gate_tier"] for t in gate_survivors))},
            "gate_blocked_by_tier": {k: sum(1 for t in blocked if t["gate_tier"] == k) for k in sorted(set(t["gate_tier"] for t in blocked))},
            "exit_reasons": {k: sum(1 for t in capped if t.get("exit_reason") == k) for k in sorted(set(t.get("exit_reason") for t in capped))},
            "zero_trade_stocks": sorted(s for s in STOCKS if per_stock[s]["trades"] == 0)}


def run_s9_week(start="2026-10-26", end="2026-10-29"):
    """S8 candidates restricted to [start, end], from cache only."""
    from stock_system_s8 import _pe_candidate as _pe, _ce_pullback_candidate as _ce
    nmap = nifty_day_map()
    _, nifty_daily = load("NIFTY")
    ndl = nifty_daily.to_dict("records")
    nbias = {}
    for i, y in enumerate(ndl):
        if i == 0:
            continue
        b, _ = bias_of(ndl[i - 1])
        nbias[y["date"].date().isoformat()] = b
    cands, trading_days = [], set()
    for sym in STOCKS:
        spot, daily = load(sym)
        dl = daily.to_dict("records")
        for i, y in enumerate(dl):
            d = y["date"]
            if not (start <= d.date().isoformat() <= end) or i == 0:
                continue
            day_spot = spot[spot["date"] == d]
            if day_spot.empty:
                continue
            trading_days.add(d.date().isoformat())
            prev = dl[i - 1]
            pdh, pdc, pdl = float(prev["high"]), float(prev["close"]), float(prev["low"])
            bias, cs = bias_of(prev)
            scale = pdc / 55000.0 if pdc else 1.0
            or_c = day_spot[day_spot["time"] < "09:30"]
            if or_c.empty:
                continue
            orh, orl = float(or_c["high"].max()), float(or_c["low"].min())
            if not (0.0025 <= (orh - orl) / pdc <= 0.030 if pdc else False):
                continue
            nb = nbias.get(d.date().isoformat())
            if nb is None:
                continue
            candles = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True).to_dict("records")
            wk = d.isocalendar()[:2]
            week = f"{wk[0]}-W{wk[1]:02d}"
            day_open = float(day_spot.iloc[0]["open"])
            day_cands = []
            pe = _pe(day_spot, candles, pdh, pdc, pdl, bias, scale, orh, orl, nb, week, sym, d)
            if pe is not None:
                day_cands.append(pe)
            ce = _ce(candles, day_open, pdh, pdc, pdl, bias, scale, orh, orl, nb, week, sym, d)
            if ce is not None:
                day_cands.append(ce)
            if not day_cands:
                continue
            day_cands.sort(key=lambda t: (t["entry_time"], -t["target_net_rs"]))
            cands.append(day_cands[0])
    return cands, trading_days


def _write_csv(path, rows):
    fields = []
    for r in rows:
        for k in r.keys():
            if k not in fields:
                fields.append(k)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    tdays_list = trading_days_list()
    events = build_events(tdays_list)
    # Jan-Oct: reuse S8 uncapped pool exactly (identical price design)
    uncapped, funnel, tdays = run_s8()
    survivors, blocked, tagged = gate_filter(uncapped, events)
    capped, capped_out = cap_select_gate(survivors)
    summ = summarise_s9(capped, tdays, uncapped, survivors, blocked)
    out = {"funnel_s8": funnel, "s8_uncapped": len(uncapped),
           "gate_survivors": len(survivors), "gate_blocked": len(blocked),
           "capped_out": capped_out, "summary": summ}
    print(json.dumps(out, indent=2, default=str))
    _write_csv(os.path.expanduser("~/workspace/trading/s11_trades_jan_oct_2026.csv"), capped)
    _write_csv(os.path.expanduser("~/workspace/trading/s11_uncapped_jan_oct_2026.csv"), survivors)
    _write_csv(os.path.expanduser("~/workspace/trading/s11_gate_blocked_jan_oct_2026.csv"), blocked)
    with open(os.path.expanduser("~/workspace/trading/data/progressive/s11_summary_2026-jan-oct.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
    # Week slice Oct 26-29, cache only
    w_unc, w_days = run_s9_week()
    w_surv, w_block, w_tag = gate_filter(w_unc, events)
    w_cap, w_capout = cap_select_gate(w_surv)
    print("WEEK", json.dumps({"trading_days_in_cache": sorted(w_days),
                              "s8_uncapped": len(w_unc), "gate_survivors": len(w_surv),
                              "gate_blocked": len(w_block), "capped": len(w_cap),
                              "capped_out": w_capout, "metrics": metrics(w_cap)}, indent=2, default=str))
    _write_csv(os.path.expanduser("~/workspace/trading/s11_trades_oct26_29_2026.csv"), w_cap)
    _write_csv(os.path.expanduser("~/workspace/trading/s11_uncapped_oct26_29_2026.csv"), w_surv)
    with open(os.path.expanduser("~/workspace/trading/data/progressive/s11_summary_oct26_29.json"), "w") as f:
        json.dump({"trading_days_in_cache": sorted(w_days), "s8_uncapped": w_unc,
                   "gate_survivors": w_surv, "gate_blocked": w_block,
                   "capped": w_cap, "metrics": metrics(w_cap)}, f, indent=2, default=str)
