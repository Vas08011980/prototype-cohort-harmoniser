import os
"""Build the candidate lexicon for the harmoniser prototype.
Every row keeps its source file. Construct assignment = keyword screen (candidate, not verified)."""
import re, json, csv, collections
import pandas as pd

S = os.environ.get('GCHN_WORKDIR', '.')
R = S + '/raw'

CONSTRUCTS = {
 'WB_LS': ('Wellbeing', 'Life satisfaction & subjective wellbeing'),
 'WB_MOOD': ('Wellbeing', 'Emotional wellbeing (low mood, worry)'),
 'WB_SE': ('Wellbeing', 'Self-esteem & self-worth'),
 'DM_ST': ('Digital media use', 'Screen time'),
 'DM_SM': ('Digital media use', 'Social media & online communication'),
 'DM_GM': ('Digital media use', 'Gaming'),
 'DM_PU': ('Digital media use', 'Problematic / compulsive use'),
 'DM_DEV': ('Digital media use', 'Device access & ownership'),
 'PC_REL': ('Proximate context', 'Parent–child relationship'),
 'PC_MON': ('Proximate context', 'Parental monitoring & media rules'),
 'PC_FAM': ('Proximate context', 'Family functioning & climate'),
}
MEDIA = r"(internet|online|phone|smart ?phone|video ?games?|gaming|games?\b|social media|social network|screens?\b|media|computer|tablet|youtube|tik ?tok|instagram|facebook|snapchat)"
TEXT_RE = {
 'WB_LS': r"life satisfaction|satisf\w* with (your |my |his |her |their )?(own )?life|satisfied with life|how (happy|satisfied) (are you|is|do you feel)|happy (are you )?with (your|the way|their|my) (life|look|family|friends|school|appearance)|close to (my|your) ideal|quality of life|cantril|best possible life|life as a whole|feel(ing)? (good|positive) about (my|your) life|optimistic about the future|personal wellbeing",
 'WB_MOOD': r"mood and feelings|miserable|unhappy|\bsad\b|depress\w*|hopeless|worthless|worr(y|ied|ies)|nervous|anxious|anxiety|feel(ing|s)? (down|blue|low)|cried|crying|felt down|lonely|loneliness|no good|nothing was fun|fearful|scared|tense",
 'WB_SE': r"self-?esteem|self-?worth|good about (myself|yourself|himself|herself)|satisfied with (myself|yourself)|good qualities|proud of (myself|yourself)|feel useless|i am a failure|positive attitude toward (myself|yourself)|like (myself|yourself)",
 'DM_ST': r"screen time|screens?\b(?! ?shar)|television|\btv\b|watch\w* (tv|television|videos?|dvds?|programmes|programs|shows|movies)|hours.{0,50}(computer|tablet|phone|internet|online)|computer (use|time)|use (a|the) computer|time online|internet use|use the internet|go online|on the internet|online for|browsing",
 'DM_SM': r"social media|social network|facebook|instagram|snapchat|tik ?tok|twitter|youtube|text messag\w*|texting|send\w* texts|instant messag\w*|chat\w* (online|with friends)|video ?chat|cyber ?bull\w*|online friends|friends online|sns\b",
 'DM_GM': r"video ?games?|computer games?|electronic games?|gaming|games? console|play\w* (online |computer |video )?games|online games?|nintendo|playstation|xbox",
 'DM_PU': r"(addict\w*|compulsive|problematic|dependen\w*|hard to stop|can'?t stop|unable to stop|lose track of time|withdrawal|preoccup\w*|tried to (cut down|reduce)|get in the way|neglect).{0,80}" + MEDIA + "|" + MEDIA + r".{0,80}(addict\w*|compulsive|problematic|dependen\w*|hard to stop|can'?t stop|lose track of time|withdrawal|preoccup\w*|cut down|get in the way)|spend a lot of time thinking about|planning my use|urge to use|use .{0,40} to forget|tried to cut down|restless or troubled|neglect\w* .{0,30}(homework|school|chores)|gaming disorder|fear of missing out|\bfomo\b|bergen|overdependence|mobile phone involvement",
 'DM_DEV': r"smart ?phone|mobile phone|cell ?phone|own (a |their own |his own |her own )?(phone|tablet|computer|laptop)|internet (access|connection)|access to the internet|computer at home|home computer|broadband|ipad|games? console in",
 'PC_REL': r"warmth|praise|affection\w*|hostil\w*|close(ness)? (to|with) (your |his |her |their )?(mother|father|parents?|mum|dad|child)|get(s)? (along|on) with (your |his |her |their )?(mother|father|parents?|mum|dad|child)|relationship (with|between) (you and )?(your |his |her |their )?(mother|father|parents?|child|mum|dad)|parent.?child (relation\w*|conflict|interaction|closeness)|argu\w* with (your |his |her |their )?(mother|father|parents?|mum|dad|child)|talk (to|with) (your |his |her )?(mother|father|parents?|mum|dad) about|disagree\w* .{0,30}parents|understands my problems|emotionally cold|feel unwanted|enjoy\w* talking (with|to) (me|you)|hugs?\b|cuddl\w*|shout\w* at|harsh",
 'PC_MON': r"monitor\w*|know\w* where|knows who|parents? know|rules? (about|on|for|regarding).{0,40}(tv|television|screen|internet|computer|games?|phone|media|online)|limit\w*.{0,30}(screen|tv|television|internet|games?|phone|computer)|parental controls?|supervis\w*|curfew|disclos\w*|less time on the computer|what (you|they) do online",
 'PC_FAM': r"family (function\w*|conflict|climate|environment|cohesion|relationships?|support|routines?|meals?|activities)|family members|as a family|fight\w* in (my|our|the) family|argu\w* (in|between) (the )?(family|parents)|parents (fight|argue|disagree)|conflict between (you and your partner|parents)|interparental|quarrel",
}
INST_RE = {
 'WB_LS': r"life satisfaction|wemwbs|warwick|swemwbs|kidscreen|personal wellbeing index|\bpwi\b|swls|satisfaction with life|wellbeing ?grid|positive affect",
 'WB_MOOD': r"mood and feelings|\bs?mfq\b|ces-?d|kessler|\bk6\b|\bk10\b|phq|gad-7|promis.{0,10}(anx|dep)|depress|anxiety",
 'WB_SE': r"rosenberg|rses|self-?esteem|harter|sppa|self.?perception",
 'DM_ST': r"screen ?time|media use|time.?use.{0,10}screen",
 'DM_SM': r"social media|cyberbull",
 'DM_GM': r"video game|gaming",
 'DM_PU': r"addiction|igdi|fomo|mobile phone involvement|problematic.{0,20}(use|media)|smartphone.{0,20}dependen|\bdependency\b",
 'DM_DEV': r"device",
 'PC_REL': r"parental bonding|\bpbi\b|parental behavio\w* inventory|\bcrpbi\b|alabama parenting|\bapq\b|network of relationships|\bnri\b|warmth|parent.?child relationship|parenting style",
 'PC_MON': r"parental monitoring|monitoring|youth disclosure|parental mediation|media rules",
 'PC_FAM': r"family environment scale|faces|family assessment device|\bfad\b|family conflict|family functioning|cohesion",
}
EXCL = re.compile(r"heroin|opium|dope|substance|homeless|screener|screening|sunscreen|screen shar|obsess|compulsions?\b|ocd|drugs?\b|alcohol|tobacco|cigarette|cannabis|marijuana|vap(e|ing)|grams|food|weight or shape|brain injury|diagnos\w*|doctor|medicat\w*|prescri\w*|nurse|hospital|teacher rating|keystroke|keyboard|app store category|google play", re.I)
TRE = {k: re.compile(v, re.I) for k, v in TEXT_RE.items()}
IRE = {k: re.compile(v, re.I) for k, v in INST_RE.items()}

