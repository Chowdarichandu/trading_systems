#!/usr/bin/env python3
"""SCENARIO-PROOFING ITEM 1 — Nifty REGIME-REV gate on rescued data.

The signal engine, exit replay, strike/expiry selection, stats and
gate legs are copied VERBATIM from november_regime_family.py (the
frozen Bank gate). The single, disclosed difference is the premium
DATA LAYER for Nifty, and it is a repair, not a rule change:

  The frozen prem_store consults daily2leg/prem_nifty_weekly.json
  before the fetched-candle folders. That store was built by
  daily2leg/fetch_weekly.py on a 10:00-15:15 grid (its book entered
  at 10:00), so every series in it starts at 10:00 and the frozen
  completeness rule (series must start <= 09:20) NC'd 33 of 38
  fired regime days even where the complete series had already
  been fetched into oi_buildup_data/ (round 1's cache) — the
  truncated store shadowed the complete one. This runner therefore
  prefers, among the SAME sources, a series that starts <= 09:20
  (the completeness property the frozen rule itself tests);
  score_leg's rules are untouched, and a day whose series still
  starts late is NC exactly as frozen.

Modes:
  --orig   : the untouched frozen prem_store (sanity — must
             reproduce the regime report's 3 legs / +6,480.25).
  (default): rescued data layer.
Local stores only — no API calls. Paper only; nothing armed.
"""
import csv, json, sys
from pathlib import Path
import pandas as pd

TR = Path.home() / "workspace/trading"
COST = 220.0
STOP, TARGET, SQ = 50.0, 90.0, "15:10"
LOT, STEP, Q3 = 65, 50, 0.574
IDX = "NIFTY"

# ---------------- spot (identical to the frozen gate) -------------
def load_spot():
    s = pd.read_csv(TR / "data/progressive/NIFTY/spot_5m.csv")
    s["timestamp"] = pd.to_datetime(s["timestamp"]).dt.tz_localize(None)
    s = s[(s["timestamp"] >= "2026-01-01") & (s["timestamp"] <= "2026-10-31")]
    s["date"] = s["timestamp"].dt.strftime("%Y-%m-%d")
    s["time"] = s["timestamp"].dt.strftime("%H:%M")
    return s.sort_values("timestamp")


def day_bars(spot):
    out = {}
    for d, g in spot.groupby("date"):
        if len(g) >= 70:
            out[d] = {r.time: (float(r.open), float(r.high), float(r.low),
                               float(r.close)) for r in g.itertuples()}
    return out

# ---------------- premium stores ----------------------------------
PREM_N = json.load(open(TR / "daily2leg/prem_nifty.json"))
PREM_NW = json.load(open(TR / "daily2leg/prem_nifty_weekly.json"))


def _folder_series(exp, strike, typ, day):
    for folder in ("btst_data", "november_shadow_data",
                   "nifty_weekly_expiry_chain", "oi_buildup_data"):
        fn = TR / folder / f"candles_NIFTY_{int(strike)}{typ}_{exp}_{day}.json"
        if fn.exists():
            body = json.loads(fn.read_text())
            cd = [c for c in ((body.get("data") or {}).get("candles") or [])
                  if c[0][:10] == day]
            if cd:
                return {c[0][11:16]: (float(c[1]), float(c[2]),
                                      float(c[3]), float(c[4]))
                        for c in cd}
    return None


def prem_store_orig(exp, strike, typ, day):
    """The frozen gate's prem_store, NIFTY branch, verbatim logic."""
    key = f"{exp}|{int(strike)}|{typ}"
    for st in (PREM_NW, PREM_N):
        cd = st.get(key, {}).get(day)
        if cd:
            return {t: tuple(float(x) for x in v) for t, v in cd.items()}
    return _folder_series(exp, strike, typ, day)


def prem_store_rescue(exp, strike, typ, day):
    """Rescued data layer: among the same sources, prefer a series
    starting <= 09:20 (see module docstring)."""
    fetched = _folder_series(exp, strike, typ, day)
    stored = None
    key = f"{exp}|{int(strike)}|{typ}"
    for st in (PREM_NW, PREM_N):
        cd = st.get(key, {}).get(day)
        if cd:
            stored = {t: tuple(float(x) for x in v)
                      for t, v in cd.items()}
            break
    for cand in (fetched, stored):
        if cand and min(cand) <= "09:20":
            return cand
    return fetched if fetched is not None else stored


PREM_STORE = prem_store_orig

# ---------------- expiry map (frozen: OI dataset column) ----------
EXP = {}
with open(TR / "oi_history/nifty_daily_oi.csv") as f:
    for r in csv.DictReader(f):
        EXP[r["date"]] = r["expiry"]

