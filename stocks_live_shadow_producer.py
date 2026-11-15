#!/usr/bin/env python3
"""SARVARITU LIVE-SHADOW PRODUCER — intraday live layer for the causal
components of the frozen SarvaRitu book (spec:
stocks_sarvaritu_forward_spec.md; official EOD construction:
stocks_sarvaritu_logger.py) plus the two November component
scorecards that sit inside the SarvaRitu roof.

BOOK LAYER (proven causal on completed 5-min bars — see control runs):
  LIVE here:  N4-V3, P2F, P2F-R2, R2-LOWBAND.
  EOD-ONLY (NOT evaluated here): F4, INV-LONG, INV-ABOVE. Their frozen
  selection is pool_pick over the whole day's first V4 / first skill-OR
  signals, ranked by setup rank BEFORE time — on 39/67 (F4 window) and
  49/84 (INV round-1) October 2026 stock-days where both heads fired,
  the frozen pick is the LATER signal, so the entry cannot be known
  when the earlier signal completes. No intraday variant is invented
  for them; the EOD logger remains their record.

SCORECARD LAYER (separate logs, separate labels — never mixed into the
book log; frozen specs stocks_n4_november_paper_spec.md and
stocks_p2f_november_shadow_spec.md):
  N4-PRIMARY  — the November primary variant of the same reaction-day
                trigger/entry as book N4-V3 (09:25-bar move >= 1%,
                entry = 09:30-bar close labelled 09:35, NO book
                exclusions), exits T125/S050 primary + T10/S050 shadow.
  P2F-SHADOW  — the ungated shadow: results only, |reaction return|
                >= 2.00%, entry R+1 09:15 open, exits T125/S050 primary
                + T10/S050 shadow, NO exclusions (all events taken).

This layer is a SHADOW: it writes ONLY to
  stocks_sarvaritu_live_shadow_log.csv (book closed trades),
  stocks_sarvaritu_live_shadow_scorecards_log.csv (scorecard trades),
  stocks_sarvaritu_live_shadow_state.json (open positions),
  stocks_sarvaritu_live_shadow_producer.log (every evaluation).
It NEVER writes the official stocks_sarvaritu_paper_log.csv or the
scorecards' own EOD logs. Paper only, real Rs0, no orders. Per 100
shares (provisional), Rs40/trade, square-off 15:10 — identical money
basis to the frozen book.

Frozen rules implemented (verbatim from stocks_engine_v2_build.py /
stocks_sarvaritu_logger.py / stocks_reaction_profiles.py, NOT
re-derived):
  - Reaction date: reaction_date if event_date <= reaction <= event+7d
    else event_date. N4 days = results + SINGLE_NEWS classes; P2F
    family = results only. Reaction return = round((close[R]/
    close[R-1]-1)*100, 2) on the stock's own daily bars; direction
    LONG iff ret > 0.
  - N4-V3 (book): on a reaction day, move = 09:25-bar close / prior
    close - 1; |move| >= 1.0% -> follow, entry = 09:30-bar close
    (labelled 09:35), exits T150/S080 scanned on bars AFTER the
    09:30 bar; book exclusions + v2 deletions apply.
  - P2F: |ret| >= 2.5%, entry R+1 09:15 open, T125/S050.
  - P2F-R2: |ret| >= 2.5%, entry R+2 09:15 open, T125/S050.
  - R2-LOWBAND: 2.0% <= |ret| < 2.5%, entry R+2 09:15 open, T125/S050;
    C23: stands aside when REGIME-CLASSIFIER-1 label is UP.
  - Event exits (book + scorecards): scan bars in order starting
    AFTER the entry bar, times <= 15:10, stop checked before target
    inside a bar, square-off at the 15:10 bar close (or last bar
    <= 15:10). Nets are computed from UNROUNDED stop/target prices;
    only the stored exit price is rounded (frozen convention).
  - Regime label: REGIME-CLASSIFIER-1 from NIFTY daily closes strictly
    before the day (prior close vs 50DMA + 5-day slope of the line).

Data: Upstox v3 intraday candles (minutes/5) with the script token from
upstox_refresh/.env (UPSTOX_ACCESS_TOKEN; never printed) and the browser
User-Agent header every api.upstox.com request requires. Prior-day
context (daily bars, calendar) is read from the forward data root the
EOD logger maintains (data/sarvaritu_fwd/, read-only here) and
stocks_sarvaritu_calendar_live.csv.

Modes:
  (default)      one live evaluation pass for today (IST).
  --replay DATE  bar-by-bar causal replay of DATE from the forward
                 root's stored native 5m bars; prints trades as JSON;
                 writes nothing to the live logs/state.
  --calendar P   calendar override (replay controls only).
"""
import argparse, csv, json, os, sys, urllib.parse, urllib.request
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

