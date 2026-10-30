"""29 Oct 2026 update: rebuild TESS and Understanding Society lexicon rows from the revised
dictionaries, add the Australian Digital Inclusion Index (ADII), and rebuild atlas / items / timeline.

Inputs (GCHN_WORKDIR/raw/, not in the repo; all from the Data Dictionaries folder in Google Drive):
  tess_instruments.docx          TESS instruments T1-T10_CleanVersion.docx (revised 27 Oct 2026)
  ukhls_targeted.xlsx            UKHLS_Targeted_Harmoniser_Dictionary_2026-10-27.xlsx
  adii_dict.xlsx                 00_ADII_Harmoniser_Dictionary.xlsx
  adii_webtables_2020_state.xlsx 03_Data_2020_Webtables_National_Subgroups.xlsx (legacy series by state)

Run from the repository root:
  GCHN_WORKDIR=/path/to/workdir python scripts/update_tess_ukhls_adii.py
  python scripts/add_context.py
"""
import os, re, json, csv
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = os.environ.get('GCHN_WORKDIR', '.')
R = os.path.join(W, 'raw')
LEX = os.path.join(ROOT, 'data', 'lexicon_candidates.csv')
APP = os.path.join(ROOT, 'app', 'gchn_data.json')
TODAY = '2026-10-29'

import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lexio import read_lex, write_lex
d = read_lex()

# ---------------------------------------------------------------- ABCD: item-level waves (29 Oct 2026)
# 1) wave presence from the data (local file data/abcd_item_waves.csv from scripts/abcd_item_waves_from_data.py; not distributed) where available;
# 2) otherwise the REDCap branching logic of the ABCD 7.0 dictionary (data/abcd_item_event_logic.csv);
# 3) otherwise the table-level coverage stays (flagged in `timing`).
from lexio import abcd_allowed
_ab = d.study == 'ABCD'
_iw = os.path.join(ROOT, 'data', 'abcd_item_waves.csv'); _lg = os.path.join(ROOT, 'data', 'abcd_item_event_logic.csv')
_cnt = pd.read_csv(_iw) if os.path.exists(_iw) else pd.DataFrame(columns=['name', 'wave', 'n_nonmissing', 'source_file'])
_wn = lambda w: float(str(w)[1:]) if str(w).startswith('Y') else -1
_maxw = _cnt.assign(wn=_cnt.wave.map(_wn)).groupby('source_file').wn.max().to_dict()
_cn = {(r.name, r.wave): (r.n_nonmissing, _maxw.get(r.source_file, -1)) for r in _cnt.itertuples()}
_cvars = set(_cnt.name)
_lgc = dict(pd.read_csv(_lg)[['name', 'branching_logic']].values) if os.path.exists(_lg) else {}
keep, tim = [], []
abcd_stats = dict(data_dropped=0, logic_dropped=0, rows=int(_ab.sum()))
for r in d.itertuples():
    if r.study != 'ABCD' or r.informant == 'Passive sensing':
        keep.append(True); tim.append(r.timing); continue
    if r.var in _cvars:
        n = _cn.get((r.var, r.wave))
        if n is None:
            mx = max((v[1] for (nm, w), v in _cn.items() if nm == r.var), default=-1)
            ok = _wn(r.wave) > mx  # wave beyond the data we counted: keep
        else:
            ok = n[0] > 0
        keep.append(ok); abcd_stats['data_dropped'] += (not ok)
        tim.append('item-level: answered in the data (wave presence only)' + ('' if (n is not None) else ' (later waves from table coverage)'))
    elif r.var in _lgc:
        a = abcd_allowed(_lgc[r.var], r.wave)
        keep.append(a is not False); abcd_stats['logic_dropped'] += (a is False)
        tim.append('item-level: REDCap branching logic (ABCD 7.0 dictionary)')
    else:
        keep.append(True); tim.append('table-level wave coverage (no item-level information yet)')
d = d.assign(timing=tim)[keep]
print('ABCD item-level waves:', abcd_stats)

