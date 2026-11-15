#!/usr/bin/env python3
"""OI BUILD-UP PROGRAMME - Part 2 scorer (2026-11-13).

Frozen family (registered in oi_buildup_programme_2026-11-13.md BEFORE
this scorer was run):
Signal at the close of day D from the reconstructed daily OI dataset
(oi_history/): spot day change s (points) and same-contract day-over-day
OI changes dCE, dPE summed over the ATM band (spot +/-5 strikes) of the
in-force expiry. Quadrants per side (PE premium change proxied by -s):
  CE: LONG_BUILDUP s>0,dCE>0 | SHORT_BUILDUP s<0,dCE>0 |
      LONG_UNWINDING s<0,dCE<0 | SHORT_COVERING s>0,dCE<0 | FLAT else
  PE: LONG_BUILDUP s<0,dPE>0 | SHORT_BUILDUP s>0,dPE>0 |
      LONG_UNWINDING s>0,dPE<0 | SHORT_COVERING s<0,dPE<0 | FLAT else
V1 (aligned): CE iff CE==LONG_BUILDUP and PE==SHORT_BUILDUP;
              PE iff CE==SHORT_BUILDUP and PE==LONG_BUILDUP.
V2 (writer-led): CE iff PE==SHORT_BUILDUP; PE iff CE==SHORT_BUILDUP.
Trade: next trading day, ONE leg, entry at the OPEN of the 09:20 5-min
bar, strike = ATM (nearest step) to that bar's spot open, contract =
in-force expiry of the trade day (Bank monthly / Nifty weekly-front).
Exits: Bank G0 (stop -50 before target +90 on every bar incl. entry
bar, fills at level, square-off at the 15:10 bar close; lot 30);
Nifty frozen S5 (ported from nifty_next_phase_score.py; lot 65).
Cost Rs220/trade. UNIQUE-ONCE by construction.
Placebos per index per variant: REVERSED direction, COIN-FLIP direction
(seed 42), SHIFTED signal (quadrant of the trading day before the
signal day, same trade days).
Gate (per index per variant): total > 0; both halves (Jan-May /
Jun-Oct by trade date) > 0; ex-top-3 > 0; total strictly beats all
three placebos; timing violations = 0; NC <= 5% of signal days.
November counterfactual: trades dated 2026-11-02..2026-11-12 (lens).
Paper only, real money Rs0. No frozen book touched.
"""
import csv, json, random, sys, time
import urllib.request, urllib.error
from pathlib import Path
from urllib.parse import quote

TR = Path.home() / "workspace/trading"
OI = TR / "oi_history"
FETCH_DIR = TR / "oi_buildup_data"
FETCH_DIR.mkdir(exist_ok=True)
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
API = "https://api.upstox.com"
COST = 220.0
CONF = {"BANKNIFTY": dict(lot=30, step=100, geom="G0"),
        "NIFTY": dict(lot=65, step=50, geom="S5")}
IDXKEY = {"BANKNIFTY": "NSE_INDEX|Nifty Bank", "NIFTY": "NSE_INDEX|Nifty 50"}

token = None
for line in (TR / "upstox_refresh/.env").read_text().splitlines():
    if line.startswith("UPSTOX_ACCESS_TOKEN="):
        token = line.split("=", 1)[1].strip()
assert token

def get(url):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}", "Accept": "application/json",
        "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read())

class RateLimited(Exception):
    pass

# ---------------- spot bars ----------------
spot_raw = json.load(open(TR / "daily2leg/spot.json"))
nov_bars = json.loads((OI / "spot_nov_bars.json").read_text())
SPOT = {}
for idx in CONF:
    dmap = {}
    for d, bars in spot_raw[idx].items():
        dmap[d] = {b[0]: (float(b[1]), float(b[2]), float(b[3]),
                          float(b[4])) for b in bars}
    for d, bars in nov_bars.get(idx, {}).items():
        dmap.setdefault(d, {b[0]: (b[1], b[2], b[3], b[4]) for b in bars})
    SPOT[idx] = dmap
CAL = sorted(d for d in SPOT["NIFTY"] if d in SPOT["BANKNIFTY"])
NEXT = {CAL[i]: CAL[i + 1] for i in range(len(CAL) - 1)}
PREV = {CAL[i]: CAL[i - 1] for i in range(1, len(CAL))}

# ---------------- OI dataset + quadrants ----------------
def load_oi(idx):
    rows = {}
    with open(OI / (idx.lower() + "_daily_oi.csv")) as f:
        for r in csv.DictReader(f):
            rows[r["date"]] = r
    return rows

def _sgn(x):
    return 1 if x > 0 else (-1 if x < 0 else 0)

