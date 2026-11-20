#!/usr/bin/env python3
"""WIDE-DAILY PART 2 driver — parent decision 2026-11-17: proceed with the
wide run on the OFFICIAL-CLOSE (parquet) basis, research only.

The control for this part is the parquet-fed frozen-25 run from Part 1
(2025: 79 trades +Rs63,621.50 - 2026: 102 trades +Rs1,50,777.40), labelled
OFFICIAL-CLOSE control everywhere. The published store-basis numbers stay
the live book's basis; nothing running is re-baselined or touched.

Machinery is imported verbatim from wide_daily_build.py (which implements
wide_daily_SPEC.md). Stages, each checkpointed to disk:
  control   - re-run the frozen 25 from parquet; PASS = full stats-dict
              equality with the Part 1 official-close anchors.
  chunk K   - score symbols [K*441, (K+1)*441) of the sorted parquet list:
              raw sim2c, liquidity-gated sim, placebo pools, meta.
  finalize  - merge chunks, compute stats / November slices / placebo /
              verdict (spec s.4), merge into wide_daily_results.json
              (Part 1 blocks preserved), rebuild wide_daily_trades.csv as
              CONTROL25_PARQUET + RAW + SCREENED.
"""
import csv, json, os, sys
import numpy as np

WS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WS)
import indicator_parameter_tuning_stocks_build as ATLAS
import ekam_build as EKAM
import ekam2c_build as EKAM2C
import wide_daily_build as W

CHUNK = 441
CKPT = os.path.join(WS, "wide_daily_part2_checkpoint.json")
RES = os.path.join(WS, "wide_daily_results.json")
TRADES_CSV = os.path.join(WS, "wide_daily_trades.csv")


def jclean(x):
    return json.loads(json.dumps(x))


def chunk_path(k):
    return os.path.join(WS, f"wide_daily_chunk_{k}.json")


def stage_control():
    prior = json.load(open(RES))
    anchors = {yr: prior["control"]["detail"][str(yr)]["got"]
               for yr in (2025, 2026)}
    data25 = {}
    for sym in ATLAS.NAMES:
        data25[sym] = W.prep_parquet(sym)
    tr25 = []
    for sym in ATLAS.NAMES:
        tr25.extend(EKAM2C.sim2c(data25[sym]))
    detail = {}
    ok = True
    for yr in (2025, 2026):
        got = EKAM2C.norm_stats(EKAM.stats(tr25, yr))
        same = (got == anchors[yr])
        ok = ok and same
        detail[str(yr)] = dict(match=same, got=got)
        print(f"official-close control {yr}: {got['trades']}t "
              f"{got['total']} vs anchor {anchors[yr]['trades']}t "
              f"{anchors[yr]['total']} -> {same}", flush=True)
    # stats_wide cross-check on the fresh control trades (as in Part 1)
    xchk = {}
    for yr in (2025, 2026):
        w = W.stats_wide(tr25, yr)
        s = EKAM.stats(tr25, yr)
        shared = ("trades", "total", "wr", "avg_hold", "worst", "ex_top3",
                  "max_dd", "forced")
        xchk[str(yr)] = all(w[f] == s[f] for f in shared)
    print("stats_wide cross-check:", xchk, flush=True)
    ck = dict(stage="control", official_close_control=dict(
        passed=ok, detail=detail,
        headline={str(yr): [detail[str(yr)]["got"]["trades"],
                             detail[str(yr)]["got"]["total"]]
                  for yr in (2025, 2026)}),
        stats_wide_crosscheck=xchk,
        control_trades=len(tr25))
    with open(CKPT, "w") as f:
        json.dump(ck, f, indent=1)
    print("CONTROL", "PASSED" if ok else "FAILED", "- checkpoint written",
          flush=True)
    if not ok:
        sys.exit(2)


