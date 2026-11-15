#!/usr/bin/env python3
"""DAILY BASE-LOAD FALLBACK — NOVEMBER COUNTERFACTUAL (companion to
tuning_daily_baseload_2026-11-12.py; frozen spec in that file's header).
November 2026, Nov 2-12 (8 trading days; Nov 10 holiday).

Signals: the day's U1 sysmap is rebuilt with the SAME machinery the
live shadow scorer uses — live_signal_producer.evaluate_legs over the
day's spot (november_shadow_score.day_context / producer_legs), with
the producer state (Volrix last-entry, V5 week-use) initialised
exactly as the scorer's state began (P.VOLRIX_LAST_ENTRY, empty
v5_days) and advanced day by day via note_state_after. Per-system
entry_time = plus5(signal_time) (the U1 merge convention, identical
to the sysmap semantics used Jan-Oct). Cross-checks: reconstructed
Skill V3 legs vs november_shadow_skill_{bank,nifty}_log.csv, and the
reconstructed Nifty sysmaps vs the sysmaps recorded in the DEC-S1
shadow log's no-trade notes.

Incumbent November books (recorded):
  BANK stack ledger (november_shadow_stack_bank_log.csv): legs
  Nov 4 09:55 (+2,480), Nov 9 10:45 (-1,720), Nov 12 11:30 (-1,720);
  recorded total -960 (incl backfill); live-only (Nov 11-12) -1,720.
  All leg days have entries <= 13:30 -> ineligible. Idle (eligible)
  days: Nov 2, 3, 5, 6, 11.
  NIFTY TUNED v1 forward: Nov 3 C CE 09:50 (+3,036.50) only (DEC-S1
  minus its B PE legs). Idle days: Nov 2, 4, 5, 6, 9, 11, 12.
Fallback legs (if any signal >= 13:30 on an idle day): strike
atm100(spot open at t*), expiry 2026-11-23, premium via
november_shadow_fetch.fetch_premium (cache-first; HTTP 429 = hard
stop -> remaining legs NOT_COMPUTED, never estimated). Geometry:
BANK sim_g0 lot 30; NIFTY replay_r5 STANDING_GEOM lot 65; Rs 220.
"""
import csv, json, sys, urllib.error
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path.home() / "workspace/trading"))
TR = Path.home() / "workspace/trading"
import live_signal_producer as P
import november_shadow_score as NS
import november_shadow_fetch as F

TRIGGER, LAST_ENTRY, EXP = "13:30", "15:05", "2026-11-23"
DAYS = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05",
        "2026-11-06", "2026-11-09", "2026-11-11", "2026-11-12"]

def plus5(t):
    h, m = int(t[:2]), int(t[3:]) + 5
    return f"{h + m // 60:02d}:{m % 60:02d}"

def sim_g0(pd, entry_time, entry_prem, lot=30):
    stop_lvl, tgt_lvl = entry_prem - 50.0, entry_prem + 90.0
    for t in sorted(pd):
        if t < entry_time or t > "15:05": continue
        o, h, l, c = pd[t]
        if l <= stop_lvl: return t, stop_lvl, "stop"
        if h >= tgt_lvl: return t, tgt_lvl, "target"
    if "15:10" in pd: return "15:10", pd["15:10"][0], "square_off"
    last = max(t for t in pd if t <= "15:05")
    return last, pd[last][3], "path_end"

