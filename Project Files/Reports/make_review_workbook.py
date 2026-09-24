#!/usr/bin/env python3
"""
Build the EPMA reviewer workbook from the current EPMA TAPP (pinned by VERSION).

What this is: the review instrument for domain experts. It sits between the TAPP
(addressable per field, opaque about structure) and the narrative (readable, not
commentable). Rows stay addressable; the narrative's grouping comes back as block
headers; the tier logic moves to a preamble sheet; four comment columns say what the
reviewer is being asked.

Design decisions, 2026-09-17:
  * `Keyed By` is rendered with DEFINER FIELD NAMES, not the cross-TAPP key vocabulary.
    Verified library-wide: in all 16 TAPPs every consumer key has exactly one definer,
    so the mapping is generated, never hand-written.
  * Three structure values, not two: "One value per X", "One or more values per X"
    (multi-valued but nothing repeats over it), "List of entries per X" (a definer).
  * The structure column is SPLIT BY LEVEL. A key rooted in `sample` / `sampling unit`
    has no meaning in the procedure record, which never names samples: those domains are
    stripped for the procedure column and the cell is flagged for review.
  * `>` never appears. Containment is declared once on the definer row ("List of entries
    per Sample Name") and consumers say only "per Sampling Unit Name". Only `x` survives.
  * Rows are grouped into blocks sharing (session structure, mode set) within a section,
    so display order differs from the CSV. Item numbers are assigned in CSV order and are
    the stable reference.

Regenerate after any version bump; this is a snapshot of one version, like the mockups.
"""

import csv, os, re, collections
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.properties import PageSetupProperties
from openpyxl.comments import Comment
from openpyxl.utils import get_column_letter

# Paths resolve from this file's own location, as build_form.py does, so the script runs
# from any working directory. The TAPP is read from the `Current TAPPs/` mirror (Rule 12);
# VERSION pins the snapshot — bump it and the output name follows.
VERSION = 'v77'
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SRC  = os.path.join(ROOT, 'Current TAPPs', 'EPMA_TAPP_%s.csv' % VERSION)
if not os.path.exists(SRC):                      # mirror stale or mid-bump
    SRC = os.path.join(ROOT, 'EPMA', 'EPMA_TAPP_%s.csv' % VERSION)
OUT  = os.path.join(HERE, 'EPMA_TAPP_%s_Review_Workbook.xlsx' % VERSION)

# Domains that do not exist until a session runs.
SESSION_ONLY = {'sample', 'sampling unit'}

# Singular display names for the domains, pointing at the definer field.
DISPLAY = {
    'sample':             'Sample Name',
    'sampling unit':      'Sampling Unit Name',
    'target species':     'Target Species',
    'monitored property': 'Monitored Element',
    'reported property':  'Reported Variable',
    'standard':           'Secondary Reference Material',
}

# Containment: a domain and the domain it nests inside, read off `defines: A > B` rows.
PARENT = {'sampling unit': 'sample'}

# Fields keyed `(none)` whose own description asks for more than one value. Identified by
# reading Columns B and F; `(none)` says "nothing repeats over this", not "one value".
# These are a question for reviewers, not a settled answer.
MULTI = {
    'Instrument Model',
    'Data Processing Software(s)',
    'EDS Detector Configuration',
    'Analytical Mode',
    'EDS Acquisition Mode',
    'Coupled Dataset or Publication Reference',
    'Coupled Technique(s)',
    'Target Material',
}

# Procedure-level multiplicity. The literature assessment (15 EPMA procedures in v77)
# states these as a set of values, each qualified by the phase or material it applies to:
# Beam Current 6/15 procedures, Beam Mode 7/15, Beam Diameter 6/15, Beam Damage 4/15.
# A single procedure-level value would misrepresent them. The domain they vary over
# (phase / material type) has no key at procedure level — a question for reviewers.
PROC_MULTI = {
    'Beam Mode', 'Beam Current', 'Beam Diameter', 'Beam Damage Minimization',
}
REVIEW_NOTE = {
    'Beam Mode': 'Stated per phase in 7 of 15 procedures assessed.',
    'Beam Current': 'Stated per phase in 6 of 15 procedures assessed (e.g. 20 nA olivine, pyroxene, oxides; 10 nA maskelynite, phosphate, sulfide, glass).',
    'Beam Diameter': 'Stated per phase in 6 of 15 procedures assessed, sometimes as a range (1–2 µm; 5–10 µm defocused).',
    'Beam Damage Minimization': 'Stated per phase in 4 of 15 procedures assessed.',
    'Beam Raster Dimensions': 'Attested in 2 of 15 procedures, one value each.',
    'Pre-Analysis Imaging and Screening': 'Attested in 15 of 15 procedures as a single description.',
    'Counting Statistics Error': 'Not stated in any of the 15 procedures assessed.',
}
NOTE_TAIL = (' The procedure record cannot name samples or analysis points, so the per-unit '
             'detail appears only in the session column. Is this what a registering '
             'laboratory would expect to enter?')

