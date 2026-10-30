"""29 Oct 2026: load the FULL Growing Up in New Zealand and LSAC data dictionaries into the lexicon,
replacing the GUiNZ crosswalk rows and the LSAC Wave-1-only extract.

Inputs (GCHN_WORKDIR/raw/, not in the repo):
  guinz_full.xlsx  69ccc194071e4a312a828c1e_DataDictionary_All_v1.03.xlsx (44 tabs, one per data collection wave × informant)
  lsac_full.xlsx   LSAC-Data-Dictionary-Release-10.1.xlsx (sheet "Release 10.1 DD", 77,039 rows)

Run from the repository root, then rebuild:
  GCHN_WORKDIR=... python scripts/load_guinz_lsac_full.py
  GCHN_WORKDIR=... python scripts/update_tess_ukhls_adii.py
  python scripts/add_context.py
Construct assignment = the same keyword screen as build_lexicon.py, plus a few dictionary-native mappings
(LSAC "Construct" field, GUiNZ "Media Use" and "Parenting" domains), listed below.
"""
import os, re, json
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = os.environ.get('GCHN_WORKDIR', '.')
R = os.path.join(W, 'raw')
LEX = os.path.join(ROOT, 'data', 'lexicon_candidates.csv')
APP = os.path.join(ROOT, 'app', 'gchn_data.json')

# ---- keyword screen: reuse the definitions in build_lexicon.py (everything before the first data load)
src = open(os.path.join(ROOT, 'scripts', 'build_lexicon.py'), encoding='utf-8').read()
src = src[:src.index('rows = []')]
ns = {}
exec(compile(src, 'build_lexicon_defs', 'exec'), ns)
classify = ns['classify']

import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lexio import read_lex, write_lex
d = read_lex()
before = d.groupby('study').size().to_dict()
d = d[~d.study.isin(['GUiNZ', 'LSAC'])]
new = []
def add(cons, **k):
    for c in sorted(set(cons)):
        new.append(dict(k, construct=c))

# ======================================================================= LSAC
L_SRC = 'LSAC-Data-Dictionary-Release-10.1.xlsx (full, 77,039 rows)'
lsac = pd.read_excel(os.path.join(R, 'lsac_full.xlsx'), sheet_name='Release 10.1 DD').fillna('')
WAVE_YEAR = {'1': '2004', '1.5': '2005', '2': '2006', '2.5': '2007', '3': '2008', '3.5': '2009', '4': '2010', '5': '2012', '6': '2014',
             '7': '2016', '8': '2018', '9C1': '2020', '9C2': '2021', '10': '2022'}
# the main wave of each file (files = cohort × age); mail-out files B3/K7 (1.5), B5/K9 (3.5)
filewave = lsac.groupby('File')['Wave'].agg(lambda s: s.astype(str).value_counts().index[0]).to_dict()
filewave.update({'B3': '1.5', 'K7': '1.5', 'B5': '3.5', 'K9': '3.5'})
LSAC_CON = {  # dictionary-native construct -> Atlas construct (added to the keyword screen)
    'Computer use': ['DM_ST'], 'Internet use': ['DM_ST'], 'TV & video use': ['DM_ST'], 'TV/computer/internet use': ['DM_ST'],
    'Digital communication': ['DM_SM'], 'Social media use': ['DM_SM'], 'Internet and offline communication': ['DM_SM'],
    'Electronic gaming': ['DM_GM'], 'Mobile phone use': ['DM_DEV'], 'Media supervision': ['PC_MON'],
    'Parental monitoring': ['PC_MON'], 'Monitoring': ['PC_MON'], 'Maternal monitoring': ['PC_MON'],
    'Parental warmth': ['PC_REL'], 'Hostile parenting': ['PC_REL'], 'Consistent parenting': ['PC_REL'],
    'Family cohesion': ['PC_FAM'],
}
def lsac_inf(p):
    p = str(p)
    if p.startswith('Study Child') or p in ('SC Partner',): return 'Youth'
    if re.match(r'(Parent|Mother|Father|P1|P2)', p): return 'Parent'
    if p.startswith('Teacher') or p in ('School', 'Main education'): return 'Teacher/School'
    if p == 'Not applicable': return 'Derived'
    return 'Other'