def stage_chunk(k):
    files = sorted(fn[:-8] for fn in os.listdir(W.UNI_DIR)
                   if fn.endswith(".parquet"))
    syms = files[k * CHUNK:(k + 1) * CHUNK]
    raw_tr, scr_tr = [], []
    excluded_ohlc, no_volume = [], []
    last_dates = {}
    pools = {2025: {}, 2026: {}}
    scored = 0
    for sym in syms:
        try:
            d = W.prep_parquet(sym)
        except Exception as e:
            excluded_ohlc.append(dict(sym=sym, reason=str(e)[:120]))
            continue
        if d["n"] < 2 or not np.isfinite(d["c"]).any():
            excluded_ohlc.append(dict(sym=sym, reason="no usable OHLC rows"))
            continue
        last_dates[sym] = d["dates"][-1]
        raw_tr.extend(EKAM2C.sim2c(d))
        liq = W.liquid_mask(d)
        if d.get("vol") is None:
            no_volume.append(sym)
        scr_tr.extend(W.sim2c_gated(d, liq))
        for yr in (2025, 2026):
            idx = [i for i, dt in enumerate(d["dates"])
                   if dt[:4] == str(yr) and 1 <= int(dt[5:7]) <= 10
                   and liq[i] and i + 1 < d["n"]]
            if idx:
                nets = [EKAM.placebo_exit_net(d, i + 1, None) for i in idx]
                pools[yr][sym] = (idx, nets)
        scored += 1
    out = dict(chunk=k, symbols_considered=len(syms), scored=scored,
               excluded_ohlc=excluded_ohlc, no_volume=no_volume,
               last_dates=last_dates,
               raw_trades=jclean(raw_tr), scr_trades=jclean(scr_tr),
               pools={str(yr): {s: [v[0], v[1]]
                                 for s, v in pools[yr].items()}
                      for yr in (2025, 2026)})
    with open(chunk_path(k), "w") as f:
        json.dump(out, f)
    print(f"chunk {k}: considered {len(syms)}, scored {scored}, "
          f"excluded {len(excluded_ohlc)}, no-volume {len(no_volume)}, "
          f"raw trades {len(raw_tr)}, screened trades {len(scr_tr)}",
          flush=True)


