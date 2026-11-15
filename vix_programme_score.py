#!/usr/bin/env python3
"""VIX PROGRAMME scorer (2026-11-15). Spec frozen in
vix_programme_SPEC.md BEFORE this ran. Machinery: frozen Round-1
scorer (oi_buildup_score.py) imported unmodified + the full-day
premium repair from round2_score.py. Paper only, real money Rs0.
On HTTP 429: hard stop, partial results saved and flagged."""
import csv, json, random, sys
import importlib.util
from pathlib import Path

TR = Path.home() / "workspace/trading"
spec = importlib.util.spec_from_file_location(
    "obs", TR / "oi_buildup_score.py")
obs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(obs)

# ---- full-day premium repair (verbatim logic from round2_score.py)
_orig_prem_bars = obs.prem_bars


def prem_bars_full(idx, exp, strike, typ, day):
    bars, src = _orig_prem_bars(idx, exp, strike, typ, day)
    if bars and bars[0][0] <= "09:20":
        return bars, src
    fn = obs.FETCH_DIR / f"candles_{idx}_{int(strike)}{typ}_{exp}_{day}.json"
    if fn.exists():
        body = json.loads(fn.read_text())
        cd = [c for c in ((body.get("data") or {}).get("candles") or [])
              if c[0][:10] == day]
        if cd:
            fb = sorted((c[0][11:16], float(c[1]), float(c[2]),
                         float(c[3]), float(c[4])) for c in cd)
            if fb[0][0] <= "09:20":
                return fb, "fetched_cache"
    fb = obs.fetch_bars(idx, exp, strike, typ, day)
    if fb:
        return fb, "fetched_full"
    return bars, src


obs.prem_bars = prem_bars_full

COST = 220.0
CONF = {"BANKNIFTY": dict(lot=30, step=100), "NIFTY": dict(lot=65, step=50)}
CAL = obs.CAL            # joint spot calendar (2025-01 .. 2026-11)
NEXT = obs.NEXT
PREV = obs.PREV
SPOT = obs.SPOT
LAST_TRADE_DAY = "2026-10-30"

# ---------------- daily closes / DMA / spot change ----------------
CLOSE = {}
for idx in CONF:
    CLOSE[idx] = {}
    for d, bars in SPOT[idx].items():
        if bars:
            t = max(bars)
            CLOSE[idx][d] = bars[t][3]


def dma20(idx, d):
    """Mean of closes of d and the 19 prior calendar days."""
    days = []
    x = d
    while x is not None and len(days) < 20:
        if x in CLOSE[idx]:
            days.append(CLOSE[idx][x])
        x = PREV.get(x)
    if len(days) < 20:
        return None
    return sum(days) / 20.0


def spot_chg_pct(idx, d):
    p = PREV.get(d)
    if p is None or p not in CLOSE[idx] or d not in CLOSE[idx]:
        return None
    return (CLOSE[idx][d] / CLOSE[idx][p] - 1.0) * 100.0


# ---------------- VIX ----------------
VIX = {}
for r in csv.DictReader(open(TR / "round2_history/india_vix_daily.csv")):
    VIX[r["date"]] = float(r["vix_close"]) if r["vix_close"] else None


def vix(d):
    return VIX.get(d)


# ---------------- OI expiry map ----------------
OI = {idx: obs.load_oi(idx) for idx in CONF}


def expiry_of(idx, day):
    row = OI[idx].get(day)
    return row["expiry"] if row else None


# ---------------- plain -50/+90 exit replay (frozen by the task) ----
def replay_plain(bars, lot):
    bs = [b for b in bars if b[0] >= "09:20"]
    if not bs or bs[0][0] != "09:20":
        return None
    entry = bs[0][1]
    stop, target, sq = entry - 50.0, entry + 90.0, "15:20"

    def out(px, reason, t):
        return dict(entry=entry, exit=px, exit_time=t,
                    exit_reason=reason,
                    net=round((px - entry) * lot - COST, 2))
    for (t, o, h, l, cl) in bs:
        if t > sq:
            break
        if l <= stop:
            return out(stop, "stop", t)
        if h >= target:
            return out(target, "target", t)
        if t == sq:
            return out(cl, "square_off", t)
    lb = bs[-1]
    return out(lb[4], "square_off", lb[0])


