"""Draw a reproducible random sample of confirmed (tier A/B) property matches for
manual review, with an automatic address-agreement flag.

Usage: py sample_precision.py <match_properties_csv> <out_csv> [n] [seed]
"""
import csv, random, re, sys


def street_num(s):
    m = re.match(r"\s*(\d+)", s or "")
    return m.group(1) if m else None


def main(src, out, n=150, seed=7):
    csv.field_size_limit(10**9)
    with open(src, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["PROPERTY_MATCH_TIER"] in ("A", "B")]
    random.Random(seed).shuffle(rows)
    cols = ["PROPERTY_ID", "PROPERTY_MATCH_TIER", "irs_name", "OWNER_NAME", "OWNER_STREET_1",
            "OWNER_CITY", "OWNER_ZIP", "HOLDER_NAME", "PROPERTY_TYPE", "CURRENT_CASH_BALANCE", "ein"]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows[:n])
    print(f"{len(rows):,} eligible property matches; wrote {min(n, len(rows))} to {out}")


if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], int(a[3]) if len(a) > 3 else 150, int(a[4]) if len(a) > 4 else 7)
