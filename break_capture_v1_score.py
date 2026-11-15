#!/usr/bin/env python3
"""BREAK-CAPTURE v1 (2026-11-08) — two index-options capture variants for the
opening-range break pattern, scored with the FULL controls gate in one run.
Research/backtest only. Nothing armed; no frozen book, log, shadow or cron
touched. Real money Rs 0; paper only.

================ PRE-REGISTERED SPEC (frozen before scoring) ================
SIGNAL (per index, per day; definitions identical to the probability study
break_trend_probability_2026-11-08.py, data = daily2leg/spot.json 5-min spot):
- OR = bars 09:15/09:20/09:25; ORH/ORL = their high/low.
- BREAK bar: first bar starting >=09:30 whose CLOSE is beyond ORH (up) or
  ORL (down). Entry signal time = break bar close.
- Each direction is its own sequence; max one sequence per direction per day.
- Days with <70 spot bars excluded and counted (study rule).

INSTRUMENT & CONVENTIONS (identical to the v21 / DEC-S1 / daily2leg scorers):
- ATM option on the break side (CE up / PE down); strike = atm() of the
  daily2leg scorer applied to the signal bar's spot close (re-entries: the
  re-break bar's close; Variant H: the check bar's close; SHIFTED placebo:
  the close of the bar immediately before the shifted fill bar).
- Bank Nifty MONTHLY expiry family, Nifty MONTHLY expiry family;
  expiry = first listed monthly expiry >= trade date (daily2leg EXPIRIES).
- Premium stores: daily2leg/prem_bank.json, daily2leg/prem_nifty.json only.
- Entry fill = premium OPEN of the next bar after the signal bar.
- Cost Rs 220/trade round trip. Lots: BANKNIFTY 30, NIFTY 65.
- Premium bars missing for a leg -> NOT_COMPUTED, counted and listed,
  never estimated. A leg needs every premium bar from entry bar through
  exit bar inclusive (entry open, all closes for the stop check, exit fill).

VARIANT R — RE-ENTRY (second-act capture):
- Enter on the break (next bar open).
- Exit at the first of: (i) spot FAILURE CLOSE after entry (5-min close back
  inside the range: <=ORH for CE / >=ORL for PE) -> exit at next bar open;
  (ii) premium hard stop -50 points, close-based (a premium CLOSE
  <= entry-50) -> exit at next bar open; (iii) square-off 15:10 (premium
  CLOSE of the 15:10 bar, the established convention).
- If stop and failure trigger on the same bar close, the exit is treated as
  the STOP exit (fill identical; consequence: no re-entry). Stated here,
  applied uniformly.
- RE-ENTRY only after a failure-close exit: if spot closes beyond the SAME
  range level again the same day, re-enter (next bar open), same exits.
  Max 2 re-entries per direction per day (3 legs max). A hard-stop exit
  ends the sequence (owner's rule: re-entry only on signal recurrence after
  a LEG stop of the failure kind — hard stop does not re-enter).
- No fixed premium target.

VARIANT H — HOLD-60 DELAYED ENTRY:
- No entry at the break. Check bar = the bar that CLOSES 60 minutes after
  the break bar's start (starts at break_start+55). At its close: enter
  (next bar open) only if no failure close occurred on any bar since the
  break AND the check bar's own close is still beyond the range level.
  Otherwise no trade for that direction that day (first break only; a later
  fresh break in the same direction does not re-qualify).
- Exits identical to R. No re-entry in H.
- Note: the study's HOLD-60 flag also required no failure close on the bar
  starting at break+60 (the entry bar here); v1 follows the task spec —
  qualification is decided at the check bar's close, and a failure close on
  the entry bar itself exits the position under the normal exit rules.

DAY GUARD (both variants): -Rs 3,000 day-loss cap per index. CONVENTION
USED (identical across variants and placebos): entries fill in time order;
before an entry fills, at its signal bar's close, compute the day P&L as
(sum of nets of legs already closed) + (open legs marked at their premium
close on that signal bar, valued (close-entry)*lot - 220 each). If that
marked P&L <= -3,000, the entry is blocked and the cap LATCHES — no further
entries that index-day in that book. Exits are never blocked.
NOTE: the owner's Rs 500 / Rs 1,000 day-profit ceilings are deliberately NOT
applied in this v1 — they would truncate the trend days this build exists
to capture. Flagged as an open layering question for December; not applied.

WINDOWS: Jan-Oct 2026 primary AND Jan-Oct 2025, reported separately per
index per variant, never pooled. Per-index verdicts always separate.
The designated premium stores contain NO 2025 trade days; every 2025 leg is
therefore NOT_COMPUTED by construction (counted, disclosed — never a zero).

PLACEBOS (per variant per index, independent books with own day caps):
- FLIPPED: identical signals/state machine, opposite option side.
- SHIFTED: every entry fill delayed +30 min (6 bars) from the correspond-
  ing real entry; strike = ATM at the close of the bar before the shifted
  fill; exit rules identical (for R, re-entries after the shifted first
  leg proceed from its own failure exits with fresh re-break signals).

GATE (per variant per index, 2026 primary):
1. Timing audit: entry fill bar strictly after signal bar; exit fill after
   exit-signal bar (square-off excepted: exit at the 15:10 close itself).
   Violations must be 0.
2. Variant net must beat BOTH placebos on 2026 net.
3. Halves Jan-May / Jun-Oct 2026 both positive.
4. Month table printed (all 10 months).
5. Ex-top-3 legs still positive.
6. Bleed: worst day, worst 3 consecutive active days, cap-hit days counted.
7. NC share of signal days <= 10%.
PASS = 2026 net > 0 AND halves > 0 AND beats both placebos AND ex-top-3 > 0
AND NC <= 10%. 2025 disclosed alongside; if a 2025 net existed and were
< -5,000 the verdict would be FAIL-DOUBLE. (Here the 2025 window is
NOT_COMPUTED window-wide — no 2025 net exists; disclosed, not zeroed.)
Anything else = FAIL with failed legs named. No variant surgery.

APPENDIX (not gated): both variants on November 2026 days Nov 2-6, from
workspace live-shadow data (spot: intraday snapshot files; premium:
prem stores' November entries + november_shadow_data/ + aggressive_data/
+ v4_options_oct_data/ candle files). Missing contract -> NC, never
estimated. Friday 2026-11-06 Bank reported explicitly.
===========================================================================
"""
import json, csv, glob, re
from pathlib import Path
from collections import defaultdict

