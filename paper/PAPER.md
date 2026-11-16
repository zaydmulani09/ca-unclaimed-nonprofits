# Money the State Is Holding: Linking California's Unclaimed Property Records to Registered Nonprofits

**Zayd Mulani**
Independent researcher
16 November 2026 (working draft)

## Abstract

California's State Controller holds unclaimed property on behalf of its owners and publishes the full public database, with owner names, addresses and balances, as bulk files. Owners must find and claim their property themselves. Journalists have reported that California does not notify nonprofits of property held in their names, but the only published estimates come from keyword searches in a few sectors. I link every open record of $100 or more (13.3 million properties, $11.4 billion; file dated 4 November 2026) to the IRS list of tax-exempt organizations in California, using normalized exact names and agreement on ZIP code or city. The conservative match identifies 5,055 organizations owed $14.2 million across 9,963 properties, of which $11.5 million has no claim pending. The median organization is owed $437, but amounts are concentrated: 84 organizations hold 52% of the matched total. About $1.3 million is payments that PayPal, Stripe and Block could not deliver and turned over to the state. I then test the method against two things. A hand-audited sample of 150 matches shows that 48% agree with the IRS street address or PO box, and that a further 2.7% have generic names I cannot vouch for; the remaining matches have distinctive names in the same city or ZIP, but are not independently verified. A recall check against three sectors reported by CBS News shows the exact-name method recovers only 1% to 17% of the dollars held under names that contain "food bank," "Make-A-Wish" or "children's hospital," because the state stores abbreviated, truncated and chapter-level names that differ from legal IRS names. Keyword totals from the state file nonetheless agree with the earlier press figures for food banks and Make-A-Wish. The $14.2 million is therefore a floor of unknown tightness. I release the code and the confirmed matches.

## 1. Introduction

When a company cannot deliver a payment to its owner for a statutory dormancy period, it must hand the money to the state, which holds it indefinitely for the owner. In California this regime is the Unclaimed Property Law (Cal. Code Civ. Proc. § 1500 et seq.), administered by the State Controller. State law requires notice to the owner's address on file for holdings of $50 or more (Watts, 2026), but once the property is reported, return depends on the owner searching the database and filing a claim.

Organizations are poorly placed to do this. Their finance staff turn over, their addresses change, and the payments that end up with the state are often small and odd: a vendor refund, an unredeemed check, a donation processor's undeliverable payout. In March 2026, CBS News California reported, from a keyword analysis of the state database, that the state owed at least $95,000 to California food banks, at least $1.3 million to children's hospitals and more than $46,000 to the Make-A-Wish Foundation, and the Yolo County Food Bank's director said she was surprised that the state does not automatically notify nonprofits (Watts, 2026). The Controller's office told CBS it would reach out to nonprofits, that it was evaluating its approach, and that automatic return was not yet in place (Watts, 2026). In April 2026 U.S. Senator Elizabeth Warren asked the national association of state unclaimed property administrators for state-by-state data, noting that some property is owed to nonprofits, food banks and hospitals (Warren, 2026). Other states have run targeted efforts, for example a state auditor mailing letters to nonprofits (Arkansas, over $115,000 identified; Arkansas Auditor, 2024), a pilot using Secretary of State addresses (Vermont, designed to return over $150,000 to more than 250 nonprofits; Mountain Times, 2024), a treasurer's return to a single federation (Pennsylvania, over $160,000; Pennsylvania Treasury, 2024) and recovery of misdirected donations for one food pantry (North Carolina, about $13,000; North Carolina Treasurer, 2025). I did not find a published census of how much of a state's database belongs to its registered nonprofits.

This note asks a simple descriptive question: how much of California's unclaimed property belongs to organizations that are registered tax-exempt entities in California, and how reliably can that be established from public data alone? The contribution is a reproducible linkage, an estimate that I treat explicitly as a lower bound, and a measurement of how far below the truth that bound is likely to sit.

## 2. Data

**State file.** The State Controller's office publishes the unclaimed property database as zipped CSV files split by reported value, refreshed weekly (California State Controller's Office, 2026). I used the "$100 to $499.99" and "$500 and up" files, both last modified 4 November 2026 and retrieved 10 November 2026. Together they contain 14,808,647 owner rows for 13,338,152 distinct properties with a combined current cash balance of $11.41 billion. The two lower-value files were not used. A property can list several owners as separate rows. Fields used: property ID, owner name and address, current cash balance, holder name, property type, and counts of pending and paid claims. Owner names are free text, often truncated, abbreviated or upper-cased.

**IRS file.** The IRS Exempt Organizations Business Master File, California extract, lists every exempt organization with an address in the state, with EIN, legal name, address, subsection of the tax code and, where filed, revenue (IRS, 2026). I retrieved it on 10 November 2026 (file modified 9 November 2026).

## 3. Method

Names in both files are uppercased, "&" is replaced by "AND," punctuation is removed, and the tokens INC, INCORPORATED, CORP, CORPORATION, THE, CO, LLC, LTD and A are dropped. A property is linked to an organization when the owner name equals the IRS name and one of the following holds:

