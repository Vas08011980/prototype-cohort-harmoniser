"""Write the invisible-room context CSVs (repo template format) into data/context/.

Values were retrieved on 23 Oct 2026 and are archived, with full source notes and READMEs, in the
Google Drive folder "Data Dictionaries / Invisible room - digital context data":
  1_ITU_Access, 2_GoogleTrends_Attention, 3_Participation, 4_Statcounter_Platform, 6_National_Youth.
This script only reshapes those archived values; it never interpolates. Then run scripts/add_context.py.
"""
import csv, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data', 'context')
RET = '2026-10-23'

# indicator_id: (label, unit, dimension, source)
META = {
 'itu_11624': ('Internet users (ITU)', '% of individuals', 'Access', 'ITU DataHub i99H (WTI); age frame varies by country'),
 'itu_12047': ('Households with internet at home (ITU)', '% of households', 'Access', 'ITU DataHub xHH6_IDI'),
 'itu_19303': ('Fixed broadband subscriptions per 100 (ITU)', 'per 100 inhabitants', 'Access', 'ITU DataHub i992b'),
 'itu_392':   ('Mobile-cellular subscriptions per 100 (ITU)', 'per 100 inhabitants', 'Access', 'ITU DataHub i911'),
 'itu_12066': ('Active mobile-broadband subscriptions per 100 (ITU)', 'per 100 inhabitants', 'Access', 'ITU DataHub i911mw'),
 'itu_37470': ('Social networking, all ages (ITU)', '% of population', 'Participation', 'ITU DataHub HHU4212asn-%_POP--'),
 'es_snet_y16_24': ('Youth 16-24 social networking (Eurostat)', '% of individuals 16-24', 'Participation', 'Eurostat isoc_ci_ac_i I_IUSNET Y16_24'),
 'es_daily_y16_24': ('Youth 16-24 daily internet use (Eurostat)', '% of individuals 16-24', 'Participation', 'Eurostat isoc_ci_ifp_fu I_IDAY Y16_24'),
 'es_games_y16_24': ('Youth 16-24 games/films/music online (Eurostat)', '% of individuals 16-24', 'Participation', 'Eurostat isoc_ci_ac_i I_IUGM Y16_24 (definition changed over time)'),
 'gt_facebook': ('Search interest: Facebook (Google Trends, own scale)', 'index 0-100 within country', 'Attention', 'Google Trends topic, monthly 2004-2025, yearly mean'),
 'gt_instagram': ('Search interest: Instagram (Google Trends, own scale)', 'index 0-100 within country', 'Attention', 'Google Trends topic'),
 'gt_youtube': ('Search interest: YouTube (Google Trends, own scale)', 'index 0-100 within country', 'Attention', 'Google Trends topic'),
 'gt_tiktok': ('Search interest: TikTok (Google Trends, own scale)', 'index 0-100 within country', 'Attention', 'Google Trends topic'),
 'gt_videogame': ('Search interest: Video games (Google Trends, own scale)', 'index 0-100 within country', 'Attention', 'Google Trends topic; 2017 dip is a Google artefact'),
 'sc_mobile': ('Mobile share of web page views (Statcounter)', '% of page views', 'Platform environment', 'Statcounter Global Stats, desktop vs mobile vs tablet'),
 'sc_facebook': ('Facebook share of social-media referrals (Statcounter)', '% of social referrals', 'Platform environment', 'Statcounter Global Stats social media'),
 'sc_instagram': ('Instagram share of social-media referrals (Statcounter)', '% of social referrals', 'Platform environment', 'Statcounter Global Stats social media'),
 'kor_youth_overdependence': ('Youth 10-19 smartphone overdependence risk (KOR, MSIT)', '% of 10-19 smartphone users', 'Participation', 'MSIT/NIA Smartphone Overdependence Survey; population prevalence, outcome-like - not an exposure'),
 'usa_yrbs_screen3h': ('High-school students using computer/games 3+ h/day (USA, YRBS)', '% of grades 9-12', 'Participation', 'CDC national YRBS trend factsheet 2003-2019'),
 'usa_yrbs_tv3h': ('High-school students watching TV 3+ h/day (USA, YRBS)', '% of grades 9-12', 'Participation', 'CDC national YRBS trend factsheet 2003-2019'),
 'usa_pew_constant': ('Teens 13-17 online almost constantly (USA, Pew)', '% of teens 13-17', 'Participation', 'Pew Research Center Teens, Social Media & Technology; 2015 = 2014-15 survey'),
 'usa_pew_smartphone': ('Teens 13-17 with smartphone access (USA, Pew)', '% of teens 13-17', 'Access', 'Pew Research Center; 2015 = 2014-15 survey'),
 'usa_pew_youtube': ('Teens 13-17 using YouTube (USA, Pew)', '% of teens 13-17', 'Platform environment', 'Pew Research Center'),
 'usa_pew_tiktok': ('Teens 13-17 using TikTok (USA, Pew)', '% of teens 13-17', 'Platform environment', 'Pew Research Center'),
 'usa_pew_instagram': ('Teens 13-17 using Instagram (USA, Pew)', '% of teens 13-17', 'Platform environment', 'Pew Research Center'),
 'usa_pew_snapchat': ('Teens 13-17 using Snapchat (USA, Pew)', '% of teens 13-17', 'Platform environment', 'Pew Research Center'),
 'usa_pew_facebook': ('Teens 13-17 using Facebook (USA, Pew)', '% of teens 13-17', 'Platform environment', 'Pew Research Center'),
 'aus_abs_child_internet': ('Children 5-14 who used the internet (AUS, ABS)', '% of children 5-14', 'Participation', 'ABS 4901.0 Children\'s Participation in Cultural and Leisure Activities'),
 'aus_abs_child_internet_12_14': ('Children 12-14 who used the internet (AUS, ABS)', '% of children 12-14', 'Participation', 'ABS 4901.0'),
 'aus_abs_child_mobile_12_14': ('Children 12-14 with a mobile phone (AUS, ABS)', '% of children 12-14', 'Access', 'ABS 4901.0'),
 'itu_19306': ('Population covered by at least LTE/4G (ITU)', '% of population', 'Access', 'ITU DataHub 19306; AUS 2023-24 values dropped (identical to 5G, suspected entry error)'),
 'itu_34236': ('Population covered by at least 5G (ITU)', '% of population', 'Access', 'ITU DataHub 34236'),
 'itu_36056': ('Affordability: 5GB mobile data basket (ITU)', '% of GNI per capita', 'Access', 'ITU ICT price baskets 36056 (2023+)'),
 'itu_33331': ('Affordability: fixed broadband 5GB basket (ITU)', '% of GNI per capita', 'Access', 'ITU ICT price baskets 33331 (2018+)'),
 'es_mobint_y16_24': ('Youth 16-24 used a mobile phone to access internet (Eurostat)', '% of individuals 16-24', 'Access', 'Eurostat isoc_ci_im_i I_IUMP Y16_24 (2011-2019)'),
 'es_mobdev_y16_24': ('Youth 16-24 used internet on a mobile/smart phone (Eurostat)', '% of individuals 16-24', 'Access', 'Eurostat isoc_ci_dev_i I_IUG_MP Y16_24 (2021+; new definition)'),
 'gt_snapchat': ('Search interest: Snapchat (Google Trends search term, own scale)', 'index 0-100 within country', 'Attention', 'Google Trends search term "snapchat"'),
 'gt_cyberbullying': ('Search interest: Cyberbullying (Google Trends, own scale)', 'index 0-100 within country', 'Attention', 'Google Trends topic'),
 'gt_chatgpt': ('Search interest: ChatGPT (Google Trends, own scale)', 'index 0-100 within country', 'Attention', 'Google Trends topic'),
 'gt_screentime': ('Search interest: Screen time (Google Trends, own scale)', 'index 0-100 within country', 'Attention', 'Google Trends topic'),
 'gtx_facebook': ('Search interest: Facebook (Google Trends, comparable across countries)', 'index, max country-month = 100', 'Attention', 'Google Trends multi-geo request, two batches linked through shared US and NZ series'),
 'gtx_instagram': ('Search interest: Instagram (Google Trends, comparable across countries)', 'index, max country-month = 100', 'Attention', 'Google Trends multi-geo request, two batches linked through shared US and NZ series'),
 'gtx_youtube': ('Search interest: YouTube (Google Trends, comparable across countries)', 'index, max country-month = 100', 'Attention', 'Google Trends multi-geo request, two batches linked through shared US and NZ series'),
 'gtx_tiktok': ('Search interest: TikTok (Google Trends, comparable across countries)', 'index, max country-month = 100', 'Attention', 'Google Trends multi-geo request, two batches linked through shared US and NZ series'),
 'gtx_snapchat': ('Search interest: Snapchat (search term) (Google Trends, comparable across countries)', 'index, max country-month = 100', 'Attention', 'Google Trends multi-geo request, two batches linked through shared US and NZ series'),
 'gtx_videogame': ('Search interest: Video games (Google Trends, comparable across countries)', 'index, max country-month = 100', 'Attention', 'Google Trends multi-geo request, two batches linked through shared US and NZ series'),
 'gtx_cyberbullying': ('Search interest: Cyberbullying (Google Trends, comparable across countries)', 'index, max country-month = 100', 'Attention', 'Google Trends multi-geo request, two batches linked through shared US and NZ series'),
 'gtx_chatgpt': ('Search interest: ChatGPT (Google Trends, comparable across countries)', 'index, max country-month = 100', 'Attention', 'Google Trends multi-geo request, two batches linked through shared US and NZ series'),
 'gtx_screentime': ('Search interest: Screen time (Google Trends, comparable across countries)', 'index, max country-month = 100', 'Attention', 'Google Trends multi-geo request, two batches linked through shared US and NZ series'),
 'gd_youth_social_media': ('News attention: social media AND youth/teens/children (GDELT)', 'matching articles per 100,000 articles from national outlets', 'Information environment', 'GDELT 2.0 GKG via BigQuery (gkg_partitioned); outlet country from GDELT domains-by-country list (May 2018); keyword match on decoded page title + URL in English, Greek, Korean, Norwegian; see scripts/gdelt_bigquery.sql'),
 'gd_screen_time': ('News attention: "screen time" (GDELT)', 'matching articles per 100,000 articles from national outlets', 'Information environment', 'GDELT 2.0 GKG via BigQuery (gkg_partitioned); outlet country from GDELT domains-by-country list (May 2018); keyword match on decoded page title + URL in English, Greek, Korean, Norwegian; see scripts/gdelt_bigquery.sql'),
 'gd_cyberbullying': ('News attention: cyberbullying (GDELT)', 'matching articles per 100,000 articles from national outlets', 'Information environment', 'GDELT 2.0 GKG via BigQuery (gkg_partitioned); outlet country from GDELT domains-by-country list (May 2018); keyword match on decoded page title + URL in English, Greek, Korean, Norwegian; see scripts/gdelt_bigquery.sql'),
 'gd_online_safety': ('News attention: "online safety" (GDELT)', 'matching articles per 100,000 articles from national outlets', 'Information environment', 'GDELT 2.0 GKG via BigQuery (gkg_partitioned); outlet country from GDELT domains-by-country list (May 2018); keyword match on decoded page title + URL in English, Greek, Korean, Norwegian; see scripts/gdelt_bigquery.sql'),
 'gd_generative_ai': ('News attention: ChatGPT OR generative AI (GDELT)', 'matching articles per 100,000 articles from national outlets', 'Information environment', 'GDELT 2.0 GKG via BigQuery (gkg_partitioned); outlet country from GDELT domains-by-country list (May 2018); keyword match on decoded page title + URL in English, Greek, Korean, Norwegian; see scripts/gdelt_bigquery.sql'),
 'gd_gaming_addiction': ('News attention: gaming disorder / video game addiction (GDELT)', 'matching articles per 100,000 articles from national outlets', 'Information environment', 'GDELT 2.0 GKG via BigQuery (gkg_partitioned); outlet country from GDELT domains-by-country list (May 2018); keyword match on decoded page title + URL in English, Greek, Korean, Norwegian; see scripts/gdelt_bigquery.sql'),
 'nzl_nzonair_child_youtube': ('Children under 14 using YouTube daily (NZL, NZ On Air)', '% daily reach, children', 'Attention', 'NZ On Air / BSA Children\'s Media Use 2020 (single year)'),
}

