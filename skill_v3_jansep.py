#!/usr/bin/env python3
"""Skill V3 (CE no-block) spot trades, index only, paper only.

Definition (frozen 2026-10-30, base S1 + V3 only):
- Data: ~/workspace/trading/data/progressive/{NIFTY,BANKNIFTY}/spot_5m.csv
  and spot_daily.csv (5-min, IST).
- OR = bars with time < 09:30 (09:15, 09:20, 09:25 bars);
  ORH = max high, ORL = min low of those bars.
- Raw signal = first 5-min close beyond OR (close > ORH = CE,
  close < ORL = PE) in window 09:30-11:30 inclusive.
- PDL = previous trading day's daily low (previous row of spot_daily.csv).
- S1 blocks, V3 change: CE bearish block REMOVED - a CE is taken on any
  bias day. The 09:30-PE rule is UNCHANGED: a 09:30 PE is taken ONLY if its
  close < PDL, else blocked and the day ends (no later signal).
- Spot exit (provisional, points x 100 shares - Rs 40, NOT an options-lot
  profit, NOT a futures profit): entry = next 5-min bar's open after the
  signal bar; stop = signal-bar low (CE) / high (PE);
  risk = |entry - stop|; if risk = 0, no trade; target = entry +/- 2 x risk;
  stop checked before target on every bar including the entry bar, using
  bar high/low breach (CE: low <= stop -> stop, high >= target -> target;
  PE: high >= stop -> stop, low <= target -> target); square-off at the
  15:10 bar close (stop/target checked on the 15:10 bar first, square-off
  only if neither is hit on it). Full-target = target exit only.
- No premiums, no stocks, no orders.
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

BASE = Path.home() / "workspace" / "trading" / "data" / "progressive"
INDICES = ["BANKNIFTY", "NIFTY"]


def load_index(idx):
    bars = defaultdict(list)  # date -> sorted list of dicts
    with open(BASE / idx / "spot_5m.csv", newline="") as f:
        for r in csv.DictReader(f):
            date, ts = r["timestamp"].split(" ")
            t = ts[:5]  # HH:MM (timestamps carry +05:30)
            bars[date].append(
                {
                    "time": t,
                    "open": float(r["open"]),
                    "high": float(r["high"]),
                    "low": float(r["low"]),
                    "close": float(r["close"]),
                }
            )
    for d in bars:
        bars[d].sort(key=lambda b: b["time"])
    daily = []  # sorted list of (date, high, low, close)
    with open(BASE / idx / "spot_daily.csv", newline="") as f:
        for r in csv.DictReader(f):
            daily.append(
                (r["date"], float(r["high"]), float(r["low"]), float(r["close"]))
            )
    daily.sort(key=lambda x: x[0])
    prev = {}
    for i in range(1, len(daily)):
        prev[daily[i][0]] = daily[i - 1]  # (prev_date, high, low, close)
    return bars, prev


def run_index(idx, start, end):
    bars_by_date, prev = load_index(idx)
    trades = []
    diag = defaultdict(int)
    for date in sorted(bars_by_date):
        if not (start <= date <= end):
            continue
        day = bars_by_date[date]
        by_time = {b["time"]: b for b in day}
        or_bars = [b for b in day if b["time"] < "09:30"]
        if len(or_bars) != 3:
            diag["or_bars_not_3"] += 1
            if not or_bars:
                continue
        orh = max(b["high"] for b in or_bars)
        orl = min(b["low"] for b in or_bars)
        if date not in prev:
            diag["no_prev_day"] += 1
            continue
        _pdate, _ph, pdl, _pc = prev[date]
        # Raw signal: first close beyond OR in 09:30-11:30 inclusive.
        sig = None
        sig_dir = None
        for b in day:
            if "09:30" <= b["time"] <= "11:30":
                if b["close"] > orh:
                    sig, sig_dir = b, "CE"
                    break
                if b["close"] < orl:
                    sig, sig_dir = b, "PE"
                    break
        if sig is None:
            diag["no_signal"] += 1
            continue
        # V3: CE bearish block removed. 09:30-PE rule unchanged.
        if sig_dir == "PE" and sig["time"] == "09:30" and not (sig["close"] < pdl):
            diag["blocked_0930_pe"] += 1
            continue
        # Entry: next 5-min bar after the signal bar.
        idx_pos = next(i for i, b in enumerate(day) if b["time"] == sig["time"])
        if idx_pos + 1 >= len(day):
            diag["no_entry_bar"] += 1
            continue
        entry_bar = day[idx_pos + 1]
        entry = entry_bar["open"]
        entry_time = entry_bar["time"]
        stop = sig["low"] if sig_dir == "CE" else sig["high"]
        risk = abs(entry - stop)
        if risk == 0:
            diag["risk_zero"] += 1
            continue
        target = entry + 2 * risk if sig_dir == "CE" else entry - 2 * risk
        # Exit scan: entry bar through 15:10 bar inclusive, stop before target.
        exit_spot, exit_time, exit_reason = None, None, None
        for b in day[idx_pos + 1:]:
            if b["time"] > "15:10":
                break
            if sig_dir == "CE":
                if b["low"] <= stop:
                    exit_spot, exit_time, exit_reason = stop, b["time"], "stop"
                    break
                if b["high"] >= target:
                    exit_spot, exit_time, exit_reason = target, b["time"], "target"
                    break
            else:
                if b["high"] >= stop:
                    exit_spot, exit_time, exit_reason = stop, b["time"], "stop"
                    break
                if b["low"] <= target:
                    exit_spot, exit_time, exit_reason = target, b["time"], "target"
                    break
            if b["time"] == "15:10":
                exit_spot, exit_time, exit_reason = b["close"], b["time"], "square_off"
                break
        if exit_spot is None:
            diag["no_exit_bar"] += 1
            continue
        pts = (exit_spot - entry) if sig_dir == "CE" else (entry - exit_spot)
        net = round(pts * 100 - 40, 2)
        trades.append(
            {
                "index": idx,
                "date": date,
                "direction": sig_dir,
                "signal_time": sig["time"],
                "entry_time": entry_time,
                "entry_spot": f"{entry:.2f}",
                "stop_spot": f"{stop:.2f}",
                "target_spot": f"{target:.2f}",
                "exit_time": exit_time,
                "exit_spot": f"{exit_spot:.2f}",
                "exit_reason": exit_reason,
                "spot_net_rs": f"{net:.2f}",
                "full_target": 1 if exit_reason == "target" else 0,
            }
        )
    return trades, diag


def main():
    out_path = Path.home() / "workspace" / "trading" / "index_options_U1_skillV3_jansep_spot.csv"
    oct_path = Path("/tmp/skillV3_oct_validation.csv")
    cols = [
        "index", "date", "direction", "signal_time", "entry_time", "entry_spot",
        "stop_spot", "target_spot", "exit_time", "exit_spot", "exit_reason",
        "spot_net_rs", "full_target",
    ]
    all_trades, all_diag = [], {}
    for idx in INDICES:
        t, d = run_index(idx, "2026-01-01", "2026-09-30")
        all_trades.extend(t)
        all_diag[idx] = dict(d)
    all_trades.sort(key=lambda r: (r["index"], r["date"]))
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(all_trades)
    # Validation: same code on October 2026.
    oct_trades = []
    for idx in INDICES:
        t, _ = run_index(idx, "2026-10-01", "2026-10-31")
        oct_trades.extend(t)
    oct_trades.sort(key=lambda r: (r["index"], r["date"]))
    with open(oct_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(oct_trades)
    print(f"jansep trades: {len(all_trades)} -> {out_path}")
    print(f"oct trades (full month in data): {len(oct_trades)} -> {oct_path}")
    print(f"jansep diag: {all_diag}")
    for idx in INDICES:
        sub = [t for t in all_trades if t["index"] == idx]
        net = sum(float(t["spot_net_rs"]) for t in sub)
        ft = sum(t["full_target"] for t in sub)
        print(f"{idx}: n={len(sub)} net={net:.2f} full_target={ft} "
              f"({100*ft/len(sub):.1f}% of trades)" if sub else f"{idx}: n=0")


if __name__ == "__main__":
    main()
