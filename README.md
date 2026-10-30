# Prototype Cohort Harmoniser

This is a prototype cross-cohort harmoniser led by A/Prof Vasileios Stavropoulos (RMIT University).

> **Metadata only — no data.** The harmoniser works only with study metadata: data dictionaries, item wording, instruments, informants, waves, ages and fieldwork years, plus public country-level digital-context indicators. It holds no participant records, no individual responses and no restricted geography, and it gives no access to any cohort's data. Data access stays with each study's custodian, through their own application process.

## Aim

The key aim is to align, before any data are requested, what major longitudinal cohort and panel studies across eight countries measured on youth wellbeing, digital media use and the proximate (family and parenting) context — which items, at what ages, in which calendar years and from which informant — and to place every wave against the digital environment of its time. This shows researchers which cross-cohort comparisons are feasible and how to design analyses that separate developmental age from digital era (the "two clocks"), so that we can ask how growing up in different digital environments relates to wellbeing and adaptation from childhood into early adulthood.

> **Disclaimer.** This is a prototype. It requires further improvement and independent checking, and it is not a validated resource.

**Status:** working prototype, 30 October 2026.

- Construct assignments come from a keyword screen. They are candidates, not validated mappings.
- No psychometric equivalence has been tested.
- The digital-context values (the "invisible room": the digital space young people grow up in, which cohort studies leave largely unmeasured) describe each country and year, and for Australia also state, remoteness and subgroup. They show what young people could be exposed to at the time, not what any individual actually did online.

## Use it online

**Interactive page:** https://vas08011980.github.io/prototype-cohort-harmoniser/app/

The page runs in any modern desktop browser; nothing is installed and nothing you do is stored. It loads about 2 MB, so give it a few seconds.

How to use it:

1. **Atlas** – start here. Rows are constructs, columns are studies. Each cell shows how many candidate items a study has for that construct and who answered (Y youth, P parent, T teacher, A adult, S passive sensing…). Click a cell to read the items.
2. **Item compare** – pick a construct and up to three studies to read the wording side by side. Check the informant, reference period and response scale before treating two items as equivalent.
3. **Two clocks** – every wave placed by calendar year (horizontal) and age (vertical). Choose a construct, then shade the bands by a digital-context indicator. Follow a horizontal line to compare the same age in different digital eras.
4. **Invisible room** – choose an age to see the digital context each study's young people were in when they reached it, with the regulation and platform-launch timeline (and the ADII for Australia).
5. **Harmonisation planner** – choose a construct and the studies to compare; the planner suggests a measurement option (0, a–e) and a timing strategy, with an untested R template.
6. **Sources & gaps** – the dictionary behind each study and what is still missing.

Treat every mapping as a candidate: check items against each study's own documentation before using them in an analysis or paper.

## What it does

The app (`app/index.html`) has six views:

- **Atlas:** 11 constructs × 12 studies, with candidate item counts and informants.
- **Item compare:** items from up to three studies, side by side. Items from the Australian cohorts show the Australian Digital Inclusion Index (ADII) for their fieldwork years.
- **Two clocks:** every wave placed by calendar year and by participant age, with three overlays:
  - shading by any context indicator (including ADII for Australia);
  - red triangles for dated youth-online regulation;
  - teal dots for platform and smartphone launches.
- **Invisible room:** the digital context in each country at a chosen age, across five dimensions. Shown with each country:
  - the youth-relevant rules in force at the time;
  - a dated, sourced regulation and launch table;
  - for Australia, an ADII panel (national, state, capital vs rest of state, remoteness and subgroups).
- **Harmonisation planner:** Table 2 options 0 and a–e, plus the five timing strategies, with an untested R template.
- **Sources & gaps:** the data dictionary behind each study, what is missing, and the shared instruments that have been verified.

There are three domains: Wellbeing, Digital media use, and Proximate context (family / parenting).

**Studies (12):** ABCD, LSAC, AStRA, MCS, TESS, Growing Up in Ireland, Growing Up in New Zealand, KCYPS 2018, PSKC, Ten to Men, Understanding Society, HILDA.

**Out of scope for this harmoniser:** LSIC, Generation R, HBCD, NCDS, BCS70, Next Steps.

**Context countries (8):** USA, AUS, GBR, IRL, NZL, NOR, GRC, KOR.

## Run it

The page loads `gchn_data.json` with `fetch`, so open it through a local web server rather than as a file:

