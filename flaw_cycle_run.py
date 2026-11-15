#!/usr/bin/env python3
"""FLAW-CYCLE 2026-11-03 — Bank v21 incumbent + FC-1/FC-2/FC-3 exit overlays.
Candidates pre-registered in flaw_cycle_candidates_2026-11-03.md BEFORE this
run. Incumbent legs/params reproduced through the audited pipeline
(assemble6 with Round-8 P21) and verified leg-for-leg vs the frozen regen
CSV before any variant is scored. Paper only.
"""
import csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import candles
import bank_r6_core
from bank_r6_core import assemble6
from bank_r7_core import P21, GDGU
from bank_r2_core import LOT, COST, WEEKS, month_end_reds

TR = Path.home() / "workspace/trading"
SQ = "15:20"

# ---------- reproduce incumbent v21 ----------
pooled, ns1 = bank_r6_core.v20_inputs()
rows21, nc21, lbk, detail, plan = assemble6(
    pooled, ns1, delay=0, ns3_causal_form=True, ns3_filter=GDGU, ns3_params=P21)
assert nc21 == 0, nc21

# verify leg-for-leg vs frozen regen CSV
ref = list(csv.DictReader(open(TR / "bank_engine_r8_v21_regen_trades.csv")))
mine = sorted(rows21, key=lambda r: (r["date"], r["entry_time"], r["leg_key"]))
ref = sorted(ref, key=lambda r: (r["date"], r["entry_time"]))
mism = 0
assert len(mine) == len(ref) == 99
for a, b in zip(mine, ref):
    for k1, k2 in [("date", "date"), ("direction", "direction"), ("family", "family"),
                   ("entry_time", "entry_time"), ("exit_time", "exit_time"),
                   ("exit_reason", "exit_reason")]:
        if str(a[k1]) != str(b[k2]): mism += 1
    if abs(a["entry"] - float(b["entry_premium"])) > 0.005: mism += 1
    if abs(a["exit"] - float(b["exit_premium"])) > 0.005: mism += 1
    if abs(a["net"] - float(b["net_inr"])) > 0.005: mism += 1
inc_net = round(sum(r["net"] for r in rows21), 2)
print(f"INCUMBENT REPRODUCED: n={len(rows21)} net={inc_net} field-mismatches={mism}")
assert mism == 0 and inc_net == 83650.50

# ---------- overlay replay (mirrors bank_r3_ws3.replay_x, mode='open') ----------
def replay_overlay(cs, entry_time, p, overlay=None, delay=0, sq=SQ):
    if not cs: return None
    idxs = [i for i, b in enumerate(cs) if b[0] >= entry_time]
    if not idxs: return None
    i0 = idxs[0] + delay
    if i0 >= len(cs): return None
    entry = cs[i0][1]; start = i0
    if start >= len(cs) or cs[start][0] > sq: return None
    stop0, trig = entry - p["stop"], entry + p["trig"]
    st = {"ft90": 0}
    def mk(px, reason, t, ft):
        return dict(net=round((px - entry) * LOT - COST, 2), exit_reason=reason,
                    exit_time=t, ft=ft, ft90=st["ft90"], entry=entry, exit=px)
    bars = cs[start:]
    if not bars: return mk(entry, "square_off", cs[i0][0], 0)
    runmax = None; lock_armed = False
    for j, b in enumerate(bars):
        t, o, h, l, cl, v = b
        if t > sq: break
        runmax = h if runmax is None else max(runmax, h)
        eff_stop = entry + 0.0 if lock_armed else stop0
        if l <= eff_stop:
            return mk(eff_stop, "lock_stop" if lock_armed else "stop", t, 0)
        if h >= entry + 90.0: st["ft90"] = 1
        if h >= trig:
            if p["lock"] is None and p["tgt2"] is None:
                return mk(trig, "target", t, 1)
            stop2 = entry + p["lock"] if p["lock"] is not None else stop0
            tgt2 = entry + p["tgt2"] if p["tgt2"] is not None else None
            rest = None
            for b2 in bars[j + 1:]:
                t2, o2, h2, l2, cl2, v2 = b2
                if t2 > sq: break
                if l2 <= stop2: rest = (stop2, "runner_stop", t2); break
                if h2 >= entry + 90.0: st["ft90"] = 1
                if tgt2 is not None and h2 >= tgt2: rest = (tgt2, "runner_target", t2); break
                if t2 == sq: rest = (cl2, "runner_square_off", t2); break
            if rest is None:
                lb = bars[-1]; rest = (lb[4], "runner_square_off", lb[0])
            return mk(rest[0], rest[1], rest[2], 1)
        # overlays act only after this bar's frozen stop/trig checks
        if overlay in ("fc2", "fc3") and h >= entry + 30.0:
            lock_armed = True
        if overlay in ("fc1", "fc3") and j == 2 and t < sq and runmax < entry + 15.0:
            return mk(cl, "nodev_cut", t, 0)
        if t == sq:
            return mk(cl, "square_off", t, 0)
    lb = bars[-1]
    return mk(lb[4], "square_off", lb[0], 0)

