#!/usr/bin/env python3
"""ROUND 7 WS3 — SKILL OR-WINDOW VARIANT (Cycles 156-157).

Frozen Skill V3 (skill_v3_jansep.py): OR = bars with time < 09:30;
signal = first close beyond OR in 09:30-11:30; CE bearish block removed;
09:30-PE rule (a PE on the 09:30 bar is taken only if its close < PDL,
else the day ends). ONE variant, per the brief: OR window 09:15-09:45 —
OR = bars with time < 09:45, signal = first close beyond that OR in
09:45-11:30, and the first-bar PE rule applied at the first signal bar
(09:45): a 09:45 PE is taken only if its close < PDL. Everything else —
entry at the next bar's open, the member's role in pooling, the causal
solo rule — is the frozen construction. Only the Bank Skill legs are
replaced; the whole book is re-gated vs v21.

Regenerated legs use the book's own conventions: strike = ATM of the
entry bar's spot open (progressive-cache entry_spot, exactly as
component_legs builds the frozen Jan-Sep Skill legs), expiry in force.
Cycle 156 validation: the same generator at the frozen window (< 09:30)
must reproduce the frozen Jan-Sep Bank Skill leg set exactly, and its
October output must match the frozen October file's Bank V3 legs on
(date, direction, entry_time, strike, expiry), before the variant is
trusted.
CAUSALITY CERTIFICATE: the 09:45 OR is complete at 09:45; every signal
bar is >= 09:45 and the entry is the next bar's open — every input is
printed at or before the signal bar, entry strictly after it."""
import sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import bank_r5_core as c5
import bank_r7_core as c7
from bank_r7_core import judge7, v21_ref
from bank_r6_core import v20_inputs
from skill_v3_jansep import load_index

def run_index_or(idx, start, end, or_end):
    """skill_v3_jansep.run_index with the OR window end parameterised.
    or_end='09:30' is the frozen construction verbatim (first signal bar
    09:30, first-bar PE rule at 09:30)."""
    bars_by_date, prev = load_index(idx)
    trades = []
    for date in sorted(bars_by_date):
        if not (start <= date <= end):
            continue
        day = bars_by_date[date]
        or_bars = [b for b in day if b["time"] < or_end]
        if not or_bars:
            continue
        orh = max(b["high"] for b in or_bars)
        orl = min(b["low"] for b in or_bars)
        if date not in prev:
            continue
        _pdate, _ph, pdl, _pc = prev[date]
        sig = sig_dir = None
        for b in day:
            if or_end <= b["time"] <= "11:30":
                if b["close"] > orh:
                    sig, sig_dir = b, "CE"
                    break
                if b["close"] < orl:
                    sig, sig_dir = b, "PE"
                    break
        if sig is None:
            continue
        if sig_dir == "PE" and sig["time"] == or_end and not (sig["close"] < pdl):
            continue
        idx_pos = next(i for i, b in enumerate(day) if b["time"] == sig["time"])
        if idx_pos + 1 >= len(day):
            continue
        entry_bar = day[idx_pos + 1]
        entry = entry_bar["open"]
        stop = sig["low"] if sig_dir == "CE" else sig["high"]
        risk = abs(entry - stop)
        if risk == 0:
            continue
        trades.append({"index": idx, "date": date, "direction": sig_dir,
                       "signal_time": sig["time"],
                       "entry_time": entry_bar["time"],
                       "entry_spot": entry})
    return trades

def _expiry(date):
    from aggressive_score import EXPIRIES
    for e in EXPIRIES:
        if e >= date:
            return e
    return "2026-11-03"  # the frozen October file's own assignment for
    # 2026-10-28 legs (the Bank Nov-03 chain gap; see below)

