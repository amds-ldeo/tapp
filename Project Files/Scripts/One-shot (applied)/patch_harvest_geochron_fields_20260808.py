#!/usr/bin/env python3
"""
patch_harvest_geochron_fields_20260808.py

Harvests the 8 fields the LA-ICP-MS Geochronology TAPP had and LA-Q/SF-ICP-MS lacked,
into the general LA-Q/SF-ICP-MS TAPP.

Seven of the eight are generic LA-ICP-MS fields, not geochronology content — the
geochronology TAPP happened to be the most complete instrument description in the
library. Retiring it without harvesting them would lose real coverage.

Names normalised on the way in
------------------------------
The geochronology TAPP inherited unit-in-name violations from Horstwood's Table 3.
Rather than import them and fix later, they are corrected here; the unit moves to
Column E per conventions.

    'Total Integration Time per Output Data Point (s)' -> 'Total Integration Time per Output Data Point'
    "'Sensitivity' as Useful Yield (%, element)"       -> 'Sensitivity as Useful Yield'
    'IC Dead Time (ns)'                                -> 'Ion Counter Dead Time'
    'Ablation Pit Depth/Ablation Rate'                 -> 'Ablation Pit Depth and Ablation Rate'

Mode flags
----------
Y/Y/Y except Total Integration Time per Output Data Point (Y/Y/N): for mapping the
per-pixel cycle is set by dwell times, with no post-hoc sweep to time — the same
reasoning already applied to Signal Integration Time in this TAPP.

Ablation pit depth is Y/Y/Y rather than spot-only, following the Signal Smoothing
precedent: the concept applies to raster and transect as a trench rather than a pit,
so the field stays visible with the difference noted in the description.

Version policy
--------------
No version bump, consistent with the other patches this week. Adding fields is
normally an integer bump, but this TAPP is mid-migration and its version is tracked
against the modules composed into it; a bump here would desynchronise
composed_tapps.json from the file for no gain. Flag if you'd rather it went to v6.
"""

from __future__ import annotations

import csv
import datetime
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(ROOT, "LA-Q_SF-ICP-MS", "LA-Q_SF-ICPMS_TAPP_v5.csv")
TODAY = datetime.date.today().isoformat()
COL_ITEM = 0

