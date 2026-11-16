"""Relaxed second-stage match (tier D) for owner names the exact match missed.

The state stores owner names truncated (~40 chars) and abbreviated, so a charity's
legal IRS name often is not equal to the name its money sits under. Tier D accepts
a record only when ALL hold:
  * same ZIP5 as one IRS organization (California),
  * after punctuation/abbreviation normalization, the owner name equals the IRS name
    or is a PREFIX of it (truncation), with at least 3 tokens,
  * exactly one IRS EIN in that ZIP satisfies the rule (no ambiguity),
  * the property was not already matched by tiers A-C.

Usage: py match_relaxed.py <raw_dir> <exact_props_csv> <out_dir>
"""
import csv, glob, os, re, sys
from collections import defaultdict

DROP = {"INC", "INCORPORATED", "CORP", "CORPORATION", "THE", "LLC", "LTD", "A", "CO"}
ABBR = {"ASSN": "ASSOCIATION", "ASSOC": "ASSOCIATION", "FDN": "FOUNDATION", "FOUND": "FOUNDATION",
        "CTR": "CENTER", "CNTR": "CENTER", "MED": "MEDICAL", "HOSP": "HOSPITAL", "UNIV": "UNIVERSITY",
        "DEPT": "DEPARTMENT", "INTL": "INTERNATIONAL", "CMTY": "COMMUNITY", "SVCS": "SERVICES",
        "SERV": "SERVICE", "CHILDRENS": "CHILDREN", "WOMENS": "WOMEN", "MENS": "MEN"}


def toks(s):
    s = s.upper().replace("'", "").replace("&", " AND ")
    s = re.sub(r"[^A-Z0-9 ]", " ", s)
    return tuple(ABBR.get(t, t) for t in s.split() if t not in DROP)


def money(s):
    try:
        return float(s)
    except ValueError:
        return 0.0


def main(raw, exact_props, out):
    os.makedirs(out, exist_ok=True)
    csv.field_size_limit(10**9)
    done = set()
    with open(exact_props, newline="", encoding="utf-8") as f:
        done.update(r["PROPERTY_ID"] for r in csv.DictReader(f))

    idx = defaultdict(list)  # (zip5, first token) -> [(tokens, ein, row)]
    with open(os.path.join(raw, "eo_ca.csv"), newline="", encoding="latin-1") as f:
        for r in csv.DictReader(f):
            t = toks(r["NAME"])
            if len(t) >= 2:
                idx[(r["ZIP"][:5], t[0])].append((t, r["EIN"], r))

    props = {}
    for path in sorted(glob.glob(os.path.join(raw, "From_*.csv"))):
        with open(path, newline="", encoding="latin-1") as f:
            for r in csv.DictReader(f):
                if r["PROPERTY_ID"] in done or money(r["CURRENT_CASH_BALANCE"]) <= 0:
                    continue
                t = toks(r["OWNER_NAME"])
                if len(t) < 3:
                    continue
                cands = idx.get((r["OWNER_ZIP"][:5], t[0]))
                if not cands:
                    continue
                eins = {}
                for it, ein, row in cands:
                    if it == t:
                        eins[ein] = ("equal", row)
                    elif it[:len(t)] == t:
                        eins.setdefault(ein, ("prefix", row))
                if len(eins) != 1:
                    continue
                ein, (how, row) = next(iter(eins.items()))
                key = (r["PROPERTY_ID"], ein)
                if key not in props:
                    props[key] = {"ein": ein, "irs_name": row["NAME"], "irs_city": row["CITY"], "irs_zip": row["ZIP"][:5],
                                  "subsection": row["SUBSECTION"], "how": how, **{k: r[k] for k in (
                                      "PROPERTY_ID", "OWNER_NAME", "OWNER_STREET_1", "OWNER_CITY", "OWNER_ZIP",
                                      "HOLDER_NAME", "PROPERTY_TYPE", "CURRENT_CASH_BALANCE", "NUMBER_OF_PENDING_CLAIMS")}}
    rows = list(props.values())
    with open(os.path.join(out, "tierD_properties.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    orgs = defaultdict(lambda: [0, 0.0, ""])
    for r in rows:
        o = orgs[r["ein"]]
        o[0] += 1
        o[1] += money(r["CURRENT_CASH_BALANCE"])
        o[2] = r["irs_name"]
    print(f"tier D: {len(rows):,} properties, {len(orgs):,} orgs, ${sum(r['CURRENT_CASH_BALANCE'] and money(r['CURRENT_CASH_BALANCE']) for r in rows):,.0f}")
    for how in ("equal", "prefix"):
        s = [r for r in rows if r["how"] == how]
        print(f"  {how}: {len(s):,} properties ${sum(money(r['CURRENT_CASH_BALANCE']) for r in s):,.0f}")
    for ein, (n, tot, name) in sorted(orgs.items(), key=lambda kv: -kv[1][1])[:15]:
        print(f"  ${tot:>10,.0f} {n:>4} {name}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