TR = Path.home() / "workspace/trading"
D2 = TR / "daily2leg"
SPOT = json.load(open(D2 / "spot.json"))
PREM = {"BANKNIFTY": json.load(open(D2 / "prem_bank.json")),
        "NIFTY": json.load(open(D2 / "prem_nifty.json"))}
LOT = {"BANKNIFTY": 30, "NIFTY": 65}
STEP = {"BANKNIFTY": 100, "NIFTY": 50}
COST = 220.0
STOP_PTS = 50.0
DAY_CAP = -3000.0
SQ = "15:10"
MIN_BARS = 70
EXPIRIES = ["2026-01-27", "2026-02-24", "2026-03-30", "2026-04-28",
            "2026-05-26", "2026-06-30", "2026-07-28", "2026-08-25",
            "2026-09-29", "2026-10-27", "2026-11-23"]
GOALS_HF = Path.home() / ("workspace/goals/3-blue-line-bank-nifty-backtest/"
                          "hidden_files")

def tmin(t):
    h, m = t.split(":"); return int(h) * 60 + int(m)

def expiry_of(d):
    for e in EXPIRIES:
        if d <= e:
            return e
    return None

def atm(idx, s):
    step = STEP[idx]
    lo = int(s // step * step)
    return lo if (s - lo) <= (lo + step - s) else lo + step

def prem_day_main(idx, exp, strike, typ, d):
    """Designated stores only. Returns dict time->[O,H,L,C] or None."""
    if exp is None:
        return None
    return PREM[idx].get(f"{exp}|{int(strike)}|{typ}", {}).get(d)

# ---------------- November appendix data ----------------
def nov_spot(idx, day):
    """Latest (fullest) intraday snapshot for (idx, day) from the watcher
    files. Returns bars [[time,o,h,l,c], ...] or None."""
    tag = "bank" if idx == "BANKNIFTY" else "nifty"
    files = sorted(glob.glob(str(GOALS_HF / f"spot_{tag}_5m_{day}_*.json")))
    best = None
    for f in files:
        try:
            raw = json.load(open(f))
        except Exception:
            continue
        bars = [[c[0][11:16], float(c[1]), float(c[2]), float(c[3]),
                 float(c[4])] for c in raw]
        if best is None or len(bars) > len(best):
            best = bars
    return best

_nov_file_cache = {}
def prem_day_nov(idx, exp, strike, typ, d):
    """November premium: designated stores first, then live-shadow candle
    files in november_shadow_data/, aggressive_data/, v4_options_oct_data/."""
    cd = prem_day_main(idx, exp, strike, typ, d)
    if cd:
        return cd
    pats = [TR / "november_shadow_data" / f"candles_{idx}_{int(strike)}{typ}_{d}_{exp}.json",
            TR / "aggressive_data" / f"candles_{idx}_{int(strike)}{typ}_{d}_{exp}.json",
            TR / "aggressive_data" / f"candles_premium_{idx}_{int(strike)}{typ}_{d}_{exp}.json",
            TR / "v4_options_oct_data" / f"candles_{idx}_{int(strike)}{typ}_{d}_{exp}.json",
            TR / "v4_options_oct_data" / f"candles_premium_{idx}_{int(strike)}{typ}_{d}_{exp}.json"]
    for p in pats:
        if not p.exists():
            continue
        key = str(p)
        if key not in _nov_file_cache:
            try:
                data = json.loads(p.read_text()).get("data", {}).get("candles", [])
                _nov_file_cache[key] = data
            except Exception:
                _nov_file_cache[key] = []
        out = {}
        for c in _nov_file_cache[key]:
            if c[0][:10] == d:
                out[c[0][11:16]] = [float(c[1]), float(c[2]), float(c[3]),
                                    float(c[4])]
        if out:
            return out
    return None

# ---------------- simulation engine ----------------
class NC(Exception):
    def __init__(self, reason):
        self.reason = reason

def simulate(idx, day, bars, variant, mode, prem_fn):
    """One index-day, one variant, one book (mode in main/flip/shift).
    Returns (legs, nc_rows, info). legs: scored leg dicts for BOTH
    directions; a direction that hits missing premium data contributes one
    NC row and its legs are discarded (cap decisions during the day stand
    as simulated — documented convention)."""
    lot = LOT[idx]
    exp = expiry_of(day)
    or_bars = [b for b in bars if b[0] in ("09:15", "09:20", "09:25")]
    if len(or_bars) < 3:
        return [], [], {"no_or": True}
    orh = max(b[2] for b in or_bars); orl = min(b[3] for b in or_bars)
    times = [b[0] for b in bars]
    tidx = {t: i for i, t in enumerate(times)}
    if SQ not in tidx:
        return [], [], {"no_sq_bar": True}
    sq_i = tidx[SQ]
    first_i = next(i for i, b in enumerate(bars) if tmin(b[0]) >= tmin("09:30"))

    dirs = {}
    for dname, level, main_side in (("up", orh, "CE"), ("down", orl, "PE")):
        side = main_side if mode != "flip" else ("PE" if main_side == "CE" else "CE")
        dirs[dname] = dict(name=dname, level=level, side=side,
                           phase="seek", break_i=None, qual=None,
                           legs_done=0, open=None, pend_in=None,
                           pend_out=None, legs=[], nc=None,
                           first_signal_seen=False)
    closed_pnl = 0.0
    cap_latched = False
    cap_hit = False

    def beyond(d, close):
        return close > d["level"] if d["name"] == "up" else close < d["level"]

    def failed_close(d, close):
        return close <= d["level"] if d["name"] == "up" else close >= d["level"]

    def prem(strike, side):
        cd = prem_fn(idx, exp, strike, side, day)
        return cd

    def bar_prem(d, t):
        cd = d["open"]["cd"]
        if t not in cd:
            raise NC(f"premium bar {t} missing for {d['open']['strike']}"
                     f"{d['open']['side']} (needed open/close in span)")
        return cd[t]

    def mark_pnl(j):
        """Day marked P&L at bar j close: closed nets + open legs marked."""
        tot = closed_pnl
        for d in dirs.values():
            if d["open"] is not None:
                cd = d["open"]["cd"]
                t = times[j]
                if t not in cd:
                    raise NC(f"premium bar {t} missing for mark of "
                             f"{d['open']['strike']}{d['open']['side']}")
                tot += (cd[t][3] - d["open"]["entry_px"]) * lot - COST
        return tot

    def try_entry(d, sig_i, fill_i, strike_ref_close_i):
        """Cap-check at signal bar close, then register pending entry."""
        nonlocal cap_latched, cap_hit
        if cap_latched:
            d["phase"] = "done"; return
        mp = mark_pnl(sig_i)
        if mp <= DAY_CAP:
            cap_latched = True; cap_hit = True
            d["phase"] = "done"; return
        strike = atm(idx, bars[strike_ref_close_i][4])
        d["pend_in"] = dict(fill_i=fill_i, sig_i=sig_i, strike=strike)
        d["phase"] = "pend_in"

    j = first_i
    while j <= sq_i:
        t = times[j]
        # ---- 1) fills at bar j open: exits first, then entries ----
        for d in dirs.values():
            if d["nc"] is not None:
                continue
            po = d["pend_out"]
            if po is not None and po["fill_i"] == j:
                try:
                    px = bar_prem(d, t)[0]
                except NC as e:
                    d["nc"] = (e.reason, d["open"]["sig_t"]); d["legs"] = []
                    d["open"] = None; d["pend_out"] = None; continue
                o = d["open"]
                net = round((px - o["entry_px"]) * lot - COST, 2)
                leg = dict(direction=d["name"], leg_no=o["leg_no"],
                           strike=o["strike"], side=o["side"],
                           signal_time=o["sig_t"], entry_time=o["entry_t"],
                           entry_premium=o["entry_px"], exit_time=t,
                           exit_premium=px, exit_reason=po["reason"],
                           exit_signal_time=po["sig_t"],
                           gross_pts=round(px - o["entry_px"], 2), net=net)
                d["legs"].append(leg)
                closed_pnl += net
                d["open"] = None; d["pend_out"] = None
                if po["reason"] == "failure_close" and variant == "R" \
                        and d["legs_done"] < 3:
                    d["phase"] = "seek_rebreak"
                else:
                    d["phase"] = "done"
        for d in dirs.values():
            if d["nc"] is not None:
                continue
            pi = d["pend_in"]
            if pi is not None and pi["fill_i"] == j:
                strike, side = pi["strike"], d["side"]
                cd = prem(idx, exp, strike, side, day) \
                    if False else prem_fn(idx, exp, strike, side, day)
                if not cd:
                    d["nc"] = (f"premium contract {exp}|{strike}|{side} "
                               f"absent for {day}", times[pi["sig_i"]])
                    d["legs"] = []; d["pend_in"] = None; continue
                if t not in cd:
                    d["nc"] = (f"premium entry bar {t} missing for "
                               f"{strike}{side}", times[pi["sig_i"]])
                    d["legs"] = []; d["pend_in"] = None; continue
                d["legs_done"] += 1
                d["open"] = dict(strike=strike, side=side, cd=cd,
                                 entry_px=cd[t][0], entry_t=t,
                                 sig_t=times[pi["sig_i"]],
                                 leg_no=d["legs_done"])
                d["pend_in"] = None
                d["phase"] = "holding"
        # ---- 2) close-of-bar exit evaluation for open legs ----
        for d in dirs.values():
            if d["nc"] is not None or d["open"] is None:
                continue
            o = d["open"]
            try:
                pcl = bar_prem(d, t)[3]
            except NC as e:
                d["nc"] = (e.reason, o["sig_t"]); d["legs"] = []
                d["open"] = None; continue
            stop_hit = pcl <= o["entry_px"] - STOP_PTS
            fail_hit = failed_close(d, bars[j][4])
            if t == SQ:
                px = pcl
                reason = "square_off"
                net = round((px - o["entry_px"]) * lot - COST, 2)
                d["legs"].append(dict(
                    direction=d["name"], leg_no=o["leg_no"],
                    strike=o["strike"], side=o["side"],
                    signal_time=o["sig_t"], entry_time=o["entry_t"],
                    entry_premium=o["entry_px"], exit_time=t,
                    exit_premium=px, exit_reason=reason,
                    exit_signal_time=t,
                    gross_pts=round(px - o["entry_px"], 2), net=net))
                closed_pnl += net
                d["open"] = None; d["phase"] = "done"
            elif stop_hit or fail_hit:
                reason = "stop" if stop_hit else "failure_close"
                d["pend_out"] = dict(fill_i=j + 1, reason=reason, sig_t=t)
                d["phase"] = "pend_out"
        # ---- 3) signal evaluation at bar j close ----
        for d in dirs.values():
            if d["nc"] is not None:
                continue
            if variant == "R" and d["phase"] in ("seek", "seek_rebreak"):
                if j < sq_i and beyond(d, bars[j][4]):
                    d["first_signal_seen"] = True
                    shift_first = (mode == "shift" and d["legs_done"] == 0
                                   and d["phase"] == "seek")
                    if shift_first:
                        fill_i = j + 7
                        if fill_i <= sq_i:
                            try:
                                try_entry(d, j, fill_i, j + 6)
                            except NC as e:
                                d["nc"] = (e.reason, t); d["legs"] = []
                        else:
                            d["phase"] = "done"
                    else:
                        try:
                            try_entry(d, j, j + 1, j)
                        except NC as e:
                            d["nc"] = (e.reason, t); d["legs"] = []
            elif variant == "H" and d["phase"] == "seek":
                if j < sq_i and beyond(d, bars[j][4]):
                    d["break_i"] = j
                    d["first_signal_seen"] = True
                    d["phase"] = "h_wait"
            elif variant == "H" and d["phase"] == "h_wait":
                if j == d["break_i"] + 11:
                    bi = d["break_i"]
                    no_fail = all(not failed_close(d, bars[k][4])
                                  for k in range(bi + 1, j + 1))
                    qual = no_fail and beyond(d, bars[j][4])
                    d["qual"] = qual
                    if qual and j + 1 <= sq_i:
                        if mode == "shift":
                            fill_i = j + 7
                            if fill_i <= sq_i:
                                try:
                                    try_entry(d, j, fill_i, j + 6)
                                except NC as e:
                                    d["nc"] = (e.reason, t); d["legs"] = []
                            else:
                                d["phase"] = "done"
                        else:
                            try:
                                try_entry(d, j, j + 1, j)
                            except NC as e:
                                d["nc"] = (e.reason, t); d["legs"] = []
                    elif d["phase"] != "done":
                        d["phase"] = "done"
        j += 1

    legs, nc_rows = [], []
    for d in dirs.values():
        if d["nc"] is not None:
            nc_rows.append(dict(direction=d["name"],
                                signal_time=d["nc"][1], reason=d["nc"][0]))
        else:
            legs.extend(d["legs"])
    info = dict(cap_hit=cap_hit,
                signals={dn: dirs[dn]["first_signal_seen"] for dn in dirs},
                qualified={dn: dirs[dn]["qual"] for dn in dirs},
                break_seen={dn: dirs[dn]["break_i"] is not None
                            for dn in dirs})
    return legs, nc_rows, info

# ---------------- book runner ----------------
def run_book(idx, window, variant, mode, november=False):
    """Returns dict with legs (scored), nc direction-days, signal-day
    denominators, cap-hit days, day nets."""
    legs_out, nc_out = [], []
    signal_dd = 0          # direction-days in the NC denominator
    cap_days = set()
    break_days = defaultdict(int)
    qual_days = 0
    if november:
        days = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05",
                "2026-11-06"]
    else:
        lo, hi = (f"{window}-01-01", f"{window}-10-31")
        days = sorted(d for d in SPOT[idx] if lo <= d <= hi)
    excluded = 0
    for day in days:
        if november:
            bars = nov_spot(idx, day)
            if not bars:
                excluded += 1
                continue
            prem_fn = prem_day_nov
        else:
            bars = SPOT[idx][day]
            if len(bars) < MIN_BARS:
                excluded += 1
                continue
            prem_fn = prem_day_main
        # signal-day denominator: a direction with a break whose first
        # entry fill can be <= 15:10 (R), resp. a qualified break (H).
        or_bars = [b for b in bars if b[0] in ("09:15", "09:20", "09:25")]
        if len(or_bars) < 3:
            excluded += 1
            continue
        orh = max(b[2] for b in or_bars); orl = min(b[3] for b in or_bars)
        times = [b[0] for b in bars]
        sq_i = times.index(SQ) if SQ in times else None
        for dname, level in (("up", orh), ("down", orl)):
            bi = None
            for i, b in enumerate(bars):
                if tmin(b[0]) < tmin("09:30"):
                    continue
                if (dname == "up" and b[4] > level) or \
                   (dname == "down" and b[4] < level):
                    bi = i; break
            if bi is None:
                continue
            break_days[dname] += 1
            if variant == "R":
                # first fill bar = bi+1 (main/flip) or bi+7 (shift)
                fill_i = bi + (7 if mode == "shift" else 1)
                if sq_i is not None and fill_i <= sq_i:
                    signal_dd += 1
            else:
                ci = bi + 11
                if ci < len(bars):
                    no_fail = all(
                        not ((b[4] <= level) if dname == "up"
                             else (b[4] >= level))
                        for b in bars[bi + 1:ci + 1])
                    beyond_c = (bars[ci][4] > level) if dname == "up" \
                        else (bars[ci][4] < level)
                    fill_i = ci + (7 if mode == "shift" else 1)
                    if no_fail and beyond_c and sq_i is not None \
                            and fill_i <= sq_i:
                        signal_dd += 1
                        qual_days += 1
        legs, nc_rows, info = simulate(idx, day, bars, variant, mode, prem_fn)
        for l in legs:
            l.update(index=idx, date=day, variant=variant, mode=mode,
                     window=("NOV" if november else window))
            legs_out.append(l)
        for n in nc_rows:
            n.update(index=idx, date=day, variant=variant, mode=mode,
                     window=("NOV" if november else window))
            nc_out.append(n)
        if info.get("cap_hit"):
            cap_days.add(day)
    day_nets = defaultdict(float)
    for l in legs_out:
        day_nets[l["date"]] += l["net"]
    return dict(legs=legs_out, nc=nc_out, signal_dd=signal_dd,
                cap_days=sorted(cap_days), day_nets=dict(day_nets),
                excluded_days=excluded, break_dd=dict(break_days),
                qualified_dd=qual_days)

