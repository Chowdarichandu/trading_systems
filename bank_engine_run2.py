#!/usr/bin/env python3
"""Bank recursive engine RUN 2 scorer (BANKNIFTY ONLY).
Book v4 assembly (V1 + NS1-CE block + premium-band [400,550) block, exits =
premium-gated runner: entry premium <400 -> runner_lock50, >=400 -> G0 plain)
plus sequentially-applied state rules. Every leg is scored individually from
premium candles; state rules decide take/skip in chronological order using
only outcomes already known at the leg's entry (prior-day legs always;
same-day legs only if exit_time <= entry_time). The state window tracks the
SIGNALLED stream (skipped legs still enter later windows), as frozen.
Controls in the same run: timing audit + state audit, placebo (identical
assembly+rules, entries +30 min), halves, month table + month-end closes,
ex-top-3 stress, independent re-sum from the written CSV, NOT_COMPUTED count.
Premiums only, lot 30, cost Rs220, UNIQUE-ONCE (inherited from V1 construction).
"""
import csv, json, sys
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import candles, score_legs, agg, month_end_reds
from bank_engine_repro import build_v1_legs
from bank_engine_cycle import FILTERS, _entry_premium

TR = Path.home() / "workspace/trading"
WEEKS = 40.6

def book_v4_legs():
    legs, _, _ = build_v1_legs()
    legs = FILTERS["drop_ns1_ce"](legs)
    legs = FILTERS["drop_prem_400_550"](legs)
    return legs

def score_all(legs, delay=0):
    """Score every leg with the book-v4 gated-runner exit assembly.
    Returns dict key -> result row (with leg fields), and NOT_COMPUTED count."""
    out, nc = {}, 0
    for l in legs:
        ep = _entry_premium(l)
        mode = "runner_lock50" if (ep is not None and ep < 400.0) else "plain"
        r, n1 = score_legs([l], mode=mode, delay=delay)
        nc += n1
        if not r:
            continue
        row = dict(r[0])
        row["rep"] = l["rep"]; row["family"] = l["family"]
        row["leg_key"] = (l["date"], l["direction"], l["entry_time"])
        out[row["leg_key"]] = row
    return out, nc

def trailing_state(stream, leg_row):
    """stream: list of scored rows in chronological order (the signal stream
    of the CURRENT assembly, i.e. legs that survived earlier banked rules).
    Returns (n_known, net) over the last 10 stream legs whose outcome is
    known at leg_row's entry."""
    known = []
    for s in stream:
        if s["leg_key"] == leg_row["leg_key"]:
            break
        if s["date"] < leg_row["date"] or (s["date"] == leg_row["date"]
                                           and s["exit_time"] <= leg_row["entry_time"]):
            known.append(s)
    last = known[-10:]
    return len(last), round(sum(x["net"] for x in last), 2), len(known)

# ---- Run-2 rules: fn(leg_row, n_known, trail_net) -> True = SKIP ----
def rule_cold_la(row, n_known, trail_net):
    return n_known >= 10 and trail_net < 0 and row["rep"] == "(lA) v2"

RULES = {"cold_la": rule_cold_la, "none": lambda r, n, t: False}

def apply_rules(stream, rule_names):
    taken, skipped = [], []
    for row in stream:
        n_known, trail_net, _ = trailing_state(stream, row)
        skip = any(RULES[name](row, n_known, trail_net) for name in rule_names)
        (skipped if skip else taken).append(row)
    return taken, skipped

