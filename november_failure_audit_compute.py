#!/usr/bin/env python3
"""November failure audit computations. Read-only; prints JSON evidence."""
import json, math
import pandas as pd
import numpy as np
from pathlib import Path

TR = Path.home() / "workspace/trading"
NOV_DAYS = ["2026-11-02","2026-11-03","2026-11-04","2026-11-05","2026-11-06","2026-11-09","2026-11-11","2026-11-12"]
out = {}

def tmin(t):
    if pd.isna(t): return None
    t = str(t)[-8:-3] if len(str(t)) > 8 else str(t)
    h, m = t.split(":")[:2]
    return int(h) * 60 + int(m)

def bars_held(r):
    e, x = tmin(r.get("entry_time")), tmin(r.get("exit_time"))
    if e is None or x is None: return None
    return round((x - e) / 5)

# ---------- spot stores ----------
def load_spot(sym, extra=None):
    s = pd.read_csv(TR / f"data/progressive/{sym}/spot_5m.csv")
    s["timestamp"] = pd.to_datetime(s["timestamp"]).dt.tz_localize(None)
    s = s[(s["timestamp"] >= "2026-01-01") & (s["timestamp"] <= "2026-10-31")]
    if extra:
        e = pd.read_csv(extra)
        e["timestamp"] = pd.to_datetime(e["timestamp"]).dt.tz_localize(None)
        s = pd.concat([s, e])
    s["date"] = s["timestamp"].dt.normalize()
    s["time"] = s["timestamp"].dt.strftime("%H:%M")
    return s.sort_values("timestamp")

bank_spot = load_spot("BANKNIFTY", TR / "data/banknifty-2026-11/spot_5m.csv")
nifty_spot = load_spot("NIFTY")
bank_daily = pd.read_csv(TR / "data/progressive/BANKNIFTY/spot_daily.csv")
bank_daily["date"] = pd.to_datetime(bank_daily["date"]).dt.normalize()
bd11 = pd.read_csv(TR / "data/banknifty-2026-11/spot_daily.csv"); bd11["date"] = pd.to_datetime(bd11["date"]).dt.normalize()
bank_daily = pd.concat([bank_daily, bd11]).drop_duplicates("date").sort_values("date")
nifty_daily = pd.read_csv(TR / "data/progressive/NIFTY/spot_daily.csv")
nifty_daily["date"] = pd.to_datetime(nifty_daily["date"]).dt.normalize()

# ---------- H2 regime ----------
def regime(spot, daily, label):
    rows = []
    dmap = {d: g for d, g in spot.groupby("date") if len(g) >= 70}  # full sessions only (drops the 14-bar 2026-11-08 fragment)
    prev_close = None
    for d in sorted(dmap):
        g = dmap[d]
        o, h, l, c = g.iloc[0]["open"], g["high"].max(), g["low"].min(), g.iloc[-1]["close"]
        pclose = prev_close
        prev_close = c
        g11 = g[g["time"] <= "11:00"]
        c11 = g11.iloc[-1]["close"] if len(g11) else np.nan
        morn = c11 - o
        after = g[g["time"] > "11:00"]
        rev = False
        if len(after) and not np.isnan(c11) and morn != 0:
            if morn > 0:
                rev = (c11 - after["low"].min()) / c11 * 100 >= 0.7
            else:
                rev = (after["high"].max() - c11) / c11 * 100 >= 0.7
        rows.append(dict(date=str(d)[:10], range_pct=(h - l) / o * 100,
                         gap_pct=(o - pclose) / pclose * 100 if pclose else np.nan,
                         eff=abs(c - o) / (h - l) if h > l else 0, reversal=bool(rev)))
    df = pd.DataFrame(rows)
    jo = df[df.date <= "2026-10-31"]; nov = df[df.date >= "2026-11-01"]
    def summ(x):
        return dict(days=len(x), range_pct_med=round(x.range_pct.median(), 3),
                    gap_abs_med=round(x.gap_pct.abs().median(), 3),
                    trend_share=round((x.eff >= 0.5).mean(), 3),
                    reversal_share=round(x.reversal.mean(), 3))
    res = dict(janoct=summ(jo), nov=summ(nov), nov_days=nov.to_dict("records"))
    # percentile of November medians inside Jan-Oct daily distribution
    for k in ("range_pct", "gap_pct"):
        res[f"nov_med_pctile_{k}"] = round(float((jo[k] <= nov[k].median()).mean() * 100), 1)
    res["janoct_reversal_days_pct"] = round(float(jo.reversal.mean() * 100), 1)
    res["nov_reversal_days"] = int(nov.reversal.sum())
    out[f"regime_{label}"] = res

