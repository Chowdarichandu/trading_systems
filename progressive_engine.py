"""Progressive engine: V4 cash + Day Trader skill cash, per instrument-month.
Paper only, no orders. Provisional cash rules (NOT Chandu's rules):
100 shares, Rs 40/trade, stop = signal-candle low/high, target = 2x stop
distance, square-off 15:10, one trade/instrument/day, thresholds scaled by
prev-close (V4 scale = prev_close/55000 in daytrader_cash_backtest.py;
skill uses same exit, stop_scale 1.0, target_ratio 2.0), Setup 1 skipped.
Reads ~/workspace/trading/data/progressive/<SYMBOL>/spot_5m.csv + spot_daily.csv
"""
import argparse, math, os, sys
sys.path.insert(0, "/home/hatch/workspace/trading")
import pandas as pd
from daytrader_cash_backtest import find_signal, run_day, bias_of
from daytrader_skill_run import find_skill_signal

BASE = os.path.expanduser("~/workspace/trading/data/progressive")
QTY, COST = 100, 40.0

def load(symbol):
    spot = pd.read_csv(os.path.join(BASE, symbol, "spot_5m.csv"), parse_dates=["timestamp"])
    daily = pd.read_csv(os.path.join(BASE, symbol, "spot_daily.csv"), parse_dates=["date"])
    spot["timestamp"] = pd.to_datetime(spot["timestamp"]).dt.tz_localize(None)
    daily["date"] = pd.to_datetime(daily["date"]).dt.tz_localize(None).dt.normalize()
    spot["date"] = spot["timestamp"].dt.normalize()
    spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
    return spot.sort_values("timestamp"), daily.sort_values("date")

def run_skill_day(raw, prev):
    # raw: list of dicts for the day, in time order, with timestamp/time/open/high/low/close
    setup, direction, sig = find_skill_signal(raw, ("or","flag","oversold"))
    if setup is None:
        return None
    candles = [c for c in raw if c["time"] >= "09:30"]
    sig_idx = next((i for i,c in enumerate(candles) if c["timestamp"]==sig["timestamp"]), None)
    if sig_idx is None or sig_idx+1 >= len(candles):
        return None
    entry = float(candles[sig_idx+1]["open"])
    if direction=="CE":
        stop = entry - 1.0*(entry-float(sig["low"])); target = entry + 2.0*(entry-stop)
    else:
        stop = entry + 1.0*(float(sig["high"])-entry); target = entry - 2.0*(stop-entry)
    if entry==stop:
        return None
    exit_reason=exit_price=exit_time=None
    for c in candles[sig_idx+1:]:
        if direction=="CE":
            if float(c["low"])<=stop: exit_reason,exit_price,exit_time="stop",stop,c["timestamp"]; break
            if float(c["high"])>=target: exit_reason,exit_price,exit_time="target",target,c["timestamp"]; break
        else:
            if float(c["high"])>=stop: exit_reason,exit_price,exit_time="stop",stop,c["timestamp"]; break
            if float(c["low"])<=target: exit_reason,exit_price,exit_time="target",target,c["timestamp"]; break
        if c["time"]=="15:10": exit_reason,exit_price,exit_time="square_off",float(c["close"]),c["timestamp"]; break
    if exit_reason is None:
        c=candles[-1]; exit_reason,exit_price,exit_time="square_off",float(c["close"]),c["timestamp"]
    d=1 if direction=="CE" else -1
    return {"setup":setup,"direction":direction,"entry":entry,"stop":stop,"target":target,
            "exit_reason":exit_reason,"exit_price":exit_price,"exit_time":exit_time,
            "net_rs": d*(exit_price-entry)*QTY-COST}

def run_month(symbol, year, month):
    spot, daily = load(symbol)
    daily_list = daily.to_dict("records")
    # map date -> prev daily
    out_v4, out_skill = [], []
    ndays=0
    for i, y in enumerate(daily_list):
        d = y["date"]
        if d.year!=year or d.month!=month or i==0:
            continue
        day_spot = spot[spot["date"]==d]
        if day_spot.empty:
            continue
        ndays+=1
        prev = daily_list[i-1]
        pdh,pdc,pdl = float(prev["high"]),float(prev["close"]),float(prev["low"])
        bias, cs = bias_of(prev)
        scale = pdc/55000.0 if pdc else 1.0
        r = run_day(day_spot, pdh,pdc,pdl,bias,scale,QTY,COST)
        if r["exit_reason"] in ("target","stop","square_off"):
            out_v4.append({"symbol":symbol,"date":d.date().isoformat(),"setup":r["setup"],"direction":r["direction"],
                           "exit_reason":r["exit_reason"],"net_rs":round(float(r["net_rs"]),2)})
        raw = day_spot.to_dict("records")
        # find_skill_signal expects timestamp as string-like comparable; use original records
        # Convert timestamp to string for matching inside that function (it only compares equality)
        for c in raw:
            c["timestamp"]=str(c["timestamp"])
        sk = run_skill_day(raw, prev)
        if sk:
            out_skill.append({"symbol":symbol,"date":d.date().isoformat(),**sk, "net_rs":round(float(sk["net_rs"]),2)})
    return ndays, out_v4, out_skill

def metrics(ndays, trades):
    if not trades:
        return {"days":ndays,"trades":0,"targets":0,"stops":0,"square_offs":0,"win_rate_pct":0.0,"net_rs":0.0,"expectancy_rs":0.0,"max_drawdown_rs":0.0,"trades_per_week":0.0}
    net=sum(t["net_rs"] for t in trades); cum=peak=dd=0.0
    for t in trades:
        cum+=t["net_rs"]; peak=max(peak,cum); dd=max(dd,peak-cum)
    return {"days":ndays,"trades":len(trades),"targets":sum(1 for t in trades if t["exit_reason"]=="target"),
            "stops":sum(1 for t in trades if t["exit_reason"]=="stop"),
            "square_offs":sum(1 for t in trades if t["exit_reason"]=="square_off"),
            "win_rate_pct":round(100*sum(1 for t in trades if t["exit_reason"]=="target")/len(trades),1),
            "net_rs":round(net,2),"expectancy_rs":round(net/len(trades),2),"max_drawdown_rs":round(dd,2),
            "trades_per_week":round(len(trades)/(ndays/5) if ndays else 0,2)}

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--symbol",required=True); ap.add_argument("--year",type=int,required=True); ap.add_argument("--month",type=int,required=True)
    a=ap.parse_args()
    nd, v, s = run_month(a.symbol, a.year, a.month)
    print(f"{a.symbol} {a.year}-{a.month:02d} days={nd}")
    print(" V4", metrics(nd, v))
    print(" SKILL", metrics(nd, s))
