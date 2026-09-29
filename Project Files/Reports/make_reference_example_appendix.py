#!/usr/bin/env python3
"""
Append Appendix A (field coverage) to EPMA_Reference_Procedure_Example_v77.md.

The coverage table is generated, not hand-written, so the claim "every TAPP field is
covered" is checked rather than asserted:
  * field list, order and keys come from the TAPP CSV;
  * the "Reported per" wording comes from make_review_workbook.phrase(), so it matches
    the reviewer workbook exactly;
  * "Stated in" counts literature-assessment columns with a non-blank, non-N value;
  * LOCATION is the only hand-written part, and the script fails if any field lacks one
    or names a table/section the document does not contain.
Re-running replaces the appendix rather than appending a second copy.
"""
import csv, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_review_workbook as mrw

# Each edition is pinned to the TAPP version it documents, so re-running after a bump never silently
# describes a newer TAPP. `python3 make_reference_example_appendix.py` rebuilds the v77 record;
# `... v86` builds the v86 edition.
VERSION = sys.argv[1] if len(sys.argv) > 1 else 'v77'
# Note (2026-09-29): regenerating v77 now differs from the committed v77 file in four "Procedure:
# reported per" cells (the beam fields). phrase() in make_review_workbook.py no longer special-cases
# them as "One or more values per procedure", because they are keyed by target material since v79. The
# committed v77 file is the record of what was generated at the time; do not regenerate it.
DOC = os.path.join(HERE, 'EPMA_Reference_Procedure_Example_%s.md' % VERSION)
_SRCS = {'v77': os.path.join(HERE, '..', '..', 'Superseded TAPPs', '2026-09-28', 'EPMA_TAPP_v77.csv')}
import glob as _glob
SRC = _SRCS.get(VERSION) or next(iter(
    _glob.glob(os.path.join(HERE, '..', '..', 'Current TAPPs', 'EPMA_TAPP_%s.csv' % VERSION))
    + _glob.glob(os.path.join(HERE, '..', '..', 'EPMA', 'EPMA_TAPP_%s.csv' % VERSION))
    + _glob.glob(os.path.join(HERE, '..', '..', 'Superseded TAPPs', '*', 'EPMA_TAPP_%s.csv' % VERSION))))
MARK = '\n---\n\n## Appendix A'