def skill_legs(or_end, jansep_end, oct_end):
    out = []
    for start, end in (("2026-01-01", jansep_end), ("2026-10-01", oct_end)):
        for t in run_index_or("BANKNIFTY", start, end, or_end):
            out.append(c5.mkleg(t["date"], t["direction"], t["entry_time"],
                                c5.atm(t["entry_spot"]),
                                _expiry(t["date"]), "Skill V3",
                                _signal=t["signal_time"]))
    # Frozen-construction symmetry: the frozen October file EXCLUDES its
    # own unscoreable legs at source (premium_status NOT_COMPUTED — the
    # Bank 2026-11-03 chain gap) instead of carrying them as NC. Apply
    # the same rule here: attempt the standard fetch, then exclude legs
    # whose candles still do not exist, named in the output.
    still = c5.fetch_missing(out)
    if still:
        print(f"  skill_legs({or_end}): excluding unscoreable legs "
              f"(Nov-03 chain gap class): {still}")
        bad = set(still)
        out = [l for l in out
               if (l["date"], l["direction"], int(l["strike"]), l["expiry"]) not in bad]
    return out

def partition(comps):
    """Split the frozen component list into its append-order blocks."""
    blocks = defaultdict(list)
    for l in comps:
        oct_ = l["date"] >= "2026-10-01"
        blocks[(l["rep"], oct_)].append(l)
    return blocks

def components_with_skill(new_skill):
    frozen = c5.component_legs(volrix=c5.volrix_gen_legs(-0.01, 15))
    b = partition(frozen)
    js = [l for l in new_skill if l["date"] < "2026-10-01"]
    oc = [l for l in new_skill if l["date"] >= "2026-10-01"]
    return (b[("(lA) v2", False)] + b[("V5 v2", False)] + js
            + [l for l in frozen if l["rep"] == "Volrix (b)"]
            + b[("(lA) v2", True)] + b[("V5 v2", True)] + oc)

def keyset(legs, with_expiry=False):
    if with_expiry:
        return sorted((l["date"], l["direction"], l["entry_time"],
                       l["strike"], l["expiry"]) for l in legs)
    return sorted((l["date"], l["direction"], l["entry_time"], l["strike"])
                  for l in legs)

ref = v21_ref()
pooled21, ns1 = v20_inputs()

# ---------- Cycle 156: frozen-window regeneration validation ----------
frozen = c5.component_legs(volrix=c5.volrix_gen_legs(-0.01, 15))
frozen_skill_js = [l for l in frozen if l["rep"] == "Skill V3"
                   and l["date"] < "2026-10-01"]
frozen_skill_oct = [l for l in frozen if l["rep"] == "Skill V3"
                    and l["date"] >= "2026-10-01"]
regen30 = skill_legs("09:30", "2026-09-30", "2026-10-28")
regen_js = [l for l in regen30 if l["date"] < "2026-10-01"]
regen_oct = [l for l in regen30 if l["date"] >= "2026-10-01"]
a, b_ = keyset(frozen_skill_js), keyset(regen_js)
print(f"C156 validation Jan-Sep: frozen {len(a)} vs regen {len(b_)}; "
      f"only-frozen {[x for x in a if x not in b_]}; "
      f"only-regen {[x for x in b_ if x not in a]}")
ao, bo = keyset(frozen_skill_oct, True), keyset(regen_oct, True)
print(f"C156 validation Oct: frozen {len(ao)} vs regen {len(bo)}; "
      f"only-frozen {[x for x in ao if x not in bo]}; "
      f"only-regen {[x for x in bo if x not in ao]}")
assert a == b_ and ao == bo, "Skill regeneration mismatch — variant not trusted"
print("C156 PASS: frozen-window regeneration reproduces the frozen Skill sets.")

# ---------- Cycle 157: OR 09:15-09:45 variant ----------
legs45 = skill_legs("09:45", "2026-09-30", "2026-10-28")
print(f"C157 population: {len(legs45)} OR45 Skill legs "
      f"(frozen window set: {len(regen30)})")
comps = components_with_skill(legs45)
pooled = c5.pool_b2(comps, solo_rule="causal")
r = judge7("C157 SKILL OR 09:15-09:45", ref, pooled, ns1)
print("   detail:", r["detail"])
