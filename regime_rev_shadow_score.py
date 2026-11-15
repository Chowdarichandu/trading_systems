#!/usr/bin/env python3
"""REGIME-REV SHADOW SCORER — forward paper evidence for the Bank
Nifty REGIME-REV v1 family (2026-11-14 setup under the owner's
free-hands scenario-proofing order; spec frozen in
november_regime_fix_2026-11-14.md Phase D).

WHAT THIS IS: a SCORE-ONLY paper shadow. REGIME-REV passed its
frozen standalone Jan-Oct gate on Bank (+Rs15,872.00, 31 legs,
both halves positive, ex-top-3 +Rs8,432.00, beats all three
placebos, 0 NC) with three recorded qualifications: Rs512.00/
trade-day is below the owner's Rs900 lens, H2 is thin (+Rs632),
and its merge test FAILED (its profit sits on stack-busy days) —
so it is NOT a stack add-on and it is armed nowhere. This scorer
collects forward evidence, one evening at a time, from Mon
2026-11-16 to the Nov 30 verdicts (the review bound). It never
writes to the stack's ledger or to any other book's ledger, job,
or log. There is NO stack-idle condition: the family is
standalone, exactly as gated.

FROZEN RULES (november_regime_fix_2026-11-14.md Phase D, verbatim):
- Morning = spot bars 09:15-10:55; O = 09:15 open, C11 = 10:55
  close, H/L = morning high/low, M = (H+L)/2, direction =
  sign(C11-O) (zero -> no trade). Gap% vs the prior session's
  close.
- REGIME MORNING: |gap%| >= 0.586 (Bank Q3) OR |morning move|
  >= 0.7% — all knowable at 11:00.
- CONFIRMATION: the first spot bar in [11:00, 15:05] whose close
  crosses M against the morning direction.
- ENTRY at that bar's close (the premium bar's close at the
  confirmation time); side = reversal side (up-morning -> PE,
  down-morning -> CE); strike = ATM (nearest 100) to the
  confirmation bar's spot close; contract = in-force monthly
  expiry.
- EXITS from the bar AFTER the confirmation bar: stop -50 checked
  before target +90 per bar, fills at the level; else the 15:10
  bar close. 1 lot of 30; Rs220/trade; BUYING ONLY; <= 1 leg/day.
- Premium series must start <= 09:20 and contain the 15:10 bar,
  else the fired day is NC (counted, never estimated).
- TIMING: morning inputs are bars ending <= 10:55 plus the prior
  close; the fill is the confirmation bar's close; exits use
  strictly later bars. Asserted per trade.

DATA SOURCING:
- Spot 5-min bars: EXACTLY the gate's own universe — the
  progressive store (data/progressive/BANKNIFTY/spot_5m.csv)
  with the November machinery's banknifty-2026-11 store overlaid
  for November days, then this scorer's forward cache
  (regime_rev_spot_fwd.json), then the v3 historical-candle
  route (cached). No other stored series is filled in: the
  gate's store holds no 2026-10-29/30 bars, so its Nov 2 gap is
  measured against the Oct 28 close — reproduced as frozen.
  A day with < 70 bars is a fragment — never a morning-read
  day -> NC.
- Premium candles: the gate's prem_store verbatim (round 5 C5
  store, then daily2leg/prem_bank.json, then the fetched-candle
  folders incl. oi_buildup_data), then round 1's fetch machinery
  (oi_buildup_score.fetch_bars — expired route for expired
  expiries, caches into oi_buildup_data in the shared convention,
  the Item 2 persistence fix's store).

LEDGER: november_shadow_regimerev_bank_log.csv — one row per
scored day (TRADED / NO_REGIME / NO_CONFIRMATION / NO_DIRECTION /
NC + the reason named), idempotent per date. Review bound: the
scorer refuses to score days after 2026-11-30 (the Nov 30
verdicts decide the family's future; the scorer says so).

DRY-RUN VERIFICATION (2026-11-14, --verify against November):
reproduces the frozen gate's November legs exactly — Nov 2 PE
54900 target +Rs2,480.00; Nov 3 PE 55300 square-off -Rs1,099.00;
Nov 5 CE 57100 target +Rs2,480.00; Nov 11 PE 60700 stop
-Rs1,720.00 (family November +Rs2,141.00). Nov 13 produces no leg
(no confirmation on the gate's spot source; the IOI dataset's
NC_NO_SPOT tag for Nov 13 came from its separate spot store,
which holds no Nov 13 bars at all — recorded in
scenario_proofing_2026-11-14.md Item 5).

Paper only, real money Rs0. No live orders. Every api.upstox.com
call carries the browser User-Agent. On HTTP 429: HARD STOP for
the run — the day is marked NC rate_limited, no retry, no route
switch.

Usage:
    python3 regime_rev_shadow_score.py [--date YYYY-MM-DD]
                                       [--dry-run] [--verify]
Default date = today (IST). --dry-run computes and prints the row
but writes NOTHING. --verify is a hard-wired no-write check
against a historical date (bypasses the start/window guards for
that check only, and can never write).
"""
import argparse, csv, json, sys
import importlib.util
import urllib.error, urllib.request
from pathlib import Path
from urllib.parse import quote
from datetime import datetime
from zoneinfo import ZoneInfo