def classify(text, instrument=''):
    if not isinstance(text, str) or len(text) < 4: return []
    full = text + ' ' + (instrument or '')
    if EXCL.search(full): return []
    out = []
    for k in TEXT_RE:
        if TRE[k].search(text) or (instrument and IRE[k].search(instrument) and len(text) > 8):
            out.append(k)
    return out

rows = []  # dicts
def add(study, cohort, wave, years, age, informant, var, text, instrument, source, level='item', extra=None, force=None):
    cs = classify(text, instrument)
    if force: cs = sorted(set(cs) | set(force))
    for c in cs:
        rows.append(dict(study=study, cohort=cohort, wave=str(wave), years=years, age=age, informant=informant,
                         var=var, text=text.strip()[:400], instrument=(instrument or '')[:120], construct=c,
                         source=source, level=level, **(extra or {})))

def inf_map(s):
    s = str(s).lower()
    if any(w in s for w in ['teacher', 'principal', 'school']): return 'Teacher/School'
    if any(w in s for w in ['parent', 'caregiver', 'mother', 'father', 'guardian', 'household questionnaire', 'household form', 'pcg', 'partner']): return 'Parent'
    if any(w in s for w in ['child', 'young', 'youth', 'self', 'adolescent', 'cohort member', 'cm ', 'individual']): return 'Youth'
    if 'derived' in s: return 'Derived'
    return 'Other'