# ---------------- family engine (verbatim) ------------------------
def morning_info(bars):
    win = [t for t in sorted(bars) if "09:15" <= t <= "10:55"]
    if len(win) < 21 or "09:15" not in bars or "10:55" not in bars:
        return None
    O = bars["09:15"][0]; C11 = bars["10:55"][3]
    H = max(bars[t][1] for t in win); L = min(bars[t][2] for t in win)
    return dict(O=O, C11=C11, H=H, L=L, M=(H + L) / 2.0,
                move_pct=(C11 - O) / O * 100.0,
                dirn=(1 if C11 > O else (-1 if C11 < O else 0)))


def confirmation(bars, mi):
    for t in sorted(bars):
        if "11:00" <= t <= "15:05":
            c = bars[t][3]
            if mi["dirn"] > 0 and c < mi["M"]:
                return t, c
            if mi["dirn"] < 0 and c > mi["M"]:
                return t, c
    return None, None


def replay_after(prem, conf_time, entry_px):
    times = [t for t in sorted(prem) if conf_time < t <= SQ]
    if SQ not in prem:
        return None
    stop, target = entry_px - STOP, entry_px + TARGET
    for t in times:
        o, h, l, c = prem[t]
        if l <= stop:
            return stop, t, "stop"
        if h >= target:
            return target, t, "target"
    return prem[SQ][3], SQ, "square_off"


def score_leg(day, side, conf_time, conf_close, delay=False):
    strike = int(round(conf_close / STEP)) * STEP
    exp = EXP.get(day)
    if not exp:
        return None, "no_expiry"
    prem = PREM_STORE(exp, strike, side, day)
    if not prem:
        return None, "no_premium_store"
    if min(prem) > "09:20":
        return None, "series_starts_after_0920"
    if SQ not in prem:
        return None, "no_1510_bar"
    et, epx = conf_time, None
    if delay:
        later = [t for t in sorted(prem) if t > conf_time]
        tgt = None
        for t in later:
            hh, mm = int(conf_time[:2]), int(conf_time[3:])
            want = hh * 60 + mm + 30
            if int(t[:2]) * 60 + int(t[3:]) >= want:
                tgt = t; break
        if tgt is None or tgt >= SQ:
            return None, "no_delay_bar"
        et, epx = tgt, prem[tgt][3]
    else:
        if conf_time not in prem:
            return None, "no_conf_bar_in_premium"
        epx = prem[conf_time][3]
    out = replay_after(prem, et, epx)
    if out is None:
        return None, "replay_none"
    xpx, xt, reason = out
    net = round((xpx - epx) * LOT - COST, 2)
    return dict(date=day, side=side, strike=strike, expiry=exp,
                conf_time=conf_time, entry_time=et, entry=epx,
                exit=xpx, exit_time=xt, exit_reason=reason, net=net), None


def run(spot_days):
    real, p1, p2, p3 = [], [], [], []
    nc = []
    fired_regime = fired_nonreg = 0
    prev_close = None
    for day in sorted(spot_days):
        bars = spot_days[day]
        first_open = bars[sorted(bars)[0]][0]
        gap = ((first_open - prev_close) / prev_close * 100
               if prev_close else None)
        prev_close = bars[sorted(bars)[-1]][3]
        mi = morning_info(bars)
        if mi is None:
            nc.append((day, "morning_incomplete")); continue
        if mi["dirn"] == 0 or gap is None:
            continue
        regime = abs(gap) >= Q3 or abs(mi["move_pct"]) >= 0.7
        ct, cc = confirmation(bars, mi)
        if ct is None:
            continue
        rev_side = "PE" if mi["dirn"] > 0 else "CE"
        morn_side = "CE" if mi["dirn"] > 0 else "PE"
        if regime:
            fired_regime += 1
            leg, why = score_leg(day, rev_side, ct, cc)
            if leg: real.append(leg)
            else: nc.append((day, f"real:{why}"))
            leg2, why2 = score_leg(day, morn_side, ct, cc)
            if leg2: p2.append(leg2)
            else: nc.append((day, f"p2:{why2}"))
            leg3, why3 = score_leg(day, rev_side, ct, cc, delay=True)
            if leg3: p3.append(leg3)
            else: nc.append((day, f"p3:{why3}"))
        else:
            fired_nonreg += 1
            leg1, why1 = score_leg(day, rev_side, ct, cc)
            if leg1: p1.append(leg1)
            else: nc.append((day, f"p1:{why1}"))
    return dict(real=real, p1=p1, p2=p2, p3=p3, nc=nc,
                fired_regime=fired_regime, fired_nonregime=fired_nonreg)