def stage_finalize():
    ck = json.load(open(CKPT))
    assert ck["official_close_control"]["passed"], "control not passed"
    files = sorted(fn[:-8] for fn in os.listdir(W.UNI_DIR)
                   if fn.endswith(".parquet"))
    nchunks = (len(files) + CHUNK - 1) // CHUNK
    raw_tr, scr_tr = [], []
    excluded_ohlc, no_volume = [], []
    last_dates = {}
    pools = {2025: {}, 2026: {}}
    scored = 0
    for k in range(nchunks):
        c = json.load(open(chunk_path(k)))
        raw_tr.extend(c["raw_trades"])
        scr_tr.extend(c["scr_trades"])
        excluded_ohlc.extend(c["excluded_ohlc"])
        no_volume.extend(c["no_volume"])
        last_dates.update(c["last_dates"])
        scored += c["scored"]
        for yr in (2025, 2026):
            for s, v in c["pools"][str(yr)].items():
                pools[yr][s] = (v[0], v[1])
    covered = scored + len(excluded_ohlc)
    print(f"finalize: files {len(files)}, scored {scored}, "
          f"excluded {len(excluded_ohlc)}, covered {covered}", flush=True)
    assert covered == len(files), "chunk coverage incomplete"

    res = json.load(open(RES))
    part1_aborted = res.pop("ABORTED", None)
    res["official_close_control"] = ck["official_close_control"]
    res["part2_basis"] = (
        "Parent decision 2026-11-17: the wide run proceeds on the "
        "OFFICIAL-CLOSE (parquet) basis as a RESEARCH basis only. The "
        "control is the parquet-fed frozen-25 run (official-close "
        "control). Published store-basis EKAM-2c numbers remain the live "
        "book's basis; the EKAM-daily forward paper is not re-baselined.")
    if part1_aborted is not None:
        res["part1_outcome_superseded"] = (
            "Part 1 stopped at the store-basis control (see 'control' and "
            "'diagnosis'). Original ABORTED text: " + part1_aborted)
    res["data"] = dict(parquet_files=len(files), scored=scored,
                       excluded_no_usable_ohlc=excluded_ohlc,
                       no_volume_column=no_volume)
    res["raw"] = {str(yr): W.stats_wide(raw_tr, yr) for yr in (2025, 2026)}
    res["raw"]["november"] = W.nov_slice(raw_tr, last_dates)
    res["screened"] = {str(yr): W.stats_wide(scr_tr, yr)
                       for yr in (2025, 2026)}
    res["screened"]["november"] = W.nov_slice(scr_tr, last_dates)
    for yr in (2025, 2026):
        st = res["screened"][str(yr)]
        st["placebo"] = W.placebo_wide(pools[yr], st["trades"], st["total"])
        print(f"screened {yr}: {st['trades']}t total {st['total']} "
              f"placebo pct {st['placebo']['percentile']}", flush=True)
        print(f"raw {yr}: {res['raw'][str(yr)]['trades']}t total "
              f"{res['raw'][str(yr)]['total']}", flush=True)
    scr = res["screened"]
    success = all(scr[str(yr)]["total"] > 0 and
                  scr[str(yr)]["placebo"]["beaten"] for yr in (2025, 2026))
    res["verdict"] = dict(
        rule="screened positive in BOTH years AND placebo beaten "
             "(percentile >= 95) in BOTH years (spec s.4)",
        success=success,
        screened_positive={str(yr): scr[str(yr)]["total"] > 0
                           for yr in (2025, 2026)},
        placebo_beaten={str(yr): scr[str(yr)]["placebo"]["beaten"]
                        for yr in (2025, 2026)},
        concentration={str(yr): dict(
            ex_top3=scr[str(yr)]["ex_top3"],
            ex_top10=scr[str(yr)]["ex_top10"],
            top5_share_pct=scr[str(yr)]["top5_share_pct"],
            top5_names=scr[str(yr)]["top5_names"],
            distinct_names=scr[str(yr)]["distinct_names"])
            for yr in (2025, 2026)})
    with open(RES, "w") as f:
        json.dump(res, f, indent=1)

    # trades CSV: preserve the Part 1 CONTROL25_PARQUET rows, append wide
    with open(TRADES_CSV, newline="") as f:
        rows = list(csv.reader(f))
    header, ctrl_rows = rows[0], [r for r in rows[1:] if r and
                                  r[0] == "CONTROL25_PARQUET"]
    assert len(ctrl_rows) == ck["control_trades"], \
        f"control rows {len(ctrl_rows)} != fresh control trades " \
        f"{ck['control_trades']}"
    with open(TRADES_CSV, "w", newline="") as f:
        wcsv = csv.writer(f)
        wcsv.writerow(header)
        for r in ctrl_rows:
            wcsv.writerow(r)
        for run, tr in (("RAW", raw_tr), ("SCREENED", scr_tr)):
            for t in sorted(tr, key=lambda x: (x["entry_date"], x["sym"])):
                wcsv.writerow([run, t["sym"], t["comps"], t["signal_date"],
                               t["entry_date"], t["exit_date"], t["entry"],
                               t["exit"], t["net"], t["hold"],
                               t["exit_kind"], t["forced"],
                               t["upgrade_date"] or ""])
    print(f"trades csv: {len(ctrl_rows)} control + {len(raw_tr)} raw + "
          f"{len(scr_tr)} screened rows", flush=True)
    print("done. verdict success =", success, flush=True)


if __name__ == "__main__":
    stage = sys.argv[1]
    if stage == "control":
        stage_control()
    elif stage == "chunk":
        stage_chunk(int(sys.argv[2]))
    elif stage == "finalize":
        stage_finalize()
    else:
        raise SystemExit(f"unknown stage {stage}")
