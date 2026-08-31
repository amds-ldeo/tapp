#!/usr/bin/env python3
"""
validate_tapp.py — structural and convention linter for the TAPP library.

Checks every TAPP CSV against the invariants and cross-TAPP consistency rules in
`references/conventions.md`. Reports violations; changes nothing.

Usage
-----
    python3 validate_tapp.py                          # lint latest version of every TAPP
    python3 validate_tapp.py --root /path/to/TAPPs
    python3 validate_tapp.py --severity ERROR         # errors only
    python3 validate_tapp.py --all-versions           # include superseded versions
    python3 validate_tapp.py --file EPMA/EPMA_TAPP_v9.csv
    python3 validate_tapp.py --csv findings.csv       # also write findings to CSV

Severity
--------
    ERROR  Structural invariant violated. The TAPP is malformed.
    WARN   Convention violated (naming, controlled vocabulary, Rules 1/3/5).
    INFO   Possible cross-TAPP drift. Needs human judgement — may be intentional.

Exit status is 1 if any ERROR was found, else 0.
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import hashlib
import os
import re
import sys
from collections import defaultdict, Counter

# ---------------------------------------------------------------------------
# Column layout
#
# conventions.md contains two conflicting column tables. The detailed table in
# the "Column structure" section (G=Comments, H=Last Update, mode flags after)
# matches every file in the library and is what this script enforces. The
# summary table in SKILL.md (G=Last update, mode flags from H) does not.
# ---------------------------------------------------------------------------
COL_ITEM, COL_DESC, COL_C, COL_D, COL_TYPE, COL_EXAMPLE, COL_COMMENT, COL_UPDATE = range(8)
COL_KEYEDBY = 8  # Rule 7
COL_PURPOSE = 9    # Column J — consumer-owned (Phase 1, 2026-08-25)
FIRST_MODE_COL = 10
SENTINEL_HEADER = "Literature Assessment"

VALID_C = {"Basic", "Advanced", "N/A"}
VALID_D = {"Read-Only", "Editable", "Basic", "Advanced"}
VALID_MODE_FLAG = {"Y", "N"}

# `Boolean` RETIRED 2026-08-30. Of 4 attested cells across its 3 fields only 1 was a bare
# Yes/No; all three moved to `Controlled list / Text` with Column F widened to the attested
# form, following the `Spectral Interference Corrections Applied` precedent.
VALID_DATA_TYPES = {
    "Text (free)", "Controlled list", "Numeric + unit", "Integer",
    "Date", "URI / DOI", "URI / IGSN", "Text / URI",
}
# "Numeric (unit)" is a family: Numeric (W), Numeric (Hz), Numeric (µm), ...
# "Numeric pair (...)" is in wide use for map dimensions and is treated as valid.
NUMERIC_UNIT_RE = re.compile(r"^Numeric(?: pair)? \(.+\)$")

# Drifted spellings of a type that already exists in the vocabulary.
DATATYPE_SYNONYMS = {
    "free text": "Text (free)",
    "text (free text)": "Text (free)",
    "controlled vocabulary": "Controlled list",
    "controlled vocabulary (list)": "Controlled list",
    "controlled list (controlled vocabulary)": "Controlled list",
    "uri": "URI / DOI",
    "numeric (unit)": "Numeric + unit",  # the doc placeholder, not a real type
}

# Ratified compound types: a vocabulary label, " / ", then a fallback label.
# See "Compound data types" in conventions.md.
_ATOMIC = (r"Controlled list|URI / DOI|URI / IGSN|Text / URI|Numeric \+ unit|"
           r"Numeric pair \([^)]+\)|Numeric \([^)]+\)|Integer|Date")
_FALLBACK = r"Text|Text \(free\)|Numeric \+ unit|Numeric \([^)]+\)"
COMPOUND_RE = re.compile(rf"^(?:{_ATOMIC}) / (?:{_FALLBACK})$")

# Malformed near-compounds: right idea, wrong construction.
MALFORMED_COMPOUND = {
    "numeric or text": "Numeric + unit / Text",
    "numeric (ms) or text": "Numeric (ms) / Text",
    "uri / text (free)": "URI / IGSN for IGSN fields, else Text / URI",
    "numeric + label": "Text (free)",
}

EXPECTED_GROUPS = [
    "1. Procedure Identification",
    "2. Samples",
    "3. Instrument & Software",
    "4. Measurement Information",
    "5. Data Processing",
    "6. Quality Control & Uncertainty",
]

COUPLING_FIELDS = [
    "Coupled Technique(s)",
    "Coupling Description",
    "Coupled Procedure DOI",
    "Coupled Dataset or Publication Reference",
]

# Rule 1 — forbidden name -> required name
FORBIDDEN_NAMES = {
    "lod": "Detection Limit",
    "limit of detection": "Detection Limit",
    "precision": "Analytical Precision",
    "accuracy": "Analytical Accuracy",
    "primary standard": "Primary Calibration Standard Name",
    "calibration material": "Primary Calibration Standard Name",
    "secondary standard": "Secondary Reference Materials",
    "monitor material": "Secondary Reference Materials",
    "spectral interference correction": "X-ray Line Overlap Corrections Applied",
    "counting error": "Counting Statistics Error",
    "statistical error": "Counting Statistics Error",
    "method name": "Procedure Name",
    "method doi": "Procedure DOI",
}

# Rule 1 — required tiers for named cross-TAPP fields
REQUIRED_TIERS = {
    "Acquisition Software": ("Basic", "Editable"),
    "Analytical Mode": ("Basic", "Read-Only"),
    "Constants and Reference Values Used": ("Basic", "Editable"),
}

# Level-encoding words banned from field names (conventions.md "Level-neutral naming")
LEVEL_WORDS = ["Default", "Achieved", "Typical", "Actual"]
TARGET_EXEMPT = {"Target Material", "Target Feature(s)", "Target Selection Criteria"}

# Unit-only parentheticals: the unit belongs in Column E, not the field name.
# "(s)" is excluded — it is the pervasive English plural convention
# ("Procedure Reference(s)", "Coupled Technique(s)"), not seconds.
UNIT_PAREN_RE = re.compile(
    r"\((?:"
    r"W|V|A|ns|fs|ps|ms|µs|us|Hz|kHz|MHz|K|°C|"
    r"µm|um|nm|mm|cm|m|Å|"
    r"g|mg|µg|ug|ng|pg|kg|"
    r"%|ppm|ppb|Ma|Ga|ka|yr|a|"
    r"L\s*min[⁻\-]?1|mL/min|L/min|mL\s*min[⁻\-]?1|"
    r"cm2|cm²|cm-2|cm⁻²|"
    r"nmol|mol|ncc|"
    r"[a-zA-Zµ°]{1,6}\s*[⁻\-]\s*\d"
    r")\)",
    re.IGNORECASE,
)

# Column B describes the FIELD. Text describing what a source paper happens to contain
# is literature-assessment commentary and belongs in a literature assessment column, not
# in the description. This pattern nearly caused a bad reconciliation call on 2026-08-08:
# two candidate descriptions looked longer and better, but the extra length was entirely
# provenance notes about Horstwood's Table 3.
#
# Deliberately narrow. A citation that attributes a METHOD ("following Mattinson, 2005")
# is legitimate and must not be flagged; only text describing a source document is.
DESC_LEAK_RE = re.compile(
    r"(?:"
    r"\bTable\s+\d|\bFigure\s+\d|\bFig\.\s*\d|"
    r"in the source(?:\s+\w+)?|"
    r"not (?:explicitly )?stated (?:for|in|by)|"
    r"as (?:described|listed|reported|given) in Table|"
    r"the (?:paper|source|reference)'s own"
    r")", re.IGNORECASE)

# --------------------------------------------------------------------------- #
# Rule 7 — Keyed By vocabulary
# --------------------------------------------------------------------------- #
# `sample` added 2026-08-12 with the decision that the analysis record is the session, which may
# cover many samples (conventions.md 7.2; Decision Record A1). Defined ahead of its retrofit —
# no field declares it until steps 8-9, which is not a 7.4c violation: 7.4c constrains definers
# without consumers, not vocabulary without users.
KEY_ANCHORS = {"sample", "sampling unit", "reported property", "channel", "analyte"}
KEY_SECONDARY = {"standard", "conversion", "model component", "acquisition pass",
                 "preparation step", "background position"}
KEY_VOCAB = KEY_ANCHORS | KEY_SECONDARY
KEY_FORBIDDEN = {"mode"}          # carried by the mode flag columns (Rule 3)

# Technique-dependent key register (Rule 7.8.7). A field name normally carries the
# same Keyed By in every TAPP; these are the ones where the technique genuinely makes
# it differ. Each entry must carry a recorded rationale in precedents.md. Extend only
# by explicit decision — and only when the divergence is real, not anticipated.
KEYED_BY_TECHNIQUE_DEPENDENT = {
    # `Detection Limit` left this register 2026-08-12: the literature audit showed 7 of 7 papers
    # reporting one LOD per element aggregated over the session, never per spot, so the LA variant
    # became `reported property` like everywhere else and the field is now uniform across all 12.
    "Primary Calibration Standard Name": "analyte in EPMA/SEM and LA-SF; (none) in LA-Q, LA-MC and the Solution TAPPs, which use a single primary or one joint calibration set",
    "Secondary Reference Materials":     "defines: standard per analyte in EPMA/SEM, which report assessed elements per RM; defines: standard in the 9 isotope TAPPs, which report the RM list only",
    # Rewritten 2026-08-12 (Decision Record C1): was "analyte only where compositional mapping
    # exists". The WDS dwell time is per spectrometer per pixel — both descriptions said so — so it
    # follows the other WDS setup fields onto `channel`.
    "Dwell Time per Pixel":              "channel (one value per spectrometer assignment) in the "
                                         "three TAPPs with WDS compositional mapping; (none) wherever "
                                         "there is no spectrometer — the imaging-only SEM variants, "
                                         "and TEM, whose STEM per-pixel dwell is scalar (TEM joined "
                                         "this field on 2026-08-27, when `STEM Dwell Time per Pixel` "
                                         "was merged into it as a Rule 1 name variant)",
    "Beam Current":                      "per phase where composition is measured, scalar in imaging-only TAPPs",
    "Monitored Masses":                  "defines: channel per analyte where there is no collector array; analyte where the cup array defines the channel",
}
KEYED_BY_EXCEPTIONS = set(KEYED_BY_TECHNIQUE_DEPENDENT)   # back-compat alias

# --------------------------------------------------------------------------- #
# Rule 6.4 / 7.8.9 — Column B uniformity across shared field names
# --------------------------------------------------------------------------- #
# A field name shared across TAPPs should carry the same description, for the reason Rule 6.4
# gives: a field that means one thing here and another there is invisible to a curator. Module
# composition enforces this where a module owns the row — and NOTHING enforced it anywhere else
# until 2026-08-12.
#
# Divergences are recorded here with their verdict from
# analysis/Triage_ColB_Uniformity_2026-08-12.csv, so the check ships at 0 WARN and catches NEW
# divergence. Registered entries report INFO; anything unregistered reports WARN.
#
# History
#   2026-08-12  Check implemented. 89 divergences frozen: PRINCIPLED 52, MIXED 17,
#               PARAPHRASE 8, SUPERSET 7, DRIFT 5.
#   2026-08-12  SUPERSET + PARAPHRASE + DRIFT harmonised (patch_colB_harmonise_20260812.py).
#               18 of those 20 fields became fully uniform and left this register; the remaining
#               2 keep a shared body with a legitimately technique-specific tail and are
#               reclassified PRINCIPLED. Register 89 -> 71.
#
# Current state: PRINCIPLED 54 (legitimate technique-specific content, no action expected) and
# MIXED 17 (the remaining harmonisation BACKLOG — some variants technique-specific, others merely
# shorter; needs reading variant by variant). The backlog stays visible: MIXED entries report
# INFO in every lint run, and removing an entry after harmonising is how it is worked down.
#
# Verified 2026-08-12: normalising British/American spelling (-ise/-ize, centre/center,
# artefact/artifact) changed NOTHING — 89 before, 89 after, zero fields differing by spelling
# alone. The split is real (151 British vs 157 American occurrences library-wide) but it does not
# drive the divergence. No house style has been imposed.
# `Sample Name` and `Sample Persistent Identifier` left this register 2026-08-12: both were
# harmonised to a single description across all 16 TAPPs by the Rule 13 retrofit, so neither
# diverges any more. A register entry for a field that no longer diverges is dead weight that
# reads as an unresolved issue.
COLB_DIVERGENCE_TRIAGED = {
    'Dwell Time per Pixel': ("PRINCIPLED", 6),
    'Accelerating Voltage': ("PRINCIPLED", 7),
    # Re-triaged 2026-08-12. Was frozen PRINCIPLED at similarity 0.01 across 6 variants — the
    # 2026-08-12 sweep judged wording, and this is a `defines:` field whose divergence reached
    # into the domain definition itself (six TAPPs described `analyte` as isotopes, the rest as
    # elements). Corrected by the reframe recorded in
    # analysis/Decision_Record_2026-08-12_Session_Sample_and_Analyte.md B1: all 13 now open with
    # one shared sentence and differ only in technique-specific tails. Now 0.36 across 4 variants,
    # and PRINCIPLED is correct for the remaining divergence. The class of error that produced the
    # original mis-triage is now caught by check_definer_stem() below.
    'Beam Current': ("PRINCIPLED", 5),
    'Beam Damage Minimization': ("PRINCIPLED", 3),
    'Beam Diameter': ("PRINCIPLED", 3),
    'Detector Configuration': ("PRINCIPLED", 8),
    'Doubly-Charged Species Monitor': ("PRINCIPLED", 8),
    'Drift Correction': ("PRINCIPLED", 3),
    # Added 2026-08-12. The description points forward to the quantification step, and that step is
    # a different field per technique: EPMA/SEM/SEM_Composition have `Matrix Correction Method`,
    # TEM has `EDS Quantification Method`. Until today all four named the TEM field, so the pointer
    # dangled in the three electron-beam TAPPs — a navigational cross-reference sending a curator to
    # a field their TAPP does not contain. Each now names the field it actually has, which is the
    # point of a pointer; the resulting 0.86 similarity is the cost.
    'EDS Spectral Processing Type': ("PRINCIPLED", 4),
    # harmonised body 2026-08-12; EPMA/SEM cross-reference WDS Dead Time Correction; TEM carries its detector conditional
    'EDS Dead Time': ("PRINCIPLED", 4),
    'EDS Live Time per Point or Pixel': ("PRINCIPLED", 4),
    'Mass Bias Correction Strategy': ("PRINCIPLED", 7),
    # harmonised body 2026-08-12; the oxide proxy is technique-specific: ThO+/Th+ in LA, CeO+/Ce+ in solution
    'Phase Identification Method': ("PRINCIPLED", 2),
    # `Pulse/Analog Detector Nonlinearity Correction` REMOVED 2026-08-31: its Column B was
    # harmonised to one text across all six while its Column F was fixed under 7.8.11, so the
    # field no longer diverges and a standing entry here would read as a decision never made.
    'Step Size / Pixel Size': ("PRINCIPLED", 3),
}


# Compound-key separators. The cross-product `x` must be whitespace-delimited: with
# `\s*` it would split inside any key name containing an x ("flux" -> ["flu", ""]).
# No current key does, but a technique-specific one could, and it would fail silently.
KEY_SPLIT_RE = re.compile(r"\s*>\s*|\s+x\s+")

# Rule 7.4a corollary — a `defines: X` field states what the key domain X *is*, so every TAPP
# carrying that field must agree on at least its opening sentence. Divergence after the first
# sentence is legitimately technique-specific (cross-references to Collector Configuration, EELS
# Edges, Monitored Masses); divergence *in* the first sentence means the TAPPs do not agree on
# what the domain is, which is a correctness problem rather than a style one.
#
# Why this check exists: `Analyte` sat in COLB_DIVERGENCE_TRIAGED as PRINCIPLED at similarity 0.01
# for a full day while six TAPPs defined the analyte domain as isotopes and seven as elements.
# A verdict of "the divergence is justified" was recorded against a field whose divergence was a
# defect. Similarity alone did not catch it — 0.01 was the lowest score in the register and was
# still labelled PRINCIPLED. Requiring a shared opening sentence tests the thing that actually
# matters, and it is not a threshold anyone has to tune.
#
# Registered exceptions ship this check at 0 WARN, as with 7.8.7 and 7.8.9. Entries here are
# INFO; anything unregistered is WARN.
# Rule 7.8.7 companion — key divergence across field-name VARIANTS, not just identical names.
#
# 7.8.7 groups by exact field name, so a TAPP that prefixes a shared field with a technique or
# signal qualifier escapes it entirely. That is not hypothetical: TEM's `EDS Detection Limit` sat
# at `analyte` while `Detection Limit` was `reported property` in all 12 TAPPs carrying it, and no
# check saw the divergence because the names differ. Found by hand on 2026-08-12, fixed in step 5.
#
# The test is whole-word SUFFIX containment — 'EDS Detection Limit' ends with 'Detection Limit' —
# requiring the shared suffix to be at least TWO words. One word is too generic and produced only
# false positives when trialled: every 'X per Analyte' ends with 'Analyte', and 'Analysis Sequence'
# ends with 'Sequence' while naming something unrelated. At two words the trial fired on exactly
# three pairs, all three genuine and all three legitimate — registered below.
KEY_NAME_VARIANT_EXEMPT = {
    ("Detection Limit", "EELS Detection Limit"):
        "different fields, and the split that made them so landed 2026-08-26. `EELS Sensitivity "
        "and Detection Limit` bundled a specification (ZLP energy resolution) with a result "
        "(detection limit), which is why no single Data Type fitted it. On splitting, the "
        "specification half turned out to need no new field at all — `EELS Energy Resolution` "
        "already carries it, `Numeric (eV FWHM)`, and the bundled ZLP half was never once filled "
        "in the literature assessment. So the field was renamed to `EELS Detection Limit`, the "
        "duplicated half dropped, and the result half typed `Numeric + unit / Text` like its "
        "`Detection Limit` sibling. The keys still differ and that is correct: an EELS edge is a "
        "`channel`, enumerated by `EELS Edges`, while `Detection Limit` is one per reported "
        "concentration variable.",
}

COLB_DEFINER_STEM_EXEMPT = {
    'Secondary Reference Materials':
        "key is itself technique-dependent — `defines: standard per analyte` in EPMA/SEM, which "
        "report assessed elements per RM, vs `defines: standard` in the 9 isotope TAPPs, which "
        "report plain RM lists (see KEYED_BY_TECHNIQUE_DEPENDENT and precedents.md). The "
        "descriptions diverge for the same recorded reason. On the harmonisation backlog: a "
        "shared opening sentence would still be an improvement.",
}


# --------------------------------------------------------------------------- #
# Rule 6.4 / 7.8.10 — Column E uniformity across shared field names
# --------------------------------------------------------------------------- #
# Column E was the LAST content column with no cross-TAPP check. A (name), B (description),
# C/D (tiers) and I (Keyed By) all had one; E had none, so a field name shared across TAPPs
# could carry a different Data Type in each with nothing to say so.
#
# That matters more than it looks. Column E is what downstream schema generation reads: in
# `amds-ldeo/geochemBuildingBlocks`, `Text (free)` generates a string with no `schema:unitText`,
# `Numeric (<unit>)` generates a number with `schema:unitText` pinned to that unit as a const,
# and `Numeric + unit` generates a number with `schema:unitText` required but unpinned. So one
# metadata item typed three ways is one item generated in three incompatible shapes — which is
# exactly what amds-ldeo/tapp#1 reports for `Detection Limit`.
#
# Divergences present on 2026-08-24 are frozen here with their verdict from
# analysis/Triage_ColE_Uniformity_2026-08-24.csv, so the check ships at 0 WARN and catches NEW
# divergence. Registered entries report INFO; anything unregistered reports WARN.
#
# Verdicts
#   LINEAGE     the divergence tracks a known authorship boundary — the LA and Solution ICP-MS
#               lineages, or EPMA and SEM — recorded per entry below. Expected to converge when
#               the two lineages are reconciled or a scoped module comes to own the field. NOT a
#               finding that the divergence is justified.
#   OPEN        tracks no boundary; not examined. Needs adjudication.
#   PRINCIPLED  adjudicated as legitimate technique-specific typing; no action expected.
#               Currently unused — nothing here has been adjudicated yet.
#
# Every current entry is therefore a BACKLOG entry, and all of them report INFO on every lint
# run so the backlog stays visible. Removing an entry after harmonising is how it is worked down.
# Nothing was marked PRINCIPLED on the way in, deliberately: recording "the divergence is
# justified" against a field nobody has read is the mis-triage that COLB_DIVERGENCE_TRIAGED
# recorded against `Analyte`, where a PRINCIPLED verdict at similarity 0.01 hid a real defect.
#
# History
#   2026-08-24  Check implemented. 18 divergences frozen: LINEAGE 14 (LA/Solution 9,
#               EPMA/SEM 5), OPEN 4. Prompted by amds-ldeo/tapp#1.
#   2026-08-26  `Internal Standard Approach` REMOVED — the register is now EMPTY. It was never a
#               typing problem: the field asks how the internal standard CONCENTRATION is obtained
#               when the IS is native to the sample rather than added, which is a property of
#               in-situ sampling. Copied into the solution lineage where that question has no
#               discriminating answer, it had been repurposed to record the IS's ROLE instead.
#               All 11 attested Solution cells were verified redundant with three other fields,
#               so it was retired from Solution Q/SF and moved into Module_LaserAblation, whose
#               6 consumers it now matches exactly. Register 1 -> 0.
#   2026-08-26  `Sample Preparation Method` -> `Controlled list / Text` and REMOVED. Its 123
#               attested cells cluster at 0.50 distinctness, so a list was always the right
#               shape; what blocked it was the assumption that 15 TAPPs spanning every technique
#               needed ONE shared vocabulary. They do not — Column F is consumer-owned, so each
#               family carries its own list: electron-beam (polished sections, mounts,
#               conductive tape), laser ablation (adds fused beads and capsule sections),
#               solution (powders, separates, waters, leachates) and TEM (FIB lift-out,
#               ultramicrotomy), the last already in use and well attested at 17 of 21 cells.
#               Register 2 -> 1.
#   2026-08-26  `Isobaric Interference Corrections Applied` -> `Controlled list / Text` and
#               REMOVED. The decision was taken during the amds-ldeo/tapp#1 evidence pass — 44
#               attested cells read "Yes — correction for doubly charged ions: ...", a Yes/No
#               spine carrying detail, which neither `Boolean` nor a bare `Controlled list`
#               holds — but was never applied; it sat in this register as though undecided.
#               Column F is now `Yes | No | N/A | None`: `Analyte-specific` was dropped as a
#               cardinality statement that belongs in Column I, and `Other: specify` because a
#               compound's `/ Text` half already grants it. Register 8 -> 7.
#   2026-08-26  Nine more harmonised and REMOVED on literature evidence — the five EPMA/SEM
#               fields did NOT share one answer: `Beam Diameter` and `Step Size / Pixel Size`
#               took `Numeric (µm) / Text` (unit unanimous, but "Focused (exact diameter N)" is
#               attested too), `Beam Raster Dimensions` and `Map Area` took
#               `Numeric pair (µm x µm)` — except `Map Area`, which the maintainer left at
#               `Numeric + unit` on 2026-08-26 because it has ZERO attested cells and the
#               pair form there rested only on symmetry with `Beam Raster Dimensions`; with no
#               evidence, do not pin a unit. `Dwell Time per Pixel` took `Numeric + unit`
#               because its single attestation reads "~0.5 s per step", disproving the `ms` pin.
#               Register 16 -> 7, OPEN 2 -> 1.
#   2026-08-24  `Detection Limit` and `Detection Limit Method` harmonised and REMOVED (the issue
#               itself). Register 18 -> 16, OPEN 4 -> 2. The name-variant pair
#               (`Detection Limit`, `EDS Detection Limit`) left COLE_NAME_VARIANT_TRIAGED in the
#               same patch, 5 -> 4, since the types now agree.
COLE_DIVERGENCE_TRIAGED = {
    # OPEN — no authorship boundary explains these; each needs a call.
    #
    # `Detection Limit` ("OPEN", 12) and `Detection Limit Method` ("OPEN", 12) LEFT THIS REGISTER
    # on 2026-08-24, resolved by fix_detection_limit_20260824.py: `Numeric + unit / Text` and
    # `Controlled list / Text` respectively, uniform across all 12 TAPPs, plus TEM's
    # `EDS Detection Limit`. That closes amds-ldeo/tapp#1. A register entry for a field that no
    # longer diverges reads as an unresolved issue, so the entries are gone rather than
    # reclassified; the reasoning is in the patch script header and in precedents.md.
    # 14 TAPPs say `Text (free)`, TEM alone says `Controlled list`. Plausibly a real closed list
    # in TEM (FIB lift-out, ultramicrotomy, crushing, ion milling) rather than drift — which is
    # the question, and it has not been asked.
    # Two TAPPs, two variants: an unadjudicated coin flip, not a majority to defer to.
    

    # LINEAGE / LA-Solution — the 6 LA tables type these as free text or Boolean, the 3 Solution
    # tables as controlled lists. Nine fields splitting the same way is one authorship boundary,
    # not nine decisions. All nine are ICP-MS-only and would be settled in one pass by the
    # ICP-MS-scoped module already on the plan (see TAPP_Development_Log.md).
    # `Isobaric Interference Corrections Applied` is the sharpest: Boolean vs Controlled list is
    # a disagreement about whether the field records WHETHER corrections were applied or WHICH.
    # `Mass Resolution Setting` is the imperfect one — Solution SF sides with the LA tables, so
    # the boundary is 7/2 rather than 6/3.
    # `Pulse/Analog Detector Nonlinearity Correction` runs the OTHER way (LA controlled, Solution
    # free text), which is why the cluster reads as accumulated drift rather than two coherent
    # house styles.
            
    # LINEAGE / EPMA-SEM — EPMA names the unit, SEM defers it to the user. Both forms are valid
    # vocabulary, so this is lower stakes than the ICP-MS cluster, but downstream one pins
    # `schema:unitText` to a const and the other does not, which is the same defect shape.
                    }

# Rule 7.8.10 companion — type divergence across field-name VARIANTS.
#
# Same hole as the 7.8.7 companion, one column over: grouping by exact name lets a TAPP that
# prefixes a shared field with a technique or signal qualifier escape the check. The suffix test
# is reused verbatim from the key companion (whole-word suffix containment, minimum two words).
#
# The key companion's register is consulted FIRST. Its three entries record why those pairs are
# DIFFERENT FIELDS, and a rationale for field identity settles both columns at once — a pair that
# is genuinely two fields may of course carry two types. Only pairs it does not cover need an
# entry here, and all five of them are pairs whose KEYS AGREE, which is precisely why the 7.8.7
# companion never saw them.
#
# `EDS Detection Limit` is the instructive one. Its key divergence WAS found by hand on
# 2026-08-12 and fixed — both are `reported property` now — but the Data Type half of the same
# two-column problem was never looked at, and TEM has sat on `Text (free)` while `Detection Limit`
# went three ways. Fixing one column of a field is not fixing the field.
COLE_NAME_VARIANT_TRIAGED = {
}



# Rules 8 and 9 — mandatory in every TAPP. Rule 10 is restricted in scope and is
# declared per TAPP in Phase 0, so its presence is not machine-enforced; when it is
# present its Keyed By is checked like any other field.
RULE8_FIELD = "Reported Variables and Units"
RULE9_FIELD = "Sampling Unit"
RULE11_FIELD = "Additional Notes"   # last field of the whole TAPP (Rule 11)

# Rule 12 — the shareable mirror of the current TAPPs. Flat folder at the library root holding the
# latest CSV + xlsx for every TAPP, refreshed on every version bump.
#
# It MUST be excluded from discover(): the mirror holds byte-identical copies, so without the
# exclusion every TAPP is found twice and which path is treated as authoritative depends on os.walk
# order. Worse, a copy accidentally bumped inside the mirror would win the version comparison and
# become the file `validate_tapp.py` lints, while `compose_tapp.py` kept using the technique-folder
# path from composed_tapps.json — the two would silently disagree about which file is live. Verified
# by construction before the mirror was created.
CURRENT_DIR = "Current TAPPs"


# Rule 7.3 `defines: <domain> per <key>` — a field that enumerates one domain while
# itself repeating over another. Splitting the two roles matters for 7.4a: the domain
# counts as defined, the `per` key counts as used, and both must be valid keys.
#
# The right-hand side is deliberately restricted to a SINGLE key. A compound form
# (`defines: A per B x C`) has no instance in the library, and its token order would
# read neither as the nesting order nor its reverse — `per` puts the innermost domain
# first while `x` runs outer-to-inner. Rather than fix that by inverting `x`, which
# would rewrite 42 existing rows and sever the reporting-table rationale in 7.3, the
# compound case is left unspecified until a real field needs it. Same principle as
# 7.4a-c retiring `conversion` and `acquisition pass` for want of a user, and 7.5
# declining to populate `keyed_by_overridable` speculatively.
DEFINES_PER_RE = re.compile(r"^defines:\s*(.+?)\s+per\s+(.+)$")


def parse_keyed_by(v):
    """Return (kind, [defined domains], [keys the field repeats over]).

    kind in {none, defines, defines_per, pair, plain}. The two lists are kept apart
    because 7.4a asks different questions of each: a defined domain must have exactly
    one definer, a used key must have one.
    """
    v = (v or "").strip()
    if v in ("(none)", ""):
        return "none", [], []
    m = DEFINES_PER_RE.match(v)
    if m:
        domain = [x.strip() for x in KEY_SPLIT_RE.split(m.group(1)) if x.strip()]
        key = [x.strip() for x in KEY_SPLIT_RE.split(m.group(2)) if x.strip()]
        return "defines_per", domain, key
    m = re.match(r"^(defines|pair):\s*(.+)$", v)
    if m:
        parts = [x.strip() for x in KEY_SPLIT_RE.split(m.group(2)) if x.strip()]
        return (m.group(1), parts, []) if m.group(1) == "defines" else (m.group(1), [], parts)
    return "plain", [], [x.strip() for x in KEY_SPLIT_RE.split(v) if x.strip()]


def colf_members(ex):
    """Column F as a set of allowed values, for the 7.8.11 divergence check.

    Order-insensitive and case-insensitive: two TAPPs listing the same members in a different
    order are NOT divergent. The leading `e.g.,` is stripped so an illustrative preamble does
    not count as a member.
    """
    ex = re.sub(r"^\s*e\.g\.,?\s*", "", ex or "")
    return frozenset(re.sub(r"\s+", " ", v.strip().strip("'\"")).lower()
                     for v in ex.split("|") if v.strip().strip("'\""))


# 7.8.11 — Column F divergence on controlled lists, frozen 2026-08-30 so the check ships at
# 0 WARN. PRINCIPLED = adjudicated, no action expected. BACKLOG = not yet examined.
# WORKED DOWN 2026-08-30: `Plasma Thermal Mode`, `Diffracting Crystal`,
# `Stage Scan vs. Beam Scan`, `Guard Electrode`, `Beam Mode` harmonised and REMOVED;
# `WDS Dead Time Correction`, `Pulse/Analog Detector Nonlinearity Correction` and
# `Chromatographic Separation Applied` likewise 2026-08-31; `Coupled Technique(s)` left the
# backlog by RETYPE — `Controlled list / Text` -> `Text (free)` via Module_Core, because a
# list that controls nothing asserts a closure the data does not have — the first where the harmonised list
# is SHORTER than a variant, EPMA's four constant-members being a {default,adjusted} x
# {Cameca,JEOL} cross-product whose vendor axis `Instrument Manufacturer` already owns. — the triage note said
# 'same domain, different verbosity', but Solution MC was also missing the `Mixed` member
# outright. Triage notes are a starting point; read the variants before acting on one.
# Work an entry down by harmonising and DELETING it, never by reclassifying: an entry for a
# field that no longer diverges reads as a standing decision that was never made.
COLF_DIVERGENCE_TRIAGED = {
 # --- PRINCIPLED: the domain genuinely differs per TAPP -------------------------------
 "Technique": ("PRINCIPLED",
   "Rule 1, adjudicated 2026-08-30: each list holds the TAPP's OWN technique, not a menu of "
   "siblings. Divergence here is the design."),
 "Analytical Mode": ("PRINCIPLED",
   "Rule 3 binds the values to that TAPP's mode-flag column headers, which differ by "
   "construction."),
 "Matrix Correction Method": ("PRINCIPLED",
   "Adjudicated 2026-08-30 on merging the EPMA/SEM and TEM name-variant pair: bulk "
   "XPP/PAP/ZAF against thin-film Cliff-Lorimer/zeta-factor. Same question, different physics "
   "regime."),
 "ICP-MS Type": ("PRINCIPLED",
   "Each TAPP lists only its own analyser family — a Q-ICP-MS TAPP should not offer MC. "
   "Scoping, not drift."),
 "Instrument Manufacturer": ("PRINCIPLED",
   "Consumer-owned vocabulary (see Module_Core.json) and vendors differ by technique: JEOL "
   "and Cameca for the electron beam, Thermo and Agilent for ICP-MS."),
 # --- BACKLOG: diverges, not yet examined ---------------------------------------------
 "Target Material": ("BACKLOG", "7 variants across 16 TAPPs."),
 "Sample Preparation Method": ("BACKLOG", "5 variants across 16 TAPPs."),
 "EDS Acquisition Mode": ("PRINCIPLED",
   "Examined 2026-08-31. The shared core was drift and is harmonised — `Point | Line scan | "
   "Map | Spectrum image` in all four, with `Map` and `Spectrum image` separated because they "
   "are different acquisitions, not synonyms. What remains diverging is scoping: "
   "`Simultaneous EDS+EELS` is meaningless without an energy-loss spectrometer (TEM only) and "
   "`Automated mineralogy` is an SEM platform. A uniform list would offer every EPMA user a "
   "mode their instrument cannot perform. The test: a member is principled if it names a "
   "capability the technique does not have."),
 "Collision/Reaction Cell (CRC) Configuration": ("PRINCIPLED",
   "Resolved 2026-08-31. `KED+DRC` was a genuine shared mode the MC tables lacked and is now "
   "added. What still differs is real: the Q tables offer "
   "`ICP-MS/MS (triple-quadrupole mode)` and the MC tables `MS/MS (pre-cell mass filter)`, "
   "because a Nu Sapphire or Thermo Neoma MS/MS has a pre-cell mass filter and a "
   "multi-collector array, NOT a triple quadrupole. Same wording in both would be false in "
   "one of them. Scoping, not drift."),
}


DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# 2026-08-30 — the two-type scheme. `Controlled list` now means CLOSED and
# `Controlled list / Text` means open, so the TYPE carries the open/closed signal and
# Column F no longer repeats it. `Other: specify` left the vocabulary entirely: on a
# closed list it contradicted the type, and on a compound it was the wrong prompt (a
# compound wants a term PLUS qualification, not "pick something else"). The user-facing
# guidance now lives once on the xlsx Legends sheet. Both types still owe `N/A | None`,
# which are conventional VALUES a user must be shown they may enter.
CONTROLLED_LIST_REQUIRED = ["N/A", "None"]
CONTROLLED_LIST_FORBIDDEN = ["Other: specify"]

# Controlled list fields exempt from the N/A | None requirement, because another rule
# binds their allowed values to an exact closed set.
# See the exemption table in the Data Type Vocabulary section of conventions.md.
# Closed list — extend only by explicit decision, documented there.
#   `Analytical Mode` — Rule 3.
#   `Technique`       — Rule 1. Both options are semantically empty: every procedure has a
#     technique, and a record declaring otherwise would be malformed.
# NOTE this set exempts a field from the REQUIRED options only. The forbidden-options check
# below has no exemptions: `Other: specify` left the vocabulary entirely on 2026-08-30 and may
# not reappear on any controlled list. `Technique` was the last field carrying it, closed once
# Rule 1 settled its vocabulary — three TAPPs' lists had not contained their own technique.
CONTROLLED_LIST_EXEMPT = {"Analytical Mode", "Technique"}
# Rule 3 exempts `Analytical Mode` from these; check_analytical_mode_vocabulary flags them.
GENERIC_LIST_OPTIONS = {"N/A", "None", "Other: specify", "Multiple (specify)"}


def _span(nums, limit=6):
    """Compact a row-number list for display: [2,3,4,9] -> '2-4, 9'."""
    if not nums:
        return ""
    runs, start, prev = [], nums[0], nums[0]
    for n in nums[1:]:
        if n == prev + 1:
            prev = n
            continue
        runs.append((start, prev))
        start = prev = n
    runs.append((start, prev))
    parts = [str(a) if a == b else f"{a}-{b}" for a, b in runs]
    if len(parts) > limit:
        return ", ".join(parts[:limit]) + f", … (+{len(parts) - limit} more)"
    return ", ".join(parts)


class Finding:
    __slots__ = ("severity", "tapp", "row", "field", "check", "message")

    def __init__(self, severity, tapp, row, field, check, message):
        self.severity = severity
        self.tapp = tapp
        self.row = row
        self.field = field
        self.check = check
        self.message = message

    def as_tuple(self):
        return (self.severity, self.tapp, self.row, self.field, self.check, self.message)


class Tapp:
    """A parsed TAPP CSV."""

    def __init__(self, path, rows):
        self.path = path
        self.name = os.path.basename(path)
        self.rows = rows
        self.header = rows[0] if rows else []
        self.sentinel_idx = self._find_sentinel()
        self.mode_cols = (
            self.header[FIRST_MODE_COL:self.sentinel_idx]
            if self.sentinel_idx is not None
            else []
        )

    def _find_sentinel(self):
        for i, h in enumerate(self.header):
            if h.strip() == SENTINEL_HEADER:
                return i
        return None

    def cell(self, row, idx):
        return row[idx].strip() if idx < len(row) else ""

    def is_group_header(self, row):
        a = self.cell(row, COL_ITEM)
        return bool(a) and bool(re.match(r"^\d+\.\s", a))

    def is_separator(self, row):
        """A separator row has no Metadata Item.

        Separator rows in several TAPPs carry stray N values in the mode and
        literature-assessment columns, so emptiness is judged on columns A-H only.
        """
        return not any(self.cell(row, i) for i in range(COL_ITEM, COL_UPDATE + 1))

    def content_rows(self):
        """Yield (row_number_1_indexed, row, current_group) for content rows only."""
        group = None
        for n, row in enumerate(self.rows[1:], start=2):
            if self.is_separator(row):
                continue
            if self.is_group_header(row):
                group = self.cell(row, COL_ITEM)
                continue
            yield n, row, group


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_structure(t: Tapp, out):
    add = lambda s, r, f, c, m: out.append(Finding(s, t.name, r, f, c, m))

    if t.sentinel_idx is None:
        add("WARN", 1, "", "sentinel-column",
            f"No column headed '{SENTINEL_HEADER}'. Mode/literature boundary cannot be "
            f"determined reliably; export falls back to a length heuristic.")
    else:
        stray_n = []
        for n, row in enumerate(t.rows[1:], start=2):
            if t.is_separator(row):
                continue
            v = t.cell(row, t.sentinel_idx)
            item = t.cell(row, COL_ITEM)
            if t.is_group_header(row):
                if v != "N":
                    add("WARN", n, item, "sentinel-group-header",
                        f"Group header should have N in the sentinel column, found '{v or 'empty'}'.")
            elif v == "N":
                # Widespread convention drift: sentinel treated as another mode column.
                stray_n.append(n)
            elif v:
                add("ERROR", n, item, "sentinel-nonempty",
                    f"Sentinel column must be empty on data rows, found '{v}'. "
                    f"This shifts the mode/literature boundary for any consumer that reads it.")
        if stray_n:
            add("WARN", stray_n[0], "", "sentinel-stray-N",
                f"{len(stray_n)} data row(s) carry 'N' in the sentinel column "
                f"(rows {_span(stray_n)}); conventions require data rows to be empty. "
                f"Harmless to the current export script, but it makes the column "
                f"indistinguishable from a mode flag.")

    # Group presence and order
    found = [t.cell(r, COL_ITEM) for r in t.rows[1:] if t.is_group_header(r)]
    if found != EXPECTED_GROUPS:
        missing = [g for g in EXPECTED_GROUPS if g not in found]
        extra = [g for g in found if g not in EXPECTED_GROUPS]
        detail = []
        if missing:
            detail.append(f"missing {missing}")
        if extra:
            detail.append(f"unexpected {extra}")
        if not detail:
            detail.append(f"out of order: {found}")
        add("ERROR", 1, "", "group-structure",
            "Six-group structure violated: " + "; ".join(detail))

    # Consecutive separator rows
    blanks = 0
    for n, row in enumerate(t.rows[1:], start=2):
        if t.is_separator(row):
            blanks += 1
            if blanks == 2:
                add("WARN", n, "", "blank-rows",
                    "More than one consecutive blank row; conventions allow exactly one between groups.")
        else:
            blanks = 0

    # Duplicate field names within this TAPP
    seen = defaultdict(list)
    for n, row, _ in t.content_rows():
        seen[t.cell(row, COL_ITEM)].append(n)
    for name, lines in seen.items():
        if len(lines) > 1:
            add("ERROR", lines[0], name, "duplicate-field",
                f"Field name appears {len(lines)} times (rows {lines}).")


def check_tiers(t: Tapp, out):
    add = lambda s, r, f, c, m: out.append(Finding(s, t.name, r, f, c, m))
    for n, row, _ in t.content_rows():
        item = t.cell(row, COL_ITEM)
        c, d = t.cell(row, COL_C), t.cell(row, COL_D)

        if not c:
            add("ERROR", n, item, "tier-missing", "Procedure-Level Tier (column C) is empty.")
        elif c not in VALID_C:
            add("ERROR", n, item, "tier-invalid",
                f"Procedure-Level Tier '{c}' is not one of {sorted(VALID_C)}.")

        if not d:
            add("ERROR", n, item, "tier-missing", "Analysis-Level Tier (column D) is empty.")
        elif d == "N/A":
            add("ERROR", n, item, "tier-d-na",
                "D=N/A is not a valid analysis-level tier. Use Read-Only for procedure-only fields.")
        elif d not in VALID_D:
            add("ERROR", n, item, "tier-invalid",
                f"Analysis-Level Tier '{d}' is not one of {sorted(VALID_D)}.")

        if d in ("Read-Only", "Editable") and c == "N/A":
            add("ERROR", n, item, "tier-inconsistent",
                f"D={d} requires a procedure-level value, but C=N/A. "
                f"{d} means 'imported from the procedure' — there is nothing to import.")


def check_modes(t: Tapp, out):
    add = lambda s, r, f, c, m: out.append(Finding(s, t.name, r, f, c, m))
    if t.sentinel_idx is None or not t.mode_cols:
        return
    span = range(FIRST_MODE_COL, t.sentinel_idx)
    for n, row in enumerate(t.rows[1:], start=2):
        if t.is_separator(row):
            continue
        item = t.cell(row, COL_ITEM)
        header_row = t.is_group_header(row)
        for i in span:
            v = t.cell(row, i)
            label = t.header[i] if i < len(t.header) else f"col{i}"
            if header_row:
                if v != "N":
                    add("WARN", n, item, "mode-flag-group-header",
                        f"Group header should have N in mode column '{label}', "
                        f"found '{v or 'empty'}'. Cosmetic: an empty flag is not Y, so the "
                        f"header still stays out of mode-filtered views.")
            elif v not in VALID_MODE_FLAG:
                add("ERROR", n, item, "mode-flag-invalid",
                    f"Mode column '{label}' has '{v or 'empty'}'; only Y or N are valid. "
                    f"Applicability of this field to this mode is undefined.")

    # A field applicable to no mode at all is almost certainly an error
    for n, row, _ in t.content_rows():
        flags = [t.cell(row, i) for i in span]
        if flags and all(f == "N" for f in flags):
            add("WARN", n, t.cell(row, COL_ITEM), "mode-all-N",
                "Field is flagged N for every mode; it will not appear in any mode-filtered view.")


def check_data_types(t: Tapp, out):
    add = lambda s, r, f, c, m: out.append(Finding(s, t.name, r, f, c, m))
    for n, row, _ in t.content_rows():
        item = t.cell(row, COL_ITEM)
        dt = t.cell(row, COL_TYPE)
        if not dt:
            add("WARN", n, item, "datatype-missing", "Data Type (column E) is empty.")
            continue
        if (dt not in VALID_DATA_TYPES and not NUMERIC_UNIT_RE.match(dt)
                and not COMPOUND_RE.match(dt)):
            syn = DATATYPE_SYNONYMS.get(dt.lower())
            mal = MALFORMED_COMPOUND.get(dt.lower())
            if syn:
                add("WARN", n, item, "datatype-synonym",
                    f"Data Type '{dt}' is a drifted spelling of '{syn}'. Use '{syn}'.")
            elif mal:
                add("WARN", n, item, "datatype-malformed-compound",
                    f"Data Type '{dt}' is not a well-formed compound. Use '{mal}'. "
                    f"See 'Compound data types' in conventions.md.")
            else:
                add("WARN", n, item, "datatype-invalid",
                    f"Data Type '{dt}' is not in the controlled vocabulary.")
        if dt.startswith("Controlled list") and item not in CONTROLLED_LIST_EXEMPT:
            ex = t.cell(row, COL_EXAMPLE)
            missing = [v for v in CONTROLLED_LIST_REQUIRED if v.lower() not in ex.lower()]
            if missing:
                add("WARN", n, item, "controlled-list-options",
                    f"Controlled list is missing required option(s) {missing} in column F.")

        # The forbidden-options check applies to EVERY type, not just controlled lists, and
        # has no exemptions. `Other: specify` left the vocabulary on 2026-08-30: it contradicts
        # a closed `Controlled list`, asks the wrong thing on a `Controlled list / Text`, and is
        # simply meaningless on `Text (free)` or `Numeric (...)`, where 137 cells across 43
        # fields were still carrying it after the controlled-list sweep.
        if True:
            ex = t.cell(row, COL_EXAMPLE)
            present = [v for v in CONTROLLED_LIST_FORBIDDEN if v.lower() in ex.lower()]
            if present:
                add("WARN", n, item, "forbidden-options",
                    f"Column F offers {present}. `Other: specify` left the vocabulary on "
                    f"2026-08-30: on `Controlled list` it contradicts a closed type; on "
                    f"`Controlled list / Text` the `/ Text` half already grants an unlisted "
                    f"answer, and it asks the wrong thing since a compound wants a listed term "
                    f"plus qualification; and on `Text (free)` or `Numeric (...)` it is "
                    f"meaningless. See the Legends sheet for the guidance it used to carry.")


def check_analytical_mode_vocabulary(t: Tapp, out):
    """Rule 3 — `Analytical Mode`'s Column F must mirror this TAPP's mode-flag headers exactly.

    conventions.md has required this from the start: the allowed values "must use the exact strings
    that appear as mode flag column headers in that TAPP. Do not paraphrase, abbreviate, or
    substitute synonyms", because sub-TAPP filtering resolves on that correspondence. Rule 3 also
    exempts the field from the generic `N/A | None | Other: specify` options for the same reason.

    Only the placement half of Rule 3 was ever enforced (Analytical Mode must be first in Group 4).
    The vocabulary half was not, and the four SEM tables drifted to an informal vocabulary — SEM
    offered `EDS | SEM-WDS | CL` against mode columns naming `EDS Point Analysis`, `EDS Mapping`,
    `WDS Point Analysis`, `WDS Mapping`, `CL Point Analysis`, `CL Mapping`. That bad vocabulary
    then generated 84 invalid publication cells, reported from outside as amds-ldeo/tapp#3:
    curators entered `EDS` and `CL` because the table told them those were the allowed values.
    Implemented 2026-08-24, after the fix, so it ships at 0 findings.

    A composite value joined with '; ' is valid when every member is a declared mode — the house
    form carries one such example last.
    """
    add = lambda s, r, f, c, m: out.append(Finding(s, t.name, r, f, c, m))
    if t.sentinel_idx is None or not t.mode_cols:
        return
    modes = [t.header[i] for i in range(FIRST_MODE_COL, t.sentinel_idx)]
    for n, row in enumerate(t.rows[1:], start=2):
        if t.cell(row, COL_ITEM) != "Analytical Mode":
            continue
        raw = t.cell(row, COL_EXAMPLE)
        for value in (v.strip() for v in raw.split("|")):
            value = re.sub(r"^e\.g\.,?\s*", "", value).strip().strip("'\"").strip()
            if not value:
                continue
            if value in GENERIC_LIST_OPTIONS:
                add("WARN", n, "Analytical Mode", "rule3-mode-vocab-generic",
                    f"Column F offers '{value}'. Rule 3 exempts `Analytical Mode` from the generic "
                    f"options: every procedure has a mode, and `Other: specify` would break the "
                    f"exact correspondence sub-TAPP filtering depends on.")
                continue
            parts = [x.strip() for x in value.split(";")]
            unknown = [x for x in parts if x not in modes]
            if unknown:
                add("WARN", n, "Analytical Mode", "rule3-mode-vocab",
                    f"Column F offers {unknown}, which {'are' if len(unknown) > 1 else 'is'} not "
                    f"among this TAPP's mode-flag headers {modes}. Rule 3 requires the exact "
                    f"strings — no paraphrase, abbreviation or synonym — because sub-TAPP "
                    f"filtering resolves on that correspondence, and because curators enter "
                    f"publication values from this list.")
        break


def check_naming(t: Tapp, out):
    add = lambda s, r, f, c, m: out.append(Finding(s, t.name, r, f, c, m))
    for n, row, _ in t.content_rows():
        item = t.cell(row, COL_ITEM)
        low = item.lower().strip()

        if low in FORBIDDEN_NAMES:
            add("WARN", n, item, "name-forbidden",
                f"Rule 1: use '{FORBIDDEN_NAMES[low]}' instead of '{item}'.")

        for w in LEVEL_WORDS:
            if re.search(rf"\b{w}\b", item):
                add("WARN", n, item, "name-level-encoding",
                    f"Field name contains '{w}'. Names must be level-neutral; "
                    f"the C/D columns encode level.")
                break

        if re.search(r"\bTarget\b", item) and item not in TARGET_EXEMPT:
            add("WARN", n, item, "name-level-encoding",
                "Field name contains 'Target'. Only 'Target Material' and "
                "'Target Feature(s)' are exempt from the level-neutral naming rule.")

        m = UNIT_PAREN_RE.search(item)
        if m:
            add("WARN", n, item, "name-unit-in-name",
                f"Field name embeds a unit '{m.group(0)}'. Units belong in Column E "
                f"(Data Type), e.g. 'Numeric (W)'.")

        if "element-specific" in low:
            add("WARN", n, item, "name-element-specific",
                "Use 'Analyte-Specific' rather than 'Element-Specific' (technique-agnostic).")

    # Column B describes the field, not the source paper
    for n, row, _ in t.content_rows():
        m = DESC_LEAK_RE.search(t.cell(row, COL_DESC))
        if m:
            add("WARN", n, t.cell(row, COL_ITEM), "description-source-leak",
                f"Description contains literature-assessment commentary ({m.group(0)!r}) — text about "
                f"what a source document contains belongs in a literature assessment column, not in "
                f"Column B. It also inflates the description, which can bias a reconciliation that "
                f"treats length as a quality signal.")

    # Column G should carry the Analyte-Specific label, not columns B or F
    for n, row, _ in t.content_rows():
        for col, letter in ((COL_DESC, "B"), (COL_EXAMPLE, "F")):
            if "element-specific" in t.cell(row, col).lower():
                add("WARN", n, t.cell(row, COL_ITEM), "name-element-specific",
                    f"Column {letter} uses 'Element-Specific'; the correct term is 'Analyte-Specific'.")


def check_rules(t: Tapp, out):
    """Rules 1, 3 and 5, plus the Group 1 coupling-field block."""
    add = lambda s, r, f, c, m: out.append(Finding(s, t.name, r, f, c, m))

    by_group = defaultdict(list)
    for n, row, group in t.content_rows():
        by_group[group].append((n, t.cell(row, COL_ITEM), t.cell(row, COL_C), t.cell(row, COL_D),
                                t.cell(row, COL_TYPE)))

    # Required tiers for named cross-TAPP fields
    for n, row, _ in t.content_rows():
        item = t.cell(row, COL_ITEM)
        if item in REQUIRED_TIERS:
            want_c, want_d = REQUIRED_TIERS[item]
            got_c, got_d = t.cell(row, COL_C), t.cell(row, COL_D)
            if (got_c, got_d) != (want_c, want_d):
                add("WARN", n, item, "rule-tier",
                    f"Expected C={want_c}, D={want_d}; found C={got_c}, D={got_d}.")

    # Rule 3 — Analytical Mode is the first field in Group 4
    g4 = by_group.get("4. Measurement Information", [])
    if not g4:
        add("ERROR", 1, "", "rule3", "Group 4 has no content rows.")
    elif g4[0][1] != "Analytical Mode":
        present = any(f[1] == "Analytical Mode" for f in g4)
        add("WARN", g4[0][0], g4[0][1], "rule3",
            f"Rule 3: 'Analytical Mode' must be the FIRST field in Group 4; "
            f"found '{g4[0][1]}'." + ("" if present else " Field is absent entirely."))

    # Rule 5 — Constants and Reference Values Used is the last field in Group 5
    g5 = by_group.get("5. Data Processing", [])
    if not g5:
        add("ERROR", 1, "", "rule5", "Group 5 has no content rows.")
    elif g5[-1][1] != "Constants and Reference Values Used":
        present = any(f[1] == "Constants and Reference Values Used" for f in g5)
        add("WARN", g5[-1][0], g5[-1][1], "rule5",
            f"Rule 5: 'Constants and Reference Values Used' must be the LAST field in Group 5; "
            f"found '{g5[-1][1]}'." + ("" if present else " Field is absent entirely."))

    # Group 1 must end with the four coupling fields, in order
    g1 = [f[1] for f in by_group.get("1. Procedure Identification", [])]
    if g1[-4:] != COUPLING_FIELDS:
        add("WARN", 1, "", "group1-coupling",
            f"Group 1 must end with {COUPLING_FIELDS} in that order; found {g1[-4:]}.")

    # Rule 5 / Rule 3 mode flags must be Y for every mode
    if t.sentinel_idx is not None and t.mode_cols:
        span = range(FIRST_MODE_COL, t.sentinel_idx)
        for n, row, _ in t.content_rows():
            item = t.cell(row, COL_ITEM)
            if item in ("Analytical Mode", "Constants and Reference Values Used"):
                flags = [t.cell(row, i) for i in span]
                if any(f != "Y" for f in flags):
                    add("WARN", n, item, "rule-mode-flags",
                        f"Must be Y for all modes (universal field); found {flags}.")


def check_keyed_by(t: Tapp, out):
    """Rule 7 — every field declares what its value repeats over."""
    add = lambda s, r, f, c, m: out.append(Finding(s, t.name, r, f, c, m))

    if t.header[COL_KEYEDBY].strip() != "Keyed By":
        add("ERROR", 1, "", "rule7-column",
            f"Column I must be headed 'Keyed By'; found "
            f"'{t.header[COL_KEYEDBY].strip()}'.")
        return

    used, defined, names = set(), __import__('collections').defaultdict(list), set()
    for n, row, _ in t.content_rows():
        item = t.cell(row, COL_ITEM)
        names.add(item)
        raw = t.cell(row, COL_KEYEDBY)

        if not raw.strip():
            add("ERROR", n, item, "rule7-blank",
                "Keyed By is blank. Every content row must declare a key, "
                "or '(none)' for a scalar field.")
            continue

        kind, domains, keys = parse_keyed_by(raw)
        for k in domains + keys:
            if k in KEY_FORBIDDEN:
                add("ERROR", n, item, "rule7-forbidden-key",
                    f"'{k}' is not a valid key — mode applicability is carried by "
                    f"the mode flag columns (Rule 3).")
            elif k not in KEY_VOCAB:
                add("WARN", n, item, "rule7-unknown-key",
                    f"'{k}' is not in the Rule 7 vocabulary. Declare technique-specific "
                    f"keys in Phase 0 and list them in the Legends sheet.")

        # 7.3 restricts the definer-with-a-key form to one domain and one key. A
        # compound on either side is refused rather than guessed at, because the token
        # order of the compound form is the open question the rule declines to settle.
        if kind == "defines_per" and (len(domains) > 1 or len(keys) > 1):
            add("ERROR", n, item, "rule7-compound-definer-key",
                f"'{raw}' uses a compound key in the 'defines: <domain> per <key>' form. "
                f"Rule 7.3 restricts both sides to a single key; the compound form is "
                f"deliberately unspecified until a real field requires it.")

        for k in domains:
            defined[k].append(item)
        used.update(keys)

    # Invariant 4 — EVERY key in use must have its domain enumerated somewhere.
    # Applies to secondary keys as well as anchors: a key whose domain is never
    # enumerated cannot be populated, whichever key it is.
    for k in sorted(used - set(defined)):
        add("ERROR", 1, "", "rule7-undefined-domain",
            f"Key '{k}' is used but no field declares 'defines: {k}'. A key whose "
            f"domain is never enumerated cannot be populated.")

    # Invariant 4b — exactly one definer per key. Two fields both claiming to
    # enumerate a domain leaves a consumer no way to know which builds the child table.
    for k, fields in sorted(defined.items()):
        if len(fields) > 1:
            add("ERROR", 1, fields[0], "rule7-multiple-definers",
                f"{len(fields)} fields declare 'defines: {k}' ({', '.join(fields)}). "
                f"Exactly one field may enumerate a key's domain; the others should be "
                f"keyed by it.")

    # Invariant 4c — a definer needs a consumer. 'defines: X' where nothing is keyed
    # by X declares a domain no field repeats over, which is a list, not a key.
    for k, fields in sorted(defined.items()):
        # Rules 8 and 9 make these mandatory for their own sake — Reported Variables and
        # Units declares the procedure's scope boundary, Sampling Unit declares the unit a
        # reported row corresponds to. Their definer role is secondary, so a TAPP with no
        # field keyed off them is not in error.
        if k not in used and not set(fields) & {RULE8_FIELD, RULE9_FIELD}:
            add("WARN", 1, fields[0], "rule7-unused-definer",
                f"'{fields[0]}' declares 'defines: {k}' but no field in this TAPP is "
                f"keyed by '{k}'. A field that merely holds a list is not a definer — "
                f"use '(none)'.")

    # Rules 8, 9 and 11 — mandatory fields.
    for fld, rule in ((RULE8_FIELD, "rule8"), (RULE9_FIELD, "rule9"), (RULE11_FIELD, "rule11")):
        if fld not in names:
            add("ERROR", 1, fld, rule, f"'{fld}' is mandatory in every TAPP.")

    # Rule 11 — Additional Notes is the LAST field of the whole TAPP, not merely the
    # last field of Group 6. Its scope is the document, and position is what says so.
    content = [t.cell(row, COL_ITEM) for _, row, _ in t.content_rows()]
    if content and RULE11_FIELD in content and content[-1] != RULE11_FIELD:
        add("ERROR", 1, content[-1], "rule11",
            f"Rule 11: '{RULE11_FIELD}' must be the last field of the TAPP; "
            f"found '{content[-1]}' after it.")

    # Comments must no longer duplicate mode applicability (Rule 7.6).
    modes = [h.strip() for h in t.header[FIRST_MODE_COL:t.sentinel_idx]]
    for n, row, _ in t.content_rows():
        c = t.cell(row, COL_COMMENT)
        if not c.strip():
            continue
        for mh in modes:
            if mh and mh.lower() in c.lower():
                add("WARN", n, t.cell(row, COL_ITEM), "rule7-comment-mode",
                    f"Comments names mode '{mh}', which the mode flag columns already "
                    f"carry. Remove it (Rule 7.6).")
                break


def check_dates(t: Tapp, out):
    add = lambda s, r, f, c, m: out.append(Finding(s, t.name, r, f, c, m))
    for n, row, _ in t.content_rows():
        v = t.cell(row, COL_UPDATE)
        if not v:
            add("INFO", n, t.cell(row, COL_ITEM), "date-missing",
                "Last Update (column H) is empty.")
        elif not DATE_RE.match(v):
            add("WARN", n, t.cell(row, COL_ITEM), "date-format",
                f"Last Update '{v}' is not YYYY-MM-DD.")


# ---------------------------------------------------------------------------
# Cross-TAPP checks
# ---------------------------------------------------------------------------

def file_digest(path):
    """sha256 of a file's bytes. Used instead of os.path.getsize for Rule 12, which two
    equal-sized but different files defeated on 2026-08-12."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_name(s: str) -> str:
    """Collapse cosmetic differences so near-duplicates group together."""
    s = s.lower().strip()
    s = re.sub(r"\s*([/(),;:-])\s*", r"\1", s)   # spaces around punctuation
    s = re.sub(r"\s+", " ", s)
    return s