- **Tier A:** the owner ZIP5 equals the IRS ZIP5.
- **Tier B:** not tier A, but the owner city equals the IRS city.

A third tier (C) accepts name equality alone when the name has at least three words, is unique among California exempt organizations, and the owner address is in California. Because place does not agree in tier C, I treat it as a lead list and exclude it from all headline figures. I also tested a relaxed tier D that allows abbreviation expansion and truncation (Section 5.3).

No fuzzy matching is used in A and B. The aim is that nearly every reported match is the right organization, at the cost of missing many.

## 4. Results

**Table 1. Linked organizations (state file of 4 November 2026).**

| | Organizations | Properties | Amount |
|---|---|---|---|
| Tier A (name, ZIP) | | 6,484 | $9,497,677 |
| Tier B (name, city) | | 3,479 | $4,725,680 |
| **Tiers A and B** | **5,055** | **9,963** | **$14,223,357** |
| of which 501(c)(3) | 4,359 | | $12,124,971 |
| of which no claim pending | | 8,979 | $11,485,697 |
| Name-only (tier C), not in headline | | 5,700 | $6,922,320 |

**Scale and concentration.** The median linked organization is owed $437 and the mean is $2,814. 3,562 organizations are owed under $1,000 (total $1.2 million), while 84 organizations are owed $25,000 or more and together hold $7.4 million, 52% of the total. The ten largest hold $3.7 million and the largest hundred $7.7 million. The IRS list includes hospitals, universities, credit unions and health plans, so the largest balances are not small charities: one hospital alone accounts for $1.6 million.

**Undelivered payments.** Of the linked properties, 1,026 across 1,001 organizations were reported by a payment processor: PayPal ($1,122,237), Stripe ($167,983) or Block ($1,273), $1,291,494 in all. These are concentrated among small organizations. One example is a Fresno rare-disease charity whose annual revenue on the IRS file is about $41,000 and which has $35,531 from PayPal held by the state.

**Claims in progress.** The state file records pending and paid claim counts per property. 984 of the 9,963 linked properties ($2.7 million) have at least one pending claim; the rest have none.

**Live check.** On 10 November 2026 I searched three linked property IDs on the state's public claim-search site; all three were returned with the same owner, holder and amount as in the bulk file (two properties of Yolo Food Bank, $2,000.00 and $555.32, and one of United Pompe Foundation, $35,530.53).

## 5. Validation

### 5.1 Precision

I drew a random sample of 150 tier A and B properties (seed 7) and compared each owner address with the IRS address for the same EIN. A match on street number, or on PO Box number, counts as address agreement.

- 72 of 150 (48%) agree on address. By tier: 70 of 117 (60%) in tier A, but 2 of 33 (6%) in tier B.
- I read all 150 name pairs. Four of the 78 non-agreeing rows have names generic enough that a different organization could plausibly share them and a same-city coincidence is possible (four, or 2.7% of the sample). The other 74 pair distinctive names with the same city or ZIP and an address that differs, usually a PO Box against a street address; I judge these likely to be the same organization but I have not verified them independently.
- Eight rows (5%) are organizations that the IRS file lists but that an ordinary reader would not call charities: credit unions, health plans, one utility and a country club.

This gives a bracket for the share of matches that are the same organization of about 48% (address-confirmed only) to 97% (everything except generic unconfirmed names). My reading is nearer the upper end, but that is judgment and not a measurement. Tier B is clearly weaker than tier A, and it contributes $4.7 million of the $14.2 million. A tighter estimate needs verification of the non-agreeing matches against external sources such as organization websites or filings.

### 5.2 Recall

To measure how much the exact method misses, I scanned all 14.8 million state rows for owner names containing the strings used by the CBS analysis and counted every property regardless of IRS linkage.

**Table 2. Dollars held under category names versus dollars linked.** (California owner address; "any address" in parentheses.)

| Category (name contains) | Properties | Held ($) | Linked ($) | Recall by $ |
|---|---|---|---|---|
| Food bank / food pantry | 53 (84) | 67,852 (93,609) | 11,240 | 17% (12%) |
| Make-A-Wish | 26 (49) | 34,357 (47,166) | 485 | 1% (1%) |
| Children's hospital | 323 (389) | 519,512 (605,596) | 39,323 | 8% (6%) |

Two points follow. First, a keyword scan of the state file, with no linking, comes close to the earlier press figures for two of the three categories: $93,609 for food banks against "at least $95,000" and $47,166 for Make-A-Wish against "more than $46,000" (Watts, 2026). The children's hospital total I find ($606,000) is below the press figure of $1.3 million; this may reflect that I excluded properties under $100 and did not search securities, but I have not tested that. Second, exact-name linkage recovers very little of that money. Inspecting the misses shows why: the state holds money under "ALAMEDA CO FOOD BANK" where the IRS lists a longer legal name, under "RADY CHILDRENS HOSPITAL HOMECARE" and "CHILDRENS HOSPITAL OAKLAND," and under a different Make-A-Wish chapter name from each holder. Chapters and affiliates with parent-and-child naming are the hard case.

