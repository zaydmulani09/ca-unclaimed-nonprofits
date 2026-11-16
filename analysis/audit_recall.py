"""Recall check for the exact-name match.

Scan every $100+ state record whose owner name looks like one of the categories
CBS News California searched in March 2026 (food banks, Make-A-Wish, children's
hospitals) and compare against what the exact-name match found.

Usage: py audit_recall.py <raw_dir> <confirmed_csv> <out_csv>
"""
import csv, glob, os, re, sys

CATS = {
    "food bank/pantry": re.compile(r"\bFOOD (BANK|PANTRY|PANTRIES|CLOSET)\b"),
    "make-a-wish": re.compile(r"MAKE ?-? ?A ?-? ?WISH"),
    "children's hospital": re.compile(r"CHILDREN'?S HOSPITAL|CHILDRENS HOSPITAL"),
}


def money(s):
    try:
        return float(s)
    except ValueError:
        return 0.0


def main(raw, confirmed, out):
    csv.field_size_limit(10**9)
    matched = set()
    with open(confirmed, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            matched.update(r["property_ids"].split())
    seen, rows = set(), []
    for path in sorted(glob.glob(os.path.join(raw, "From_*.csv"))):
        with open(path, newline="", encoding="latin-1") as f:
            for r in csv.DictReader(f):
                name = r["OWNER_NAME"].upper()
                for cat, rx in CATS.items():
                    if rx.search(name):
                        key = (r["PROPERTY_ID"], name)
                        if key in seen:
                            break
                        seen.add(key)
                        rows.append({
                            "category": cat, "property_id": r["PROPERTY_ID"], "owner_name": r["OWNER_NAME"],
                            "city": r["OWNER_CITY"], "state": r["OWNER_STATE"], "zip": r["OWNER_ZIP"],
                            "balance": money(r["CURRENT_CASH_BALANCE"]), "holder": r["HOLDER_NAME"],
                            "pending": r["NUMBER_OF_PENDING_CLAIMS"],
                            "in_confirmed_match": r["PROPERTY_ID"] in matched,
                        })
                        break
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for scope, test in (("CA owner address", lambda r: r["state"] == "CA"), ("any address", lambda r: True)):
        print(f"--- {scope}")
        for cat in CATS:
            rs = [r for r in rows if r["category"] == cat and test(r)]
            tot = sum(r["balance"] for r in rs)
            hit = sum(r["balance"] for r in rs if r["in_confirmed_match"])
            n_hit = sum(r["in_confirmed_match"] for r in rs)
            print(f"{cat:22} records {len(rs):5}  total ${tot:>11,.0f}  matched {n_hit:4} ${hit:>10,.0f}  "
                  f"recall by $ {hit / tot if tot else 0:.0%}, by count {n_hit / len(rs) if rs else 0:.0%}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
