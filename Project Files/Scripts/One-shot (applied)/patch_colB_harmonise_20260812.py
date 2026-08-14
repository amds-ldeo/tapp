#!/usr/bin/env python3
"""Harmonise the 20 SUPERSET / PARAPHRASE / DRIFT Column B divergences (Rule 7.8.9 backlog).

Target text per field is written out in full below so the change is reviewable without diffing 16
files. Every field here is TAPP-owned (verified in the triage), so nothing is at risk of being
reverted by recomposition.

Three fields are only PARTIALLY harmonisable — a shared body plus a legitimately technique-specific
tail. They are handled with a body + per-TAPP tail, and their register verdict is corrected from
SUPERSET/DRIFT to PRINCIPLED, because what remains after harmonising is real:

  EDS Spectral Processing Type   TEM keeps the Rule 6.5 conditional referencing its
                                `Spectroscopic Detector(s)` gate, which EPMA/SEM have no analogue for
  EDS Dead Time                 EPMA/SEM keep the cross-reference to `WDS Dead Time Correction`;
                                TEM keeps its detector conditional
  Oxide Production Method and Threshold
                                MIS-TRIAGED as DRIFT. The oxide proxy is genuinely technique-specific:
                                LA uses ThO+/Th+ (mass 248/232), solution work uses CeO+/Ce+
                                (156/140). Only the framing and the closing cross-reference harmonise.

Two bugs found while reading the full text:

  E-scan Range (Solution_SF)    carries a DUPLICATED sentence — "Record 'N/A' if E-scan acquisition
                                is not used. Record 'N/A' where E-scan acquisition mode is not used."
                                Fixed by adopting the clean LA-SF text.
  Interference Corrections Applied
                                EPMA's examples were prefixed "Common EPMA interferences", which
                                would be wrong once the text is shared with the SEM TAPPs. Generalised
                                to "Common interferences" — the Ti Kβ / Cr Kβ / Ba Lα overlaps are
                                properties of the X-ray lines, not of the instrument.

Spelling: each target keeps the spelling of the variant it is based on. A library-wide house style
is still undecided (151 British vs 157 American occurrences), so this pass does not impose one.

Dry-run by default. Pass --apply to write.
"""
import argparse
import csv
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "Claude Skills for TAPP", "scripts"))
import validate_tapp as V  # noqa: E402

COL_B, COL_H = 1, 7
DATE = "2026-08-12"