PROSE = {
 'Procedure Name': 'A short descriptive name with a version number, identifying the instrument, the technique and the scope of what is measured.',
 'Technique': 'Whether the procedure uses WDS, EDS or both.',
 'Procedure Author': 'The person or laboratory responsible for the procedure; ORCID recommended for a person.',
 'Laboratory': 'The laboratory or institution hosting the instrument.',
 'Laboratory ID': "The laboratory's persistent identifier.",
 'Procedure Start Date': 'The date this procedure configuration first went into production use.',
 'Funding Source for Procedure Development': 'The funding that supported the instrument, major upgrades and development of the procedure, with agencies and grant numbers.',
 'Procedure Reference(s)': 'Publications or technical reports describing, validating or benchmarking the procedure.',
 'Procedure DOI': "The DOI of the registered procedure followed, or 'pending'.",
 'Session Identifier': "The laboratory's own run, sequence or batch identifier for the session, as generated by the instrument or acquisition software.",
 'Analyst': 'The analyst or analysts who performed the session; ORCID recommended.',
 'Analysis Start Date': 'The date the session began.',
 'Analysis End Date': 'The date the session ended.',
 'Funding Source for Analysis': 'The funding that supported these analyses, with agencies and grant numbers.',
 'Coupled Technique(s)': "Other techniques applied to the same samples whose results are interpreted together with these, with the instrument, laboratory or purpose of each; 'None' if not coupled.",
 'Coupling Description': 'What data or context passes between the techniques, and which technique is performed first and why. Required whenever a coupled technique is named.',
 'Coupled Procedure DOI': "The registered procedure DOI of the coupled technique, a publication DOI, 'pending', or 'None'.",
 'Coupled Dataset or Publication Reference': "The identifier of the dataset or publication reporting both datasets together, 'same submission', or 'pending'.",
 'Target Material': 'The material types the procedure is designed to analyse.',
 'Sample Preparation Method': "The form in which samples are presented to the instrument and the preparation that brought them to it; 'None' where material is analysed as received.",
 'Sample Name': 'The name of each sample analysed in the session, as the laboratory records it.',
 'Sampling Unit Type': 'The kind of subdivision of a sample that one row of reported results corresponds to, giving both levels where such units nest.',
 'Sampling Unit Name': 'The label of each unit analysed and the sample it belongs to; where units are too numerous to name individually, the acquisition area they belong to.',
 'Sample Persistent Identifier': 'The persistent identifier of the sample, at the level actually analysed; IGSN recommended.',
 'Sampling Unit Selection Criteria': 'The criteria by which the units analysed are selected within a sample.',
 'Pre-Analysis Imaging and Screening': 'Imaging or screening performed before analysis to locate and select the units analysed, with the technique, instrument and settings, and how individual analyses are linked back to the images.',
 'Instrument Manufacturer': 'The manufacturer of the instrument.',
 'Instrument Model': 'The model designation, including any generation or configuration suffix.',
 'Electron Source': 'The type of electron source.',
 'Acquisition Software': 'The software that controls the instrument and acquires the data, with version number.',
 'Data Processing Software(s)': 'Every software package applied to the data after acquisition, with version numbers.',
 'WDS Spectrometer Configuration': 'The number, type and crystal range of the WDS spectrometers, with manufacturer and model.',
 'EDS Detector Configuration': 'The detector type, manufacturer, number of detector elements, active area and solid angle, window type and geometry, with multiple detectors listed separately.',
 'Analytical Mode': 'The analytical modes the procedure covers.',
 'Beam Mode': 'The beam mode. Must be consistent with beam diameter and raster dimensions.',
 'Accelerating Voltage': 'The accelerating voltage in kV, with justification for any departure from the standard operating voltage.',
 'Beam Current': 'The probe current in nA.',
 'Beam Diameter': 'The beam diameter in µm.',
 'Beam Raster Dimensions': 'The width and height in µm of the area over which the beam is rastered.',
 'Beam Damage Minimization': 'The measures taken to minimise beam damage, with the beam conditions used and the phases to which they are applied.',
 'Drift Correction': 'How drift in beam current and spectrometer position is monitored and corrected during a session.',
 'Target Species': 'The elements the procedure determines. Isotopes are never separate entries.',
 'Monitored Elements': 'The elements monitored in order to make the determinations, grouped under the determined element each serves; elements monitored only to correct an interference serve none.',
 'Reported Variables and Units': 'The quantities the procedure finally reports, with their units, including intermediate quantities reported alongside final ones.',
 'EPMA Technique per Target Species': 'Whether the element is measured by WDS or by EDS.',
 'X-ray Line': 'The X-ray emission line measured.',
 'Diffracting Crystal': 'The diffracting crystal.',
 'WDS Spectrometer Channel': 'The spectrometer position or positions on which the element is measured, one entry per assignment, including an element measured on more than one spectrometer with the intensities aggregated.',
 'Sequence': 'The order in which the element is acquired and, where the element suite exceeds the number of spectrometers, the acquisition pass to which it belongs.',
 'Proportional Counter / Detector': 'The detector type.',
 'WDS PHA Setting': 'The pulse height analyser mode.',
 'Peak Counting Time': 'The on-peak counting time in seconds.',
 'Background Counting Time': 'The total off-peak background counting time in seconds, summed across all background positions.',
 'Background Position(s)': 'The location of each background position relative to the peak, in millimetres or sin θ and on the high- or low-energy side, or that no off-peak positions are used.',
 'EDS Live Time per Point or Pixel': 'The live time per analysis point in seconds.',
 'EDS Acquisition Mode': 'How the beam is positioned during EDS acquisition, listing all approaches used.',
 'Dwell Time per Pixel': 'The dwell time per pixel: one value per spectrometer assignment for WDS, and a single live time per pixel for EDS.',
 'Step Size / Pixel Size': 'The step size in micrometres, with X and Y given separately where they differ.',
 'Map Dimensions': 'The map dimensions in pixels.',
 'Map Area': 'The physical extent of the mapped area.',
 'Stage Scan vs. Beam Scan': 'Whether maps are acquired by stage scan or by beam scan.',
 'Matrix Correction Method': 'The matrix correction algorithm, which also applies when count maps are converted to concentration maps.',
 'Mass Absorption Coefficients (MACs)': 'The database of mass absorption coefficients the correction uses.',
 'X-ray Background Correction Method': 'How the background beneath the peak is estimated and subtracted.',
 'Time-Dependent Intensity Correction': 'The time-dependent intensity correction applied.',
 'Target Species Estimation Method': 'How the concentration of the element is obtained from the measured data.',
 'Halogen Correction on Oxygen': 'Whether oxygen is adjusted for halogen substitution where oxygen is calculated by stoichiometry.',
 'WDS Dead Time Correction': 'The dead-time correction algorithm and any instrument-specific constant. No measured WDS dead time is reported.',
 'EDS Spectral Processing Type': 'How net peak intensities are extracted from the spectra before quantification.',
 'Blank Correction': 'The method and reference material used to determine and subtract a blank.',
 'Normalization / Standards-Based Correction': "Any normalisation applied beyond the primary calibration, or 'None'.",
 'Calibration Factor and Determination Method': 'Any externally calibrated factor that converts the measured quantity into the reported quantity, how that factor was determined, and its uncertainty.',
 'Procedural Blank Level': "The blank level measured in the session, together with the blank's composition where the reported quantity is a ratio.",
 'Analysis Inclusion and Rejection Criteria': 'The rules deciding which individual results contribute to a reported aggregate value, and the outcome of applying them: how many results were obtained, how many were included, and on what grounds any were excluded.',
 'Constants and Reference Values Used': "The physical constants and citable reference values used in data reduction, with their sources, or 'None'.",
 'Primary Calibration Standard Name': "The primary reference material against which the instrument is calibrated, its source, and a citation for the accepted values used; where quantification uses a stored library or response model, that instead. 'None' means no calibration was performed.",
 'Secondary Reference Materials': 'The reference materials measured as unknowns alongside the samples, with the source of each and a citation for its accepted values.',
 'X-ray Line Overlap Corrections Applied': 'Whether an X-ray line overlap correction is applied and, if so, the overlapping lines and the correction method.',
 'Interfering Elements': 'The elements whose lines overlap the measured peak.',
 'Interference Correction Standard': 'The reference material used to calibrate the interference correction.',
 'Detection Limit': 'The detection limit, with units, stating whether the value is a typical estimate or a session-specific measurement. Must be consistent with the stated method.',
 'Detection Limit Method': 'The formula or approach used to calculate the detection limit, with a citation where one exists.',
 'Analytical Precision': 'The reproducibility of repeated measurements, as a one-sigma relative standard deviation in percent, with the number of analyses and the measured value.',
 'Analytical Accuracy': 'The offset between measured and accepted values, as a percent relative bias, with the source of the accepted value.',
 'Counting Statistics Error': 'The uncertainty predicted from counting statistics, including the counts on any background or blank subtracted, with the sigma level stated.',
 'EDS Dead Time': 'The percent dead time recorded by the detector.',
 'Goodness-of-Fit or Dispersion Statistic': 'The statistic used to assess whether scatter among the contributing individual results exceeds what analytical uncertainty alone predicts, together with its value.',
 'Additional Notes': 'Any information not captured elsewhere, including anomalies, deviations from the registered procedure and instrument modifications.',
}

