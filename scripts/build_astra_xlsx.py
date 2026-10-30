import os
import pandas as pd, re
S = os.environ.get('GCHN_WORKDIR', '.')
v = pd.read_csv(S + '/astra_dictionary_rows.csv', dtype=str).fillna('')
v['position'] = v['position'].astype(int)
lex = pd.read_csv(S + '/lexicon_candidates.csv', low_memory=False, dtype=str).fillna('')
lx = lex[lex.study == 'AStRA'].groupby(['cohort', 'var'])['construct'].apply(lambda s: '; '.join(sorted(set(s)))).to_dict()
NAMES = {'WB_LS': 'Life satisfaction & subjective wellbeing', 'WB_MOOD': 'Emotional wellbeing (low mood, worry)', 'WB_SE': 'Self-esteem & self-worth',
         'DM_ST': 'Screen time', 'DM_SM': 'Social media & online communication', 'DM_GM': 'Gaming', 'DM_PU': 'Problematic / compulsive use',
         'DM_DEV': 'Device access & ownership', 'PC_REL': 'Parent–child relationship', 'PC_MON': 'Parental monitoring & media rules', 'PC_FAM': 'Family functioning & climate'}
v['Harmoniser construct (candidate, keyword screen)'] = ['; '.join(NAMES[c] for c in lx.get((co, va), '').split('; ') if c) for co, va in zip(v.cohort, v.variable)]
v['Block / instrument prefix'] = [ (re.match(r'([A-Za-z]+)', a).group(1).lower() if re.match(r'([A-Za-z]+)', a) else a) for a in v.variable]
v = v.rename(columns={'study': 'Study', 'cohort': 'Cohort', 'variable': 'Variable', 'position': 'Position', 'label': 'Label', 'measurement': 'Measurement level',
                      'wave': 'Wave', 'year': 'Year', 'informant': 'Informant (inferred from block)', 'value_labels': 'Value labels (first 20)', 'source': 'Source file'})
cols = ['Study', 'Cohort', 'Wave', 'Year', 'Position', 'Variable', 'Label', 'Block / instrument prefix', 'Informant (inferred from block)', 'Measurement level',
        'Value labels (first 20)', 'Harmoniser construct (candidate, keyword screen)', 'Source file']
v = v[cols].sort_values(['Cohort', 'Position'])
j = lambda s: ', '.join(sorted(set(x for x in s if x)))
bs = v.groupby(['Cohort', 'Block / instrument prefix']).agg(
    Example_label=('Label', 'first'), N_variables=('Variable', 'size'), Waves=('Wave', j), Years=('Year', j),
    Informant=('Informant (inferred from block)', j),
    Constructs=('Harmoniser construct (candidate, keyword screen)', lambda s: '; '.join(sorted(set(x for y in s for x in y.split('; ') if x))))).reset_index()
bs = bs[bs.N_variables >= 2]
coh = pd.DataFrame([
 ['AStRA Cohort 1', '2005–2007', 'W1 2005, W2 2006, W3 2007', 'Adolescents in Athens-area lower-secondary schools (grades 1–3); Greek and immigrant youth', int((v.Cohort == 'AStRA Cohort 1').sum()), 'Self-report; teacher ratings (TCH); peer sociometrics; school records', 'AStRA1-data-dictionary.spv (raw file AStRA1raw.sav)'],
 ['AStRA Cohort 2', '2013–2015', 'W1–W3', 'School cohort; economic-crisis module; FACES II/IV; PBI (mother & father); mood; SDQ; Rosenberg', int((v.Cohort == 'AStRA Cohort 2').sum()), 'Self-report; teacher ratings; peer sociometrics; school records', 'AStRA2-data-dictionary.spv'],
 ['AStRA Cohort 3 (Migrant Youth Resilience)', '2022–2023', 'W1 (April 2022), W2', 'Migrant and Greek youth; SDQ, SCL, DEPS, DERS, RSES, SWLS; parent–adolescent conflict incl. computer/phone time; home internet quality', int((v.Cohort == 'AStRA Cohort 3 (Migrant Youth Resilience)').sum()), 'Self-report; peer nominations (PAR); grades', 'AStRA3-data-dictionary.spv'],
], columns=['Cohort', 'Years', 'Waves', 'Design / content notes', 'N variables', 'Informants', 'Source'])
readme = pd.DataFrame({'AStRA data dictionary – harmoniser edition (built 22 Oct 2026)': [
 'Built from the three SPSS output files in the AStRA Data folder (AStRA1/2/3-data-dictionary.spv), converted with PSPP. Every variable, label, measurement level and the first 20 value labels are kept.',
 'Wave and year come from variable names (.w1/.w2/.w3) and the cohort titles. Age at each wave is NOT tabulated: the files hold "Age (in 2005)", "age@2012" and "Age @ W1 (April 2022)" variables, whose values need the .sav data.',
 'Informant is inferred from the instrument block (TCH = teacher, SOC/PAR = peer sociometrics, MRK/GPA/ABS = school records, otherwise adolescent self-report). Check before analysis.',
 'Harmoniser construct = keyword screen for the three domains (wellbeing, digital media use, proximate context). Candidates only, not validated mappings.',
 'Folder note: 3bea483e-9d00-4ba1-9f38-aa421e8df6f8.pdf in the AStRA Data folder is an unrelated manuscript (Slovak OGD-Q validation, Helvich, Novak & Tavel). It looks misfiled.',
 'Scoring syntax AStRA1/2/3-scoring.sps is in the same folder (not parsed here).']})
out = '/mnt/user-data/outputs/AStRA_Data_Dictionary_Harmoniser_2026-10-22.xlsx'
with pd.ExcelWriter(out) as w:
    readme.to_excel(w, sheet_name='README', index=False); coh.to_excel(w, sheet_name='Cohorts', index=False)
    bs.to_excel(w, sheet_name='Blocks_by_cohort', index=False); v.to_excel(w, sheet_name='All_Variables', index=False)
    v[v['Harmoniser construct (candidate, keyword screen)'] != ''].to_excel(w, sheet_name='Harmoniser_candidates', index=False)
bs.to_csv(S + '/astra_blocks.csv', index=False)
print(len(v), len(bs), (v['Harmoniser construct (candidate, keyword screen)'] != '').sum(), len(open(S + '/astra_blocks.csv').read()))