regime(bank_spot, bank_daily, "BANKNIFTY")
regime(nifty_spot, nifty_daily, "NIFTY")  # NIFTY nov will be empty (no stored bars) -> handled below

# ---------- November legs ----------
def read_log(fn, **kw):
    df = pd.read_csv(TR / fn, dtype=str)
    df["net"] = pd.to_numeric(df["net_inr"], errors="coerce")
    return df

nov = {}
df = read_log("november_paper_bank_log.csv"); nov["bank_legacy"] = df[df.channel == "PRIMARY"]
df = read_log("november_paper_nifty_log.csv"); nov["nifty_primary"] = df[df.channel == "PRIMARY"]
nov["bank_stack"] = read_log("november_shadow_stack_bank_log.csv")
nov["bank_v21"] = read_log("november_shadow_v21_bank_log.csv")
nov["bank_v22"] = read_log("november_shadow_v22_bank_log.csv")
nov["decs1"] = read_log("november_shadow_decs1_nifty_log.csv")
nov["skill_bank"] = read_log("november_shadow_skill_bank_log.csv")
nov["skill_nifty"] = read_log("november_shadow_skill_nifty_log.csv")

def leg_stats(df, cost=220):
    legs = df[df.net.notna()].copy()
    if len(legs) == 0:
        return dict(net=0.0, legs=0, traded_days=0)
    legs["bars"] = legs.apply(bars_held, axis=1)
    stops = legs[legs.exit_reason == "stop"]
    quick = stops[stops.bars <= 2]
    return dict(net=round(legs.net.sum(), 2), legs=int(len(legs)),
                traded_days=int(legs.date.nunique()),
                pe_net=round(legs[legs.direction == "PE"].net.sum(), 2), pe_legs=int((legs.direction == "PE").sum()),
                ce_net=round(legs[legs.direction == "CE"].net.sum(), 2), ce_legs=int((legs.direction == "CE").sum()),
                stops=int(len(stops)), quick_stops=int(len(quick)),
                quick_stop_legs=[f"{r.date} {r.direction} {r.strike} bars={int(r.bars)}" for r in quick.itertuples()],
                cost_drag=int(len(legs) * cost),
                gross=round(legs.net.sum() + len(legs) * cost, 2),
                detail=[f"{r.date} {r.direction} {r.strike} {r.entry_time}->{r.exit_time} {r.exit_reason} {r.net:+.0f} bars={r.bars}" for r in legs.itertuples()])

nov_stats = {}
for k, v in nov.items():
    nov_stats[k] = leg_stats(v)
# TUNED v1 / v2 November derived from DEC-S1 log (construction: v1 = DEC-S1 - B PE; v2 = - B PE - A CE - C CE)
d1 = nov["decs1"]; dlegs = d1[d1.net.notna()].copy()
def comp(r):
    s = str(r.system_source)
    return s.split()[-1] if s.startswith("DEC-S1") else "?"
dlegs["comp"] = dlegs.apply(comp, axis=1)
v1 = dlegs[~((dlegs.comp == "B") & (dlegs.direction == "PE"))]
v2 = v1[~(((v1.comp == "A") | (v1.comp == "C")) & (v1.direction == "CE"))]
nov_stats["tuned_v1"] = dict(net=round(v1.net.sum(), 2), legs=int(len(v1)), detail=[f"{r.date} {r.comp} {r.direction} {r.net:+.0f}" for r in v1.itertuples()])
nov_stats["tuned_v2"] = dict(net=round(v2.net.sum(), 2), legs=int(len(v2)))
out["november"] = nov_stats

# duplicate-leg census across index lines (same date+strike+direction+entry_time)
from collections import Counter
inst = []
for k in ("bank_legacy", "bank_stack", "bank_v21", "bank_v22", "skill_bank", "nifty_primary", "skill_nifty", "decs1"):
    legs = nov[k][nov[k].net.notna()]
    for r in legs.itertuples():
        inst.append((r.date, str(r.strike), r.direction, str(r.entry_time)))
cnt = Counter(inst)
out["nov_index_leg_instances"] = dict(total_instances=len(inst), distinct_trades=len(cnt),
                                      duplicated_instances=len(inst) - len(cnt),
                                      dup_detail={f"{k[0]} {k[2]} {k[1]} @{k[3]}": v for k, v in cnt.items() if v > 1})