def check_cross_tapp(tapps, out):
    add = lambda s, tp, f, c, m: out.append(Finding(s, tp, "", f, c, m))

    variants = defaultdict(set)          # normalized -> {(tapp, raw_name)}
    tiers = defaultdict(set)             # raw name -> {(tapp, C, D)}
    keyed = defaultdict(set)             # raw name -> {(tapp, Keyed By)}
    dtypes = defaultdict(set)            # raw name -> {(tapp, Data Type)}
    descs = defaultdict(set)             # raw name -> {(tapp, normalised description)}
    allowed = defaultdict(dict)          # raw name -> {tapp: frozenset(members)}  (7.8.11)

    for t in tapps:
        for _, row, _ in t.content_rows():
            raw = t.cell(row, COL_ITEM)
            variants[normalize_name(raw)].add((t.name, raw))
            tiers[raw].add((t.name, t.cell(row, COL_C), t.cell(row, COL_D)))
            keyed[raw].add((t.name, t.cell(row, COL_KEYEDBY).strip()))
            dtypes[raw].add((t.name, t.cell(row, COL_TYPE).strip()))
            descs[raw].add((t.name, re.sub(r"\s+", " ", t.cell(row, COL_DESC).strip())))
            if t.cell(row, COL_TYPE).strip().startswith("Controlled list"):
                allowed[raw][t.name] = colf_members(t.cell(row, COL_EXAMPLE))

    # Near-duplicate spellings of the same field across TAPPs
    for _, entries in sorted(variants.items()):
        spellings = {raw for _, raw in entries}
        if len(spellings) > 1:
            detail = "; ".join(f"{tp}: '{raw}'" for tp, raw in sorted(entries))
            add("WARN", "(cross-TAPP)", sorted(spellings)[0], "name-variant",
                f"Same field spelled {len(spellings)} ways — {detail}. "
                f"Rule 1 requires identical names across TAPPs.")

    # Same field name, different tiers
    for raw, entries in sorted(tiers.items()):
        combos = {(c, d) for _, c, d in entries}
        if len(combos) > 1 and len(entries) > 1:
            detail = "; ".join(f"{tp}: C={c},D={d}" for tp, c, d in sorted(entries))
            add("INFO", "(cross-TAPP)", raw, "tier-divergence",
                f"Tier assignment differs across {len(entries)} TAPPs — {detail}. "
                f"Intentional divergence must be recorded in precedents.md (Rule 2/4).")

    # Rule 7.8.7 — same field name, different Keyed By. Keys are uniform across TAPPs by
    # default; a divergence is only acceptable when it is registered with a recorded reason.
    # This invariant was specified in conventions 7.8.7 from the start and the register constant
    # was defined, but the check itself was never implemented — so every divergence introduced
    # between the 2026-08-11 retrofit and 2026-08-12 passed silently. Implemented 2026-08-12.
    for raw, entries in sorted(keyed.items()):
        distinct = {k for _, k in entries if k}
        if len(distinct) <= 1 or len(entries) <= 1:
            continue
        detail = "; ".join(f"{tp}: {k or '(blank)'}" for tp, k in sorted(entries))
        if raw in KEYED_BY_TECHNIQUE_DEPENDENT:
            add("INFO", "(cross-TAPP)", raw, "keyed-by-divergence-registered",
                f"Keyed By differs across {len(entries)} TAPPs — {detail}. Registered as "
                f"technique-dependent: {KEYED_BY_TECHNIQUE_DEPENDENT[raw]}")
        else:
            add("WARN", "(cross-TAPP)", raw, "keyed-by-divergence",
                f"Keyed By differs across {len(entries)} TAPPs — {detail}. Keys are uniform by "
                f"default (Rule 7.8.7): either make them agree, or add '{raw}' to "
                f"KEYED_BY_TECHNIQUE_DEPENDENT with a rationale recorded in precedents.md.")

    # Rule 7.8.7 companion — key divergence across field-name variants. See
    # KEY_NAME_VARIANT_EXEMPT for why the test is a two-word suffix rather than similarity.
    def name_words(s):
        return re.sub(r"[^a-z0-9 ]", " ", s.lower()).split()

    keysets = {raw: {k for _, k in ents if k} for raw, ents in keyed.items()}
    for short in sorted(keysets):
        ws = name_words(short)
        if len(ws) < 2:
            continue                       # one-word names are too generic to imply a variant
        for long in sorted(keysets):
            wl = name_words(long)
            if long == short or len(wl) <= len(ws) or wl[-len(ws):] != ws:
                continue
            if keysets[short] == keysets[long]:
                continue
            detail = (f"'{long}' = {sorted(keysets[long])}; "
                      f"'{short}' = {sorted(keysets[short])}")
            pair = (short, long)
            if pair in KEY_NAME_VARIANT_EXEMPT:
                add("INFO", "(cross-TAPP)", long, "keyed-by-name-variant-registered",
                    f"Name variant with divergent keys — {detail}. Registered: "
                    f"{KEY_NAME_VARIANT_EXEMPT[pair]}")
            else:
                add("WARN", "(cross-TAPP)", long, "keyed-by-name-variant",
                    f"'{long}' ends with the field name '{short}' but carries a different Keyed "
                    f"By — {detail}. 7.8.7 groups by exact name, so a qualifier prefix hides key "
                    f"divergence from it. Either make the keys agree, rename per Rule 1, or "
                    f"register the pair in KEY_NAME_VARIANT_EXEMPT with a rationale.")

    # Rule 6.4 / 7.8.9 — same field name, materially different description. Implemented
    # 2026-08-12; the 89 divergences present at that date are frozen in
    # COLB_DIVERGENCE_TRIAGED so this ships at 0 WARN and catches new drift.
    import difflib
    for raw, entries in sorted(descs.items()):
        texts = {d for _, d in entries if d}
        if len(texts) <= 1 or len(entries) <= 1:
            continue
        ts = sorted(texts)
        worst = min(difflib.SequenceMatcher(None, a, b).ratio()
                    for i, a in enumerate(ts) for b in ts[i + 1:])
        if worst >= 0.90:
            continue                       # trivial rewording, not worth a finding
        tapps_n = len({tp for tp, _ in entries})
        if raw in COLB_DIVERGENCE_TRIAGED:
            verdict, _ = COLB_DIVERGENCE_TRIAGED[raw]
            sev = "INFO"
            msg = (f"Description differs across {tapps_n} TAPPs in {len(texts)} variants "
                   f"(similarity {worst:.2f}) — triaged 2026-08-12 as {verdict}.")
            if verdict != "PRINCIPLED":
                msg += (" On the harmonisation backlog: see "
                        "analysis/Triage_ColB_Uniformity_2026-08-12.csv.")
            add(sev, "(cross-TAPP)", raw, f"colb-divergence-{verdict.lower()}", msg)
        else:
            add("WARN", "(cross-TAPP)", raw, "colb-divergence",
                f"Description differs across {tapps_n} TAPPs in {len(texts)} variants "
                f"(similarity {worst:.2f}) and is NOT in COLB_DIVERGENCE_TRIAGED. Descriptions are "
                f"uniform by default (Rule 6.4): make them agree, or triage the field and record it.")

    # 7.8.11 — same field name, different ALLOWED VALUES. Column F is normative on a
    # controlled list (it IS the domain) and merely illustrative on `Text (free)` or
    # `Numeric (...)`, so this check is scoped to controlled-list types: 18 fields diverge
    # there against 109 that diverge on example lists, where variation is expected and
    # correct. Implemented 2026-08-30, the 18 frozen in COLF_DIVERGENCE_TRIAGED so it ships
    # at 0 WARN and catches new drift.
    #
    # Column F was the last content column with no cross-TAPP check, and it earned one:
    # three separate defects in a single 2026-08-30 pass traced to it — `Dwell Time per
    # Pixel` kept unit-free numerals after its type moved to `Numeric + unit`; the
    # interference flags read `Yes | No | N/A` while describing none of 51 attested cells;
    # and `Technique` drifted to `Other: specify` in 13 of 16 TAPPs. Every one was found by
    # reading, because nothing was looking.
    for raw, per in sorted(allowed.items()):
        if len(per) < 2:
            continue
        vs = list({frozenset(m) for m in per.values()})
        if len(vs) <= 1:
            continue
        worst = min((len(a & b) / len(a | b) if (a | b) else 1.0)
                    for i, a in enumerate(vs) for b in vs[i + 1:])
        n_tapps = len(per)
        if raw in COLF_DIVERGENCE_TRIAGED:
            verdict, why = COLF_DIVERGENCE_TRIAGED[raw]
            msg = (f"Allowed values differ across {n_tapps} TAPPs in {len(vs)} variants "
                   f"(worst overlap {worst:.2f}) — triaged 2026-08-30 as {verdict}. {why}")
            add("INFO", "(cross-TAPP)", raw, f"colf-divergence-{verdict.lower()}", msg)
        else:
            add("WARN", "(cross-TAPP)", raw, "colf-divergence",
                f"Allowed values differ across {n_tapps} TAPPs in {len(vs)} variants "
                f"(worst overlap {worst:.2f}) and the field is NOT in COLF_DIVERGENCE_TRIAGED. "
                f"On a controlled list Column F IS the domain, so divergence is either drift to "
                f"harmonise or a technique-appropriate difference to register with a rationale.")

    # Rule 7.4a corollary — every `defines:` field must share an opening sentence across the TAPPs
    # that carry it. See COLB_DEFINER_STEM_EXEMPT for why similarity alone was not enough.
    def common_prefix(strings):
        lo, hi = min(strings), max(strings)      # lexicographic bounds fix the common prefix
        for i, ch in enumerate(lo):
            if i >= len(hi) or ch != hi[i]:
                return lo[:i]
        return lo

    for raw, entries in sorted(descs.items()):
        if not any(k.startswith("defines:") for _, k in keyed.get(raw, set()) if k):
            continue
        texts = sorted({d for _, d in entries if d})
        if len(texts) <= 1:
            continue
        stem = common_prefix(texts)
        if ". " in stem or stem.endswith("."):
            continue                              # they agree on at least the first sentence
        tapps_n = len({tp for tp, _ in entries})
        if raw in COLB_DEFINER_STEM_EXEMPT:
            add("INFO", "(cross-TAPP)", raw, "colb-definer-stem-registered",
                f"`defines:` field whose {len(texts)} descriptions across {tapps_n} TAPPs share no "
                f"opening sentence ({len(stem)} chars in common). Registered: "
                f"{COLB_DEFINER_STEM_EXEMPT[raw]}")
        else:
            add("WARN", "(cross-TAPP)", raw, "colb-definer-stem",
                f"`defines:` field whose {len(texts)} descriptions across {tapps_n} TAPPs share no "
                f"opening sentence ({len(stem)} chars in common). A definer states what its key "
                f"domain IS, so the TAPPs must agree on that sentence; technique-specific detail "
                f"belongs after it. Give them a shared stem, or register the field in "
                f"COLB_DEFINER_STEM_EXEMPT with a rationale.")

    # Rule 7.8.10 — same field name, different Data Type. Column E is read by downstream schema
    # generation, so a field typed three ways generates the same metadata item in three
    # incompatible shapes. Divergences present at 2026-08-24 are frozen in
    # COLE_DIVERGENCE_TRIAGED so this ships at 0 WARN and catches new drift.
    for raw, entries in sorted(dtypes.items()):
        seen = {d for _, d in entries if d}
        if len(seen) <= 1 or len(entries) <= 1:
            continue
        tapps_n = len({tp for tp, _ in entries})
        detail = "; ".join(f"{tp}: {d or '(blank)'}" for tp, d in sorted(entries))
        if raw in COLE_DIVERGENCE_TRIAGED:
            verdict, _ = COLE_DIVERGENCE_TRIAGED[raw]
            msg = (f"Data Type differs across {tapps_n} TAPPs in {len(seen)} variants — {detail}. "
                   f"Triaged 2026-08-24 as {verdict}.")
            if verdict != "PRINCIPLED":
                msg += (" On the harmonisation backlog: see "
                        "analysis/Triage_ColE_Uniformity_2026-08-24.csv.")
            add("INFO", "(cross-TAPP)", raw, f"cole-divergence-{verdict.lower()}", msg)
        else:
            add("WARN", "(cross-TAPP)", raw, "cole-divergence",
                f"Data Type differs across {tapps_n} TAPPs in {len(seen)} variants — {detail}. "
                f"Data Types are uniform by default (Rule 7.8.10): Column E drives schema "
                f"generation, so divergence ships one metadata item in several shapes. Make them "
                f"agree, or triage the field and record it in COLE_DIVERGENCE_TRIAGED.")

    # Rule 7.8.10 companion — type divergence across field-name VARIANTS, reusing the 7.8.7
    # suffix test. KEY_NAME_VARIANT_EXEMPT is consulted first: a rationale recording why two
    # names are two different FIELDS settles Column E as well as Column I.
    typesets = {raw: {d for _, d in ents if d} for raw, ents in dtypes.items()}
    for short in sorted(typesets):
        ws = name_words(short)
        if len(ws) < 2:
            continue
        for long in sorted(typesets):
            wl = name_words(long)
            if long == short or len(wl) <= len(ws) or wl[-len(ws):] != ws:
                continue
            if typesets[short] == typesets[long]:
                continue
            detail = (f"'{long}' = {sorted(typesets[long])}; "
                      f"'{short}' = {sorted(typesets[short])}")
            pair = (short, long)
            if pair in KEY_NAME_VARIANT_EXEMPT:
                add("INFO", "(cross-TAPP)", long, "cole-name-variant-registered",
                    f"Name variant with divergent Data Types — {detail}. Registered as different "
                    f"fields in KEY_NAME_VARIANT_EXEMPT: {KEY_NAME_VARIANT_EXEMPT[pair]}")
            elif pair in COLE_NAME_VARIANT_TRIAGED:
                add("INFO", "(cross-TAPP)", long, "cole-name-variant-triaged",
                    f"Name variant with divergent Data Types — {detail}. Triaged 2026-08-24: "
                    f"{COLE_NAME_VARIANT_TRIAGED[pair]}")
            else:
                add("WARN", "(cross-TAPP)", long, "cole-name-variant",
                    f"'{long}' ends with the field name '{short}' but carries a different Data "
                    f"Type — {detail}. 7.8.10 groups by exact name, so a qualifier prefix hides "
                    f"type divergence from it. Either make the types agree, rename per Rule 1, or "
                    f"register the pair in COLE_NAME_VARIANT_TRIAGED with a rationale.")