def bank_atm100(s):
    lo = int(s // 100 * 100)
    return lo if (s - lo) <= (lo + 100 - s) else lo + 100

def main():
    out = dict(window="2026-11-02..2026-11-12", sysmaps={}, cross_checks={},
               bank={}, nifty={}, errors=[])
    st = {"volrix_last_entry": dict(P.VOLRIX_LAST_ENTRY),
          "v5_days": {"BANKNIFTY": [], "NIFTY": []},
          "scored": {"bank_v22": [], "bank_v21": [], "nifty_decs1": [],
                     "skill_bank": [], "skill_nifty": []}}
    spot_by = {}   # (sym, day) -> {time: open}
    sysmap = defaultdict(dict)  # (sym, day, dir) -> {system: entry_time}
    hard_stop = None
    for day in DAYS:
        for sym in ("BANKNIFTY", "NIFTY"):
            try:
                ctx = NS.day_context(sym, day)
            except urllib.error.HTTPError as e:
                hard_stop = f"HTTP {e.code} in day_context {sym} {day}"
                break
            except Exception as e:
                hard_stop = f"{type(e).__name__} in day_context {sym} {day}: {e}"
                break
            spot_by[(sym, day)] = {b["time"]: b["open"] for b in ctx["own"]}
            legs, _notes = NS.producer_legs(sym, ctx, day, st)
            for l in legs:
                k = (sym, day, l["direction"])
                et = plus5(l["signal_time"])
                if l["system"] not in sysmap[k] or et < sysmap[k][l["system"]]:
                    sysmap[k][l["system"]] = et
            NS.note_state_after(st, sym, day, legs)
        if hard_stop: break
    out["sysmaps"] = {f"{s}|{d}|{dr}": dict(m)
                      for (s, d, dr), m in sorted(sysmap.items())}
    if hard_stop:
        out["hard_stop"] = hard_stop
        out["bank"] = out["nifty"] = "NOT_COMPUTED — " + hard_stop
        (TR / "tuning_daily_baseload_2026-11-12_nov_results.json").write_text(
            json.dumps(out, indent=1, default=str))
        print("HARD STOP:", hard_stop); return 1

    # --- cross-checks -------------------------------------------------
    xc = {}
    for sym, logf in (("BANKNIFTY", "november_shadow_skill_bank_log.csv"),
                      ("NIFTY", "november_shadow_skill_nifty_log.csv")):
        logged = {}
        for r in csv.DictReader(open(TR / logf)):
            if r["date"] in DAYS and r["signal_time"]:  # skip no-trade rows
                logged[r["date"]] = (r["direction"], r["signal_time"])
        mine = {}
        for (s, d, dr), m in sysmap.items():
            if s == sym and "Skill V3" in m:
                # producer entry = plus5(signal); invert for comparison
                et = m["Skill V3"]
                h, mm = int(et[:2]), int(et[3:]) - 5
                mine[d] = (dr, f"{h - (1 if mm < 0 else 0):02d}:{(mm + 60) % 60 if mm < 0 else mm:02d}")
        xc[sym] = dict(logged=logged, reconstructed=mine,
                       match=(logged == mine))
    out["cross_checks"]["skill_legs"] = xc
    decs1_notes_sysmap = {  # recorded in november_shadow_decs1_nifty_log.csv
        "2026-11-04": {}, "2026-11-06": {"CE": ["Skill V3"]},
        "2026-11-09": {"PE": ["Skill V3", "V5 v2"]},
        "2026-11-12": {"CE": ["Skill V3"]}}
    mine_n = {}
    for (s, d, dr), m in sysmap.items():
        if s == "NIFTY" and d in decs1_notes_sysmap:
            mine_n.setdefault(d, {})[dr] = sorted(m)
    out["cross_checks"]["decs1_note_sysmaps"] = dict(
        recorded=decs1_notes_sysmap, reconstructed=mine_n,
        match=all(mine_n.get(d, {}) == v for d, v in decs1_notes_sysmap.items()))

    # --- eligibility + selection --------------------------------------
    stack_days = {"2026-11-04": ["09:55"], "2026-11-09": ["10:45"],
                  "2026-11-12": ["11:30"]}
    v1_days = {"2026-11-03": ["09:50"]}
    def select(sym, inc_days):
        picked, idle_report = [], {}
        for day in DAYS:
            inc = inc_days.get(day, [])
            if inc and min(inc) <= TRIGGER:
                idle_report[day] = "incumbent-leg-by-1330"; continue
            cands = []
            for dr in ("CE", "PE"):
                for sysname, t in sysmap.get((sym, day, dr), {}).items():
                    if TRIGGER <= t <= LAST_ENTRY: cands.append((t, dr, sysname))
            if not cands:
                idle_report[day] = "idle-no-signal-after-1330"; continue
            tstar = min(c[0] for c in cands)
            if len({c[1] for c in cands if c[0] == tstar}) > 1:
                idle_report[day] = f"tie-at-{tstar}"; continue
            dr = next(c[1] for c in cands if c[0] == tstar)
            so = spot_by[(sym, day)].get(tstar)
            if so is None:
                idle_report[day] = "no-spot-bar-at-tstar"; continue
            strike = bank_atm100(so) if sym == "BANKNIFTY" else \
                int(so / 100.0 + 0.5) * 100
            picked.append(dict(date=day, direction=dr, entry_time=tstar,
                               strike=strike,
                               systems=sorted(c[2] for c in cands
                                              if c[0] == tstar and c[1] == dr)))
            idle_report[day] = f"fallback-{dr}-{tstar}"
        return picked, idle_report

    bank_picks, bank_days = select("BANKNIFTY", stack_days)
    nifty_picks, nifty_days = select("NIFTY", v1_days)

    # --- premium + scoring ---------------------------------------------
    from nifty_engine_r5_harness import replay_r5
    import nifty_engine_r7_harness as R7
    def score(sym, picks):
        res, nc = [], []
        stopped = False
        for p in picks:
            if stopped:
                nc.append({**p, "reason": "not-computed-after-429"}); continue
            status, _n = F.fetch_premium(sym, p["strike"], p["direction"],
                                         p["date"], EXP, None)
            if status.startswith("HTTP 429"):
                stopped = True
                nc.append({**p, "reason": "HTTP 429 hard stop"}); continue
            f = TR / "november_shadow_data" / \
                f"candles_{sym}_{p['strike']}{p['direction']}_{p['date']}_{EXP}.json"
            bars = None
            if f.exists():
                data = json.loads(f.read_text()).get("data", {}).get("candles", [])
                rows = [(c[0][11:16], float(c[1]), float(c[2]), float(c[3]),
                         float(c[4])) for c in sorted(data, key=lambda c: c[0])
                        if c[0][:10] == p["date"]]
                if rows: bars = rows
            if not bars:
                nc.append({**p, "reason": f"premium-unavailable ({status})"})
                continue
            if sym == "BANKNIFTY":
                pd = {b[0]: (b[1], b[2], b[3], b[4]) for b in bars}
                if p["entry_time"] not in pd:
                    nc.append({**p, "reason": "no-entry-bar"}); continue
                ep = pd[p["entry_time"]][0]
                xt, xp, reason = sim_g0(pd, p["entry_time"], ep)
                net = round((xp - ep) * 30 - 220.0, 2)
                res.append({**p, "entry": ep, "exit_time": xt, "exit": xp,
                            "exit_reason": reason, "net": net})
            else:
                bl = [[b[0], b[1], b[2], b[3], b[4], 0.0] for b in bars]
                r = replay_r5(bl, p["entry_time"], **dict(R7.STANDING_GEOM))
                if r is None:
                    nc.append({**p, "reason": "replay-none"}); continue
                res.append({**p, "entry": r["entry"], "exit_time": r["exit_time"],
                            "exit": r["exit"], "exit_reason": r["exit_reason"],
                            "net": r["net"]})
        return res, nc

    bank_res, bank_nc = score("BANKNIFTY", bank_picks)
    nifty_res, nifty_nc = score("NIFTY", nifty_picks)
    bfb = round(sum(r["net"] for r in bank_res), 2)
    nfb = round(sum(r["net"] for r in nifty_res), 2)
    out["bank"] = dict(baseline_recorded=-960.0, baseline_live_only=-1720.0,
                       day_status=bank_days, fallback_legs=bank_res,
                       fallback_nc=bank_nc, fallback_net=bfb,
                       counterfactual_recorded=round(-960.0 + bfb, 2),
                       counterfactual_live_framing=round(-1720.0 + round(
                           sum(r["net"] for r in bank_res
                               if r["date"] >= "2026-11-11"), 2), 2))
    out["nifty"] = dict(baseline_v1_forward=3036.50,
                        day_status=nifty_days, fallback_legs=nifty_res,
                        fallback_nc=nifty_nc, fallback_net=nfb,
                        counterfactual_v1=round(3036.50 + nfb, 2))
    with open(TR / "tuning_daily_baseload_2026-11-12_nov_trades.csv", "w",
              newline="") as f:
        w = csv.writer(f)
        w.writerow(["index", "date", "direction", "entry_time", "strike",
                    "expiry", "systems", "entry", "exit", "exit_time",
                    "exit_reason", "net"])
        for sym, rr in (("BANKNIFTY", bank_res), ("NIFTY", nifty_res)):
            for r in rr:
                w.writerow([sym, r["date"], r["direction"], r["entry_time"],
                            r["strike"], EXP, "; ".join(r["systems"]),
                            r["entry"], r["exit"], r["exit_time"],
                            r["exit_reason"], r["net"]])
    (TR / "tuning_daily_baseload_2026-11-12_nov_results.json").write_text(
        json.dumps(out, indent=1, default=str))
    print("cross-checks:", json.dumps(out["cross_checks"], default=str)[:400])
    print(f"[NOV BANK] days: {bank_days}")
    print(f"[NOV BANK] fallback legs {len(bank_res)} net {bfb:+,.2f} NC {len(bank_nc)} "
          f"| CF recorded {-960.0 + bfb:+,.2f} | CF live-framing "
          f"{out['bank']['counterfactual_live_framing']:+,.2f}")
    print(f"[NOV NIFTY] days: {nifty_days}")
    print(f"[NOV NIFTY] fallback legs {len(nifty_res)} net {nfb:+,.2f} NC "
          f"{len(nifty_nc)} | CF v1 {3036.50 + nfb:+,.2f}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