LOCATION = {
 'Procedure Name': '§1.1', 'Technique': '§1.1', 'Procedure Author': '§1.1',
 'Laboratory': '§1.1; §2.1', 'Laboratory ID': '§1.1',
 'Procedure Start Date': '§1.1', 'Funding Source for Procedure Development': '§1.1',
 'Procedure Reference(s)': '§1.1', 'Procedure DOI': '§2.1', 'Session Identifier': '§2.1',
 'Analyst': '§2.1', 'Analysis Start Date': '§2.1', 'Analysis End Date': '§2.1',
 'Funding Source for Analysis': '§2.1', 'Coupled Technique(s)': '§1.2; §2.1',
 'Coupling Description': '§1.2; §2.1', 'Coupled Procedure DOI': '§2.1',
 'Coupled Dataset or Publication Reference': '§2.1',
 'Target Material': '§1.3', 'Sample Preparation Method': '§1.3; Table 9',
 'Sample Name': 'Table 9', 'Sampling Unit Type': '§1.3', 'Sampling Unit Name': 'Table 10',
 'Sample Persistent Identifier': 'Table 9', 'Sampling Unit Selection Criteria': '§1.3',
 'Pre-Analysis Imaging and Screening': '§1.3; Table 9',
 'Instrument Manufacturer': '§1.4', 'Instrument Model': '§1.4', 'Electron Source': '§1.4',
 'Acquisition Software': '§1.4; §2.3', 'Data Processing Software(s)': '§1.4; §2.3',
 'WDS Spectrometer Configuration': '§1.4', 'EDS Detector Configuration': '§1.4',
 'Analytical Mode': '§1.5', 'Beam Mode': 'Table 1; Table 10',
 'Accelerating Voltage': '§1.5; §2.3', 'Beam Current': 'Table 1; Table 10',
 'Beam Diameter': 'Table 1; Table 10', 'Beam Raster Dimensions': 'Table 1; Table 10',
 'Beam Damage Minimization': 'Table 1; Table 10', 'Drift Correction': '§1.5',
 'Target Species': '§1.6; Table 2', 'Monitored Elements': '§1.6; Table 3',
 'Reported Variables and Units': 'Table 4', 'EPMA Technique per Target Species': 'Table 2',
 'X-ray Line': 'Table 3', 'Diffracting Crystal': 'Table 3',
 'WDS Spectrometer Channel': 'Table 3', 'Sequence': 'Table 3; §1.6',
 'Proportional Counter / Detector': 'Table 3', 'WDS PHA Setting': 'Table 3',
 'Peak Counting Time': 'Table 3b; §2.3', 'Background Counting Time': 'Table 3b; §2.3',
 'Background Position(s)': 'Table 3b', 'EDS Live Time per Point or Pixel': '§1.7',
 'EDS Acquisition Mode': '§1.7', 'Dwell Time per Pixel': 'Table 3b; §1.8',
 'Step Size / Pixel Size': '§1.8', 'Map Dimensions': '§2.3', 'Map Area': '§2.3',
 'Stage Scan vs. Beam Scan': '§1.8',
 'Matrix Correction Method': '§1.9', 'Mass Absorption Coefficients (MACs)': '§1.9',
 'X-ray Background Correction Method': 'Table 3b',
 'Time-Dependent Intensity Correction': 'Table 5',
 'Target Species Estimation Method': 'Table 2', 'Halogen Correction on Oxygen': '§1.9',
 'WDS Dead Time Correction': '§1.9', 'EDS Spectral Processing Type': '§1.9',
 'Blank Correction': 'Table 5', 'Normalization / Standards-Based Correction': 'Table 6',
 'Calibration Factor and Determination Method': '§1.9',
 'Procedural Blank Level': '§2.4', 'Analysis Inclusion and Rejection Criteria': '§1.9; §2.4',
 'Constants and Reference Values Used': '§1.9',
 'Primary Calibration Standard Name': 'Table 2',
 'Secondary Reference Materials': 'Table 7',
 'X-ray Line Overlap Corrections Applied': 'Table 5', 'Interfering Elements': 'Table 5',
 'Interference Correction Standard': 'Table 5',
 'Detection Limit': 'Table 6; Table 11', 'Detection Limit Method': 'Table 6',
 'Analytical Precision': 'Table 8; Table 12', 'Analytical Accuracy': 'Table 8; Table 12',
 'Counting Statistics Error': 'Table 6; Table 13', 'EDS Dead Time': '§2.4',
 'Goodness-of-Fit or Dispersion Statistic': 'Table 14',
 'Additional Notes': '§2.5',
}