def score(overlay, delay=0):
    out, nc = [], 0
    for r in rows21:
        leg = lbk[r["leg_key"]]
        cs = candles(leg["index"], leg["strike"], leg["direction"], leg["date"], leg["expiry"])
        res = replay_overlay(cs, leg["entry_time"], r["_params"], overlay=overlay, delay=delay)
        if res is None: nc += 1; continue
        out.append(dict(date=r["date"], direction=r["direction"], family=r["family"],
                        rep=r["rep"], leg_key=r["leg_key"], segment=r.get("segment"),
                        entry_time=leg["entry_time"], **res))
    return out, nc

def controls(rows, nc, placebo_net):
    reds, tot, table = month_end_reds(rows)
    months = {m: round(sum(r["net"] for r in rows if r["date"][5:7] == m), 2)
              for m in ("01","02","03","04","05","06","07","08","09","10")}
    top3 = sorted(rows, key=lambda x: -x["net"])[:3]
    viol = [r["leg_key"] for r in rows if r["exit_time"] < r["entry_time"]]
    return dict(n=len(rows), net=round(sum(r["net"] for r in rows), 2),
                ft90_pct=round(100.0 * sum(r.get("ft90", 0) for r in rows) / len(rows), 1),
                per_week=round(len(rows) / WEEKS, 2),
                not_computed=nc, red_month_ends=reds, month_end_table=table, months=months,
                halves=dict(jan_may=round(sum(r["net"] for r in rows if r["date"] < "2026-06-01"), 2),
                            jun_oct=round(sum(r["net"] for r in rows if r["date"] >= "2026-06-01"), 2)),
                placebo_net=placebo_net, timing_violations=viol,
                ex_top3=round(sum(r["net"] for r in rows) - sum(r["net"] for r in top3), 2),
                top3=[(r["date"], r["net"]) for r in top3])

def write_trades(rows, fname):
    p = TR / fname
    with open(p, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date","direction","family","rep","leg_key","segment","entry_time",
                    "entry_premium","exit_time","exit_premium","exit_reason","net_inr"])
        for r in sorted(rows, key=lambda x: (x["date"], x["entry_time"])):
            w.writerow([r["date"], r["direction"], r["family"], r["rep"], r["leg_key"],
                        r.get("segment"), r["entry_time"], r["entry"], r["exit_time"],
                        r["exit"], r["exit_reason"], r["net"]])
    rs, rn = 0.0, 0
    for r in csv.DictReader(open(p)):
        rs += float(r["net_inr"]); rn += 1
    return dict(n=rn, net=round(rs, 2))

