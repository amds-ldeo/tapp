#!/usr/bin/env python3
"""Close the Lab-XCT Phase 3 extraction gap, and localise one Column F.

The gap was shaped, not random: 0 of 55 Lab-XCT native rows were unextracted, against 10 of 34
module-composed rows. Every gap was a field that arrived by composition, so the Phase 3 pass had
evidently been run against the technique-specific field list. Two of the ten are mandatory —
`Sampling Unit` (Rule 9) and `Reported Variables and Units` (Rule 8) — which is why the Lab-XCT
`sampling unit` key was unvalidated and the VOI-vs-sampling-unit question looked open.

Every value below was read from the source PDF in the session that wrote this script, per the
Source Rule in lit_assessment.md. `N` = applicable but not stated. Group header rows take `N`,
matching the convention every other TAPP follows (Lab-XCT had them blank).

Also fixes `Reported Variables and Units` Column F, which still carried the generic library
examples (d56Fe, 206Pb/238U dates) for a technique that reports volumes, modal mineralogy and
porosity. Column F is consumer-owned under Module_Core, so this is a TAPP-level edit.
"""
import csv, os, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
SRC = os.path.join(ROOT, "XCT", "Lab-XCT_TAPP_v37.csv")   # composed to the NEW version; v36 is preserved as published
DATE = "2026-09-01"

# columns 1..14 in lit-assessment order
M = {
"Session Identifier": [
 "N (scan record dated 29 October 2024; operator named, no session identifier assigned)",
 "N","N","N","N","N","N","N","N","N","N","N","N","N"],

"Instrument Manufacturer": [
 "Nikon","Zeiss","North Star Imaging","North Star Imaging","Nikon","Nikon","Nikon","Nikon",
 "Bruker","Zeiss","Nikon","Nikon",
 'GE / Waygate (stated as "Phoenix Nanotom S")',
 'Zeiss (stated as "XRADIA XRM500")'],

"Analytical Mode": [
 "Single-volume","Single-volume","Multi-volume stitching","Multi-volume stitching",
 "Single-volume","Single-volume","Single-volume","Single-volume","Single-volume",
 "Single-volume","Single-volume","Single-volume","Single-volume","Single-volume"],

"Sampling Unit": [
 "Whole sample (single allocated Bennu particle; 928 slices)",
 "Sub-volume > Grain (sub-samples A0180-A and A0180-B; size and shape factor reported per microchondrule / sulphide-silicate object)",
 "Whole sample (six overlapping cone-beam volumes stitched into one continuous dataset per core; the sub-volumes are an acquisition unit, not a reporting unit)",
 "Whole sample (six overlapping cone-beam volumes stitched into one continuous dataset per core; the sub-volumes are an acquisition unit, not a reporting unit)",
 "Whole sample (the 73001 CSVC container assembly)",
 "Grain (individual extracted particles >4 mm, each individually bagged and scanned)",
 "Sub-volume (modal mineralogy reported for six 2-D XCT slices at ~1 mm spacing and for the entire chip volume)",
 "Aliquot (~1 g crushed Murchison B in a glass vial)",
 "Whole sample (one scan per meteorite specimen: NWA 8277, NWA 6963)",
 "Region of interest (individual melt inclusion) > Phase (glass, clinopyroxene, spinel, vapour)",
 "Region of interest (individual fluid inclusion) > Phase (vapour, liquid)",
 "Region of interest (individual fluid inclusion) > Phase (vapour, liquid)",
 "Region of interest (individual fluid inclusion) > Phase (vapour, liquid, oil, solid bitumen)",
 "Whole sample (8 mm core) > Phase (plagioclase network)"],

"Sampling Unit Selection Criteria": [
 "N (single allocated particle; no selection criteria stated)",
 "N (whole particle scanned; the sample split into parts A and B along fractures during mounting, not by selection)",
 "N","N",
 "N (whole CSVC assembly scanned)",
 "Particles >4 mm extracted during dissection are individually bagged and XCT scanned for classification and characterization, without destructive chipping, sectioning or dust removal",
 "Single 2.7 g chip (~1.1 x 1.2 x 0.8 cm) taken from the outer part of one stone, selected because it provides a profile from the weathered exterior to the fresh interior; six 2-D slices at ~1 mm spacing extracted for modal analysis",
 "N (whole crushed aliquot scanned in its vial)",
 "N","N",
 "No sectioning was carried out prior to HRXCT scanning; Sample B was scanned entirely",
 "1.4 x 1.4 x 1.4 mm region of interest containing fluid inclusion #3, scanned at higher resolution after the whole-sample scan",
 "N","N"],

"Pre-Analysis Imaging and Screening": [
 "N",
 "Optical microscopy — morphological inspection of the sample exterior through the container window with the CLOXS digital optical microscope system on automated digital sample stages at JAXA/ISAS, before the sample was decanted for nano-XCT",
 "N","N","N","N",
 "N (XCT is itself the pre-screening step here: the chip was characterized in 3-D prior to destructive sampling)",
 "N","N",
 "N (epoxy mounting and secondary electron imaging were carried out after HRXCT, for subsequent microprobe work)",
 "Optical photography of the sample showing the fluid inclusion array, with inclusions numbered for correspondence with the HRXCT reconstruction (Fig. 2)",
 "Optical photography identifying the fluid inclusion array; inclusion #3 targeted for the high-resolution region-of-interest scan (Fig. 2)",
 "Optical microscopy under UV illumination, used to identify hydrocarbon-bearing phases within the inclusions (Fig. 9)",
 "N"],

"Reported Variables and Units": [
 "N (instrument and scan-parameter record; no derived variables reported)",
 "Microchondrule / sulphide-silicate object diameter (um) and shape factor; object abundance; particle volume",
 "N","N",
 "Space between the bottom tip of the CSVC and the Teflon cap; Teflon cap location and integrity (nominal)",
 "N (particles scanned for classification and characterization; no quantitative variables stated)",
 "Modal mineralogy (vol%) for augite, mesostasis, olivine and titanomagnetite; slice area (mm2)",
 "Absorbed x-ray dose (~180 Gy, the maximum a Bennu sample would receive during an XCT imaging experiment)",
 "Density and porosity; proportions, volume, size, shape and spatial distribution of internal structure",
 "Phase volumes within the melt inclusion (glass, clinopyroxene, spinel, vapour)",
 "Total fluid inclusion volume (mm3); vapour volume (mm3); liquid volume (mm3); vapour volumetric fraction phi_vap (%)",
 "Total fluid inclusion volume (mm3); vapour volume (mm3); liquid volume (mm3); vapour volumetric fraction phi_vap (%)",
 "Total fluid inclusion volume (mm3); phase volumes (mm3); vapour volumetric fraction phi_vap (%)",
 "Plagioclase network interconnectivity"],

"Calibration Factor and Determination Method": [
 "N","N","N","N","N","N",
 "N (segmentation performed on uncalibrated grayscale values; no attenuation calibration stated)",
 "N","N",
 "N (segmentation performed on relative grey values; no attenuation calibration stated)",
 "N (segmentation performed on relative grey values; no attenuation calibration stated)",
 "N (segmentation performed on relative grey values; no attenuation calibration stated)",
 "N (segmentation performed on relative grey values; no attenuation calibration stated)",
 "N"],

"Constants and Reference Values Used": [
 "N","N","N","N","N","N",
 "N (minerals discriminated by contrasting linear attenuation coefficients; no coefficient values stated)",
 "N",
 "N (mass attenuation coefficients are discussed for the micro-XRF Rayleigh/Compton work, not for the micro-CT)",
 "N","N","N","N",
 "N (olivine and pyroxene were not segmented owing to similar attenuation coefficients under the imaging conditions; no values stated)"],

"Additional Notes": ["N"]*14,
}