# ---------------------------------------------------------------- full harmonisation
# field -> single target description for every TAPP carrying it
FULL = {
    "Between-Session (Long-Term) Analytical Precision and Assessment Method":
        "Reproducibility of measurements across multiple analytical sessions over weeks to months "
        "(long-term or intermediate precision). Report both the assessment method and the precision "
        "values. Specify: reference material used, number of sessions n, time span covered, and "
        "statistic reported. Long-term precision is typically assessed from a compiled record of "
        "secondary reference material values across all sessions.",

    "Sequence":
        "Order in which analytes are acquired in the spectrometer sequence during point analysis. "
        "Relevant for minimizing beam damage (volatile elements measured first) and for sequential "
        "multi-channel setups. Not applicable to X-ray mapping, where all assigned spectrometers "
        "collect simultaneously at each pixel.",

    "WDS Dead Time Correction":
        "Method used to correct for WDS proportional counter dead time at high count rates. Dead "
        "time errors are most significant for major elements with high count rates (e.g., Si, Fe, "
        "Ca). Unlike EDS dead time — which is hardware-managed and reported as a session QC "
        "percentage (see EDS Dead Time) — WDS dead time correction is a user-selectable algorithm "
        "in the data reduction software. No separate measured WDS dead time value is reported; the "
        "correction is applied transparently during intensity-to-concentration conversion.",

    "Interference Corrections Applied":
        "Whether a spectral interference correction was applied for each analyte. Common "
        "interferences include Ti Kb on V Ka, Cr Kb on Mn Ka, and Ba La on Ti Ka.",

    "Analytical Accuracy":
        "Offset between measured and accepted reference values for secondary standards, expressed "
        "as percent relative bias. Include reference material, reference value source, and "
        "per-analyte value.",

    "Triple Scanning Mode":
        "Whether each mass peak is scanned three times per cycle and the results averaged (Y/N). "
        "Used to reduce noise from short-term magnetic field instabilities on sector-field "
        "instruments. Triple scanning affects the effective integration time per cycle and should "
        "be reported. Record 'N/A' if not applicable to the instrument.",

    # Rule 8's canonical text, which 10 of 16 TAPPs already carry. Adopting it everywhere also
    # aligns the field with the wording specified in conventions.md Rule 8.
    "Reported Variables and Units":
        "The final variable(s) this procedure reports and their units — distinct from Analyte and "
        "Monitored Isotopes, which record what was acquired. A procedure may acquire many masses "
        "and report a small number of derived quantities; without this field a data consumer cannot "
        "tell which. Record every reported variable, including intermediate quantities reported "
        "alongside final ones (e.g. both the 206Pb/238U ratio and the 206Pb/238U date). Where a "
        "reported variable is a nominal property with no magnitude (e.g. a mineral identification), "
        "record the variable and give the unit as 'N/A — nominal property'.",

    "Torch Depth":
        "Distance between the load coil and the sampling cone tip (mm), also called injector depth "
        "or torch position depending on the instrument manufacturer. Affects ion transmission "
        "efficiency, oxide formation, and doubly-charged species production. The procedure "
        "specifies a target value optimised during initial setup; the analyst confirms or "
        "fine-adjusts during session tuning.",

    "Oxide Production":
        "Measured oxide production ratio obtained during session-start tuning, for the proxy "
        "specified in Oxide Production Method and Threshold. Record the measured value and confirm "
        "whether the procedure threshold was met.",

    "WDS Spectrometer Configuration":
        "Number, type, and crystal range of WDS spectrometers on the instrument. Include "
        "manufacturer, model, and crystal range. For SEM-WDS configurations (third-party WDS on a "
        "non-EPMA platform), include WDS manufacturer and model.",

    "X-ray Line":
        "X-ray emission line measured for each analyte. Line choice affects sensitivity, matrix "
        "correction accuracy, and susceptibility to peak overlap and spectral interference.",

    "Background Correction Method":
        "Method used to estimate and subtract background X-ray intensity beneath the peak. For WDS: "
        "typically 2-point off-peak linear interpolation or Mean Atomic Number (MAN) background "
        "model. For EDS: spectral background fitting or top-hat filter applied during spectral "
        "processing.",

    "Analytical Precision":
        "Reproducibility of repeated measurements on the same or equivalent reference material, "
        "expressed as 1-sigma relative standard deviation (%). Include reference material name, "
        "number of analyses (n), and value per analyte or element group.",

    # Solution_SF carried the closing sentence twice; the LA-SF text is the clean one.
    "E-scan Range":
        "Electric scan range used for peak acquisition, expressed as percentage of the centre mass "
        "(%). Varies the accelerating voltage to cover masses in the vicinity of the set magnetic "
        "mass without re-scanning the magnet. Record 'N/A' if E-scan acquisition mode is not used.",

    # The instrument noun differed per TAPP ("the SEM", "the TEM/STEM", "the EPMA"). Within a TAPP
    # the technique is already declared, so "the instrument" loses nothing and gains uniformity.
    "Instrument Manufacturer":
        "Make of the instrument used for this procedure.",

    "Electron Source":
        "Type of electron gun used in the instrument.",

    "Matrix Correction Method":
        "X-ray matrix correction algorithm applied during quantitative EDS or WDS data reduction. "
        "For X-ray mapping, applies when raw count maps are converted to quantitative concentration "
        "maps.",
}