ls = dict(rows=len(lsac), kept=0)
for _, r in lsac.iterrows():
    if r['Topic'] in ('Identifiers',) and r['Construct'] != 'TV/computer/internet use': continue
    text = str(r['Question']) if len(str(r['Question'])) > 5 else str(r['Variable Label'])
    inst = ' – '.join(x for x in (str(r['Topic']), str(r['Construct']), str(r['Measure'])) if x and x != 'nan')
    cons = classify(text, inst) + LSAC_CON.get(str(r['Construct']), [])
    if not cons: continue
    f = str(r['File']); coh = f[0]; age = int(f[1:])
    w = filewave.get(f, str(r['Wave']))
    ls['kept'] += 1
    add(cons, study='LSAC', cohort='LSAC %s cohort' % coh, wave='W' + w, years=WAVE_YEAR.get(w, ''), age=str(r["Child's Age"]).replace('/', '–') or str(age),
        informant=lsac_inf(r['Person Label']), var=str(r['Without Age']) or str(r['Variable Name']), text=text[:400], instrument=inst[:120],
        source=L_SRC, level='item', timing='dictionary (file = cohort × age; wave fieldwork year)')

# ======================================================================= GUiNZ
G_SRC = 'DataDictionary_All_v1.03.xlsx (GUiNZ, full, 44 tabs)'
# data collection wave -> (wave label, child age in years, fieldwork years)
DCW = [('DCW0', 'Antenatal', 0, '2009–2010'), ('DCW1W6', '6w', 0.1, '2009–2010'), ('DCW1', '9m', 0.75, '2010'),
       ('DCW2M16', '16m', 1.33, '2010–2011'), ('DCW2M23', '23m', 1.9, '2011'), ('DCW2Y2', '2y', 2, '2011–2012'),
       ('DCW3', '31m', 2.6, '2012'), ('DCW4', '45m', 3.75, '2013'), ('DCW5', '4.5y', 4.5, '2014'), ('DCW6', '6y', 6, '2015–2016'),
       ('DCW8', '8y', 8, '2017–2018'), ('DCW11LDC', '11y (COVID-19 survey)', 10.5, '2020'), ('DCW12', '12y', 12, '2021–2022'),
       ('DCW13EW', '13y (e-wave)', 13, '2022–2023'), ('DCW15', '15y', 15, '2024–2025')]
def g_wave(sheet):
    for pre, lab, age, yrs in sorted(DCW, key=lambda t: -len(t[0])):  # longest prefix first (DCW12 before DCW1)
        if sheet.startswith(pre): return pre, lab, age, yrs, sheet[len(pre):]
    return None
def g_inf(suffix, age):
    s = suffix
    if s in ('C', 'LDC', 'EWC'): return 'Youth' if age >= 8 else 'Parent'  # infant "C" files are mother-reported/measured
    if s in ('CM', 'CP', 'CONDCM', 'M', 'P', 'M16CM', 'M23CM', 'Y2CM', 'Y2CP', 'M16M', 'M23M', 'Y2M', 'Y2P', 'EWM', 'CON'): return 'Parent'
    if s.endswith('CO') or s == 'CO': return 'Observed'
    if s == 'T': return 'Teacher/School'
    if s in ('M', 'Y2O', 'O'): return 'Other'
    return 'Parent' if 'M' in s or 'P' in s else 'Other'
gs = dict(sheets=0, vars=0, kept=0)
x = pd.ExcelFile(os.path.join(R, 'guinz_full.xlsx'))
for sheet in x.sheet_names:
    gw = g_wave(sheet)
    if not gw: continue  # 'Perinatal' (birth record linkage) has no survey items
    pre, wl, age, yrs, suf = gw
    t = pd.read_excel(x, sheet, header=2)
    t.columns = [str(c).strip() for c in t.columns]
    if 'Variable name' not in t.columns: continue
    for c in ('Research domain', 'Subdomain'):
        if c not in t.columns: t[c] = ''
    t[['Research domain', 'Subdomain']] = t[['Research domain', 'Subdomain']].ffill()
    t = t[t['Variable name'].notna() & (t['Variable name'].astype(str).str.strip() != '')]
    gs['sheets'] += 1; gs['vars'] += len(t)
    inf = g_inf(suf.replace(pre, ''), age)
    for _, r in t.iterrows():
        q = r.get('Question'); lab = r.get('Labels')
        text = str(q) if isinstance(q, str) and len(q) > 3 else (str(lab) if isinstance(lab, str) else '')
        if not text: continue
        dom = ' – '.join(str(v) for v in (r['Research domain'], r['Subdomain']) if isinstance(v, str))
        cons = classify(text, dom)
        if re.search(r'media use|screen|media interaction|technology', dom, re.I) and not cons: cons = ['DM_ST']
        if re.search(r'\bparenting\b', dom, re.I) and not cons: cons = ['PC_REL']
        vn = str(r['Variable name']).strip().upper()
        if re.match(r'TU11[4-9]_', vn): cons = sorted(set(cons) | {'DM_PU', 'DM_ST'})  # GUiNZ problematic screen-use items (12y)
        if re.match(r'SDQ\d', vn): cons = sorted(set(cons) | {'WB_MOOD'})
        if re.match(r'WBE[1-7]_Y15C$', vn) or re.match(r'LSA1_', vn): cons = sorted(set(cons) | {'WB_LS'})  # SWEMWBS-worded items; Cantril ladder
        if not cons: continue
        var = re.sub(r'_(?:A[MP]|[MY]\d+[A-Z]*|W6|LDC|EW[CM]|Y\d+[A-Z]*)$', '', str(r['Variable name']).strip())
        gs['kept'] += 1
        add(cons, study='GUiNZ', cohort='GUiNZ (born 2009–10)', wave=wl, years=yrs, age=age, informant=inf, var=var,
            text=re.sub(r'\s+', ' ', text)[:400], instrument=('%s · %s' % (sheet, dom))[:120], source=G_SRC, level='item',
            timing='dictionary tab = data collection wave × informant; years from fieldwork window (approx.)')

