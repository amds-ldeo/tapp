"""
Patch: LA-Q:SF-ICPMS_TAPP_v2.csv → LA-Q:SF-ICPMS_TAPP_v3.csv

Changes applied
---------------
GROUP 3 — Instrument & Software
  ADD  Instrument Serial Number or Lab Identifier  (after ICP-MS Type)
  ADD  Torch Type                                  (after Torch Depth)
  ADD  Collision/Reaction Cell (CRC) Configuration (after Detector Configuration; Q-ICP-MS only)

GROUP 4 — Measurement Information
  MOD  Auxiliary and Cool Gas Flow Rates → split into:
         Coolant (Plasma) Gas Flow Rate  C=Basic  D=Editable  (replaces combined field)
         Auxiliary Gas Flow Rate         C=Basic  D=Editable  (inserted immediately after)
  MOD  RF Power: D=Read-Only → D=Editable
  REM  Drift Monitor Frequency removed from Group 4
         (data preserved; moved to Group 6 as Calibration Standard Measurement Frequency)
  ADD  Monitored Isotopes               (after Analyte; both instrument types)
  ADD  Mass Resolution per Analyte      (after Monitored Isotopes; SF-ICP-MS only)
  ADD  E-scan Range                     (after Mass Resolution per Analyte; SF-ICP-MS only)
  ADD  Triple Scanning Mode             (after E-scan Range; SF-ICP-MS only)
  ADD  Signal Collection Mode           (after Triple Scanning Mode; Q-ICP-MS only)
  ADD  Collision Gas Type               (after Signal Collection Mode; Q-ICP-MS only)
  ADD  Collision Gas Flow Rate          (after Collision Gas Type; Q-ICP-MS only)
  ADD  Cell Exit Discrimination Voltage (after Collision Gas Flow Rate; Q-ICP-MS only)
  ADD  Reaction Gas Type                (after Cell Exit Discrimination Voltage; Q-ICP-MS only)
  ADD  Reaction Gas Flow Rate           (after Reaction Gas Type; Q-ICP-MS only)
  REN  Spectrometer Dwell Time → Dwell Time per Mass

GROUP 5 — Data Processing
  ADD  Isotope Dilution Data Reduction Method  (after Interference Correction Method)

GROUP 6 — Quality Control & Uncertainty
  ADD  Calibration Standard Measurement Frequency  (after Primary Calibration Standard Name;
         content and lit-assessment data ported from the removed Drift Monitor Frequency row)
"""

import csv

TODAY = "2026-06-17"
SRC = "LA-Q:SF-ICPMS_TAPP_v2.csv"
DST = "LA-Q:SF-ICPMS_TAPP_v3.csv"


# ── helpers ──────────────────────────────────────────────────────────────────

def load(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.reader(f))


def save(rows, path):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerows(rows)


def find(rows, name):
    """Return index of first row whose column 0 equals name exactly."""
    for i, r in enumerate(rows):
        if r and r[0] == name:
            return i
    raise KeyError(f"Row not found: {name!r}")


def blank_row(ncols):
    return [""] * ncols


def new_field(name, desc, c_tier, d_tier, dtype, example, comments="",
              spot="Y", transect="Y", mapping="Y", ncols=25):
    """Build a new content row.  Literature-assessment columns (12-24) default to 'N'."""
    row = [name, desc, c_tier, d_tier, dtype, example, comments, TODAY,
           spot, transect, mapping, ""]          # col 11 = sentinel (empty)
    row += ["N"] * (ncols - len(row))
    assert len(row) == ncols
    return row


# ── load ─────────────────────────────────────────────────────────────────────

rows = load(SRC)
NCOLS = len(rows[0])   # 25


# ═══════════════════════════════════════════════════════════════════════════
# GROUP 3 — Instrument & Software
# ═══════════════════════════════════════════════════════════════════════════

# ── 3-A. Instrument Serial Number or Lab Identifier ──────────────────────
i = find(rows, "ICP-MS Type")
rows.insert(i + 1, new_field(
    "Instrument Serial Number or Lab Identifier",
    "Serial number or laboratory-internal identifier for the specific instrument unit. "
    "Supports traceability to instrument service records.",
    "Advanced", "Editable", "Text (free)",
    "e.g., 'Element XR S/N 1234' | 'Lab unit: Ghent-SF2'",
    "", "Y", "Y", "Y", NCOLS,
))