WS = "/home/hatch/workspace/trading"
FWD = f"{WS}/data/sarvaritu_fwd"
LIVE_CAL = f"{WS}/stocks_sarvaritu_calendar_live.csv"
LIVE_LOG = f"{WS}/stocks_sarvaritu_live_shadow_log.csv"
SC_LOG = f"{WS}/stocks_sarvaritu_live_shadow_scorecards_log.csv"
STATE = f"{WS}/stocks_sarvaritu_live_shadow_state.json"
PLOG = f"{WS}/stocks_sarvaritu_live_shadow_producer.log"
KEYS = f"{WS}/data/progressive/keys.json"
ENV_FILE = f"{WS}/upstox_refresh/.env"
API = "https://api.upstox.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
IST = ZoneInfo("Asia/Kolkata")
COST = 40.0
SYMBOLS = ["GODREJCP", "GLENMARK", "ITC", "RECLTD", "TVSMOTOR", "UNITDSPR",
           "OBEROIRLTY", "NTPC", "INDUSTOWER", "KALYANKJIL", "HDFCBANK",
           "NHPC", "PFC", "IRCTC", "WIPRO", "NATIONALUM", "VEDL",
           "HINDCOPPER", "HINDZINC", "HINDALCO", "TATASTEEL", "ASTRAL",
           "BDL", "OIL", "HINDUNILVR"]
SINGLE_NEWS = {"management_change", "large_order", "fda_approval",
               "block_deal", "sector_policy", "pricing", "corporate_action"}
EXCL_V2 = {("N4-V3", "GLENMARK", "SHORT"), ("N4-V3", "BDL", "SHORT"),
           ("N4-V3", "HINDALCO", "SHORT"), ("N4-V3", "HINDZINC", "LONG"),
           ("N4-V3", "UNITDSPR", "LONG"), ("N4-V3", "RECLTD", "LONG"),
           ("N4-V3", "WIPRO", "SHORT"), ("P2F-R2", "KALYANKJIL", "LONG")}
LOG_FIELDS = ["date", "comp", "stock", "dir", "entry_time", "entry",
              "exit", "exit_time", "exit_reason", "net", "regime", "mode"]
SC_FIELDS = ["date", "comp", "stock", "dir", "entry_time", "entry",
             "exit", "exit_time", "exit_reason", "net", "shadow_net_T10",
             "regime", "mode"]

def plog(msg):
    line = f"{datetime.now(IST).isoformat(timespec='seconds')} {msg}"
    with open(PLOG, "a") as f:
        f.write(line + "\n")

def wk(dstr):
    return date.fromisoformat(dstr).weekday() >= 5

# ---------------------------------------------------------------- data
def load_daily(sym, upto=None):
    rows = []
    p = f"{FWD}/{sym}/spot_daily.csv"
    if not os.path.exists(p):
        return rows
    for r in csv.DictReader(open(p)):
        d = r["date"][:10]
        if upto and d > upto:
            continue
        rows.append({"date": d, "open": float(r["open"]), "high": float(r["high"]),
                     "low": float(r["low"]), "close": float(r["close"])})
    rows.sort(key=lambda x: x["date"])
    return rows

def load_bars_fwd(sym, day):
    p = f"{FWD}/{sym}/spot_5m.csv"
    out = []
    if not os.path.exists(p):
        return out
    for r in csv.DictReader(open(p)):
        if r["timestamp"][:10] != day:
            continue
        out.append({"timestamp": r["timestamp"][:19], "time": r["timestamp"][11:16],
                    "open": float(r["open"]), "high": float(r["high"]),
                    "low": float(r["low"]), "close": float(r["close"])})
    out.sort(key=lambda x: x["timestamp"])
    return out

