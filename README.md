# California unclaimed property owed to nonprofits

California's State Controller publishes its whole unclaimed property database as CSV, with owner names and balances. The IRS publishes every tax-exempt organization in the state. This repo matches the two.

Using the state file dated 2026-11-04 (every open property of $100 or more, 13.3 million of them) and the IRS file for California:

| | Organizations | Properties | Owed |
|---|---|---|---|
| Name matches and ZIP or city matches | 5,055 | 9,963 | $14,223,357 |
| &nbsp;&nbsp;ZIP match only (tier A) | | 6,484 | $9,497,677 |
| &nbsp;&nbsp;City-only match (tier B, weaker) | | 3,479 | $4,725,680 |
| of which 501(c)(3) | 4,359 | | $12,124,971 |
| of which no claim pending | | 8,979 | $11,485,697 |
| Payment processors as holder (PayPal, Stripe, Block) | 1,001 | 1,026 | $1,291,494 |

`data/nonprofits_confirmed_matches.csv` has one row per organization: EIN, IRS name and city, amount, number of properties, the holders, and the state property IDs. Anyone can look up an ID at https://claimit.ca.gov/app/claim-search (leave the name blank, put the ID in the Property ID box). Claiming is free and goes through the Controller.

## How it matches

Names are uppercased, `&` becomes `AND`, punctuation is dropped, and `INC`, `CORP`, `LLC`, `LTD`, `CO`, `THE`, `A` are removed. A property counts only when its owner name equals an IRS organization name **and** the ZIP matches (tier A) or the city matches (tier B). Nothing fuzzy.

The script also computes a tier C (name only, name unique among California nonprofits, three or more words) and a keyword scan for school districts, cities and counties. Those are lead lists and are not in the published file or the table above.

## How good is it? (measured, see paper/PAPER.md)

- **Precision.** In a random sample of 150 matches (`audit/audit_precision_sample.csv`), 48% agree with the IRS street address or PO box (60% for ZIP matches, only 6% for city-only matches). Four more (2.7%) have generic names I can't vouch for. The remaining ~74 pair distinctive names with the same city or ZIP but a different address, and I think they're mostly the same organization, but that is my reading, not a check. Treat 48% to 97% as the bracket. About 5% of the sample are credit unions, health plans and similar, which the IRS lists as exempt.
- **Recall is low.** I scanned the whole state file for owner names containing "food bank", "Make-A-Wish" or "children's hospital" (`audit/audit_recall_categories.csv`) and compared with what the exact match found: food banks 17% of dollars, Make-A-Wish 1%, children's hospitals 8%. The state stores abbreviated, truncated and chapter-level names ("ALAMEDA CO FOOD BANK") that differ from the legal IRS name. The $14.2M is a floor, and in sectors like these it may be low by a large factor.
- **The keyword totals line up with CBS.** The same scan finds $93.6K held for food banks and $47.2K for Make-A-Wish, close to the "at least $95,000" and "more than $46,000" CBS News California reported in March.
- **A relaxed pass** (`analysis/match_relaxed.py`, output in `data/tierD_relaxed_matches.csv`) adds 338 properties, $291,801, 197 organizations. It keeps only abbreviation-equal names and visibly truncated names. A looser prefix rule produced mostly false matches (a hospital matched to its own foundation, a school district to its education foundation), so I dropped it. Not included in the headline.
- **Live spot check.** Three property IDs looked up on the state's site on 2026-11-10 all matched the file: 1034194536 and 1025048383 (Yolo Food Bank, $2,000.00 and $555.32) and 1046558277 (United Pompe Foundation, PayPal, $35,530.53).
- **Other caveats.** The IRS file includes hospitals and universities, not just small charities. Some properties list several owners. A pending claim means someone filed, not who. The files change weekly. Properties under $100 and securities were not scanned.

## Re-running

```
py -3 analysis/match.py <raw_dir> <out_dir>
```

`raw_dir` needs the state CSVs (`From_*.csv`, from https://sco.ca.gov/upd_download_property_records.html) and `eo_ca.csv` from https://www.irs.gov/pub/irs-soi/eo_ca.csv. Standard library only. About 10 minutes for the $100+ files.

## Sources

- California State Controller, unclaimed property records download
- IRS Exempt Organizations Business Master File, California extract
- Julie Watts, "California unclaimed property: state owes charities money", CBS News California, 2026-03-11

## License

Code: MIT. Data: CC0. The underlying records are public government data.
