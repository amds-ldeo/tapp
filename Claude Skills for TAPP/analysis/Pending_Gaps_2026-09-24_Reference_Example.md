# Pending: six structural gaps exposed by the EPMA reference example (2026-09-24)

**Status (2026-09-29): gaps 1, 3, 4, 5 and 6 implemented; gap 2 held. The follow-on literature passes are complete for EPMA and the four SEM TAPPs.**

| Gap | Status |
|---|---|
| 5 | **Fixed** 2026-09-28. Module_Core v9 re-keys `Sample Preparation Method` to `sample`; the projection rule is now conventions 7.3.3. Script: `Project Files/Scripts/gaps5and6_sample_prep_key_20260928.py`; see also `precedents.md`, 2026-09-28. |
| 6 | **Fixed** 2026-09-28, in the same pass: `Monitored Elements` gains one sentence. |
| 1 | **Implemented** 2026-09-28. EPMA: Module_Core v10, EPMA v79; a point/map split was added after checking the key against the mapping procedures. SEM: SEM v79, SEM_Composition v78, SEM_Imaging v41, SEM_FIBSEM v42, on their own evidence (below). TEM: no change; it has none of the fields. Scripts: `Project Files/Scripts/gap1_target_material_20260928.py`, `gap1_sem_target_material_20260928.py`. |
| 3 | **Implemented** 2026-09-28: Module_Aggregation v5, Geochronology v8, UPb v9; 13 TAPPs. The per-TAPP grouping key was withdrawn on the evidence in favour of a session list, `Combined Results`. Script: `Project Files/Scripts/gap3_combined_results_20260928.py`. |
| 4 | **Implemented** 2026-09-28 in EPMA v80, SEM v77 and SEM_Composition v76, not EPMA alone: the SEM TAPPs carried the same field as `Technique per Target Species`. The conditional-applicability half is deferred. Script: `Project Files/Scripts/gap4_detection_method_20260928.py`. |
| 2 | **Held** until attested. |

**Follow-on literature passes (tasks 2 and 3 of the 2026-09-28 plan).** Each is done paper by paper, together
with the keyed-notation conversion (conventions 7.3.4), because converting a cell means re-reading its source.

| TAPP(s) | Status |
|---|---|
| EPMA | **Complete** at v86 (2026-09-29). Every field is assessed except `Laboratory ID` and `Procedure Start Date`, which are blank by decision (0 of 12 papers). Scripts: `epma_roundtrip_fixes_20260929.py`, `epma_remaining_fields_20260929.py`; round-trip 95%. |
| SEM, SEM_Composition, SEM_Imaging, SEM_FIBSEM | **Complete** 2026-09-29 (SEM v83, SEM_Composition v81, SEM_Imaging v43, SEM_FIBSEM v44): 840 cells, every never-assessed field; only `Session Identifier` is blank, by decision. The cells are not yet in the keyed notation beyond the new ones, and SEM is not in `KEYED_NOTATION_ENFORCED`. Scripts: `sem_never_assessed_fields_20260929.py`; three phantom Barnes+2025 columns then removed by `sem_remove_phantom_barnes_20260929.py`. |
| The other Module_Aggregation TAPPs | Not started: `Combination Method`, `Combined Results`, `Other Statistics`. |

**Where the gaps came from.** Writing `Project Files/Reports/EPMA_Reference_Procedure_Example_v77.md` required filling all 88 fields of EPMA TAPP v77. That exposed six places where complete documentation needs structure the TAPP does not declare. Appendix B of the example states them briefly.

This note records what each gap is, the design agreed for it, the evidence behind the design, what the design touches, and the implementation order. Proposals that were considered and replaced are kept in short "Replaced proposal" notes, so the reasoning is not lost.

## Level dependence: one mechanism, not two

On 2026-09-24 gaps 1 and 5 looked like two different problems.

- **Projection (gap 5).** One key, read at two levels.
- **Substitution (gap 1).** A procedure-level key that differs from the session key.

The substitution case turned out not to exist. Once `target material` is a list (gap 1 below), the key the literature attests for beam conditions is `target material` at **both** levels. So projection, conventions 7.3.3, is the only mechanism needed. No field needs a second key column or an override notation.

**Projection (conventions 7.3.3).** Column I states the session-level key. At procedure level, drop every domain whose definer is C=N/A: today, `sample` and `sampling unit`. Seven EPMA fields depended on this before it was written down, and the review-workbook generator (`phrase()` in `Project Files/Reports/make_review_workbook.py`) had already implemented it.