# ---------------------------------------------------------------- structure phrases

def parse_key(k):
    """Return (is_definer, parent_domain_or_None, [operand domains])."""
    k = k.strip()
    if k.startswith('defines:'):
        body = k[len('defines:'):].strip()
        if ' per ' in body:
            enumerated, parent = [x.strip() for x in body.split(' per ', 1)]
            return True, parent, [enumerated]
        if '>' in body:                      # defines: sample > sampling unit
            segs = [s.strip() for s in body.split('>')]
            return True, segs[-2], [segs[-1]]
        return True, None, [body]
    if k == '(none)':
        return False, None, []
    operands = []
    for part in k.split(' x '):
        segs = [s.strip() for s in part.split('>')]
        operands.append(segs[-1])            # `>` collapses: the innermost domain wins
    return False, None, operands


def chain(domain):
    """Domain plus its containment parents, innermost first.

    Expansion follows `>` (containment) only, never `defines: A per B`. Rule 7 draws that
    line: under `>` the inner domain cannot be enumerated without the outer one, whereas
    `per` is a grouping whose entries may have no parent — Monitored Elements explicitly
    admits elements that serve no target species.
    """
    out, seen = [DISPLAY[domain]], {domain}
    d = domain
    while d in PARENT and PARENT[d] not in seen:
        d = PARENT[d]; seen.add(d); out.append(DISPLAY[d])
    return ' per '.join(out)