# (anchor field, insert-after?, name, description, C, D, datatype, example, comment, modes)
FIELDS = [
 ("Ablation Cell Type", "Sample Introduction",
  "Configuration by which the ablated aerosol is delivered to the plasma, including tubing, any "
  "signal-homogenising device, and any co-aspirated solution introduced alongside the aerosol — for "
  "example a Tl solution used for instrumental mass bias correction, or an isotopic spike used for "
  "isotope dilution. Distinct from the carrier and make-up gas fields, which record gas identity and "
  "flow rather than what else enters the plasma.",
  "Basic", "Read-Only", "Text (free)",
  "e.g., 'Squid signal homogeniser, 2 m PTFE tubing, no co-aspiration' | "
  "'Dry plasma; Tl solution co-aspirated via desolvating nebuliser for mass bias correction'",
  "", "YYY"),

 ("Laser Spot Geometry", "Spot Diameter (Measured)",
  "Diameter of the laser spot as independently measured on the sample or on a test material, distinct "
  "from the nominal value the procedure registers. Measured companion to Laser Spot Geometry: nominal "
  "and delivered spot size can differ appreciably with optics condition and focus.",
  "N/A", "Basic", "Numeric (µm)",
  "e.g., '32.4' | 'nominal 35, measured 33.1 +/- 0.8 (n = 12 pits, white-light profilometry)'",
  "", "YYY"),

 ("Ablation Duration per Spot", "Ablation Pit Depth and Ablation Rate",
  "Depth of the ablation pit produced under the registered laser conditions, the method used to measure "
  "it, and the resulting per-pulse ablation rate. Sets the achievable depth resolution and governs "
  "downhole elemental fractionation. For transect and mapping the equivalent quantity is trench depth "
  "under the same conditions.",
  "Basic", "Editable", "Text (free)",
  "e.g., 'Pit depth 18 um after 300 pulses (white-light profilometry); 60 nm/pulse' | "
  "'Trench depth 4 um at 5 um/s scan speed'",
  "", "YYY"),

 ("Monitored Isotopes", "Reported Variables and Units",
  "The final variable(s) this procedure reports and their units — distinct from Analyte and Monitored "
  "Isotopes, which record what was acquired. A procedure may acquire many masses and report a small "
  "number of derived quantities; without this field a data consumer cannot tell which columns of a "
  "dataset the procedure is accountable for.",
  "Basic", "Read-Only", "Text (free)",
  "e.g., 'Element concentrations in ug/g; 2SE per analyte' | "
  "'207Pb/206Pb, 206Pb/238U, 207Pb/235U (radiogenic, common-Pb corrected), absolute ratios with 2-sigma'",
  "", "YYY"),

 ("Dwell Time per Mass", "Total Integration Time per Output Data Point",
  "Total duty-cycle time for one complete mass-scan sweep — the sum of all per-isotope dwell times plus "
  "inter-mass settling times. Sets the time resolution of the downhole signal, and is not recoverable "
  "from Dwell Time per Mass alone because settling time is not captured there. Applies to sequential "
  "(quadrupole and single-collector sector-field) acquisition.",
  "Basic", "Editable", "Numeric (s)",
  "e.g., '0.284' | '0.31 s (24 masses, 10 ms dwell, 4 ms settling)'",
  "", "YYN"),

 ("ICP Tuning", "Sensitivity as Useful Yield",
  "Instrument sensitivity expressed as useful yield: the percentage of sampled atoms of a given element "
  "ultimately detected as ions, with the method used to derive it cited. A more rigorous and more "
  "comparable statement of sensitivity than counts per second per unit concentration, which depends on "
  "spot size, fluence and repetition rate.",
  "N/A", "Advanced", "Numeric (%)",
  "e.g., '0.42 (U, method of Horstwood et al. 2016)' | 'Pb 0.31%, U 0.44%'",
  "Analyte-Specific", "YYY"),

 ("Signal Collection Mode", "Ion Counter Dead Time",
  "Dead time of each ion-counting detector channel, used in the dead-time correction applied to high "
  "count rates. Distinct from Pulse/Analog Detector Nonlinearity Correction, which cross-calibrates the "
  "two detector modes rather than correcting counting losses within the pulse-counting mode.",
  "Basic", "Editable", "Numeric (ns)",
  "e.g., '23' | '23 ns (determined from NIST 612 at varying spot size, checked quarterly)'",
  "", "YYY"),

 ("Elemental Fractionation Correction", "Mass Bias Correction Strategy",
  "Strategy used to correct instrumental isotopic mass fractionation, also called mass bias or mass "
  "discrimination. Distinct from Elemental Fractionation Correction, which addresses inter-element "
  "fractionation during ablation and transport: this field addresses discrimination between isotopes of "
  "the same element, and applies wherever the procedure reports isotope ratios.",
  "Basic", "Read-Only", "Text (free)",
  "e.g., 'Standard-sample bracketing against NIST 612' | "
  "'Co-aspirated Tl, exponential law' | 'None (elemental concentrations only)'",
  "", "YYY"),
]


def main():
    dry = "--dry-run" in sys.argv
    with open(TARGET, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    header = rows[0]
    width = len(header)
    sent = next(i for i, h in enumerate(header) if h.strip() == "Literature Assessment")

    existing = {r[COL_ITEM].strip() for r in rows[1:] if r and r[COL_ITEM].strip()}
    added = []

    for anchor, name, desc, c, d, dtype, ex, comment, modes in FIELDS:
        if name in existing:
            print(f"  -- {name!r} already present, skipped")
            continue
        idx = next((i for i, r in enumerate(rows) if r and r[COL_ITEM].strip() == anchor), None)
        if idx is None:
            print(f"  !! anchor {anchor!r} not found — {name!r} NOT added")
            return 2
        row = [""] * width
        row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7] = \
            name, desc, c, d, dtype, ex, comment, TODAY
        for j, flag in enumerate(modes):
            row[8 + j] = flag
        rows.insert(idx + 1, row)
        added.append((idx + 2, anchor, name, c, d, dtype, modes))

    if added and not dry:
        with open(TARGET, "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerows(rows)

    print(f"\n{os.path.relpath(TARGET, ROOT)}")
    for at, anchor, name, c, d, dtype, modes in added:
        print(f"    after {anchor[:34]:<34} + {name[:44]:<44} C={c:<9} D={d:<10} {dtype:<16} {modes}")

    verb = "would be" if dry else ""
    print(f"\n{'=' * 92}")
    print(f"  {len(added)} field(s) {verb} added.")
    if dry:
        print("  Dry run — nothing written.")
    print("=" * 92)
    return 0


if __name__ == "__main__":
    sys.exit(main())
