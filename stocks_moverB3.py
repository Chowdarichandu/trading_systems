#!/usr/bin/env python3
"""MOVER-B3 tuning — families frozen in stocks_moverB3_frozen.md BEFORE
scoring. Equity cash, LONG/SHORT, paper only, real Rs0. Provisional
per 100 shares, net = gross - Rs40/trade. Window Jan-Oct 2026.

Machinery: stocks_moverB2.py build/collect/enrich reused verbatim.
Modes: validate | b31a | b31b | b31c | b32a | b32b | b32c | b33 | b34
"""
import json, os, sys
import importlib.util

BASE = "/home/hatch/workspace/trading"
spec = importlib.util.spec_from_file_location("b2", f"{BASE}/stocks_moverB2.py")
B2 = importlib.util.module_from_spec(spec)
_argv = sys.argv
sys.argv = ["b2"]
spec.loader.exec_module(B2)
sys.argv = _argv

RESULTS_F = f"{BASE}/stocks_moverB3_results.json"
B2_NET = 812204.86

BASE_CFG = {"threshold": 0.01, "window_end": "10:30", "same_dir": False,
            "tp": 1.25, "sp": 0.5, "cap": 2}

CELLS = {
    "B3-1a": {"label": "MEASUREMENT 10:45", "cfg": {**BASE_CFG, "window_end": "10:45"},
              "modifies": "B2 candidate (10:30)", "bar": B2_NET},
    "B3-1b": {"label": "MEASUREMENT 11:00", "cfg": {**BASE_CFG, "window_end": "11:00"},
              "modifies": "B2 candidate (10:30)", "bar": B2_NET},
    "B3-1c": {"label": "MEASUREMENT 11:30", "cfg": {**BASE_CFG, "window_end": "11:30"},
              "modifies": "B2 candidate (10:30)", "bar": B2_NET},
    "B3-2a": {"label": "10:30 + DIRECT-ONLY (cap 1)", "cfg": {**BASE_CFG, "cap": 1},
              "modifies": "B2 candidate (10:30)", "bar": B2_NET},
    "B3-2b": {"label": "10:30 + SAME-DIRECTION", "cfg": {**BASE_CFG, "same_dir": True},
              "modifies": "B2 candidate (10:30)", "bar": B2_NET},
    "B3-2c": {"label": "10:30 + COMBINED (cap 1 + same-direction)",
              "cfg": {**BASE_CFG, "cap": 1, "same_dir": True},
              "modifies": "B2 candidate (10:30)", "bar": B2_NET},
}


def load_results():
    if os.path.exists(RESULTS_F):
        return json.load(open(RESULTS_F))
    return {}


def save_results(r):
    json.dump(r, open(RESULTS_F, "w"), indent=1)


def gate(pooled, bar):
    return {"net_gt_modified": pooled["net"] > bar,
            "both_halves_positive": pooled["jan_may"]["chain_net"] > 0
                                    and pooled["jun_oct"]["chain_net"] > 0,
            "breadth_ge_47": pooled["breadth"] >= 47,
            "max_dd_ok": pooled["max_dd"] >= -25000.0,
            "no_losing_month": not pooled["losing_months"]}


def gate_pass(g):
    return all(g.values())


def fmt(tag, s):
    p = s["pooled"]
    print(f"{tag}: pooled chains={p['chains']} trades={p['trades']} net={p['net']} "
          f"exp/ch={p['exp_per_chain']} JM={p['jan_may']['chain_net']} "
          f"JO={p['jun_oct']['chain_net']} Oct={p['october']['chain_net']} "
          f"breadth={p['breadth']}/50 top3={p['top3_share_pct']}% "
          f"losing={p['losing_months']} maxDD={p['max_dd']} | "
          f"home net={s['home']['net']} br={s['home']['breadth']}/25 | "
          f"ext net={s['ext']['net']} br={s['ext']['breadth']}/25", flush=True)


def score(r, key, cell):
    home, ext, s = B2.run_config(cell["cfg"])
    s["config"] = cell["cfg"]
    s["label"] = cell["label"]
    s["modifies"] = cell["modifies"]
    s["bar"] = cell["bar"]
    s["gate"] = gate(s["pooled"], cell["bar"])
    s["gate_pass"] = gate_pass(s["gate"])
    r[key] = s
    save_results(r)
    B2.dump("B3_" + key, home + ext)
    fmt(key + " " + cell["label"], s)
    print(f"{key} GATE (bar {cell['bar']}): {s['gate']} -> "
          f"{'PASS' if s['gate_pass'] else 'FAIL'}", flush=True)
    return s