# ── 3-B. Torch Type ───────────────────────────────────────────────────────
i = find(rows, "Torch Depth")
rows.insert(i + 1, new_field(
    "Torch Type",
    "Type of plasma torch installed. Injector inner diameter (typically 1.5–2.5 mm) "
    "affects aerosol transport efficiency and plasma conditions in LA-ICP-MS.",
    "Advanced", "Read-Only", "Text (free)",
    "Standard quartz | High-matrix (low-flow) | Low-volume | N/A | None | Other: specify",
    "", "Y", "Y", "Y", NCOLS,
))

# ── 3-C. CRC Configuration ───────────────────────────────────────────────
i = find(rows, "Detector Configuration")
rows.insert(i + 1, new_field(
    "Collision/Reaction Cell (CRC) Configuration",
    "Whether a collision or reaction cell is installed and its operating mode. "
    "In standard mode (STD), no cell gas is introduced and the cell acts only as an "
    "ion guide. In kinetic energy discrimination (KED) mode, helium thermalizes ions "
    "so that polyatomic interferences (larger collision cross-section) are selectively "
    "retarded by a cell exit barrier voltage. In dynamic reaction cell (DRC) mode, a "
    "reactive gas selectively neutralizes specific interferences through ion-molecule "
    "reactions. On ICP-MS/MS instruments (e.g., Agilent 8900), a second mass filter "
    "preceding the cell enables precursor-ion selection. Specific gas types, flow rates, "
    "and cell voltages are documented in Group 4. Record 'Not applicable' for SF-ICP-MS "
    "instruments, which lack collision/reaction cells.",
    "Basic", "Read-Only", "Controlled list",
    "STD (standard mode, no gas) | KED (kinetic energy discrimination, He gas) | "
    "DRC (dynamic reaction cell, reactive gas) | "
    "ICP-MS/MS (triple-quadrupole mode) | Not applicable (SF-ICP-MS) | Other: specify",
    "Q-ICP-MS only", "Y", "Y", "Y", NCOLS,
))


# ═══════════════════════════════════════════════════════════════════════════
# GROUP 4 — Measurement Information
# ═══════════════════════════════════════════════════════════════════════════

# ── 4-A. Split "Auxiliary and Cool Gas Flow Rates" into two separate fields ──
i = find(rows, "Auxiliary and Cool Gas Flow Rates")
old_lit = rows[i][12:]   # preserve any existing literature-assessment data

# Replace the combined field with Coolant (Plasma) Gas Flow Rate
rows[i] = new_field(
    "Coolant (Plasma) Gas Flow Rate",
    "Flow rate of the outer (coolant/plasma) argon gas stream that sustains the ICP "
    "plasma, in L/min. Determines plasma volume and stability. Set during initial plasma "
    "optimisation and confirmed at each session start.",
    "Basic", "Editable", "Numeric (L/min)",
    "14 L/min | 15 L/min | Other: specify",
    "", "Y", "Y", "Y", NCOLS,
)
rows[i][12:] = old_lit   # carry forward any previously recorded values

# Insert Auxiliary Gas Flow Rate immediately after
rows.insert(i + 1, new_field(
    "Auxiliary Gas Flow Rate",
    "Flow rate of the intermediate (auxiliary) argon gas stream that positions the plasma "
    "relative to the load coil, in L/min. Affects ion extraction efficiency and oxide "
    "production rates. Distinct from the carrier gas (which transports ablation aerosol) "
    "and the coolant (plasma) gas.",
    "Basic", "Editable", "Numeric (L/min)",
    "0.8 L/min | 1.0 L/min | 1.2 L/min | Other: specify",
    "", "Y", "Y", "Y", NCOLS,
))

# ── 4-B. RF Power: D=Read-Only → D=Editable ──────────────────────────────
i = find(rows, "RF Power")
rows[i][3] = "Editable"
rows[i][7] = TODAY

# ── 4-C. Remove Drift Monitor Frequency (will be re-inserted in Group 6) ──
i = find(rows, "Drift Monitor Frequency")
drift_row = rows.pop(i)    # preserve the entire row (including lit-assessment data)