def phrase(name, key, level):
    """level is 'procedure' or 'session'. Returns (phrase, flagged)."""
    is_def, parent, operands = parse_key(key)
    per_record = 'procedure' if level == 'procedure' else 'session'
    if is_def:
        if parent is None:
            return 'List of entries', False
        if level == 'procedure' and parent in SESSION_ONLY:
            return 'List of entries', True
        return 'List of entries per %s' % chain(parent), False
    kept, dropped, tail = [], False, ''
    for d in operands:
        if level == 'procedure' and d in SESSION_ONLY:
            dropped = True
        else:
            kept.append(d)
    if not kept:
        multi = name in MULTI or (level == 'procedure' and name in PROC_MULTI)
        stem = 'One or more values per %s' if multi else 'One value per %s'
        return stem % per_record, dropped
    # cross-product members joined with ×; containment appended once, outermost last
    parents = []
    for d in kept:
        c = chain(d).split(' per ')
        parents = c[1:] if len(c) > 1 else parents
    body = ' × '.join(DISPLAY[d] for d in kept)
    if parents:
        body += ' per ' + ' per '.join(parents)
    return 'One value per %s' % body, dropped


MODE_PHRASE = {
    'YYYY': 'all four modes', 'NNYY': 'WDS only', 'YYNN': 'EDS only',
    'NYNY': 'mapping only', 'YNYN': 'point analysis only',
    'NNYN': 'WDS point analysis only', 'YNNN': 'EDS point analysis only',
}

# ---------------------------------------------------------------- styling
TIER_STYLE = {'Basic': ('C00000', True), 'Advanced': ('375623', True),
              'Read-Only': ('0070C0', True), 'Editable': ('7030A0', True),
              'N/A': ('808080', False)}
HEAD_FILL    = PatternFill('solid', fgColor='44546A')
SECTION_FILL = PatternFill('solid', fgColor='C9D5EA')
BLOCK_FILL   = PatternFill('solid', fgColor='EDF1F8')
FLAG_FILL    = PatternFill('solid', fgColor='FFF2CC')
ASK_FILL     = PatternFill('solid', fgColor='FBE5D6')
LEGEND_FILL  = PatternFill('solid', fgColor='F2F2F2')
THIN  = Side(style='thin', color='BFBFBF')
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

