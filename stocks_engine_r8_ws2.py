#!/usr/bin/env python3
"""ROUND 8 — WS2: INDEX-STATE CONDITIONING (R8-05, R8-06).

R8-05: the certified morning NE-REV population (R7-08 construction,
re-anchored first) admitted only on days where NIFTY's 10:25-bar
close is <= -0.30% vs its prior-day close (state knowable at 10:30;
entries 10:35). Placebos: flipped / one-bar-late rows of the same
build under the same day filter.
R8-06: the banked fade legs (book comps GAP-FADE + GAP-FADE-INC)
restricted to days where NIFTY's 09:15-bar close (completes 09:20)
is below its prior-day close. Precedence asserted per leg in bar
indices (state bar index 0; every fade entry bar index >= 1).
Placebos: mirror restriction (not-down subset) and a chrono
restriction removing the same count of legs earliest-first.
"""
import sys
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r7_builders as B7
import stocks_engine_r8_builders as B8
import stocks_engine_r8_lib as R8

books = R8.load_books()

def renamed(rows, comp):
    return {yr: [dict(t, comp=comp) for t in rows[yr]] for yr in rows}

# ------------------------------------------------------------- R8-05 -
cert_set = B7.certified_exclusions()[0]
real, flipped, late, viol, stats = B7.nerev_gen(
    signal_time="10:25", entry_time="10:35", thr=2.0, excl=cert_set)
assert viol == 0, viol
sa = {yr: round(sum(t["net"] for t in real[yr]), 2) for yr in (2025, 2026)}
assert sa == {2025: 14105.64, 2026: 24112.86}, sa
assert (len(real[2025]), len(real[2026])) == (291, 370)
print("NE-REV certified anchor OK (+14,105.64 / +24,112.86; 291/370)")

def idx_filter(rows):
    kept = {2025: [], 2026: []}
    dropped_state, dropped_unknown = 0, 0
    for yr in (2025, 2026):
        for t in rows[yr]:
            mv = B8.nifty_move(t["date"], "10:25")
            if mv is None:
                dropped_unknown += 1
            elif mv <= -0.30:
                kept[yr].append(t)
            else:
                dropped_state += 1
    return kept, dropped_state, dropped_unknown

real_f, ds, du = idx_filter(real)
flip_f, _, _ = idx_filter(flipped)
late_f, _, _ = idx_filter(late)
sa_f = {yr: round(sum(t["net"] for t in real_f[yr]), 2)
        for yr in (2025, 2026)}
COMP = "NE-REV-IDX"
var = R8.add_comp(books, COMP, renamed(real_f, COMP))
pl = [R8.full_total(R8.add_comp(books, COMP, renamed(flip_f, COMP))),
      R8.full_total(R8.add_comp(books, COMP, renamed(late_f, COMP)))]
out = R8.gate(books, var, pl, timing_violations=viol)
failed = [k for k, v in out["legs"].items()
          if isinstance(v, bool) and not v]
R8.record(
    "R8-05",
    "NE-REV-IDX (certified NE-REV admitted only when NIFTY "
    "10:25-bar close <= -0.30% vs prior close; entry 10:35, "
    "T100/S065)", out,
    note=f"unconditioned certified anchor reproduced first "
         f"(+14,105.64 / +24,112.86; 661 rows). Day filter kept "
         f"{len(real_f[2025])}/{len(real_f[2026])} rows; dropped "
         f"{ds} signal rows on state (NIFTY not down >= 0.30%) "
         f"and {du} on state-unknown (missing NIFTY bar or prior "
         f"close — counted, never guessed). Conditioned "
         f"standalone: {sa_f[2025]} (2025) / {sa_f[2026]} (2026). "
         f"Timing audit: the state bar completes at 10:30 and "
         f"every entry is at 10:35, strictly after both the "
         f"stock's and the index's 10:25 bars; violations counted "
         f"= {viol} (stock construction) and the day filter uses "
         f"only the completed 10:25 index bar. Placebos under the "
         f"same filter: opposite-direction book {pl[0]}; "
         f"one-bar-late book {pl[1]}. Failed legs: {failed}.",
    extra={"standalone": {str(k): v for k, v in sa_f.items()},
           "population_trades": {"2025": len(real_f[2025]),
                                 "2026": len(real_f[2026])},
           "dropped_state": ds, "dropped_unknown": du})

