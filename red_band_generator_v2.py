"""
Red band generator v2 — institutional parameters given by Chandu 2026-10-28.

Dual pipeline:
  Master bands: Daily OHLC, 60-session rolling lookback (truncated by
    available data), points = daily wick highs and lows (old support
    flipped to resistance is represented by repeated wick touches).
  Tactical ledges: 15-minute data, 20-session rolling lookback, points =
    15-min swing highs/lows AND consolidation shelves (3+ consecutive
    15-min bars paused in a <=50pt range before expansion).

Rules (exact, per user):
  - Non-chaining centroid clustering: NO chaining. A cluster starts at
    its lowest unused point and includes only points <= start + 50.
    The next cluster starts after that window. This cannot merge into
    500+ point bands.
  - Session deduplication: group points by session_date BEFORE counting.
    Multiple touches in one session count as 1. A band needs >=3
    distinct sessions.
  - Width: dynamic wick overlap, hard cap 50 points. Cluster width is
    max-min of its session-representative points, and is <=50 by
    construction. If a denser core exists, the densest 50pt window is
    reported (see clip_to_core below).
  - Centre: mean of per-session representative values (median of that
    session's points inside the cluster), so one busy session cannot
    drag the centre.

No orders, no live trades, no credentials. Output only.
Usage:
  python3 red_band_generator_v2.py \
    --spot5m ~/workspace/trading/data/banknifty-2026-10/spot_5m.csv \
    --daily ~/workspace/trading/data/banknifty-2026-10/spot_daily.csv \
    --out ~/workspace/trading/data/banknifty-2026-10/red_bands_v2.json
"""
import argparse, json
import pandas as pd