_bar_cache = {}


def get_bars(idx, exp, strike, typ, day):
    k = (idx, exp, int(strike), typ, day)
    if k not in _bar_cache:
        _bar_cache[k] = obs.prem_bars(idx, exp, strike, typ, day)
    return _bar_cache[k]


def construct(idx, tday, dirn):
    """Build one trade on tday; returns (trade, None) or (None, why)."""
    exp = expiry_of(idx, tday)
    sbar = SPOT[idx].get(tday, {}).get("09:20")
    if exp is None or sbar is None:
        return None, "no_spot_or_expiry"
    strike = int(round(sbar[0] / CONF[idx]["step"])) * CONF[idx]["step"]
    bars, src = get_bars(idx, exp, strike, dirn, tday)
    if not bars:
        return None, "no_premium_candles"
    r = replay_plain(bars, CONF[idx]["lot"])
    if r is None:
        return None, "replay_none"
    return dict(index=idx, trade_date=tday, direction=dirn,
                strike=strike, expiry=exp, store=src, **r), None


# ================= PART A — ANATOMY =================
BANDS = ["<12", "12-14", "14-17", "17-20", ">20"]


def band_of(v):
    if v < 12:
        return "<12"
    if v < 14:
        return "12-14"
    if v < 17:
        return "14-17"
    if v < 20:
        return "17-20"
    return ">20"


def part_a():
    files = {
        "BANKNIFTY": ("TUNED STACK v2",
                      "solid60_programme_2026-11-13_bank_A_stack_ALL_X-1_trades.csv",
                      111, 127351.50),
        "NIFTY": ("TUNED v1",
                  "solid60_programme_2026-11-13_nifty_v1_ALL_X-1_trades.csv",
                  74, 103050.25),
    }
    out = {}
    for idx, (name, fn, exp_n, exp_net) in files.items():
        legs = list(csv.DictReader(open(TR / fn)))
        tot = round(sum(float(r["net_inr"]) for r in legs), 2)
        assert len(legs) == exp_n and abs(tot - exp_net) < 0.01, \
            (idx, len(legs), tot)
        bands = {b: [] for b in BANDS}
        nc = []
        for r in legs:
            d = r["date"]
            p = PREV.get(d)
            v = vix(p) if p else None
            if v is None:
                nc.append(d)
                continue
            bands[band_of(v)].append(r)
        rows = {}
        for b in BANDS:
            ls = bands[b]
            net = round(sum(float(r["net_inr"]) for r in ls), 2)
            days = len({r["date"] for r in ls})
            wins = sum(1 for r in ls if float(r["net_inr"]) > 0)
            rows[b] = dict(
                legs=len(ls), net=net,
                wr=round(100.0 * wins / len(ls), 1) if ls else None,
                trade_days=days,
                rs_per_trade_day=round(net / days, 2) if days else None)
        out[idx] = dict(book=name, legs=len(legs), total=tot,
                        bands=rows, nc_legs=len(nc), nc_dates=nc)
    return out


# ================= PART B — RULES =================
def sig_v1(idx, d):
    v = vix(d)
    if v is None or v >= 12:
        return None
    m = dma20(idx, d)
    if m is None or d not in CLOSE[idx]:
        return None
    return "CE" if CLOSE[idx][d] > m else None


def spike_day(idx, d):
    p = PREV.get(d)
    if p is None:
        return False
    a, b = vix(d), vix(p)
    if a is None or b is None:
        return False
    if (a / b - 1.0) * 100.0 < 15.0:
        return False
    chg = spot_chg_pct(idx, d)
    return chg is not None and chg <= -1.0


def sig_v2(idx, d):
    if not spike_day(idx, d):
        return None
    p = PREV.get(d)
    if p is not None and spike_day(idx, p):
        return None          # not the first day of the spike run
    return "CE"


SIG = {"V1": sig_v1, "V2": sig_v2}


def run_rule(idx, rule):
    trades, nc = [], []
    sig_days = [d for d in CAL
                if "2025-12-31" <= d and d in NEXT
                and NEXT[d] <= LAST_TRADE_DAY]
    for d in sig_days:
        dirn = SIG[rule](idx, d)
        if dirn is None:
            continue
        tday = NEXT[d]
        t, why = construct(idx, tday, dirn)
        if t is None:
            nc.append(dict(signal_date=d, trade_date=tday, why=why))
            continue
        t["rule"] = rule
        t["signal_date"] = d
        trades.append(t)
    return trades, nc


