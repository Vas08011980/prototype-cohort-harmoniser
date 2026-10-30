"""Merge country-year context indicators into the app.

Put one or more CSV files in data/context/ with these columns:
  iso3, year, indicator_id, value, unit, dimension, label, source, retrieved
  - iso3: AUS, USA, GBR, IRL, NZL, NOR, GRC, KOR (ISO 3166-1 alpha-3)
  - year: calendar year (2000-2026). Aggregate monthly data (e.g. Google Trends) to yearly means first.
  - dimension: Access | Participation | Attention | Platform environment | Information environment
  - one row per country x year x indicator; leave value empty when there is no published value (never interpolate)

Then run from the repository root:
  python scripts/add_context.py
The indicators are written to app/gchn_data.json under "context" and appear in the app's Shading menu
and in the Invisible room panel. Re-running replaces previously merged context indicators.
"""
import csv, glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, 'app', 'gchn_data.json')
DIMS = {'Access', 'Participation', 'Attention', 'Platform environment', 'Information environment'}
ISO = {'AUS', 'USA', 'GBR', 'IRL', 'NZL', 'NOR', 'GRC', 'KOR'}
Y0, Y1 = 2000, 2026

data = json.load(open(APP))
context = {}
problems = []
files = sorted(glob.glob(os.path.join(ROOT, 'data', 'context', '*.csv')))
for f in files:
    for n, r in enumerate(csv.DictReader(open(f, encoding='utf-8-sig')), start=2):
        try:
            iso, year, ind = r['iso3'].strip().upper(), int(r['year']), r['indicator_id'].strip()
        except (KeyError, ValueError) as e:
            problems.append(f'{os.path.basename(f)} line {n}: {e}'); continue
        if iso not in ISO: problems.append(f'{os.path.basename(f)} line {n}: unknown iso3 {iso}'); continue
        if r['dimension'].strip() not in DIMS: problems.append(f'{os.path.basename(f)} line {n}: dimension must be one of {sorted(DIMS)}'); continue
        if not Y0 <= year <= Y1: continue
        c = context.setdefault(ind, dict(label=r['label'].strip(), unit=r['unit'].strip(), dimension=r['dimension'].strip(),
                                         source=r['source'].strip(), retrieved=r['retrieved'].strip(), file=os.path.basename(f),
                                         values={i: [None] * (Y1 - Y0 + 1) for i in ISO}))
        v = r['value'].strip()
        c['values'][iso][year - Y0] = float(v) if v else None

data['context'] = context
json.dump(data, open(APP, 'w'))
print(f'Merged {len(context)} indicators from {len(files)} file(s) into app/gchn_data.json')
for k, c in context.items():
    filled = sum(v is not None for a in c['values'].values() for v in a)
    print(f'  {k}: {c["label"]} [{c["dimension"]}] {filled} country-year values')
if problems:
    print('\nRows skipped:'); print('\n'.join(problems[:50])); sys.exit(1)