# ---------------------------------------------------------------- partial harmonisation
# field -> (shared body, {tapp-prefix: tail appended for that TAPP only})
PARTIAL = {
    "EDS Spectral Processing Type": (
        "Method used to process EDS spectra and extract net peak intensities from raw spectral "
        "data. Applied before quantification (EDS Quantification Method). Common approaches include "
        "background fitting and subtraction followed by peak integration, and filter fit or "
        "Gaussian deconvolution for overlapping peaks.",
        {"TEM": " Record 'N/A' where EDS is not listed in Spectroscopic Detector(s)."},
    ),
    "EDS Dead Time": (
        "Percent dead time reported by the EDS detector during the session — the fraction of total "
        "acquisition time the detector spent processing rather than counting. EDS dead time "
        "correction is managed automatically by the detector electronics; this field documents the "
        "resulting percentage as a session QC metric. Values above ~40% indicate excessive count "
        "rate and may degrade spectral quality and quantitative accuracy.",
        {"TEM": " Record 'N/A' where EDS is not listed in Spectroscopic Detector(s).",
         "EPMA": " Unlike WDS dead time (see WDS Dead Time Correction), no user-selectable "
                 "correction algorithm is required.",
         "SEM": " Unlike WDS dead time (see WDS Dead Time Correction), no user-selectable "
                "correction algorithm is required."},
    ),
    "Oxide Production Method and Threshold": (
        "Method used to quantify plasma oxide production and the acceptance threshold applied "
        "before commencing analysis. Record both the monitored mass ratio(s) and the maximum "
        "allowed threshold(s). Measured values are recorded in Oxide Production.",
        {"LA-": " The ThO⁺/Th⁺ ratio (mass 248/232) is most widely used, but UO⁺/U⁺ (mass 254/238) "
                "or CeO⁺/Ce⁺ (mass 156/140) may also be used.",
         "Solution_MC": " CeO+/Ce+ (m/z 156/140) is the standard monitor proxy. Stricter oxide "
                        "thresholds may be required for analytes sensitive to oxide interferences "
                        "(e.g., BaO+ on REE isotopes).",
         "Solution_SF": " CeO+/Ce+ (m/z 156/140) is the standard monitor proxy; stricter thresholds "
                        "than Q-ICP-MS are commonly required. BaO+/Ba+ may also be monitored.",
         "Solution_Q": " CeO+/Ce+ (m/z 156/140) is the standard monitor proxy."},
    ),
}


def target_for(field, base):
    """Resolve the target description for `field` in the TAPP file named `base`."""
    if field in FULL:
        return FULL[field]
    body, tails = PARTIAL[field]
    for pref, tail in sorted(tails.items(), key=lambda kv: -len(kv[0])):
        if base.startswith(pref):
            return body + tail
    return body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    fields = set(FULL) | set(PARTIAL)
    changed, unchanged, files = [], 0, set()
    for path in V.discover(ROOT):
        base = os.path.basename(path)
        rows = list(csv.reader(open(path, newline="", encoding="utf-8-sig")))
        dirty = False
        for n, r in enumerate(rows[1:], start=2):
            if not r or len(r) <= COL_H or r[0].strip() not in fields:
                continue
            fld = r[0].strip()
            tgt = target_for(fld, base)
            cur = r[COL_B]
            if cur.strip() == tgt:
                unchanged += 1
                continue
            r[COL_B] = tgt
            r[COL_H] = DATE
            dirty = True
            files.add(base)
            changed.append((base, n, fld, len(cur), len(tgt)))
        if dirty and args.apply:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                csv.writer(f).writerows(rows)

    from collections import Counter
    per_field = Counter(c[2] for c in changed)
    for fld in sorted(per_field):
        kind = "FULL" if fld in FULL else "PARTIAL"
        print(f"  {per_field[fld]:3d} row(s)  [{kind:7s}] {fld}")
    print(f"\n{len(changed)} row(s) rewritten across {len(files)} file(s); "
          f"{unchanged} already matched")
    print("OK" + ("" if args.apply else " (dry run — pass --apply to write)"))


if __name__ == "__main__":
    main()
