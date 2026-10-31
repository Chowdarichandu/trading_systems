"""Run 1: Day Trader skill's OWN entries, Bank Nifty spot cash.

PROPRIETARY WORKING FILE for Chandu only. Do not publish or share outside
Chandu's workspace. Rules below are provisional translations of the skill
doc's pattern names into fixed, testable definitions, because the skill
doc itself does not give numeric thresholds for flags / oversold bounces.
Each definition is labelled PROVISIONAL in the report; none is Chandu's
v4 rule, and none is presented as a proven edge.

Patterns (one trade per day, earliest signal wins):
- OR breakout / breakdown (skill scanner): first 5-min close beyond ORH
  (long) or below ORL (short) after 09:30, up to 11:30.
- Flag (skill scanner): after 09:30, first run of 3 consecutive 5-min
  candles each with high-low range <= 0.30% of close and total
  (max high - min low) <= 0.50% of close; signal = next candle closing
  above the flag high (long) or below the flag low (short), up to 14:30.
- Oversold bounce (skill scanner): RSI(14, Wilder) on 5-min closes,
  computed from 09:15, below 30 at the previous candle's close, and the
  current candle closes above the previous candle's high, up to 14:30.
  RSI is computed on closes only; no volume filter is used.

Exit (skill exit planner, provisional, same as the v4 cash run so that
Run 1 vs Run 2 compares ENTRY, not exit): signal candle low (long) /
high (short) as stop, stop_scale * signal distance, target =
target_ratio * stop distance, square-off at 15:10, stop priority if
both stop and target are hit in one candle. 100 shares provisional,
Rs 40/trade assumed cost.

Tuning design (pre-stated, in this file before results):
- Tune period Jan-Jun 2026, validate period Jul-Oct 2026, October
  reported as context only and never used to pick a candidate.
- Skill candidate rule: highest Jan-Jun net among target_ratio
  (1, 2, 3) x stop_scale (0.5, 1, 1.5) with all three patterns,
  provided trades >= 20. Trades/week is reported, not used to
  filter the candidate, because X's 2-3/week is a PORTFOLIO total,
  not a single-instrument rule.
- Pattern ablation (OR only, OR+flag, OR+oversold, all) is reported
  on Jan-Jun only, as sensitivity, not as a candidate.
"""
import sys
sys.path.insert(0, "/home/hatch/workspace/trading")
from daytrader_cash_tuning import load_data, metrics


def rsi_wilder(closes, period=14):
    rsis = [None] * len(closes)
    if len(closes) <= period:
        return rsis
    gains, losses = [], []
    for i in range(1, period + 1):
        d = closes[i] - closes[i - 1]
        gains.append(max(d, 0.0)); losses.append(max(-d, 0.0))
    ag, al = sum(gains) / period, sum(losses) / period
    rsis[period] = 100 - 100 / (1 + ag / al) if al else 100.0
    for i in range(period + 1, len(closes)):
        d = closes[i] - closes[i - 1]
        ag = (ag * (period - 1) + max(d, 0.0)) / period
        al = (al * (period - 1) + max(-d, 0.0)) / period
        rsis[i] = 100 - 100 / (1 + ag / al) if al else 100.0
    return rsis


def find_skill_signal(raw, patterns):
    or_c = [c for c in raw if c["time"] < "09:30"]
    if not or_c:
        return None, None, None
    orh = max(c["high"] for c in or_c); orl = min(c["low"] for c in or_c)
    candles = [c for c in raw if c["time"] >= "09:30"]
    closes = [c["close"] for c in raw]
    rsis = rsi_wilder(closes)
    raw_index = {id(c): i for i, c in enumerate(raw)}
    # OR pattern, up to 11:30.
    if "or" in patterns:
        for c in candles:
            if c["time"] > "11:30":
                break
            if c["close"] > orh:
                return "or_breakout", "CE", c
            if c["close"] < orl:
                return "or_breakdown", "PE", c
    # Flag and oversold are checked in candle order from 09:30; earliest wins
    # if OR did not already fire (OR loop above returns on first hit, so
    # reaching here means no OR signal before 11:30; flag/oversold may fire
    # earlier in the day than an OR signal after 11:30 is excluded by design).
    for i, c in enumerate(candles):
        if c["time"] > "14:30":
            break
        if "flag" in patterns and i >= 3:
            w = candles[i - 3:i]
            if all((x["high"] - x["low"]) <= 0.0030 * x["close"] for x in w) and \
               (max(x["high"] for x in w) - min(x["low"] for x in w)) <= 0.0050 * c["close"]:
                # Signal is the candle AFTER the flag window; check it now if it is c.
                # (Window is candles[i-3:i], so c is the first post-flag candle.)
                fh, fl = max(x["high"] for x in w), min(x["low"] for x in w)
                if c["close"] > fh:
                    return "flag_breakout", "CE", c
                if c["close"] < fl:
                    return "flag_breakdown", "PE", c
        if "oversold" in patterns and i >= 1:
            ri = raw_index[id(c)]
            if ri >= 1 and rsis[ri - 1] is not None and rsis[ri - 1] < 30 and c["close"] > candles[i - 1]["high"]:
                return "oversold_bounce", "CE", c
    return None, None, None