# --------------------------------------------------------------------------- #
# Library freshness — documentation and registers, not just TAPPs
# --------------------------------------------------------------------------- #
# Added 2026-08-12 after a hand audit found three shipped documents describing a library
# that no longer existed: README_TAPP_for_Schema_Generation.md still defined the analysis
# object as one sample, SKILL.md's key list omitted `sample`, and two live registers pointed
# at superseded files. None of it was caught, because every check to that point looked only
# at TAPPs. The rule the library keeps relearning (7.8): a documented invariant is not an
# enforced one — and documentation itself is subject to the same rule.
#
# A file is treated as a LIVE document (must describe the current library) unless it is a
# dated record. Dated records are correct to name the state at their date and are skipped:
#   * a date in the filename (2026-08-12 or 20260812), or
#   * an explicit entry in HISTORICAL_DOCS.
#
# RETIRED_FIELDS is the one part that needs maintaining by hand: add an entry whenever a
# field is retired or renamed, and the check will find every live document still naming it.
HISTORICAL_DOCS = {
    "Project Files/Design Notes/TAPP_Development_Log.md":
        "dated change history — naming retired fields is how a log works",
}
RETIRED_FIELDS = {
    "Mass Cycles per Replicate":       "renamed 2026-08-17 -> Number of Scans per Replicate — 'cycle' is "
                                       "reserved for simultaneous multi-collection readouts, a "
                                       "different acquisition mode from a sequential mass scan",
    "In-Run Isotope Ratio Reproducibility and Assessment Method":
                                       "renamed 2026-08-17 -> Within-Session Analytical Precision "
                                       "and Assessment Method — the 'In-Run' name contradicted the "
                                       "field's own definition and was drawing internal precision",
    "Between-Session Reproducibility and Assessment Method":
                                       "renamed 2026-08-17 -> Between-Session (Long-Term) Analytical "
                                       "Precision and Assessment Method — VIM3 reserves "
                                       "'reproducibility' for different-laboratory conditions",
    "Number of Replicates per Sample": "renamed 2026-08-17 -> Number of Replicates — 'per Sample' is "
                                       "wrong for spatially resolved techniques, where replicates "
                                       "are per grain or location",
    "Sensitivity as Useful Yield":     "renamed 2026-08-17 -> Instrument Sensitivity — merged with the "
                                       "Solution field; useful yield survives as one permitted "
                                       "expression, reported once in 28 LA papers",
    "Make-up Gas Flow Rate":           "renamed 2026-08-17 -> Make-up Gas and Flow Rate — reconciled "
                                       "with the LA name; the field holds gas identity as well as flow",
    "Plasma / Make-up Gas Addition":   "renamed 2026-08-17 -> Make-up Gas and Flow Rate — the 'Plasma' "
                                       "prefix collided with Coolant (Plasma) Gas Flow Rate",
    "Monitored Isotopes":              "renamed 2026-08-17 -> Monitored Masses — the field defines "
                                       "the channel domain, which contains reaction-product and "
                                       "adduct masses as well as atomic isotopes",
    "Minimum Resolvable Feature Size": "retired 2026-08-12 (Lab-XCT v17) — redundant with "
                                       "Partial Volume Effect Criteria",
    "Mass Resolution per Analyte":     "renamed 2026-08-12 -> Mass Resolution Assignment",
    "Data Reduction Software":         "renamed 2026-08-14 -> Data Processing Software(s) — "
                                       "not every technique reduces data; XCT reconstruction expands it",
    "Segmentation and Analysis Software":
                                       "absorbed 2026-08-14 -> Data Processing Software(s) (Lab-XCT). "
                                       "Lab-XCT retains Reconstruction Software as a technique-specific field",
}
DOC_ROOTS = ("Claude Skills for TAPP", "Project Files", ".")
DATED_RE = re.compile(r"(20\d{2}-\d{2}-\d{2}|20\d{6})")

