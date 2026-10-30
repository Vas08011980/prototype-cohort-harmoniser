# Invisible room update – 23 Oct 2026

What changed
- `app/gchn_data.json`: the built-in shading series (`itu.net`, `itu.bb`, `itu.mob`) now come from the ITU DataHub directly (2000–2025) instead of the World Bank WDI copy (2000–2024). Only three values differed by >0.5 (AUS 2024 broadband and mobile, GBR 2024 mobile: ITU revisions).
- `app/gchn_data.json` → `context`: 31 country-year indicators merged with `scripts/add_context.py`:
  - Access (ITU): internet users, households online, fixed broadband /100, mobile /100, active mobile broadband /100; teen smartphone access (Pew, USA); 12–14 mobile ownership (ABS, AUS).
  - Participation: ITU social networking (all ages); Eurostat youth 16–24 social networking, daily use, games/films/music (GBR to 2020, GRC, IRL, NOR); KOR youth smartphone overdependence (MSIT, 2015–2024); USA YRBS screen 3h+/TV 3h+ (2003–2019) and Pew "online almost constantly"; AUS ABS child internet use (2006–2012).
  - Attention: Google Trends topics Facebook, Instagram, YouTube, TikTok, Video games (single-topic scale, yearly means 2004–2025); NZ On Air YouTube daily reach (2020).
  - Platform environment: Statcounter mobile share and Facebook/Instagram referral share (2009–2025); Pew teen platform use (USA).
  - Information environment: not loaded (GDELT pull did not complete).
- `app/index.html`: footer and the five-dimension panel updated; mobile shading max raised to 200.
- `data/context/*.csv`: the template-format files behind the merge; `data/context/raw/` holds the Trends and Statcounter yearly extracts; `scripts/build_context_csvs.py` regenerates the CSVs.

Provenance: every series, with source notes, URLs and READMEs, is archived in Google Drive → Data Dictionaries → "Invisible room – digital context data" (folders 1–6).

Cautions
- All are country-year opportunity indicators, not individual exposure; age frames differ by country.
- KOR overdependence is an outcome-like prevalence – do not use it as a predictor of the same construct in KCYPS/PSKC.
- Flags to verify: KOR 2019 value is derived; YRBS 2015–2019 year alignment; Google Trends 2017 video-game dip; Statcounter KOR artefacts; Snapchat Trends topic dropped.