# ---------------------------------------------------------------- AStRA ages (29 Oct 2026)
# C1 (2005–07) and C2 (2013–15): first grade of Gymnasium at W1, M age 12.6 (Motti-Stefanidi et al., 2017: N = 1,057 and 1,052),
# annual waves -> 12.6, 13.6, 14.6. C3 (2022–23): Gymnasium grades 1–3 at W1 (dictionary: sch_grade.w1) -> 12–15 at W1, 13–16 at W2.
_AG = {('AStRA Cohort 1', 'W1'): 12.6, ('AStRA Cohort 1', 'W2'): 13.6, ('AStRA Cohort 1', 'W3'): 14.6,
       ('AStRA Cohort 2', 'W1'): 12.6, ('AStRA Cohort 2', 'W2'): 13.6, ('AStRA Cohort 2', 'W3'): 14.6,
       ('AStRA Cohort 3 (Migrant Youth Resilience)', 'W1'): '12–15', ('AStRA Cohort 3 (Migrant Youth Resilience)', 'W2'): '13–16'}
_m = d.study == 'AStRA'
d.loc[_m, 'age'] = [str(_AG.get((c, w), a)) for c, w, a in zip(d.loc[_m, 'cohort'], d.loc[_m, 'wave'], d.loc[_m, 'age'])]
d.loc[_m, 'timing'] = 'C1/C2: M age 12.6 at W1 (Motti-Stefanidi et al., 2017), annual; C3: Gymnasium grades 1–3 at W1'
before = d.groupby('study').size().to_dict()
d = d[~d.study.isin(['TESS', 'Understanding Society'])]
new = []

def row(**k):
    base = dict(study='', cohort='', wave='', years='', age='', informant='', var='', text='', instrument='', construct='',
                source='', level='item', timing='')
    base.update(k); new.append(base)

# ---------------------------------------------------------------- TESS
import docx
TESS_SRC = 'TESS instruments T1-T10_CleanVersion.docx (rev. 27 Oct 2026)'
doc = docx.Document(os.path.join(R, 'tess_instruments.docx'))
tab = doc.tables[0]
grid = [[c.text.strip() for c in r.cells] for r in tab.rows]
assert all(len(r) == 11 for r in grid), 'TESS table is no longer 11 columns wide'
TP = {k: (2 + 2 * k, '%d–%d' % (2005 + 2 * k, 2006 + 2 * k)) for k in range(1, 11)}  # T1 = 4y (2007–08) ... T10 = 22y (2025–26)
SECTIONS = {
    'Information from child/adolescence': 'Youth',
    'Information from parents – about child/adolescent': 'Parent',
    'Parent report on parent-child relationship and parenting': 'Parent',
    'Parent report on parents': 'Parent',
    'Day-care and school reports': 'Teacher/School',
    'Reports from health clinic': 'Other',
    'Observation and testing': 'Observed',
    'Coding of parent-child interaction': 'Observed',
}
# (section informant, row label prefix) -> constructs. Labels are matched on the start of the row label.
TESS_MAP = [
    ('Youth', 'Mental health - diagnoses', ['WB_MOOD'], 'Diagnostic interview (includes depressive and anxiety disorders)'),
    ('Youth', 'Perceived relationship to parents and parenting', ['PC_REL'], ''),
    ('Youth', 'Parenting styles', ['PC_REL', 'PC_MON'], 'APQ includes a poor monitoring/supervision subscale'),
    ('Youth', 'Youth disclosure', ['PC_MON'], ''),
    ('Youth', 'Loneliness', ['WB_MOOD'], ''),
    ('Youth', 'Worrying', ['WB_MOOD'], ''),
    ('Youth', 'Rumination', ['WB_MOOD'], ''),
    ('Youth', 'Quality of life and well-being', ['WB_LS'], 'Adopted from the UK Millennium Cohort Study 7-item wellbeing grid'),
    ('Youth', 'Self-esteem', ['WB_SE'], ''),
    ('Youth', 'Screen use', ['DM_ST'], ''),
    ('Youth', 'Fear of missing out', ['DM_PU', 'DM_SM'], ''),
    ('Youth', 'Cyberbullying', ['DM_SM'], ''),
    ('Youth', 'Internet gaming disorder –', ['DM_GM', 'DM_PU'], 'Semi-structured clinical IGD interview'),
    ('Youth', 'Internet gaming disorder', ['DM_GM', 'DM_PU'], ''),
    ('Youth', 'Social media use', ['DM_SM'], ''),
    ('Youth', 'Data donation', ['DM_SM', 'DM_ST'], 'Planned; objective, retrospective'),
    ('Youth', 'Retrospective social media interaction records', ['DM_SM'], 'Planned; objective, retrospective'),
    ('Youth', 'AI interaction records', ['DM_ST'], 'Planned; objective, retrospective'),
    ('Youth', 'Conflict with parents and peers', ['PC_REL'], ''),
    ('Youth', 'Family climate', ['PC_FAM'], ''),
    ('Parent', 'Mental health of child', ['WB_MOOD'], 'Parent report about the child'),
    ('Parent', 'Screen use (type, frequency, duration)', ['DM_ST'], 'Parent report about the child'),
    ('Parent', 'Attitudes towards child expressing emotions', ['PC_REL'], ''),
    ('Parent', 'Parenting styles', ['PC_REL', 'PC_MON'], 'APQ includes a poor monitoring/supervision subscale'),
    ('Parent', 'Parental stress', ['PC_REL'], 'PSI includes a parent–child dysfunctional interaction subscale'),
    ('Parent', 'Family climate', ['PC_FAM'], ''),
    ('Parent', 'Marital relationship quality', ['PC_FAM'], ''),
    ('Parent', 'Interparental conflict and aggression', ['PC_FAM'], ''),
    ('Parent', 'Relationship history', ['PC_FAM'], ''),
    ('Parent', 'Parental social media use', ['DM_SM'], "Parent's own use (proximate digital context)"),
    ('Parent', 'Parental gaming', ['DM_GM'], "Parent's own use (proximate digital context)"),
    ('Teacher/School', 'Mental health of child', ['WB_MOOD'], 'Teacher report'),
    ('Observed', 'Emotional availability', ['PC_REL'], 'Coded parent–child interaction'),
    ('Observed', 'Parent-child interaction', ['PC_REL'], 'Coded parent–child interaction'),
]
sec = None
tess_stats = dict(rows=len(grid), cols=len(grid[0]), data_rows=0, filled=sum(1 for r in grid[1:] for c in r[1:] if c), mapped_rows=0)
for r in grid[1:]:
    lab = r[0]
    if lab in SECTIONS and not any(r[1:]): sec = SECTIONS[lab]; continue
    tess_stats['data_rows'] += 1
    hit = next((m for m in TESS_MAP if m[0] == sec and lab.startswith(m[1])), None)
    if not hit: continue
    tess_stats['mapped_rows'] += 1
    _, _, cons, note = hit
    short = lab.split(' Source:')[0]
    for k in range(1, 11):
        cell = r[k].strip().replace('Interview (revidert) + et spm nakenbilder.', 'Interview (revised) + one question on nude images').replace('Koding:', 'Coding:')
        if not cell: continue
        age, yrs = TP[k]
        for c in cons:
            row(study='TESS', cohort='TESS (Trondheim, born 2003–04)', wave='T%d' % k, years=yrs, age=age, informant=sec,
                var='', text=short + (' – ' + note if note else ''), instrument=cell, construct=c, source=TESS_SRC, level='instrument',
                timing='instrument overview, time points aligned (T1 4y … T10 22y; biennial)')
