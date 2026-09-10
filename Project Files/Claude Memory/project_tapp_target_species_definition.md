---
name: project-tapp-target-species-definition
description: "`target species` (called `analyte` until 2026-09-01) = the chemical species determined, at whatever resolution the chemistry is resolved; an isotope is NEVER one; settled and executed 2026-08-12"
metadata: 
  node_type: memory
  type: project
---

> **Renamed 2026-09-01 / 2026-09-07.** The field `Analyte` is **`Target Species`** and the key
> `analyte` is **`target species`**, renamed together across all 16 TAPPs at the schema developer's
> request — "analyte" reads as the physical thing put into the instrument, not the chemical species
> determined. `conventions.md` keeps "analyte" as the cited **IUPAC/ISO** term, and the VIM3 lineage
> row records that VIM3 §2.3 names it only to warn against using it *as* the measurand. **The
> definition below did not change — only its name.** Dated findings keep their original wording;
> the live guidance in "How to apply" has been updated.

**Status: EXECUTED 2026-08-12**, alongside [[project_tapp_session_sample_rule13]] — same decision record, `Claude Skills for TAPP/analysis/Decision_Record_2026-08-12_Session_Sample_and_Analyte.md` Part B. Normative text: `conventions.md` 7.2, 7.3.1, and the VIM3 vocabulary table. Reasoning: `precedents.md`, "`analyte` is the chemical species, never the isotope".

**The definition** (Rule 7.2's own wording, which was always right — eight field descriptions contradicting it were the defect):

> the chemical entity the procedure sets out to determine, **at whatever resolution the chemistry is resolved**.

**An isotope is NEVER an analyte — unconditionally.** No exception for nuclide-reporting techniques: ¹⁰Be cosmogenics has analyte **Be** (the separation chemistry, the ¹⁰B interference, the carrier and calibration are all elemental; `[¹⁰Be]` is the reported property), ¹⁴C dating has analyte **C**, ²¹⁰Pb has **Pb**. No case could be constructed where an isotope must be the analyte.

**Two boundary tests**, both already in the library. Against `channel`: would substituting a different isotope, line or address for the same entity leave the target of determination unchanged? Yes → `channel`. Against `reported property`: could the procedure ever report more than one quantity per analyte? Yes → `reported property` (the isomorphism precedent).

**Allowed content — the axis is chemical identity and is NOT ordered relative to the element:**

| Position | Example |
|---|---|
| finer than element | `Fe²⁺, Fe³⁺` (XANES, Mössbauer) |
| at element level | `Si, Fe, Rb, Sr` |
| a chemically defined fraction of an element | organic carbon (TOC) |
| orthogonal to elements | `n-C₂₉ alkane`; `C₁₈H₂₀O₈` |

**Never allowed**, because the distinction is not chemical: masses/acquisition addresses (→ `channel`); reported quantities (→ `reported property`); internal standards, interference monitors, carriers (→ `channel`); **the same species in a different environment** (→ `model component`). So **Fe²⁺ and Fe³⁺ are different analytes; Fe²⁺-on-M1 and Fe²⁺-on-M2 are not.** One granularity per TAPP, declared in Phase 0 under 7.7.

**Why:** isotopes of an element *are the same chemical species* — same separation chemistry, calibration standard, crystallographic site, chromatographic behaviour, elemental interferences. Isotopes are the **only** axis where measurement granularity is finer than chemical granularity, which is why that one case reads as an imposed grouping while valence and compounds feel natural. Two reasons disqualify the isotope domain: **7.4c** (every isotope-flavoured field in the library is scalar — nothing needs "one value per isotope shared across its channels"), and **technique-neutrality** (Fe is Fe by EPMA, ICP-MS, XRF or INAA; ⁵⁶Fe exists only inside a mass spectrometer, and a cross-technique registry needs the axis that survives a change of instrument).

**⚠ The obvious argument does NOT work — do not re-run it.** "Isotope-as-analyte merely duplicates `channel` or `reported property`" proves too much: element-as-analyte duplicates the reported-property list in *every* concentration-reporting procedure, and the field was kept anyway. Duplication was never the disqualifier. Nor is the isotope domain simply `channel` renamed — Misra et al. 2014 acquires ⁴³Ca in both LR and MR, so it is genuinely coarser than `channel` and finer than `analyte`.

**How to apply:**
- Filling in `Target Species` as a researcher: *would a chemist call these different substances?* ⁵⁶Fe vs ⁵⁷Fe — no. Fe²⁺ vs Fe³⁺ — yes. n-C₂₉ vs n-C₃₁ — yes.
- **Tell people to search by `reported property`, not `target species`.** [Fe] by LA-Q-ICP-MS and δ⁵⁶Fe by LA-MC-ICP-MS both carry `Target Species = Fe`. A sentence claiming `Analyte` "enables matching of procedures to analytical needs" was added and then removed for exactly this reason. **The field exists because the key exists** — 57 rows declare `Keyed By = target species` (count 2026-09-08) and become uninterpretable without a definer (7.4a). If procedure discovery is a real requirement, the fix is a **controlled vocabulary on `Reported Variables and Units`** (currently `Text (free)`), not leaning on `Analyte`.
- Worked case, Rb–Sr reporting isotope concentrations, isotope ratios, elemental concentrations and elemental ratios: `Target Species` = **Rb, Sr**. Two entries. All four output kinds are reported properties.
- Metrology mapping now in `conventions.md`: **analyte = what is analysed; measurand = which quantity of it is obtained**, and TAPP's `reported property` *is* the measurand (VIM3 §2.3).

**Three merge proposals rejected, all reaching for `channel` under another name:** `monitored species` (collapses into `channel` and evicts interference monitors and internal standards, which are monitored and never determined); a generalised `analyte` covering physical-property sweeps (Lab-XCT is 92% scalar — those techniques have no determinand layer, because determinand and reported property coincide); `Target Elements` (cannot hold a molecule, a valence species or a nuclide).

**What changed in the library:** all 13 `Analyte` descriptions reframed around one shared opening sentence, with the isotope clause added only in the nine mass-spectrometric TAPPs; `channel` minted in EPMA/SEM/SEM_Composition on multi-spectrometer evidence (Jia et al. 2022 measures Cr on two spectrometers with aggregate intensity counting) — `WDS Spectrometer Channel` is now `defines: channel per analyte`; `Mass Resolution per Analyte` → **`Mass Resolution Assignment`**, keyed `channel` (Misra's ⁴³Ca).

**Still open:** XRD phase identity has a claim from `analyte`, `model component` and `reported property` at once; orientation as an axis (AMS, velocity anisotropy) fits neither `channel` nor `sampling unit`; and the matrix-element grey zone — an element fully calibrated but never reported.

See [[project_tapp_session_sample_rule13]], [[project_tapp_keyed_by_rule7]], [[project_tapp_colB_colI_survey]].
