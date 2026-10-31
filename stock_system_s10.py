"""S10 stock system — frozen spec in new_stock_system_s10_frozen.md.
Paper only, no orders, cash intraday only, NO options.
S10 = S9 exactly, ONE change: setup2_or_breakdown PE candidates get a
structural-support room test (nearest prior-20d daily low below entry,
extend to 60d, open-downside sentinel) replacing the PD-level room test.
S9 gate + gate-ranked cap imported unchanged.
All rupee totals are per 100 shares, provisional — NOT a lot profit.
"""
import sys, os, json, csv
sys.path.insert(0, "/home/hatch/workspace/trading")
import pandas as pd
from progressive_capped import load
from daytrader_cash_backtest import find_signal, bias_of
from new_stock_system_s1 import replay, nifty_day_map
from stock_system_s8 import _ce_pullback_candidate, metrics, STOCKS
from stock_system_s9 import (build_events, gate_filter, cap_select_gate,
                             trading_days_list, summarise_s9)

QTY, COST = 100, 40.0
ROOM_MIN = 1.5


def _structural_room(entry, lows20, lows60):
    """Return (room, room_ratio_basis_value, basis) per frozen S10 spec.
    room None means open downside (test passed, sentinel ratio 999.0)."""
    below20 = [s for s in lows20 if s < entry]
    if below20:
        room = entry - max(below20)
        return room, "swing20"
    below60 = [s for s in lows60 if s < entry]
    if below60:
        room = entry - max(below60)
        return room, "swing60"
    return None, "open_downside"


def _pe_candidate_s10(day_spot, candles, pdh, pdc, pdl, bias, scale, orh, orl,
                      nb, week, sym, d, lows20, lows60):
    """S8 _pe_candidate copied; ONLY the room branch differs for setup2 PE."""
    setup, direction, sig = find_signal(day_spot, pdh, pdc, pdl, bias, scale)
    if setup is None or sig is None or direction != "PE":
        return None
    sig_idx = None
    for j, c in enumerate(candles):
        if str(c["timestamp"]) == str(sig["timestamp"]):
            sig_idx = j
            break
    if sig_idx is None or sig_idx + 2 >= len(candles):
        return None
    conf = candles[sig_idx + 1]
    if not (float(conf["close"]) < float(sig["close"])):
        return None
    entry_candle = candles[sig_idx + 2]
    entry = float(entry_candle["open"])
    stop = max(float(sig["high"]), float(conf["high"]))
    risk = stop - entry
    if risk <= 0:
        return None
    target = entry - 2 * risk
    if setup == "setup2_or_breakdown":
        room, basis = _structural_room(entry, lows20, lows60)
        if room is None:
            room_val, room_ratio = "", 999.0
        else:
            if room < ROOM_MIN * risk:
                return None
            room_val, room_ratio = round(room, 2), round(room / risk, 3)
    else:
        levels = sorted(set([pdh, pdc, pdl]))
        nxt = [l for l in levels if l < entry]
        if not nxt:
            return None
        room = entry - max(nxt)
        if room < ROOM_MIN * risk:
            return None
        room_val, room_ratio, basis = round(room, 2), round(room / risk, 3), "pd_level"
    if nb == "bullish":  # Nifty bias-only: PE blocked on bullish Nifty days
        return None
    tnet = round(2 * risk * QTY - COST, 2)
    if tnet < 500:
        return None
    crecs = [{"time": c["time"], "high": float(c["high"]), "low": float(c["low"]),
              "close": float(c["close"])} for c in candles]
    out = replay(crecs, sig_idx + 2, entry, stop, target, "PE")
    return {"symbol": sym, "date": d.date().isoformat(), "month": d.month, "week": week,
            "setup": setup, "direction": "PE", "bias": bias,
            "signal_time": str(sig["timestamp"]), "confirm_time": str(conf["timestamp"]),
            "entry_time": entry_candle["time"],
            "entry": round(entry, 2), "stop": round(stop, 2), "target": round(target, 2),
            "risk": round(risk, 2), "room": room_val, "room_ratio": room_ratio,
            "room_basis": basis if setup == "setup2_or_breakdown" else "pd_level",
            "target_net_rs": tnet, "orh": orh, "orl": orl, "nifty_bias": nb, **out}


def run_s10(year=2026, months=range(1, 11)):
    _, nifty_daily = load("NIFTY")
    ndl = nifty_daily.to_dict("records")
    nbias = {}
    for i, y in enumerate(ndl):
        if i == 0:
            continue
        b, _ = bias_of(ndl[i - 1])
        nbias[y["date"].date().isoformat()] = b
    funnel = {"scanned": 0, "or_pass": 0, "uncapped": 0}
    trading_days = set()
    cands = []
    for sym in STOCKS:
        spot, daily = load(sym)
        dl = daily.to_dict("records")
        for i, y in enumerate(dl):
            d = y["date"]
            if d.year != year or d.month not in months or i == 0:
                continue
            day_spot = spot[spot["date"] == d]
            if day_spot.empty:
                continue
            funnel["scanned"] += 1
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
            funnel["or_pass"] += 1
            nb = nbias.get(d.date().isoformat())
            if nb is None:
                continue
            candles = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True).to_dict("records")
            wk = d.isocalendar()[:2]
            week = f"{wk[0]}-W{wk[1]:02d}"
            day_open = float(day_spot.iloc[0]["open"])
            lows20 = [float(r["low"]) for r in dl[max(0, i - 20):i]]
            lows60 = [float(r["low"]) for r in dl[max(0, i - 60):i]]
            day_cands = []
            pe = _pe_candidate_s10(day_spot, candles, pdh, pdc, pdl, bias, scale,
                                   orh, orl, nb, week, sym, d, lows20, lows60)
            if pe is not None:
                day_cands.append(pe)
            ce = _ce_pullback_candidate(candles, day_open, pdh, pdc, pdl, bias, scale,
                                        orh, orl, nb, week, sym, d)
            if ce is not None:
                day_cands.append(ce)
            if not day_cands:
                continue
            day_cands.sort(key=lambda t: (t["entry_time"], -t["target_net_rs"]))
            cands.append(day_cands[0])
    funnel["uncapped"] = len(cands)
    return cands, funnel, trading_days


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
    uncapped, funnel, tdays = run_s10()
    survivors, blocked, tagged = gate_filter(uncapped, events)
    capped, capped_out = cap_select_gate(survivors)
    summ = summarise_s9(capped, tdays, uncapped, survivors, blocked)
    s2pe = [t for t in capped if t["setup"] == "setup2_or_breakdown"]
    s2pe_unc = [t for t in uncapped if t["setup"] == "setup2_or_breakdown"]
    out = {"funnel": funnel, "uncapped": len(uncapped),
           "gate_survivors": len(survivors), "gate_blocked": len(blocked),
           "capped_out": capped_out, "summary": summ,
           "setup2pe_uncapped": len(s2pe_unc),
           "setup2pe_capped_metrics": metrics(s2pe),
           "setup2pe_room_basis": {b: sum(1 for t in s2pe_unc if t.get("room_basis") == b)
                                   for b in sorted(set(t.get("room_basis") for t in s2pe_unc))}}
    print(json.dumps(out, indent=2, default=str))
    base = os.path.expanduser("~/workspace/trading")
    _write_csv(f"{base}/s10_trades_jan_oct_2026.csv", capped)
    _write_csv(f"{base}/s10_uncapped_jan_oct_2026.csv", survivors)
    _write_csv(f"{base}/s10_gate_blocked_jan_oct_2026.csv", blocked)
    with open(f"{base}/data/progressive/s10_summary_2026-jan-oct.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