APPENDIX_B = """
## Appendix B — What the example needed that the TAPP structure cannot hold

Writing the example to 100% coverage exposed six places where complete documentation needs a structure the TAPP does not yet declare. The example handles each one as noted. These are questions for the TAPP, not faults in the example.

1. **Beam conditions vary by phase at procedure level.** Table 1 states them per phase group, and so do 7 of the 15 assessed procedures. However, the TAPP keys these fields by *Sampling Unit Name per Sample Name*, a list that does not exist until a session runs. So at procedure level the TAPP can say only "one or more values per procedure". No list of phase groups is declared. Counting times are the same problem one step further on: Zega et al. (2025) give them by phase, but the TAPP keys them by monitored element only. The example therefore uses one counting time per element.
2. **Per-element values can differ between modes.** Two fields hit this:
   - `X-ray Background Correction Method`: Table 3b holds two values per cell, two-point off-peak for points and MAN for maps.
   - `WDS Spectrometer Channel`: §1.8 reassigns P and Ni to other spectrometers for mapping, so that all five mapped elements fit in one pass.

   Both fields are keyed by monitored element and apply to more than one mode, so neither can say which value belongs to which mode.
3. **Aggregate statistics belong to a phase mean.** The inclusion outcome (§2.4) and the dispersion statistic (Table 14) describe means per phase per sample. The TAPP keys the dispersion statistic by *Reported Variable* alone, so Table 14 names the phase in its title rather than in a column the TAPP defines.
4. **Technique is chosen element by element within one mode.** Crystal, spectrometer, detector, PHA and counting times are WDS-only fields keyed by monitored element. In a combined WDS+EDS point analysis, 5 of the 17 monitored elements are measured by EDS, so those fields do not apply to them. The mode flags work per mode, not per element, so Table 3 fills these cells with "—".
5. **Preparation can differ by sample.** In this session EX-CC-02 was ion-polished and EX-CC-01 was not, so Table 9 reports preparation per sample. `Sample Preparation Method` is keyed `(none)`: one value per session. This is despite Rule 13's own premise that a session may cover samples "each with its own identity and possibly its own preparation".
6. **Target species with no monitored element.** O and C are determined by stoichiometry and have no entry under *Monitored Elements*. The TAPP allows this, but nothing states it. A consumer that expects every target species to have at least one monitored element would fail on them.
"""


# v86: the fields gaps 1, 3 and 4 added or re-keyed, located in the v86 edition.
LOCATION_V86 = dict(LOCATION)
del LOCATION_V86['EPMA Technique per Target Species']
LOCATION_V86.update({
 'Target Material': '§1.3; Table 1; Table 2b',
 'Target Material of Sampling Unit': 'Table 10',
 'Beam Mode': 'Table 1; §2.3', 'Beam Current': 'Table 1; §2.3', 'Beam Diameter': 'Table 1; §2.3',
 'Beam Raster Dimensions': 'Table 1; §2.3', 'Beam Damage Minimization': 'Table 1; §2.3',
 'Mapping Beam Mode': '§1.5; §2.3', 'Mapping Beam Current': '§1.5; §2.3', 'Mapping Beam Diameter': '§1.5; §2.3',
 'X-ray Detection Method per Monitored Element': 'Table 3',
 'Primary Calibration Standard Name': 'Table 2b',
 'Combination Method': '§1.9', 'Combined Results': 'Table 14',
 'Analysis Inclusion and Rejection Criteria': '§1.9; Table 14',
 'Goodness-of-Fit or Dispersion Statistic': 'Table 15', 'Other Statistics': 'Table 15',
})

APPENDIX_B_V86 = """
## Appendix B — The six gaps the v77 edition exposed, at v86

Writing the v77 edition to 100% coverage exposed six places where complete documentation needed a
structure the TAPP did not declare (`EPMA_Reference_Procedure_Example_v77.md`, Appendix B). Four
were closed by v86, and two are held.

1. **Beam conditions vary by phase — closed.** `Target Material` is now a list that beam conditions are
   stated against (Table 1), and each analysis point names its target material (Table 10). Maps have
   their own beam fields (§1.5, §2.3), since Liu et al. (2016) ran one material at 20 nA for points and
   200 nA for maps. *Held:* counting times per phase, which only Zega et al. (2025) state; the example
   still uses one counting time per element.
2. **Per-element values that differ between modes — held.** Table 3b still gives two background methods in
   one cell (two-point off-peak for points, MAN for maps), and §1.8 still reassigns P and Ni for mapping.
   None of the 15 assessed procedures states such a difference, so the TAPP waits for one that does.
3. **Statistics on combined values — closed.** Combined results are a session list (Table 14). The inclusion
   outcome is given per combined result, and the dispersion and other statistics per combined result and
   reported variable (Table 15). How each variable is combined is stated in §1.9.
4. **WDS or EDS chosen element by element — closed.** The detection method is stated per monitored element
   (Table 3), including Zn, which serves no target species. The WDS-only columns are still marked "—" for EDS
   elements. A general mechanism for applicability conditional on another field's value was deferred.
5. **Preparation differs by sample — closed.** Preparation is registered once and reported per sample
   (Table 9).
6. **Target species with no monitored element — closed.** The TAPP now says that a species determined by
   stoichiometry or by difference has none (O and C here).

**One further finding, from the literature rather than the example.** Nine of the 15 assessed papers
state their geometry (point analyses or maps) without naming WDS or EDS. `Analytical Mode` pairs the
two, so those papers cannot give it a value. Splitting EPMA's modes into geometry × detector is held.
"""


