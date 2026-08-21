#!/usr/bin/env python3
"""
Three changes falling out of the TQ-ICP-MS literature verification (Wu 2023, Gil-Diaz 2020,
Lopez Garcia 2026, in LA-Q-ICP-MS/TQ literature assessment/).

1. RENAME  `Monitored Isotopes` -> `Monitored Masses`  (8 TAPPs)
   The field is the `defines: channel` definer, and the channel domain demonstrably contains
   non-isotopic species: Wu et al. 2023 assign dwell times to reaction products, "(176+82)Hf
   (300 ms)", and Gil-Diaz et al. 2020 measure "125Te+16O -> 141TeO" and "77Se+16O -> 93SeO".
   A field named "Isotopes" that must enumerate molecular ions invites a curator to prune them,
   which would leave the channel domain incomplete and break Rule 7.4a for every field keyed by
   `channel` (`Dwell Time per Mass`, `Interference Correction Method`).
   `Monitored Masses` chosen over `Monitored Species` because conventions.md defines Analyte as
   "the chemical species a measurement is performed on" — reusing "species" for the channel side
   would blur the analyte/channel line the 2026-08-12 decision record settled. It also pairs with
   the existing channel-keyed `Dwell Time per Mass`.
   Column I divergence is PRESERVED: `analyte` in the two LA-MC TAPPs (where the cup array defines
   the channel), `defines: channel per analyte` in the other six. That divergence is registered in
   KEYED_BY_TECHNIQUE_DEPENDENT and is not what this change is about.

2. ADD  `Reaction Product Ion / Mass-Shift Transition`  (3 Q TAPPs), keyed `channel`
   The one genuine residue of the TQ residue test. No existing field records precursor + reagent ->
   product: `Monitored Masses` records the mass measured, not the chemistry that produced it, and
   without that a consumer cannot tell which analyte a shifted mass reports.
   Added only to LA-Q, LA-Q_UPb and Solution Q — the TAPPs with attested instances. Not provisioned
   into the MC or SF TAPPs (Rule 6.10: do not create from no instance).

3. RE-KEY  `Collision/Reaction Cell (CRC) Configuration`  `(none)` -> `channel`  (6 TAPPs)
   Gil-Diaz et al. 2020 use two cell modes for two isotopes of the SAME element in one study —
   "126Te measured in KED-mode (He)" and "125Te ... in mass-shift O2-mode". A scalar Controlled list
   cannot express that. Rule 7.11 G3: declare the finest key unconditionally, since "a consumer
   given `(none)` cannot hold per-channel values at all"; Rule 7.12: the key is the finest axis
   attested in reported data. Rule 7.4a holds in all six — the Q TAPPs define `channel` via
   `Monitored Masses`, the MC TAPPs via `Collector Configuration`.

Literature cells for the new field are `N` throughout, NOT `N/A`. Deriving "no mass shift" from a
stated STD or KED value would be exactly the step the Inference Rule forbids: "If a value is
logically implied by other stated values but not written explicitly, record N."
"""
import csv, os, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
APPLY = "--apply" in sys.argv
DATE = "2026-08-17"

OLD, NEW = "Monitored Isotopes", "Monitored Masses"
CRC = "Collision/Reaction Cell (CRC) Configuration"
RPI = "Reaction Product Ion / Mass-Shift Transition"

NEW_B = ("Specific masses monitored in this procedure, grouped by the analyte element they serve "
         "where they serve one. Covers atomic isotopes and, where a reaction cell shifts an analyte "
         "onto a different mass, the product mass actually measured. Includes interference-monitor "
         "and internal-standard masses, which serve no analyte and so have no parent element. The "
         "analyte list is given by the Analyte field and is never inferred from the element symbols "
         "appearing here.")

RPI_B = ("For each monitored mass produced by a reaction in the collision/reaction cell, the precursor "
         "ion, the reagent gas and the product ion measured. Records the mass-shift chemistry relating "
         "the mass measured to the analyte it reports, which the monitored mass alone does not state. "
         "Record 'N/A' where the analyte is measured on its own mass.")

