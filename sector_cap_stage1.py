#!/usr/bin/env python3
"""SECTOR ADDITIONS — Rs3,000 PRICE-CAP RETEST, STAGE 1.
Owner rule (2026-11-17 07:43 IST): "We are not trading anything more
than 3000 rupees" — no stock priced above Rs3,000 is traded.

From the LOCAL daily dump only (universe_daily/<SYM>.parquet, through
2026-11-13):
  1. the 12 proposed additions marked IN (latest close <= 3000) / OUT;
  2. for every OUT name, the replacement: the sector report's named
     alternate if it qualifies (Cement AMBUJACEM, Hospitals MAXHEALTH),
     else walk down that sector's liquidity ranking in the dump
     (median Oct-2026 traded value) to the first name with
     latest close <= 3000 AND median >= Rs1 crore;
  3. the frozen 25 incumbents checked against the cap (report only).

Sector membership: the official NIFTY 200 constituent list on disk
(wide200_universe_2026-11-11.csv, fetched 2026-11-11 from
niftyindices.com) "Industry" column, plus an explicit supplement list
below for liquid sector members outside the NIFTY 200.
Writes sector_cap_stage1.json. Research only."""
import csv, json, os
import pandas as pd

WS = "/home/hatch/workspace/trading"
DUMP = f"{WS}/universe_daily"
CAP = 3000.0
FLOOR_CR = 1.0  # Rs 1 crore median daily traded value

FROZEN25 = ["ASTRAL", "BDL", "GLENMARK", "GODREJCP", "HDFCBANK",
            "HINDALCO", "HINDCOPPER", "HINDUNILVR", "HINDZINC",
            "INDUSTOWER", "IRCTC", "ITC", "KALYANKJIL", "NATIONALUM",
            "NHPC", "NTPC", "OBEROIRLTY", "OIL", "PFC", "RECLTD",
            "TATASTEEL", "TVSMOTOR", "UNITDSPR", "VEDL", "WIPRO"]
ADD12 = ["ULTRACEMCO", "LT", "SBILIFE", "APOLLOHOSP", "ICICIBANK", "SBIN",
         "RELIANCE", "INFY", "M&M", "BHARTIARTL", "SUNPHARMA", "TITAN"]
ADD_SECTOR = {"ULTRACEMCO": "Cement", "LT": "Capital Goods",
              "SBILIFE": "Insurance", "APOLLOHOSP": "Hospitals",
              "ICICIBANK": "Banking", "SBIN": "Banking — PSU",
              "RELIANCE": "Energy (Oil & Gas)", "INFY": "IT",
              "M&M": "Auto", "BHARTIARTL": "Telecom",
              "SUNPHARMA": "Pharma", "TITAN": "Retail / Consumer Durables"}
# sector report's named alternates (sector_coverage_2026-11-17.md s.3)
NAMED_ALT = {"Cement": "AMBUJACEM", "Hospitals": "MAXHEALTH",
             "Auto": "MARUTI", "Retail / Consumer Durables": "TRENT",
             "Capital Goods": None, "Insurance": "HDFCLIFE",
             "Energy (Oil & Gas)": "ONGC", "IT": "TCS", "Pharma": "CIPLA",
             "Banking": None, "Banking — PSU": None, "Telecom": None}