# Only prose documents and the two live registers are checked. TAPP CSVs are data, not
# documentation: every superseded Lab-XCT version legitimately still contains a retired
# field as one of its rows, and flagging those would bury the real findings.
LIVE_REGISTERS = {"TAPP_Module_Register.csv", "TAPP_Composed_Variants.csv"}
SKIP_DIR_PARTS = ("Superseded", "Archive", "Current TAPPs", "Literature Assessment",
                  "Seed Papers", "One-shot")


def rel_is_register(fname):
    return fname in LIVE_REGISTERS


# Files whose job includes naming a field in order to record that it was retired or renamed.
# Distinct from HISTORICAL_DOCS: these are live and authoritative, and a retirement that went
# unrecorded in them would be the actual defect.
RETIRED_FIELD_MENTION_OK = {
    "Claude Skills for TAPP/references/precedents.md":
        "the precedent recording a retirement has to name what it retired",
    "Claude Skills for TAPP/references/conventions.md":
        "rule text closing a deferred question has to name the field the question was about",
}
TAPP_REF_RE = re.compile(r"([A-Za-z0-9_\-]+_TAPP(?:_UPb)?)_v(\d+)\.csv")


def check_library_freshness(root, out):
    """Live documents and registers must describe the library as it currently is."""
    add = lambda sev, f, code, msg: out.append(Finding(sev, "(library)", "", f, code, msg))
    regp = os.path.join(root, "composed_tapps.json")
    if not os.path.exists(regp):
        return
    reg = json.load(open(regp, encoding="utf-8"))
    current = {os.path.basename(e["tapp"]).rsplit("_v", 1)[0]: os.path.basename(e["tapp"])
               for e in reg["composed"]}

    # --- live module register vs the manifests it mirrors
    modreg = os.path.join(root, "Project Files", "Registers & Planning", "TAPP_Module_Register.csv")
    if os.path.exists(modreg):
        live, used = {}, Counter()
        for j in sorted(glob.glob(os.path.join(root, "Claude Skills for TAPP", "modules", "Module_*.json"))):
            d = json.load(open(j, encoding="utf-8"))
            live[d["module"]] = d["version"]
        for e in reg["composed"]:
            for m in e["modules"]:
                used[m["name"]] += 1
        for r in list(csv.reader(open(modreg, encoding="utf-8-sig")))[1:]:
            if not r or not r[0].strip():
                continue
            m = r[0].strip()
            if m in live and len(r) > 5 and r[5].strip() != live[m]:
                add("WARN", m, "register-stale-module-version",
                    f"TAPP_Module_Register.csv records {m} v{r[5].strip()}; the manifest says "
                    f"v{live[m]}. Refresh the register.")
            if len(r) > 6 and r[6].strip() != f"{used.get(m, 0)} TAPP(s)":
                add("WARN", m, "register-stale-consumers",
                    f"TAPP_Module_Register.csv records '{r[6].strip()}' consumers for {m}; "
                    f"composed_tapps.json has {used.get(m, 0)}.")

    # --- live documents naming superseded versions or retired fields
    seen = set()
    for base in DOC_ROOTS:
        for dp, dn, fn in os.walk(os.path.join(root, base)):
            dn[:] = [d for d in dn if not _excluded(d) and d not in (".git", "__pycache__")]
            for f in fn:
                if not (f.endswith(".md") or rel_is_register(f)):
                    continue
                path = os.path.join(dp, f)
                rel = os.path.relpath(path, root)
                if rel in seen:
                    continue
                seen.add(rel)
                if DATED_RE.search(f) or rel in HISTORICAL_DOCS:
                    continue
                if any(part in rel for part in SKIP_DIR_PARTS):
                    continue
                try:
                    text = open(path, encoding="utf-8", errors="replace").read()
                except OSError:
                    continue
                for stem, v in set(TAPP_REF_RE.findall(text)):
                    name = f"{stem}_v{v}.csv"
                    if stem in current and name != current[stem]:
                        add("WARN", rel, "doc-stale-version-ref",
                            f"names '{name}' but the current file is '{current[stem]}'. A live "
                            f"document must not point at a superseded version; date the file or "
                            f"add it to HISTORICAL_DOCS if it is a record rather than a guide.")
                for fld, why in RETIRED_FIELDS.items():
                    if rel in RETIRED_FIELD_MENTION_OK:
                        break
                    if re.search(r"(?<![A-Za-z])" + re.escape(fld) + r"(?![A-Za-z])", text):
                        add("WARN", rel, "doc-retired-field",
                            f"names the field '{fld}' — {why}. Update the text, or add the file "
                            f"to HISTORICAL_DOCS if it is a dated record.")