# incumbent self-check through the overlay scorer (overlay=None must equal v21)
inc_rows, inc_nc = score(None)
inc_resum = write_trades(inc_rows, "flaw_cycle_incumbent_trades.csv")
same = all(abs(a["net"] - b["net"]) < 0.005 and a["exit_time"] == b["exit_time"]
           and a["exit_reason"] == b["exit_reason"]
           for a, b in zip(sorted(inc_rows, key=lambda r: r["leg_key"]),
                           sorted(rows21, key=lambda r: r["leg_key"])))
print(f"OVERLAY SCORER INCUMBENT CHECK: identical={same} resum={inc_resum} nc={inc_nc}")
assert same and inc_nc == 0

results = {}
inc_pl, _ = score(None, delay=6)
inc_pl_net = round(sum(r["net"] for r in inc_pl), 2)
inc_c = controls(inc_rows, inc_nc, inc_pl_net)
inc_c["independent_resum"] = inc_resum
results["incumbent"] = inc_c
print("INCUMBENT controls:", json.dumps(inc_c))

for name, ov in [("FC-1_nodev_cut", "fc1"), ("FC-2_giveback_lock", "fc2"), ("FC-3_combined", "fc3")]:
    vrows, vnc = score(ov)
    pl, _ = score(ov, delay=6)
    pl_net = round(sum(r["net"] for r in pl), 2)
    c = controls(vrows, vnc, pl_net)
    resum = write_trades(vrows, f"flaw_cycle_{ov}_trades.csv")
    c["independent_resum"] = resum
    c["resum_matches"] = (resum["n"] == c["n"] and abs(resum["net"] - c["net"]) < 0.005)
    # banking gate vs incumbent + ex-top-3 leg
    failed = []
    if not c["net"] > inc_c["net"]: failed.append(f"net {c['net']} !> incumbent {inc_c['net']}")
    if c["red_month_ends"]: failed.append(f"red month-ends {c['red_month_ends']}")
    for m, v in inc_c["months"].items():
        if v > 0 and c["months"].get(m, 0.0) < 0:
            failed.append(f"month {m} flips green->red ({v} -> {c['months'].get(m)})")
    if c["ft90_pct"] < inc_c["ft90_pct"]: failed.append(f"FT90 {c['ft90_pct']} < {inc_c['ft90_pct']}")
    if c["per_week"] < 2.0: failed.append(f"frequency {c['per_week']}/wk < 2.0")
    if c["halves"]["jan_may"] < 0 or c["halves"]["jun_oct"] < 0: failed.append(f"negative half {c['halves']}")
    if not c["net"] > pl_net: failed.append(f"own placebo not beaten ({pl_net})")
    if not c["net"] > inc_pl_net: failed.append(f"incumbent placebo not beaten ({inc_pl_net})")
    if c["timing_violations"]: failed.append(f"timing violations {len(c['timing_violations'])}")
    if c["not_computed"]: failed.append(f"NOT_COMPUTED {c['not_computed']}")
    if not c["resum_matches"]: failed.append("re-sum mismatch")
    if c["ex_top3"] < 0: failed.append(f"ex-top-3 {c['ex_top3']} < 0")
    c["gate_pass"] = len(failed) == 0
    c["gate_failed_legs"] = failed
    # effect detail
    diffs = {}
    base = {r["leg_key"]: r for r in inc_rows}
    changed = [(r["leg_key"], r["date"], r["family"], base[r["leg_key"]]["exit_reason"],
                r["exit_reason"], round(r["net"] - base[r["leg_key"]]["net"], 2))
               for r in vrows if abs(r["net"] - base[r["leg_key"]]["net"]) > 0.005]
    c["legs_changed"] = len(changed)
    c["delta_vs_incumbent"] = round(c["net"] - inc_c["net"], 2)
    c["changed_legs"] = changed
    results[name] = c
    print(f"{name}: net={c['net']} delta={c['delta_vs_incumbent']} changed={len(changed)} "
          f"PASS={c['gate_pass']} failed={failed}")

