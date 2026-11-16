# California unclaimed property owed to nonprofits

California's State Controller publishes its whole unclaimed property database as CSV, with owner names and balances. The IRS publishes every tax-exempt organization in the state. This repo matches the two.

Using the state file dated 2026-11-04 (every open property of $100 or more, 13.3 million of them) and the IRS file for California:

| | Organizations | Properties | Owed |
|---|---|---|---|
| Name matches and ZIP or city matches | 5,055 | 9,963 | $14,223,357 |
| of which 501(c)(3) | 4,359 | | $12,124,971 |
| of which no claim pending | | 8,979 | $11,485,697 |
| Payment processors as holder (PayPal, Stripe, Block) | 1,001 | 1,026 | $1,291,494 |

`data/nonprofits_confirmed_matches.csv` has one row per organization: EIN, IRS name and city, amount, number of properties, the holders, and the state property IDs. Anyone can look up an ID at https://claimit.ca.gov/app/claim-search (leave the name blank, put the ID in the Property ID box). Claiming is free and goes through the Controller.

## How it matches

Names are uppercased, `&` becomes `AND`, punctuation is dropped, and `INC`, `CORP`, `LLC`, `LTD`, `CO`, `THE`, `A` are removed. A property counts only when its owner name equals an IRS organization name **and** the ZIP matches (tier A) or the city matches (tier B). Nothing fuzzy.

The script also computes a tier C (name only, name unique among California nonprofits, three or more words) and a keyword scan for school districts, cities and counties. Those are lead lists and are not in the published file or the table above.

## Read this before quoting a number

- **It undercounts.** Exact names only. Variant spellings and abbreviations are missed. CBS News California found at least $95,000 owed to food banks by keyword search in March 2026; this method finds about $12,600 for organizations with "food bank" or "food pantry" in their IRS name.
- **Not everything in the IRS file is a charity.** It includes credit unions, health plans and trade associations. El Camino Hospital alone is $1.57M. The 501(c)(3) row is the cleaner figure and still includes large hospitals and universities.
- **A match is a lead, not a title.** Some properties list several owners. A pending claim means someone filed, not who.
- **Spot check.** I looked up three property IDs on the state's site on 2026-11-10 and all three matched the file: 1034194536 and 1025048383 (Yolo Food Bank, $2,000.00 and $555.32) and 1046558277 (United Pompe Foundation, PayPal, $35,530.53). The Yolo Food Bank balance is in line with the figure CBS reported in March. Nothing else has been checked live.
- **Snapshot.** Files change weekly.
- **Under $100 and securities** were not scanned.

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