# ------------------------------------------------------------- R8-06 -
FADE_COMPS = {"GAP-FADE", "GAP-FADE-INC"}
GRID0 = 9 * 60 + 15

def bar_index(time_str):
    hh, mm = int(time_str[:2]), int(time_str[3:5])
    return (hh * 60 + mm - GRID0) // 5

legs = []
for yr in (2025, 2026):
    for i, t in enumerate(books[yr]):
        if t["comp"] in FADE_COMPS:
            legs.append((yr, i, t))
viol6 = 0
state = {}
unknown = 0
for yr, i, t in legs:
    if bar_index(t["entry_time"]) <= 0:
        viol6 += 1
    mv = B8.nifty_move(t["date"], "09:15")
    if mv is None:
        unknown += 1
        state[(yr, i)] = False
    else:
        state[(yr, i)] = mv < 0
assert viol6 == 0, viol6
n_down = sum(1 for v in state.values() if v)
n_legs = len(legs)
print(f"fade legs {n_legs}; NIFTY-down days {n_down}; not-down "
      f"{n_legs - n_down}; state-unknown {unknown}; bar-index "
      f"violations {viol6}")

def restrict(keep_down):
    out = {}
    for yr in (2025, 2026):
        out[yr] = [t for i, t in enumerate(books[yr])
                   if t["comp"] not in FADE_COMPS
                   or state[(yr, i)] == keep_down]
    return out

var6 = restrict(True)
removed = n_legs - n_down
mirror6 = restrict(False)

chrono_legs = sorted(legs, key=lambda x: (x[2]["date"],
                                          x[2]["entry_time"],
                                          x[2]["stock"]))
drop_keys = {(yr, i) for yr, i, t in chrono_legs[:removed]}
chrono6 = {yr: [t for i, t in enumerate(books[yr])
                if (yr, i) not in drop_keys] for yr in (2025, 2026)}
pl6 = [R8.full_total(mirror6), R8.full_total(chrono6)]
out6 = R8.gate(books, var6, pl6, timing_violations=viol6)
failed6 = [k for k, v in out6["legs"].items()
           if isinstance(v, bool) and not v]
kept_sa = {}
for yr in (2025, 2026):
    kept_sa[yr] = round(sum(t["net"] for (y, i, t) in legs
                            if y == yr and state[(y, i)]), 2)
R8.record(
    "R8-06",
    "BANKED FADE x NIFTY-DOWN STATE (GAP-FADE + GAP-FADE-INC legs "
    "kept only when NIFTY's 09:15-bar close < prior-day close)", 
    out6,
    note=f"banked fade legs {n_legs} (both comps, both years); "
         f"state down on {n_down}, not-down on {n_legs - n_down} "
         f"(incl. {unknown} state-unknown, counted and treated "
         f"as not-down — never guessed); variant removes the "
         f"{removed} not-down legs. Kept-leg standalone (full "
         f"year): {kept_sa[2025]} (2025) / {kept_sa[2026]} (2026). "
         f"Timing audit: state = close of NIFTY's 09:15 bar "
         f"(bar index 0, completes 09:20); every fade entry is at "
         f"09:20 (index 1) or 09:40 (index 5) — strictly after "
         f"the state bar in the engine's bar-index form; "
         f"violations counted = {viol6}. Placebos: P1 mirror "
         f"restriction (not-down legs kept) book {pl6[0]}; P2 "
         f"chrono restriction (same count removed "
         f"earliest-first) book {pl6[1]}. Failed legs: "
         f"{failed6}.",
    extra={"fade_legs": n_legs, "down_legs": n_down,
           "removed_legs": removed, "unknown_state_legs": unknown,
           "kept_standalone": {str(k): v for k, v in kept_sa.items()}})
print("WS2 done.")