# Column order keeps each record's two columns together: structure then level.
# "Session level" is this workbook's name for the TAPP's Analysis-Level Tier. One word is
# used throughout — "analysis" collides with an individual analysis point, which is the
# one thing the record is NOT.
# ---------------------------------------------------------------- columns
# Each review column sits immediately after the content column it judges and shares its
# colour: the content header is the family's dark tone, the review header the mid tone,
# and the review cells below a pale wash of it.
FAMILY = {
    'item':      dict(dark='7030A0', mid='B4A7D6', pale='EDE7F5'),
    'procedure': dict(dark='2F5597', mid='8FAADC', pale='DCE4F4'),
    'session':   dict(dark='548235', mid='A9D08E', pale='E4F0DC'),
    'mode':      dict(dark='44546A', mid='44546A', pale='FFFFFF'),
    'comment':   dict(dark='833C0B', mid='F4B183', pale='FBE5D6'),
}

# No double quotes in any option: the list becomes an XLSX formula string that is itself
# double-quoted, and an embedded " makes Excel offer to repair the file.
OPT_NEEDED = ['Keep', 'Drop', 'Merge with another row', 'Split into several rows']
OPT_STRUCT = ['Yes', 'Repeats over the wrong thing', 'Should be a list',
              'Should be a single value']
OPT_PTIER  = ['Yes', 'Should be required', 'Should be optional',
              'Should not be in the procedure record']
OPT_STIER  = ['Yes', 'Should be required', 'Should be optional',
              'Should be fixed by the procedure', 'Should be adjustable']

# key, header, width, colour family, kind, dropdown options
COLSPEC = [
    ('num',      '#',                            7,  None,        'content', None),
    ('name',     'Metadata item',                31, 'item',      'content', None),
    ('needed',   'Needed?',                      17, 'item',      'review',  OPT_NEEDED),
    ('prose',    'What to report',               56, None,        'content', None),
    ('pstruct',  'Structure — procedure record', 28, 'procedure', 'content', None),
    ('pstructr', 'Structure right?',             16, 'procedure', 'review',  OPT_STRUCT),
    ('ptier',    'Procedure-Level Tier',         14, 'procedure', 'content', None),
    ('ptierr',   'Tier right?',                  16, 'procedure', 'review',  OPT_PTIER),
    ('sstruct',  'Structure — session record',   31, 'session',   'content', None),
    ('sstructr', 'Structure right?',             16, 'session',   'review',  OPT_STRUCT),
    ('stier',    'Session-Level Tier',           14, 'session',   'content', None),
    ('stierr',   'Tier right?',                  16, 'session',   'review',  OPT_STIER),
]
MODE_W, COMMENT_W = 10, 38
COMMENT_COL = ('comment', 'Comment', COMMENT_W, 'comment', 'review', None)


def colspec(modes):
    """Full column list: the fixed columns, one per mode, then the free-text comment."""
    spec = list(COLSPEC)
    for m in modes:
        spec.append(('mode:' + m, m, MODE_W, 'mode', 'content', None))
    spec.append(COMMENT_COL)
    return spec



def load():
    rows = list(csv.reader(open(SRC, encoding='utf-8-sig')))
    h = rows[0]
    sent = h.index('Literature Assessment')
    m0 = h.index('Purpose') + 1
    modes = h[m0:sent]
    out, sec, secname, idx = [], 0, '', 0
    for r in rows[1:]:
        if not r[2].strip() and not r[3].strip():
            if r[0].strip():
                sec += 1; secname = r[0].split('. ', 1)[-1]; idx = 0
            continue
        idx += 1
        out.append(dict(sec=sec, secname=secname, num='%d.%d' % (sec, idx), name=r[0].strip(),
                        C=r[2].strip(), D=r[3].strip(), key=r[8].strip(),
                        modes=''.join(x.strip() for x in r[m0:sent])))
    return out, modes