def mode_validate():
    r = load_results()
    home, ext, s = B2.run_config(BASE_CFG)
    p = s["pooled"]
    exp = {"chains": 1212, "trades": 1835, "net": 812204.86,
           "jm": 448461.50, "jo": 363743.36, "oct": 144167.85,
           "breadth": 48, "exp": 670.14, "dd": -18493.11}
    got = {"chains": p["chains"], "trades": p["trades"], "net": p["net"],
           "jm": p["jan_may"]["chain_net"], "jo": p["jun_oct"]["chain_net"],
           "oct": p["october"]["chain_net"], "breadth": p["breadth"],
           "exp": p["exp_per_chain"], "dd": p["max_dd"]}
    ok = all(abs(got[k] - v) < 0.01 for k, v in exp.items()) \
        and not p["losing_months"] \
        and abs(s["home"]["net"] - 270069.11) < 0.01 \
        and abs(s["ext"]["net"] - 542135.75) < 0.01
    print(f"ANCHOR B2 candidate: {got} losing={p['losing_months']} "
          f"home={s['home']['net']} ext={s['ext']['net']} -> "
          f"{'PASS' if ok else 'FAIL'}", flush=True)
    r["BASE"] = {**s, "config": BASE_CFG, "anchor_pass": bool(ok)}
    save_results(r)
    B2.dump("B3_BASE", home + ext)
    fmt("BASE B2 candidate (10:30)", s)
    print("VALIDATION:", bool(ok), flush=True)
    return bool(ok)


def require_base(r):
    if not r.get("BASE", {}).get("anchor_pass"):
        print("Base anchor not validated — run validate first.", flush=True)
        sys.exit(1)


def best_config(r):
    """Best configuration overall by pooled net among BASE + scored cells."""
    cands = [("BASE (B2 candidate)", r["BASE"]["config"], r["BASE"]["pooled"]["net"])]
    for k, v in r.items():
        if k.startswith("B3-") and isinstance(v, dict) and "pooled" in v:
            cands.append((k, v["config"], v["pooled"]["net"]))
    cands.sort(key=lambda x: -x[2])
    return cands[0]


def mode_b33():
    r = load_results()
    require_base(r)
    plain = {k: r[k] for k in ("B3-1a", "B3-1b", "B3-1c") if k in r}
    if len(plain) < 3:
        print("B3-3 requires all B3-1 cells first.", flush=True)
        sys.exit(1)
    best_key = max(plain, key=lambda k: plain[k]["pooled"]["net"])
    best = plain[best_key]
    if best["pooled"]["net"] <= B2_NET:
        print(f"B3-3 NOT RUN: best B3-1 cell {best_key} net "
              f"{best['pooled']['net']} does not beat 10:30 base {B2_NET}.",
              flush=True)
        r["B3-3"] = {"run": False,
                     "reason": f"best B3-1 cell {best_key} net "
                               f"{best['pooled']['net']} <= B2 candidate {B2_NET}"}
        save_results(r)
        return
    peak_cfg = dict(best["config"])
    cfg = {**peak_cfg, "cap": 1, "same_dir": True}
    cell = {"label": f"PEAK {peak_cfg['window_end']} + COMBINED (cap 1 + same-direction)",
            "cfg": cfg, "modifies": f"{best_key} plain ({peak_cfg['window_end']})",
            "bar": max(best["pooled"]["net"], B2_NET)}
    print(f"B3-3 peak = {best_key} at {peak_cfg['window_end']} "
          f"(net {best['pooled']['net']})", flush=True)
    score(r, "B3-3", cell)


def mode_b34():
    r = load_results()
    require_base(r)
    name, cfg, net = best_config(r)
    print(f"B3-4 base = {name} (pooled net {net}) cfg={cfg}", flush=True)
    r["B3-4_BASE"] = {"source": name, "source_net": net, "source_config": cfg}
    save_results(r)
    for key, tp, sp in (("B3-4a", 1.5, 0.5), ("B3-4b", 1.25, 0.65)):
        c = {**cfg, "tp": tp, "sp": sp}
        cell = {"label": f"EXIT T{int(tp*100)}/S{int(sp*100)} on {name}",
                "cfg": c, "modifies": name, "bar": net}
        score(r, key, cell)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "validate"
    r = load_results()
    if mode == "validate":
        if not mode_validate():
            print("VALIDATION FAILED — aborting.", flush=True)
            sys.exit(1)
    elif mode in ("b31a", "b31b", "b31c", "b32a", "b32b", "b32c"):
        require_base(r)
        key = {"b31a": "B3-1a", "b31b": "B3-1b", "b31c": "B3-1c",
               "b32a": "B3-2a", "b32b": "B3-2b", "b32c": "B3-2c"}[mode]
        score(r, key, CELLS[key])
    elif mode == "b33":
        mode_b33()
    elif mode == "b34":
        mode_b34()
    else:
        print("unknown mode", mode)
        sys.exit(1)
    print("DONE", mode, flush=True)