def stats(legs):
    if not legs:
        return dict(legs=0, total=0.0)
    byd = {}
    for l in legs:
        byd[l["date"]] = byd.get(l["date"], 0.0) + l["net"]
    tot = round(sum(l["net"] for l in legs), 2)
    h1 = round(sum(l["net"] for l in legs if l["date"][:7] <= "2026-05"), 2)
    h2 = round(sum(l["net"] for l in legs if l["date"][:7] >= "2026-06"), 2)
    ex3 = round(tot - sum(sorted((l["net"] for l in legs), reverse=True)[:3]), 2)
    months = {}
    for l in legs:
        months[l["date"][:7]] = round(months.get(l["date"][:7], 0.0) + l["net"], 2)
    return dict(legs=len(legs), total=tot, trade_days=len(byd),
                per_trade_day=round(tot / len(byd), 2) if byd else 0.0,
                per_leg=round(tot / len(legs), 2),
                win_rate=round(100.0 * sum(1 for l in legs if l["net"] > 0) / len(legs), 1),
                h1=h1, h2=h2, ex_top3=ex3, months=months,
                green_days=sum(1 for v in byd.values() if v > 0),
                red_days=sum(1 for v in byd.values() if v < 0))


def gate(res):
    real = stats(res["real"]); p1 = stats(res["p1"])
    p2 = stats(res["p2"]); p3 = stats(res["p3"])
    nc_real = sum(1 for _, w in res["nc"] if w.startswith("real:"))
    fired = res["fired_regime"]
    resum = round(sum(l["net"] for l in res["real"]), 2)
    legs_gate = {
        "total>0": real["total"] > 0,
        "halves>0": real.get("h1", 0) > 0 and real.get("h2", 0) > 0,
        "ex_top3>0": real.get("ex_top3", 0) > 0,
        "beats_P1_total": real["total"] > p1["total"],
        "beats_P1_per_leg": real.get("per_leg", 0) > p1.get("per_leg", 0),
        "beats_P2_total": real["total"] > p2["total"],
        "beats_P3_total": real["total"] > p3["total"],
        "nc<=5%_of_fired": (nc_real / fired <= 0.05) if fired else False,
        "resum_exact": resum == real["total"],
    }
    passed = all(legs_gate.values())
    return dict(real=real, p1_nonregime=p1, p2_flip=p2, p3_delay=p3,
                fired_regime=fired, fired_nonregime=res["fired_nonregime"],
                nc_real=nc_real, nc_all=res["nc"], gate_legs=legs_gate,
                verdict="PASS" if passed else "FAIL")


def main():
    global PREM_STORE
    mode = "orig" if "--orig" in sys.argv else "rescue"
    PREM_STORE = prem_store_orig if mode == "orig" else prem_store_rescue
    days = day_bars(load_spot())
    res = run(days)
    g = gate(res)
    print(f"MODE {mode}: fired_regime={g['fired_regime']} "
          f"fired_nonregime={g['fired_nonregime']}")
    print(" real:", g["real"])
    print(" P1:", g["p1_nonregime"], "\n P2:", g["p2_flip"],
          "\n P3:", g["p3_delay"])
    print(" gate:", g["gate_legs"], "->", g["verdict"],
          "| NC real:", g["nc_real"])
    if mode == "rescue":
        with open(TR / "scenario1_nifty_regimerev_trades.csv", "w",
                  newline="") as f:
            w = csv.writer(f)
            w.writerow(["book", "date", "side", "strike", "expiry",
                        "conf_time", "entry_time", "entry", "exit",
                        "exit_time", "exit_reason", "net"])
            for book, legs in (("real", res["real"]),
                               ("p1_nonregime", res["p1"]),
                               ("p2_flip", res["p2"]),
                               ("p3_delay", res["p3"])):
                for l in legs:
                    w.writerow([book] + [l[k] for k in (
                        "date", "side", "strike", "expiry", "conf_time",
                        "entry_time", "entry", "exit", "exit_time",
                        "exit_reason", "net")])
        from collections import Counter
        (TR / "scenario1_gate_results.json").write_text(json.dumps(
            dict(mode=mode, **{k: v for k, v in g.items()
                               if k != "nc_all"},
                 nc_counts=dict(Counter(w for _, w in res["nc"]))),
            indent=1, default=str))
    else:
        (TR / "scenario1_orig_check.json").write_text(json.dumps(
            dict(real_legs=res["real"],
                 nc_counts=__import__("collections").Counter(
                     w for _, w in res["nc"])), indent=1, default=str))
    return g


if __name__ == "__main__":
    main()