# ── 4-D. Insert new fields after Analyte ─────────────────────────────────
#
# Desired order after "Analyte":
#   Monitored Isotopes
#   Mass Resolution per Analyte     (SF-ICP-MS only)
#   E-scan Range                    (SF-ICP-MS only)
#   Triple Scanning Mode            (SF-ICP-MS only)
#   Signal Collection Mode          (Q-ICP-MS only)
#   Collision Gas Type              (Q-ICP-MS only)  ┐
#   Collision Gas Flow Rate         (Q-ICP-MS only)  │ CRC cluster
#   Cell Exit Discrimination Voltage(Q-ICP-MS only)  │
#   Reaction Gas Type               (Q-ICP-MS only)  │
#   Reaction Gas Flow Rate          (Q-ICP-MS only)  ┘
#   [existing: Spectrometer Dwell Time → renamed]

i = find(rows, "Analyte")

new_g4_fields = [
    new_field(
        "Monitored Isotopes",
        "Specific isotope(s) monitored per analyte element in this protocol, including "
        "any interference-monitor masses. Analyte-specific field.",
        "Basic", "Read-Only", "Text (free)",
        "⁷Li | ²⁵Mg | ⁵⁶Fe | ²⁰⁸Pb | N/A | None | Other: specify",
        "Analyte-Specific", "Y", "Y", "Y", NCOLS,
    ),
    new_field(
        "Mass Resolution per Analyte",
        "Mass resolution mode assigned to each analyte in this protocol. The selected "
        "resolution determines which polyatomic interferences are physically resolved by "
        "the magnetic sector. Per-analyte assignments are documented here; the overall "
        "mode(s) used in the protocol are recorded in Mass Resolution Setting (Group 3). "
        "Analyte-specific field.",
        "Basic", "Read-Only", "Text (free)",
        "LR: Ag, Cd, Sb, Tl, Bi; MR: Ga, Ge, Mo, In, Sn, W | "
        "All LR (m/Δm ≈ 300) | N/A | None | Other: specify",
        "SF-ICP-MS only; Analyte-Specific", "Y", "Y", "Y", NCOLS,
    ),
    new_field(
        "E-scan Range",
        "Electric scan range used for peak acquisition, expressed as percentage of the "
        "centre mass (%). Varies the accelerating voltage to cover masses in the vicinity "
        "of the set magnetic mass without re-scanning the magnet. Record 'N/A' if E-scan "
        "acquisition mode is not used.",
        "Advanced", "Read-Only", "Numeric (%)",
        "15% | 10% | N/A",
        "SF-ICP-MS only", "Y", "Y", "Y", NCOLS,
    ),
    new_field(
        "Triple Scanning Mode",
        "Whether each mass peak is scanned three times per cycle and the results averaged "
        "(Y/N). Used to reduce noise from short-term magnetic field instabilities on "
        "sector-field instruments. In LA-SF-ICP-MS, triple scanning affects the effective "
        "integration time per cycle and should be reported. Record 'N/A' if not applicable "
        "to the instrument.",
        "Advanced", "Read-Only", "Controlled list",
        "Y | N | N/A | None | Other: specify",
        "SF-ICP-MS only", "Y", "Y", "Y", NCOLS,
    ),
    new_field(
        "Signal Collection Mode",
        "Mode used to collect ion signal across the monitored masses. In peak hopping mode, "
        "the quadrupole jumps sequentially between pre-set mass positions and dwells at each "
        "peak; in scanning mode, the quadrupole sweeps continuously across a defined mass "
        "range. Peak hopping is standard for multi-element trace analysis as it maximises "
        "integration time at each mass.",
        "Basic", "Read-Only", "Controlled list",
        "Peak hopping | Scanning | N/A | None | Other: specify",
        "Q-ICP-MS only", "Y", "Y", "Y", NCOLS,
    ),
    new_field(
        "Collision Gas Type",
        "Type of collision gas introduced into the collision/reaction cell in KED mode. "
        "Helium (He) is the standard collision gas for kinetic energy discrimination due "
        "to its low mass and chemical inertness. Record 'None' if the CRC is in STD mode "
        "or not installed.",
        "Basic", "Read-Only", "Text (free)",
        "He (helium) | None | N/A | Other: specify",
        "Q-ICP-MS only", "Y", "Y", "Y", NCOLS,
    ),
    new_field(
        "Collision Gas Flow Rate",
        "Flow rate of the collision gas (typically He) introduced into the collision/reaction "
        "cell, in mL/min. Controls the degree of ion thermalization and KED efficiency. "
        "Record 'None' if the CRC is in STD mode.",
        "Basic", "Editable", "Numeric (mL/min)",
        "3.5 mL/min | 4.0 mL/min | None (STD mode)",
        "Q-ICP-MS only", "Y", "Y", "Y", NCOLS,
    ),
    new_field(
        "Cell Exit Discrimination Voltage",
        "Bias voltage applied at the collision/reaction cell exit to discriminate between "
        "analyte ions and low-energy polyatomic interferences in KED mode, in volts (V). "
        "A negative bias preferentially retards slow polyatomic ions while transmitting "
        "faster analyte ions. Record 'None' if the CRC is in STD mode.",
        "Basic", "Editable", "Numeric (V)",
        "−5 V | −8 V | None (STD mode)",
        "Q-ICP-MS only", "Y", "Y", "Y", NCOLS,
    ),
    new_field(
        "Reaction Gas Type",
        "Type of reactive gas introduced into the dynamic reaction cell (DRC) for "
        "interference removal through ion-molecule reactions. Common reaction gases include "
        "NH₃ (e.g., for Fe, Ca, K isotopes) and O₂ (e.g., for As, Ge). "
        "Record 'None' if DRC mode is not used.",
        "Advanced", "Read-Only", "Text (free)",
        "NH₃ | O₂ | CH₄ | None | N/A | Other: specify",
        "Q-ICP-MS only", "Y", "Y", "Y", NCOLS,
    ),
    new_field(
        "Reaction Gas Flow Rate",
        "Flow rate of the reactive gas introduced into the dynamic reaction cell (DRC), "
        "in mL/min.",
        "Advanced", "Editable", "Numeric (mL/min)",
        "0.4 mL/min | 0.8 mL/min | None",
        "Q-ICP-MS only", "Y", "Y", "Y", NCOLS,
    ),
]

