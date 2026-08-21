"""
Patch TAPP_Planning_Table.csv — 2026-05-16
Changes:
  1. LIT (#43): priority L → H
  2. AFM row (#52): rename from PCD-AFM to AFM (technique); include STHM-AFM as mode
  3. SEM row (#2): add deferred FIB-SEM discussion note
  4. VLM row (#39): add VLMBasemap investigation note
  5. Append new row for TDM (Temperature-Dependent Magnetization)
"""

import csv

INPUT = "TAPP_Planning_Table.csv"
OUTPUT = "TAPP_Planning_Table.csv"

with open(INPUT, newline="", encoding="utf-8-sig") as f:
    rows = list(csv.reader(f))

# Helper: find the first row whose column A starts with a given number string
def find_row(number_str):
    for i, r in enumerate(rows):
        if r and r[0].strip() == number_str:
            return i
    return None

# Column indices (0-based):
# 0=#, 1=Thematic Group, 2=Proposed TAPP Name, 3=Component Methods,
# 4=Property Type, 5=Data Format, 6=Relevant?, 7=Priority, 8=Notes, 9=Labs

# ── 1. LIT (#43): priority L → H ─────────────────────────────────────────────
i_lit = find_row("43")
assert i_lit is not None, "Row 43 (LIT) not found"
assert rows[i_lit][7].strip() == "L", f"Expected L, got {rows[i_lit][7]!r}"
rows[i_lit][7] = "H"
print(f"Row {i_lit}: LIT priority updated L → H")

# ── 2. AFM row (#52): rename and update scope ─────────────────────────────────
i_afm = find_row("52")
assert i_afm is not None, "Row 52 (AFM/PCD-AFM) not found"
rows[i_afm][2] = "Atomic Force Microscopy (AFM)"
rows[i_afm][3] = ("PCD-AFM (Particle Cohesion Determination); "
                  "SThM-AFM (Scanning Thermal Microscopy); "
                  "AFM (topography – standalone)")
rows[i_afm][4] = "Physical (surface adhesion/cohesion; nanoscale topography; local thermal properties)"
rows[i_afm][5] = "Tabular + Imagery"
rows[i_afm][8] = (
    "AFM is the technique; PCD-AFM and SThM-AFM are two methods (applications of AFM to acquire "
    "different data types). One TAPP with mode flags: Topography | Thermal (SThM) | Cohesion (PCD). "
    "SThM-AFM has 377 records in ADA (5th most common — likely Hayabusa2-specific); priority and "
    "scope to be revisited if JAXA data submissions continue."
)
print(f"Row {i_afm}: AFM row renamed and updated")

# ── 3. SEM row (#2): add FIB-SEM deferred note ───────────────────────────────
i_sem = find_row("2")
assert i_sem is not None, "Row 2 (SEM) not found"
existing_note = rows[i_sem][8]
rows[i_sem][8] = (
    existing_note.rstrip()
    + " DEFERRED: FIB-SEM ion-beam metadata scope (beam current, milling protocol, section geometry) "
    "to be reviewed during Phase 0 of SEM TAPP development — may require additional instrument-variant "
    "fields or a future standalone FIB-SEM TAPP. FIB-SEM has 177 records in ADA (8th most common)."
)
print(f"Row {i_sem}: SEM row updated with FIB-SEM deferred note")

# ── 4. VLM row (#39): add VLMBasemap investigation note ──────────────────────
i_vlm = find_row("39")
assert i_vlm is not None, "Row 39 (VLM) not found"
existing_vlm = rows[i_vlm][8]
rows[i_vlm][8] = (
    existing_vlm.rstrip()
    + " DEFERRED: 'VLMBasemap' appears as a separate ADA identifier (15 records). "
    "Examine ADA records before deciding whether this is a data sub-type of VLM or SLS, "
    "or a distinct technique requiring its own planning table row."
)
print(f"Row {i_vlm}: VLM row updated with VLMBasemap deferred note")

# ── 5. Append TDM row ─────────────────────────────────────────────────────────
tdm_row = [
    "TDM",                                    # # (non-integer placeholder)
    "Physical Properties",                    # Thematic Group
    "Temperature-Dependent Magnetization (TDM)",  # TAPP Name
    "TDM",                                    # Component Methods
    "Physical/magnetic (magnetization vs. temperature → magnetic mineral identification)",  # Property Type
    "Tabular",                                # Data Format
    "Marginal – physical/magnetic",           # Relevant to Astromat?
    "L",                                      # Priority
    (
        "Measures sample magnetization as a function of temperature to identify magnetic mineral "
        "phases (magnetite, pyrrhotite) via Curie/Néel temperature inflections. Used in meteoritics "
        "for magnetic mineralogy characterization. Identified from ADA stats (1 record); not previously "
        "in planning table. No TAPP developed. Low priority given minimal current ADA representation."
    ),                                        # Notes
    "",                                       # Labs
]
rows.append(tdm_row)
print(f"Appended TDM row at position {len(rows) - 1}")

# ── Write ─────────────────────────────────────────────────────────────────────
with open(OUTPUT, "w", newline="", encoding="utf-8-sig") as f:
    csv.writer(f).writerows(rows)

print("\nAll changes written to", OUTPUT)

# ── Verify ────────────────────────────────────────────────────────────────────
with open(OUTPUT, newline="", encoding="utf-8-sig") as f:
    verify = list(csv.reader(f))

print("\n--- Verification ---")
print(f"LIT priority:  {verify[i_lit][7]!r}")
print(f"AFM name:      {verify[i_afm][2]!r}")
print(f"SEM note tail: ...{verify[i_sem][8][-80:]!r}")
print(f"VLM note tail: ...{verify[i_vlm][8][-80:]!r}")
print(f"TDM row:       {verify[-1][:3]}")