def gate_lite(idx, rule, trades):
    total = round(sum(t["net"] for t in trades), 2)
    h1 = round(sum(t["net"] for t in trades
                   if t["trade_date"][:7] <= "2026-05"), 2)
    h2 = round(sum(t["net"] for t in trades
                   if t["trade_date"][:7] >= "2026-06"), 2)
    top3 = sorted((t["net"] for t in trades), reverse=True)[:3]
    ex3 = round(total - sum(top3), 2)
    months = {}
    for m in sorted({t["trade_date"][:7] for t in trades}):
        mt = [t for t in trades if t["trade_date"][:7] == m]
        months[m] = dict(n=len(mt),
                         net=round(sum(t["net"] for t in mt), 2))
    wins = sum(1 for t in trades if t["net"] > 0)
    # random-entry placebo: 200 draws, same count, random distinct days
    rng = random.Random(42)
    pool = [d for d in CAL if "2026-01-01" <= d <= LAST_TRADE_DAY]
    draws = []
    n = len(trades)
    if n:
        for _ in range(200):
            picked, tot, guard = [], 0.0, 0
            used = set()
            while len(picked) < n and guard < 40 * n:
                guard += 1
                d = pool[rng.randrange(len(pool))]
                if d in used:
                    continue
                t, _w = construct(idx, d, "CE")
                if t is None:
                    continue
                used.add(d)
                picked.append(t)
                tot += t["net"]
            draws.append(round(tot, 2))
        pct = round(100.0 * sum(1 for x in draws if x <= total)
                    / len(draws), 1) if draws else None
        med = sorted(draws)[len(draws) // 2] if draws else None
    else:
        pct, med = None, None
    fails = []
    if not total > 0:
        fails.append("total <= 0")
    if not h1 > 0:
        fails.append("Jan-May half <= 0")
    if not h2 > 0:
        fails.append("Jun-Oct half <= 0")
    if not ex3 > 0:
        fails.append("ex-top-3 <= 0")
    if pct is None or pct < 95:
        fails.append("placebo percentile < 95")
    return dict(trades=n, net=total,
                wr=round(100.0 * wins / n, 1) if n else None,
                h1=h1, h2=h2, ex_top3=ex3, top3=top3, months=months,
                placebo_pct=pct, placebo_median=med,
                verdict="PASS" if not fails else "FAIL",
                failing_legs=fails)


def main():
    results = {"scope": "VIX programme 2026-11-15 — Jan-Oct 2026",
               "vix_source": "round2_history/india_vix_daily.csv "
                             "(Yahoo Finance ^INDIAVIX daily closes, "
                             "Round-2 dataset; 203/205 Jan-Oct days, "
                             "missing 2026-01-01 and 2026-02-01)"}
    all_trades = []
    try:
        results["part_a"] = part_a()
        results["part_b"] = {}
        for idx in ("BANKNIFTY", "NIFTY"):
            results["part_b"][idx] = {}
            for rule in ("V1", "V2"):
                trades, nc = run_rule(idx, rule)
                g = gate_lite(idx, rule, trades)
                g["nc"] = len(nc)
                g["nc_rows"] = nc
                results["part_b"][idx][rule] = g
                all_trades.extend(trades)
                print(idx, rule, g["trades"], g["net"], g["verdict"],
                      "NC", len(nc), flush=True)
    except obs.RateLimited:
        results["RATE_LIMITED"] = True
        print("RATE LIMITED — partial save", flush=True)
    (TR / "vix_programme_results.json").write_text(
        json.dumps(results, indent=1))
    with open(TR / "vix_programme_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "index", "rule", "signal_date", "trade_date", "direction",
            "strike", "expiry", "entry", "exit", "exit_time",
            "exit_reason", "net", "store"])
        w.writeheader()
        for t in all_trades:
            w.writerow({k: t.get(k) for k in w.fieldnames})
    print("saved", flush=True)


if __name__ == "__main__":
    main()