HEADERS = ["1. Procedure Identification","2. Samples","3. Instrument & Software",
           "4. Measurement Information","5. Data Processing","6. Quality Control & Uncertainty"]

NEW_F_RVU = ("e.g., 'Modal mineralogy (vol%: augite, mesostasis, olivine, titanomagnetite)' | "
             "'Porosity (vol%); bulk density (g cm-3)' | "
             "'Inclusion volume (mm3); vapour volumetric fraction (%)' | "
             "'Equivalent diameter (um); shape factor (dimensionless)' | "
             "'Phase interconnectivity (N/A - nominal property)' | "
             "'Absorbed x-ray dose (Gy)'")


def main(apply=False):
    rows = list(csv.reader(open(SRC, newline="", encoding="utf-8-sig")))
    hdr = rows[0]
    sent = hdr.index("Literature Assessment")
    first, n = sent + 1, 14
    assert len(hdr) - first >= n, (len(hdr), first)
    iu = hdr.index("Last Update")

    changed = 0
    for r in rows[1:]:
        if not r or not r[0].strip():
            continue
        name = r[0].strip()
        vals = M.get(name)
        if name in HEADERS:
            vals = ["N"] * n
        if vals is None:
            continue
        while len(r) < len(hdr):
            r.append("")
        if any(c.strip() for c in r[first:first + n]):
            raise SystemExit("refusing to overwrite existing extraction in %r" % name)
        for i, v in enumerate(vals):
            r[first + i] = v
        if name not in HEADERS:
            r[iu] = DATE
        changed += 1
        print("  %-46s %d cells" % (name[:46], n))

    for r in rows[1:]:
        if r and r[0].strip() == "Reported Variables and Units":
            print("\n  Column F (Reported Variables and Units):\n    was: %s\n    now: %s"
                  % (r[5][:90], NEW_F_RVU[:90]))
            r[5] = NEW_F_RVU

    print("\n  %d rows filled (%d fields + %d group headers)" % (changed, len(M), len(HEADERS)))
    if not apply:
        print("(dry run — pass --apply to write)")
        return
    with open(SRC, "w", newline="", encoding="utf-8-sig") as f:
        csv.writer(f).writerows(rows)
    print("written:", SRC)


if __name__ == "__main__":
    main("--apply" in sys.argv)
