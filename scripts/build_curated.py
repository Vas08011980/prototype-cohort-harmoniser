import os
import json, re, csv, io
S = os.environ.get('GCHN_WORKDIR', '.')
out = []
def r(study, cohort, wave, years, age, inf, var, text, inst, construct, source, level='item', timing=''):
    out.append(dict(study=study, cohort=cohort, wave=wave, years=years, age=age, informant=inf, var=var, text=text, instrument=inst,
                    construct=construct, source=source, level=level, timing=timing))

# --- UKHLS: rows from "Understanding Society (UKHLS) – Data Dictionary (digital engagement & mental health)" (Drive sheet), youth 10–15 file
U = 'UKHLS Data Dictionary (digital engagement & mental health) – Drive sheet'
def ukw(ws):  # wave k fieldwork ~ (2008+k)–(2010+k); youth age 10–15
    for w in ws:
        r('Understanding Society', 'UKHLS youth (10–15)', 'W%d' % w, '%d–%d' % (2008 + w, 2010 + w), '10–15', 'Youth', *cur, U, timing='design (24-month waves from 2009)')
items = [
 ('ypsocweb', "Do you have a social media profile or account on any sites or apps? (earlier: belong to social networking web-sites)", 'Youth self-completion', 'DM_SM', range(1, 16)),
 ('ypnetcht', "On a normal school day, how many hours do you spend chatting or interacting with friends through social media, gaming websites or apps?", 'Youth self-completion', 'DM_SM', range(1, 16)),
 ('ypnetchtw', "On a weekend ... how many hours do you spend chatting or interacting with friends ... social media, gaming websites or apps?", 'Youth self-completion', 'DM_SM', range(12, 16)),
 ('ypfndonl', "In a typical week, how often do you get together with friends online (mobile phone, social media, online gaming)?", 'Youth self-completion', 'DM_SM', range(12, 16)),
 ('ypcomp', "Do you ever use a computer at home?", 'Youth self-completion', 'DM_DEV', [1, 3, 5, 7, 10]),
 ('ypconsol', "Games console in the household", 'Youth self-completion', 'DM_GM', [1, 3, 5, 7, 10]),
 ('ypconstm', "Hours spent playing games on a games console on a school day", 'Youth self-completion', 'DM_GM', [1, 3, 5, 7, 10]),
 ('ypdevice1-6', "Do you have any of the following devices, either of your own or that you can borrow? (smartphone, mobile, tablet, TV, console...)", 'Youth self-completion', 'DM_DEV', range(12, 16)),
 ('yptvvidhrs', "On a normal school day, how many hours do you spend using a tablet, TV, smartphone, games console or computer? (early waves: TV only – break in series)", 'Youth self-completion', 'DM_ST', range(1, 16)),
 ('yptvvidhrw', "On a weekend ... how many hours do you spend using a tablet, TV, smartphone, games console or computer?", 'Youth self-completion', 'DM_ST', [2, 4, 6, 8, 10, 12, 13, 14, 15]),
 ('ypdvpg', "How often do you use any of these devices for... playing games", 'Youth self-completion', 'DM_GM', [12, 14]),
]
for var, text, inst, c, ws in items:
    cur = (var, text, inst, c)
    ukw(ws)

# --- GUiNZ: crosswalk sheet (indicative, from GUiNZ dictionary review) "GUiNZ – ABCD – LSAC indicative crosswalk"
G = 'GUiNZ – ABCD – LSAC indicative crosswalk (Drive sheet)'
def gz(c, text, ages, inf, inst):
    for a in ages:
        yrs = '%d–%d' % (2009 + int(a), 2010 + int(a)) if a >= 1 else '2009–10'
        r('GUiNZ', 'GUiNZ (born 2009–10)', '%gy' % a, yrs, a, inf, '', text, inst, c, G, level='measure', timing='age from sheet; year = birth window + age (approx.)')
gz('DM_ST', 'Weekday/weekend hours of TV, TV on in room and other screen activities; frequency of 15 screen activities outside school', [8], 'Parent', 'Screen-time items (mother); activity frequency (child)')
gz('DM_ST', 'Usual hours on school days and weekend days; activity frequency', [12], 'Youth', 'Banded hours (<1h to >5h)')
gz('DM_ST', 'TV/DVD/computer/gaming hours on last weekday', [2, 4.5], 'Parent', 'Hours/minutes')
gz('DM_DEV', "Child's own device by type; device access", [8, 11, 12], 'Youth', 'Yes/no by device')
gz('DM_SM', 'Platforms used – TikTok, Instagram, Snapchat, YouTube etc.; social media among 15 screen activities', [8, 11, 12], 'Youth', 'Frequency; platform checklist')
gz('DM_PU', "Six problematic screen-use items TU114–119 ('hard to stop', 'sneaks use') – resembles Problematic Media Use Measure", [12], 'Parent', 'TU114–119 (Likert)')
gz('PC_MON', 'Screen-time rules and enforcement; content/time rules, parental controls; media rules', [4.5, 8, 12], 'Parent', 'Yes/no and Likert')
gz('PC_MON', 'Parental knowledge (child report)', [12], 'Youth', 'Likert')
gz('WB_MOOD', 'DS1–10 depressive-symptom items (wording matches CES-DC; scale not named in dictionary)', [8, 12, 15], 'Youth', 'CES-DC-type, 4-point')
gz('WB_MOOD', 'PROMIS Anxiety (raw and T-scores)', [8, 12, 15], 'Youth', 'PROMIS 5-point')
gz('WB_MOOD', 'Strengths and Difficulties Questionnaire (25 items) – emotional symptoms subscale', [2, 4.5, 8, 15], 'Parent', 'SDQ 3-point')
gz('WB_MOOD', 'Strengths and Difficulties Questionnaire – self-report', [12], 'Youth', 'SDQ 3-point')
gz('WB_LS', 'KIDSCREEN-10', [8, 12, 13], 'Youth', 'KIDSCREEN-10')
gz('WB_LS', '7-item wellbeing scale (likely SWEMWBS); Cantril ladder life satisfaction', [15], 'Youth', 'Likert; 0–10 ladder')