def stated(v):
    v = v.strip()
    return bool(v) and v.upper() not in ('N', 'N/A', 'NONE', 'NOT STATED', '—', '-')


def main():
    rows = list(csv.reader(open(SRC, encoding='utf-8-sig')))
    h = rows[0]
    sent = h.index('Literature Assessment')
    lit = [i for i in range(sent + 1, len(h)) if h[i].strip()]
    location = LOCATION_V86 if VERSION != 'v77' else LOCATION
    fields, missing, bad = [], [], []
    doc = open(DOC, encoding='utf-8').read()
    body = doc.split(MARK)[0]
    sec, idx = 0, 0
    for r in rows[1:]:
        if not r[2].strip() and not r[3].strip():
            if r[0].strip():
                sec += 1; idx = 0
            continue
        idx += 1
        name = r[0].strip()
        loc = location.get(name)
        if loc is None:
            missing.append(name); continue
        for ref in [x.strip() for x in loc.split(';')]:
            anchor = ('### ' + ref[1:] + ' ') if ref.startswith('§') else ('**' + ref + '.')
            if anchor not in body:
                bad.append((name, ref))
        n = sum(stated(r[i]) if i < len(r) else 0 for i in lit)
        proc, _ = mrw.phrase(name, r[8].strip(), 'procedure')
        if r[2].strip() == 'N/A':
            proc = '—'
        sess, _ = mrw.phrase(name, r[8].strip(), 'session')
        fields.append(('%d.%d' % (sec, idx), name, r[2].strip(), proc, r[3].strip(), sess, loc, n))
    extra = set(location) - {f[1] for f in fields}
    if missing or bad or extra:
        sys.exit('missing location: %s\nbad reference: %s\nunknown field: %s' % (missing, bad, sorted(extra)))

    out = [MARK.lstrip('\n'), ' — Field coverage\n',
           '\n*Generated from %s by `make_reference_example_appendix.py`. It covers every field in the TAPP, in TAPP order. '
           '"Reported per" uses the same wording as the reviewer workbook. "Stated in" counts how many of the %d assessed procedures report the field. '
           '0 means this example had to add the content.*\n\n' % (os.path.basename(SRC), len(lit)),
           '| # | TAPP field | Procedure tier | Procedure: reported per | Session tier | Session: reported per | Where in this document | Stated in |\n',
           '|---|---|---|---|---|---|---|---|\n']
    for num, name, c, proc, d, sess, loc, n in fields:
        out.append('| %s | %s | %s | %s | %s | %s | %s | %d / %d |\n' % (num, name, c, proc, d, sess, loc, n, len(lit)))
    added = sum(1 for f in fields if f[7] == 0)
    out.append('\n**%d fields covered of %d.** %d are stated in none of the assessed procedures, and %d in two or fewer.\n'
               % (len(fields), len(fields), added, sum(1 for f in fields if f[7] <= 2)))
    out.append(APPENDIX_B if VERSION == 'v77' else APPENDIX_B_V86)
    open(DOC, 'w', encoding='utf-8').write(body.rstrip('\n') + '\n' + '\n'.join([''.join(out)]))
    print('fields covered: %d; stated in none: %d; references checked: all resolve' % (len(fields), added))


if __name__ == '__main__':
    main()