# ---------- flaw quantification on the incumbent ----------
def mins(t): return int(t[:2]) * 60 + int(t[3:5])
flaw = {"full_stops": 0, "full_stop_drag": 0.0, "never_dev": 0, "never_dev_drag": 0.0,
        "dev_then_stop": 0, "dev_then_stop_drag": 0.0, "quick_stop_10": 0, "quick_stop_15": 0,
        "by_scope": {}, "entry_buckets_never_dev": {}, "entry_buckets_full_stop": {},
        "never_dev_legs": [], "dev_stop_legs": []}
scopes = {"ALL": lambda f: True, "OR_family_BASE+NS1": lambda f: f in ("BASE", "NS1_second"),
          "addon_NS3+S3": lambda f: f not in ("BASE", "NS1_second")}
for sn, fn in scopes.items():
    flaw["by_scope"][sn] = {"legs": 0, "full_stops": 0, "drag": 0.0, "never_dev": 0,
                            "never_dev_drag": 0.0, "dev_stop": 0, "dev_stop_drag": 0.0}
for r in rows21:
    leg = lbk[r["leg_key"]]
    cs = candles(leg["index"], leg["strike"], leg["direction"], leg["date"], leg["expiry"])
    bars = [b for b in cs if r["entry_time"] <= b[0] <= r["exit_time"]]
    mfe = round(max(b[2] for b in bars) - r["entry"], 2)
    full = r["exit_reason"] == "stop"
    dur = mins(r["exit_time"]) - mins(r["entry_time"])
    bucket = ("<10:00" if r["entry_time"] < "10:00" else "10:00-10:59" if r["entry_time"] < "11:00"
              else "11:00-11:59" if r["entry_time"] < "12:00" else ">=12:00")
    for sn, fn in scopes.items():
        if not fn(r["family"]): continue
        s = flaw["by_scope"][sn]; s["legs"] += 1
        if full:
            s["full_stops"] += 1; s["drag"] = round(s["drag"] + r["net"], 2)
            if mfe < 30: s["never_dev"] += 1; s["never_dev_drag"] = round(s["never_dev_drag"] + r["net"], 2)
            else: s["dev_stop"] += 1; s["dev_stop_drag"] = round(s["dev_stop_drag"] + r["net"], 2)
    if full:
        flaw["full_stops"] += 1; flaw["full_stop_drag"] = round(flaw["full_stop_drag"] + r["net"], 2)
        flaw["entry_buckets_full_stop"][bucket] = flaw["entry_buckets_full_stop"].get(bucket, 0) + 1
        if dur <= 10: flaw["quick_stop_10"] += 1
        if dur <= 15: flaw["quick_stop_15"] += 1
        if mfe < 30:
            flaw["never_dev"] += 1; flaw["never_dev_drag"] = round(flaw["never_dev_drag"] + r["net"], 2)
            flaw["entry_buckets_never_dev"][bucket] = flaw["entry_buckets_never_dev"].get(bucket, 0) + 1
            flaw["never_dev_legs"].append([r["date"], r["family"], r["direction"], r["entry_time"], mfe, r["net"]])
        else:
            flaw["dev_then_stop"] += 1; flaw["dev_then_stop_drag"] = round(flaw["dev_then_stop_drag"] + r["net"], 2)
            flaw["dev_stop_legs"].append([r["date"], r["family"], r["direction"], r["entry_time"], mfe, r["net"]])
results["flaw_quantification"] = flaw
print("FLAW:", json.dumps(flaw["by_scope"]))
print("never_dev:", flaw["never_dev"], flaw["never_dev_drag"], "| dev_stop:", flaw["dev_then_stop"], flaw["dev_then_stop_drag"])
print("entry buckets never-dev:", flaw["entry_buckets_never_dev"], "| full-stop:", flaw["entry_buckets_full_stop"])

(TR / "flaw_cycle_results_2026-11-03.json").write_text(json.dumps(results, indent=1))
print("WROTE flaw_cycle_results_2026-11-03.json")
