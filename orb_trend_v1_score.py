#!/usr/bin/env python3
"""ORB-TREND v1 — 15-minute opening-range breakout sleeve for STOCKS.

PRE-REGISTERED SPEC (frozen before first scoring, 2026-11-05):
- Universe: Chandu's 25-stock SarvaRitu watchlist (list copied verbatim
  from stocks_sarvaritu_logger.py SYMBOLS — the authoritative list).
- Equity cash intraday, provisional per 100 shares, cost Rs40/trade.
  Paper only, real money Rs0. NO options/futures numbers anywhere.
- OR = high/low of the 09:15, 09:20, 09:25 5-min bars.
- Trigger: FIRST 5-min bar starting 09:30..14:00 whose CLOSE is above
  OR high (LONG) or below OR low (SHORT). Entry = open of the next bar.
  One entry per stock per day, first break only, no re-entry.
- Families: F1 = no room filter. F2 = room filter vs prior-day daily
  candle: LONG only if PDH >= entry*1.01; SHORT only if PDL <= entry*0.99.
- Exits (both scored on each family's identical entries):
  X1 fixed: stop -0.80%, target +1.50%, square-off at 15:10 bar close.
  X2 trailing ride: initial stop -0.80%; peak (max bar high for LONG /
  min bar low for SHORT, entry bar onward; stop for a bar is set from
  peaks through the PREVIOUS bar, so on the entry bar only the initial
  stop applies) arms at peak >= +1.00% favourable: stop = max(entry
  +0.10%, peak*(1-0.75%)) for LONG (mirror SHORT), never loosening.
  Exit at stop price on touch. No fixed target. Square-off 15:10 close.
- Replay: stop checked before target on every bar INCLUDING the entry
  bar; stop/target levels rounded to 2dp (frozen book convention).
- Windows judged SEPARATELY: Jan-Oct 2025 and Jan-Oct 2026 (data root
  data/full_hist). November 2026 is NOT part of the gate.
- NOT_COMPUTED (counted, named, never estimated): OR bars missing;
  a gap in the trigger window before any trigger; entry bar missing;
  a gap during holding or the day ending before the 15:10 bar; F2 legs
  with no prior-day daily row.
- Placebos (same qualifying days): (i) FLIPPED — opposite direction,
  same entry bar open, same exit variant; (ii) SHIFTED — same direction,
  entry at the open of the bar starting 30 minutes after the real entry
  bar's start, same exit variant.
- GATE PASS per year per F x X: net > 0 AND beats both placebos AND
  Jan-May > 0 AND Jun-Oct > 0 AND ex-top-3 > 0. Months and breadth are
  reported as evidence, not auto-fail legs.
- Nov 5 2026 counterfactual (NOT in the gate): F1 entries from
  data/sarvaritu_fwd (the forward store the evening engine fetched).
"""
import csv, json, pathlib, collections, sys

WS = pathlib.Path.home() / "workspace/trading"
FULL = WS / "data/full_hist"
FWD = WS / "data/sarvaritu_fwd"
COST = 40.0
SYMBOLS = ["GODREJCP", "GLENMARK", "ITC", "RECLTD", "TVSMOTOR", "UNITDSPR",
           "OBEROIRLTY", "NTPC", "INDUSTOWER", "KALYANKJIL", "HDFCBANK",
           "NHPC", "PFC", "IRCTC", "WIPRO", "NATIONALUM", "VEDL",
           "HINDCOPPER", "HINDZINC", "HINDALCO", "TATASTEEL", "ASTRAL",
           "BDL", "OIL", "HINDUNILVR"]
OR_TIMES = ["09:15", "09:20", "09:25"]
SQ = "15:10"


def tmin(t):
    return int(t[:2]) * 60 + int(t[3:5])


def tstr(m):
    return f"{m // 60:02d}:{m % 60:02d}"