# App time-use: screenshots (T7–T10) are in the overview. Retrospective objective app-use records matched to each wave
# are confirmed by the study lead (29 Oct 2026) but are not itemised in the overview file.
for k in range(7, 11):
    age, yrs = TP[k]
    for c in ['DM_ST', 'DM_SM']:
        row(study='TESS', cohort='TESS (Trondheim, born 2003–04)', wave='T%d' % k, years=yrs, age=age, informant='Passive sensing',
            var='', text='Objective app time-use: screenshot of the phone’s 7-day app-usage log, collected at the visit',
            instrument='Screen shot of mobile – time use on apps 7 days', construct=c, source=TESS_SRC, level='measure',
            timing='objective log, 7 days before the visit')
        row(study='TESS', cohort='TESS (Trondheim, born 2003–04)', wave='T%d' % k, years=yrs, age=age, informant='Passive sensing',
            var='', text='Retrospective objective application-use records, matched to this wave (study-lead confirmation, 29 Oct 2026; not yet itemised in the instrument overview)',
            instrument='Retrospective objective app records (per wave)', construct=c, source='Study lead confirmation (V. Stavropoulos, 29 Oct 2026)',
            level='measure', timing='objective log, matched per wave – verify coverage window with TESS')

# ---------------------------------------------------------------- Understanding Society (targeted dictionary)
U_SRC = 'UKHLS_Targeted_Harmoniser_Dictionary_2026-10-27.xlsx'
u = pd.read_excel(os.path.join(R, 'ukhls_targeted.xlsx'), sheet_name='Targeted_Dictionary')
CON = {'Life satisfaction & subjective wellbeing': 'WB_LS', 'Emotional wellbeing (low mood, worry)': 'WB_MOOD',
       'Self-esteem & self-worth': 'WB_SE', 'Screen time': 'DM_ST', 'Social media & online communication': 'DM_SM',
       'Gaming': 'DM_GM', 'Problematic / compulsive use': 'DM_PU', 'Device access & ownership': 'DM_DEV',
       'Parent–child relationship': 'PC_REL', 'Parental monitoring & media rules': 'PC_MON', 'Family functioning & climate': 'PC_FAM'}