def quadrants(row):
    if row is None or row["spot_chg_pts"] in (None, "") \
            or row["d_ce_oi"] in (None, "") or row["d_pe_oi"] in (None, ""):
        return None
    s = _sgn(float(row["spot_chg_pts"]))
    dce, dpe = _sgn(float(row["d_ce_oi"])), _sgn(float(row["d_pe_oi"]))
    if s == 0 or dce == 0 or dpe == 0:
        return ("FLAT", "FLAT")
    ce = {(1, 1): "LONG_BUILDUP", (-1, 1): "SHORT_BUILDUP",
          (-1, -1): "LONG_UNWINDING", (1, -1): "SHORT_COVERING"}[(s, dce)]
    pe = {(-1, 1): "LONG_BUILDUP", (1, 1): "SHORT_BUILDUP",
          (1, -1): "LONG_UNWINDING", (-1, -1): "SHORT_COVERING"}[(s, dpe)]
    return (ce, pe)

def direction(variant, q):
    if q is None:
        return None
    ce, pe = q
    if variant == "V1":
        if ce == "LONG_BUILDUP" and pe == "SHORT_BUILDUP":
            return "CE"
        if ce == "SHORT_BUILDUP" and pe == "LONG_BUILDUP":
            return "PE"
        return None
    if pe == "SHORT_BUILDUP":
        return "CE"
    if ce == "SHORT_BUILDUP":
        return "PE"
    return None

# ---------------- premium bars ----------------
PREM_B = json.load(open(TR / "daily2leg/prem_bank.json"))
PREM_N = json.load(open(TR / "daily2leg/prem_nifty.json"))
PREM_NW = json.load(open(TR / "daily2leg/prem_nifty_weekly.json"))

def store_bars(idx, exp, strike, typ, day):
    key = f"{exp}|{int(strike)}|{typ}"
    stores = (PREM_B,) if idx == "BANKNIFTY" else (PREM_NW, PREM_N)
    for st in stores:
        cd = st.get(key, {}).get(day)
        if cd:
            return sorted((t, float(v[0]), float(v[1]), float(v[2]),
                           float(v[3])) for t, v in cd.items()), "store"
    for folder in ("btst_data", "november_shadow_data",
                   "nifty_weekly_expiry_chain"):
        fn = TR / folder / f"candles_{idx}_{int(strike)}{typ}_{exp}_{day}.json"
        if fn.exists():
            body = json.loads(fn.read_text())
            cd = [c for c in ((body.get("data") or {}).get("candles") or [])
                  if c[0][:10] == day]
            if cd:
                return sorted((c[0][11:16], float(c[1]), float(c[2]),
                               float(c[3]), float(c[4])) for c in cd), folder
    fn = FETCH_DIR / f"candles_{idx}_{int(strike)}{typ}_{exp}_{day}.json"
    if fn.exists():
        body = json.loads(fn.read_text())
        cd = [c for c in ((body.get("data") or {}).get("candles") or [])
              if c[0][:10] == day]
        if cd:
            return sorted((c[0][11:16], float(c[1]), float(c[2]),
                           float(c[3]), float(c[4])) for c in cd), "fetched"
    return None, None

_key_cache = {}
def fetch_bars(idx, exp, strike, typ, day):
    if exp < "2026-11-13":
        ck = (idx, exp)
        if ck not in _key_cache:
            body = get(f"{API}/v2/expired-instruments/option/contract"
                       f"?instrument_key={quote(IDXKEY[idx], safe='')}"
                       f"&expiry_date={exp}")
            _key_cache[ck] = {
                (int(float(c["strike_price"])), c["instrument_type"]):
                c["instrument_key"] for c in (body.get("data") or [])}
        key = _key_cache[ck].get((int(strike), typ))
        if not key:
            return None
        url = (f"{API}/v2/expired-instruments/historical-candle/"
               f"{quote(key, safe='')}/5minute/{day}/{day}")
    else:
        rows = json.loads((TR / "daily2leg/instruments_cache.json")
                          .read_text())["rows"]
        key = next((r["key"] for r in rows if r["name"] == idx
                    and r["expiry"] == exp
                    and int(float(r["strike"])) == int(strike)
                    and r["option_type"] == typ), None)
        if not key:
            return None
        url = (f"{API}/v3/historical-candle/{quote(key, safe='')}"
               f"/minutes/5/{day}/{day}")
    try:
        body = get(url)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RateLimited()
        return None
    cd = [c for c in ((body.get("data") or {}).get("candles") or [])
          if c[0][:10] == day]
    if not cd:
        return None
    fn = FETCH_DIR / f"candles_{idx}_{int(strike)}{typ}_{exp}_{day}.json"
    fn.write_text(json.dumps(body))
    time.sleep(0.3)
    return sorted((c[0][11:16], float(c[1]), float(c[2]), float(c[3]),
                   float(c[4])) for c in cd)

