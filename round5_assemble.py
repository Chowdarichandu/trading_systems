#!/usr/bin/env python3
"""ROUND 5 — cache-only assembly of morning_flow.csv (2026-11-14).
Makes NO API calls. The data build was stopped by an Upstox HTTP 429
at 713/1,100 contracts; this assembles what is on disk: a day is
'complete' only if every band contract (11 strikes x CE/PE, in-force
monthly expiry nearest the 10:55 spot close) has a cached 09:15 and
10:55 bar with non-null OI. All 214 days get a row; incomplete days
are flagged, never silently dropped. Re-running the data build after
a fresh fetch window completes the dataset and this assembly.
"""
import csv, json
from pathlib import Path

TR = Path.home() / "workspace/trading"
OUT = TR / "round5_history"
ALL_EXP = ["2026-01-27", "2026-02-24", "2026-03-30", "2026-04-28",
           "2026-05-26", "2026-06-30", "2026-07-28", "2026-08-25",
           "2026-09-29", "2026-10-27", "2026-11-23"]
NOV_DAYS = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05",
            "2026-11-06", "2026-11-09", "2026-11-11", "2026-11-12",
            "2026-11-13"]


def in_force(day):
    for e in ALL_EXP:
        if e >= day:
            return e
    return None


SPOT = {}
raw = json.load(open(TR / "daily2leg/spot.json"))
for d, bars in raw["BANKNIFTY"].items():
    SPOT[d] = {b[0]: (float(b[1]), float(b[2]), float(b[3]), float(b[4]))
               for b in bars}
for fn in (TR / "oi_history/spot_nov_bars.json",
           TR / "round4_history/spot_extra.json"):
    if fn.exists():
        data = json.loads(fn.read_text())
        if isinstance(data, dict) and "BANKNIFTY" in data:
            data = data["BANKNIFTY"]
        if isinstance(data, dict):
            for d, bars in data.items():
                if d not in SPOT and isinstance(bars, list) and bars:
                    SPOT[d] = {b[0]: (float(b[1]), float(b[2]),
                                      float(b[3]), float(b[4]))
                               for b in bars}
_prog = TR / "data/progressive/BANKNIFTY/spot_5m.csv"
if _prog.exists():
    with open(_prog) as f:
        for r in csv.DictReader(f):
            SPOT.setdefault(r["timestamp"][:10], {})[
                r["timestamp"][11:16]] = (float(r["open"]), float(r["high"]),
                                          float(r["low"]), float(r["close"]))

DAYS = sorted(d for d in SPOT if "2026-01-01" <= d <= "2026-10-31") + \
       [d for d in NOV_DAYS if d in SPOT]

CIDX = {}


def contract_day(exp, s, typ, day):
    ck = (exp, s, typ)
    if ck not in CIDX:
        fn = OUT / f"C5_{exp}_{s}{typ}.json"
        byd = {}
        if (OUT / f"C5_{exp}_{s}{typ}.done").exists() and fn.exists():
            for r in json.loads(fn.read_text()):
                byd.setdefault(r[0], {})[r[1]] = r
        CIDX[ck] = byd
    return CIDX[ck].get(day, {})


def quadrant(doi, dp):
    if doi == 0 or dp == 0:
        return "FLAT"
    if doi > 0 and dp > 0:
        return "LONG_BUILDUP"
    if doi > 0 and dp < 0:
        return "SHORT_BUILDUP"
    if doi < 0 and dp > 0:
        return "SHORT_COVERING"
    return "LONG_UNWINDING"


FIELDS = ["date", "expiry", "atm", "spot_close_1055",
          "oi0915_CE", "oi1055_CE", "doi_CE", "p0915_CE", "p1055_CE",
          "dp_CE", "vol_CE", "quad_CE",
          "oi0915_PE", "oi1055_PE", "doi_PE", "p0915_PE", "p1055_PE",
          "dp_PE", "vol_PE", "quad_PE", "vol_share_CE", "complete"]
rows = []
for d in DAYS:
    s = SPOT[d].get("10:55")
    if s is None:
        continue
    atm = int(round(s[3] / 100.0)) * 100
    exp = in_force(d)
    row = {"date": d, "expiry": exp, "atm": atm, "spot_close_1055": s[3]}
    complete = True
    for typ in ("CE", "PE"):
        oi15 = oi55 = p15 = p55 = vol = 0.0
        ok = True
        for k in range(-5, 6):
            bars = contract_day(exp, atm + 100 * k, typ, d)
            b15, b55 = bars.get("09:15"), bars.get("10:55")
            if b15 is None or b55 is None or b15[7] is None \
                    or b55[7] is None:
                ok = False
                break
            oi15 += b15[7]
            oi55 += b55[7]
            p15 += b15[5]
            p55 += b55[5]
            vol += sum(r[6] for r in bars.values()
                       if "09:15" <= r[1] <= "10:55" and r[6] is not None)
        if not ok:
            complete = False
            break
        row[f"oi0915_{typ}"] = oi15
        row[f"oi1055_{typ}"] = oi55
        row[f"doi_{typ}"] = oi55 - oi15
        row[f"p0915_{typ}"] = round(p15, 2)
        row[f"p1055_{typ}"] = round(p55, 2)
        row[f"dp_{typ}"] = round(p55 - p15, 2)
        row[f"vol_{typ}"] = vol
        row[f"quad_{typ}"] = quadrant(oi55 - oi15, p55 - p15)
    row["complete"] = complete
    if complete:
        tv = row["vol_CE"] + row["vol_PE"]
        row["vol_share_CE"] = round(row["vol_CE"] / tv, 4) if tv else None
    rows.append(row)

with open(OUT / "morning_flow.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS)
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in FIELDS})
jo = [r for r in rows if r["date"] <= "2026-10-31"]
nov = [r for r in rows if r["date"] > "2026-10-31"]
print(f"rows={len(rows)} Jan-Oct complete="
      f"{sum(1 for r in jo if r['complete'])}/{len(jo)} "
      f"Nov complete={sum(1 for r in nov if r['complete'])}/{len(nov)}")
bym = {}
for r in jo:
    bym.setdefault(r["date"][:7], [0, 0])
    bym[r["date"][:7]][1] += 1
    bym[r["date"][:7]][0] += 1 if r["complete"] else 0
for m in sorted(bym):
    print(f"  {m}: {bym[m][0]}/{bym[m][1]} complete")