def run_skill(days, target_ratio, stop_scale, patterns, lo, hi):
    trades, ndays = [], 0
    for ds in sorted(days):
        if not (lo <= ds <= hi):
            continue
        prev, raw = days[ds]
        candles = [c for c in raw if c["time"] >= "09:30"]
        if not candles:
            continue
        ndays += 1
        setup, direction, sig = find_skill_signal(raw, patterns)
        if setup is None:
            continue
        sig_idx = next(i for i, c in enumerate(candles) if c["timestamp"] == sig["timestamp"])
        if sig_idx + 1 >= len(candles):
            continue
        entry = float(candles[sig_idx + 1]["open"])
        if direction == "CE":
            stop = entry - stop_scale * (entry - float(sig["low"]))
            target = entry + target_ratio * (entry - stop)
        else:
            stop = entry + stop_scale * (float(sig["high"]) - entry)
            target = entry - target_ratio * (stop - entry)
        if entry == stop:
            continue
        exit_reason = exit_price = exit_time = None
        for c in candles[sig_idx + 1:]:
            high, low, close, t = float(c["high"]), float(c["low"]), float(c["close"]), c["time"]
            if direction == "CE":
                if low <= stop:
                    exit_reason, exit_price, exit_time = "stop", stop, c["timestamp"]; break
                if high >= target:
                    exit_reason, exit_price, exit_time = "target", target, c["timestamp"]; break
            else:
                if high >= stop:
                    exit_reason, exit_price, exit_time = "stop", stop, c["timestamp"]; break
                if low <= target:
                    exit_reason, exit_price, exit_time = "target", target, c["timestamp"]; break
            if t == "15:10":
                exit_reason, exit_price, exit_time = "square_off", close, c["timestamp"]; break
        if exit_reason is None:
            c = candles[-1]
            exit_reason, exit_price, exit_time = "square_off", float(c["close"]), c["timestamp"]
        d = 1 if direction == "CE" else -1
        trades.append({"date": ds, "setup": setup, "direction": direction, "entry": entry,
                       "stop": stop, "target": target, "exit_reason": exit_reason,
                       "exit_price": exit_price, "net_rs": d * (exit_price - entry) * 100 - 40.0})
    return ndays, trades


def main():
    days = load_data()
    print(f"Loaded {len(days)} days {min(days)}..{max(days)}")
    periods = {"Jan-Jun (tune)": ("2026-01-01", "2026-06-30"),
               "Jul-Oct (validate)": ("2026-07-01", "2026-10-27"),
               "Jan-Oct": ("2026-01-01", "2026-10-27"),
               "Oct only (context)": ("2026-10-01", "2026-10-27")}
    for plabel, (lo, hi) in periods.items():
        nd, tr = run_skill(days, 2.0, 1.0, ("or", "flag", "oversold"), lo, hi)
        m = metrics(nd, tr)
        print(f"SKILL-ALL [{plabel}] days={nd} trades={m['trades']} T={m['targets']} S={m['stops']} SQ={m['square_offs']} "
              f"win={m['win_rate_pct']}% net={m['net_rs']} exp={m['expectancy_rs']} DD={m['max_drawdown_rs']} tpw={m['trades_per_week']}", flush=True)
        if plabel == "Oct only (context)":
            for t in tr:
                print("  OCT-TRADE", t, flush=True)
    # Pattern ablation, tune period only.
    for pats in [("or",), ("or", "flag"), ("or", "oversold"), ("or", "flag", "oversold")]:
        nd, tr = run_skill(days, 2.0, 1.0, pats, "2026-01-01", "2026-06-30")
        m = metrics(nd, tr)
        print(f"ABLATION {pats} Jan-Jun: trades={m['trades']} T={m['targets']} S={m['stops']} win={m['win_rate_pct']}% "
              f"net={m['net_rs']} DD={m['max_drawdown_rs']} tpw={m['trades_per_week']}", flush=True)
    # Grid, tune period only.
    grid = []
    for ratio in (1.0, 2.0, 3.0):
        for ss in (0.5, 1.0, 1.5):
            nd, tr = run_skill(days, ratio, ss, ("or", "flag", "oversold"), "2026-01-01", "2026-06-30")
            m = metrics(nd, tr)
            grid.append({"target_ratio": ratio, "stop_scale": ss, **m})
            print(f"SKILL-GRID ratio={ratio} stop_scale={ss} trades={m['trades']} net={m['net_rs']} win={m['win_rate_pct']}% DD={m['max_drawdown_rs']} tpw={m['trades_per_week']}", flush=True)
    cand = max((g for g in grid if g["trades"] >= 20), key=lambda g: g["net_rs"])
    print("SKILL-CANDIDATE", cand, flush=True)
    for plabel, (lo, hi) in periods.items():
        nd, tr = run_skill(days, cand["target_ratio"], cand["stop_scale"], ("or", "flag", "oversold"), lo, hi)
        m = metrics(nd, tr)
        print(f"SKILL-CANDIDATE [{plabel}] trades={m['trades']} T={m['targets']} S={m['stops']} win={m['win_rate_pct']}% "
              f"net={m['net_rs']} exp={m['expectancy_rs']} DD={m['max_drawdown_rs']} tpw={m['trades_per_week']}", flush=True)
    import pandas as pd, os
    pd.DataFrame(grid).to_csv(os.path.expanduser("~/workspace/trading/daytrader_skill_tuning_grid_janjun.csv"), index=False)


if __name__ == "__main__":
    main()