INF = {'Y': 'Youth', 'P': 'Parent', 'A': 'Adult (self)', 'H': 'Household', 'D': 'Derived', 'S': 'Digital trace'}
AGE = {'Y': '10–15', 'P': '0–15', 'A': '16–25', 'H': '', 'D': '', 'S': ''}
GROUP = {'Y': 'youth (10–15)', 'P': 'parent report on child (0–15)', 'A': 'adults (youth slice 16–25)', 'H': 'household', 'D': 'derived', 'S': 'linked Twitter/X data'}
COMP = {'UKHLS main survey': 'UKHLS', 'BHPS (harmonised)': 'BHPS', 'Innovation Panel': 'IP', 'COVID-19 Study': 'COVID-19 Study',
        'PEACH': 'PEACH', 'IP Twitter Study': 'IP Twitter Study', 'IP Wellbeing App Study': 'IP Wellbeing App'}
u = u[u['Construct'].isin(CON)]
ustats = dict(rows=len(u), stems=u['Variable stem'].nunique())
for _, r in u.iterrows():
    code = str(r['Informant (Atlas code)']).strip()
    comp = str(r['Component'])
    waves = [w.strip() for w in str(r['Waves assessed']).split(',') if w.strip()]
    years = [y.strip() for y in str(r['Fieldwork years assessed']).split(',') if y.strip()]
    if len(years) != len(waves): years = [', '.join(years)] * len(waves) if len(waves) else years
    age = AGE.get(code, '')
    lab = str(r['Variable label (latest wave)'])
    if comp == 'PEACH':
        m = re.search(r'age (\d+)', lab); age = m.group(1) if m else '3–8'
    vl = str(r.get('Value labels (latest wave; standard missing codes -1 to -10 omitted)', '') or '')
    text = lab + (' [' + vl[:160] + ']' if vl and vl != 'nan' else '')
    for w, y in zip(waves, years):
        wl = w if comp in ('UKHLS main survey', 'BHPS (harmonised)', 'Innovation Panel') else '%s: %s' % (COMP[comp], w)
        if comp == 'BHPS (harmonised)': wl = w.replace('BHPS ', 'BHPS-')
        row(study='Understanding Society', cohort='%s %s' % (COMP[comp], GROUP.get(code, code)), wave=wl, years=y.replace('-', '–'), age=age,
            informant=INF.get(code, 'Other'), var=str(r['Variable stem']), text=text, instrument='%s · %s file' % (comp, r['File type']),
            construct=CON[r['Construct']], source=U_SRC, level='item',
            timing='dictionary (fieldwork years per wave)' + ('' if comp in ('UKHLS main survey', 'BHPS (harmonised)', 'Innovation Panel', 'COVID-19 Study') else '; not a wave-based design'))

# ---------------------------------------------------------------- keyword-screen false positives (checked by hand, 29 Oct 2026)
FP = {'PC_MON': r"treated you unfairly|supervisor|laid off|fired from|discriminat|skipped school|help (?:with )?or supervision|needs help with|monitor put on|monitor (?:was )?(?:taken off|removed|worn|on)|accelerometer|activity monitor|heart ?rate monitor|blood pressure|glucose|know where to (?:get|find|go)|local services|restrictions does the family member|baby monitor",
      'WB_LS': r"satisf\w* with (?:the |this |your |their |his |her )?(?:programme|program|course|care|childcare|main care|service|services|arrangement|job|work|pay|income|house|housing|accommodation|neighbourhood|area|hospital|treatment|doctor|teacher|centre)|with this \(school|main care arrangement|satisfied are you with the effect|with the way that you re|satisfied (?:are you )?with your current (?:job|work|childcare|care|arrangement|employment)|career progress|job satisfaction|satisfied are you with (?:the )?(?:response|help)|satisfied are you with: the school|satisfied are you with your bab|satisfied (?:are you )?with your relationship|arrangements you have made",
      'PC_FAM': r"not currently in paid work",
      'DM_PU': r"reacts strongly to separation|dependent on me",
      'DM_GM': r"betting|gambl|lotter",
      'DM_ST': r"kidscreen"}