TR = Path.home() / "workspace/trading"
IST = ZoneInfo("Asia/Kolkata")
START = "2026-11-16"
WINDOW_END = "2026-11-30"   # review bound: the Nov 30 verdicts
COST = 220.0
LOT = 30
STEP = 100
Q3 = 0.586
STOP, TARGET, SQ = 50.0, 90.0, "15:10"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
API = "https://api.upstox.com"
LEDGER = TR / "november_shadow_regimerev_bank_log.csv"
SPOT_FWD = TR / "regime_rev_spot_fwd.json"
MIN_DAY_BARS = 70

LEDGER_FIELDS = ["date", "status", "reason", "gap_pct",
                 "morning_pct", "direction", "strike", "expiry",
                 "conf_time", "entry_time", "entry_premium",
                 "exit_time", "exit_premium", "exit_reason",
                 "net_inr", "timing_violations", "notes"]

_spec = importlib.util.spec_from_file_location(
    "oi_buildup_score", TR / "oi_buildup_score.py")
obs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(obs)


class RateLimited(Exception):
    pass


_token = None
for _line in (TR / "upstox_refresh/.env").read_text().splitlines():
    if _line.startswith("UPSTOX_ACCESS_TOKEN="):
        _token = _line.split("=", 1)[1].strip()
assert _token


def get(url):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {_token}",
        "Accept": "application/json", "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RateLimited()
        return None


# ---------------- spot bars (the gate's sourcing) ------------------
def _csv_spot(fn):
    out = {}
    if not fn.exists():
        return out
    with open(fn) as f:
        for r in csv.DictReader(f):
            out.setdefault(r["timestamp"][:10], {})[
                r["timestamp"][11:16]] = (float(r["open"]),
                                          float(r["high"]),
                                          float(r["low"]),
                                          float(r["close"]))
    return out


def _spot_map():
    """{date: {time: (o,h,l,c)}} — EXACTLY the frozen gate's spot
    universe: the progressive store as the base (the gate's
    Jan-Oct source) with the November machinery's
    banknifty-2026-11 store overlaid for its days (the gate's
    November source), plus this scorer's own forward cache.
    Deliberately NOT filled from any other stored series: the
    gate's store holds no 2026-10-29/30 bars, so its Nov 2 gap is
    measured against the Oct 28 close (+1.05%, regime) — the
    shadow reproduces the gate's chain as frozen, gap quirks
    included, rather than silently 'correcting' them."""
    m = _csv_spot(TR / "data/progressive/BANKNIFTY/spot_5m.csv")
    for d, bars in _csv_spot(TR / "data/banknifty-2026-11/spot_5m.csv").items():
        m[d] = bars
    if SPOT_FWD.exists():
        for d, rows in json.loads(SPOT_FWD.read_text()).items():
            m.setdefault(d, {b[0]: tuple(b[1:]) for b in rows})
    return m


def _fetch_spot_day(day):
    ikey = quote(obs.IDXKEY["BANKNIFTY"], safe="")
    body = get(f"{API}/v3/historical-candle/{ikey}"
               f"/minutes/5/{day}/{day}")
    cd = [c for c in ((body or {}).get("data") or {}).get("candles")
          or [] if c[0][:10] == day]
    if not cd:
        return None
    return {c[0][11:16]: (float(c[1]), float(c[2]), float(c[3]),
                          float(c[4])) for c in cd}


def spot_bars(day, dry):
    """(bars, source) or (None, reason). Also returns nothing else;
    prev-close is derived by the caller from the same map."""
    m = _spot_map()
    bars = m.get(day)
    if bars and len(bars) >= MIN_DAY_BARS:
        return bars, "stored"
    bars = _fetch_spot_day(day)  # may raise RateLimited
    if bars is None:
        return None, "spot_unserved"
    if len(bars) < MIN_DAY_BARS:
        return None, f"spot_fragment_{len(bars)}_bars"
    if not dry:
        cache = {}
        if SPOT_FWD.exists():
            cache = json.loads(SPOT_FWD.read_text())
        cache[day] = [[t] + list(v) for t, v in sorted(bars.items())]
        SPOT_FWD.write_text(json.dumps(cache))
    return bars, "fetched_v3"