nd = pd.DataFrame(new)
d = pd.concat([d, nd], ignore_index=True).fillna('')
write_lex(d)
after = d.groupby('study').size().to_dict()
print('LSAC:', ls, '| GUiNZ:', gs)
print('rows before/after:', {k: (before.get(k), after.get(k)) for k in ('LSAC', 'GUiNZ')})
print(nd.groupby(['study', 'construct']).size().unstack(fill_value=0).to_string())

# ---- study metadata in the app JSON (the rebuild in update_tess_ukhls_adii.py keeps these)
D = json.load(open(APP))
for s in D['studies']:
    if s['id'] == 'LSAC':
        s.update(status='full', dict_file='LSAC-Data-Dictionary-Release-10.1.xlsx (full)',
                 design='Cohort: B (born 2003–04, 0–1y in 2004) & K (born 1999–2000, 4–5y in 2004); biennial W1 2004 → W10 2022',
                 note=('Full Release 10.1 dictionary (77,039 variable × wave rows, B and K cohorts, W1–W10 incl. between-wave mail-outs). '
                       'Wave = data file (cohort × child age); variables are aggregated across waves on their age-free stem. Informant from the '
                       'dictionary "Person Label": Study Child = Y, Parent 1/2, mother, father, parent living elsewhere = P, teacher/carer = T, '
                       'derived scores = D. Construct = keyword screen plus LSAC\'s own construct labels (e.g. Electronic gaming, Social media use, '
                       'Media supervision, Parental warmth, Hostile parenting, Parental monitoring).'))
    if s['id'] == 'GUiNZ':
        s.update(status='full', dict_file='DataDictionary_All_v1.03.xlsx (full, 44 tabs)',
                 design='Birth cohort (born Apr 2009–Mar 2010); antenatal → 6 weeks → 9m … 8y, 12y, 13y e-wave, 15y',
                 note=('Full data dictionary: %d tabs (data collection wave × informant: M mother, P partner, CM/CP parent report on the child, '
                       'C child self-report from 8y, CO observation, T teacher), %d variables. Ages are the scheduled collection ages; '
                       'fieldwork years are approximate windows from the birth cohort. The crosswalk rows used before have been replaced.')
                      % (gs['sheets'], gs['vars']))
for a in D['anchors']:
    if a['inst'].startswith('Strengths and Difficulties'):
        a['where'] = [w for w in a['where'] if w[0] not in ('GUiNZ', 'LSAC')] + [
            ['GUiNZ', 'Mother report on the child (2y–8y tabs); child self-report at 12y (SDQ items in DCW12C)'],
            ['LSAC', 'Parent, teacher/carer and study-child self-report (10–17y), both cohorts']]
        a['note'] = 'Strongest item-level anchor across 7 studies. Informant differs (parent vs self vs teacher): never pool across informants (Table 2, e).'
    if a['inst'].startswith('Short Mood and Feelings'):
        a['where'] = [w for w in a['where'] if w[0] != 'LSAC'] + [['LSAC', 'Study-child "Depressed feelings" scale, 12–16y (SMFQ-type; the dictionary does not name the instrument, confirm in LSAC documentation)']]
    if a['inst'].startswith('Kessler'):
        a['where'] = [w for w in a['where'] if w[0] != 'LSAC'] + [['LSAC', 'Parents K6 (all waves); study child K10 16–23y and K6 19–23y']]
        a['note'] = 'Parent-wellbeing measure in MCS/GUI/LSAC (proximate context); youth self-report in HILDA and LSAC (16–23y), a within-Australia anchor.'
json.dump(D, open(APP, 'w'), default=lambda o: None, allow_nan=False)
print('metadata updated')