# KIDSCREEN is a quality-of-life measure: 'screen' inside the name triggered the screen-time keyword. Re-assign to WB_LS.
d = d.reset_index(drop=True)
ks = (d.construct == 'DM_ST') & (d.text.str.contains('kidscreen', case=False) | d.instrument.str.contains('kidscreen', case=False))
d = pd.concat([d, d[ks].assign(construct='WB_LS').drop_duplicates()], ignore_index=True)
drop = pd.Series(False, index=d.index)
for c, pat in FP.items():
    drop |= (d.construct == c) & (d.text.str.contains(pat, case=False, regex=True) | (d.instrument.str.contains(pat, case=False, regex=True) if c == 'DM_ST' else False))
RFP = os.path.join(ROOT, 'data', 'removed_false_positives.csv')
prev = pd.read_csv(RFP).fillna('') if os.path.exists(RFP) else pd.DataFrame()
pd.concat([prev, d[drop]]).astype(str).drop_duplicates().to_csv(RFP, index=False)  # cumulative audit trail
print('false-positive rows removed:', int(drop.sum()), d[drop].groupby(['study', 'construct']).size().to_dict())
d = d[~drop]

nd = pd.DataFrame(new)
d = pd.concat([d, nd], ignore_index=True)
write_lex(d)
after = d.groupby('study').size().to_dict()
print('lexicon rows before/after:', {k: (before.get(k), after.get(k)) for k in sorted(set(before) | set(after))})
print('TESS table:', tess_stats, '| UKHLS targeted rows used:', ustats)

# ---------------------------------------------------------------- rebuild aggregates (same logic as build_data.py)
D = json.load(open(APP))
d = d.fillna('')
def yr(x):
    m = [int(a) for a in re.findall(r'(20\d\d|19\d\d)', str(x))]
    return (min(m) + max(m)) / 2 if m else None
def rng(x):
    if isinstance(x, (int, float)) and x == x: return (float(x), float(x))
    m = [float(a) for a in re.findall(r'\d+(?:\.\d+)?', str(x))]
    if not m: return (None, None)
    if '+' in str(x): return (m[0], m[0])
    return (min(m[:2]), max(m[:2]))
d['alo'] = d['age'].apply(lambda x: rng(x)[0]); d['ahi'] = d['age'].apply(lambda x: rng(x)[1])
d['yearn'] = d['years'].apply(yr)
wkey = lambda s: (re.sub(r'\d+(\.\d+)?', '', s), float((re.findall(r'\d+(?:\.\d+)?', s) or ['0'])[0]), s)
items, atlas = {}, {}
for (st, c), g in d.groupby(['study', 'construct']):
    agg = []
    for (var, text), gg in g.groupby(['var', 'text'], sort=False):
        ui = list(dict.fromkeys(x for x in gg.instrument if x))
        agg.append(dict(v=str(var), t=text, i=sorted(set(gg.informant)), ins=(' → '.join(ui[:4]) + (' …' if len(ui) > 4 else '')) if st == 'TESS' else (ui[0] if ui else ''), w=sorted(set(gg.wave), key=wkey),
                        a=[gg.alo.min(), gg.ahi.max()] if gg.alo.notna().any() else None, y=sorted(set(str(x) for x in gg.years if x))[:6],
                        co=sorted(set(gg.cohort)), src=gg.source.iloc[0], lvl=gg.level.iloc[0], tm=gg.timing.iloc[0]))
    agg.sort(key=lambda r: (-('Youth' in r['i']), -len(r['w'])))
    instruments = sorted(set(g.instrument) - {''})
    atlas.setdefault(st, {})[c] = dict(n=len(agg), ninst=len(instruments), inst=instruments[:12],
                                       waves=sorted(set(g.wave), key=wkey), inf=sorted(set(g.informant)),
                                       age=[g.alo.min(), g.ahi.max()] if g.alo.notna().any() else None,
                                       yr=[g.yearn.min(), g.yearn.max()] if g.yearn.notna().any() else None)
    items[st + '|' + c] = agg[:60]
