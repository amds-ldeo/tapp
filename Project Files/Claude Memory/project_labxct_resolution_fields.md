---
name: project-labxct-resolution-fields
description: "Lab-XCT v17 — Minimum Resolvable Feature Size retired as redundant, Spatial Resolution renamed; 9 of 10 XCT papers use 'spatial resolution' to mean voxel size"
metadata: 
  node_type: memory
  type: project
---

**Status: EXECUTED 2026-08-12, Lab-XCT v16 → v17 (98 fields → 97).** Reasoning is in `precedents.md`, "Lab-XCT resolution fields — three collapsed to two". Column-by-column review table: https://claude.ai/code/artifact/8fa2fdf0-00c7-4a93-b02d-65f4d1c7cd24

**The two fields that remain:**

| Field | What it is | C/D | Keyed By |
|---|---|---|---|
| `Voxel Size` | reconstruction sampling interval | Basic / Editable | `(none)` |
| `Effective Spatial Resolution (PSF/MTF)` | can two features be *separated* — PSF, geometric unsharpness, reconstruction filter; Nyquist floor 2× voxel. **Contrast-independent** | N/A / Advanced | `(none)` |

`Minimum Resolvable Feature Size` is **gone**. The minimum feature size criterion now lives in
`Partial Volume Effect Criteria` (`sample > sampling unit`), which already asked for it.

**⚠ The literature fact that drives everything here — check before touching this field again.**
**Nine of ten XCT papers use "spatial resolution" to mean the voxel size.** Genge: *"Spatial
resolutions (in voxels) were 0.625 µm"*; Richard: *"2.06 µm/px (8.7 µm³/vx)"*; Tomkinson: *"resolution
of 10.3 × 10.3 × 10.3 µm³ per voxel"*. **One procedure in seventeen** reports an effective resolution
(Glavin, *"~30 µm, around 3× the voxel size"* — a rule of thumb, not MTF). So the field reads almost
empty and that is correct, not an extraction failure.

**Why:** the third field was retired for **redundancy, not subjectivity.** A stated cut-off is
analyst-defined by nature and must still be recorded — two labs reporting 12% porosity at 3-voxel and
10-voxel thresholds are not reporting the same number, and the library keeps equally subjective fields
(`Analysis Inclusion and Rejection Criteria`). The real ground: `Partial Volume Effect Criteria`
already requested *"the minimum feature size criterion adopted for the procedure (in voxels or µm)"*
and already held both real criteria in the corpus — Genge's ≥5.4 µm and Tomkinson's ~3 voxels, the
latter while the retired field read `N` for that same procedure. Genge's criterion sat in **both**
fields at once. The criterion/measurement split (Oxide Production pattern) fails when the measurement
half has one instance and it duplicates a resolution limit.

**How to apply:**
- **Before trusting any literature column, check what the papers mean by the field's own name.** A
  term precise in the TAPP may be loose in the community; extractions will be faithful to the papers,
  not to the definition. This is the generalisable lesson, and it is a sibling of the Phase 3 trap in
  [[project_tapp_session_sample_rule13]]'s EPMA note (a null result can be an artefact of which papers
  are in the corpus).
- File a paper's stated "spatial resolution" under `Voxel Size` unless PSF/MTF was actually measured.
  The renamed field's description now says this.
- Setting a feature-size criterion: Withers et al. (2021) — ≥3 voxels to identify, ≥10 for reliable
  shape and volume. Now cited in `Partial Volume Effect Criteria`.
- **Extraction traps confirmed in this corpus, do not re-import them:** Neuman's and Shearer's
  *"spatial resolution of 60 µm"* is a **multispectral core imager**, not XCT. Treiman's *"voxel
  dimension of 15 µm with a minimum resolution of 30 µm"* is explicitly the **NCT (neutron)**
  tomograms — that paper reports no X-ray parameters, and its cells now say so. Richard's "~2 µm" was
  the measured size of a vapour phase, not a detection limit; those two cells were cleared.

**Still open:** nothing for Lab-XCT. Library-wide, the related unresolved item is that nine of eleven
domain definers are `Text (free)` — domains declared but not machine-enumerable, which is the ceiling
on the JSON schema work.

See [[project_tapp_session_sample_rule13]], [[project_tapp_target_species_definition]], [[project_tapp_keyed_by_rule7]].
