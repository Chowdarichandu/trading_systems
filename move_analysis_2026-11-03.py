"""Movement capacity analysis — Jan-Oct 2026, 5-min spot, both indices.
Question (Chandu): how much does each index actually move in a given
time frame, so the hunt size (10-20 premium points, then trail) can be
set from evidence. Base rates over ALL anchors (no signal selection).
"""
import json
import statistics as st
from pathlib import Path

SPOT = json.load(open(Path(__file__).parent / "daily2leg" / "spot.json"))


def pct(v, q):
    s = sorted(v)
    return s[min(len(s) - 1, int(q * len(s)))]


def analyse(idx):
    days = {d: b for d, b in SPOT[idx].items()
            if len(b) >= 74 and "2026-01-01" <= d <= "2026-10-31"}
    out = {"days": len(days)}
    # day range
    dr = []
    for d, bars in days.items():
        hi = max(b[1] for b in bars); lo = min(b[2] for b in bars)
        dr.append(hi - lo)
    out["day_range"] = (st.mean(dr), st.median(dr), pct(dr, 0.75), pct(dr, 0.90))
    # |move| over horizons (bars: 5min=1, 15=3, 30=6, 60=12)
    for h, lab in ((1, "5m"), (3, "15m"), (6, "30m"), (12, "60m")):
        mv = []
        for d, bars in days.items():
            closes = [b[3] for b in bars]
            for i in range(len(closes) - h):
                mv.append(abs(closes[i + h] - closes[i]))
        out[lab] = (st.mean(mv), st.median(mv), pct(mv, 0.75), pct(mv, 0.90), len(mv))
    # forward room + best one-way run over next 30 / 60 min from each anchor
    for h, lab in ((6, "30m"), (12, "60m")):
        room, run = [], []
        for d, bars in days.items():
            for i in range(len(bars) - h):
                w = bars[i + 1: i + 1 + h]
                hi = max(b[1] for b in w); lo = min(b[2] for b in w)
                p = bars[i][3]
                room.append(hi - lo)
                run.append(max(hi - p, p - lo))
        out["room" + lab] = (st.mean(room), st.median(room))
        out["run" + lab] = (st.mean(run), st.median(run), pct(run, 0.75))
        for need in (20, 30, 40, 60, 80, 100):
            out[f"run{lab}>={need}"] = 100.0 * sum(1 for r in run if r >= need) / len(run)
    # 30-min |move| by time-of-day bucket (anchor bar index: 0=09:15)
    buckets = {"09:15-10:30": (0, 14), "10:30-13:00": (15, 44), "13:00-15:00": (45, 69)}
    for lab, (a, b) in buckets.items():
        mv = []
        for d, bars in days.items():
            closes = [x[3] for x in bars]
            for i in range(a, min(b, len(closes) - 6)):
                mv.append(abs(closes[i + 6] - closes[i]))
        out["tod30_" + lab] = st.mean(mv)
    return out


for idx in ("BANKNIFTY", "NIFTY"):
    r = analyse(idx)
    print(f"\n===== {idx} — {r['days']} days, Jan-Oct 2026, 5-min spot =====")
    m, md, p75, p90 = r["day_range"]
    print(f"Full-day range: mean {m:.0f} · median {md:.0f} · p75 {p75:.0f} · p90 {p90:.0f} pts")
    print("|move| mean / median / p75 / p90 (pts):")
    for lab in ("5m", "15m", "30m", "60m"):
        m, md, p75, p90, n = r[lab]
        print(f"  {lab:>4}: {m:6.1f} / {md:6.1f} / {p75:6.1f} / {p90:6.1f}   (n={n})")
    for lab in ("09:15-10:30", "10:30-13:00", "13:00-15:00"):
        print(f"  30m |move| when starting {lab}: {r['tod30_' + lab]:.1f} pts")
    for lab in ("30m", "60m"):
        rm, rmd = r["room" + lab]; runm, runmd, run75 = r["run" + lab]
        print(f"Next {lab}: total room (hi-lo) mean {rm:.0f} · best one-way run mean {runm:.0f} / median {runmd:.0f} / p75 {run75:.0f} pts")
        fr = " · ".join(f">={n}pts {r[f'run{lab}>={n}']:.0f}%" for n in (20, 30, 40, 60, 80, 100))
        print(f"  best-run frequency: {fr}")
