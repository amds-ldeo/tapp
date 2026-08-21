"""
LA-ICP-MS TAPP v11 → v12

Changes:
  1. Add "Analytical Mode" as the first field in Group 4 (before "Laser Spot Geometry")
     — mandatory cross-TAPP field per conventions Rule 3 (added 2026-06);
       this was the last active TAPP lacking the field after the 2026-06 library-wide
       consistency review (EPMA v7, SEM v4, LA-Q:SF v2, Lab-XCT v8, TEM v7 all updated
       in the same review cycle).

Files modified in this propagation cycle:
  EPMA_TAPP_v7.csv, SEM_TAPP_v4.csv, LA-Q:SF-ICPMS_TAPP_v2.csv,
  Lab-XCT_TAPP_v8.csv, TEM_TAPP_v7.csv, LA-ICPMS_TAPP_v12.csv (this file)
"""

import csv

SRC  = '/Users/ruolin/Documents/Astromat/TAPPs/LA-ICP-MS/LA-ICPMS_TAPP_v11.csv'
DEST = '/Users/ruolin/Documents/Astromat/TAPPs/LA-ICP-MS/LA-ICPMS_TAPP_v12.csv'
TODAY = '2026-06-01'

C_ITEM  = 0; C_DESC = 1; C_PROTO = 2; C_ANAL = 3; C_DTYPE = 4
C_EX = 5; C_COMM = 6; C_DATE = 7
C_SPOT = 8; C_TRANS = 9; C_MAP = 10; C_LIT = 11

with open(SRC, newline='', encoding='utf-8-sig') as f:
    rows = list(csv.reader(f))

n_cols = len(rows[0])
print(f'Loaded v11: {len(rows)} rows, {n_cols} cols')

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
        'with transect scanning in the same session), list all applicable modes separated by '
        'semicolons. Serves as the protocol-level declaration of measurement type, distinct from '
        'the mode flag columns which indicate per-field applicability.'
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
    if r[C_ITEM].strip() in ('Analytical Mode', 'Laser Spot Geometry'):
        print(f'  Row {i:3d} [{r[0]:<35}] P={r[2]:<10} A={r[3]:<12} '
              f'Spot={r[C_SPOT]} Trans={r[C_TRANS]} Map={r[C_MAP]}')
