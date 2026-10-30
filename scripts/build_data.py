import os
import pandas as pd, json, re, collections
S = os.environ.get('GCHN_WORKDIR', '.')
d = pd.read_csv(S + '/lexicon_candidates.csv', low_memory=False).fillna('')
itu = json.load(open(S + '/ctx/itu.json'))

CON = {
 'WB_LS': ['Wellbeing', 'Life satisfaction & subjective wellbeing'],
 'WB_MOOD': ['Wellbeing', 'Emotional wellbeing (low mood, worry)'],
 'WB_SE': ['Wellbeing', 'Self-esteem & self-worth'],
 'DM_ST': ['Digital media use', 'Screen time'],
 'DM_SM': ['Digital media use', 'Social media & online communication'],
 'DM_GM': ['Digital media use', 'Gaming'],
 'DM_PU': ['Digital media use', 'Problematic / compulsive use'],
 'DM_DEV': ['Digital media use', 'Device access & ownership'],
 'PC_REL': ['Proximate context', 'Parent–child relationship'],
 'PC_MON': ['Proximate context', 'Parental monitoring & media rules'],
 'PC_FAM': ['Proximate context', 'Family functioning & climate'],
}
STUDIES = [
 dict(id='ABCD', name='ABCD Study', country='USA', iso='USA', design='Cohort (9–10y at baseline, 2016–18; annual)', status='full',
      dict_file='ABCD_7.0_dictionary_with_waves.xlsx', note='Wave coverage in this dictionary is table-level: items added to a table later (e.g. social-media addiction items) are listed at every wave. Treat item waves as over-inclusive until checked against the events file.',
      geo='Site (21), state – via restricted geocodes'),
 dict(id='LSAC', name='LSAC (Growing Up in Australia)', country='Australia', iso='AUS', design='Cohort: B (0–1y) & K (4–5y) in 2004; biennial', status='partial',
      dict_file='LSAC-Data-Dictionary-Release-10.1.xlsx', note='The Release 10.1 dictionary (11 MB) is over the Drive connector limit. Only Wave 1 rows were retrieved; later-wave items come from the GUiNZ–ABCD–LSAC crosswalk and are not shown here. Full load pending.',
      geo='State, remoteness (general release)'),
 dict(id='AStRA', name='AStRA (Athens)', country='Greece', iso='GRC', design='School cohorts: C1 2005–07, C2 2013–15, C3 2022–23 (migrant-youth)', status='full',
      dict_file='AStRA1/2/3-data-dictionary.spv (SPSS output) → new XLSX', note='Dictionary rebuilt from the three SPSS output files in this session. Age at wave not yet tabulated (labels give school grade only). No screen-time items in C1–C2; C3 has internet-quality and parent–adolescent conflict over computer/phone time.',
      geo='Athens schools (school code)'),
 dict(id='MCS', name='Millennium Cohort Study', country='UK', iso='GBR', design='Birth cohort 2000–02; sweeps 9m → 23y', status='full',
      dict_file='MCS_Full_Data_Dictionary_Harmoniser_2026-10-13.xlsx', note='', geo='UK country, Government Office Region (EUL)'),
 dict(id='TESS', name='Trondheim Early Secure Study', country='Norway', iso='NOR', design='Community cohort (born 2003–04); biennial T1 4y → T10 22y', status='instrument',
      dict_file='TESS instruments T1-T10_CleanVersion.docx', note='Instrument overview only (English, a few Norwegian notes). Rows have 9 cells against 10 time-point headers, so the wave of each instrument is ambiguous. Needs an item-level dictionary.',
      geo='Trondheim (single municipality)'),
 dict(id='GUI', name='Growing Up in Ireland', country='Ireland', iso='IRL', design="Cohort '98 (9y in 2007) and '08 (9m in 2008)", status='full',
      dict_file='GUI_All_Cohorts_Overview_and_Alignment.xlsx', note="Cohort '24 not yet in the variable list.", geo='Region (restricted for finer levels)'),
 dict(id='GUiNZ', name='Growing Up in New Zealand', country='New Zealand', iso='NZL', design='Birth cohort 2009–10; antenatal → 15y', status='crosswalk',
      dict_file='GUiNZ – ABCD – LSAC indicative crosswalk (Drive sheet)', note='The full dictionary (DataDictionary_All_v1.03.xlsx, 9 MB) did not come through the connector. Rows shown are from the crosswalk sheet, at measure level.',
      geo='Region/DHB (via data access)'),
 dict(id='KCYPS', name='KCYPS 2018 (Korea)', country='South Korea', iso='KOR', design='E4 (≈10y) and M1 (≈13y) cohorts in 2018; annual W1–W7', status='full',
      dict_file='KCYPS 2018 – Variable Dictionary (English, W1–W7)', note='Ages are approximate, from school grade.', geo='Province (school & residence)'),
 dict(id='PSKC', name='Panel Study on Korean Children', country='South Korea', iso='KOR', design='Births Apr–Jul 2008; annual W1–W16 (≈15y)', status='construct',
      dict_file='PSKC_Data_Dictionary.xlsx', note='Construct × wave level (English); item level needs the Korean codebook.', geo='Region (6 sampling regions)'),
 dict(id='Ten to Men', name='Ten to Men', country='Australia', iso='AUS', design='Males 10–55 in 2013–14 (boys 10–17); W1–W5', status='full',
      dict_file='Ten to Men 2025 Release Data Dictionary.xlsx', note='Includes adult men; youth slice = boys cohort. W2 years not stated in the dictionary (verify).', geo='State, SA1/SA2 (restricted)'),
 dict(id='Understanding Society', name='Understanding Society (UKHLS)', country='UK', iso='GBR', design='Household panel 2009–; youth questionnaire 10–15, adults 16+', status='partial',
      dict_file='UKHLS digital-engagement sheet (Drive)', note='Only the digital-engagement rows were retrieved; the full harmoniser dictionary (38 MB) is over the connector limit.',
      geo='Country, GOR, LSOA (special licence)'),
 dict(id='HILDA', name='HILDA', country='Australia', iso='AUS', design='Household panel 2001– (annual); self-report 15+', status='full',
      dict_file='HILDA_R24_Data_Dictionary.xlsx', note='Youth slice (15–24) to be defined at analysis. Child items come from one adult (household questionnaire).', geo='State, section of state'),
]
sid = {s['id']: s for s in STUDIES}