def session_representatives(points):
    """points: list of (value, session_str). Return list of
    (session_str, median_value_for_that_session_in_cluster)."""
    by_session = {}
    for v, s in points:
        by_session.setdefault(s, []).append(v)
    reps = []
    for s, vals in sorted(by_session.items()):
        vals = sorted(vals)
        n = len(vals)
        med = vals[n // 2] if n % 2 == 1 else (vals[n // 2 - 1] + vals[n // 2]) / 2.0
        reps.append((s, med))
    return reps


def cluster_non_chaining(points, cap=50.0, min_sessions=3):
    """points: list of (value, session_str), unsorted.
    Returns list of dicts with low/high/centre/width/distinct_sessions/sessions.
    Non-chaining: cluster anchor = lowest remaining value; include only
    values <= anchor + cap. Next cluster starts above anchor + cap.
    """
    pts = sorted(points, key=lambda x: x[0])
    used = [False] * len(pts)
    bands = []
    for i, (v, s) in enumerate(pts):
        if used[i]:
            continue
        # Collect this window
        window_idx = []
        for j in range(i, len(pts)):
            if used[j]:
                continue
            if pts[j][0] <= v + cap:
                window_idx.append(j)
            elif pts[j][0] > v + cap:
                # sorted, but there may be used points beyond; keep scanning
                # only until we are safely past the window for unused points
                # (unused points are sorted too, so we can break on first
                # unused point past the window)
                break
        # Note: the break above only triggers on an unused point past the
        # window, which is correct for sorted unused values.
        window = [pts[j] for j in window_idx]
        reps = session_representatives(window)
        distinct = len(reps)
        if distinct >= min_sessions:
            vals = [r for _, r in reps]
            lo, hi = min(vals), max(vals)
            # Width is already <= cap by construction, but clip to the
            # densest core if for any reason lo/hi span > cap (defensive).
            if hi - lo > cap:
                # densest 50pt window over session representatives
                sv = sorted(vals)
                best = (0, sv[0])
                for k in range(len(sv)):
                    cnt = sum(1 for x in sv if sv[k] <= x <= sv[k] + cap)
                    if cnt > best[0]:
                        best = (cnt, sv[k])
                core = [x for x in sv if best[1] <= x <= best[1] + cap]
                lo, hi = min(core), max(core)
                vals = core
            centre = sum(vals) / len(vals) if vals else (lo + hi) / 2.0
            bands.append({
                "low": round(lo, 2),
                "high": round(hi, 2),
                "centre": round(centre, 2),
                "width": round(hi - lo, 2),
                "distinct_sessions": distinct,
                "sessions": [s for s, _ in reps],
            })
        for j in window_idx:
            used[j] = True
    return bands


def clip_to_core(points, cap=50.0):
    """Fallback helper, kept for explicitness: given session reps,
    return the densest <=cap window. Not used in the main path because
    cluster_non_chaining already enforces cap, but documented here as
    the user's 'clip to high-density core' rule."""
    sv = sorted(points)
    if not sv or sv[-1] - sv[0] <= cap:
        return sv
    best_lo, best_cnt = sv[0], -1
    for v in sv:
        cnt = sum(1 for x in sv if v <= x <= v + cap)
        if cnt > best_cnt:
            best_cnt, best_lo = cnt, v
    return [x for x in sv if best_lo <= x <= best_lo + cap]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spot5m", required=True)
    ap.add_argument("--daily", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--master-lookback", type=int, default=60)
    ap.add_argument("--tactical-lookback", type=int, default=20)
    ap.add_argument("--cap", type=float, default=50.0)
    ap.add_argument("--min-sessions", type=int, default=3)
    args = ap.parse_args()

    daily = pd.read_csv(args.daily, parse_dates=["date"]).sort_values("date").reset_index(drop=True)
    spot = pd.read_csv(args.spot5m, parse_dates=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    spot["session"] = spot["timestamp"].dt.strftime("%Y-%m-%d")

    # 15-min resample once
    s15 = (
        spot.set_index("timestamp")
        .groupby("session")
        .resample("15min", level="timestamp")
        .agg({"open": "first", "high": "max", "low": "min", "close": "last"})
        .dropna()
        .reset_index()
    )
    # The groupby/resample above loses a clean session column in some
    # pandas versions; rebuild it from the timestamp.
    s15["session"] = s15["timestamp"].dt.strftime("%Y-%m-%d")
    s15 = s15.sort_values("timestamp").reset_index(drop=True)

    # Swing points per session, computed on the full 15-min series
    swing_points = []  # (value, session)
    for sess, grp in s15.groupby("session"):
        grp = grp.sort_values("timestamp").reset_index(drop=True)
        for i in range(1, len(grp) - 1):
            if grp["high"].iloc[i] >= grp["high"].iloc[i - 1] and grp["high"].iloc[i] >= grp["high"].iloc[i + 1]:
                swing_points.append((float(grp["high"].iloc[i]), sess))
            if grp["low"].iloc[i] <= grp["low"].iloc[i - 1] and grp["low"].iloc[i] <= grp["low"].iloc[i + 1]:
                swing_points.append((float(grp["low"].iloc[i]), sess))

    # Consolidation shelves: 3+ consecutive 15-min bars paused in <=50pt
    # range (max high - min low <= 50), centre = mean close of the shelf.
    shelf_points = []
    for sess, grp in s15.groupby("session"):
        grp = grp.sort_values("timestamp").reset_index(drop=True)
        for i in range(len(grp) - 2):
            win = grp.iloc[i:i + 3]
            if float(win["high"].max()) - float(win["low"].min()) <= 50.0:
                shelf_points.append((float(win["close"].mean()), sess))

    daily_dates = sorted(daily["date"].dt.strftime("%Y-%m-%d").tolist())
    spot_dates = sorted(spot["session"].unique().tolist())
    # Target dates: every spot date that has a prior daily session
    result = {
        "method": "v2 non-chaining centroid, session-dedup >=3, cap 50",
        "master_lookback_sessions_requested": args.master_lookback,
        "tactical_lookback_sessions_requested": args.tactical_lookback,
        "data_note": "Daily data in this file covers only Sep 29-Oct 27, so the 60-session master lookback is truncated to available prior sessions; tactical 20-session lookback is likewise truncated early in the pilot.",
        "per_date": {},
    }

    for target in spot_dates:
        # Prior daily sessions, up to master lookback, strictly before target
        prior_daily = daily[daily["date"].dt.strftime("%Y-%m-%d") < target].tail(args.master_lookback)
        if prior_daily.empty:
            continue
        master_points = []
        for _, row in prior_daily.iterrows():
            sess = row["date"].strftime("%Y-%m-%d")
            master_points.append((float(row["high"]), sess))
            master_points.append((float(row["low"]), sess))
        master = cluster_non_chaining(master_points, cap=args.cap, min_sessions=args.min_sessions)

        # Prior spot sessions for tactical, up to tactical lookback
        prior_sessions = [d for d in spot_dates if d < target][-args.tactical_lookback:]
        tac_points = [(v, s) for v, s in swing_points if s in prior_sessions]
        tac_points += [(v, s) for v, s in shelf_points if s in prior_sessions]
        tactical = cluster_non_chaining(tac_points, cap=args.cap, min_sessions=args.min_sessions)

        result["per_date"][target] = {
            "master_lookback_actual_sessions": len(prior_daily),
            "tactical_lookback_actual_sessions": len(prior_sessions),
            "master_bands": master,
            "tactical_ledges": tactical,
        }

    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Wrote {args.out}")
    for d, v in result["per_date"].items():
        print(f"{d} master_actual={v['master_lookback_actual_sessions']} tactical_actual={v['tactical_lookback_actual_sessions']} master={len(v['master_bands'])} tactical={len(v['tactical_ledges'])}")
    return result


if __name__ == "__main__":
    main()