## The gaps

### Gap 1 — beam conditions vary by phase — IMPLEMENTED 2026-09-28 (EPMA, then the SEM TAPPs)

**The problem.** The five beam fields are keyed `sample > sampling unit`:

- Beam Mode
- Beam Current
- Beam Diameter
- Beam Raster Dimensions
- Beam Damage Minimization

Under projection, that key gives one value per procedure. Published procedures state these values per phase.

**What the literature attests.** Across the 15 EPMA procedures, every stated beam condition is either one value for the whole procedure or one value per phase or material. None is stated per analysis point. So the finest attested key (Rule 7.3.2, 7.12) is per material, not `sample > sampling unit`. The 2026-09-08 acquisition-pass precedent chose `sample > sampling unit` for mineral-dependent conditions because no per-material list existed then.

**Agreed design.**

1. **`Target Material` becomes the definer of a new key, `target material`.** It is C=Basic and already required in every TAPP. Its allowed values are open (`Controlled list / Text`), so a procedure may name a finer entry where its conditions need one.
2. **The five beam fields are re-keyed to `target material`.** The procedure registers the conditions for each target material. The session records the conditions it used for each target material (D=Editable, within the procedure's bounds). One key serves both levels.
3. **A new session field, *Target Material of Sampling Unit*,** records which listed target material each analysis point belongs to. It is keyed `sample > sampling unit`, C=N/A, D=Basic. It is the link from a point to its conditions, and it fills the "Phase" column that the reference example's Table 10 needed and no field held.
4. **Rule 7.4c exemption for `Target Material`.** Target Material belongs to Module_Core, so it would become a definer in all 16 TAPPs, but only the electron-beam TAPPs will have consumers. Exempt it from 7.4c on the Rule 8/9 ground: the field is informative in its own right, because it states the procedure's scope for discovery.
5. **`Counting Statistics Error` is unchanged.** It varies point by point, so `sample > sampling unit x reported property` stays.

**Grain check against Target Material's categories.** The categories are Silicate mineral, Silicate glass, Oxide, Sulfide, Carbonate, Phosphate, and Metal or alloy. Six of the seven procedures that state per-phase beam conditions fit them:

- **Liu 2016** fits because glass is its own category: 20 nA for silicate minerals and oxides; 10 nA for maskelynite (glass), phosphate and sulfide.
- **Zega 2025**, **McCoy 2025**, **Barnes 2025**, **Seifert 2026** and **Neuman 2025** also fit.
- **Pang 2016 does not fit.** It defocuses the beam for plagioclase and keeps it focused for olivine and pyroxene, which splits "Silicate mineral". The open list covers this: the procedure names a "Plagioclase" entry. The cost is some loss of Target Material's role as discovery vocabulary.

**Amended before implementation: point and map fields are split (2026-09-28).** Checking the key against the three mapping procedures found Liu+2016 running olivine at 20 nA for points and at 200 nA for the olivine megacryst maps. One value per material cannot hold both. Neuman+2025 maps all phases at a single 100 nA. So:
- the five beam fields are point-analysis fields (mode flags YNYN), keyed `target material`;
- new mapping twins — `Mapping Beam Mode`, `Mapping Beam Current` and `Mapping Beam Diameter` — are flagged NYNY and keyed per map (`sample > sampling unit`), following the `Peak Counting Time` / `Dwell Time per Pixel` pattern.

**What is given up.** A session that changes the conditions for a single grain cannot record that per point; it goes in Additional Notes.

**Falsifier.** A procedure that reports beam conditions per analysis point.

**Scope.** EPMA first. SEM and TEM follow after their literature columns are checked for per-phase beam conditions.

**SEM and TEM, done 2026-09-28.**
- **TEM: no change.** It carries none of the five fields. Its own beam fields are `(none)`, and none
  of its 21 columns states a condition per phase.
- **SEM: the columns could not decide it.** Mode, Diameter, Raster and Damage were never assessed
  (blank in all 35 SEM and 9 SEM_Composition columns). Beam Current is one value per column. The
  source papers settled it:
  - no procedure states a condition per point;
  - one states a condition per material (Ferus+2020, a 5 µm beam for glass and feldspar);
  - three run points and maps differently (Barnes+2025 Hokkaido, ~1 nA points and ~2 nA maps;
    Ferus+2020; Pascucci+2026, by aperture);
  - imaging current follows the image, not the material (Garvie+2008).
- **As built.**
  - **SEM and SEM_Composition** match EPMA.
  - **SEM's `Beam Current`** keeps the point modes, including CL Point. `Mapping Beam Current`, keyed
    per map or image, covers every mode that scans: X-ray and CL maps, EBSD, SE and BSE images, and
    FIB-SEM work.
  - **Rule 4 propagation.** SEM_Imaging splits its `Beam Current` the same way and gains the link
    field. SEM_FIBSEM renames its `Beam Current` to `Mapping Beam Current`.
- **Literature.** The never-assessed fields, the mapping twins and the link field are blank in all four
  SEM TAPPs, and are assessed with the `Target Material of Sampling Unit` pass.

See `precedents.md`, "The SEM TAPPs follow EPMA" (2026-09-28).

**Held.** Counting times per phase, `target material x monitored property`, are attested only by Zega+2025 (1 of 15). Revisit when a second procedure attests them.

**Replaced proposals.**

- **A new `phase group` domain with a "Phase Groups" field, plus a procedure-level key override (2026-09-24).** Replaced once the attested grain was seen to be per material. The override notation it required became unnecessary.
- **"Key everything sample-keyed to `target material`" (discussed 2026-09-28).** Rejected, for three reasons:
  - Samples in microbeam work contain several materials (EX-CC-01 has five), so `Sample Name` cannot sit under one target material.
  - Preparation varies by sample, not by material: Seifert's two mounts are the same material, and only one was ion-polished.
  - Projection already makes `sample` a session-only key.

### Gap 3 — statistics on averaged values — IMPLEMENTED 2026-09-28

**Amended before implementation: a session list instead of a key for each TAPP.** Reading the inclusion cells showed combined values at different levels within one TAPP:

- **EPMA:** per phase (Liu 2016, Pang 2016, Broussard 2026) and per grain (Ma 2017).
- **LA-Q-ICP-MS:** per grain (Nakanishi 2022), per aliquot (Liu 2024), per phase (Liu 2016) and per sample (Wu 2023).

As built:

- **New session list:** `Combined Results` (`defines: combined result`, C=N/A). Each entry names one combined value.
- **Inclusion rules** keyed `combined result`. The procedure states the rules once, under 7.3.3.
- **Dispersion statistic and Other Statistics** keyed `combined result x reported property`.
- **Combination Method** as agreed.
- **Stays in Module_Aggregation.** No Rule 6.4 exception was needed, and there are no per-TAPP keys.

The table below records the design as first agreed.

**The problem.** Two fields describe averaged or otherwise combined values:

- `Goodness-of-Fit or Dispersion Statistic`, keyed by `reported property` alone;
- `Analysis Inclusion and Rejection Criteria`, keyed `(none)`.

A session that reports two means of the same variable, such as FeO in olivine and FeO in pyroxene, needs two statistics, but the key can hold only one. In addition, **no field outside geochronology records whether a reported variable is a single result or a combination of several.** Geochronology alone has `Age Model`, "the statistical model used to combine individual analyses into a single reported age". In EPMA the worked example could say "mean compositions are reported for each phase in each sample" only in prose.

**Two different things.** A reported variable is the *kind* of quantity, and the procedure declares it once. A weighted-mean date or an isochron age is a reported variable. The *instance*, such as "the weighted-mean date of sample X" or "the olivine mean in EX-CC-01", names a sample, so it exists only in the session. Reported variables can say *whether* and *how* a value is combined. They cannot say *which instance*, because they are sample-neutral.

**Agreed design.**

| Field | Keyed by | Tiers | Note |
|---|---|---|---|
| **Combination Method** (new; generalises `Age Model`) | `reported property` | C=Basic where any value is combined | For each reported variable: whether it is combined, how (arithmetic mean, weighted mean, isochron regression, …), and over what group (per grain, per phase within a sample, per sample). `Age Model` moves out of Module_Geochronology into Module_Aggregation as this field, so the geochronology TAPPs receive it from there. |
| **Analysis Inclusion and Rejection Criteria** (existing) | each TAPP's own grouping; EPMA `sample x target material` | unchanged, C=Basic D=Basic | Under projection the procedure states the rules once, and the session gives the outcome per group. The field is not split. |
| **Goodness-of-Fit or Dispersion Statistic** (existing) | each TAPP's grouping `x reported property`; EPMA `sample x target material x reported property` | unchanged, C=N/A D=Basic | The one required statistic. |
| **Other Statistics** (new) | same as the dispersion statistic | C=N/A D=Advanced | Anything further the author reports, with the statistic named. Covers the wide range of statistics without trying to classify them. |

**Keys differ by technique, so each TAPP declares its own.** Module_Aggregation stops owning Column I for its fields and keeps the names, descriptions and tiers. Each consuming TAPP declares its grouping, and the divergence is registered through the existing `keyed-by-divergence-registered` mechanism.

| Technique | A combined value is taken over | Grouping key |
|---|---|---|
| EPMA | a phase within a sample | `sample x target material` (needs gap 1) |
| U-Pb | a sample (Wu 2023: 236 of 246 spots) | `sample` |
| Grain averages | one grain (Nakanishi 2022: 1–3 spots) | `sample > sampling unit` |
| Two data treatments of one sample | each treatment is its own reported variable (Zhang 2022: Normal and SUIA isochrons) | `sample` |

**Evidence.** The 2026-09-16 precedent in `precedents.md` ("`Analysis Inclusion and Rejection Criteria` keeps `(none)`") found that combined values sit at three levels:

- per unit (Nakanishi 2022);
- per phase (Liu 2016: n = 7 and n = 13 per phase);
- per sample (Wu 2023).

It kept `(none)` as "least-wrong" because no single key fits all three. Letting each TAPP declare its own grouping resolves that without a new, unfamiliar term.

**Wording.** No field name or description uses "aggregate". Descriptions say "averaged or otherwise combined". The existing descriptions of both Aggregation fields say "reported aggregate value" and must be reworded.

**Cost.** Module_Aggregation (13 consumers) and Module_Geochronology. `Age Model` is known to the schema consumer, so its move needs a note to them. Consumer Column I values are set per TAPP. Rule 6.4's column-ownership text must allow a module that does not own Column I.

**Order dependency.** EPMA's grouping key uses `target material`, so gap 1 must be implemented first.

**Replaced proposals.**

- **A new `aggregate` domain with a "Reported Aggregates" definer (2026-09-24 and 2026-09-28).** Replaced for two reasons. "Aggregate" is not geochemists' vocabulary. And it conflated the kind of reported variable with its instance, which the existing lists (`sample`, `target material`, `sampling unit`) already identify per technique.
- **Splitting the inclusion field into criteria and outcome (2026-09-24).** Replaced once projection was written down: one field states the rules at procedure level and the outcome per group at session level.

### Gap 4 — WDS or EDS chosen element by element — IMPLEMENTED 2026-09-28 (re-key)

**The problem.** In a combined WDS+EDS point analysis, the WDS-only per-element fields do not apply to the EDS-measured elements:

- Diffracting Crystal
- WDS Spectrometer Channel
- Proportional Counter / Detector
- WDS PHA Setting
- the counting times

Mode flags work per mode. Here the choice of detector is made per element.

**Why the problem arises.** EPMA's four modes combine two axes:

- **Detector: WDS or EDS.** In a combined analysis this is chosen per element.
- **Geometry: point or mapping.** This is chosen for the whole acquisition.

`Analytical Mode` stays per procedure. It declares which modes the procedure covers, and the mode flags switch whole groups of fields.

**What "EPMA Technique" means.** It is the X-ray detection method used to measure an element.

- **WDS (wavelength-dispersive).** A crystal spectrometer separates X-rays by wavelength through Bragg diffraction, and a proportional counter counts them.
- **EDS (energy-dispersive).** A solid-state detector sorts every photon by energy at the same time.

The Group 1 `Technique` field (`EPMA-WDS | EPMA-EDS | EPMA-WDS+EDS`) should equal the combination of the per-element values.

**Agreed design.** Re-key `EPMA Technique per Target Species` from `target species` to `monitored property`, and rename it **X-ray Detection Method per Monitored Element**. There are three reasons:

- The field then sits at the grain of the fields it gates.
- The name no longer collides with the Group 1 `Technique` field.
- It can record the method for elements monitored only to correct an interference. Zn in the reference example serves no target species, so a per-target-species field has nowhere to record its method.

The field is TAPP-owned. **Correction:** this record first said EPMA only, but SEM and SEM_Composition carry the same field as `Technique per Target Species`. All three were changed together, as Rules 2 and 4 require. Both old names are in `RETIRED_FIELDS`, and the schema spec carries a migration note.

**Deferred.** A general conditional-applicability mechanism, such as an "Applies When" column holding `X-ray Detection Method = WDS`. 47 fields state a condition in Column B prose today, among them Coupling Description in all 16 TAPPs and Beam Raster Dimensions ("when Beam Mode = Rastered"). The mechanism is not needed for this re-key. Weigh it against the 7.3.2 reasoning that extra grammar has a cost for every downstream consumer.

**Replaced proposal.** Keying `Analytical Mode` by monitored element (raised 2026-09-28) was rejected. Mode is a per-procedure declaration; only the detector axis varies per element.

**Larger alternative, not pursued.** Split EPMA's mode columns into geometry × detector. That would revisit the Phase 0 mode decision.

**Evidence for it, 2026-09-29.** The EPMA cells round-trip (`Project Files/Reports/EPMA_Cells_RoundTrip_2026-09-29/`)
found that 9 of 15 EPMA papers state their geometry (point analyses, maps) without naming WDS or EDS.
`Analytical Mode`'s closed list pairs the two, so those procedures get `N`, and 14 stated facts
survive only as commentary. This is the largest single residue of the round-trip. **Held by the
user on 2026-09-29.** The split stays the deferred alternative; revisit it with the other electron-beam
TAPPs, or if another round-trip shows the same residue.

### Gap 2 — per-element values can differ between modes — HELD

**The problem.** In the example, the same element uses a two-point off-peak background for points and a MAN background for maps, and a different spectrometer for maps than for points.

**Status: held (confirmed 2026-09-28).** None of the 15 EPMA procedures attests this. Neuman+2025 maps only, with MAN; Zega+2025 runs points only, with off-peak backgrounds. The example invented the case.

**If attested.** Follow the `Peak Counting Time` / `Dwell Time per Pixel` pattern: mode-flagged twin fields for `X-ray Background Correction Method` and `WDS Spectrometer Channel`. A `mode` key is forbidden by Rule 7.2.

**Falsifier.** One procedure reporting both points and maps with a different background method or spectrometer assignment for the same element.

**Checked again 2026-09-29, in the EPMA keyed-notation pilot, which re-read all 12 EPMA papers.** Not
found. Four procedures report both points and maps: Liu+2016, Zega+2025, Broussard+2026 and
Neuman+2025, where Neuman maps only. None states a background method or a spectrometer assignment for
its maps that differs from its points. Only Neuman+2025 names a map background (MAN). Broussard+2026
says only that "a similar calibration was used for quantitative EPMA stage mapping".

### Gap 5 — preparation can differ by sample — FIXED 2026-09-28

`Sample Preparation Method` is re-keyed `(none)` → `sample` in Module_Core v9, and its tiers are unchanged (C=Basic, D=Editable). Rule 13 already required this. The literature attestation is 1 of 128 cells (Seifert+2026, "one mount ion-polished before carbon coating"). Its procedure-level shape is unchanged under projection.

**Still open.** Should the same test — can this differ between samples in one session? — be applied to the other `(none)` fields in Group 2? `Sampling Unit Selection Criteria` is the obvious candidate.

### Gap 6 — target species with no monitored element — FIXED 2026-09-28

`Monitored Elements` (EPMA, SEM, SEM_Composition) now says: "A target species determined by stoichiometry or by difference, rather than measured, has no monitored element."

## Implementation order

| Order | Gap | Why here |
|---|---|---|
| done | 5, 6 and projection (7.3.3) | Already decided by Rule 13. |
| done | Gap 1, EPMA | Created the `target material` key that gap 3 needs. |
| done | Gap 4 | EPMA, SEM and SEM_Composition; TAPP-owned. |
| done | Gap 3 | Three modules, 13 TAPPs. |
| done | Gap 1, SEM and TEM | SEM TAPPs changed on paper evidence; TEM unchanged. |
| — | Gap 2 | Held until attested. |

Every change follows the usual gates:

- run `check_field_ownership.py` before editing;
- edit modules and recompose, never a TAPP's module-owned columns directly;
- run `compose_tapp.py --check` before and after;
- run `validate_tapp.py` at 0 ERROR / 0 WARN;
- where Column I changes, run `audit_keys_vs_literature.py`;
- bump the version, park the superseded files and fill the superseded README;
- sync `Current TAPPs/` and the skill installation copy.
