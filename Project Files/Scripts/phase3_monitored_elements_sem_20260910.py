#!/usr/bin/env python3
"""Phase 3 for `Monitored Elements` in SEM (35 columns) and SEM_Composition (9).

SEM_Composition's nine columns are the same nine EDS procedures that appear in SEM, so one
reading serves both and the shared cells are written identically.

TWO KINDS OF CELL.

1. `N/A` for the 26 SEM columns whose procedure is not an X-ray-spectrometry mode — SE and BSE
   imaging, CL mapping, EBSD, FIB TEM-sample preparation, 3D tomography. Nothing is monitored
   because no X-ray spectrum is acquired. This is not a gap in the literature; it is the field
   not applying, which is what `N/A` means and what the field's own mode flags already say
   (`Monitored Elements` is flagged Y only for the four EDS/WDS modes). The mode is read from
   each column header rather than hardcoded, so a re-ordered or added column cannot be
   mis-assigned.

2. The nine EDS columns, read from six papers in this session.

THE RESULT IS THIN, AND THAT IS THE FINDING. Of the nine EDS procedures, exactly ONE
enumerates the elements it monitored — Barnes et al. 2025, "multi-element EDS mapping (Mg,
Si, Fe, Ni, S, Na, Ca and Al)" (p.11). One more, Gucsik et al. 2013, names eight elements but
attaches them to its WDS X-ray maps, not to the EDS, and that limit is written into the cell.
The other seven describe the detector, the accelerating voltage and the acquisition time
without ever saying what was measured. SEM-EDS acquires a full spectrum, so a paper can report
compositions without ever declaring an element set — which is precisely why this field cannot
be filled by inference from the results tables.

Pascucci et al. 2026 is the trap worth naming: it DOES list "Si, Fe, Ca, Al, and S" (p.6), but
that is the element set of its EMPA-WDS mapping on a JEOL JXA/8230 — a different instrument
from the Zeiss Supra 40 FE-SEM these two columns record. Reading it into the SEM-EDS cells
would be a cross-instrument error of exactly the kind Column A separates procedures to prevent.
"""

import csv, io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATE = "2026-09-10"
FIELD = "Monitored Elements"
TAPPS = [("SEM/SEM_TAPP_v64.csv", "SEM/SEM_TAPP_v65.csv"),
         ("SEM/SEM_Composition_TAPP_v63.csv", "SEM/SEM_Composition_TAPP_v64.csv")]

EDS = {
"Genge et al. 2025":
  "N — \"quantitative EDS analyses (with an Oxford X-Max SDD system and an XPP correction "
  "procedure calibrated with Oxford factory internal standards) were carried out at 10 kV\" (p.2), "
  "to determine the composition of the Al-Cu alloy phases and associated minerals; no element set "
  "is enumerated",
"Gucsik et al. 2013":
  "Mg, Al, Ca, Si, Ti, Cr, Mn, Fe — \"Among the detected elements were Mg, Al, Ca, Si, Ti, Cr, Mn, "
  "and Fe\" (p.2). NOTE the sentence attaches these to the WDS X-ray distribution maps; the EDS "
  "itself is described only as \"semiquantitative analyses for major elements\" and \"qualitative "
  "measurements by EDS\", so the EDS element set is not separately stated",
"Izawa et al. 2010 | EDS Mapping":
  "N — the Leo 440 SEM carries \"a Gresham light element detector and a Quartz XOne EDX analysis "
  "system, capable of detecting all elements from C to U, with a detection limit of ~0.5 wt% for "
  "most elements\" (p.3). That is the detector's range, not the set monitored; the maps' elements "
  "are not enumerated",
"Izawa et al. 2010 | EDS Point Analysis":
  "N — the Leo 1540 FIB/SEM CrossBeam is \"equipped with an Oxford Instruments INCA EDX system "
  "allowing for elemental analysis\" (p.3); no element set is stated",
"Pascucci et al. 2026":
  "N — the Zeiss Supra 40 FE-SEM carries an Oxford INCA Energy 350 EDS with an X-ACT SDD (p.3), but "
  "no element set is given for the SEM-EDS work. The paper's \"Si, Fe, Ca, Al, and S\" list (p.6) "
  "belongs to its EMPA-WDS mapping on a JEOL JXA/8230 — a different instrument and a different "
  "procedure — and is deliberately not read across",
"Zega et al. 2025 | EDS Point Analysis":
  "N — \"EDS spectra were acquired at 15 kV with acquisition times ranging from 20 to 200 s with an "
  "incident beam current of ~900 pA\" on the JEOL 7600F (p.9); no element set is stated",
"Zega et al. 2025 | EDS Mapping":
  "N — \"The compositional heterogeneity of the particles was assessed through EDS mapping\" on the "
  "Hitachi S-4800 (p.9); no element set is stated",
"Barnes et al. 2025":
  "Mg, Si, Fe, Ni, S, Na, Ca, Al — \"multi-element EDS mapping (Mg, Si, Fe, Ni, S, Na, Ca and Al) of "
  "the different grains\" (p.11)",
}

NA = ("N/A — this procedure is %s. No X-ray spectrum is acquired, so no element is monitored; "
      "`Monitored Elements` is flagged N for this mode in the mode-flag columns")


def value_for(header):
    hs = " ".join(header.split())
    parts = [p.strip() for p in hs.split("|")]
    mode = re.sub(r"\s*\(.*$", "", parts[-1]).strip() if len(parts) >= 3 else ""
    if "EDS" not in mode and "WDS" not in mode:
        return NA % mode, mode
    hits = [k for k in EDS if all(p.strip().lower() in hs.lower() for p in k.split("|"))]
    if len(hits) != 1:
        raise SystemExit("  !! %d EDS match(es) for %s" % (len(hits), hs[:70]))
    return EDS[hits[0]], mode


def main(apply=False):
    for rel, new in TAPPS:
        rows = list(csv.reader(io.open(os.path.join(ROOT, rel), newline="", encoding="utf-8-sig")))
        h = rows[0]; s = h.index("Literature Assessment")
        iU = h.index("Last Update")
        lit = [i for i in range(s + 1, len(h)) if h[i].strip()]
        row = next(r for r in rows[1:] if r and r[0].strip() == FIELD)
        while len(row) < len(h): row.append("")
        na = eds = 0
        for i in lit:
            if row[i].strip():
                print("  !! already filled: %s" % h[i][:40]); return 1
            v, mode = value_for(h[i])
            row[i] = v
            if v.startswith("N/A"): na += 1
            else: eds += 1
        row[iU] = DATE
        print("  %-34s %d columns: %d N/A (non-spectrometry modes), %d EDS"
              % (os.path.basename(rel), len(lit), na, eds))
        if apply:
            with io.open(os.path.join(ROOT, new), "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
            print("      wrote %s" % os.path.basename(new))
    if not apply:
        print("\n(dry run — pass --apply to write)")
    return 0


sys.exit(main("--apply" in sys.argv))