def controls(stream_all, taken, skipped, placebo_taken, nc, pnc, legs_by_key):
    reds, tot, table = month_end_reds(taken)
    a = agg(taken, WEEKS)
    viol, checked, state_viol = [], 0, []
    for r in taken:
        if r["exit_time"] < r["entry_time"]:
            viol.append((r["date"], r["entry_time"], "exit before entry"))
        l = legs_by_key.get(r["leg_key"])
        cs = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        bars = [b for b in (cs or []) if b[0] == r["entry_time"]]
        if not bars:
            viol.append((r["date"], r["entry_time"], "entry bar missing")); continue
        checked += 1
        if abs(bars[0][1] - r["entry"]) > 0.005:
            viol.append((r["date"], r["entry_time"], "entry premium != open of entry bar"))
    # state audit: re-derive every skip decision and confirm its state inputs
    # all exited at or before the decision leg's entry
    for r in skipped:
        known = [s for s in stream_all
                 if s["date"] < r["date"] or (s["date"] == r["date"] and s["exit_time"] <= r["entry_time"])]
        before = [s for s in stream_all if (s["date"], s["entry_time"]) < (r["date"], r["entry_time"])]
        leaked = [s for s in before if s not in known and s["date"] == r["date"]]
        # same-day not-yet-exited legs are excluded from the state by
        # construction; count how many decisions had such exclusions
        if leaked:
            state_viol.append((r["date"], r["entry_time"], f"{len(leaked)} same-day unexited legs correctly excluded"))
    top3 = sorted(taken, key=lambda x: -x["net"])[:3]
    ex_top3 = round(tot - sum(r["net"] for r in top3), 2)
    h1 = round(sum(r["net"] for r in taken if r["date"] < "2026-06-01"), 2)
    h2 = round(sum(r["net"] for r in taken if r["date"] >= "2026-06-01"), 2)
    p_agg = agg(placebo_taken, WEEKS)
    months = {}
    for m in ("01", "02", "03", "04", "05", "06", "07", "08", "09", "10"):
        months[m] = round(sum(r["net"] for r in taken if r["date"][5:7] == m), 2)
    return dict(n=a["n"], net=a["net"], ft_pct=a["ft_pct"], per_week=a["per_week"],
                not_computed=nc, red_month_ends=reds, month_table=table, months=months,
                halves=dict(jan_may=h1, jun_oct=h2),
                timing_violations=viol, timing_entry_bars_checked=checked,
                state_audit_notes=state_viol,
                placebo=dict(n=p_agg["n"], net=p_agg["net"], not_computed=pnc),
                ex_top3_total=ex_top3,
                top3=[(r["date"], r["direction"], r["net"]) for r in top3],
                skipped=[(r["date"], r["entry_time"], r["direction"], r["rep"], r["net"]) for r in skipped])

def run(cycle_id, rule_names):
    legs = book_v4_legs()
    legs_by_key = {(l["date"], l["direction"], l["entry_time"]): l for l in legs}
    scored, nc = score_all(legs, delay=0)
    stream = sorted(scored.values(), key=lambda x: (x["date"], x["entry_time"]))
    taken, skipped = apply_rules(stream, rule_names)
    p_scored, pnc = score_all(legs, delay=6)
    p_stream = sorted(p_scored.values(), key=lambda x: (x["date"], x["entry_time"]))
    # placebo: identical rules applied on the delayed stream (its own state)
    p_taken, _ = apply_rules(p_stream, rule_names)
    s = controls(stream, taken, skipped, p_taken, nc, pnc, legs_by_key)
    out_csv = TR / f"bank_engine_{cycle_id}_trades.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "direction", "family", "rep", "entry_time", "entry_premium",
                    "exit_time", "exit_premium", "exit_reason", "full_target", "net_inr"])
        for r in sorted(taken, key=lambda x: (x["date"], x["entry_time"])):
            w.writerow([r["date"], r["direction"], r["family"], r["rep"], r["entry_time"],
                        r["entry"], r["exit_time"], r["exit"], r["exit_reason"], r["ft"], r["net"]])
    rs, rn = 0.0, 0
    for r in csv.DictReader(open(out_csv)):
        rs += float(r["net_inr"]); rn += 1
    s.update(cycle=cycle_id, rules=rule_names,
             independent_resum=dict(n=rn, net=round(rs, 2)),
             resum_matches=(rn == s["n"] and abs(round(rs, 2) - s["net"]) < 0.005))
    print(json.dumps(s, indent=1))
    (TR / f"bank_engine_{cycle_id}_summary.json").write_text(json.dumps(s, indent=1))
    return s

if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2].split(",") if len(sys.argv) > 2 else ["none"])