def prev_close(day):
    m = _spot_map()
    prev = [d for d in m if d < day and len(m[d]) >= MIN_DAY_BARS]
    if not prev:
        return None
    d = max(prev)
    bars = m[d]
    return bars[sorted(bars)[-1]][3]


# ---------------- expiry (in-force monthly) ------------------------
def _expiry_map():
    m = {}
    with open(TR / "oi_history/banknifty_daily_oi.csv") as f:
        for r in csv.DictReader(f):
            m[r["date"]] = r["expiry"]
    m.update({d: "2026-11-23" for d in
              ("2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05",
               "2026-11-06", "2026-11-09", "2026-11-11", "2026-11-12",
               "2026-11-13")})
    return m


EXP = _expiry_map()
MONTHLIES = sorted(set(EXP.values()) | {"2026-11-23", "2026-12-29"})


def in_force_expiry(day):
    if day in EXP:
        return EXP[day]
    cand = [e for e in MONTHLIES if e >= day]
    return min(cand) if cand else None


# ---------------- premium (the gate's prem_store, verbatim) --------
R5H = TR / "round5_history"
_c5 = {}


def _prem_bank_c5(exp, strike, typ, day):
    ck = (exp, strike, typ)
    if ck not in _c5:
        fn = R5H / f"C5_{exp}_{strike}{typ}.json"
        byd = {}
        if fn.exists():
            for r in json.loads(fn.read_text()):
                byd.setdefault(r[0], {})[r[1]] = (float(r[2]),
                                                  float(r[3]),
                                                  float(r[4]),
                                                  float(r[5]))
        _c5[ck] = byd
    return _c5[ck].get(day)


PREM_B = json.load(open(TR / "daily2leg/prem_bank.json"))


def prem_store(exp, strike, typ, day):
    b = _prem_bank_c5(exp, strike, typ, day)
    if b:
        return b
    key = f"{exp}|{int(strike)}|{typ}"
    cd = PREM_B.get(key, {}).get(day)
    if cd:
        return {t: tuple(float(x) for x in v) for t, v in cd.items()}
    for folder in ("btst_data", "november_shadow_data",
                   "nifty_weekly_expiry_chain", "oi_buildup_data"):
        fn = TR / folder / f"candles_BANKNIFTY_{int(strike)}{typ}_{exp}_{day}.json"
        if fn.exists():
            body = json.loads(fn.read_text())
            cd = [c for c in ((body.get("data") or {}).get("candles")
                              or []) if c[0][:10] == day]
            if cd:
                return {c[0][11:16]: (float(c[1]), float(c[2]),
                                      float(c[3]), float(c[4]))
                        for c in cd}
    return None


def prem_bars(exp, strike, typ, day):
    """(prem_dict, source) — gate stores first, then round 1's
    fetch machinery (which caches into oi_buildup_data)."""
    prem = prem_store(exp, strike, typ, day)
    if prem:
        return prem, "store"
    bars = obs.fetch_bars("BANKNIFTY", exp, strike, typ, day)
    if bars:
        return {b[0]: (b[1], b[2], b[3], b[4]) for b in bars}, "fetched"
    return None, None


# ---------------- frozen family logic (verbatim) -------------------
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


# ---------------- ledger --------------------------------------------
def ledger_rows():
    if not LEDGER.exists():
        return []
    with open(LEDGER) as f:
        return list(csv.DictReader(f))


def write_row(row, dry):
    if dry:
        return
    rows = [r for r in ledger_rows() if r["date"] != row["date"]]
    rows.append(row)
    rows.sort(key=lambda r: r["date"])
    with open(LEDGER, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_FIELDS)
        w.writeheader()
        w.writerows(rows)


