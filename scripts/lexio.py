"""Read/write data/lexicon_candidates.csv.

To keep the CSV under GitHub's web-upload size, the long, per-study constant columns `source` and `timing`
are stored as short keys (S01…, T01…) and expanded from data/lexicon_lookup.csv on read."""
import os
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEX = os.path.join(ROOT, 'data', 'lexicon_candidates.csv')
LOOK = os.path.join(ROOT, 'data', 'lexicon_lookup.csv')

def read_lex():
    d = pd.read_csv(LEX, low_memory=False).fillna('')
    if os.path.exists(LOOK):
        lk = pd.read_csv(LOOK).fillna('')
        m = dict(zip(lk.key, lk.value))
        for c in ('source', 'timing'):
            d[c] = d[c].map(lambda v: m.get(v, v))
    return d

def write_lex(d):
    d = d.copy()
    rows = []
    for c, p in (('source', 'S'), ('timing', 'T')):
        vals = sorted(set(d[c].astype(str)))
        keys = {v: '%s%02d' % (p, i + 1) for i, v in enumerate(vals)}
        rows += [dict(key=k, column=c, value=v) for v, k in keys.items()]
        d[c] = d[c].astype(str).map(keys)
    pd.DataFrame(rows).to_csv(LOOK, index=False)
    d.to_csv(LEX, index=False)

# ---------------------------------------------------------------- ABCD item-level waves from REDCap branching logic
import re as _re
_EVW = {'baseline_year_1_arm_1': 'Y0', '6_month_follow_up_arm_1': 'Y0.5', '18_month_follow_up_arm_1': 'Y1.5',
        '30_month_follow_up_arm_1': 'Y2.5', '42_month_follow_up_arm_1': 'Y3.5', '54_month_follow_up_arm_1': 'Y4.5',
        '66_month_follow_up_arm_1': 'Y5.5', '78_month_follow_up_arm_1': 'Y6.5'}
for _k in range(1, 10):
    _EVW['%d_year_follow_up_y_arm_1' % _k] = 'Y%d' % _k

def abcd_allowed(logic, wave):
    """True/False if the item's branching logic allows (or excludes) this wave; None if the logic cannot be evaluated.
    Conditions on other variables are treated as possibly true, so the result is conservative (keeps the wave when unsure)."""
    ev = next((k for k, v in _EVW.items() if v == wave), None)
    if ev is None: return None
    s = str(logic)
    s = _re.sub(r"\[event-name\]\s*(!=|<>|=)\s*[\"']([^\"']+)[\"']",
                lambda m: str((m.group(2) == ev) if m.group(1) == '=' else (m.group(2) != ev)), s)
    s = _re.sub(r"\[[^\]]+\](\(\d+\))?\s*(!=|<>|>=|<=|=|>|<)\s*(\"[^\"]*\"|'[^']*'|[-\w.]+)", 'True', s)
    s = _re.sub(r"\[[^\]]+\](\(\d+\))?", 'True', s)
    s = _re.sub(r'\bAND\b', ' and ', s, flags=_re.I); s = _re.sub(r'\bOR\b', ' or ', s, flags=_re.I); s = _re.sub(r'\bNOT\b', ' not ', s, flags=_re.I)
    if not _re.fullmatch(r"[\sTrueFalsandotr()]+", s): return None
    try: return bool(eval(s, {'__builtins__': {}}))
    except Exception: return None
