"""Match California unclaimed-property records to IRS-registered CA nonprofits.

Usage: py match.py <raw_dir> <out_dir>
  raw_dir holds the SCO CSVs (From_*.csv) and IRS eo_ca.csv.

Precision first: a match needs the normalized name to be identical AND the
ZIP5 (tier A) or city (tier B) to agree. Tier C is name-only: the name must
belong to exactly one CA nonprofit, have 3+ words, and the owner address must
be in California. No fuzzy matching. Public agencies (not in the IRS file) are
found by keyword and written separately.
# ponytail: exact-name only; misses abbreviations/typos. Add token-set fuzzy
# matching with manual review if recall matters more than precision.
"""
import csv, glob, os, re, sys
from collections import defaultdict

PUBLIC = [
    ("school", re.compile(r"SCHOOL DISTRICT|UNIFIED SCHOOL|COMMUNITY COLLEGE DISTRICT|COUNTY OFFICE OF EDUCATION|SCHOOL DIST")),
    ("city", re.compile(r"^(CITY|TOWN) OF (?!HOPE)[A-Z]")),
    ("county", re.compile(r"^COUNTY OF [A-Z]|COUNTY (TREASURER|TAX COLLECTOR|SHERIFF|CLERK)")),
    ("special_district", re.compile(r"(FIRE PROTECTION|WATER|SANITARY|SANITATION|IRRIGATION|UTILITY|UTILITIES|HOSPITAL|HEALTHCARE|LIBRARY|PARK|RECREATION AND PARK|TRANSIT|CEMETERY|MOSQUITO ABATEMENT) DISTRICT|HOUSING AUTHORITY")),
]
DROP = {"INC", "INCORPORATED", "CORP", "CORPORATION", "THE", "CO", "LLC", "LTD", "A"}


def norm(s):
    s = s.upper().replace("&", " AND ")
    s = re.sub(r"[^A-Z0-9 ]", " ", s)
    return " ".join(t for t in s.split() if t not in DROP)


def money(s):
    try:
        return float(s)
    except ValueError:
        return 0.0


