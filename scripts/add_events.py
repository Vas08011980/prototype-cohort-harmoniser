"""Merge the dated event files into the app.

data/events/regulation_timeline.csv  - laws, regulator milestones, school phone policies (one row per event)
data/events/platform_launches.csv    - national and global platform / smartphone launches
Every row must carry a source_url. Dates are ISO (YYYY-MM-DD, YYYY-MM or YYYY) with a 'precision' column.
Run from the repository root:  python scripts/add_events.py
"""
import csv, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, 'app', 'gchn_data.json')
ISO = {'AUS', 'USA', 'GBR', 'IRL', 'NZL', 'NOR', 'GRC', 'KOR', 'GLOBAL'}
problems = []


def load(name, required):
    rows = []
    for n, r in enumerate(csv.DictReader(open(os.path.join(ROOT, 'data', 'events', name), encoding='utf-8-sig')), start=2):
        r = {k: (v or '').strip() for k, v in r.items()}
        miss = [k for k in required if not r.get(k)]
        if miss:
            problems.append(f'{name} line {n}: missing {miss}'); continue
        if not re.fullmatch(r'\d{4}(-\d{2}(-\d{2})?)?', r['date']):
            problems.append(f'{name} line {n}: bad date {r["date"]}'); continue
        bad = [a for a in r['applies_to'].split(';') if a not in ISO]
        if bad:
            problems.append(f'{name} line {n}: unknown applies_to {bad}'); continue
        rows.append(r)
    return sorted(rows, key=lambda r: r['date'])


data = json.load(open(APP))
reg = load('regulation_timeline.csv', ['date', 'precision', 'applies_to', 'kind', 'status', 'title', 'source_url'])
lau = load('platform_launches.csv', ['date', 'precision', 'applies_to', 'kind', 'title', 'source_url'])
data['events'] = {'reg': reg, 'launch': lau}
json.dump(data, open(APP, 'w'))
print(f'Merged {len(reg)} regulation events and {len(lau)} launches into app/gchn_data.json')
if problems:
    print('\n'.join(problems)); sys.exit(1)