```
cd app && python3 -m http.server 8000 # then open http://localhost:8000
```

## Repository layout

| Path | Content |
|---|---|
| `app/index.html` | Single-page app (vanilla JS and SVG, Google Fonts). |
| `app/gchn_data.json` | Aggregated lexicon, atlas, timeline points, ITU series, context indicators (`context`), the ADII block (`adii`), dated events (`events`) and verified anchors. |
| `data/lexicon_candidates.csv` | Every candidate row: study, cohort, wave, years, age, informant, variable, text, instrument, construct, source file. |
| `data/lexicon_lookup.csv` | Expands the short `source` (S01…) and `timing` (T01…) keys in `lexicon_candidates.csv`; read it with `scripts/lexio.py` (`read_lex()`). |
| `data/abcd_item_event_logic.csv` | ABCD 7.0 items whose REDCap branching logic restricts the events they are asked at (1,124 items); used for item-level ABCD waves. |
| `data/pskc_variable_labels.csv` | Korean variable labels of the 16 PSKC SPSS files (metadata only). |
| `data/korean_construct_terms.csv` | Korean term lexicon used to find the Atlas constructs in PSKC and KCYPS (for review by a Korean speaker). |
| `data/removed_false_positives.csv` | Keyword-screen rows removed by rule after hand checking (29 Oct 2026), kept for audit. |
| `data/context/*.csv` | Digital-context indicators ready for the app, one file per source (`adii_australia.csv` added 29 Oct 2026). |
| `data/context/raw/` | Raw source extracts (Google Trends, Statcounter, ITU extras, Eurostat mobile, GDELT counts) that `build_context_csvs.py` reads. |
| `data/events/regulation_timeline.csv` | Youth-online laws, regulator milestones and school phone policies. Each row has a date, its precision, the countries it applies to, its status and a source URL. |
| `data/events/platform_launches.csv` | National and global platform and smartphone launches, each with a source URL. |
| `data/itu_wdi_2000_2024.json` | Legacy World Bank WDI extract, kept for provenance and superseded by the ITU-direct series. |
| `data/AStRA_*.xlsx`, `data/astra_dictionary_rows.csv` | AStRA dictionary rebuilt from the three SPSS output files (4,570 variables). |
| `docs/INVISIBLE_ROOM_2026-10-23.md` | Notes on the invisible-room data: sources, decisions and gaps. |
| `docs/UPDATE_2026-10-29.md` | What changed on 29 Oct 2026 and what is still open. |
| `scripts/` | Build pipeline (Python 3, pandas, openpyxl, python-docx), plus `gdelt_bigquery.sql`. |

**Lexicon build order:** `itu_values.py` → `build_curated.py` → `build_lexicon.py` → `build_data.py` (→ `build_astra_xlsx.py`) → `load_guinz_lsac_full.py` → `korean_constructs.py` → `update_tess_ukhls_adii.py`. Set `GCHN_WORKDIR` to a folder containing two subfolders:

- `raw/`: the source dictionaries (not in this repo);
- `astra/`: PSPP CSV exports.

`load_guinz_lsac_full.py` (29 Oct 2026) replaces the GUiNZ crosswalk and the LSAC Wave-1 extract with the full dictionaries. `update_tess_ukhls_adii.py` (29 Oct 2026) replaces the TESS and Understanding Society rows from the revised dictionaries, removes hand-checked keyword false positives, adds the ADII block and `data/context/adii_australia.csv`, and rebuilds the atlas, items and timeline. Its raw inputs are listed in the script header.

**Context build order:** `build_context_csvs.py` → `add_context.py` → `add_events.py`. Run them from the repository root.

## The invisible room: digital context included

The country-year values cover 2000–2025 where sources allow. Gaps stay empty and nothing is interpolated.