def check_module_versions(root, out):
    """Rule 6 — a module's manifest version must match every version recorded for it in
    composed_tapps.json.

    A module's version lives in two places and nothing checked that they agreed. Both known
    divergences were found by hand on 2026-08-12: Module_ReportingCore's manifest said 3 while
    the register claimed 4 against all 16 consumers, and Module_MCICPMS said 3 against a
    register claim of 4 on all 3. Neither was noticed for as long as it had existed.

    Resolution convention, applied to both and recorded in their manifests: the register is
    written per TAPP by the composition tooling, the manifest is hand-edited, so the manifest is
    the likelier one to have been missed and is the one brought into line. Where the manifest is
    also gaining a content change in the same pass, skip past the register's claimed version
    rather than colliding with it — ReportingCore went 3 -> 5 for that reason.

    A module present in modules/ but composed into nothing is INFO, not WARN: Module_ArAr is
    built ahead of its TAPP, which Rule 6.10 permits.
    """
    add = lambda s, f, c, m: out.append(Finding(s, "(modules)", "", f, c, m))
    reg_path = os.path.join(root, "composed_tapps.json")
    mod_dir = os.path.join(root, "Claude Skills for TAPP", "modules")
    if not (os.path.exists(reg_path) and os.path.isdir(mod_dir)):
        return
    try:
        reg = json.load(open(reg_path, encoding="utf-8"))
    except Exception as exc:                                  # noqa: BLE001
        add("WARN", "composed_tapps.json", "module-version-unreadable", f"could not read: {exc}")
        return

    recorded = defaultdict(Counter)
    for entry in reg.get("composed", []):
        for m in entry.get("modules", []):
            recorded[m.get("name")][m.get("version")] += 1

    for path in sorted(glob.glob(os.path.join(mod_dir, "Module_*.json"))):
        try:
            man = json.load(open(path, encoding="utf-8"))
        except Exception as exc:                              # noqa: BLE001
            add("WARN", os.path.basename(path), "module-version-unreadable",
                f"could not read: {exc}")
            continue
        name, mver = man.get("module"), man.get("version")
        seen = recorded.get(name)
        if not seen:
            add("INFO", name, "module-unused",
                f"Module '{name}' (manifest v{mver}) is composed into no TAPP. Legitimate where a "
                f"module is built ahead of its technique (Rule 6.10); a finding only so it does "
                f"not sit unnoticed if the TAPP was expected.")
            continue
        if set(seen) != {mver}:
            detail = ", ".join(f"v{v} in {c} TAPP(s)" for v, c in sorted(seen.items()))
            add("WARN", name, "module-version-drift",
                f"Module '{name}' manifest says v{mver}, composed_tapps.json records {detail}. "
                f"The two must agree. Bring the manifest into line with the register (it is "
                f"hand-edited and is the likelier one to have been missed), recording the reason "
                f"in the manifest's 'decisions'; where the same pass also changes module content, "
                f"skip past the register's claimed version rather than colliding with it.")