NO_TL = re.compile(r'PEACH|Twitter|Wellbeing App|household|derived')
tl = []
for (st, coh, w), g in d.groupby(['study', 'cohort', 'wave']):
    y = g.yearn.dropna()
    if not len(y) or NO_TL.search(coh) or float(y.median()) < 1999.5: continue
    amin = g.alo.min() if g.alo.notna().any() else None; amax = g.ahi.max() if g.ahi.notna().any() else None
    tl.append(dict(s=st, co=coh, w=w, a=[amin, amax], y=float(y.median()), c={c: sorted(set(gg.informant)) for c, gg in g.groupby('construct')}))
# keep the old unchanged-study aggregates identical where the inputs did not change (sanity check)
for st in D['atlas']:
    if st in ('TESS', 'Understanding Society'): continue
    for c, a in D['atlas'][st].items():
        if atlas.get(st, {}).get(c, {}).get('n') != a['n']:
            print('  count changed (false-positive clean-up):', st, c, a['n'], '->', atlas.get(st, {}).get(c, {}).get('n'))
D['atlas'], D['items'], D['timeline'] = atlas, items, tl

# ---------------------------------------------------------------- study metadata
for s in D['studies']:
    if s['id'] == 'TESS':
        s.update(status='instrument', dict_file='TESS instruments T1-T10_CleanVersion.docx (revised 27 Oct 2026)',
                 design='Community cohort (born 2003–04); biennial T1 4y → T10 22y (2007–2026)',
                 note=('Instrument overview (English): %d rows × %d columns (instrument label + 10 time points, T1 4y to T10 22y); '
                       '%d of %d time-point cells filled. Every row now carries a cell for each time point, so instruments are placed at the '
                       'correct wave and age. Digital media: screen-use interview (T3–T10), Internet Gaming Disorder Interview (IGDI, T4–T10), '
                       'semi-structured clinical IGD interview (T4–T8; Wichstrøm et al., 2026, Addiction), social media use (T4–T10), FoMO (T7–T10), '
                       'cyberbullying (T6–T10) and objective 7-day app time-use screenshots (T7–T10). Retrospective objective app-use records matched '
                       'to each wave are confirmed by the study lead but not itemised in the overview; data-donation streams (social media and AI '
                       'interaction records) are planned. Item-level wording still needs the TESS codebook.')
                      % (tess_stats['rows'], tess_stats['cols'], tess_stats['filled'], (tess_stats['rows'] - 1) * 10))
    if s['id'] == 'Understanding Society':
        s.update(status='full', dict_file=U_SRC,
                 design='Household panel: BHPS 1991–2008, UKHLS 2009– (W1–W15); youth 10–15, adults 16+; Innovation Panel, COVID-19 Study, PEACH',
                 note=('Targeted harmoniser dictionary (condensed from the 50,067-stem full dictionary to the 11 Atlas constructs): '
                       '%d item × construct rows, %d variable stems, across UKHLS main survey, harmonised BHPS, Innovation Panel, COVID-19 Study, '
                       'PEACH, IP Wellbeing App and the IP Twitter linkage. Informants: Y youth self-completion 10–15, P parent/proxy about the child, '
                       'A adult self-report (youth slice 16–25 at analysis), H household, S linked Twitter/X data. Adult items were screened by keyword '
                       'only, so rarely worded adult items may be missing. BHPS waves before 2000 are listed in Atlas and Item compare but not plotted on Two clocks.')
                      % (ustats['rows'], ustats['stems']))

for s_ in D['studies']:
    if s_['id'] == 'AStRA':
        s_['note'] = ('Dictionary rebuilt from the three SPSS output files. Ages: C1 (2005–07) and C2 (2013–15) start in the first grade of Gymnasium, '
                      'M age 12.6 at W1 (Motti-Stefanidi et al., 2017, N = 1,057 and 1,052), with annual waves (≈12.6, 13.6, 14.6); C3 (2022–23) spans '
                      'Gymnasium grades 1–3 at W1 (≈12–15). No screen-time items in C1–C2; C3 has internet-quality and parent–adolescent conflict over computer/phone time.')
    if s_['id'] == 'ABCD':
        s_['note'] = ('Waves are now item-level where the information exists: (1) wave presence in the data (no counts kept) for tables run through '
                      'scripts/abcd_item_waves_from_data.py (so far: parent Screen Time Questionnaire, Release 5.1, Y0–Y4), (2) the REDCap branching '
                      'logic of the ABCD 7.0 dictionary (1,124 items with event conditions). All other items keep table-level coverage, which can '
                      'over-state waves for items added later (e.g. youth social-media and video-game addiction items).')