| Dimension | Included sources | Coverage |
|---|---|---|
| Access | **ITU DataHub (direct API):** internet use, fixed and mobile broadband, mobile subscriptions, 4G/LTE and 5G coverage, mobile-data affordability | 2000–2025 |
| Access | **Australian Digital Inclusion Index (ADII):** total, Access, Affordability (and Digital Ability under Participation). Legacy Roy Morgan series (national, state, capital vs rest of state, subgroups incl. age 14–24) and AIUS series (national; 2024 by state, remoteness, First Nations, age band, household type). The two series are kept separate. | 2014–2024 (AUS) |
| Participation | **Eurostat** youth aged 16–24: internet activities and mobile internet (GRC, IRL, NOR; GBR to 2020) | 2002–2025 |
| Participation | **National youth series:** KOR MSIT smartphone overdependence (ages 10–19); USA CDC YRBS and Pew Teens; AUS ABS child internet use; NZL NZ On Air | varies |
| Attention | **Google Trends**, platform topics: Facebook, Instagram, YouTube, TikTok, Snapchat, video game | 2004–2025 |
| Attention | **Google Trends**, issue topics: ChatGPT, cyberbullying, screen time | 2004–2025 |
| Attention | **Google Trends**, cross-country series on one shared scale | 2004–2025 |
| Platform environment | **Statcounter:** social-media referral share (Facebook, Instagram, etc.) and device share (desktop, mobile, tablet) | 2009–2025 |
| Platform environment | **Platform and smartphone launch dates**, national where verified, otherwise global | dated events |
| Information environment | **Regulation timeline:** 43 dated, sourced events across the 8 countries and the EU (e.g. COPPA, the Korean shutdown law, UK Online Safety Act, EU DSA, Australia's under-16 minimum age) | 2000–2026 |
| Information environment | **GDELT news attention**, 6 topics: youth + social media, screen time, cyberbullying, online safety, generative AI (from 2022), gaming disorder. Values are matching articles per 100,000 articles from national outlets. | 2017–2025 |

How the main sources were collected:

- **Google Trends** values are yearly means of monthly interest (0–100), retrieved from trends.google.com.
  - The single-topic series are each scaled within their own country, so compare change over time within a country.
  - The cross-country series share one scale. They are the only Trends values to use for comparing countries.
- **GDELT** was pulled from the GDELT 2.0 Global Knowledge Graph in Google BigQuery; `scripts/gdelt_bigquery.sql` is the exact query.
  - Each news site is assigned to a country using GDELT's domains-by-country list.
  - Topics are matched on the decoded headline plus the URL, using English, Greek, Korean and Norwegian keywords.
  - Raw counts are kept in `data/context/raw/gdelt_bq_counts_2017_2025.csv`.
- **ITU** values come directly from the ITU DataHub API (retrieved 23 Oct 2026). They replace the earlier World Bank transcription.
- **ADII** values come from the reports, 2020 webtables and 2024 dashboard exports saved in the Data Dictionaries folder ("Australian Digital Inclusion Index", with `00_ADII_Harmoniser_Dictionary.xlsx`), retrieved 27 Oct 2026. Join to cohort records by data year × state × capital/rest of state × remoteness; the AIUS series surveys adults 18+ only, so for children ADII is the household and parental digital environment.

### Adding more context data

1. Save each source as a CSV in `data/context/` with the columns `iso3, year, indicator_id, value, unit, dimension, label, source, retrieved`, one row per country-year. `data/context/TEMPLATE_google_trends.csv.example` shows the format.
2. Set `dimension` to one of: Access, Participation, Attention, Platform environment, Information environment.
3. Aggregate monthly series to yearly means first. Leave `value` empty where nothing is published; never interpolate.
4. Run `python scripts/add_context.py` from the repository root. It checks the rows, merges them into `app/gchn_data.json` and lists any rows it skipped.
5. For dated events, add rows to `data/events/*.csv`; every row needs a `source_url`. Then run `python scripts/add_events.py`.
6. Reload the app. Each indicator appears in two places:
   - the Shading menu on Two clocks;
   - its dimension in Invisible room.

## Sources and provenance

Each lexicon row keeps its source file. The source dictionaries are in the team's "Data Dictionaries" Google Drive folder, which is not public. The invisible-room source files are in a subfolder of it, "Invisible room – digital context data", which has one subfolder per source and a README in each.

| Study | Status | Source |
|---|---|---|
| ABCD | full | ABCD_7.0_dictionary_with_waves.xlsx |
| MCS | full | MCS_Full_Data_Dictionary_Harmoniser_2026-10-13.xlsx |
| GUI | full | GUI_All_Cohorts_Overview_and_Alignment.xlsx |
| KCYPS 2018 | full | KCYPS 2018 – Variable Dictionary (English, W1–W7) |
| HILDA | full | HILDA_R24_Data_Dictionary.xlsx |
| Ten to Men | full | Ten to Men 2025 Release Data Dictionary.xlsx |
| AStRA | full (rebuilt) | AStRA1/2/3-data-dictionary.spv |
| Understanding Society | full, targeted to the 11 constructs (1,433 item × construct rows, 958 stems) | UKHLS_Targeted_Harmoniser_Dictionary_2026-10-27.xlsx |
| TESS | instrument level, waves aligned (150 rows × 11 columns; 683 of 1,490 time-point cells filled) | TESS instruments T1-T10_CleanVersion.docx (revised 27 Oct 2026) |
| LSAC | full (77,039 variable × wave rows, B and K cohorts, W1–W10) | LSAC-Data-Dictionary-Release-10.1.xlsx |
| GUiNZ | full (43 tabs, 16,035 variables, antenatal → 15y) | DataDictionary_All_v1.03.xlsx |
| PSKC | full, item level from Korean labels (W1–W16) | PSKC SPSS files W1–W16 |

## Known issues

**Lexicon**

- ABCD waves come from the public ABCD 7.0 data dictionary: item-level where it gives REDCap branching logic (1,124 items), otherwise table-level coverage, which over-states waves for items added later (e.g. youth phone-involvement items).
- Some timings are approximate. Cohort years for GUiNZ, ABCD and UKHLS are derived from the study design or birth window; TESS years assume biennial visits from T1 in 2007–08. AStRA ages: C1/C2 M age 12.6 at W1 (Motti-Stefanidi et al., 2017), annual waves; C3 Gymnasium grades 1–3 at W1.
- The keyword screen produces both false positives and false negatives. Every mapping needs reviewer approval before it reaches the Masterfile.
- LSAC and GUiNZ are loaded from their full dictionaries; GUiNZ fieldwork years are approximate windows from the birth cohort and scheduled collection ages.
- TESS: item-level wording needs the TESS codebook. Retrospective objective app-use records matched per wave are entered on the study lead's confirmation; their coverage window still needs confirming with TESS.
- Understanding Society: adult items were screened by keyword only, so rarely worded adult items may be missing. BHPS waves before 2000 are listed but not plotted on Two clocks.

**Invisible room**

- Context indicators measure exposure *opportunity*. Linking them to cohort waves needs an age–period–cohort design that accounts for the confounding between them.
- Google Trends has known artefacts:
  - its search share differs by country (Naver dominates in Korea), so KOR levels are understated;
  - the video-game topic dips for one year in 2017 in every country;
  - Snapchat values are unreliable.
- Statcounter misses TikTok, Snapchat, Naver and Kakao, and its KOR values for 2018–19 and 2024–25 look like artefacts.
- Korean smartphone overdependence measures an outcome in the population, not an exposure.
- The ITU 4G/LTE values for AUS 2023–24 are excluded as a suspected entry error.
- GDELT needs three cautions:
  - the Greek, Korean and Norwegian keywords still need checking by native speakers;
  - KOR and NOR counts are small, so their year-to-year swings are noisy;
  - compare trends within a country, not levels across countries.
- ADII: never splice the legacy (2014–2020) and AIUS (2020–2024) series; the 2024 Affordability measure was redesigned, so 2024 totals are not comparable with earlier totals.
- Some regulation dates are verified only to month or year (Norway Personal Data Act; publication of Greek Law 4624/2019). YouTube local launch dates for NOR and GRC are still missing.
- Still to add:
  - a youth time series for NZL;
  - AUS youth series after 2012;
  - ADII 2021 and 2022 state and remoteness values, and LGA small-area estimates;
  - sub-national regulation beyond the examples listed.

## Governance

Metadata only: no participant records, no individual responses, no frequencies and no restricted geography. The repository contains verbatim item wording and the AStRA dictionary. Context sources are public. Respect each provider's terms (ITU, Eurostat, Google Trends, Statcounter, GDELT, ADII under CC BY-NC-SA 4.0) when redistributing.

## Credits

- Vasileios Stavropoulos (RMIT University) – lead.
- Spyridon Kavvadias and Yifei Hao (RMIT University) – helped build the harmoniser.
- Maria Prokofieva (Victoria University) – the inspiration for this work.
- Mark Griffiths and Daria Kuss (Nottingham Trent University), Frosso Motti-Stefanidi (National and Kapodistrian University of Athens), Michelle Colder Carras, Nafsika Antoniadou (University of Ioannina), Karen Waldie (University of Auckland) and Young Yim Doh (KAIST) – reviewed the datasets from their countries and the datasets they have worked on.

Prototype assembled with Claude (Anthropic).