def check_current_tapps(tapps, root, out):
    """Rule 12 — the `Current TAPPs/` mirror must hold the latest CSV + xlsx for every TAPP.

    The mirror exists to be shared as a unit, so a stale one is worse than none: a recipient cannot
    tell that what they were handed is out of date. Reported at WARN so it cannot sit unnoticed.
    Every finding is fixed by one command: `Project Files/Scripts/sync_current_tapps.py --apply`.
    """
    add = lambda s, f, c, m: out.append(Finding(s, "(Rule 12)", "", f, c, m))
    mirror = os.path.join(root, CURRENT_DIR)

    if not os.path.isdir(mirror):
        add("WARN", "", "rule12-missing-folder",
            f"'{CURRENT_DIR}/' does not exist at the library root. Rule 12 requires a flat mirror of "
            f"the latest CSV + xlsx for every TAPP; run sync_current_tapps.py --apply.")
        return

    present = {f for f in os.listdir(mirror)
               if os.path.isfile(os.path.join(mirror, f))
               and re.search(r"_TAPP_v\d+(\.\d+)?\.(csv|xlsx)$", f)}
    expected = {}
    for t in tapps:
        for ext in ("csv", "xlsx"):
            src = t.path[:-4] + "." + ext
            if os.path.exists(src):
                expected[os.path.basename(src)] = src

    for name, src in sorted(expected.items()):
        dst = os.path.join(mirror, name)
        if not os.path.exists(dst):
            # is an OLDER version of the same TAPP sitting there instead?
            stem = name.rsplit("_v", 1)[0]
            ext = name.rsplit(".", 1)[1]
            stale = sorted(f for f in present
                           if f.rsplit("_v", 1)[0] == stem and f.endswith("." + ext))
            if stale:
                add("WARN", name, "rule12-stale",
                    f"'{CURRENT_DIR}/' holds {', '.join(stale)} but the current version is {name}. "
                    f"Rule 12: the mirror must replace the previous version, not accumulate.")
            else:
                add("WARN", name, "rule12-absent",
                    f"{name} is missing from '{CURRENT_DIR}/'.")
            continue
        # Content hash, not size. Size was the original test and it silently missed a change:
        # on 2026-08-12 a regenerated xlsx and its mirror copy were both exactly 42785 bytes
        # with different content. `sync_current_tapps.py` carried the same defect and was fixed
        # in step with this. See conventions.md 12.2.
        if file_digest(dst) != file_digest(src):
            add("WARN", name, "rule12-differs",
                f"'{CURRENT_DIR}/{name}' differs in content from the library copy. The mirror is a "
                f"copy, never an editing target — re-sync to discard local changes.")

    for name in sorted(present - set(expected)):
        add("WARN", name, "rule12-extra",
            f"'{CURRENT_DIR}/{name}' does not correspond to any current TAPP. Either it is a "
            f"superseded version that should have been replaced, or a TAPP that has been retired.")