# 'ISO indicator: year=value ...'
DATA = """
AUS itu_11624: 2000=46.756 2001=52.689 2005=63 2006=66 2007=69.45 2008=71.67 2009=74.25 2010=76 2011=79.488 2012=79 2013=83.453 2014=84 2015=84.561 2016=86.54 2017=86.545 2018=90.008 2019=93.61 2020=94.693 2021=96.972 2022=96.119 2023=96.116 2024=96.131
GBR itu_11624: 2000=26.822 2001=33.481 2002=56.48 2003=64.82 2004=65.61 2005=70 2006=68.82 2007=75.09 2008=78.39 2009=83.56 2010=85 2011=85.38 2012=87.48 2013=89.844 2014=91.613 2015=92 2016=94.776 2017=90.425 2018=90.692 2019=92.517 2020=94.818 2021=96.197 2022=95.465 2023=95.447 2024=95.472
GRC itu_11624: 2000=9.139 2001=10.935 2002=14.67 2003=17.8 2004=21.42 2005=24 2006=32.25 2007=35.88 2008=38.2 2009=42.4 2010=44.4 2011=51.65 2012=55.07 2013=59.866 2014=63.207 2015=66.835 2016=69.088 2017=69.893 2018=72.238 2019=75.671 2020=78.116 2021=78.494 2022=83.171 2023=85.01 2024=86.27 2025=89.153
IRL itu_11624: 2000=17.85 2001=23.139 2002=25.85 2003=34.31 2004=36.99 2005=41.61 2006=54.82 2007=61.158 2008=65.34 2009=67.38 2010=69.85 2011=74.89 2012=76.92 2013=78.248 2014=83.492 2015=83.495 2016=83.5 2017=84.114 2018=87 2019=87 2020=92 2021=93.506 2022=95.037 2023=96.866 2024=97.188
KOR itu_11624: 2000=44.7 2001=56.6 2002=59.4 2003=65.5 2004=72.7 2005=73.5 2006=78.1 2007=78.8 2008=81 2009=81.6 2010=83.7 2011=83.759 2012=84.07 2013=84.77 2014=87.557 2015=89.896 2016=92.843 2017=95.069 2018=96.023 2019=96.158 2020=96.505 2021=97.571 2022=97.169 2023=97.416 2024=97.896 2025=96.092
NOR itu_11624: 2000=52 2001=64 2002=72.84 2003=78.13 2004=77.69 2005=81.99 2006=82.55 2007=86.93 2008=90.57 2009=92.08 2010=93.39 2011=93.49 2012=94.65 2013=95.053 2014=96.301 2015=96.81 2016=97.298 2017=96.358 2018=96.492 2019=98 2020=94.608 2021=99 2022=99 2023=99 2024=99
NZL itu_11624: 2000=47.38 2001=53.241 2002=59.081 2003=60.963 2004=61.848 2005=62.72 2006=69 2007=69.76 2008=72.03 2009=79.7 2010=80.46 2011=81.23 2012=81.644 2013=82.78 2014=84 2015=85.2 2016=86.5 2017=87.7 2018=89 2019=89.864 2020=90.921 2021=91.991 2022=93.073 2023=93.326 2024=93.519
USA itu_11624: 2000=43.079 2001=49.081 2002=58.785 2003=61.697 2004=64.758 2005=67.968 2006=68.931 2007=75 2008=74 2009=71 2010=71.69 2011=69.729 2012=74.7 2013=71.4 2014=73 2015=74.554 2016=85.544 2017=87.275 2018=88.499 2019=89.43 2020=90.345 2021=91.268 2022=92.729 2023=93.526 2024=94.694
AUS itu_12047: 2000=33 2001=42 2002=46 2003=53 2004=54 2005=56 2006=60 2007=63.66 2008=66.618 2009=71.77 2010=74.07 2011=78.917 2012=79 2013=82.688 2014=84.3 2015=85.887 2016=86.115 2017=86.115 2018=86.744 2019=87.378 2020=97.15 2021=97.181 2022=97.458 2023=97.767 2024=97.803
GBR itu_12047: 2000=30 2001=45 2002=49.72 2003=55.11 2004=55.899 2005=60.232 2006=62.641 2007=66.718 2008=71.143 2009=76.693 2010=79.6 2011=82.7 2012=86.8 2013=88.446 2014=89.93 2015=91.252 2017=89.632 2018=90.203 2019=92.893 2020=95.244 2021=96.281 2022=96.34 2023=96.397 2024=96.441
GRC itu_12047: 2001=9.9 2002=12.151 2003=16.301 2004=16.544 2005=21.731 2006=23.123 2007=25.397 2008=30.963 2009=38.065 2010=46.4 2011=50.17 2012=53.58 2013=56.313 2014=65.551 2015=68.091 2016=69.126 2017=70.958 2018=76.493 2019=78.54 2020=80.382 2021=85.071 2022=85.494 2023=86.901 2024=84.576 2025=88.735
IRL itu_12047: 2000=20.4 2001=34 2002=34.775 2003=35.567 2004=39.731 2005=47.184 2006=49.953 2007=57.271 2008=63.047 2009=66.67 2010=71.7 2011=78.12 2012=81.09 2013=82.389 2014=82 2015=85 2017=88.999 2018=89 2019=91 2020=92 2021=91.113 2022=94.997 2023=96.747 2024=97.067
KOR itu_12047: 2000=49.8 2001=63.2 2002=70.23 2003=78.1 2004=86 2005=92.73 2006=93.99 2007=94.13 2008=94.27 2009=95.905 2010=96.8 2011=97.232 2012=97.35 2013=98.14 2014=98.487 2015=98.794 2016=99.194 2017=99.505 2018=99.478 2019=99.689 2020=99.749 2021=99.932 2022=99.961 2023=99.966 2024=99.971 2025=99.981
NOR itu_12047: 2000=49 2001=56 2002=58 2003=60.491 2004=60.089 2005=64.006 2006=68.794 2007=77.591 2008=83.97 2009=85.564 2010=89.8 2011=92.24 2012=92.69 2013=94.285 2014=93.07 2015=97.279 2016=97 2017=97 2018=96 2019=98 2020=96.123 2021=99 2022=99 2023=99 2024=99.488
NZL itu_12047: 2001=37.4 2002=43 2003=50 2004=57 2005=62.081 2006=64.559 2007=65.9 2008=67.533 2009=75.262 2010=76.81 2011=78.39 2012=80.24 2013=76.8 2014=79.83 2015=82.75 2016=85.66 2017=87.804 2018=88.445 2019=89.091 2020=94.31 2021=95.988 2022=96.921 2023=97.295 2024=97.283
USA itu_12047: 2000=41.5 2001=50.5 2002=52 2003=54.7 2004=56.4 2005=58.1 2006=59.9 2007=61.7 2008=63.6 2009=68.685 2010=71.06 2011=71.7 2012=74.8 2013=78.58 2014=79.875 2015=81.475 2016=81.867 2017=83.847 2018=85.35 2019=86.612 2020=90.554 2021=94.352 2022=92.663 2023=94.772 2024=94.855
AUS itu_19303: 2001=0.634 2002=1.317 2003=2.608 2004=5.048 2005=9.934 2006=18.941 2008=24.871 2009=23.968 2010=24.885 2011=24.698 2012=25.096 2013=25.74 2014=27.7 2015=28.512 2016=30.308 2017=32.033 2018=33.549 2019=34.543 2020=35.347 2021=35.836 2022=36.393 2023=36.627 2024=37.84 2025=37.985
GBR itu_19303: 2000=0.09 2001=0.558 2002=2.278 2003=5.205 2004=10.178 2005=16.335 2006=21.315 2007=25.361 2008=27.907 2009=28.601 2011=32.419 2012=33.905 2013=35.782 2014=36.583 2015=37.721 2016=38.659 2017=39.249 2018=39.829 2019=40.023 2020=40.578 2021=41.113 2022=41.287 2023=41.437 2024=42.165
GRC itu_19303: 2003=0.096 2004=0.47 2005=1.458 2006=4.432 2007=9.211 2008=13.605 2009=17.254 2010=20.249 2011=22.183 2012=24.342 2013=26.562 2014=28.973 2015=31.781 2016=33.549 2017=35.135 2018=36.92 2019=38.357 2020=39.788 2021=41.921 2022=42.923 2023=43.854 2024=44.676 2025=44.589
IRL itu_19303: 2002=0.27 2003=1.047 2004=3.741 2005=7.761 2006=13.158 2007=17.269 2008=19.867 2009=21.536 2010=22.372 2011=23.381 2012=24.175 2013=25.714 2014=27.022 2015=27.846 2016=28.615 2017=29.079 2018=29.351 2019=29.645 2020=30.435 2021=31.362 2022=31.536 2023=31.891 2024=32.302 2025=33.253
KOR itu_19303: 2000=8.275 2001=16.619 2002=21.999 2003=23.527 2004=24.994 2005=25.476 2006=29.252 2007=30.533 2008=32.002 2009=33.676 2010=35.256 2011=36.353 2012=36.8 2013=37.422 2014=37.988 2015=39.276 2016=40.071 2017=41.168 2018=41.219 2019=42.037 2020=43.054 2021=44.253 2022=45.454 2023=46.568 2024=47.801 2025=48.839
NOR itu_19303: 2000=0.519 2001=1.962 2002=4.524 2003=8.736 2004=14.628 2005=21.443 2006=26.704 2007=30.946 2008=33.083 2009=34.549 2010=35.248 2011=36.053 2012=37.018 2013=37.612 2014=38.485 2015=39.51 2016=40.24 2017=41.033 2018=41.528 2019=42.272 2020=44.386 2021=44.939 2022=45.664 2023=45.438 2024=45.163 2025=46.754
NZL itu_19303: 2000=0.121 2001=0.444 2002=1.101 2003=2.063 2004=4.694 2005=7.763 2006=11.244 2007=20.198 2008=21.469 2009=23.751 2010=25.116 2011=26.878 2012=28.833 2013=29.547 2014=31.174 2015=31.445 2016=32.462 2017=32.892 2018=33.619 2019=34.023 2020=34.813 2021=35.263 2022=36.304 2023=37.853 2024=38.045 2025=38.308
USA itu_19303: 2000=2.512 2001=4.5 2002=6.925 2003=9.57 2004=12.758 2005=17.299 2006=20.165 2007=23.755 2008=25.291 2009=25.969 2010=27.172 2011=28.117 2012=29.174 2013=30 2014=30.271 2015=31.341 2016=32.114 2017=32.57 2018=33.056 2019=33.835 2020=35.716 2021=37.007 2022=37.489 2023=38.094 2024=38.857 2025=39.106
AUS itu_392: 2000=44.751 2001=57.484 2002=64.658 2003=72.388 2004=82.208 2005=90.764 2006=95.966 2007=101.458 2008=103.507 2009=101.914 2010=101.619 2011=105.824 2012=106.5 2013=107.332 2014=106.206 2015=107.608 2016=109.129 2017=107.8 2018=110.033 2019=109.753 2020=104.93 2021=105.119 2022=109.469 2023=112.513 2024=113.708 2025=112.671
GBR itu_392: 2000=73.576 2001=78.065 2002=82.679 2003=90.699 2004=99.199 2005=108.046 2006=114.786 2007=119.989 2008=120.819 2009=122.357 2010=121.781 2011=121.498 2012=122.465 2013=122.185 2014=120.958 2015=121.212 2016=119.787 2017=119.207 2018=118.184 2019=120.25 2020=117.305 2021=117.887 2022=119.834 2023=122.782 2024=122.887 2025=123.243
GRC itu_392: 2000=55.018 2001=73.445 2002=85.528 2003=81.845 2004=85.174 2005=93.435 2006=99.671 2007=111.309 2008=124.578 2009=119.689 2010=110.5 2011=109.174 2012=120.926 2013=114.143 2014=111.488 2015=116.133 2016=116.365 2017=120.306 2018=113.418 2019=110.855 2020=106.67 2021=108.644 2022=109.027 2023=110.792 2024=113.598 2025=115.739
IRL itu_392: 2000=64.719 2001=76.884 2002=76.366 2003=87.655 2004=94.932 2005=102.761 2006=109.871 2007=113.138 2008=112.531 2009=103.766 2010=103.123 2011=107.135 2012=108.99 2013=105.538 2014=105.461 2015=104.243 2016=102.558 2017=101.842 2018=102.03 2019=104.598 2020=105.046 2021=106.87 2022=110.609 2023=110.798 2024=112.639 2025=114.61
KOR itu_392: 2000=57.341 2001=61.742 2002=68.379 2003=70.698 2004=76.705 2005=80.127 2006=83.733 2007=92.094 2008=94.314 2009=98.759 2010=104.097 2011=106.878 2012=108.115 2013=109.206 2014=113.359 2015=115.595 2016=119.49 2017=123.642 2018=128.495 2019=133.08 2020=135.973 2021=140.516 2022=148.684 2023=162.114 2024=172.52 2025=180.722
NOR itu_392: 2000=71.79 2001=79.603 2002=83.517 2003=88.962 2004=98.541 2005=102.841 2006=104.472 2007=106.979 2008=109.293 2009=110.892 2010=114.524 2011=115.596 2012=115.524 2013=112.046 2014=111.69 2015=110.118 2016=109.427 2017=108.393 2018=107.703 2019=108.005 2020=108.297 2021=109.586 2022=111.657 2023=109.654 2024=109.349 2025=108.837
NZL itu_392: 2000=39.973 2001=58.791 2002=61.982 2003=64.61 2004=74.12 2005=85.369 2006=90.922 2007=100.662 2008=108.404 2009=109.193 2010=108.331 2011=109.978 2012=111.568 2013=107.009 2014=112.757 2015=121.369 2016=129.381 2017=132.98 2018=128.937 2019=120.475 2020=123.001 2021=114.455 2022=115.984 2023=126.855 2024=130.093 2025=130.924
USA itu_392: 2000=38.893 2001=45.202 2002=49.393 2003=55.41 2004=63.124 2005=68.884 2006=76.859 2007=82.592 2008=85.68 2009=89.046 2010=91.659 2011=94.683 2012=96.128 2013=97.06 2014=99.84 2015=101.832 2016=102.752 2017=102.381 2018=103.935 2019=105.321 2020=103.855 2021=106.325 2022=108.786 2023=112.411 2024=113.19 2025=114.309
AUS itu_12066: 2010=56.121 2011=80.557 2012=96.505 2013=111.012 2014=114.547 2015=126.357 2016=129.651 2017=133.355 2018=128.457 2019=128.495 2020=123.024 2021=121.843 2022=126.285 2023=128.501 2024=129.03 2025=127.69
GBR itu_12066: 2009=36.473 2010=42.52 2011=61.59 2012=75.599 2013=85.494 2014=86.915 2015=85.453 2016=83.138 2017=87.75 2018=99.112 2019=104.43 2020=108.53 2021=125.279 2022=127.106 2023=129.799 2024=130.174 2025=130.929
GRC itu_12066: 2009=12.375 2010=25.048 2011=30.554 2012=34.621 2013=36.593 2014=41.861 2015=46.935 2016=55.198 2017=65.792 2018=79.801 2019=85.109 2020=86.278 2021=93.344 2022=89.368 2023=93.843 2024=97.293 2025=105.25
IRL itu_12066: 2009=49.832 2010=48.195 2011=58.69 2012=63.948 2013=67.19 2014=81.315 2015=95.538 2016=100.234 2017=100.939 2018=102.657 2019=104.31 2020=103.596 2021=107.752 2022=116.579 2023=118.159 2024=120.084 2025=122.032
KOR itu_12066: 2008=73.072 2009=87.866 2010=97.035 2011=103.478 2012=103.876 2013=103.637 2014=106.356 2015=107.018 2016=108.608 2017=111.662 2018=112.585 2019=113.697 2020=115.569 2021=117.113 2022=120.211 2023=121.796 2024=125.397 2025=129.562
NOR itu_12066: 2008=57.927 2009=68.536 2010=74.377 2011=76.079 2012=83.648 2013=86.044 2014=105.553 2015=94.606 2016=95.731 2017=98.33 2018=99.668 2019=102.303 2020=104.517 2021=114.889 2022=116.578 2023=114.178 2024=113.491 2025=112.679
NZL itu_12066: 2010=38.802 2011=53.437 2012=65.939 2013=82.221 2014=93.301 2015=113.783 2016=99.687 2017=99.34 2018=96 2019=96.164 2020=89.923 2021=93.682 2022=97.452 2023=109.379 2024=108.593 2025=106.971
USA itu_12066: 2008=8.7 2009=40.162 2010=60.283 2011=77.22 2012=89.224 2013=97.983 2014=102.556 2015=115.141 2016=124.301 2017=129.874 2018=138.215 2019=145.918 2020=154.347 2021=164.246 2022=173.686 2023=184.683 2024=196.707 2025=204.702
AUS itu_37470: 2013=53.476 2015=60.923 2017=69.155
GBR itu_37470: 2011=49.681 2013=58.123 2014=59.822 2015=65.656 2016=68.755 2020=70.473
GRC itu_37470: 2011=28.063 2013=36.114 2014=40.654 2015=43.907 2016=46.654 2020=59.406 2021=62.051 2022=67.034 2023=68.096 2024=68.379 2025=73.039
IRL itu_37470: 2011=40.266 2013=47.512 2014=52.841 2015=54.762
KOR itu_37470: 2013=43.53 2014=54.093 2015=57.232 2016=60.221 2017=67.868 2018=65.481 2019=63.202 2020=65.532 2021=68.355 2022=66.408 2023=66.747 2024=71.215 2025=65.335
NOR itu_37470: 2011=58.957 2013=67.58 2014=70.667 2015=73.216 2016=76.159 2017=80.413 2020=86 2021=87 2022=88 2023=88
USA itu_37470: 2015=45.135
GBR es_snet_y16_24: 2011=90.01 2013=93.27 2014=90.83 2015=91.97 2016=90.36 2017=95.39 2018=92.79 2019=98.35 2020=97.61
GRC es_snet_y16_24: 2011=72.78 2013=82.85 2014=80.09 2015=87.54 2016=88.59 2017=91.73 2018=96.13 2019=92.17 2020=89.52 2021=94.42 2022=93.31 2023=94.4 2024=97.08 2025=91.63
IRL es_snet_y16_24: 2011=79.39 2013=86.61 2014=89.55 2015=85.61 2016=89.07 2017=90.81 2018=89.7 2019=89.5 2023=91.51 2024=95.43 2025=93.14
NOR es_snet_y16_24: 2011=95.74 2013=97.42 2014=94.71 2015=92.08 2016=96.47 2017=95.88 2018=95.28 2019=97.25 2020=97.89 2021=96.46 2022=97.12 2023=98.04 2024=97.69 2025=96.01
GBR es_daily_y16_24: 2003=32.94 2004=40.22 2005=42.31 2006=49.99 2007=62.95 2008=72.21 2009=82.78 2010=80.01 2011=84.59 2012=88.82 2013=94.38 2014=92.13 2015=92.87 2016=96.42 2017=93.48 2018=100 2019=100 2020=100
GRC es_daily_y16_24: 2003=12.19 2004=13.44 2005=19.21 2006=20.39 2007=33.67 2008=47.16 2009=57.4 2010=62.17 2011=70.91 2012=74.08 2013=82.16 2014=83.56 2015=88.54 2016=91.67 2017=90.8 2018=94.83 2019=95.24 2020=96.11 2021=96.12 2022=97.94 2023=97.7 2024=98.17 2025=99.53
IRL es_daily_y16_24: 2003=11.98 2004=12.62 2005=17.07 2006=32.49 2007=42.9 2008=54.04 2009=57.51 2010=71.01 2011=78.47 2012=81.67 2013=83.13 2014=87.7 2015=91.45 2016=94.86 2017=92.88 2018=94.92 2019=96.58 2023=100 2024=99.49 2025=99.49
NOR es_daily_y16_24: 2003=43.02 2004=47.43 2005=59.57 2006=75.12 2007=75.07 2008=90.81 2009=88.92 2010=94.24 2011=93.24 2012=97.69 2013=95.65 2014=98.26 2015=97.7 2016=100 2017=97.78 2018=98.01 2019=98.12 2020=100 2021=98.3 2022=98.84 2023=98.87 2024=100 2025=96.45
GBR es_games_y16_24: 2002=27.84 2003=44.69 2004=51.63 2005=55.32 2006=54.65 2007=52.3 2009=67.21 2010=59.8 2012=67 2014=68.47
GRC es_games_y16_24: 2002=12.62 2003=22.92 2004=30.59 2005=27.89 2006=37.28 2007=44.31 2009=56.24 2010=50.28 2012=64.48 2014=67.43
IRL es_games_y16_24: 2003=9.87 2004=11.32 2005=14.6 2006=25.42 2007=29.33 2009=46.19 2010=45.67 2012=39.21 2014=73.05
NOR es_games_y16_24: 2003=59.97 2004=64.46 2005=59.92 2006=74.93 2007=72.92 2009=65.36 2010=72.68 2012=86.73 2014=78.73
KOR kor_youth_overdependence: 2015=31.6 2016=30.6 2017=30.3 2018=29.3 2019=30.2 2020=35.8 2021=37.0 2022=40.1 2023=40.1 2024=42.6
USA usa_yrbs_screen3h: 2003=22.1 2005=21.1 2007=24.9 2009=24.9 2011=31.1 2013=41.3 2015=41.7 2017=43.0 2019=46.1
USA usa_yrbs_tv3h: 2003=38.2 2005=37.2 2007=35.4 2009=32.8 2011=32.4 2013=32.5 2015=24.7 2017=20.7 2019=19.8
USA usa_pew_constant: 2015=24 2022=46 2023=46 2024=46
USA usa_pew_smartphone: 2015=73 2022=95 2023=95 2024=95
USA usa_pew_youtube: 2022=95 2023=93 2024=90
USA usa_pew_tiktok: 2022=67 2023=63 2024=63
USA usa_pew_instagram: 2015=52 2022=62 2023=59 2024=61
USA usa_pew_snapchat: 2015=41 2022=59 2023=60 2024=55
USA usa_pew_facebook: 2015=71 2022=32 2023=33 2024=32
AUS aus_abs_child_internet: 2006=65 2009=79 2012=90
AUS aus_abs_child_internet_12_14: 2009=96 2012=98
AUS aus_abs_child_mobile_12_14: 2009=76 2012=73
NZL nzl_nzonair_child_youtube: 2020=51
"""

