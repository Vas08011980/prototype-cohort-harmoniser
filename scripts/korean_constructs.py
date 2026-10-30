"""Identify Atlas constructs in the two Korean cohorts with KOREAN terms (29 Oct 2026).

PSKC  – item level from the Korean variable labels of the 16 public SPSS files (metadata only: data/pskc_variable_labels.csv,
        extracted with pyreadstat metadataonly=True; no participant values are read or stored).
KCYPS – the files we hold (English codebook and variable dictionary) carry no Korean text, so each KCYPS scale is bridged to
        its Korean scale name (KCYPS_KO below) and the Korean lexicon is applied to that name; the English keyword screen is
        kept as a second pass.
The lexicon is written to data/korean_construct_terms.csv for review by a Korean speaker.

Run from the repository root, then rebuild:
  GCHN_WORKDIR=... python scripts/korean_constructs.py
  GCHN_WORKDIR=... python scripts/update_tess_ukhls_adii.py && python scripts/add_context.py
"""
import os, re, sys, json
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lexio import read_lex, write_lex

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = os.environ.get('GCHN_WORKDIR', '.')
APP = os.path.join(ROOT, 'app', 'gchn_data.json')

# ---- Korean construct lexicon (term, English gloss, construct)
KO = [
 ('삶의 만족|삶 만족|생활 ?만족|삶에 대한 만족|삶의만족', 'life satisfaction', 'WB_LS'),
 ('행복', 'happiness', 'WB_LS'),
 ('주관적 ?안녕|안녕감|웰빙', 'subjective wellbeing', 'WB_LS'),
 ('우울', 'depression / low mood', 'WB_MOOD'),
 ('불안', 'anxiety', 'WB_MOOD'),
 ('걱정', 'worry', 'WB_MOOD'),
 ('외로|고독', 'loneliness', 'WB_MOOD'),
 ('정서 ?문제|내재화|위축', 'emotional problems / internalising / withdrawal', 'WB_MOOD'),
 ('자아존중|자존감|자기존중', 'self-esteem', 'WB_SE'),
 ('미디어|매체 ?이용|영상 ?시청|동영상|텔레비전|TV|인터넷 ?이용|컴퓨터 ?이용|스크린', 'media / screen use', 'DM_ST'),
 ('스마트폰 ?(이용|사용)|휴대폰 ?(이용|사용)|사용 목적별', 'smartphone use', 'DM_ST'),
 ('SNS|소셜|사회관계망|메신저|카카오|채팅|사이버 ?(폭력|괴롭힘|따돌림)|문자', 'social media / online communication / cyberbullying', 'DM_SM'),
 ('게임', 'gaming', 'DM_GM'),
 ('중독|과의존|과몰입|스마트폰 ?의존|일상생활 ?장애|금단|내성|가상세계', 'addiction / overdependence (withdrawal, tolerance, daily-life disturbance, virtual-world orientation)', 'DM_PU'),
 ('휴대폰|휴대전화|스마트폰 ?(소유|보유)|기기 ?(소유|보유)|태블릿|컴퓨터 ?(보유|소유)|인터넷 ?접속', 'device access & ownership', 'DM_DEV'),
 ('양육 ?태도|양육 ?행동|양육 ?방식|따스함|따뜻|애정|온정|거부|자율성 ?지지|강요|체벌|부모-?자녀|부모와의 ?관계|부모 ?자녀 ?(관계|상호작용)|애착|친밀', 'parenting / parent–child relationship', 'PC_REL'),
 ('양육 ?스트레스', 'parenting stress', 'PC_REL'),
 ('감독|관리 ?감독|모니터링|규칙|구조 ?제공|통제|(미디어|스마트폰|게임) ?(지도|중재|제한)|이용 ?(지도|제한)', 'parental monitoring, rules & structure', 'PC_MON'),
 ('가족 ?(기능|관계|갈등|응집|분위기|여가|건강성)|부부 ?(갈등|관계)|결혼 ?만족|가정 ?분위기|비일관', 'family functioning & climate', 'PC_FAM'),
]
KO_EXCL = re.compile(r'가중치|참여 여부|치아|구강|진단 여부|흡연|음주|약물|체중|키\b|신장|출생|성별|생성\. ID|조사일|응답자|사고/중독|중독으로 인한|식중독|보드 ?게임|수혜|육아지원|양육 ?수당|양육 ?지원|양육비|보육료|반에는|학급 규칙|학교 규칙|어린이집|유치원 ?(비용|선택)', re.I)
KO_RE = [(re.compile(t), c) for t, _, c in KO]
def ko_classify(label):
    if not isinstance(label, str) or KO_EXCL.search(label): return []
    out = {c for rx, c in KO_RE if rx.search(label)}
    if 'PC_REL' in out and re.search(r'또래|친구|교사|선생님', label) and not re.search(r'부모|모애착|부애착|어머니|아버지', label):
        out.discard('PC_REL')  # peer or teacher relationships are not the parent–child relationship
    return sorted(out)