# post-exit 60-min spot behaviour for stopped BANK legs (deduped)
bs = bank_spot.copy(); bs["tmin"] = bs["timestamp"].dt.hour * 60 + bs["timestamp"].dt.minute
seen = set(); post = []
for k in ("bank_legacy", "bank_stack", "bank_v21", "bank_v22", "skill_bank"):
    legs = nov[k][nov[k].net.notna()]
    for r in legs.itertuples():
        if r.exit_reason != "stop": continue
        key = (r.date, str(r.strike), r.direction, str(r.entry_time))
        if key in seen: continue
        seen.add(key)
        day = bs[bs.date == pd.Timestamp(r.date)]
        xt = tmin(r.exit_time)
        win = day[(day.tmin > xt) & (day.tmin <= xt + 60)]
        if not len(win): continue
        exit_spot_row = day[day.tmin <= xt]
        es = exit_spot_row.iloc[-1]["close"] if len(exit_spot_row) else np.nan
        adv = (win.high.max() - es) if r.direction == "PE" else (es - win.low.min())  # spot running further against the leg
        fav = (es - win.low.min()) if r.direction == "PE" else (win.high.max() - es)  # spot coming back in the leg's favour
        post.append(dict(leg=f"{r.date} {r.direction} {r.strike}", exit=r.exit_time,
                         adverse_next60=round(float(adv), 1), favourable_next60=round(float(fav), 1)))
out["bank_stopped_legs_next60"] = post

# ---------- Jan-Oct legs ----------
stack = pd.read_csv(TR / "bank_positive_tuning_2026-11-10_eve19_trades.csv")
stack["net"] = stack.net_inr
v21r = pd.read_csv(TR / "bank_engine_r8_v21_regen_trades.csv")
out["v21_regen_cols"] = list(v21r.columns)
out["v21_regen_sum"] = dict(rows=len(v21r), net=round(pd.to_numeric(v21r.filter(regex="net").iloc[:, 0], errors="coerce").sum(), 2)) if v21r.filter(regex="net").shape[1] else {}
np1 = pd.read_csv(TR / "nifty_next_phase_trades.csv"); np1["net"] = np1.net_inr
decs1_jo = np1.copy()
tv1 = decs1_jo[~((decs1_jo.component == "B") & (decs1_jo.direction == "PE"))]
tv2 = tv1[~(((tv1.component == "A") | (tv1.component == "C")) & (tv1.direction == "CE"))]
sb = pd.read_csv(TR / "stocks_engine_adoptedC_book2026_trades.csv")
out["stockbook_cols"] = list(sb.columns)

def jo_stats(df, datecol="date", cost=220, legs_have_times=True):
    df = df.copy(); df["m"] = df[datecol].astype(str).str[:7]
    months = {m: round(g.net.sum(), 2) for m, g in df.groupby("m") if "2026-0" in m or "2026-1" in m}
    months = {k: v for k, v in months.items() if k <= "2026-10"}
    daily = df.groupby(df[datecol].astype(str).str[:10]).net.sum()
    # worst 8-trading-day window using all calendar trading days present in spot? use rolling over sorted distinct dates of the book's own traded days + zero days approximated by months' trading days unknown -> use daily series over book dates only, flagged
    res = dict(total=round(df.net.sum(), 2), legs=int(len(df)), months=months,
               red_months=int(sum(1 for v in months.values() if v < 0)),
               worst_month=min(months.values()) if months else None,
               mean_month=round(np.mean(list(months.values())), 2) if months else None,
               pe_net=round(df[df.direction == "PE"].net.sum(), 2) if "direction" in df else None,
               ce_net=round(df[df.direction == "CE"].net.sum(), 2) if "direction" in df else None,
               pe_legs=int((df.direction == "PE").sum()) if "direction" in df else None,
               ce_legs=int((df.direction == "CE").sum()) if "direction" in df else None,
               traded_days=int(df[datecol].nunique()),
               cost_drag=int(len(df) * cost), gross=round(df.net.sum() + len(df) * cost, 2),
               daily_net_mean=round(float(daily.mean()), 2), daily_net_min=round(float(daily.min()), 2))
    if legs_have_times and "entry_time" in df and "exit_time" in df:
        df["bars"] = df.apply(bars_held, axis=1)
        st = df[df.exit_reason == "stop"]
        res["stops"] = int(len(st)); res["quick_stops"] = int((st.bars <= 2).sum())
        res["quick_stop_share"] = round(float((st.bars <= 2).mean()), 3) if len(st) else None
    return res

out["janoct_stack"] = jo_stats(stack)
out["janoct_decs1"] = jo_stats(decs1_jo)
out["janoct_tuned_v1"] = jo_stats(tv1)
out["janoct_tuned_v2"] = jo_stats(tv2)
# stock book: find net/date/dir columns
netcol = [c for c in sb.columns if "net" in c.lower()][0]
sb["net"] = pd.to_numeric(sb[netcol], errors="coerce")
datecol = [c for c in sb.columns if "date" in c.lower()][0]
out["janoct_stockbook"] = jo_stats(sb, datecol=datecol, cost=40, legs_have_times=False)

print(json.dumps(out, indent=1, default=str))