def num(x):
    if isinstance(x, (int, float)) and x == x: return float(x)
    m = re.findall(r'\d+(?:\.\d+)?', str(x))
    if not m: return None
    v = [float(a) for a in m[:2]]
    return sum(v) / len(v)

def yr(x):
    m = [int(a) for a in re.findall(r'(20\d\d|19\d\d)', str(x))]
    if not m:
        m2 = re.findall(r'20\d\d(?:\.\d)?', str(x))
        return None
    return (min(m) + max(m)) / 2

# ---------- items: aggregate by study/construct/var/text ----------
def rng(x):
    if isinstance(x, (int, float)) and x == x: return (float(x), float(x))
    m = [float(a) for a in re.findall(r'\d+(?:\.\d+)?', str(x))]
    if not m: return (None, None)
    if '+' in str(x): return (m[0], m[0])
    return (min(m[:2]), max(m[:2]))
d['alo'] = d['age'].apply(lambda x: rng(x)[0]); d['ahi'] = d['age'].apply(lambda x: rng(x)[1])
d.loc[d.study == 'TESS', ['alo', 'ahi']] = None
d['agen'] = d['alo']
d['yearn'] = d['years'].apply(yr)
items = {}
atlas = {}
for (st, c), g in d.groupby(['study', 'construct']):
    agg = []
    for (var, text), gg in g.groupby(['var', 'text'], sort=False):
        agg.append(dict(v=str(var), t=text, i=sorted(set(gg.informant)), ins=gg.instrument.iloc[0], w=sorted(set(gg.wave), key=lambda s: (len(s), s)),
                        a=[gg.alo.min(), gg.ahi.max()] if gg.alo.notna().any() else None, y=sorted(set(str(x) for x in gg.years if x))[:6],
                        co=sorted(set(gg.cohort)), src=gg.source.iloc[0], lvl=gg.level.iloc[0], tm=gg.timing.iloc[0]))
    # rank: youth first, then waves covered
    agg.sort(key=lambda r: (-('Youth' in r['i']), -len(r['w'])))
    instruments = sorted(set(g.instrument) - {''})
    atlas.setdefault(st, {})[c] = dict(n=len(agg), ninst=len(instruments), inst=instruments[:12],
                                       waves=sorted(set(g.wave), key=lambda s: (len(s), s)), inf=sorted(set(g.informant)),
                                       age=[g.alo.min(), g.ahi.max()] if g.alo.notna().any() else None,
                                       yr=[g.yearn.min(), g.yearn.max()] if g.yearn.notna().any() else None)
    items[st + '|' + c] = agg[:60]