These three categories are not a random draw, so I cannot extrapolate their recall to all organizations. They do show that the headline figure can be low by a factor of several in sectors with chapter structures, abbreviations and hospital systems.

### 5.3 A relaxed tier

I tested a relaxed match that expands common abbreviations and accepts an owner name that is a token prefix of an IRS name, requires the same ZIP5, requires a unique candidate EIN in that ZIP, and excludes properties already linked. It produced 3,304 properties ($3.6 million). Reading a sample showed that most prefix matches were false: a parent entity matched to its own foundation or auxiliary (a county hospital and its hospital foundation; a school district and its education foundation; a court and the judges' association), which are different legal entities. I therefore kept only two kinds: names that are equal after abbreviation expansion (269 properties, $216,857; a 20-row read found no errors) and prefix matches where the owner name visibly ends on a connective such as "OF" or "AND," indicating truncation (69 properties, $74,945). Together these add 338 properties, $291,801 and 197 organizations. This is small relative to the gap in Table 2, which indicates that the missing money needs a real fuzzy matcher with human review. I do not include tier D in the headline.

## 6. Limitations

1. **Floor, not estimate.** Exact names miss variants. Recall by dollars in three sectors was 1% to 17%. Overall recall is unknown.
2. **Precision is bracketed, not measured.** Between 48% and 97% of A and B matches are the same organization by the checks above; tier B is weaker than tier A.
3. **Scope of "nonprofit".** The IRS file includes credit unions, health plans, trade associations and large hospital systems. The 501(c)(3) subset is cleaner but still contains large institutions.
4. **Ownership.** Some properties list several owners, and a pending claim counter does not say whose claim it is.
5. **Snapshot.** The files change weekly. The values here are as of 4 November 2026.
6. **Excluded.** Properties under $100 and securities were not analysed. Public-sector owners (school districts, cities, counties) were identified only by name keyword and are not reported here.
7. **No outcome data.** I do not yet know whether any linked organization has claimed its property as a result of this work.

## 7. Discussion

A match this simple, using only public files, finds more than $14 million belonging to California nonprofits and shows that most of it has not been claimed. The state is likely to hold better identifiers than a public analyst has. Holder reports and other state registries (Vermont's pilot used Secretary of State addresses) could be used to link an owner to a current address without relying on name equality, and the measured recall in Section 5.2 suggests that name-based linking from the outside will always be weak where abbreviation and affiliate naming are common. The same linkage supports a policy that the Controller has already described as under development: notifying organizations by mail or email, or returning small balances automatically. The magnitude here, a few thousand dollars for most organizations but many tens of thousands for a few, suggests that a letter campaign targeted at the roughly 430 organizations owed $5,000 or more would cover three quarters of the matched dollars.

Several states have done this at smaller scale (Arkansas, Vermont, Pennsylvania, North Carolina), typically starting from state-held data. A second use is accountability: the pending and paid claim counters in the public file allow a before-and-after comparison, so the effect of any outreach on claims could be measured from the same weekly release. I have begun contacting organizations and outlets and will report claim outcomes in a later version if the data show a change.

## 8. Data and code availability

Code, the 5,055 linked organizations (with state property IDs so each can be checked at claimit.ca.gov) and the audit scripts are at https://github.com/zaydmulani09/ca-unclaimed-nonprofits (code MIT, data CC0). The underlying state and IRS files are public. The sample used in Section 5.1 is reproducible with seed 7.

## References

Arkansas Auditor of State. (2024). State Auditor Dennis Milligan finds money for Arkansas nonprofits. https://auditor.ar.gov/news-feed/state-auditor-dennis-milligan-finds-money-for-arkansas-nonprofits/

California State Controller's Office. (2026). Download unclaimed property records. https://sco.ca.gov/upd_download_property_records.html (files modified 4 November 2026; retrieved 10 November 2026).

Internal Revenue Service. (2026). Exempt Organizations Business Master File, California extract. https://www.irs.gov/pub/irs-soi/eo_ca.csv (modified 9 November 2026; retrieved 10 November 2026).

Mountain Times. (2024, March 20). State aims to reunite Vermont nonprofits with unclaimed property. https://mountaintimes.info/2024/03/20/state-aims-to-reunite-vermont-nonprofits-with-unclaimed-property

North Carolina Department of State Treasurer. (2025, October 17). Treasurer Briner returns missing money to Iredell County nonprofit food pantry. https://www.nctreasurer.gov/news/press-releases/2025/10/17/treasurer-briner-returns-missing-money-iredell-county-nonprofit-food-pantry

Pennsylvania Treasury. (2024, February 7). Treasury returns unclaimed property to United Way of Pennsylvania. https://patreasury.gov/newsroom/archive/2024/2-7-United-Way.html

Warren, E. (2026, April 15). Letter to the National Association of Unclaimed Property Administrators on state escheatment practices. U.S. Senate Committee on Banking, Housing, and Urban Affairs. https://www.banking.senate.gov/newsroom/minority/warren-seeks-data-on-states-seizing-americans-unclaimed-assets

Watts, J. (2026, March 11). California unclaimed property: State owes charities money. CBS News. https://www.cbsnews.com/news/california-unclaimed-property-state-owes-charities-money
