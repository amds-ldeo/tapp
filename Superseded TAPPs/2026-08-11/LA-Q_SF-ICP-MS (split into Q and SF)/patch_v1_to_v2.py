"""
LA-Q:SF-ICPMS TAPP v1 → v2

Changes:
  1. Add "Analytical Mode" at the start of Group 4 (before "Laser Spot Geometry")
     — cross-TAPP consistency: protocol-level declaration of measurement mode,
       distinct from mode flag columns which indicate per-field applicability.
"""

import csv

SRC  = '/Users/ruolin/Documents/Astromat/TAPPs/LA-Q:SF-ICP-MS/LA-Q:SF-ICPMS_TAPP_v1.csv'
DEST = '/Users/ruolin/Documents/Astromat/TAPPs/LA-Q:SF-ICP-MS/LA-Q:SF-ICPMS_TAPP_v2.csv'
TODAY = '2026-06-01'

# Column indices (0-based)
C_ITEM  = 0; C_DESC = 1; C_PROTO = 2; C_ANAL = 3; C_DTYPE = 4
C_EX = 5; C_COMM = 6; C_DATE = 7
C_SPOT = 8; C_TRANS = 9; C_MAP = 10; C_LIT = 11

with open(SRC, newline='', encoding='utf-8-sig') as f:
    rows = list(csv.reader(f))

n_cols = len(rows[0])
print(f'Loaded v1: {len(rows)} rows, {n_cols} cols')

def find(name):
    for i, r in enumerate(rows):
        if r[C_ITEM].strip() == name:
            return i
    raise ValueError(f'Not found: {name!r}')

def new_row(item, desc, proto, anal, dtype, example, comments, modes):
    r = [''] * n_cols
    r[C_ITEM] = item; r[C_DESC] = desc; r[C_PROTO] = proto; r[C_ANAL] = anal
    r[C_DTYPE] = dtype; r[C_EX] = example; r[C_COMM] = comments; r[C_DATE] = TODAY
    r[C_LIT] = 'Literature Assessment'
    for c in [C_SPOT, C_TRANS, C_MAP]:
        r[c] = 'N'
    for c, v in modes.items():
        r[c] = v
    return r

# ── 1. Add "Analytical Mode" before "Laser Spot Geometry" ────────────────────
idx = find('Laser Spot Geometry')
rows.insert(idx, new_row(
    item='Analytical Mode',
    desc=(
        'Primary analytical mode(s) executed under this protocol. For single-mode protocols, '
        'records one value (e.g., Spot). For multi-mode protocols (e.g., spot analysis combined '
        'with transect scanning), list all applicable modes. Serves as the protocol-level '
        'declaration of measurement type, distinct from the mode flag columns which indicate '
        'per-field applicability.'
    ),
    proto='Basic', anal='Read-Only',
    dtype='Controlled vocabulary',
    example="'Spot' | 'Transect' | 'Mapping' | 'Spot; Transect'",
    comments='',
    modes={C_SPOT: 'Y', C_TRANS: 'Y', C_MAP: 'Y'},
))
print(f'  1. Inserted Analytical Mode before row {idx} (Laser Spot Geometry)')

with open(DEST, 'w', newline='', encoding='utf-8') as f:
    csv.writer(f).writerows(rows)

with open(DEST, newline='', encoding='utf-8-sig') as f:
    rows2 = list(csv.reader(f))
print(f'\nWritten: {len(rows2)} rows, {len(rows2[0])} cols → {DEST}')

for i, r in enumerate(rows2):
    if r[0].strip() in ('Analytical Mode', 'Laser Spot Geometry'):
        print(f'  Row {i:3d} [{r[0]:<35}] P={r[2]:<10} A={r[3]:<12} '
              f'Spot={r[C_SPOT]} Trans={r[C_TRANS]} Map={r[C_MAP]}')
