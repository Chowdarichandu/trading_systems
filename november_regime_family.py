#!/usr/bin/env python3
"""NOVEMBER REGIME FIX — Phase D: REGIME-REV v1 (frozen in
november_regime_fix_2026-11-14.md BEFORE this run's results).

Spec (both indices, identical; only the index's own Q3 |gap|
constant and strike step/lot differ — the frozen definition applied
to the index's own distribution, not per-index tuning):
  morning = spot bars 09:15..10:55; O = 09:15 open, C11 = 10:55
  close, H/L = morning high/low, M = (H+L)/2, dir = sign(C11-O).
  gap% = (O - prev session close)/prev close * 100.
  REGIME MORNING: |gap%| >= Q3 (Bank 0.586 / Nifty 0.574) OR
  |(C11-O)/O*100| >= 0.7, and dir != 0. All known at 11:00.
  CONFIRMATION: first spot bar in [11:00, 15:05] whose CLOSE crosses
  M against the morning direction (up-morning: close < M;
  down-morning: close > M).
  ENTRY at that bar's close; side = reversal side (up -> PE,
  down -> CE); strike = ATM (Bank step 100 / Nifty step 50) to the
  confirmation bar's spot close; contract = in-force monthly expiry
  (OI dataset's expiry column).
  EXITS from the bar AFTER the confirmation bar (the fill is at its
  close): stop -50 checked before target +90 per bar, fills at the
  level; else the 15:10 bar close. 1 lot; Rs 220/trade; BUYING only.
  Premium series must start <= 09:20 and contain the 15:10 bar,
  else the fired day is NC (counted, never estimated).
Placebos: P1 = identical logic on NON-regime mornings;
P2 = regime days, same confirmation event, MORNING side bought;
P3 = regime days, entry at the close 30 min after confirmation
(same contract as the real leg).
Local stores only — NO API calls anywhere in this script.
"""
import csv, json
from pathlib import Path
import pandas as pd

TR = Path.home() / "workspace/trading"
COST = 220.0
STOP, TARGET, SQ = 50.0, 90.0, "15:10"
CONF = {"BANKNIFTY": dict(lot=30, step=100, q3=0.586),
        "NIFTY": dict(lot=65, step=50, q3=0.574)}

# ---------------- spot (same store as Phase C) ----------------
def load_spot(sym, extra=None):
    s = pd.read_csv(TR / f"data/progressive/{sym}/spot_5m.csv")
    s["timestamp"] = pd.to_datetime(s["timestamp"]).dt.tz_localize(None)
    s = s[(s["timestamp"] >= "2026-01-01") & (s["timestamp"] <= "2026-10-31")]
    if extra:
        e = pd.read_csv(extra)
        e["timestamp"] = pd.to_datetime(e["timestamp"]).dt.tz_localize(None)
        s = pd.concat([s, e])
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

# ---------------- premium stores (local only) ----------------
R5H = TR / "round5_history"
_c5 = {}
def prem_bank_c5(exp, strike, typ, day):
    ck = (exp, strike, typ)
    if ck not in _c5:
        fn = R5H / f"C5_{exp}_{strike}{typ}.json"
        byd = {}
        if fn.exists():
            for r in json.loads(fn.read_text()):
                byd.setdefault(r[0], {})[r[1]] = (float(r[2]), float(r[3]),
                                                  float(r[4]), float(r[5]))
        _c5[ck] = byd
    return _c5[ck].get(day)

PREM_B = json.load(open(TR / "daily2leg/prem_bank.json"))
PREM_N = json.load(open(TR / "daily2leg/prem_nifty.json"))
PREM_NW = json.load(open(TR / "daily2leg/prem_nifty_weekly.json"))

def prem_store(idx, exp, strike, typ, day):
    """-> {time: (o,h,l,c)} or None. Local stores only."""
    if idx == "BANKNIFTY":
        b = prem_bank_c5(exp, strike, typ, day)
        if b:
            return b
    key = f"{exp}|{int(strike)}|{typ}"
    stores = (PREM_B,) if idx == "BANKNIFTY" else (PREM_NW, PREM_N)
    for st in stores:
        cd = st.get(key, {}).get(day)
        if cd:
            return {t: tuple(float(x) for x in v) for t, v in cd.items()}
    for folder in ("btst_data", "november_shadow_data",
                   "nifty_weekly_expiry_chain", "oi_buildup_data"):
        fn = TR / folder / f"candles_{idx}_{int(strike)}{typ}_{exp}_{day}.json"
        if fn.exists():
            body = json.loads(fn.read_text())
            cd = [c for c in ((body.get("data") or {}).get("candles") or [])
                  if c[0][:10] == day]
            if cd:
                return {c[0][11:16]: (float(c[1]), float(c[2]), float(c[3]),
                                      float(c[4])) for c in cd}
    return None

# ---------------- expiry maps ----------------
def expiry_map(fn):
    m = {}
    with open(TR / fn) as f:
        for r in csv.DictReader(f):
            m[r["date"]] = r["expiry"]
    return m
EXP = {"BANKNIFTY": expiry_map("oi_history/banknifty_daily_oi.csv"),
       "NIFTY": expiry_map("oi_history/nifty_daily_oi.csv")}
EXP["BANKNIFTY"].update({d: "2026-11-23" for d in
    ("2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05", "2026-11-06",
     "2026-11-09", "2026-11-11", "2026-11-12", "2026-11-13")})

# ---------------- family engine ----------------
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
    """Exits from the bar after conf_time; entry_px = fill (close)."""
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