def main(raw, out):
    os.makedirs(out, exist_ok=True)
    csv.field_size_limit(10**9)

    # --- IRS Exempt Organizations Business Master File, California ---
    by_zip, by_city, by_name = defaultdict(list), defaultdict(list), defaultdict(list)
    with open(os.path.join(raw, "eo_ca.csv"), newline="", encoding="latin-1") as f:
        for r in csv.DictReader(f):
            n = norm(r["NAME"])
            if len(n) < 6:
                continue
            by_zip[(n, r["ZIP"][:5])].append(r)
            by_city[(n, norm(r["CITY"]))].append(r)
            by_name[n].append(r)

    # --- SCO unclaimed property ---
    hits = defaultdict(lambda: {"props": {}, "tier": "C"})
    public = defaultdict(lambda: {"props": {}, "cities": set()})
    rows = scanned_balance = 0
    seen_props = set()
    for path in sorted(glob.glob(os.path.join(raw, "From_*.csv"))):
        with open(path, newline="", encoding="latin-1") as f:
            for r in csv.DictReader(f):
                rows += 1
                bal = money(r["CURRENT_CASH_BALANCE"])
                if bal <= 0:
                    continue
                if r["PROPERTY_ID"] not in seen_props:
                    seen_props.add(r["PROPERTY_ID"])
                    scanned_balance += bal
                n = norm(r["OWNER_NAME"])
                orgs = by_zip.get((n, r["OWNER_ZIP"][:5]))
                tier = "A"
                if not orgs:
                    orgs = by_city.get((n, norm(r["OWNER_CITY"])))
                    tier = "B"
                if not orgs and r["OWNER_STATE"] == "CA" and len(n.split()) >= 3:
                    orgs = by_name.get(n)
                    tier = "C"
                    if orgs and len(orgs) != 1:
                        orgs = None
                if not orgs:
                    if r["OWNER_STATE"] == "CA":
                        for cls, rx in PUBLIC:
                            if rx.search(n):
                                pe = public[(cls, n)]
                                pe["props"][r["PROPERTY_ID"]] = r
                                pe["cities"].add(r["OWNER_CITY"])
                                break
                    continue
                h = hits[orgs[0]["EIN"]]
                h["org"], h["n_same_name"] = orgs[0], len(orgs)
                h["tier"] = min(h["tier"], tier)
                prev = h["props"].get(r["PROPERTY_ID"])
                r["PROPERTY_MATCH_TIER"] = min(tier, prev["PROPERTY_MATCH_TIER"]) if prev else tier
                h["props"][r["PROPERTY_ID"]] = r

    out_rows, detail = [], []
    for ein, h in hits.items():
        o, props = h["org"], h["props"].values()
        total = sum(money(p["CURRENT_CASH_BALANCE"]) for p in props)
        out_rows.append({
            "ein": ein, "irs_name": o["NAME"], "irs_city": o["CITY"], "irs_zip": o["ZIP"][:5],
            "subsection": o["SUBSECTION"], "ntee": o["NTEE_CD"], "irs_revenue": o["REVENUE_AMT"],
            "last_990_period": o["TAX_PERIOD"], "match_tier": h["tier"],
            "irs_orgs_same_name_place": h["n_same_name"],
            "n_properties": len(h["props"]), "total_balance": round(total, 2),
            "balance_place_confirmed": round(sum(money(p["CURRENT_CASH_BALANCE"]) for p in props if p["PROPERTY_MATCH_TIER"] != "C"), 2),
            "n_with_pending_claim": sum(p["NUMBER_OF_PENDING_CLAIMS"] not in ("", "0") for p in props),
            "n_multi_owner": sum(p["NO_OF_OWNERS"] not in ("", "1") for p in props),
            "largest_property": max(money(p["CURRENT_CASH_BALANCE"]) for p in props),
            "holders": "; ".join(sorted({p["HOLDER_NAME"] for p in props})[:6]),
            "property_ids": " ".join(sorted(h["props"])),
        })
        for p in props:
            detail.append({"ein": ein, "irs_name": o["NAME"], "match_tier": h["tier"], **p})
    out_rows.sort(key=lambda r: -r["total_balance"])

    for name, data in (("nonprofit_matches.csv", out_rows), ("nonprofit_match_properties.csv", detail)):
        with open(os.path.join(out, name), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0]))
            w.writeheader()
            w.writerows(data)

    pub_rows = []
    for (cls, n), pe in public.items():
        props = pe["props"].values()
        pub_rows.append({
            "class": cls, "owner_name_normalized": n,
            "n_properties": len(pe["props"]),
            "total_balance": round(sum(money(p["CURRENT_CASH_BALANCE"]) for p in props), 2),
            "n_with_pending_claim": sum(p["NUMBER_OF_PENDING_CLAIMS"] not in ("", "0") for p in props),
            "owner_cities": "; ".join(sorted(pe["cities"])[:5]),
            "holders": "; ".join(sorted({p["HOLDER_NAME"] for p in props})[:6]),
            "property_ids": " ".join(sorted(pe["props"])),
        })
    pub_rows.sort(key=lambda r: -r["total_balance"])
    with open(os.path.join(out, "public_agency_candidates.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(pub_rows[0]))
        w.writeheader()
        w.writerows(pub_rows)
    for cls, _ in PUBLIC:
        s = [r for r in pub_rows if r["class"] == cls]
        print(f"public/{cls}: {len(s):,} names, {sum(r['n_properties'] for r in s):,} properties, ${sum(r['total_balance'] for r in s):,.0f}")
        for r in s[:8]:
            print(f"    ${r['total_balance']:>13,.2f} {r['n_properties']:>5}  {r['owner_name_normalized']}")

    tot = sum(r["total_balance"] for r in out_rows)
    print(f"SCO rows scanned: {rows:,}; distinct open properties: {len(seen_props):,}; balance ${scanned_balance:,.0f}")
    print(f"Nonprofits matched: {len(out_rows):,}; properties: {len(detail):,}; total ${tot:,.0f}")
    for t in "ABC":
        s = [r for r in out_rows if r["match_tier"] == t]
        ps = [p for p in detail if p["PROPERTY_MATCH_TIER"] == t]
        print(f"  tier {t}: {len(s):,} orgs (best tier), ${sum(r['total_balance'] for r in s):,.0f}; "
              f"property-level {len(ps):,} properties ${sum(money(p['CURRENT_CASH_BALANCE']) for p in ps):,.0f}")
    for r in out_rows[:40]:
        print(f"  ${r['total_balance']:>13,.2f}  {r['n_properties']:>4}  {r['match_tier']}  {r['irs_name']} ({r['irs_city']})")


def demo():
    assert norm("The Yolo Food Bank, Inc.") == norm("YOLO FOOD BANK") == "YOLO FOOD BANK"
    assert norm("A & B Co") == "AND B"
    assert money("12.50") == 12.5 and money("") == 0.0


if __name__ == "__main__":
    demo()
    main(sys.argv[1], sys.argv[2])
