"""Item-level wave coverage for ABCD, computed from the tabulated data you hold under your DUC.

Usage (run locally; neither participant data nor counts enter the repo; the output stays local):
  python scripts/abcd_item_waves_from_data.py /path/to/ABCD_7.0_data_dictionary_FULL.csv /path/to/tables/*.csv [*.tsv *.parquet]
Accepts ABCD 5.x tables (columns = NDA/REDCap names, `eventname`) and 6.x/7.x tables (`participant_id`, `session_id`).
Writes a local data/abcd_item_waves.csv (not distributed): name (7.0), wave (Y0, Y0.5, Y1 …), n_nonmissing. The rebuild uses it in preference to
the REDCap branching logic, keeping a (name, wave) only where n_nonmissing > 0.
"""
import os, re, sys, glob
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data', 'abcd_item_waves.csv')
EVW = {'baseline_year_1_arm_1': 'Y0', '6_month_follow_up_arm_1': 'Y0.5', '18_month_follow_up_arm_1': 'Y1.5', '30_month_follow_up_arm_1': 'Y2.5',
       '42_month_follow_up_arm_1': 'Y3.5', '54_month_follow_up_arm_1': 'Y4.5', '66_month_follow_up_arm_1': 'Y5.5', '78_month_follow_up_arm_1': 'Y6.5'}
EVW.update({'%d_year_follow_up_y_arm_1' % k: 'Y%d' % k for k in range(1, 10)})

def ses_to_wave(s):  # ses-02A -> Y2 ; ses-02M -> Y2.5
    m = re.match(r'ses-(\d\d)([AM])', str(s))
    return ('Y%d' % int(m.group(1)) + ('.5' if m.group(2) == 'M' else '')) if m else None

dic = pd.read_csv(sys.argv[1], low_memory=False, usecols=['name', 'name_nda', 'name_redcap'])
old2new = {}
for _, r in dic.iterrows():
    for c in ('name_nda', 'name_redcap'):
        if isinstance(r[c], str): old2new.setdefault(r[c], r['name'])
rows = []
files = [f for pat in sys.argv[2:] for f in glob.glob(pat)]
for f in files:
    t = pd.read_parquet(f) if f.endswith('.parquet') else pd.read_csv(f, sep='\t' if f.endswith('.tsv') else ',', low_memory=False)
    if 'eventname' in t.columns: t['_w'] = t['eventname'].map(EVW)
    elif 'session_id' in t.columns: t['_w'] = t['session_id'].map(ses_to_wave)
    else: print('skip (no event column):', f); continue
    skip = {'src_subject_id', 'eventname', 'participant_id', 'session_id', '_w'}
    cols = [c for c in t.columns if c not in skip]
    nn = t[cols].notna().groupby(t['_w']).sum()
    for c in cols:
        for w, n in nn[c].items():
            rows.append(dict(name=old2new.get(c, c), wave=w, n_nonmissing=int(n), source_file=os.path.basename(f)))
    print('counted', os.path.basename(f), len(cols), 'variables')
new = pd.DataFrame(rows)
if os.path.exists(OUT):
    old = pd.read_csv(OUT)
    new = pd.concat([old[~old.name.isin(new.name)], new])
new.to_csv(OUT, index=False)
print('wrote', OUT, len(new), 'rows')