def stats_for(book):
    legs = book["legs"]
    net = round(sum(l["net"] for l in legs), 2)
    h1 = round(sum(l["net"] for l in legs if l["date"][5:7] in
                   ("01", "02", "03", "04", "05")), 2)
    h2 = round(sum(l["net"] for l in legs if l["date"][5:7] in
                   ("06", "07", "08", "09", "10")), 2)
    months = {}
    for m in range(1, 11):
        mm = f"{m:02d}"
        months[mm] = round(sum(l["net"] for l in legs
                               if l["date"][5:7] == mm), 2)
    top3 = sorted((l["net"] for l in legs), reverse=True)[:3]
    ex_top3 = round(net - sum(top3), 2)
    dn = book["day_nets"]
    worst_day = min(dn.values()) if dn else None
    worst_day_date = min(dn, key=dn.get) if dn else None
    dates_sorted = sorted(dn)
    worst3 = None
    for i in range(len(dates_sorted) - 2):
        s = sum(dn[dates_sorted[k]] for k in range(i, i + 3))
        if worst3 is None or s < worst3[0]:
            worst3 = (round(s, 2), dates_sorted[i], dates_sorted[i + 2])
    # timing audit
    viol = 0
    for l in legs:
        if not (l["entry_time"] > l["signal_time"]):
            viol += 1
        if l["exit_reason"] == "square_off":
            if l["exit_time"] != SQ:
                viol += 1
        else:
            if not (l["exit_time"] > l["exit_signal_time"]):
                viol += 1
    nc_n = len(book["nc"])
    nc_pct = round(100.0 * nc_n / book["signal_dd"], 2) \
        if book["signal_dd"] else None
    return dict(n_legs=len(legs), net=net, half1=h1, half2=h2,
                months=months, ex_top3=ex_top3, worst_day=worst_day,
                worst_day_date=worst_day_date,
                worst_3day=worst3[0] if worst3 else None,
                worst_3day_span=(worst3[1], worst3[2]) if worst3 else None,
                cap_hit_days=len(book["cap_days"]),
                timing_violations=viol, nc_days=nc_n,
                signal_dd=book["signal_dd"], nc_pct=nc_pct,
                active_days=len(dn))