def check_group1_template(tapps, template_path, out, restrict=None):
    """Compare each TAPP's Group 1 against the canonical template (Rule 1).

    `restrict` limits the template to a named field set. Needed since 2026-08-14: Group 1 is
    owned by Module_Core, whose CSV also carries the 10 universals belonging to Groups 2-6.
    Without the restriction every one of those would be read as a missing Group 1 field.
    """
    if not os.path.exists(template_path):
        out.append(Finding("WARN", "(template)", "", "", "group1-template",
                           f"Template not found at {template_path}; Group 1 comparison skipped."))
        return

    with open(template_path, newline="", encoding="utf-8-sig") as f:
        trows = list(csv.reader(f))

    tmpl = {}
    order = []
    for r in trows[1:]:
        a = r[0].strip() if r else ""
        if not a or re.match(r"^\d+\.\s", a):
            continue
        if restrict is not None and a not in restrict:
            continue
        tmpl[a] = (r[COL_DESC].strip(), r[COL_C].strip(), r[COL_D].strip(), r[COL_TYPE].strip())
        order.append(a)

    for t in tapps:
        g1 = [(n, t.cell(row, COL_ITEM), t.cell(row, COL_DESC), t.cell(row, COL_C),
               t.cell(row, COL_D), t.cell(row, COL_TYPE))
              for n, row, g in t.content_rows() if g == "1. Procedure Identification"]
        names = [f[1] for f in g1]

        for missing in [k for k in order if k not in names]:
            out.append(Finding("WARN", t.name, "", missing, "group1-missing",
                               "Group 1 field present in the template is missing from this TAPP."))
        for extra in [k for k in names if k not in tmpl]:
            out.append(Finding("INFO", t.name, "", extra, "group1-extra",
                               "Group 1 field is not in the template."))

        if names and [k for k in names if k in tmpl] != [k for k in order if k in names]:
            out.append(Finding("WARN", t.name, "", "", "group1-order",
                               "Group 1 field order differs from the template."))

        for n, name, desc, c, d, dtype in g1:
            if name not in tmpl:
                continue
            t_desc, t_c, t_d, t_type = tmpl[name]
            if (c, d) != (t_c, t_d):
                out.append(Finding("WARN", t.name, n, name, "group1-tier",
                                   f"Tier differs from template: TAPP C={c},D={d} vs "
                                   f"template C={t_c},D={t_d}."))
            if t_type and dtype != t_type:
                out.append(Finding("WARN", t.name, n, name, "group1-datatype",
                                   f"Data Type differs from template: '{dtype}' vs '{t_type}'."))
            if t_desc and desc != t_desc:
                out.append(Finding("INFO", t.name, n, name, "group1-description",
                                   "Description differs from the template. Column B is "
                                   "template-owned; only Column F is technique-specific."))