pd.DataFrame([dict(term_ko=t, gloss_en=g, construct=c) for t, g, c in KO]).to_csv(os.path.join(ROOT, 'data', 'korean_construct_terms.csv'), index=False)

# keyword screen (English) from build_lexicon.py, used as a second pass for KCYPS
src = open(os.path.join(ROOT, 'scripts', 'build_lexicon.py'), encoding='utf-8').read()
ns = {}; exec(compile(src[:src.index('rows = []')], 'build_lexicon_defs', 'exec'), ns)
classify = ns['classify']

d = read_lex()
before = d.groupby('study').size().to_dict()
d = d[~d.study.isin(['PSKC', 'KCYPS'])]
new = []

# ======================================================================= PSKC (Korean labels, item level)
P_SRC = 'PSKC SPSS files W1–W16 (Korean variable labels, metadata only)'
p = pd.read_csv(os.path.join(ROOT, 'data', 'pskc_variable_labels.csv')).fillna('')
PRE_INF = {'J': 'Youth', 'E': 'Parent', 'F': 'Parent', 'D': 'Parent', 'K': 'Parent', 'I': 'Teacher/School', 'L': 'Teacher/School',
           'H': 'Teacher/School', 'A': 'Observed', 'G': 'Parent', 'B': 'Parent', 'C': 'Parent'}
ps = dict(vars=len(p), kept=0)
for _, r in p.iterrows():
    cons = ko_classify(r['label'])
    if not cons: continue
    w = int(r['wave']); age = 0.3 if w == 1 else w - 1
    who = (re.search(r'"([^"]+)"', r['label']) or [None, ''])[1]
    inf = PRE_INF.get(str(r['variable'])[:1], 'Other')
    if who in ('모', '부') and inf == 'Youth': inf = 'Parent'
    ps['kept'] += 1
    for c in cons:
        new.append(dict(study='PSKC', cohort='PSKC 2008 births', wave='W%d' % w, years=str(int(r['year'])), age=age, informant=inf,
                        var=str(r['variable']), text=str(r['label'])[:400], instrument=('값: ' + str(r['value_labels'])[:110]) if r['value_labels'] else '',
                        construct=c, source=P_SRC, level='item', timing='SPSS file per wave; age = years since birth (approx.)'))