def main():
    results = {}
    all_rows = []
    for idx in ("BANKNIFTY", "NIFTY"):
        for variant in ("R", "H"):
            for window in ("2026", "2025"):
                books = {}
                for mode in ("main", "flip", "shift"):
                    b = run_book(idx, window, variant, mode)
                    books[mode] = b
                    for l in b["legs"]:
                        row = dict(book=f"{variant}" if mode == "main"
                                   else f"{variant}_{mode.upper()}",
                                   window=window, index=idx, variant=variant,
                                   date=l["date"], direction=l["direction"],
                                   leg_no=l["leg_no"], strike=l["strike"],
                                   side=l["side"],
                                   signal_time=l["signal_time"],
                                   entry_time=l["entry_time"],
                                   entry_premium=l["entry_premium"],
                                   exit_time=l["exit_time"],
                                   exit_premium=l["exit_premium"],
                                   exit_reason=l["exit_reason"],
                                   exit_signal_time=l["exit_signal_time"],
                                   gross_pts=l["gross_pts"],
                                   net_inr=l["net"], status="SCORED",
                                   nc_reason="")
                        all_rows.append(row)
                    if mode == "main":
                        for n in b["nc"]:
                            all_rows.append(dict(
                                book=variant, window=window, index=idx,
                                variant=variant, date=n["date"],
                                direction=n["direction"], leg_no="",
                                strike="", side="",
                                signal_time=n["signal_time"], entry_time="",
                                entry_premium="", exit_time="",
                                exit_premium="", exit_reason="",
                                exit_signal_time="", gross_pts="",
                                net_inr="", status="NOT_COMPUTED",
                                nc_reason=n["reason"]))
                st = stats_for(books["main"])
                st["flip_net"] = round(sum(l["net"] for l in
                                           books["flip"]["legs"]), 2)
                st["flip_legs"] = len(books["flip"]["legs"])
                st["shift_net"] = round(sum(l["net"] for l in
                                            books["shift"]["legs"]), 2)
                st["shift_legs"] = len(books["shift"]["legs"])
                st["excluded_days"] = books["main"]["excluded_days"]
                st["break_dd"] = books["main"]["break_dd"]
                st["qualified_dd"] = books["main"]["qualified_dd"]
                results[f"{idx}|{variant}|{window}"] = st
                print(f"{idx} {variant} {window}: legs={st['n_legs']} "
                      f"net={st['net']} H1={st['half1']} H2={st['half2']} "
                      f"flip={st['flip_net']} shift={st['shift_net']} "
                      f"exTop3={st['ex_top3']} NC={st['nc_days']}/"
                      f"{st['signal_dd']} ({st['nc_pct']}%) "
                      f"viol={st['timing_violations']}")
    # ---- November appendix ----
    nov = {}
    for idx in ("BANKNIFTY", "NIFTY"):
        for variant in ("R", "H"):
            b = run_book(idx, "NOV", variant, "main", november=True)
            st = stats_for(b)
            nov[f"{idx}|{variant}"] = dict(
                stats=st, legs=b["legs"], nc=b["nc"],
                day_nets=b["day_nets"])
            for l in b["legs"]:
                all_rows.append(dict(
                    book=f"NOV_{variant}", window="NOV", index=idx,
                    variant=variant, date=l["date"],
                    direction=l["direction"], leg_no=l["leg_no"],
                    strike=l["strike"], side=l["side"],
                    signal_time=l["signal_time"],
                    entry_time=l["entry_time"],
                    entry_premium=l["entry_premium"],
                    exit_time=l["exit_time"], exit_premium=l["exit_premium"],
                    exit_reason=l["exit_reason"],
                    exit_signal_time=l["exit_signal_time"],
                    gross_pts=l["gross_pts"], net_inr=l["net"],
                    status="SCORED", nc_reason=""))
            for n in b["nc"]:
                all_rows.append(dict(
                    book=f"NOV_{variant}", window="NOV", index=idx,
                    variant=variant, date=n["date"],
                    direction=n["direction"], leg_no="", strike="",
                    side="", signal_time=n["signal_time"], entry_time="",
                    entry_premium="", exit_time="", exit_premium="",
                    exit_reason="", exit_signal_time="", gross_pts="",
                    net_inr="", status="NOT_COMPUTED",
                    nc_reason=n["reason"]))
            print(f"NOV {idx} {variant}: legs={st['n_legs']} "
                  f"net={st['net']} NC={st['nc_days']}/{st['signal_dd']}")
    # ---- verdicts (2026 legs; 2025 disclosed) ----
    verdicts = {}
    for idx in ("BANKNIFTY", "NIFTY"):
        for variant in ("R", "H"):
            st = results[f"{idx}|{variant}|2026"]
            st25 = results[f"{idx}|{variant}|2025"]
            failed = []
            if not (st["net"] > 0):
                failed.append("2026 net not > 0")
            if not (st["half1"] > 0 and st["half2"] > 0):
                failed.append("halves not both positive")
            if not (st["net"] > st["flip_net"]):
                failed.append("does not beat FLIPPED placebo")
            if not (st["net"] > st["shift_net"]):
                failed.append("does not beat SHIFTED placebo")
            if not (st["ex_top3"] > 0):
                failed.append("ex-top-3 not positive")
            if st["nc_pct"] is None or st["nc_pct"] > 10.0:
                failed.append("NC share > 10% of signal days")
            if st["timing_violations"] != 0:
                failed.append("timing violations present")
            v25_note = ("2025 NOT_COMPUTED window-wide (designated premium "
                        "stores hold no 2025 trade days) — no 2025 net "
                        "exists, so the FAIL-DOUBLE clause has no net to "
                        "test; disclosed, not zeroed.")
            verdicts[f"{idx}|{variant}"] = dict(
                verdict=("PASS" if not failed else "FAIL"),
                failed_legs=failed, note_2025=v25_note)
            print(f"VERDICT {idx} {variant}: "
                  f"{verdicts[f'{idx}|{variant}']['verdict']} {failed}")
    out = dict(results=results, verdicts=verdicts,
               november={k: dict(stats=v["stats"], legs=v["legs"],
                                 nc=v["nc"], day_nets=v["day_nets"])
                         for k, v in nov.items()})
    (TR / "break_capture_v1_results.json").write_text(
        json.dumps(out, indent=1, default=str))
    cols = ["book", "window", "index", "variant", "date", "direction",
            "leg_no", "strike", "side", "signal_time", "entry_time",
            "entry_premium", "exit_time", "exit_premium", "exit_reason",
            "exit_signal_time", "gross_pts", "net_inr", "status",
            "nc_reason"]
    with open(TR / "break_capture_v1_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in sorted(all_rows, key=lambda r: (r["window"], r["index"],
                                                 r["book"], r["date"],
                                                 str(r["leg_no"]))):
            w.writerow({c: r.get(c, "") for c in cols})
    print("WROTE break_capture_v1_results.json + break_capture_v1_trades.csv"
          f" rows={len(all_rows)}")

if __name__ == "__main__":
    main()