RPI_F = {
 "LA-Q-ICP-MS":       "e.g., '176Hf + NH3 -> (176+82)Hf+ (adduct, +82 u)' | 'N/A (on-mass measurement)'",
 "LA-Q-ICP-MS_UPb":   "e.g., '176Hf + NH3 -> (176+82)Hf+ (adduct, +82 u)' | 'N/A (on-mass measurement)'",
 "Solution_Q-ICP-MS": "e.g., '125Te + 16O -> 141TeO+' | '77Se + 16O -> 93SeO+' | 'N/A (on-mass measurement)'",
}
# product-ion example appended to Monitored Masses Column F in the reaction-cell TAPPs
MM_F_EXTRA = {
 "LA-Q-ICP-MS":       " | (176+82)Hf (NH3 mass-shift product)",
 "LA-Q-ICP-MS_UPb":   " | (176+82)Hf (NH3 mass-shift product)",
 "Solution_Q-ICP-MS": " | 141TeO (O2 mass-shift product of 125Te)",
}

JOBS = [  # src, dst, key, {rename, add_rpi, rekey_crc}
 ("LA-Q-ICP-MS/LA-Q-ICP-MS_TAPP_v21.csv",              "LA-Q-ICP-MS/LA-Q-ICP-MS_TAPP_v22.csv",              "LA-Q-ICP-MS",       (1,1,1)),
 ("LA-Q-ICP-MS/LA-Q-ICP-MS_UPb_TAPP_v22.csv",          "LA-Q-ICP-MS/LA-Q-ICP-MS_UPb_TAPP_v23.csv",          "LA-Q-ICP-MS_UPb",   (1,1,1)),
 ("Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v25.csv",  "Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v26.csv",  "Solution_Q-ICP-MS", (1,1,1)),
 ("LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v19.csv",             "LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v20.csv",             "LA-MC-ICPMS",       (1,0,1)),
 ("LA-MC-ICP-MS/LA-MC-ICPMS_UPb_TAPP_v19.csv",         "LA-MC-ICP-MS/LA-MC-ICPMS_UPb_TAPP_v20.csv",         "LA-MC-ICPMS_UPb",   (1,0,1)),
 ("Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v23.csv","Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v24.csv","Solution_MC-ICP-MS",(0,0,1)),
 ("LA-SF-ICP-MS/LA-SF-ICP-MS_TAPP_v21.csv",            "LA-SF-ICP-MS/LA-SF-ICP-MS_TAPP_v22.csv",            "LA-SF-ICP-MS",      (1,0,0)),
 ("LA-SF-ICP-MS/LA-SF-ICP-MS_UPb_TAPP_v22.csv",        "LA-SF-ICP-MS/LA-SF-ICP-MS_UPb_TAPP_v23.csv",        "LA-SF-ICP-MS_UPb",  (1,0,0)),
 ("Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v25.csv","Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v26.csv","Solution_SF-ICP-MS",(1,0,0)),
]

for src, dst, key, (do_ren, do_add, do_key) in JOBS:
    p = os.path.join(ROOT, src)
    rows = list(csv.reader(open(p, encoding='utf-8-sig')))
    hdr = rows[0]
    ncol = len(hdr)
    si = hdr.index('Literature Assessment') if 'Literature Assessment' in hdr else ncol
    acts = []

    if do_ren:
        hit = [r for r in rows[1:] if r and r[0] == OLD]
        assert len(hit) == 1, f"{key}: {len(hit)} rows named {OLD}"
        r = hit[0]
        r[0], r[1], r[7] = NEW, NEW_B, DATE
        if key in MM_F_EXTRA and MM_F_EXTRA[key] not in r[5]:
            r[5] = r[5].replace(" | N/A | None | Other: specify", MM_F_EXTRA[key] + " | N/A | None | Other: specify")
        acts.append(f"renamed (key kept: {r[8]})")

    if do_key:
        hit = [r for r in rows[1:] if r and r[0] == CRC]
        assert len(hit) == 1, f"{key}: CRC row not found"
        r = hit[0]
        assert r[8] == '(none)', f"{key}: CRC key already {r[8]}"
        r[8], r[7] = 'channel', DATE
        acts.append("CRC re-keyed -> channel")

    if do_add:
        anchor = max(i for i, r in enumerate(rows) if r and r[0] == "Reaction Gas Flow Rate")
        new = [RPI, RPI_B, "Advanced", "Read-Only", "Text (free)", RPI_F[key], "", DATE, "channel"]
        new += [""] * (ncol - len(new))
        for k in range(si + 1, ncol):
            new[k] = "N"
        rows.insert(anchor + 1, new)
        acts.append(f"added {RPI} after row {anchor}")

    assert all(len(r) == ncol for r in rows), f"{key}: ragged"
    print(f"{'WROTE' if APPLY else 'DRY '} {os.path.basename(dst):36} " + "; ".join(acts))
    if APPLY:
        with open(os.path.join(ROOT, dst), "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerows(rows)

if not APPLY:
    print("\ndry run — rerun with --apply")