# ---------------------------------------------------------------------------
# Discovery and reporting
# ---------------------------------------------------------------------------

def _excluded(dirname):
    """Directories whose TAPPs are not part of the live library.

    Pattern-based rather than a fixed list, so archiving a TAPP is a matter of moving it
    into a folder named Superseded/Archive rather than also editing this script.
    """
    if dirname.startswith("."):
        return True
    low = dirname.lower()
    return (dirname == "unpacked_tapp"
            or dirname == CURRENT_DIR
            or low.startswith("superseded")
            or "archive" in low)


def version_of(path):
    m = re.search(r"_v(\d+(?:\.\d+)?)\.csv$", os.path.basename(path))
    return float(m.group(1)) if m else -1.0


def discover(root, all_versions=False):
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not _excluded(d)]
        for fn in filenames:
            if re.search(r"_TAPP_v\d+(\.\d+)?\.csv$", fn):
                found.append(os.path.join(dirpath, fn))
    if all_versions:
        return sorted(found)
    latest = {}
    for p in found:
        key = os.path.basename(p).rsplit("_v", 1)[0]
        if key not in latest or version_of(p) > version_of(latest[key]):
            latest[key] = p
    return [latest[k] for k in sorted(latest)]


def load(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return Tapp(path, list(csv.reader(f)))


SEV_ORDER = {"ERROR": 0, "WARN": 1, "INFO": 2}


def collapse(findings, threshold=5):
    """Fold repetitive (tapp, check) groups into one summary finding.

    A check that fires on 80 rows of one file is one problem, not eighty.
    """
    groups = defaultdict(list)
    for f in findings:
        groups[(f.tapp, f.check, f.severity)].append(f)

    out = []
    for (tapp, check, sev), fs in groups.items():
        if len(fs) < threshold:
            out.extend(fs)
            continue
        rows = sorted(int(f.row) for f in fs if str(f.row).isdigit())
        fields = sorted({f.field for f in fs if f.field})
        shown = ", ".join(fields[:4]) + (f", … (+{len(fields) - 4} more)" if len(fields) > 4 else "")
        out.append(Finding(
            sev, tapp, rows[0] if rows else "", f"[{len(fs)} occurrences]", check,
            f"{fs[0].message} — affects {len(fs)} rows"
            + (f" ({_span(rows)})" if rows else "")
            + (f"; fields: {shown}" if fields else "")))
    return out


def report(findings, min_severity, out=sys.stdout, do_collapse=True):
    threshold = SEV_ORDER[min_severity]
    shown = [f for f in findings if SEV_ORDER[f.severity] <= threshold]
    if do_collapse:
        shown = collapse(shown)

    by_tapp = defaultdict(list)
    for f in shown:
        by_tapp[f.tapp].append(f)

    for tapp in sorted(by_tapp):
        fs = sorted(by_tapp[tapp], key=lambda x: (SEV_ORDER[x.severity], str(x.row), x.check))
        counts = defaultdict(int)
        for f in fs:
            counts[f.severity] += 1
        summary = "  ".join(f"{s}:{counts[s]}" for s in ("ERROR", "WARN", "INFO") if counts[s])
        print(f"\n{'=' * 100}", file=out)
        print(f"{tapp}   [{summary}]", file=out)
        print("=" * 100, file=out)
        for f in fs:
            loc = f"row {f.row}" if f.row else "—"
            head = f"  {f.severity:<5} {loc:<9} {f.check:<24}"
            print(f"{head} {f.field}", file=out)
            print(f"{' ' * len(head)} {f.message}", file=out)

    total = defaultdict(int)
    for f in findings:
        total[f.severity] += 1
    print(f"\n{'=' * 100}", file=out)
    print("SUMMARY", file=out)
    print("=" * 100, file=out)
    for s in ("ERROR", "WARN", "INFO"):
        print(f"  {s:<6} {total[s]}", file=out)
    print(f"  {'TOTAL':<6} {sum(total.values())}", file=out)

    by_check = defaultdict(int)
    for f in findings:
        if SEV_ORDER[f.severity] <= threshold:
            by_check[(f.severity, f.check)] += 1
    if by_check:
        print("\n  By check:", file=out)
        for (sev, check), n in sorted(by_check.items(), key=lambda x: (-x[1], x[0])):
            print(f"    {sev:<5} {check:<26} {n}", file=out)


def main():
    ap = argparse.ArgumentParser(description="Lint TAPP CSVs against conventions.md.")
    default_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    ap.add_argument("--root", default=default_root, help="TAPP library root directory")
    ap.add_argument("--file", action="append", help="Lint specific file(s) instead of discovering")
    ap.add_argument("--all-versions", action="store_true", help="Include superseded versions")
    ap.add_argument("--severity", choices=["ERROR", "WARN", "INFO"], default="INFO",
                    help="Minimum severity to display (default: INFO)")
    ap.add_argument("--csv", help="Also write findings to this CSV path")
    ap.add_argument("--no-cross", action="store_true", help="Skip cross-TAPP checks")
    ap.add_argument("--no-collapse", action="store_true",
                    help="List every occurrence instead of folding repetitive checks")
    args = ap.parse_args()

    if args.file:
        paths = [p if os.path.isabs(p) else os.path.join(args.root, p) for p in args.file]
    else:
        paths = discover(args.root, args.all_versions)

    if not paths:
        print(f"No TAPP CSVs found under {args.root}", file=sys.stderr)
        return 2

    tapps, findings = [], []
    for p in paths:
        try:
            t = load(p)
        except Exception as e:  # noqa: BLE001 - surface parse failures as findings
            findings.append(Finding("ERROR", os.path.basename(p), "", "", "unreadable", str(e)))
            continue
        tapps.append(t)
        for check in (check_structure, check_tiers, check_modes, check_data_types,
                      check_analytical_mode_vocabulary,
                      check_naming, check_rules, check_keyed_by, check_dates):
            check(t, findings)

    if not args.no_cross and len(tapps) > 1:
        check_cross_tapp(tapps, findings)
        check_current_tapps(tapps, args.root, findings)
        check_module_versions(args.root, findings)
        check_library_freshness(args.root, findings)
        # Group 1's owner, newest first: Module_Core (since 2026-08-14, which also carries the
        # 10 universals from Groups 2-6 and so must be restricted to its Group 1 block), then
        # Module_Group1 (retired), then the pre-migration template.
        mod = os.path.join(args.root, "Claude Skills for TAPP", "modules")
        core_csv, core_json = (os.path.join(mod, "Module_Core.csv"),
                               os.path.join(mod, "Module_Core.json"))
        module_g1 = os.path.join(mod, "Module_Group1.csv")
        legacy_g1 = os.path.join(args.root, "Claude Skills for TAPP", "tapp_files",
                                 "Template TAPP Group 1.csv")
        restrict = None
        if os.path.exists(core_csv) and os.path.exists(core_json):
            g1_path = core_csv
            try:
                with open(core_json, encoding="utf-8") as fh:
                    blocks = json.load(fh).get("blocks", [])
                blk = next((b for b in blocks
                            if b.get("target_group", "").startswith("1.")), None)
                if blk:
                    restrict = set(blk["fields"])
            except (ValueError, OSError) as exc:
                findings.append(Finding("WARN", "(template)", "", "", "group1-template",
                                        f"Module_Core.json unreadable ({exc}); Group 1 block "
                                        f"could not be isolated."))
        elif os.path.exists(module_g1):
            g1_path = module_g1
        else:
            g1_path = legacy_g1
        check_group1_template(tapps, g1_path, findings, restrict)

    print(f"Linted {len(tapps)} TAPP file(s) under {args.root}")
    report(findings, args.severity, do_collapse=not args.no_collapse)

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["Severity", "TAPP", "Row", "Field", "Check", "Message"])
            w.writerows(f_.as_tuple() for f_ in sorted(
                findings, key=lambda x: (SEV_ORDER[x.severity], x.tapp, str(x.row))))
        print(f"\nFindings written to {args.csv}")

    return 1 if any(f.severity == "ERROR" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