# ======================================================================= KCYPS (Korean scale names bridged to the English dictionary)
KCYPS_KO = {  # (Sub-area, Survey item / scale) -> Korean scale name used in the KCYPS 2018 questionnaires (to verify against the Korean codebook)
 ('Parenting attitude', 'Warmth'): '부모양육태도 – 따스함', ('Parenting attitude', 'Rejection'): '부모양육태도 – 거부',
 ('Parenting attitude', 'Autonomy Support'): '부모양육태도 – 자율성지지', ('Parenting attitude', 'Coercion'): '부모양육태도 – 강요',
 ('Parenting attitude', 'Structure'): '부모양육태도 – 구조제공', ('Parenting attitude', 'Chaos'): '부모양육태도 – 비일관성',
 ('Parental relationship', 'Time spent with parents'): '부모와 함께 보내는 시간',
 ('Daily routine', "Parents’ conversation time"): '부모와의 대화 시간',
 ('Smartphone', 'Dependency'): '스마트폰 의존', ('Smartphone', 'Frequency by purpose of use'): '스마트폰 사용 목적별 빈도', ('Smartphone', 'Usage'): '스마트폰 사용',
 ('스마트폰', '사용 목적별 빈도'): '스마트폰 사용 목적별 빈도',
 ('Emotional issues', 'Depression'): '정서문제 – 우울', ('Emotional issues', 'Social withdrawal'): '정서문제 – 사회적 위축',
 ('Satisfaction', 'Life satisfaction'): '삶의 만족도', ('Happiness', 'Happiness'): '행복감', ('Self-awareness', 'Self-esteem'): '자아존중감',
}
KCYPS_EXTRA = {'부모와 함께 보내는 시간': ['PC_REL'], '부모와의 대화 시간': ['PC_REL'], '부모양육태도 – 구조제공': ['PC_REL', 'PC_MON']}
k = pd.read_csv(os.path.join(W, 'raw', 'kcyps_dict.csv'))
ks = dict(rows=len(k), kept=0, by_korean=0)
for _, r in k.iterrows():
    ko = KCYPS_KO.get((str(r['Sub-area']), str(r['Survey item / scale'])))
    cons_ko = sorted(set(ko_classify(ko) + KCYPS_EXTRA.get(ko, []))) if ko else []
    txt = ' – '.join(str(x) for x in [r['Area'], r['Sub-area'], r['Survey item / scale'], r['Subfactor'], r['Variable description']] if isinstance(x, str))
    # Korean scale name decides when a bridge exists; the English screen is only used for scales without one
    cons = cons_ko if ko else classify(txt, str(r['Survey item / scale']) if isinstance(r['Survey item / scale'], str) else '')
    if not cons: continue
    ks['kept'] += 1; ks['by_korean'] += bool(cons_ko)
    inf = 'Youth' if 'Youth' in str(r['Informant']) else 'Parent'
    used = str(r['Questionnaire used by (cohort/waves)']); form = str(r['Form']).lower()
    text = (ko + ' | ' if ko else '') + txt
    for i, y in enumerate(range(2018, 2025), start=1):
        if not isinstance(r['W%d %d' % (i, y)], str): continue
        cohorts = []
        if 'elementary' in form: cohorts = [('E4 cohort', 10 + i - 1)]
        elif 'guardian' in form or form == 'p': cohorts = [('E4 cohort', 10 + i - 1), ('M1 cohort', 13 + i - 1)]
        else:
            if 'E4' in used: cohorts.append(('E4 cohort', 10 + i - 1))
            if 'M1' in used or not cohorts: cohorts.append(('M1 cohort', 13 + i - 1))
        for coh, age in cohorts:
            if coh == 'E4 cohort' and 'elementary' not in form and 'guardian' not in form and form != 'p' and i < 4: continue
            for c in cons:
                new.append(dict(study='KCYPS', cohort='KCYPS 2018 ' + coh, wave='W%d' % i, years=str(y), age=age, informant=inf,
                                var=str(r['Variable name stem (data: stem+wN)']), text=text[:400],
                                instrument=str(r['Survey item / scale']) if isinstance(r['Survey item / scale'], str) else '',
                                construct=c, source='KCYPS 2018 – Variable Dictionary (English, W1–W7) + Korean scale names', level='item',
                                timing='dictionary (age approx. from grade)'))
nd = pd.DataFrame(new)
d = pd.concat([d, nd], ignore_index=True).fillna('')
write_lex(d)
after = d.groupby('study').size().to_dict()
print('PSKC', ps, '| KCYPS', ks)
print('rows before/after:', {s: (before.get(s), after.get(s)) for s in ('PSKC', 'KCYPS')})
print(nd.groupby(['study', 'construct']).size().unstack(fill_value=0).to_string())

D = json.load(open(APP))
for s in D['studies']:
    if s['id'] == 'PSKC':
        s.update(status='full', dict_file='PSKC SPSS files W1–W16 (Korean variable labels)',
                 note=('Item level from the Korean variable labels of all 16 public SPSS files (%d variables; metadata only, no participant values). '
                       'Constructs found with a Korean term lexicon (data/korean_construct_terms.csv), e.g. 부모 감독 → parental monitoring, '
                       '스마트폰/미디어 이용 → screen time, 게임 → gaming, 우울 → low mood, 행복감 → wellbeing. Item text is shown in Korean. '
                       'Informant from the questionnaire letter (J child, E/F/D mother/father, I/L school/teacher, A assessment). '
                       'The lexicon needs review by a Korean speaker.') % ps['vars'])
    if s['id'] == 'KCYPS':
        s['note'] = ('Ages are approximate, from school grade. Constructs are identified through the Korean scale names of the KCYPS 2018 questionnaires '
                     '(e.g. 부모양육태도 – 구조제공, 스마트폰 의존, 삶의 만족도), bridged to the English dictionary, plus the English keyword screen. '
                     'KCYPS 2018 has no parental-monitoring (knowledge/supervision) or media-rules scale; the closest is parenting Structure '
                     '(구조제공: rules, expectations, explanations), shown under monitoring as a proxy. The Korean codebook (NYPI) would allow '
                     'item-level Korean matching.')
json.dump(D, open(APP, 'w'), default=lambda o: None, allow_nan=False)