# ---------- ABCD ----------
a = pd.read_excel(R + '/abcd.xlsx')
a = a[~a['domain'].isin(['Imaging', 'MR Spectroscopy', 'Genetics', 'Linked External Data', 'ABCD (General)', 'Endocannabinoid'])]
a_ears = a[a['table_label'].str.contains('EARS', na=False)]
a = a[~a['table_label'].str.contains('EARS', na=False)]
for tl, grp in a_ears.groupby('table_label'):
    codes = sorted({c.strip() for wc in grp['wave_codes'].astype(str) for c in wc.split(';') if re.match(r'\d\d[AM]', c.strip())})
    for c in codes:
        k = int(c[:2])
        rows.append(dict(study='ABCD', cohort='ABCD', wave='Y%d' % k, years='%d–%d' % (2016 + k, 2018 + k), age=round(9.9 + k, 1), informant='Passive sensing',
                         var=grp['table_name'].iloc[0], text='%s (%d passive-sensing variables, e.g. app-category use)' % (tl, len(grp)), instrument=tl,
                         construct='DM_ST', source='ABCD_7.0_dictionary_with_waves.xlsx', level='measure', timing='design (baseline 2016–18, age 9–10)'))
for _, r in a.iterrows():
    seg = re.match(r'^[a-z]+_([a-z])_', str(r['table_name']))
    inf = {'y': 'Youth', 'p': 'Parent', 't': 'Teacher/School'}.get(seg.group(1) if seg else '', 'Other')
    codes = [c.strip() for c in str(r['wave_codes']).split(';') if re.match(r'\d\d[AM]', c.strip())]
    for c in codes:
        k = int(c[:2]); mid = c[2] == 'M'
        age = round(9.9 + k + (0.5 if mid else 0), 1)
        y0 = 2016 + k + (0.5 if mid else 0)
        add('ABCD', 'ABCD', ('Y%d' % k) + ('.5' if mid else ''), '%g–%g' % (y0, y0 + 2), age, inf, r['name'], str(r['label']),
            str(r['table_label']), 'ABCD_7.0_dictionary_with_waves.xlsx', extra={'timing': 'table-level wave coverage (over-inclusive for items added later)'},
            force=['DM_PU'] if (re.search(r'stq__(vidgame|phone|socmed)_\d+$', str(r['name'])) and re.match(r"(I |I'|The thought|When )", str(r['label']))) else None)

# ---------- MCS ----------
m = pd.read_excel(R + '/mcs.xlsx', sheet_name='Variables')
for _, r in m.iterrows():
    txt = r['Question text'] if isinstance(r['Question text'], str) and len(r['Question text']) > 5 else str(r['Variable label'])
    resp = str(r['Respondent']) + ' ' + str(r['Dataset name'])
    inf = 'Youth' if re.search(r'cm_interview|cm_saq|23y_cm|cohort member|self', resp, re.I) and not re.search(r'parent', str(r['Respondent']), re.I) else inf_map(resp)
    add('MCS', 'MCS 2000–02', 'S' + str(r['Sweep']), str(r['Fieldwork years']).split(' (')[0], r['Approx age (years)'], inf,
        r['Variable name'], txt, str(r['Questionnaire - subsection/ scale']) if isinstance(r['Questionnaire - subsection/ scale'], str) else str(r['Sub Topic1']),
        'MCS_Full_Data_Dictionary_Harmoniser_2026-10-13.xlsx', extra={'timing': 'dictionary'})