# Google Trends (single-topic, yearly means) and Statcounter, wide blocks: iso year v1 v2 ...
GT_COLS = ['gt_facebook', 'gt_instagram', 'gt_youtube', 'gt_tiktok', 'gt_videogame']
SC_COLS = ['sc_mobile', 'sc_facebook', 'sc_instagram']


def rows():
    for line in DATA.strip().splitlines():
        head, vals = line.split(':', 1)
        iso, ind = head.split()
        for tok in vals.split():
            y, v = tok.split('=')
            yield iso, int(y), ind, v


def wide(path, cols):
    if not os.path.exists(path):
        return
    for r in csv.DictReader(open(path)):
        for c in cols:
            if r.get(c) not in (None, '', 'NA'):
                yield r['iso3'], int(r['year']), c, r[c]


def main():
    os.makedirs(OUT, exist_ok=True)
    allrows = list(rows())
    allrows += list(wide(os.path.join(OUT, 'raw', 'gt_yearly.csv'), GT_COLS))
    allrows += list(wide(os.path.join(OUT, 'raw', 'sc_yearly.csv'), SC_COLS))
    for fn in ['itu_extra.csv', 'es_mobile_y16_24.csv', 'gt_extra_long.csv', 'gdelt_yearly.csv']:
        fp = os.path.join(OUT, 'raw', fn)
        if os.path.exists(fp):
            for r in csv.DictReader(open(fp)):
                if r['indicator_id'] == 'itu_19306' and r['iso3'] == 'AUS' and r['year'] in ('2023', '2024'):
                    continue  # suspected entry error: equals the 5G value
                allrows.append((r['iso3'], int(r['year']), r['indicator_id'], r['value']))
    groups = {'itu': 'itu_direct', 'es': 'eurostat_youth', 'gt': 'google_trends', 'gtx': 'google_trends_xcountry', 'gd': 'gdelt_news', 'sc': 'statcounter',
              'kor': 'national_youth', 'usa': 'national_youth', 'aus': 'national_youth', 'nzl': 'national_youth'}
    files = {}
    seen = set()
    for iso, y, ind, v in allrows:
        key = (iso, y, ind)
        assert key not in seen, f'duplicate {key}'
        seen.add(key)
        lab, unit, dim, src = META[ind]
        fn = groups[ind.split('_')[0]]
        files.setdefault(fn, []).append([iso, y, ind, v, unit, dim, lab, src, RET])
    for fn, rs in files.items():
        with open(os.path.join(OUT, fn + '.csv'), 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['iso3', 'year', 'indicator_id', 'value', 'unit', 'dimension', 'label', 'source', 'retrieved'])
            w.writerows(sorted(rs, key=lambda r: (r[2], r[0], r[1])))
        print(fn, len(rs), 'rows')


if __name__ == '__main__':
    main()
