"""
Patch TAPP_Planning_Table.csv — 2026-06-15
Changes:
  1. Row 5 (Solution ICP-MS) → split into Row 5 (Solution Q-ICP-MS) + Row 5a (Solution SF-ICP-MS)
  2. Row 7 (LA-Q/SF-ICP-MS) → add scope clarification (trace elements only; geochronology is Row 7d)
  3. Insert new Row 7d (LA-SF-ICP-MS Geochronology) after Row 7c
"""
import csv
from copy import deepcopy

INPUT  = '/Users/ruolin/Documents/Astromat/TAPPs/TAPP_Planning_Table.csv'
OUTPUT = '/Users/ruolin/Documents/Astromat/TAPPs/TAPP_Planning_Table.csv'

with open(INPUT, newline='', encoding='utf-8-sig') as f:
    rows = list(csv.reader(f))

ROW_5_Q = [
    '5',
    'Mass Spectrometry – ICP',
    'Solution Q-ICP-MS',
    'Q-ICP-MS (Quadrupole ICP-MS); solution mode',
    'Elemental composition (trace/major)',
    'Tabular',
    'Yes – core',
    'H',
    (
        'Separate TAPP from Solution SF-ICP-MS (see Row 5a). '
        'Single-quadrupole (Q) detector; unit mass resolution; '
        'trace/major elemental concentrations in digested/dissolved samples. '
        'Excludes: TQ-ICP-MS/MS (triple quadrupole; MS/MS-specific metadata too distinct), '
        'SF-ICP-MS, MC-ICP-MS, LA-coupled variants, and ICP-OES. '
        'CRC (collision/reaction cell) parameters — He KED, reactive gas DRC/CRC modes — '
        'are Q-specific and central to interference management strategy; '
        'no mode flag columns (single-mode technique). '
        'Architecture decision 2026-06-15: separate from SF because CRC fields would be '
        'dead-ends in an SF TAPP, and resolution mode fields would be trivial constants in a Q TAPP. '
        'LA-Q/SF-ICP-MS stays combined (CRC absent from all 13 assessed LA protocols). '
        '4 seed papers confirmed (Solution Q-ICP-MS/ folder).'
    ),
    'Caltech (Francois Tissot), ASU (Ren Marquez)',
]

ROW_5A_SF = [
    '5a',
    '',
    'Solution SF-ICP-MS',
    'HR-ICP-MS; single-collector sector-field ICP-MS (SF-ICP-MS); solution mode',
    'Elemental composition (trace/major)',
    'Tabular',
    'Yes – core',
    'H',
    (
        'Separate TAPP from Solution Q-ICP-MS (see Row 5). '
        'Single-collector sector-field (SF) detector; selectable mass resolution '
        '(low ~300 / medium ~4000 / high ~10 000 m/Δm) resolves polyatomic interferences '
        'without CRC. Trace/major elemental concentrations in digested/dissolved samples. '
        'Excludes: Q-ICP-MS, TQ-ICP-MS/MS, MC-ICP-MS, LA-coupled variants, and ICP-OES. '
        'No mode flag columns (single-mode technique; mass resolution setting is an '
        'analyte-specific field value, not a separate mode). '
        'SF-specific fields include: mass resolution setting per analyte, '
        'SEM–Faraday detector cross-calibration. '
        'Architecture decision 2026-06-15 (see Row 5 notes). '
        'Seed papers TBD.'
    ),
    'Caltech (Francois Tissot), ASU (Ren Marquez)',
]

ROW_7D_GEO = [
    '7d',
    '',
    'LA-SF-ICP-MS Geochronology',
    'LA-SF-ICP-MS (single-collector sector-field) for in-situ U–Pb isotope dating',
    'Isotopic composition (U–Pb) → age/geochronology',
    'Tabular',
    'Yes – isotopic',
    'H',
    (
        'Separate from LA-Q/SF-ICP-MS (trace elements) due to distinct data product '
        '(isotopic age vs. elemental concentration), data reduction philosophy '
        '(down-hole fractionation correction, common-Pb correction, Concordia age calculation), '
        'calibration standards (mineral-matched primary: GJ-1, 91500, Plešovice), '
        'and QC metrics (concordance %, MSWD). '
        'SF-specific hardware central to this application: E-scan mode at fixed magnet, '
        'SEM triple mode (pulse/analog/Faraday), per-isotope asymmetric dwell times (e.g., '
        '2 ms for ²⁰²Hg, 30 ms for ²⁰⁷Pb), enhancement N₂ addition. '
        'Q-ICP-MS not standard for this application due to sensitivity constraints and '
        'Hg/Pb isobar complexity at unit resolution. '
        'Shared Group 1–3 laser and plasma hardware fields must be kept consistent with '
        'LA-Q/SF-ICP-MS TAPP per cross-TAPP propagation rule. '
        '5 seed papers identified in LA-Q:SF-ICP-MS/LA-SF-ICP-MS/ folder: '
        'Frei & Gerdes 2009 (Chem. Geol.); Eckelmann et al. 2014 (Gondwana Res.); '
        'Lana et al. 2021 (Geostand. Geoanal. Res.); Wei et al. 2022 (JAAS); '
        'Yang et al. 2020 (JAAS). '
        'Future TAPP — not yet in development.'
    ),
    '',
]

new_rows = []
for row in rows:
    num = row[0].strip() if row else ''

    if num == '5':
        new_rows.append(ROW_5_Q)
        new_rows.append(ROW_5A_SF)

    elif num == '7':
        updated = deepcopy(row)
        updated[8] = (
            'Covers both quadrupole and single-collector sector-field instruments coupled to '
            'laser ablation for multi-element trace/major chemistry. '
            'Scope is trace element analysis only — LA-SF-ICP-MS U–Pb geochronology '
            'is a separate future TAPP (see Row 7d). '
            'Excludes MC and TQ/ToF mass analyzers, which require dedicated TAPPs. '
            'Most common LA-ICP-MS configuration in meteoritics literature. '
            'TAPP v2 complete; 13 Q/SF-instrument protocols assessed from literature.'
        )
        new_rows.append(updated)

    elif num == '7c':
        new_rows.append(row)
        new_rows.append(ROW_7D_GEO)

    else:
        new_rows.append(row)

with open(OUTPUT, 'w', newline='', encoding='utf-8-sig') as f:
    csv.writer(f).writerows(new_rows)

# Verification
print('Patch applied. Verifying key rows:')
with open(OUTPUT, newline='', encoding='utf-8-sig') as f:
    check = list(csv.reader(f))
for r in check:
    if r and r[0].strip() in ('5', '5a', '7', '7c', '7d'):
        print(f'  Row {r[0]:4s} | {r[2]}')