# ---------- GUI ----------
g = pd.read_excel(R + '/gui.xlsx', sheet_name='All_Variables')
for _, r in g.iterrows():
    inf = inf_map(r['Informant / source'])
    if inf == 'Derived': continue
    yrs = re.findall(r'(20\d\d)', str(r['Fieldwork dates']))
    add('GUI', str(r['Cohort']), str(r['Wave']), '–'.join(dict.fromkeys(yrs)), r['Approx. age (yrs)'], inf, r['Variable name'],
        str(r['Variable label / question text']), ' '.join(str(x) for x in [r['Domain'], r['Harmonised item key'], r['Extraction note']] if isinstance(x, str)), 'GUI_All_Cohorts_Overview_and_Alignment.xlsx', extra={'timing': 'dictionary'})

# ---------- HILDA (youth slice 15–24) ----------
h = pd.read_excel(R + '/hilda.xlsx', sheet_name='Variable_Dictionary')
for _, r in h.iterrows():
    src = str(r['Informant / source'])
    if src.startswith('Derived'): continue
    inf = 'Youth' if 'Self' in src else 'Parent'  # HQ/HF = adult household informant
    for w in re.findall(r'\d+', str(r['Waves present'])):
        w = int(w)
        add('HILDA', 'HILDA 2001–', 'W%d' % w, str(2000 + w), '15–24', inf, r['Variable stem (prefix a–x for W1–W24)'], str(r['Variable label']),
            str(r['Nested area']), 'HILDA_R24_Data_Dictionary.xlsx', extra={'timing': 'dictionary (survey year)'})

# ---------- Ten to Men ----------
t = pd.read_excel(R + '/t2m.xlsx', sheet_name='Data Dictionary')
T2M_YEARS = {1: '2013–14', 2: '2015–16 (verify)', 3: '2020–21', 4: '2022', 4.1: '2022–24 (top-up)', 5: '2024–25'}
for _, r in t.iterrows():
    pop = str(r['Population'])
    if pop.startswith('18+') or pop.startswith('15+'):
        pass
    inf = 'Parent' if 'Parent' in pop else 'Youth'
    txt = r['Question'] if isinstance(r['Question'], str) and r['Question'] != 'Derived variable' else str(r['Variable Label'])
    add('Ten to Men', 'Ten to Men (boys 10–17 at W1)', 'W%g' % r['Wave'], T2M_YEARS.get(r['Wave'], ''), pop, inf, r['Variable Name'], txt,
        str(r['Instrument']) if isinstance(r['Instrument'], str) else str(r['Research Domain']), 'Ten to Men 2025 Release Data Dictionary.xlsx',
        extra={'timing': 'dictionary (Population = asked age group)'})

# ---------- PSKC (construct level) ----------
p = pd.read_excel(R + '/pskc.xlsx', sheet_name='Long (construct x wave)')
for _, r in p.iterrows():
    inf = inf_map(r['Informant(s)'])
    add('PSKC', 'PSKC 2008 births', 'W%s' % r['Wave'], str(r['Year']), r['Approx. age (yrs)'], inf, r['Construct ID'],
        '%s – %s' % (r['Topic'], r['Construct (EN)']), str(r['Standardised measure']) if isinstance(r['Standardised measure'], str) else '',
        'PSKC_Data_Dictionary.xlsx', level='construct', extra={'timing': 'dictionary'})

