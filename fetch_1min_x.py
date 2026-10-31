"""Fetch 1-min index candles (Upstox helper) for family (x) days. Paper only.
Saves CSVs to ~/workspace/trading/data/1min/<INDEX>/spot_1m_<date>.csv
plus a manifest JSON. One request per instrument-day.
"""
import json, os, subprocess, sys, time

HELPER = os.path.expanduser("~/workspace/custom-connectors/custom.upstox/bin/upstox.py")
OUT = os.path.expanduser("~/workspace/trading/data/1min")
KEYS = {"NIFTY": "NSE_INDEX|Nifty 50", "BANKNIFTY": "NSE_INDEX|Nifty Bank"}
DAYS = ["2026-01-09", "2026-02-06", "2026-03-30", "2026-04-02", "2026-05-13",
        "2026-06-29", "2026-07-08", "2026-08-19",
        "2026-01-21", "2026-02-24", "2026-03-16", "2026-03-13", "2026-03-23",
        "2026-04-24", "2026-05-05", "2026-07-22", "2026-08-12", "2026-08-27",
        "2026-09-29", "2026-09-07", "2026-10-08", "2026-10-23"]

def fetch(idx, day):
    cmd = [sys.executable, HELPER, "candles", "--instrument-key", KEYS[idx],
           "--unit", "minutes", "--interval", "1", "--from", day, "--to", day]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if p.returncode != 0:
        return None, f"exit {p.returncode}: {p.stderr[:300]}"
    try:
        payload = json.loads(p.stdout)
    except Exception as e:
        return None, f"bad json: {e}: {p.stdout[:300]}"
    if payload.get("status") != "success":
        return None, f"status={payload.get('status')}: {str(payload)[:300]}"
    rows = payload["data"]["candles"]
    # rows: [timestamp, open, high, low, close, volume, oi], newest first
    rows = sorted(rows, key=lambda r: r[0])
    return rows, None

def main():
    manifest = {}
    for idx in KEYS:
        os.makedirs(os.path.join(OUT, idx), exist_ok=True)
    for day in DAYS:
        for idx in KEYS:
            path = os.path.join(OUT, idx, f"spot_1m_{day}.csv")
            if os.path.exists(path):
                manifest[f"{idx}/{day}"] = "cached"
                print(f"cached {idx} {day}")
                continue
            rows, err = fetch(idx, day)
            if err:
                manifest[f"{idx}/{day}"] = f"FAILED: {err}"
                print(f"FAILED {idx} {day}: {err}")
                continue
            with open(path, "w") as f:
                f.write("timestamp,open,high,low,close\n")
                for r in rows:
                    f.write(f"{r[0]},{r[1]},{r[2]},{r[3]},{r[4]}\n")
            manifest[f"{idx}/{day}"] = f"{len(rows)} bars, {rows[0][0]}..{rows[-1][0]}"
            print(f"ok {idx} {day}: {len(rows)} bars")
            time.sleep(0.3)
    with open(os.path.join(OUT, "manifest_1min_x.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