for field in reversed(new_g4_fields):
    rows.insert(i + 1, field)

# ── 4-E. Rename Spectrometer Dwell Time → Dwell Time per Mass ────────────
i = find(rows, "Spectrometer Dwell Time")
rows[i][0] = "Dwell Time per Mass"
rows[i][7] = TODAY


# ═══════════════════════════════════════════════════════════════════════════
# GROUP 5 — Data Processing
# ═══════════════════════════════════════════════════════════════════════════

# ── 5-A. Isotope Dilution Data Reduction Method ───────────────────────────
i = find(rows, "Interference Correction Method")
rows.insert(i + 1, new_field(
    "Isotope Dilution Data Reduction Method",
    "Mass balance approach used to calculate sample mass fractions from spike-sample "
    "isotope ratio measurements in isotope dilution (ID) analysis. Record 'None' if "
    "isotope dilution is not used.",
    "Basic", "Read-Only", "Text (free)",
    "IUPAC isotope dilution equations | Double-spike inversion | None | N/A | "
    "Other: specify",
    "", "Y", "Y", "Y", NCOLS,
))


# ═══════════════════════════════════════════════════════════════════════════
# GROUP 6 — Quality Control & Uncertainty
# ═══════════════════════════════════════════════════════════════════════════

# ── 6-A. Calibration Standard Measurement Frequency ──────────────────────
#   Port content from the removed Drift Monitor Frequency row; replace name,
#   description, and tiers; preserve all literature-assessment column values.
i = find(rows, "Primary Calibration Standard Name")

cal_freq_row = new_field(
    "Calibration Standard Measurement Frequency",
    "How often the primary calibration standard is measured relative to unknown samples "
    "within a session. For LA-ICP-MS, this defines the bracketing interval between "
    "calibration standard ablations used to monitor and correct for instrumental drift.",
    "Basic", "Read-Only", "Text (free)",
    "Before and after every 5 unknowns | Bracketing every 10 samples | "
    "Start and end of session only | N/A | None | Other: specify",
    "", "Y", "Y", "Y", NCOLS,
)
cal_freq_row[12:] = drift_row[12:]   # carry over literature-assessment data

rows.insert(i + 1, cal_freq_row)


# ═══════════════════════════════════════════════════════════════════════════
# WRITE OUTPUT
# ═══════════════════════════════════════════════════════════════════════════

save(rows, DST)
print(f"Written: {DST}")
print(f"  Rows   : {len(rows)}")
print(f"  Columns: {len(rows[0])}")

# Sanity check: print field names only
print("\n--- Field list ---")
for i, r in enumerate(rows):
    if r:
        print(f"  {i:3d}: {r[0]}")