# ---------- KCYPS 2018 ----------
k = pd.read_excel(R + '/kcyps.xlsx')
for _, r in k.iterrows():
    inf = 'Youth' if 'Youth' in str(r['Informant']) else 'Parent'
    txt = ' – '.join(str(x) for x in [r['Area'], r['Sub-area'], r['Survey item / scale'], r['Subfactor'], r['Variable description']] if isinstance(x, str))
    used = str(r['Questionnaire used by (cohort/waves)'])
    form = str(r['Form']).lower()
    for i, y in enumerate(range(2018, 2025), start=1):
        if not isinstance(r['W%d %d' % (i, y)], str): continue
        cohorts = []
        if 'elementary' in form: cohorts = [('E4 cohort', 10 + i - 1)]
        elif 'guardian' in form: cohorts = [('E4 cohort', 10 + i - 1), ('M1 cohort', 13 + i - 1)]
        else:
            if 'E4' in used: cohorts.append(('E4 cohort', 10 + i - 1))
            if 'M1' in used or not cohorts: cohorts.append(('M1 cohort', 13 + i - 1))
        for coh, age in cohorts:
            if coh == 'E4 cohort' and 'elementary' not in form and 'guardian' not in form and i < 4: continue
            add('KCYPS', 'KCYPS 2018 ' + coh, 'W%d' % i, str(y), age, inf, str(r['Variable name stem (data: stem+wN)']), txt,
                str(r['Survey item / scale']) if isinstance(r['Survey item / scale'], str) else '', 'KCYPS 2018 – Variable Dictionary (English, W1–W7)',
                extra={'timing': 'dictionary (age approx. from grade)'})

# ---------- AStRA (from SPSS .spv) ----------
ASTRA = {'a1': ('AStRA Cohort 1', {1: '2005', 2: '2006', 3: '2007'}), 'a2': ('AStRA Cohort 2', {1: '2013', 2: '2014', 3: '2015'}),
         'a3': ('AStRA Cohort 3 (Migrant Youth Resilience)', {1: '2022', 2: '2023'})}
astra_rows = []
for f, (coh, yrs) in ASTRA.items():
    sec = None; vals = collections.defaultdict(list); cur = None; varinfo = []
    for line in csv.reader(open(S + '/astra/%s.csv' % f, encoding='utf-8', errors='replace')):
        if line and line[0].startswith('Table:'): sec = line[0]; continue
        if sec == 'Table: Variable Information' and len(line) > 3 and line[1].isdigit(): varinfo.append(line)
        elif sec == 'Table: Variable Values' and len(line) >= 3:
            if line[0]: cur = line[0]
            if cur: vals[cur].append('%s=%s' % (line[1], line[2]))
    for line in varinfo:
        var, pos, lab, lvl = line[0], line[1], line[2], line[3]
        wm = re.search(r'\.w(\d)\b|^w(\d)-|\(W(\d)\)', var + ' ' + lab, re.I)
        wave = int(next(x for x in wm.groups() if x)) if wm else None
        upp = var.upper()
        inf = 'Teacher/School' if re.match(r'^(TCH|MRK|ABSNT|ABS|GRD|GPA|KIDS|VLD|CLIM)', upp) and not upp.startswith('CLIM') else \
              'Peers (sociometric)' if re.match(r'^(SOC|PAR|SP\d|SI\d|POP|ZPOP|PCT|HAP|DSCR|PDIS)', upp) else 'Youth'
        if upp.startswith('CLIM'): inf = 'Youth'
        rec = dict(study='AStRA', cohort=coh, variable=var, position=int(pos), label=lab, measurement=lvl, wave=('W%d' % wave) if wave else 'cross-wave/derived',
                   year=yrs.get(wave, '') if wave else '', informant=inf, value_labels='; '.join(vals.get(var, [])[:20]),
                   source='AStRA%s-data-dictionary.spv' % f[1])
        astra_rows.append(rec)
        add('AStRA', coh, rec['wave'], rec['year'], 'lower-secondary (age TBC)', inf, var, lab, '', rec['source'], extra={'timing': 'dictionary (wave/year from cohort title)'})

pd.DataFrame(astra_rows).to_csv(S + '/astra_dictionary_rows.csv', index=False)

# ---------- curated rows: UKHLS (digital), GUiNZ crosswalk, TESS instrument overview, LSAC partial ----------
CUR = json.load(open(S + '/curated_raw.json'))
for r in CUR:
    if r['construct']:
        rows.append(r)
    else:
        for c in classify(r['text'], r['instrument']):
            rows.append(dict(r, construct=c))

df = pd.DataFrame(rows)
df.to_csv(S + '/lexicon_candidates.csv', index=False)
print(df.groupby(['study']).size())
print(df.groupby(['study', 'construct']).size().unstack(fill_value=0))