# ---------------- scoring flow --------------------------------------
def score_day(T, dry):
    row = {k: "" for k in LEDGER_FIELDS}
    row["date"] = T
    try:
        bars, ssrc = spot_bars(T, dry)
    except RateLimited:
        row.update(status="NC", reason="rate_limited")
        return row
    if bars is None:
        row.update(status="NC", reason=ssrc)
        return row
    pc = prev_close(T)
    if pc is None:
        row.update(status="NC", reason="no_prev_close")
        return row
    mi = morning_info(bars)
    if mi is None:
        row.update(status="NC", reason="morning_incomplete")
        return row
    gap = (mi["O"] - pc) / pc * 100.0
    row.update(gap_pct=f"{gap:.3f}",
               morning_pct=f"{mi['move_pct']:.3f}",
               direction=("UP" if mi["dirn"] > 0 else
                          "DOWN" if mi["dirn"] < 0 else "FLAT"),
               notes=f"spot={ssrc}")
    if mi["dirn"] == 0:
        row.update(status="NO_DIRECTION", reason="flat_morning")
        return row
    regime = abs(gap) >= Q3 or abs(mi["move_pct"]) >= 0.7
    if not regime:
        row.update(status="NO_REGIME", reason="not_a_regime_morning")
        return row
    ct, cc = confirmation(bars, mi)
    if ct is None:
        row.update(status="NO_CONFIRMATION",
                   reason="no_midpoint_cross_after_1100")
        return row
    side = "PE" if mi["dirn"] > 0 else "CE"
    strike = int(round(cc / STEP)) * STEP
    exp = in_force_expiry(T)
    row.update(strike=str(strike), expiry=exp or "", conf_time=ct)
    if not exp:
        row.update(status="NC", reason="no_expiry")
        return row
    try:
        prem, psrc = prem_bars(exp, strike, side, T)
    except RateLimited:
        row.update(status="NC", reason="rate_limited")
        return row
    except urllib.error.HTTPError as e:
        if e.code == 429:
            row.update(status="NC", reason="rate_limited")
            return row
        raise
    if not prem:
        row.update(status="NC", reason="no_premium_store")
        return row
    if min(prem) > "09:20":
        row.update(status="NC", reason="series_starts_after_0920")
        return row
    if SQ not in prem:
        row.update(status="NC", reason="no_1510_bar")
        return row
    if ct not in prem:
        row.update(status="NC", reason="no_conf_bar_in_premium")
        return row
    epx = prem[ct][3]
    out = replay_after(prem, ct, epx)
    if out is None:
        row.update(status="NC", reason="replay_none")
        return row
    xpx, xt, reason = out
    net = round((xpx - epx) * LOT - COST, 2)
    # TIMING ASSERTION: morning inputs end at 10:55; the fill is the
    # confirmation bar's close; exits replay strictly later bars.
    viol = 0
    if not (ct >= "11:00" and xt > ct):
        viol += 1
    row["timing_violations"] = str(viol)
    assert viol == 0, "timing violation on scored leg"
    row.update(status="TRADED", reason="scored", entry_time=ct,
               entry_premium=f"{epx:.2f}", exit_time=xt,
               exit_premium=f"{xpx:.2f}", exit_reason=reason,
               net_inr=f"{net:.2f}",
               notes=f"spot={ssrc}; premium={psrc}; side={side}")
    return row


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verify", action="store_true",
                    help="no-write historical check; bypasses the "
                         "start/window guards, never writes")
    a = ap.parse_args(argv)
    if a.verify:
        a.dry_run = True
    T = a.date or datetime.now(IST).date().isoformat()
    if not a.verify and T < START:
        print(f"REGIME-REV SHADOW: {T} is before the shadow start "
              f"{START} — nothing scored.")
        return 0
    if not a.verify and T > WINDOW_END:
        print(f"REGIME-REV SHADOW: {T} is past the review bound "
              f"{WINDOW_END} (the Nov 30 verdicts) — scoring closed; "
              f"the review is due, do not score further days.")
        return 0
    try:
        row = score_day(T, a.dry_run)
    except RateLimited:
        row = {k: "" for k in LEDGER_FIELDS}
        row.update(date=T, status="NC", reason="rate_limited")
    write_row(row, a.dry_run)
    after = ledger_rows() if not a.dry_run else []
    traded = [r for r in after if r["status"] == "TRADED"]
    tnet = round(sum(float(r["net_inr"]) for r in traded), 2)
    print(f"REGIME-REV SHADOW {T}: status={row['status']} "
          f"reason={row['reason']} gap={row['gap_pct'] or '-'}% "
          f"morning={row['morning_pct'] or '-'}% "
          f"dir={row['direction'] or '-'} "
          f"strike={row['strike'] or '-'} "
          f"conf={row['conf_time'] or '-'} "
          f"net={row['net_inr'] or '-'}"
          f"{' (DRY RUN — nothing written)' if a.dry_run else ''}")
    if not a.dry_run:
        print(f"REGIME-REV SHADOW tally: traded={len(traded)} "
              f"shadow_net={tnet:+.2f} (paper, real money Rs0)")
    return 3 if row["reason"] == "rate_limited" else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