def prem_bars(idx, exp, strike, typ, day):
    bars, src = store_bars(idx, exp, strike, typ, day)
    if bars:
        return bars, src
    bars = fetch_bars(idx, exp, strike, typ, day)
    return (bars, "fetched") if bars else (None, None)

# ---------------- exit replays ----------------
def replay_g0(bars, lot):
    bs = [b for b in bars if b[0] >= "09:20"]
    if not bs or bs[0][0] != "09:20":
        return None
    entry = bs[0][1]
    stop, target, sq = entry - 50.0, entry + 90.0, "15:10"
    def out(px, reason, t, ft):
        return dict(entry=entry, exit=px, exit_time=t, exit_reason=reason,
                    ft=ft, net=round((px - entry) * lot - COST, 2))
    for (t, o, h, l, cl) in bs:
        if t > sq:
            break
        if l <= stop:
            return out(stop, "stop", t, 0)
        if h >= target:
            return out(target, "target", t, 1)
        if t == sq:
            return out(cl, "square_off", t, 0)
    lb = bs[-1]
    return out(lb[4], "square_off", lb[0], 0)

def replay_s5(bars, lot):
    entry_time, sq = "09:20", "15:20"
    if not bars:
        return None
    idxs = [i for i, b in enumerate(bars) if b[0] >= entry_time]
    if not idxs:
        return None
    bs = bars[idxs[0]:]
    if bs[0][0] > sq or bs[0][0] != entry_time:
        return None
    entry = bs[0][1]
    stop, target = entry - 50.0, entry + 90.0
    lock, tgt2, arm = 60.0, 175.0, 50.0
    def out(pts, reason, t, ft, px):
        return dict(entry=entry, exit=px, exit_time=t, exit_reason=reason,
                    ft=ft, net=round(pts * lot - COST, 2))
    cur_stop = stop
    for i, (t, o, h, l, cl) in enumerate(bs):
        if t > sq:
            break
        if l <= cur_stop:
            return out(cur_stop - entry,
                       "be_stop" if cur_stop == entry else "stop", t, 0,
                       cur_stop)
        if h >= target:
            stop2, target2 = entry + lock, entry + tgt2
            for (t2, o2, h2, l2, cl2) in bs[i + 1:]:
                if t2 > sq:
                    break
                if l2 <= stop2:
                    return out(stop2 - entry, "runner_stop", t2, 1, stop2)
                if h2 >= target2:
                    return out(target2 - entry, "runner_target", t2, 1,
                               target2)
                if t2 == sq:
                    return out(cl2 - entry, "runner_square_off", t2, 1, cl2)
            lb = bs[-1]
            return out(lb[4] - entry, "runner_square_off", lb[0], 1, lb[4])
        if (h - entry) >= arm:
            cur_stop = max(cur_stop, entry)
        if t == sq:
            return out(cl - entry, "square_off", t, 0, cl)
    lb = bs[-1]
    return out(lb[4] - entry, "square_off", lb[0], 0, lb[4])

# ---------------- scoring ----------------
def run_book(idx, variant, mode, oi):
    cfg = CONF[idx]
    rng = random.Random(42)
    trades, nc = [], []
    sig_days = [d for d in sorted(oi)
                if "2026-01-01" <= d <= "2026-11-11" and d in NEXT]
    for d in sig_days:
        row = oi[d]
        if row["status"] != "complete":
            continue
        q = quadrants(row)
        src_day = d
        if mode == "shifted":
            pd = PREV.get(d)
            q = quadrants(oi.get(pd)) if pd else None
            src_day = pd
        dirn = direction(variant, q)
        if dirn is None:
            continue
        if mode == "reversed":
            dirn = "PE" if dirn == "CE" else "CE"
        elif mode == "coin":
            dirn = "CE" if rng.random() < 0.5 else "PE"
        tday = NEXT[d]
        exp = oi[tday]["expiry"] if tday in oi else None
        sbar = SPOT[idx].get(tday, {}).get("09:20")
        if exp is None or sbar is None:
            nc.append(dict(signal_date=d, trade_date=tday,
                           why="no_spot_or_expiry"))
            continue
        strike = int(round(sbar[0] / cfg["step"])) * cfg["step"]
        bars, src = prem_bars(idx, exp, strike, dirn, tday)
        if not bars:
            nc.append(dict(signal_date=d, trade_date=tday,
                           why="no_premium_candles"))
            continue
        r = replay_g0(bars, cfg["lot"]) if cfg["geom"] == "G0" \
            else replay_s5(bars, cfg["lot"])
        if r is None:
            nc.append(dict(signal_date=d, trade_date=tday,
                           why="replay_none"))
            continue
        trades.append(dict(index=idx, variant=variant, mode=mode,
                           signal_date=d, src_signal_date=src_day,
                           trade_date=tday, direction=dirn, strike=strike,
                           expiry=exp, ce_q=q[0], pe_q=q[1], store=src,
                           **r))
    return trades, nc