def load_bars(root, sym):
    """-> {date: {time: (o,h,l,c)}}"""
    out = collections.defaultdict(dict)
    p = root / sym / "spot_5m.csv"
    if not p.exists():
        return out
    for r in csv.DictReader(open(p)):
        out[r["timestamp"][:10]][r["timestamp"][11:16]] = (
            float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"]))
    return out


def load_daily(root, sym):
    """-> {date: (o,h,l,c)} ordered dict by file order"""
    out = {}
    p = root / sym / "spot_daily.csv"
    if not p.exists():
        return out
    for r in csv.DictReader(open(p)):
        out[r["date"]] = (float(r["open"]), float(r["high"]),
                          float(r["low"]), float(r["close"]))
    return out


def net_of(entry, exit_price, direction):
    if direction == "LONG":
        return round((exit_price - entry) * 100 - COST, 2)
    return round((entry - exit_price) * 100 - COST, 2)


def exit_x1(bars, entry_time, entry, direction):
    if direction == "LONG":
        stop, target = round(entry * 0.992, 2), round(entry * 1.015, 2)
    else:
        stop, target = round(entry * 1.008, 2), round(entry * 0.985, 2)
    m = tmin(entry_time)
    while m <= tmin(SQ):
        t = tstr(m)
        o, h, l, c = bars[t]
        if direction == "LONG":
            if l <= stop:
                return t, stop, "stop"
            if h >= target:
                return t, target, "target"
        else:
            if h >= stop:
                return t, stop, "stop"
            if l <= target:
                return t, target, "target"
        if t == SQ:
            return t, c, "square_off"
        m += 5
    raise AssertionError("holding window incomplete")


def exit_x2(bars, entry_time, entry, direction):
    if direction == "LONG":
        stop = round(entry * 0.992, 2)
        peak, armed = entry, False
    else:
        stop = round(entry * 1.008, 2)
        peak, armed = entry, False
    m = tmin(entry_time)
    while m <= tmin(SQ):
        t = tstr(m)
        o, h, l, c = bars[t]
        if direction == "LONG":
            if l <= stop:
                return t, stop, "trail_stop" if armed else "stop"
            if h > peak:
                peak = h
            if peak >= entry * 1.01:
                armed = True
            if armed:
                stop = max(stop, round(entry * 1.001, 2), round(peak * 0.9925, 2))
        else:
            if h >= stop:
                return t, stop, "trail_stop" if armed else "stop"
            if l < peak:
                peak = l
            if peak <= entry * 0.99:
                armed = True
            if armed:
                stop = min(stop, round(entry * 0.999, 2), round(peak * 1.0075, 2))
        if t == SQ:
            return t, c, "square_off"
        m += 5
    raise AssertionError("holding window incomplete")


EXITORS = {"X1": exit_x1, "X2": exit_x2}


def find_trigger(bars):
    """Returns (status, trigger_time, direction) — status: ok / none / nc."""
    if any(t not in bars for t in OR_TIMES):
        return "nc", None, "OR bars missing (no 09:15-09:25 bars)"
    orh = max(bars[t][1] for t in OR_TIMES)
    orl = min(bars[t][2] for t in OR_TIMES)
    m = tmin("09:30")
    while m <= tmin("14:00"):
        t = tstr(m)
        if t not in bars:
            return "nc", None, "gap in trigger window before any trigger"
        c = bars[t][3]
        if c > orh:
            return "ok", t, "LONG"
        if c < orl:
            return "ok", t, "SHORT"
        m += 5
    return "none", None, None


def holding_complete(bars, entry_time):
    m = tmin(entry_time)
    while m <= tmin(SQ):
        if tstr(m) not in bars:
            return False
        m += 5
    return True


def score_window(root, lo, hi):
    """Score all stock-days in [lo, hi]. Returns (legs, nc_list, audits).
    legs: one dict per (stock-day trigger) with everything needed."""
    legs, nc, audits = [], [], {"timing_violations": 0, "days_seen": 0}
    for sym in SYMBOLS:
        bars_by_day = load_bars(root, sym)
        daily = load_daily(root, sym)
        daily_dates = sorted(daily)
        for day in sorted(bars_by_day):
            if not (lo <= day <= hi):
                continue
            audits["days_seen"] += 1
            bars = bars_by_day[day]
            status, trig_t, extra = find_trigger(bars)
            if status == "nc":
                nc.append({"stock": sym, "date": day, "reason": trig_t if False else extra})
                continue
            if status == "none":
                continue
            direction = extra
            entry_t = tstr(tmin(trig_t) + 5)
            if entry_t not in bars:
                nc.append({"stock": sym, "date": day,
                           "reason": "entry bar missing after trigger"})
                continue
            if not holding_complete(bars, entry_t):
                nc.append({"stock": sym, "date": day,
                           "reason": "gap during holding / day ends before 15:10 bar"})
                continue
            entry = bars[entry_t][0]
            # timing audit: entry strictly after trigger bar start and the
            # entry price is the next bar's open (info = trigger bar close,
            # complete exactly at entry-bar start).
            if not tmin(entry_t) > tmin(trig_t):
                audits["timing_violations"] += 1
            # F2 prior-day room data
            prior = None
            idx = [d for d in daily_dates if d < day]
            if idx:
                prior = daily[idx[-1]]
            leg = {"stock": sym, "date": day, "dir": direction,
                   "trigger_time": trig_t, "entry_time": entry_t,
                   "entry": entry, "prior_day": prior}
            # real + placebo scorings for F1
            for xv, fn in EXITORS.items():
                xt, xp, xr = fn(bars, entry_t, entry, direction)
                leg[f"F1_{xv}"] = (xt, xp, xr, net_of(entry, xp, direction))
                fdir = "SHORT" if direction == "LONG" else "LONG"
                xt, xp, xr = fn(bars, entry_t, entry, fdir)
                leg[f"F1_{xv}_FLIP"] = (xt, xp, xr, net_of(entry, xp, fdir))
                shift_t = tstr(tmin(entry_t) + 30)
                if shift_t in bars and holding_complete(bars, shift_t):
                    sentry = bars[shift_t][0]
                    xt, xp, xr = fn(bars, shift_t, sentry, direction)
                    leg[f"F1_{xv}_SHIFT"] = (xt, xp, xr, net_of(sentry, xp, direction))
                else:
                    leg[f"F1_{xv}_SHIFT"] = None
            legs.append(leg)
    return legs, nc, audits


def f2_admit(leg):
    """Returns True/False/'nc' for the F2 room filter."""
    prior = leg["prior_day"]
    if prior is None:
        return "nc"
    pdh, pdl = prior[1], prior[2]
    e = leg["entry"]
    if leg["dir"] == "LONG":
        return pdh >= e * 1.01
    return pdl <= e * 0.99


def aggregate(legs, fam, xv):
    rows = []
    for leg in legs:
        if fam == "F2":
            adm = f2_admit(leg)
            if adm is not True:
                continue
        key = f"F1_{xv}"  # F2 shares F1's identical-entry scorings
        xt, xp, xr, net = leg[key]
        flip = leg[f"F1_{xv}_FLIP"][3]
        shift = leg[f"F1_{xv}_SHIFT"][3] if leg[f"F1_{xv}_SHIFT"] else None
        rows.append({"date": leg["date"], "stock": leg["stock"], "dir": leg["dir"],
                     "trigger_time": leg["trigger_time"], "entry_time": leg["entry_time"],
                     "entry": leg["entry"], "exit_time": xt, "exit_price": xp,
                     "exit_reason": xr, "net": net, "flip_net": flip, "shift_net": shift})
    return rows


def summarise(rows, year):
    net = round(sum(r["net"] for r in rows), 2)
    longs = [r for r in rows if r["dir"] == "LONG"]
    shorts = [r for r in rows if r["dir"] == "SHORT"]
    h1 = round(sum(r["net"] for r in rows if r["date"][5:7] in ("01", "02", "03", "04", "05")), 2)
    h2 = round(sum(r["net"] for r in rows if r["date"][5:7] in ("06", "07", "08", "09", "10")), 2)
    months = {}
    for mo in range(1, 11):
        mrows = [r for r in rows if int(r["date"][5:7]) == mo]
        months[f"{year}-{mo:02d}"] = {"trades": len(mrows),
                                      "net": round(sum(r["net"] for r in mrows), 2)}
    top3 = sorted(rows, key=lambda r: -r["net"])[:3]
    ex_top3 = round(net - sum(r["net"] for r in top3), 2)
    by_stock = collections.defaultdict(float)
    for r in rows:
        by_stock[r["stock"]] += r["net"]
    breadth = sorted(s for s, v in by_stock.items() if v > 0)
    flips = [r["flip_net"] for r in rows]
    shifts = [r["shift_net"] for r in rows if r["shift_net"] is not None]
    flip_net = round(sum(flips), 2)
    shift_net = round(sum(shifts), 2)
    wins = sum(1 for r in rows if r["net"] > 0)
    gate = {"net>0": net > 0, "beats_flipped": net > flip_net,
            "beats_shifted": net > shift_net, "H1>0": h1 > 0, "H2>0": h2 > 0,
            "ex_top3>0": ex_top3 > 0}
    gate["PASS"] = all(gate.values())
    return {
        "trades": len(rows),
        "win_pct": round(100.0 * wins / len(rows), 1) if rows else 0.0,
        "net": net,
        "long": {"trades": len(longs), "net": round(sum(r["net"] for r in longs), 2)},
        "short": {"trades": len(shorts), "net": round(sum(r["net"] for r in shorts), 2)},
        "halves": {"H1_Jan_May": h1, "H2_Jun_Oct": h2},
        "months": months,
        "ex_top3": ex_top3,
        "top3": [{"date": r["date"], "stock": r["stock"], "net": r["net"]} for r in top3],
        "breadth_positive_stocks": len(breadth), "breadth_list": breadth,
        "placebo_flipped": {"trades": len(flips), "net": flip_net},
        "placebo_shifted": {"trades": len(shifts), "net": shift_net,
                            "unscored": len(rows) - len(shifts)},
        "gate": gate,
    }


def main():
    results = {"spec": "ORB-TREND v1 (pre-registered 2026-11-05)",
               "basis": "equity cash intraday, provisional per 100 shares, Rs40/trade",
               "years": {}}
    all_trade_rows = []
    for year, lo, hi in ((2025, "2025-01-01", "2025-10-31"),
                         (2026, "2026-01-01", "2026-10-31")):
        legs, nc, audits = score_window(FULL, lo, hi)
        f2_nc = sum(1 for leg in legs if f2_admit(leg) == "nc")
        yres = {"stock_days_seen": audits["days_seen"],
                "timing_violations": audits["timing_violations"],
                "triggered_legs": len(legs),
                "not_computed": {"count": len(nc),
                                 "by_reason": dict(collections.Counter(
                                     x["reason"] for x in nc)),
                                 "rows": nc,
                                 "f2_prior_day_missing": f2_nc},
                "books": {}}
        for fam in ("F1", "F2"):
            for xv in ("X1", "X2"):
                rows = aggregate(legs, fam, xv)
                yres["books"][f"{fam}-{xv}"] = summarise(rows, year)
                for r in rows:
                    all_trade_rows.append({
                        "year": year, "family": fam, "exit_variant": xv,
                        "kind": "real", "date": r["date"], "stock": r["stock"],
                        "dir": r["dir"], "trigger_time": r["trigger_time"],
                        "entry_time": r["entry_time"], "entry": r["entry"],
                        "exit_time": r["exit_time"], "exit_price": r["exit_price"],
                        "exit_reason": r["exit_reason"], "net_inr": r["net"]})
                    all_trade_rows.append({
                        "year": year, "family": fam, "exit_variant": xv,
                        "kind": "placebo_flipped", "date": r["date"],
                        "stock": r["stock"],
                        "dir": "SHORT" if r["dir"] == "LONG" else "LONG",
                        "trigger_time": r["trigger_time"],
                        "entry_time": r["entry_time"], "entry": r["entry"],
                        "exit_time": "", "exit_price": "", "exit_reason": "",
                        "net_inr": r["flip_net"]})
                    if r["shift_net"] is not None:
                        leg0 = next(l for l in legs if l["date"] == r["date"]
                                    and l["stock"] == r["stock"])
                        st, sxp, sxr, snet = leg0[f"F1_{xv}_SHIFT"]
                        bars_note = tstr(tmin(r["entry_time"]) + 30)
                        all_trade_rows.append({
                            "year": year, "family": fam, "exit_variant": xv,
                            "kind": "placebo_shifted", "date": r["date"],
                            "stock": r["stock"], "dir": r["dir"],
                            "trigger_time": r["trigger_time"],
                            "entry_time": bars_note, "entry": "",
                            "exit_time": st, "exit_price": sxp,
                            "exit_reason": sxr, "net_inr": snet})
        results["years"][str(year)] = yres
        print(f"year {year}: legs={len(legs)} NC={len(nc)} "
              f"timing_violations={audits['timing_violations']}", flush=True)

    # ---- Nov 5 2026 counterfactual (F1 only, fwd store; NOT in gate) ----
    legs5, nc5, _ = score_window(FWD, "2026-11-05", "2026-11-05")
    cf = {"date": "2026-11-05", "triggered": len(legs5),
          "not_computed": nc5, "rows": []}
    for leg in sorted(legs5, key=lambda l: (l["trigger_time"], l["stock"])):
        row = {"stock": leg["stock"], "dir": leg["dir"],
               "trigger_time": leg["trigger_time"], "entry_time": leg["entry_time"],
               "entry": leg["entry"]}
        for xv in ("X1", "X2"):
            xt, xp, xr, net = leg[f"F1_{xv}"]
            row[xv] = {"exit_time": xt, "exit_price": xp,
                       "exit_reason": xr, "net": net}
        cf["rows"].append(row)
    cf["totals"] = {xv: round(sum(r[xv]["net"] for r in cf["rows"]), 2)
                    for xv in ("X1", "X2")}
    results["nov5_counterfactual"] = cf

    # ---- write trades CSV ----
    fields = ["year", "family", "exit_variant", "kind", "date", "stock", "dir",
              "trigger_time", "entry_time", "entry", "exit_time", "exit_price",
              "exit_reason", "net_inr"]
    out_csv = WS / "orb_trend_v1_trades.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in all_trade_rows:
            w.writerow(r)

    # ---- independent re-sum from the CSV (second code path) ----
    resum = collections.defaultdict(float)
    with open(out_csv) as f:
        for r in csv.DictReader(f):
            if r["kind"] == "real":
                resum[(r["year"], r["family"], r["exit_variant"])] += float(r["net_inr"])
    mismatches = []
    for year in ("2025", "2026"):
        for fam in ("F1", "F2"):
            for xv in ("X1", "X2"):
                got = round(resum[(year, fam, xv)], 2)
                want = results["years"][year]["books"][f"{fam}-{xv}"]["net"]
                if got != want:
                    mismatches.append({"book": f"{year} {fam}-{xv}",
                                       "csv": got, "memory": want})
    results["independent_resum"] = {"match": not mismatches, "mismatches": mismatches}
    assert not mismatches, f"re-sum mismatch: {mismatches}"

    with open(WS / "orb_trend_v1_results.json", "w") as f:
        json.dump(results, f, indent=1)
    print(json.dumps({"resum_match": True,
                      "nov5_triggered": cf["triggered"],
                      "nov5_totals": cf["totals"]}, indent=1))
    for year in ("2025", "2026"):
        for k, b in results["years"][year]["books"].items():
            print(year, k, "trades", b["trades"], "net", b["net"],
                  "flip", b["placebo_flipped"]["net"], "shift",
                  b["placebo_shifted"]["net"], "H1", b["halves"]["H1_Jan_May"],
                  "H2", b["halves"]["H2_Jun_Oct"], "exT3", b["ex_top3"],
                  "GATE", "PASS" if b["gate"]["PASS"] else "FAIL")


if __name__ == "__main__":
    main()