# --- TESS: instrument overview (TESS instruments T1-T10_CleanVersion.docx). Column alignment to time points is ambiguous (header 10 points, rows 9 cells).
T = 'TESS instruments T1-T10_CleanVersion.docx'
tess = [
 ('Youth', 'Screen use – interview; later + screenshot of phone app time-use (7 days)', 'Interview / screenshots', 'DM_ST'),
 ('Youth', 'Social media use', 'Questionnaire', 'DM_SM'),
 ('Youth', 'Internet gaming disorder', 'IGDI (Internet Gaming Disorder Interview)', 'DM_PU'),
 ('Youth', 'Fear of missing out', 'FoMOs (Przybylski et al., 2013)', 'DM_PU'),
 ('Youth', 'Cyberbullying', 'CBVEQ-G', 'DM_SM'),
 ('Youth', 'Quality of life and well-being', 'UK Millennium Cohort Study 7-item wellbeing items', 'WB_LS'),
 ('Youth', 'Self-esteem', 'SDQ-I / SDQ-II / SPPA-R (Harter)', 'WB_SE'),
 ('Youth', 'Loneliness', 'UCLA-LS (abbreviated)', 'WB_MOOD'),
 ('Youth', 'Worrying', 'PSWQ (brief)', 'WB_MOOD'),
 ('Youth', 'Perceived relationship to parents and parenting', 'NRI (Network of Relationships Inventory)', 'PC_REL'),
 ('Youth', 'Parenting styles', 'APQ; PBI (Care + Control/overprotection)', 'PC_REL'),
 ('Youth', 'Youth disclosure', 'Youth Disclosure Scale (Stattin & Kerr)', 'PC_MON'),
 ('Youth', 'Family climate', 'FAD (McMaster Family Assessment Device)', 'PC_FAM'),
 ('Parent', 'Screen use (type, frequency, duration) – parent report on child', 'Interview', 'DM_ST'),
 ('Parent', 'Parental social media use; parental gaming', 'Questionnaire', 'DM_SM'),
 ('Parent', 'Parenting styles', 'APQ (Alabama Parenting Questionnaire)', 'PC_REL'),
 ('Parent', 'Family climate', 'FAD', 'PC_FAM'),
 ('Parent', 'Interparental conflict and aggression', 'CPS (Conflicts and Problem-Solving Scales)', 'PC_FAM'),
 ('Parent', 'Mental health of child (emotional problems)', 'SDQ, CBCL', 'WB_MOOD'),
]
for inf, text, inst, c in tess:
    r('TESS', 'TESS (Trondheim, born 2003–04)', 'T1–T10 (alignment unverified)', '2007–2026 (approx.)', '4–22', inf, '', text, inst, c, T, level='instrument',
      timing='instrument overview only: time-point columns misaligned in source table')

# --- LSAC: partial dictionary extract (Release 10.1 xlsx exceeds connector limit; only Wave 1 rows retrieved)
t = open(S + '/raw/lsac.txt').read()
parts = re.split(r' (?=\d+,[BK]\d+,\d+,[BK],)', t)
n = 0
for p in parts:
    m = re.match(r'\d+,([BK]\d+),\d+,([BK]),', p)
    if not m: continue
    try:
        f = next(csv.reader(io.StringIO(p.replace('\\_', '_'))))
    except Exception:
        continue
    if len(f) < 17: continue
    wavecode, coh, var, inf, waves, lab, topic, sub, meas, q = f[1], f[3], f[4], f[9], f[10], f[11], f[12], f[13], f[14], f[15]
    age = '0–1' if coh == 'B' else '4–5'
    out.append(dict(study='LSAC', cohort='LSAC %s cohort' % coh, wave='W1', years='2004', age=age,
                    informant='Parent' if re.search(r'parent|mother|father|P1|P2', inf, re.I) else ('Youth' if re.search(r'child|study child|\bSC\b', inf, re.I) else ('Teacher/School' if re.search('teacher|carer', inf, re.I) else 'Other')),
                    var=var, text=q[:400], instrument=' – '.join(x for x in (topic, sub, meas) if x and x not in ('NA', 'None')), construct=None, source='LSAC-Data-Dictionary-Release-10.1.xlsx (partial extract: Wave 1)',
                    level='item', timing='dictionary'))
    n += 1
print('LSAC partial rows', n)
json.dump(out, open(S + '/curated_raw.json', 'w'))