def build():
    fields, modes = load()
    missing = [f['name'] for f in fields if f['name'] not in PROSE]
    if missing:
        raise SystemExit('no sentence written for: %s' % missing)

    wb = Workbook()

    # ============================== sheet 1: preamble ==============================
    lg = wb.active; lg.title = 'How to read and review'
    lg.sheet_view.showGridLines = False
    r = 1
    def head(txt, size=14):
        nonlocal r
        c = lg.cell(row=r, column=1, value=txt); c.font = Font(bold=True, size=size); r += 1
    def para(txt):
        nonlocal r
        c = lg.cell(row=r, column=1, value=txt)
        c.alignment = Alignment(wrap_text=True, vertical='top')
        lg.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
        lg.row_dimensions[r].height = 15 * (1 + len(txt) // 150); r += 1
    def rows_(pairs):
        nonlocal r
        for label, meaning, colour in pairs:
            a = lg.cell(row=r, column=1, value=label)
            a.font = Font(bold=True, size=11, color=colour or '000000')
            a.alignment = Alignment(vertical='top', wrap_text=True); a.fill = LEGEND_FILL
            b = lg.cell(row=r, column=2, value=meaning)
            b.alignment = Alignment(wrap_text=True, vertical='top'); r += 1
        r += 1

    head('EPMA metadata — reviewer workbook (EPMA TAPP v77)')
    para('Every item is documented twice: once in the procedure record, the standing recipe that is '
         'registered and cited by DOI, and once in the session record, which describes one analytical '
         'session run under it. One session may cover several samples. Read this sheet first, then '
         'review the table on the next sheet.')
    r += 1

    head('Which record an item belongs to', 12)
    para('An item belongs to the procedure when it can be decided before any analysis is run. It '
         'belongs to the session alone when its value can only be known once the session has taken '
         'place — who ran it and when, what was analysed, and every measured outcome.')
    rows_([('Procedure-Level Tier', 'Basic = the procedure cannot be registered without it. Advanced = strongly recommended but may be left out. N/A = not part of the procedure record.', None),
           ('Session-Level Tier',  'Read-Only = fixed by the procedure; a session that changes it is running a different procedure. Editable = set by the procedure but may be adjusted within the bounds it allows, and the session records the value used. Basic = the session must report it. Advanced = the session should report it.', None)])
    rows_([('Basic', 'Required', 'C00000'), ('Advanced', 'Recommended', '375623'),
           ('Read-Only', 'Fixed by the procedure', '0070C0'),
           ('Editable', 'Adjustable within procedure-defined bounds', '7030A0'),
           ('N/A', 'Not applicable at that level', '808080')])

    head('How many values — the two structure columns', 12)
    para('Each record has two columns of its own — what it holds, and its tier — colour-coded '
         'blue for the procedure record and green for the session record. Structure is stated '
         'separately for the two records because some lists do not exist until a session runs. '
         'Three phrasings are used:')
    rows_([('One value per …', 'A single value.', None),
           ('One or more values per …', 'Several values may be given, but nothing else is reported per them.', None),
           ('List of entries per …', 'An itemised list. Other rows are reported per entry of this list, so the list has to be established first.', None)])
    para('What follows "per" is the name of the row that establishes the list, not a general term, '
         'and the whole chain is spelled out from the inside outwards. Beam Current reads "One value '
         'per Sampling Unit Name per Sample Name": one value for each analysis point, within each '
         'sample. "Per procedure" or "per session" appears only where nothing repeats at all. Where '
         'two lists cross rather than nest, they are joined with ×, outer first: "One value per '
         'Secondary Reference Material × Reported Variable" means one value for each reported '
         'variable, within each reference material.')
    rows_([('Sample Name', 'the list of samples analysed in the session', None),
           ('Sampling Unit Name', 'the list of analysis points or areas, per sample', None),
           ('Target Species', 'the list of elements the procedure determines', None),
           ('Monitored Element', 'the list in "Monitored Elements" — what is measured to determine those elements', None),
           ('Reported Variable', 'the list in "Reported Variables and Units"', None),
           ('Secondary Reference Material', 'the list in "Secondary Reference Materials"', None)])
    para('Cells shaded pale yellow in the procedure column are the ones we are least sure of. The '
         'item repeats over samples or analysis points, which the procedure record cannot name, so '
         'the per-unit detail appears only in the session column. Four of them — beam mode, current, '
         'diameter and damage minimisation — are written "one or more values per procedure" because '
         'published procedures state them per phase or material (20 nA for olivine and pyroxene, '
         '10 nA for maskelynite and phosphate, and so on), which no list in this table names. Hover '
         'over a shaded cell for what the literature shows. Tell us whether the procedure record '
         'should ask for these per phase or material type, and if so, who supplies that list.')
    r += 1

    head('Modes', 12)
    para('The four columns on the right are the analytical modes this technique covers. ✓ means the '
         'item applies to that mode; – means it does not. Within each group, rows that repeat over the '
         'same thing in the same modes are kept together and separated by a rule. Every row carries '
         'its own values, so sorting or filtering the sheet loses nothing.')
    r += 1

    head('What we are asking you', 12)
    para('Six columns are for your review, and each one sits immediately to the right of the column '
         'it judges and carries the same colour: "Needed?" beside the metadata item, "Structure '
         'right?" beside each structure column, "Tier right?" beside each tier column, and one free-'
         'text "Comment" at the end of the row. All but the last are drop-downs, so answers can be '
         'tallied. Review columns are shaded; content columns are not.')
    rows_([('Needed?', 'Keep · Drop · Merge with another row · Split into several rows. "Split" is the one to use when a single row is really several things a laboratory would report separately.', '7030A0'),
           ('Structure right?', 'One beside each structure column: Yes · Repeats over the wrong thing (the "per" names the wrong list) · Should be a list · Should be a single value. Judge the procedure and session columns separately — they often differ.', None),
           ('Tier right? (procedure)', 'Yes · Should be required · Should be optional · Should not be in the procedure record.', '2F5597'),
           ('Tier right? (session)', 'Yes · Should be required · Should be optional · Should be fixed by the procedure · Should be adjustable.', '548235'),
           ('Comment', 'Anything else, including the wording of "What to report".', '833C0B')])
    para('A note on wording: this workbook says "session" throughout for what the underlying TAPP '
         'calls the analysis level, because "analysis" is easily read as one analysis point, which is '
         'the one thing the record is not. "Session level" here is the TAPP\'s Analysis-Level Tier.')
    para('This workbook is generated from EPMA_TAPP_v77.csv and is a snapshot of that version. '
         'Data types, allowed values and examples are deliberately not shown; they are reviewed '
         'separately against the TAPP itself.')
    lg.column_dimensions['A'].width = 31
    lg.column_dimensions['B'].width = 104
    lg.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    lg.page_setup.orientation = 'landscape'
    lg.page_setup.fitToWidth = 1
    lg.page_setup.fitToHeight = 0

    # ============================== sheet 2: the table ==============================
    ws = wb.create_sheet('EPMA metadata table')
    ws.sheet_view.showGridLines = False
    spec = colspec(modes)
    ncols = len(spec)
    idx = {c[0]: i + 1 for i, c in enumerate(spec)}
    hdr = 1
    for j, (key, header, width, fam, kind, opts) in enumerate(spec, start=1):
        c = ws.cell(row=hdr, column=j, value=header)
        f = FAMILY.get(fam)
        if kind == 'review':
            c.fill = PatternFill('solid', fgColor=f['mid'])
            c.font = Font(bold=True, size=11, color='1F2A44')
        else:
            c.fill = PatternFill('solid', fgColor=f['dark'] if f else '44546A')
            c.font = Font(bold=True, size=11, color='FFFFFF')
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        c.border = BORDER
        ws.column_dimensions[get_column_letter(j)].width = width
    ws.row_dimensions[hdr].height = 40

    row = hdr + 1
    flagged = []
    sections = sorted({f['sec'] for f in fields})
    for si, sec in enumerate(sections):
        members_all = [f for f in fields if f['sec'] == sec]
        if si:                                   # one blank row between groups
            row += 1
        for j in range(1, ncols + 1):
            cell = ws.cell(row=row, column=j); cell.fill = SECTION_FILL; cell.border = BORDER
        ws.cell(row=row, column=1, value=str(sec)).font = Font(bold=True, size=12)
        ws.cell(row=row, column=2, value=members_all[0]['secname']).font = Font(bold=True, size=12)
        ws.row_dimensions[row].height = 22
        row += 1

        # Rows are grouped by what they repeat over and by mode; the groups carry no
        # header of their own, only a rule above the first row of each.
        groups = collections.OrderedDict()
        for f in members_all:
            sess, _ = phrase(f['name'], f['key'], 'session')
            groups.setdefault((sess.split(' per ', 1)[-1] if ' per ' in sess else sess,
                               f['modes']), []).append(f)

        for gi, ((per, modepat), members) in enumerate(groups.items()):
            for f in members:
                proc, flag = phrase(f['name'], f['key'], 'procedure')
                if f['C'] == 'N/A':
                    proc, flag = '—', False
                sess_f, _ = phrase(f['name'], f['key'], 'session')
                if flag:
                    flagged.append(f['name'])
                values = {'num': f['num'], 'name': f['name'], 'prose': PROSE[f['name']],
                          'pstruct': proc, 'ptier': f['C'],
                          'sstruct': sess_f, 'stier': f['D']}
                for k, ch in zip(modes, f['modes']):
                    values['mode:' + k] = '✓' if ch == 'Y' else '–'
                top = Side(style='thin', color='7F7F7F') if (f is members[0] and gi) else THIN
                for j, (key, header, width, fam, kind, opts) in enumerate(spec, start=1):
                    cell = ws.cell(row=row, column=j, value=values.get(key))
                    cell.border = Border(left=THIN, right=THIN, top=top, bottom=THIN)
                    if kind == 'review':
                        cell.fill = PatternFill('solid', fgColor=FAMILY[fam]['pale'])
                        cell.alignment = Alignment(wrap_text=True, vertical='top')
                    elif key in ('ptier', 'stier'):
                        colour, bold = TIER_STYLE.get(cell.value, ('000000', False))
                        cell.font = Font(bold=bold, color=colour, size=11)
                        cell.alignment = Alignment(horizontal='center', vertical='top')
                    elif key.startswith('mode:'):
                        tick = cell.value == '✓'
                        cell.font = Font(bold=tick, size=11,
                                         color='375623' if tick else 'BFBFBF')
                        cell.alignment = Alignment(horizontal='center', vertical='top')
                    elif key == 'name':
                        cell.font = Font(bold=True, size=11)
                        cell.alignment = Alignment(vertical='top', wrap_text=True)
                    else:
                        cell.alignment = Alignment(wrap_text=(key == 'prose'), vertical='top')
                if flag:
                    c = ws.cell(row=row, column=idx['pstruct'])
                    c.fill = FLAG_FILL
                    note = REVIEW_NOTE.get(f['name'], '')
                    c.comment = Comment((note + NOTE_TAIL).strip(), 'TAPP review',
                                        height=130, width=330)
                row += 1

    for j, (key, header, width, fam, kind, opts) in enumerate(spec, start=1):
        if kind == 'review' and opts:
            col = get_column_letter(j)
            dv = DataValidation(type='list', formula1='"%s"' % ','.join(opts),
                                allow_blank=True)
            dv.prompt = header; dv.promptTitle = header
            ws.add_data_validation(dv)
            dv.add('%s%d:%s%d' % (col, hdr + 1, col, row - 1))
    ws.freeze_panes = ws.cell(row=hdr + 1, column=4)
    ws.auto_filter.ref = 'A%d:%s%d' % (hdr, get_column_letter(ncols), row - 1)
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    ws.page_setup.orientation = 'landscape'
    ws.page_setup.paperSize = 8
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.print_title_rows = '%d:%d' % (hdr, hdr)

    # ============================== sheet 3: traceability ==========================
    tr = wb.create_sheet('Structure key (traceability)')
    tr.sheet_view.showGridLines = False
    for j, h in enumerate(['#', 'Metadata item', 'TAPP "Keyed By" (Column I)',
                           'Structure — procedure record', 'Structure — session record'], start=1):
        c = tr.cell(row=1, column=j, value=h)
        c.font = Font(bold=True, size=11, color='FFFFFF'); c.fill = HEAD_FILL
        c.alignment = Alignment(horizontal='center', wrap_text=True)
    for i, f in enumerate(fields, start=2):
        proc, flag = phrase(f['name'], f['key'], 'procedure')
        if f['C'] == 'N/A':
            proc = '—'
        sess, _ = phrase(f['name'], f['key'], 'session')
        for j, v in enumerate([f['num'], f['name'], f['key'], proc, sess], start=1):
            cell = tr.cell(row=i, column=j, value=v)
            cell.alignment = Alignment(wrap_text=True, vertical='top')
        if flag:
            tr.cell(row=i, column=4).fill = FLAG_FILL
    for col, w in zip('ABCDE', [7, 34, 40, 30, 32]):
        tr.column_dimensions[col].width = w
    tr.freeze_panes = 'A2'
    tr.auto_filter.ref = 'A1:E%d' % (len(fields) + 1)

    wb.save(OUT)
    return OUT, len(fields), sorted(set(flagged))


if __name__ == '__main__':
    out, n, flagged = build()
    print('read   %s' % SRC)
    print('wrote %s — %d fields' % (out, n))
    print('procedure-level cells flagged (session-only domain stripped): %d' % len(flagged))
    for f in flagged:
        print('   -', f)