# --- sector buckets for the walk-down (NSE industry names in the
# NIFTY 200 list) + supplements for liquid members outside the 200.
# Cement: the NIFTY 200 list carries cement under "Construction
# Materials" (AMBUJACEM, ULTRACEMCO); supplements add the other
# listed cement makers. Hospitals: the NIFTY "Healthcare" industry
# mixes pharma with hospitals, so the bucket is the hospital-operator
# list only. Cement and Hospitals take the task-assigned named
# alternate first (named_first=True); the rest walk down the ranking.
BUCKETS = {
    "Cement": dict(ind=["Construction Materials"],
                   supp=["ACC", "SHREECEM", "DALBHARAT", "RAMCOCEM",
                         "JKCEMENT", "BIRLACORPN", "JKLCEMENT", "NUVOCO",
                         "HEIDELBERG", "ORIENTCEM", "SAGARCEM"],
                   named_first=True),
    "Capital Goods": dict(
        ind=["Capital Goods"],
        supp=["CGPOWER", "POLYCAB", "KEI", "RRKABEL", "THERMAX",
              "KIRLOSENG", "ELGIEQUIP", "TIMKEN", "WABAG", "GRINDWELL"],
        named_first=False),
    "Hospitals": dict(ind=[],
                      supp=["APOLLOHOSP", "MAXHEALTH", "FORTIS", "NH",
                            "KIMS", "RAINBOW", "ASTERDM", "MEDANTA",
                            "YATHARTH", "HCG"],
                      named_first=True),
    "Auto": dict(
        ind=["Automobile and Auto Components"],
        supp=["TMPV", "TATAMOTORS", "ASHOKLEY", "MOTHERSON", "APOLLOTYRE",
              "EXIDEIND", "SONACOMS", "BALKRISIND", "CEATLTD", "JKTYRE"],
        named_first=False),
    # the coverage report's bucket is "Retail / Consumer Durables":
    # NSE "Consumer Durables" + the retail names carried in
    # "Consumer Services" (avenue/trent class) — listed explicitly.
    "Retail / Consumer Durables": dict(
        ind=["Consumer Durables"],
        supp=["DMART", "TRENT", "ABFRL", "SHOPERSTOP", "VMART", "VMM",
              "SPENCERS", "METROBRAND", "BATAINDIA", "RELAXO", "CAMPUS"],
        named_first=False),
}


def metrics(sym):
    path = f"{DUMP}/{sym}.parquet"
    if not os.path.exists(path):
        return None
    df = pd.read_parquet(path, columns=["date", "close", "volume"])
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    oct26 = df[(df["date"] >= "2026-10-01") & (df["date"] <= "2026-10-31")]
    med_cr = float((oct26["close"] * oct26["volume"]).median()) / 1e7
    latest = df.iloc[-1]
    return dict(sym=sym, latest_close=round(float(latest["close"]), 2),
                latest_date=str(latest["date"].date()),
                oct2026_median_traded_value_cr=round(med_cr, 2),
                oct2026_sessions=int(len(oct26)))


