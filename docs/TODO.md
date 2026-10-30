# To do: Yifei and Spiros

## 1. Digital context (the "invisible room")
| Dimension | Status | Add |
|---|---|---|
| Access | Loaded (World Bank copy of ITU) | Replace with a direct ITU DataHub download of the same three series. Add households with home internet (%), mobile-broadband subscriptions /100, 4G coverage (%) and the mobile-broadband affordability basket (% GNI per capita). |
| Participation | Proxy only | Social-media users (% of population), smartphone / mobile internet users (%), and internet use by 16–24 year olds where available (Eurostat, national offices). |
| Attention | Missing | Your Google Trends exports, monthly from 2004. Countries: AU, US, GB, IE, NZ, NO, GR, KR. Use Topic entities and one shared anchor term in every download. Record the retrieval date, then average months to years. |
| Platform environment | Hand-coded launch years only | Statcounter social-media referral share by country (from 2009), mobile/OS share, and country availability dates with sources. |
| Information environment | Missing | GDELT yearly share of news on social media, gaming, online safety, youth wellbeing and AI. A dated, sourced regulation timeline per country. |

To add any of these, save a CSV in `data/context/` and run `python scripts/add_context.py` (see README).

## 2. Lexicon gaps
- **LSAC**: load the full Release 10.1 dictionary; only Wave 1 is in.
- **Growing Up in New Zealand**: load DataDictionary_All_v1.03.xlsx; only the crosswalk is in.
- **Understanding Society**: load the full harmoniser dictionary; only the digital-engagement rows are in.
- **TESS**: build an item-level dictionary. The T1–T10 overview has 9 cells per row against 10 time points.
- **AStRA**: tabulate age at each wave from the .sav files.
- **ABCD**: replace the table-level wave coverage with item-level coverage from the events file.

## 3. Review
- Go through the candidate rows per construct and mark each as approve, reject or revise. Start with screen time, social media, emotional wellbeing and the parent–child relationship.
- Check each "shared instrument" item by item: wording, response options, informant, age.
