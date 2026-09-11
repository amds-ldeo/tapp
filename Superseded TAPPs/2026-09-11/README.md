# Superseded TAPPs — 2026-09-11

Retained for reference and provenance. **Do not develop against these, and do not register
procedures using them.** Folders beginning `Superseded` are excluded from `validate_tapp.py`
discovery.

## What was superseded, and by what

| Superseded | Successor |
|---|---|
| `LA-MC-ICPMS_TAPP_v76` | `v77` |
| `LA-MC-ICPMS_UPb_TAPP_v75` | `v76` |
| `LA-Q-ICP-MS_TAPP_v77` | `v78` |
| `LA-Q-ICP-MS_UPb_TAPP_v77` | `v78` |
| `LA-SF-ICP-MS_TAPP_v74` | `v75` |
| `LA-SF-ICP-MS_UPb_TAPP_v75` | `v76` |
| `Solution_MC-ICP-MS_TAPP_v76` | `v78` |
| `Solution_MC-ICP-MS_TAPP_v77` | `v78` |
| `Solution_Q-ICP-MS_TAPP_v80` | `v81` |
| `Solution_SF-ICP-MS_TAPP_v76` | `v77` |

10 version(s), 20 file(s) (CSV + xlsx). Solution MC appears twice because both passes touched it.

## Why

Two passes on the same day, both arising from amds-ldeo/tapp#6. Answering it meant reading every
Solution MC paper for how it describes its detectors and whether it monitors doubly-charged ions.

### Pass 1 — six Solution MC literature cells corrected (v76 → v77)

`../../Project Files/Scripts/patch_faraday_barnes_solutionmc_20260911.py`.

- **`Faraday Cup Array Configuration`, four cells.**
  - Craddock 2008 and Nowell 2008 (NIGL Nu Plasma) read `N`, but both papers state the array:
    nine Faraday cups, and a 7-Faraday "U–Pb" collector block.
  - Nie 2019 read "Three collectors used". That is how many collectors the procedure used, which
    `Collector Configuration` already records. The paper states the array: nine Faraday collectors.
  - Nowell 2008 (Durham Neptune) gains its page reference and the SEM ion counter the same paper
    uses for abundance sensitivity. The field asks whether an ion counter is present.
- **Barnes 2025, ETH Zurich, two cells.** `Monitored Masses` quoted a sentence that does not exist
  in the paper. It joined the ETH Ti procedure's opening to the LLNL procedure described
  immediately after it, bringing in ⁴⁵Sc, which only LLNL measured. The cell now gives ETH's two
  cup configurations, and `Collector Configuration` lists both.

The cause of the Barnes error is recorded for reuse: `pdftotext -layout` interleaves the two
columns of a journal page, so a quote lifted from it can join two sentences. Quote from
reading-order text only.

Four further Barnes-ETH cells disagree with the ETH passage, and a fifth cites a value not found
in it. All five were reported rather than changed, because the correction was scoped to the cells
above: `Integration Time per Cycle`, `Reported Variables and Units`, `Isotope Ratio Reported`,
`Mass Bias Correction Strategy` and `Analytical Accuracy and Assessment Method`.

### Pass 2 — the Doubly-Charged fields move into Module_ICPMS (v15 → v16), all nine ICP-MS TAPPs

`../../Project Files/Scripts/modularise_doubly_charged_20260911.py`.

**Why here.** `Doubly-Charged Species Monitor` and `Doubly-Charged Species Production` were in eight
of the nine ICP-MS TAPPs, every one but Solution MC. So each carrier held its own copy rather than
composing one. On 2026-08-14 they were held back until Solution MC's literature could say whether
it genuinely lacks them.

**What the literature showed.** It cannot tell them apart:
- 0 of 14 Solution MC procedures report a tuning-time M²⁺/M⁺ ratio, and neither do the Q and SF
  papers (1 of 15).
- Two MC papers name doubly-charged ions as interferences (Craddock 2008, Pringle & Moynier 2017).
  That is `Interfering Species` content, and those two cells record it as `N (...)`.

The placement therefore rests on the module's own subject: doubly-charged ions form in the plasma,
which every ICP-MS shares whatever the analyser. The module's footprint was already these nine
TAPPs, so no new module was needed.

**Values.** Taken from the carriers:
- `Production` already agreed in all eight.
- `Monitor` had two descriptions; the fuller LA text was adopted.
- Tiers stay at C=Advanced, D=Editable.

**Deliberately left open.** `Production` asks for both the threshold and the measured value, the
conflation the oxide pair was split to avoid. It was not split, because the measured half is
unattested. Recorded in the module's `decisions`.

**Consequences, all by design:**
- `Monitor`'s entry in the validator's Column B divergence register was removed, because the field
  no longer diverges.
- `Project Files/Reports/cfg.json` and the Reports README now point the LA-MC mockup at v77, and the
  mockup was rebuilt.

## Verification

**Pass 1.**
- A cell-level diff shows **exactly 6 cells changed**, all in literature columns. Row count and
  header are unchanged.
- No field, tier, data type, description or `Keyed By` value changed.

**Pass 2.** A cell-level diff of every pair shows only the expected cells:
- **In all eight carriers,** each row's G gained `Source: ICP-MS module` and its H was stamped
  2026-09-11.
- **In Solution Q and SF,** `Monitor`'s description changed to the LA text.
- **In the six LA TAPPs,** `Production`'s empty Purpose received the module default.
- **Solution MC** gained exactly the two rows (141 → 143), placed at the end of Group 4. Composition
  does not fill Column F or J on an inserted row, so the script filled both from the module
  defaults. Its literature cells come from the 2026-09-11 reading: 12 plain `N` plus two `N (...)`
  on `Monitor`, and 14 `N` on `Production`.
- No other cell moved in any TAPP.

**Both passes.**
- `recompose_all_20260812.py --check`: 16 MATCH, 0 DIFFERS.
- `check_field_ownership.py` reports both fields as Module_ICPMS.
- `build_module_register.py --check` and `build_schema_spec_counts.py`: current.
- `audit_keys_vs_literature.py` regenerated. Apart from file names, the only change is that four
  Solution MC findings moved down two rows, because the two new rows sit above them. No finding was
  added, removed or changed.
- `validate_tapp.py` after both passes: 0 ERROR / 0 WARN.