def load_token():
    for line in open(ENV_FILE):
        if line.startswith("UPSTOX_ACCESS_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("UPSTOX_ACCESS_TOKEN not found in upstox_refresh/.env")

def api_get(path):
    req = urllib.request.Request(API + path, headers={
        "Authorization": f"Bearer {load_token()}",
        "Accept": "application/json", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())

def fetch_intraday_5m(sym):
    keys = json.load(open(KEYS))
    enc = urllib.parse.quote(keys[sym], safe="")
    payload = api_get(f"/v3/historical-candle/intraday/{enc}/minutes/5")
    rows = (payload.get("data") or {}).get("candles") or []
    out = []
    for c in rows:
        ts = str(c[0])[:19].replace("T", " ")
        out.append({"timestamp": ts, "time": ts[11:16], "open": float(c[1]),
                    "high": float(c[2]), "low": float(c[3]), "close": float(c[4])})
    out.sort(key=lambda x: x["timestamp"])
    return out

# ------------------------------------------------------- frozen context
def eff_reaction(r):
    ev = date.fromisoformat(r["event_date"][:10])
    react = date.fromisoformat(r["reaction_date"][:10]) if r.get("reaction_date") else None
    eff = react if (react and ev <= react <= ev + timedelta(days=7)) else ev
    return eff.isoformat()

def calendar_events(cal_path):
    evs = []
    for r in csv.DictReader(open(cal_path)):
        if r["stock"] not in SYMBOLS or not r["event_date"]:
            continue
        evs.append({"stock": r["stock"], "event_type": r["event_type"],
                    "event_date": r["event_date"][:10], "R": eff_reaction(r)})
    return evs

def regime_label_today(nifty_daily, target):
    """REGIME-CLASSIFIER-1 for `target` (target not in nifty_daily)."""
    closes = [d["close"] for d in nifty_daily]
    dates = [d["date"] for d in nifty_daily]
    if len(closes) < 56 or dates[-1] >= target:
        return "UNCLASSIFIED"
    prev_close = closes[-1]
    ma50_t = sum(closes[-50:]) / 50
    j5 = len(closes) - 5                      # axis[j-5] == dates[-5]
    ma50_j5 = sum(closes[j5 - 50:j5]) / 50
    s = ma50_t - ma50_j5
    if prev_close > ma50_t and s >= 0:
        return "UP"
    if prev_close <= ma50_t and s <= 0:
        return "DOWN"
    return "FLAT"

def _reaction_ret(daily_by_sym, sym, R):
    daily = daily_by_sym.get(sym, [])
    dmap = {d["date"]: i for i, d in enumerate(daily)}
    if R not in dmap or dmap[R] == 0:
        return None
    ri = dmap[R]
    return round((daily[ri]["close"] / daily[ri - 1]["close"] - 1) * 100, 2)

def due_candidates(cal_path, target, daily_by_sym, trading_days):
    """Book P2F-family candidates whose ENTRY date is `target`, plus the
    set of (stock, day) N4 reaction days. Trading-day lags are counted
    on the NIFTY calendar; returns use the stock's own daily closes."""
    evs = calendar_events(cal_path)
    tcal = {d: i for i, d in enumerate(trading_days)}
    if target not in tcal:
        return [], set()
    out = []
    n4_days = set()
    for e in evs:
        if e["event_type"] == "results" or e["event_type"] in SINGLE_NEWS:
            n4_days.add((e["stock"], e["R"]))
        if e["event_type"] != "results":
            continue
        sym, R = e["stock"], e["R"]
        if R not in tcal:
            continue
        ret = _reaction_ret(daily_by_sym, sym, R)
        if ret is None:
            continue
        direction = "LONG" if ret > 0 else "SHORT"
        for comp, lag, lo_b, hi_b in (("P2F", 1, 2.5, None),
                                      ("P2F-R2", 2, 2.5, None),
                                      ("R2-LOWBAND", 2, 2.0, 2.5)):
            ei = tcal[R] + lag
            if ei >= len(trading_days) or trading_days[ei] != target:
                continue
            if abs(ret) < lo_b or (hi_b is not None and abs(ret) >= hi_b):
                continue
            out.append({"comp": comp, "stock": sym, "dir": direction,
                        "reaction_ret_pct": ret, "R": R})
    return out, n4_days

def shadow_candidates(cal_path, target, daily_by_sym, trading_days):
    """P2F-SHADOW candidates (ungated): results only, |ret| >= 2.00%,
    entry R+1. No exclusions — every qualifying event is taken."""
    evs = calendar_events(cal_path)
    tcal = {d: i for i, d in enumerate(trading_days)}
    if target not in tcal:
        return []
    out = []
    for e in evs:
        if e["event_type"] != "results":
            continue
        sym, R = e["stock"], e["R"]
        if R not in tcal:
            continue
        ei = tcal[R] + 1
        if ei >= len(trading_days) or trading_days[ei] != target:
            continue
        ret = _reaction_ret(daily_by_sym, sym, R)
        if ret is None or abs(ret) < 2.0:
            continue
        out.append({"comp": "P2F-SHADOW", "stock": sym,
                    "dir": "LONG" if ret > 0 else "SHORT",
                    "reaction_ret_pct": ret, "R": R})
    return out

def comp_allowed(comp, stock, direction, regime):
    if (comp, stock, direction) in EXCL_V2:
        return False
    if comp == "N4-V3":
        if stock == "ASTRAL":
            return False
        if stock == "TVSMOTOR" and direction == "LONG":
            return False
        if stock == "OIL" and direction == "LONG":
            return False
    if comp == "P2F":
        if stock in ("ASTRAL", "HINDUNILVR"):
            return False
        if stock == "HINDALCO" and direction == "LONG":
            return False
    if comp == "P2F-R2":
        if stock in ("ASTRAL", "HINDUNILVR"):
            return False
        if stock == "TVSMOTOR" and direction == "LONG":
            return False
    if comp == "R2-LOWBAND":
        if stock in ("ASTRAL", "HINDUNILVR"):
            return False
        if stock == "HINDALCO" and direction == "LONG":
            return False
        if regime == "UP":                    # C23 stand-aside
            return False
    return True

# ------------------------------------------------------------ exit scan
def scan_exit(bars, entry, direction, tgt_pct, stp_pct, from_idx):
    """Frozen event-replay semantics on bars[from_idx:]: stop before
    target inside a bar; bars after 15:10 never trigger; the 15:10 bar
    square-offs at its close; if bars run out past 15:10 with no exit,
    square-off at the last bar <= 15:10. Exit price returned UNROUNDED
    (frozen nets use unrounded levels). Returns (reason, price, time)
    or None if still open on the bars available."""
    sign = 1 if direction == "LONG" else -1
    target = entry * (1 + sign * tgt_pct / 100)
    stop = entry * (1 - sign * stp_pct / 100)
    last = None
    i = from_idx
    while i < len(bars):
        c = bars[i]
        if c["time"] > "15:10":
            break
        last = c
        if sign == 1:
            if c["low"] <= stop:
                return "stop", stop, c["time"]
            if c["high"] >= target:
                return "target", target, c["time"]
        else:
            if c["high"] >= stop:
                return "stop", stop, c["time"]
            if c["low"] <= target:
                return "target", target, c["time"]
        if c["time"] == "15:10":
            return "square_off", c["close"], c["time"]
        i += 1
    if last is not None and bars and bars[-1]["time"] > "15:10":
        return "square_off", last["close"], last["time"]
    return None

def net_of(direction, entry, exit_price):
    sign = 1 if direction == "LONG" else -1
    return round(sign * (exit_price - entry) * 100 - COST, 2)

# ------------------------------------------------------------- evaluate
class Evaluator:
    """One trading day, bar-by-bar. Feed completed bars per symbol via
    step() (book) and step_scorecards(); all rules causal."""
    def __init__(self, target, cal_path):
        self.target = target
        self.cal_path = cal_path
        self.daily = {s: [d for d in load_daily(s, upto=target)
                          if d["date"] < target] for s in SYMBOLS}
        nifty_daily = [d for d in load_daily("NIFTY", upto=target)
                       if d["date"] < target]
        self.regime = regime_label_today(nifty_daily, target)
        trading_days = sorted({d["date"] for d in nifty_daily} | {target})
        self.cands, self.n4_days = due_candidates(
            cal_path, target, self.daily, trading_days)
        self.cands = [c for c in self.cands
                      if comp_allowed(c["comp"], c["stock"], c["dir"], self.regime)]
        self.sc_cands = shadow_candidates(
            cal_path, target, self.daily, trading_days)
        self.positions = {}      # book: (comp, stock) -> pos
        self.closed = []         # book closed trades
        self.entered = set()     # book (comp, stock)
        self.sc_positions = {}   # scorecard: (comp, stock) -> pos
        self.sc_closed = []      # scorecard closed trades
        self.sc_entered = set()  # scorecard (comp, stock)

    def prev_close(self, sym):
        d = self.daily.get(sym, [])
        return d[-1]["close"] if d else None

    # ---- book layer ----
    def step(self, sym, bars):
        actions = []
        if wk(self.target) or not bars:
            return actions
        for c in [x for x in self.cands if x["stock"] == sym]:
            key = (c["comp"], sym)
            if key in self.entered:
                continue
            self.entered.add(key)
            entry = bars[0]["open"]
            pos = {"comp": c["comp"], "stock": sym, "dir": c["dir"],
                   "entry_time": "09:15", "entry": round(entry, 2),
                   "entry_idx": 0, "scan_from": 1,
                   "tgt": 1.25, "stp": 0.50, "R": c["R"],
                   "reaction_ret_pct": c["reaction_ret_pct"]}
            self.positions[key] = pos
            actions.append({"action": "ENTRY", "layer": "book",
                            **{k: pos[k] for k in ("comp", "stock", "dir", "entry_time", "entry")},
                            "date": self.target, "regime": self.regime,
                            "basis": f"results reaction {c['reaction_ret_pct']:+.2f}% on {c['R']}"})
        if (sym, self.target) in self.n4_days and ("N4-V3", sym) not in self.entered:
            by_time = {b["time"]: b for b in bars}
            if "09:25" in by_time and "09:30" in by_time:
                pc = self.prev_close(sym)
                if pc:
                    move = (by_time["09:25"]["close"] / pc - 1) * 100
                    if abs(move) >= 1.0:
                        direction = "LONG" if move > 0 else "SHORT"
                        if comp_allowed("N4-V3", sym, direction, self.regime):
                            self.entered.add(("N4-V3", sym))
                            ei = next(i for i, b in enumerate(bars)
                                      if b["time"] == "09:30")
                            entry = by_time["09:30"]["close"]
                            pos = {"comp": "N4-V3", "stock": sym, "dir": direction,
                                   "entry_time": "09:35", "entry": round(entry, 2),
                                   "entry_idx": ei, "scan_from": ei + 1,
                                   "tgt": 1.50, "stp": 0.80}
                            self.positions[("N4-V3", sym)] = pos
                            actions.append({"action": "ENTRY", "layer": "book",
                                            **{k: pos[k] for k in ("comp", "stock", "dir", "entry_time", "entry")},
                                            "date": self.target, "regime": self.regime,
                                            "basis": f"reaction-day move {move:+.2f}% by 09:30"})
        for key in [k for k in self.positions if k[1] == sym]:
            pos = self.positions[key]
            r = scan_exit(bars, pos["entry"], pos["dir"],
                          pos["tgt"], pos["stp"], pos["scan_from"])
            if r is None:
                continue
            reason, ep, et = r
            trade = {"date": self.target, "comp": pos["comp"], "stock": sym,
                     "dir": pos["dir"], "entry_time": pos["entry_time"],
                     "entry": pos["entry"], "exit": round(ep, 2), "exit_time": et,
                     "exit_reason": reason,
                     "net": net_of(pos["dir"], pos["entry"], ep),
                     "regime": self.regime, "mode": "LIVE-SHADOW"}
            self.closed.append(trade)
            del self.positions[key]
            actions.append({"action": "EXIT", "layer": "book", **trade})
        return actions

    # ---- scorecard layer ----
    def _sc_new_pos(self, comp, sym, direction, entry_time, entry, scan_from, basis):
        pos = {"comp": comp, "stock": sym, "dir": direction,
               "entry_time": entry_time, "entry": round(entry, 2),
               "scan_from": scan_from, "basis": basis,
               "variants": {
                   "primary": {"tgt": 1.25, "stp": 0.50, "done": False, "result": None},
                   "t10": {"tgt": 1.0, "stp": 0.50, "done": False, "result": None}}}
        self.sc_positions[(comp, sym)] = pos
        return {"action": "ENTRY", "layer": "scorecard",
                "comp": comp, "stock": sym, "dir": direction,
                "entry_time": entry_time, "entry": pos["entry"],
                "date": self.target, "regime": self.regime, "basis": basis}

    def step_scorecards(self, sym, bars):
        actions = []
        if wk(self.target) or not bars:
            return actions
        for c in [x for x in self.sc_cands if x["stock"] == sym]:
            key = ("P2F-SHADOW", sym)
            if key in self.sc_entered:
                continue
            self.sc_entered.add(key)
            actions.append(self._sc_new_pos(
                "P2F-SHADOW", sym, c["dir"], "09:15", bars[0]["open"], 1,
                f"P2F shadow: results reaction {c['reaction_ret_pct']:+.2f}% on {c['R']}, R+1 open"))
        if (sym, self.target) in self.n4_days and ("N4-PRIMARY", sym) not in self.sc_entered:
            by_time = {b["time"]: b for b in bars}
            if "09:25" in by_time and "09:30" in by_time:
                pc = self.prev_close(sym)
                if pc:
                    move = (by_time["09:25"]["close"] / pc - 1) * 100
                    if abs(move) >= 1.0:
                        direction = "LONG" if move > 0 else "SHORT"
                        self.sc_entered.add(("N4-PRIMARY", sym))
                        ei = next(i for i, b in enumerate(bars)
                                  if b["time"] == "09:30")
                        actions.append(self._sc_new_pos(
                            "N4-PRIMARY", sym, direction, "09:35",
                            by_time["09:30"]["close"], ei + 1,
                            f"N4 primary scorecard: reaction-day move {move:+.2f}% by 09:30"))
        for key in [k for k in self.sc_positions if k[1] == sym]:
            pos = self.sc_positions[key]
            for vn, v in pos["variants"].items():
                if v["done"]:
                    continue
                r = scan_exit(bars, pos["entry"], pos["dir"],
                              v["tgt"], v["stp"], pos["scan_from"])
                if r is not None:
                    v["done"] = True
                    v["result"] = r
            if all(v["done"] for v in pos["variants"].values()):
                pr = pos["variants"]["primary"]["result"]
                tr = pos["variants"]["t10"]["result"]
                trade = {"date": self.target, "comp": pos["comp"], "stock": sym,
                         "dir": pos["dir"], "entry_time": pos["entry_time"],
                         "entry": pos["entry"], "exit": round(pr[1], 2),
                         "exit_time": pr[2], "exit_reason": pr[0],
                         "net": net_of(pos["dir"], pos["entry"], pr[1]),
                         "shadow_net_T10": net_of(pos["dir"], pos["entry"], tr[1]),
                         "regime": self.regime, "mode": "LIVE-SHADOW-SCORECARD"}
                self.sc_closed.append(trade)
                del self.sc_positions[key]
                actions.append({"action": "EXIT", "layer": "scorecard", **trade})
        return actions

# ---------------------------------------------------------------- modes
def run_replay(target, cal_path):
    ev = Evaluator(target, cal_path)
    all_bars = {s: load_bars_fwd(s, target) for s in SYMBOLS}
    times = sorted({b["time"] for s in SYMBOLS for b in all_bars[s]})
    actions = []
    for t in times:
        for s in SYMBOLS:
            bars = [b for b in all_bars[s] if b["time"] <= t]
            actions.extend(ev.step(s, bars))
            actions.extend(ev.step_scorecards(s, bars))
    print(json.dumps({"date": target, "calendar": os.path.basename(cal_path),
                      "regime": ev.regime,
                      "candidates": ev.cands,
                      "scorecard_candidates": ev.sc_cands,
                      "trades": ev.closed,
                      "scorecard_trades": ev.sc_closed,
                      "actions": actions}, indent=1))
    return 0

def _append_csv(path, fields, rows):
    if not rows:
        return
    exists = os.path.exists(path)
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if not exists:
            w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fields})