# ---------- timeline points ----------
tl = []
for (st, coh, w), g in d.groupby(['study', 'cohort', 'wave']):
    y = g.yearn.dropna()
    if not len(y) or g.study.iloc[0] == 'TESS': continue
    amin = g.alo.min() if g.alo.notna().any() else None; amax = g.ahi.max() if g.ahi.notna().any() else None
    cons = {}
    for c, gg in g.groupby('construct'):
        cons[c] = sorted(set(gg.informant))
    tl.append(dict(s=st, co=coh, w=w, a=[amin, amax], y=float(y.median()), c=cons))

# ---------- anchors (verified against source dictionaries in this session) ----------
anchors = [
 dict(inst='Strengths and Difficulties Questionnaire (SDQ)', con='WB_MOOD', where=[
   ['MCS', 'Sweeps 2–7 (mainly parent report)'], ['GUI', "Cohort '98 W1–W3; Cohort '08 W2–W6"], ['AStRA', 'C1, C2, C3 (adolescent self-report)'],
   ['GUiNZ', 'Mother 2y–15y; child 12y (crosswalk)'], ['TESS', 'Parent & teacher report (overview)']],
   note='Strongest item-level anchor across 5 studies. Informant differs (parent vs self vs teacher): never pool across informants (Table 2, e).'),
 dict(inst='Rosenberg Self-Esteem Scale', con='WB_SE', where=[
   ['MCS', 'Sweeps 6–7 (cohort member); Sweep 1 = mother’s own self-esteem'], ['GUI', "Cohort '98 W3–W4; Cohort '08 W6"], ['AStRA', 'C1, C2, C3 (self-report)']],
   note='Same instrument, but item count and response options must be checked per study before IRT linking.'),
 dict(inst='Parental Bonding Instrument (PBI)', con='PC_REL', where=[['AStRA', 'C2, W1–W3, mother and father versions'], ['TESS', 'Youth report, adolescence (overview)']],
   note='Direct anchor Greece–Norway for the parent–child relationship.'),
 dict(inst='Short Mood and Feelings Questionnaire (SMFQ)', con='WB_MOOD', where=[['GUI', "Cohort '98 W2; Cohort '08 W6"], ['LSAC', 'Adolescence (crosswalk, not dictionary-verified)']],
   note='Not detected in the MCS harmoniser-edition labels: check MCS questionnaires before claiming it.'),
 dict(inst='Kessler K6/K10', con='WB_MOOD', where=[['MCS', 'Parent, sweeps 2–8'], ['GUI', 'Parent, both cohorts'], ['HILDA', 'K10 self-report, odd waves 7–23']],
   note='Parent-wellbeing measure in MCS/GUI (proximate context); youth self-report only in HILDA.'),
 dict(inst='Single-item life satisfaction', con='WB_LS', where=[['HILDA', 'All waves (0–10)'], ['MCS', 'Sweeps 6/8; 0–10 at 23y'], ['GUI', "Cohort '98 W3–W5"], ['KCYPS', 'Youth scale items'], ['GUiNZ', 'Cantril ladder 15y']],
   note='Shared concept, different stems and scales (0–10, 1–7, ladder): route c or a, not d.'),
 dict(inst='MCS 7-item wellbeing grid ("How happy are you with…")', con='WB_LS', where=[['MCS', 'Sweep 6 (14y)'], ['TESS', 'Youth report (overview lists "UK Millennium study (7 item)")']],
   note='TESS adopted the MCS items, which makes this a rare cross-country anchor to verify item by item.'),
]

# ---------- worked examples for the planner ----------
json.dump(dict(constructs=CON, studies=STUDIES, atlas=atlas, items=items, timeline=tl, itu=itu, anchors=anchors,
               generated='22 Oct 2026'), open(S + '/gchn_data.json', 'w'), default=lambda o: None)
print(len(json.dumps(items)) / 1e6, 'MB items;', len(tl), 'timeline points')