# ---------------------------------------------------------------- anchors (re-checked against the revised sources)
for a in D['anchors']:
    if a['inst'].startswith('Strengths and Difficulties'):
        a['where'] = [w for w in a['where'] if w[0] not in ('TESS', 'Understanding Society')] + [['TESS', 'Parent and teacher report at T1 (4y); CBCL/TRF from T2'],
                                                                  ['Understanding Society', 'Youth self-report 10–15 (odd waves W1–W15); parent report on child']]
    if a['inst'].startswith('Rosenberg'):
        a['where'] = [w for w in a['where'] if w[0] != 'Understanding Society'] + [['Understanding Society', 'Youth 10–15, Rosenberg-type ypest items (BHPS youth and UKHLS)']]
    if a['inst'].startswith('Parental Bonding'):
        a['where'] = [['AStRA', 'C2, W1–W3, mother and father versions'], ['TESS', 'Youth report T6–T10 (14–22y), care + control/overprotection']]
    if a['inst'].startswith('MCS 7-item'):
        a['where'] = [['MCS', 'Sweep 6 (14y)'], ['TESS', 'Youth report T6–T10 (14–22y): "UK Millennium study (7 item)"']]
    if a['inst'].startswith('Single-item life'):
        a['where'] = [w for w in a['where'] if w[0] != 'Understanding Society'] + [['Understanding Society', 'Adults: satisfaction with life overall (sclfsato); youth: happiness with life as a whole (yphlf)']]
D['anchors'] = [a for a in D['anchors'] if not a['inst'].startswith('Short Warwick')]
if True:
    D['anchors'].append(dict(inst='Short Warwick-Edinburgh Mental Wellbeing Scale (SWEMWBS)', con='WB_LS',
                             where=[['Understanding Society', 'Adults, W1, W4, W7, W10, W13 (swemwbs_dv)'], ['GUiNZ', 'Child self-report at 15y, WBE1–WBE7 (7 items, SWEMWBS wording, last 2 weeks; full dictionary)']],
                             note='Youth (GUiNZ, 15y) vs adult (UKHLS, 16+) respondents: align on age band (16–17 in UKHLS) before linking; check response options item by item.'))
if not any(a['inst'].startswith('Internet Gaming Disorder') for a in D['anchors']):
    D['anchors'].append(dict(inst='Internet Gaming Disorder (DSM-5 Section III criteria)', con='DM_PU',
                             where=[['TESS', 'IGDI T4–T10 and clinical IGD interview T4–T8'], ['ABCD', 'Video-game addiction items in the Screen Time Questionnaire (Y2+)']],
                             note='Same DSM-5 criteria, different formats (clinical interview vs self-report questionnaire): route c (threshold) or a, not d.'))

# ---------------------------------------------------------------- ADII
adii = pd.ExcelFile(os.path.join(R, 'adii_dict.xlsx'))
v24 = pd.read_excel(adii, 'Values_2024')
legacy = {}
ws = pd.read_excel(os.path.join(R, 'adii_webtables_2020_state.xlsx'), sheet_name='Australia', header=None)
rows = ws.values.tolist(); i = 0
while i < len(rows):
    r0 = rows[i]
    if str(r0[0]).strip().isdigit() and len(str(r0[0]).strip()) == 4 and r0[1] == 'Australia':
        yv = int(str(r0[0]).strip()); hdr = [str(x).replace('*', '').strip() if x == x and x is not None else None for x in r0]
        secn = None
        for b in rows[i + 1:i + 17]:
            lab = b[0] if b[0] == b[0] else None
            if lab in ('ACCESS', 'AFFORDABILITY', 'DIGITAL ABILITY'): secn = lab; continue
            key = 'TOTAL' if lab == 'DIGITAL INCLUSION INDEX' else (secn if lab is None and secn and b[1] == b[1] else None)
            if not key: continue
            for j, h in enumerate(hdr):
                if j and h:
                    try:
                        fv = float(b[j])
                        if fv == fv: legacy.setdefault(key, {}).setdefault(h, {})[yv] = fv
                    except (TypeError, ValueError): pass
        i += 17
    else: i += 1
DIMN = {'TOTAL': 'ADII score', 'ACCESS': 'Access', 'AFFORDABILITY': 'Affordability', 'DIGITAL ABILITY': 'Digital Ability'}
aius = {}
for _, r in v24.iterrows():
    if r['Geography/subgroup type'] == 'National':
        aius.setdefault(r['Measure'], {})[int(r['Data year'])] = float(r['Score (0-100)'])