def score_leg(idx, day, bars, mi, side, conf_time, conf_close, delay=False):
    cfg = CONF[idx]
    step = cfg["step"]
    strike = int(round(conf_close / step)) * step
    exp = EXP[idx].get(day)
    if not exp:
        return None, "no_expiry"
    prem = prem_store(idx, exp, strike, side, day)
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
    net = round((xpx - epx) * cfg["lot"] - COST, 2)
    return dict(date=day, side=side, strike=strike, expiry=exp,
                conf_time=conf_time, entry_time=et, entry=epx,
                exit=xpx, exit_time=xt, exit_reason=reason, net=net), None

def run_index(idx, spot_days, prev_close_chain, window_days):
    cfg = CONF[idx]
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
        if day not in window_days:
            continue
        mi = morning_info(bars)
        if mi is None:
            nc.append((day, "morning_incomplete")); continue
        if mi["dirn"] == 0 or gap is None:
            continue
        regime = abs(gap) >= cfg["q3"] or abs(mi["move_pct"]) >= 0.7
        ct, cc = confirmation(bars, mi)
        if ct is None:
            continue
        rev_side = "PE" if mi["dirn"] > 0 else "CE"
        morn_side = "CE" if mi["dirn"] > 0 else "PE"
        if regime:
            fired_regime += 1
            leg, why = score_leg(idx, day, bars, mi, rev_side, ct, cc)
            if leg: real.append(leg)
            else: nc.append((day, f"real:{why}"))
            leg2, _ = score_leg(idx, day, bars, mi, morn_side, ct, cc)
            if leg2: p2.append(leg2)
            leg3, _ = score_leg(idx, day, bars, mi, rev_side, ct, cc,
                                delay=True)
            if leg3: p3.append(leg3)
        else:
            fired_nonreg += 1
            leg1, why1 = score_leg(idx, day, bars, mi, rev_side, ct, cc)
            if leg1: p1.append(leg1)
            else: nc.append((day, f"p1:{why1}"))
    return dict(real=real, p1_nonregime=p1, p2_flip=p2, p3_delay=p3,
                nc=nc, fired_regime=fired_regime, fired_nonregime=fired_nonreg)

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

results = {}
# BANK Jan-Oct + November
bank_spot = load_spot("BANKNIFTY", TR / "data/banknifty-2026-11/spot_5m.csv")
bank_days = day_bars(bank_spot)
jo_days = {d for d in bank_days if d <= "2026-10-31"}
nov_days = {d for d in bank_days if d >= "2026-11-01"}
res = run_index("BANKNIFTY", bank_days, None, jo_days)
results["BANKNIFTY_janoct"] = {k: (stats(v) if isinstance(v, list) and v and isinstance(v[0], dict) and "net" in v[0] else v)
                               for k, v in res.items()}
results["BANKNIFTY_janoct"]["real_legs"] = res["real"]
results["BANKNIFTY_janoct"]["nc"] = res["nc"]
res_nov = run_index("BANKNIFTY", bank_days, None, nov_days)
results["BANKNIFTY_november"] = {k: (stats(v) if isinstance(v, list) and v and isinstance(v[0], dict) and "net" in v[0] else v)
                                 for k, v in res_nov.items()}
results["BANKNIFTY_november"]["real_legs"] = res_nov["real"]
results["BANKNIFTY_november"]["nc"] = res_nov["nc"]
# NIFTY Jan-Oct
nifty_spot = load_spot("NIFTY")
nifty_days = day_bars(nifty_spot)
res_n = run_index("NIFTY", nifty_days, None, {d for d in nifty_days if d <= "2026-10-31"})
results["NIFTY_janoct"] = {k: (stats(v) if isinstance(v, list) and v and isinstance(v[0], dict) and "net" in v[0] else v)
                           for k, v in res_n.items()}
results["NIFTY_janoct"]["real_legs"] = res_n["real"]
results["NIFTY_janoct"]["nc"] = res_n["nc"]

with open(TR / "november_regime_family_results.json", "w") as f:
    json.dump(results, f, indent=1, default=str)
with open(TR / "november_regime_family_trades.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["book", "date", "side", "strike", "expiry", "conf_time",
                "entry_time", "entry", "exit", "exit_time", "exit_reason", "net"])
    for book, key in (("BANK_real", "BANKNIFTY_janoct"),):
        for l in results[key]["real_legs"]:
            w.writerow([book] + [l[k] for k in ("date", "side", "strike", "expiry",
                        "conf_time", "entry_time", "entry", "exit", "exit_time",
                        "exit_reason", "net")])
    for l in results["NIFTY_janoct"]["real_legs"]:
        w.writerow(["NIFTY_real"] + [l[k] for k in ("date", "side", "strike", "expiry",
                    "conf_time", "entry_time", "entry", "exit", "exit_time",
                    "exit_reason", "net")])
    for l in results["BANKNIFTY_november"]["real_legs"]:
        w.writerow(["BANK_nov"] + [l[k] for k in ("date", "side", "strike", "expiry",
                    "conf_time", "entry_time", "entry", "exit", "exit_time",
                    "exit_reason", "net")])
for key in ("BANKNIFTY_janoct", "NIFTY_janoct", "BANKNIFTY_november"):
    r = results[key]
    print(key, "real:", r["real"], "| P1:", r["p1_nonregime"],
          "| P2:", r["p2_flip"], "| P3:", r["p3_delay"],
          "| fired_regime:", r["fired_regime"], "fired_nonregime:", r["fired_nonregime"],
          "| NC:", len(r["nc"]), r["nc"][:5])
print("FAMILY DONE")