def run_live():
    now = datetime.now(IST)
    target = now.date().isoformat()
    ev = Evaluator(target, LIVE_CAL)
    state = {"date": target, "positions": {}, "entered": [],
             "sc_positions": {}, "sc_entered": []}
    if os.path.exists(STATE):
        try:
            state = json.load(open(STATE))
        except Exception:
            pass
    if state.get("date") != target:
        state = {"date": target, "positions": {}, "entered": [],
                 "sc_positions": {}, "sc_entered": []}
    ev.entered = {tuple(x) for x in state.get("entered", [])}
    for k, v in state.get("positions", {}).items():
        comp, stock = k.split("|")
        ev.positions[(comp, stock)] = v
    ev.sc_entered = {tuple(x) for x in state.get("sc_entered", [])}
    for k, v in state.get("sc_positions", {}).items():
        comp, stock = k.split("|")
        ev.sc_positions[(comp, stock)] = v
    fetched, missing = {}, []
    for s in SYMBOLS:
        try:
            bars = fetch_intraday_5m(s)
        except Exception as e:
            bars = []
            plog(f"live {target} fetch failed {s}: {str(e)[:160]}")
        done = [b for b in bars
                if datetime.fromisoformat(b["timestamp"]).replace(tzinfo=IST)
                + timedelta(minutes=5) <= now]
        if done:
            fetched[s] = done
        else:
            missing.append(s)
    actions = []
    if wk(target):
        summary = {"date": target, "status": "weekend_rf1", "actions": []}
    elif len(missing) >= 20:
        summary = {"date": target, "status": "no_market_data",
                   "symbols_missing": missing, "actions": []}
    else:
        for s in SYMBOLS:
            if s in fetched:
                actions.extend(ev.step(s, fetched[s]))
                actions.extend(ev.step_scorecards(s, fetched[s]))
        state = {"date": target,
                 "positions": {f"{k[0]}|{k[1]}": v for k, v in ev.positions.items()},
                 "entered": sorted(list(x) for x in ev.entered),
                 "sc_positions": {f"{k[0]}|{k[1]}": v for k, v in ev.sc_positions.items()},
                 "sc_entered": sorted(list(x) for x in ev.sc_entered)}
        with open(STATE, "w") as f:
            json.dump(state, f, indent=1)
        _append_csv(LIVE_LOG, LOG_FIELDS,
                    [a for a in actions if a["action"] == "EXIT" and a.get("layer") == "book"])
        _append_csv(SC_LOG, SC_FIELDS,
                    [a for a in actions if a["action"] == "EXIT" and a.get("layer") == "scorecard"])
        summary = {"date": target, "status": "ok", "regime": ev.regime,
                   "candidates": ev.cands,
                   "scorecard_candidates": ev.sc_cands,
                   "open_positions": [f"{k[0]}:{k[1]}" for k in ev.positions],
                   "open_scorecard_positions": [f"{k[0]}:{k[1]}" for k in ev.sc_positions],
                   "data_missing": missing, "actions": actions}
    for a in actions:
        print(f"LIVE_SHADOW_{a['action']} {json.dumps(a)}")
    print(f"RUN_SUMMARY {json.dumps(summary)}")
    plog(f"live {target} summary {json.dumps(summary)[:600]}")
    return 0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--replay", default=None, help="YYYY-MM-DD replay from forward root")
    ap.add_argument("--calendar", default=LIVE_CAL)
    args = ap.parse_args()
    if args.replay:
        return run_replay(args.replay, args.calendar)
    return run_live()

if __name__ == "__main__":
    raise SystemExit(main())