ctx_rows = []
def crow(ind, year, val, label, dim, unit, src):
    ctx_rows.append(dict(iso3='AUS', year=year, indicator_id=ind, value=val, unit=unit, dimension=dim, label=label, source=src, retrieved='2026-10-27'))
LSRC = 'ADII legacy series (Roy Morgan Single Source), 2020 webtables'
for key, ind, dim in [('TOTAL', 'adii_legacy_total', 'Access'), ('ACCESS', 'adii_legacy_access', 'Access'),
                      ('AFFORDABILITY', 'adii_legacy_afford', 'Access'), ('DIGITAL ABILITY', 'adii_legacy_ability', 'Participation')]:
    for y, v in sorted(legacy[key]['Australia'].items()):
        crow(ind, y, v, 'Digital inclusion (ADII legacy 2014–2020): %s (AUS)' % DIMN[key], dim, 'index 0–100 (adults 18+)', LSRC)
ASRC = 'ADII / Australian Internet Usage Survey, dashboard export (data years; 2020 = pilot)'
for meas, ind, dim in [('ADII score', 'adii_aius_total', 'Access'), ('Access', 'adii_aius_access', 'Access'),
                       ('Affordability', 'adii_aius_afford', 'Access'), ('Digital Ability', 'adii_aius_ability', 'Participation')]:
    for y, v in sorted(aius.get(meas, {}).items()):
        crow(ind, y, v, 'Digital inclusion (ADII 2020– AIUS series): %s (AUS)' % meas, dim, 'index 0–100 (adults 18+)', ASRC)
with open(os.path.join(ROOT, 'data', 'context', 'adii_australia.csv'), 'w', newline='') as f:
    wr = csv.DictWriter(f, fieldnames=list(ctx_rows[0])); wr.writeheader(); wr.writerows(ctx_rows)
geo24 = [dict(type=r['Geography/subgroup type'], cat=str(r['Category']), v=float(r['Score (0-100)'])) for _, r in v24.iterrows()
         if r['Measure'] == 'ADII score' and int(r['Data year']) == 2024]
D['adii'] = dict(
    about=('Australian Digital Inclusion Index (ADII): adult (18+) population index, 0–100, across Access, Affordability and Digital Ability. '
           'Two series that must not be spliced: the legacy Roy Morgan series (2014–2020) and the Australian Internet Usage Survey series '
           '(2020 pilot, 2021, 2022, 2024). The 2024 Affordability measure was redesigned, so 2024 totals are not comparable with earlier totals. '
           'The current AIUS series surveys adults 18+ only (the legacy series reports an age 14–24 band), so ADII describes the household and parental digital environment of Australian cohort members (LSAC, HILDA, Ten to Men), not the young person’s own use.'),
    cite=('Thomas, J., McCosker, A., Parkinson, S., Hegarty, K., Featherstone, D., Kennedy, J., Ormond-Parker, L., Morrison, K., Rea, H., & Ganley, L. '
          '(2025). Measuring Australia’s Digital Divide: Australian Digital Inclusion Index 2025. ADM+S Centre of Excellence for Automated '
          'Decision-Making and Society, RMIT University, Swinburne University of Technology, and Telstra. CC BY-NC-SA 4.0.'),
    link='Join to cohort records by data year × state/territory × capital city vs rest of state × remoteness area (data year, not publication year). '
         'Geography-only joins as the primary analysis; subgroup-matched scores (e.g. couple with children × income quintile) as sensitivity analyses.',
    legacy={k: {g: {str(y): v for y, v in sorted(s.items())} for g, s in grp.items()} for k, grp in legacy.items()},
    aius={m: {str(y): v for y, v in sorted(s.items())} for m, s in aius.items()},
    geo2024=geo24,
    source_folder='Google Drive › Data Dictionaries › Australian Digital Inclusion Index (reports 2016–2025, technical reports, webtables, 85 dashboard exports)')
D['generated'] = TODAY
json.dump(D, open(APP, 'w'), default=lambda o: None, allow_nan=False)
print('ADII context rows:', len(ctx_rows), '| geo 2024 rows:', len(geo24), '| legacy groups:', list(legacy['TOTAL']))
print('timeline points:', len(tl), '| items MB', round(len(json.dumps(items)) / 1e6, 2))