def stats(trades):
    gate = [t for t in trades if t["trade_date"] <= "2026-10-31"]
    total = round(sum(t["net"] for t in gate), 2)
    months = {}
    for m in sorted({t["trade_date"][:7] for t in gate}):
        months[m] = round(sum(t["net"] for t in gate
                              if t["trade_date"][:7] == m), 2)
    h1 = round(sum(t["net"] for t in gate
                   if t["trade_date"][:7] <= "2026-05"), 2)
    h2 = round(sum(t["net"] for t in gate
                   if t["trade_date"][:7] >= "2026-06"), 2)
    top3 = sorted((t["net"] for t in gate), reverse=True)[:3]
    nov = [t for t in trades if "2026-11-02" <= t["trade_date"]
           <= "2026-11-12"]
    return dict(n=len(gate), total=total, months=months, h1=h1, h2=h2,
                ex_top3=round(total - sum(top3), 2), top3=top3,
                ft=sum(t["ft"] for t in gate),
                pace_per_month=round(total / 10, 2),
                nov_n=len(nov),
                nov_total=round(sum(t["net"] for t in nov), 2),
                nov_trades=[{k: t[k] for k in
                             ("signal_date", "trade_date", "direction",
                              "strike", "expiry", "entry", "exit",
                              "exit_time", "exit_reason", "net")}
                            for t in nov])

def main():
    results = {}
    all_trades = []
    try:
        for idx in CONF:
            oi = load_oi(idx)
            results[idx] = {}
            for variant in ("V1", "V2"):
                entry = {}
                real, nc = run_book(idx, variant, "real", oi)
                entry["real"] = stats(real)
                entry["nc"] = nc
                entry["timing_violations"] = sum(
                    1 for t in real if not t["signal_date"] < t["trade_date"])
                for mode in ("reversed", "coin", "shifted"):
                    pl, _ = run_book(idx, variant, mode, oi)
                    entry[mode] = stats(pl)
                    all_trades += pl
                all_trades += real
                s, e = entry["real"], entry
                legs = dict(
                    total_pos=s["total"] > 0,
                    halves_pos=s["h1"] > 0 and s["h2"] > 0,
                    ex_top3_pos=s["ex_top3"] > 0,
                    beats_reversed=s["total"] > e["reversed"]["total"],
                    beats_coin=s["total"] > e["coin"]["total"],
                    beats_shifted=s["total"] > e["shifted"]["total"],
                    timing_clean=e["timing_violations"] == 0,
                    nc_ok=len(nc) <= max(1, int(0.05 * (s["n"] + len(nc)))),
                )
                entry["gate_legs"] = legs
                entry["gate_pass"] = all(legs.values())
                results[idx][variant] = entry
                print(f"{idx} {variant}: n={s['n']} total={s['total']} "
                      f"H=({s['h1']},{s['h2']}) ex3={s['ex_top3']} "
                      f"pace={s['pace_per_month']} NC={len(nc)} "
                      f"PASS={entry['gate_pass']} legs={legs}", flush=True)
                print(f"   placebos: rev={e['reversed']['total']} "
                      f"coin={e['coin']['total']} "
                      f"shift={e['shifted']['total']} | NOV n={s['nov_n']} "
                      f"total={s['nov_total']}", flush=True)
    except RateLimited:
        print("RATE_LIMIT_STOP during scoring fetch - partial results",
              flush=True)
        results["rate_limited"] = True
    with open(TR / "oi_buildup_trades.csv", "w", newline="") as f:
        if all_trades:
            w = csv.DictWriter(f, fieldnames=list(all_trades[0].keys()))
            w.writeheader()
            w.writerows(all_trades)
    chk = {}
    with open(TR / "oi_buildup_trades.csv") as f:
        for r in csv.DictReader(f):
            if r["mode"] == "real" and r["trade_date"] <= "2026-10-31":
                k = (r["index"], r["variant"])
                chk[k] = round(chk.get(k, 0.0) + float(r["net"]), 2)
    for idx in list(results):
        if not isinstance(results[idx], dict):
            continue
        for variant in ("V1", "V2"):
            mine = results[idx][variant]["real"]["total"]
            assert chk.get((idx, variant)) == mine, \
                f"RESUM MISMATCH {idx} {variant}"
    results["resum_check"] = "EXACT for all real books"
    (TR / "oi_buildup_results.json").write_text(json.dumps(results, indent=1))
    print("re-sum EXACT; results -> oi_buildup_results.json")

if __name__ == "__main__":
    main()