def main():
    out = {}
    # ---- 1. the 12 additions: IN / OUT
    adds = {}
    for s in ADD12:
        m = metrics(s)
        m["sector"] = ADD_SECTOR[s]
        m["cap_status"] = "IN" if m["latest_close"] <= CAP else "OUT"
        adds[s] = m
    out["additions12"] = adds
    print("=== THE 12 ADDITIONS vs the Rs3,000 cap (latest close 2026-11-13) ===")
    for s in ADD12:
        m = adds[s]
        print(f"  {s:12s} {m['sector']:26s} close {m['latest_close']:>10}  "
              f"medVal {m['oct2026_median_traded_value_cr']:>9} cr  -> {m['cap_status']}")

    # ---- incumbents vs the cap (report only)
    inc = {}
    for s in FROZEN25:
        m = metrics(s)
        m["above_cap"] = m["latest_close"] > CAP
        inc[s] = m
    out["incumbents25"] = inc
    above = [s for s in FROZEN25 if inc[s]["above_cap"]]
    print(f"\n=== INCUMBENTS ABOVE CAP: {above} ===")
    for s in above:
        print(f"  {s}: close {inc[s]['latest_close']}")

    # ---- sector membership from the official NIFTY 200 list
    rows = [l for l in open(f"{WS}/wide200_universe_2026-11-11.csv")
            if not l.startswith("#")]
    ind_of = {}
    for r in csv.DictReader(rows):
        ind_of[r["Symbol"]] = r["Industry"]
    out["industry_source"] = ("wide200_universe_2026-11-11.csv — official "
                              "NIFTY 200 constituent list (niftyindices.com, "
                              "fetched 2026-11-11), Industry column")

    # ---- 2. replacements for the OUT names
    replacements = {}
    for s in ADD12:
        if adds[s]["cap_status"] == "IN":
            continue
        sector = ADD_SECTOR[s]
        bucket = BUCKETS[sector]
        members = {sym for sym, ind in ind_of.items() if ind in bucket["ind"]}
        members |= set(bucket["supp"])
        members.discard(s)
        # incumbents are already in the universe — a replacement must
        # be a NEW name, so the frozen 25 are excluded from the ranking
        members -= set(FROZEN25)
        ranked = []
        for sym in sorted(members):
            m = metrics(sym)
            if m is None:
                continue
            m["industry"] = ind_of.get(sym, "(supplement list)")
            ranked.append(m)
        ranked.sort(key=lambda m: -m["oct2026_median_traded_value_cr"])

        def qualifies(m):
            return m["latest_close"] <= CAP and \
                m["oct2026_median_traded_value_cr"] >= FLOOR_CR

        pick = None
        named0 = NAMED_ALT.get(sector)
        if bucket.get("named_first") and named0:
            cand = next((m for m in ranked if m["sym"] == named0), None)
            if cand is not None and qualifies(cand):
                pick = cand
        if pick is None:
            for m in ranked:
                if qualifies(m):
                    pick = m
                    break
        named = NAMED_ALT.get(sector)
        replacements[sector] = dict(
            out_name=s, out_close=adds[s]["latest_close"],
            named_alternate=named,
            named_alternate_is_pick=bool(pick and named == pick["sym"]),
            pick=(pick["sym"] if pick else None), pick_detail=pick,
            ranking=[dict(sym=m["sym"], close=m["latest_close"],
                          med_cr=m["oct2026_median_traded_value_cr"],
                          industry=m["industry"]) for m in ranked[:12]])
        print(f"\n--- REPLACEMENT for {s} ({sector}), out at "
              f"{adds[s]['latest_close']} ---")
        for m in ranked[:12]:
            ok = m["latest_close"] <= CAP and \
                m["oct2026_median_traded_value_cr"] >= FLOOR_CR
            print(f"    {m['sym']:12s} close {m['latest_close']:>10}  medVal "
                  f"{m['oct2026_median_traded_value_cr']:>9} cr  "
                  f"{'<= PICK' if pick and m['sym'] == pick['sym'] else ''}"
                  f"{'' if ok else '  (fails cap/floor)'}")
        print(f"  PICK: {pick['sym'] if pick else 'NONE — sector left uncovered'}")
    out["replacements"] = replacements

    # ---- final capped addition set
    final = []
    for s in ADD12:
        if adds[s]["cap_status"] == "IN":
            final.append(dict(sym=s, sector=ADD_SECTOR[s], via="original pick",
                              close=adds[s]["latest_close"],
                              med_cr=adds[s]["oct2026_median_traded_value_cr"]))
    for sector, r in replacements.items():
        if r["pick"]:
            final.append(dict(sym=r["pick"], sector=sector,
                              via=f"replacement for {r['out_name']}",
                              close=r["pick_detail"]["latest_close"],
                              med_cr=r["pick_detail"]["oct2026_median_traded_value_cr"]))
    out["final_capped_additions"] = final
    print(f"\n=== FINAL CAPPED ADDITION SET: {len(final)} names "
          f"(universe 25 + {len(final)} = {25 + len(final)}) ===")
    for f in final:
        print(f"  {f['sym']:12s} {f['sector']:26s} close {f['close']:>10}  "
              f"medVal {f['med_cr']:>9} cr  [{f['via']}]")
    json.dump(out, open(f"{WS}/sector_cap_stage1.json", "w"), indent=1)
    print("\nWROTE sector_cap_stage1.json")


if __name__ == "__main__":
    main()
