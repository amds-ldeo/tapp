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

DOC = os.path.join(HERE, 'EPMA_Reference_Procedure_Example_v77.md')
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


def stated(v):
    v = v.strip()
    return bool(v) and v.upper() not in ('N', 'N/A', 'NONE', 'NOT STATED', '—', '-')


def main():
    rows = list(csv.reader(open(mrw.SRC, encoding='utf-8-sig')))
    h = rows[0]
    sent = h.index('Literature Assessment')
    lit = [i for i in range(sent + 1, len(h)) if h[i].strip()]
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
        loc = LOCATION.get(name)
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
    extra = set(LOCATION) - {f[1] for f in fields}
    if missing or bad or extra:
        sys.exit('missing location: %s\nbad reference: %s\nunknown field: %s' % (missing, bad, sorted(extra)))

    out = [MARK.lstrip('\n'), ' — Field coverage\n',
           '\n*Generated from %s by `make_reference_example_appendix.py`. It covers every field in the TAPP, in TAPP order. '
           '"Reported per" uses the same wording as the reviewer workbook. "Stated in" counts how many of the %d assessed procedures report the field. '
           '0 means this example had to add the content.*\n\n' % (os.path.basename(mrw.SRC), len(lit)),
           '| # | TAPP field | Procedure tier | Procedure: reported per | Session tier | Session: reported per | Where in this document | Stated in |\n',
           '|---|---|---|---|---|---|---|---|\n']
    for num, name, c, proc, d, sess, loc, n in fields:
        out.append('| %s | %s | %s | %s | %s | %s | %s | %d / %d |\n' % (num, name, c, proc, d, sess, loc, n, len(lit)))
    added = sum(1 for f in fields if f[7] == 0)
    out.append('\n**%d fields covered of %d.** %d are stated in none of the assessed procedures, and %d in two or fewer.\n'
               % (len(fields), len(fields), added, sum(1 for f in fields if f[7] <= 2)))
    out.append(APPENDIX_B)
    open(DOC, 'w', encoding='utf-8').write(body.rstrip('\n') + '\n' + '\n'.join([''.join(out)]))
    print('fields covered: %d; stated in none: %d; references checked: all resolve' % (len(fields), added))


if __name__ == '__main__':
    main()
