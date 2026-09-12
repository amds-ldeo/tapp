# Superseded TAPPs — 2026-09-11

Retained for reference and provenance. **Do not develop against these, and do not register
procedures using them.** Folders beginning `Superseded` are excluded from `validate_tapp.py`
discovery.

## What was superseded, and by what

| Superseded | Successor |
|---|---|
| `LA-MC-ICPMS_TAPP_v76` | `v78` |
| `LA-MC-ICPMS_TAPP_v77` | `v78` |
| `LA-MC-ICPMS_UPb_TAPP_v75` | `v77` |
| `LA-MC-ICPMS_UPb_TAPP_v76` | `v77` |
| `LA-Q-ICP-MS_TAPP_v77` | `v79` |
| `LA-Q-ICP-MS_TAPP_v78` | `v79` |
| `LA-Q-ICP-MS_UPb_TAPP_v77` | `v79` |
| `LA-Q-ICP-MS_UPb_TAPP_v78` | `v79` |
| `LA-SF-ICP-MS_TAPP_v74` | `v76` |
| `LA-SF-ICP-MS_TAPP_v75` | `v76` |
| `LA-SF-ICP-MS_UPb_TAPP_v75` | `v77` |
| `LA-SF-ICP-MS_UPb_TAPP_v76` | `v77` |
| `Solution_MC-ICP-MS_TAPP_v76` | `v79` |
| `Solution_MC-ICP-MS_TAPP_v77` | `v79` |
| `Solution_MC-ICP-MS_TAPP_v78` | `v79` |
| `Solution_Q-ICP-MS_TAPP_v80` | `v82` |
| `Solution_Q-ICP-MS_TAPP_v81` | `v82` |
| `Solution_SF-ICP-MS_TAPP_v76` | `v78` |
| `Solution_SF-ICP-MS_TAPP_v77` | `v78` |

19 version(s), 38 file(s) (CSV + xlsx). Most TAPPs appear twice because two of the four passes
touched them; Solution MC, touched by three, appears three times.

## Why

Four passes on the same day, all arising from amds-ldeo/tapp#6. Answering it meant reading every
Solution MC paper for how it describes its detectors and whether it monitors doubly-charged ions.

### Pass 1 — six Solution MC literature cells corrected

`../../Project Files/Scripts/patch_faraday_barnes_solutionmc_20260911.py`. Solution MC v76 → v77.

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
`Mass Bias Correction Strategy` and `Analytical Accuracy and Assessment Method`. Pass 4 corrects
them.

### Pass 2 — the Doubly-Charged fields move into Module_ICPMS (v15 → v16)

`../../Project Files/Scripts/modularise_doubly_charged_20260911.py`. All nine ICP-MS TAPPs.

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
which every ICP-MS shares whatever the analyser. Solution MC gained both rows.

**Values.**
- `Production` already agreed in all eight.
- `Monitor` had two descriptions; the fuller LA text was adopted.
- Tiers are unchanged.

**Deliberately left open.** `Production` asks for both the threshold and the measured value, the
conflation the oxide pair was split to avoid. It was not split, because the measured half is
unattested.

### Pass 3 — Module_SingleCollector created (v1); `Detector Configuration` leaves LA-MC

`../../Project Files/Scripts/create_module_singlecollector_20260911.py`. Eight TAPPs.

**Why `Detector Configuration` left the multi-collector TAPPs.** Reading the Solution MC papers
settled what the field is.
- In LA-MC and LA-MC U-Pb it duplicated Module_MCICPMS's `Faraday Cup Array Configuration`. Every
  Solution MC paper that describes its detectors does so in that field's terms. For Zhang 2022, the
  one assessed LA-MC procedure, the two cells held the same content.
- It was removed from both LA-MC TAPPs. LA-MC U-Pb has no literature columns, so no evidence was
  lost.

**The new module.** It holds `Detector Configuration` and `Pulse/Analog Detector Nonlinearity
Correction` for the six single-collector ICP-MS TAPPs.
- **Rule 6.10:** 2 fields × 6 consumers = 12 placements, and it is a real component: the detection
  system of a single-collector analyser, the counterpart of Module_MCICPMS's Faraday array.
- **Rule 6.15:** the six TAPPs are a subset of Module_ICPMS's nine, which nominates absorption. The
  subject test refuses it, because Module_ICPMS is defined as what every ICP-MS shares independent
  of the analyser. The test is recorded as `sub_module_test` in the manifest.

**Values.**
- `Pulse/Analog` already agreed in all six.
- `Detector Configuration`'s three descriptions were harmonised to one single-collector text, and
  its "Multi-collector array" option left Column F.
- `Ion Counter Dead Time` is deliberately not included; the manifest records why.

### Pass 4 — the five remaining Barnes ETH cells corrected

`../../Project Files/Scripts/patch_barnes_eth_ti_solutionmc_20260911.py`. Solution MC v78 → v79.

These are the five cells pass 1 reported. Each was re-read against the ETH passage (pp.7–8) in
reading-order text, and every new value carries its page.

- **Two cells had borrowed from the LLNL procedure**, which the paper describes straight after ETH's.
  - `Integration Time per Cycle` read "4 s", LLNL's value. ETH used 8.39 s for the first cup
    configuration and 4.19 s for the second.
  - `Analytical Accuracy and Assessment Method` quoted "±0.16 and ±0.26 ε50Ti". ±0.16 is ETH's
    ε50Ti (9 analyses of BHVO-2); ±0.26 is LLNL's (16 analyses of BCR-2 and BHVO-2). Its quoted
    phrase "under conditions similar to the methods used" is from neither Ti procedure. It comes
    from the ion-chromatography section lower on p.8. The cell now gives ETH's three values
    (±0.17 ε46Ti, ±0.09 ε48Ti, ±0.16 ε50Ti) and the two materials ETH ran (BHVO-2, Agua Zarcas).
- **Three cells were incomplete.**
  - `Reported Variables and Units` and `Isotope Ratio Reported` gave only ε50Ti and 50Ti. The paper
    reports εiTi for 46Ti, 48Ti and 50Ti, each on iTi/47Ti.
  - `Mass Bias Correction Strategy` gave only bracketing. ETH normalised internally to
    49Ti/47Ti = 0.749766 with the exponential law and reported against a bracketing standard, the
    shape Budde 2016 and Hopp 2021 already record in that row.

**Noted, not acted on.** ETH's integration time is stated per cup configuration, as Nowell 2008
(NIGL) states its per sequence. That is per-pass evidence for a field keyed `monitored property`.

### Consequences of passes 2 and 3

- Both fields' entries left the validator's Column B divergence register, because neither diverges
  any more.
- The LA-MC mockup now points at v78. `cfg.json`'s hand-written footer count went from 125 to 124,
  and the page was rebuilt.

## Verification

Each pass was predicted before it ran, and a cell-level diff of every superseded/successor pair
matched the prediction.

**Pass 1.** Exactly 6 literature cells changed. No field, tier, data type, description or
`Keyed By` value changed.

**Pass 2.**
- **In all eight carriers,** each row's G gained the module stamp and its H was stamped
  2026-09-11.
- **In Solution Q and SF,** `Monitor`'s description changed to the LA text.
- **In the six LA TAPPs,** `Production`'s empty Purpose received the module default.
- **Solution MC** gained exactly the two rows (141 → 143), placed at the end of Group 4, with F and
  J filled from the module defaults and literature cells from the 2026-09-11 reading.

**Pass 3.**
- **In all six single-collector TAPPs,** `Detector Configuration` changed in B (new description),
  F (MC option removed), G and H. `Pulse/Analog` changed in G and H.
- **In the four LA TAPPs only,** both fields' empty Purpose cells received the module defaults.
- **Rows:** the row count and field order are unchanged in all six. LA-MC and LA-MC U-Pb each lost
  exactly one row.

**Pass 4.** Exactly 5 literature cells changed, all in `Barnes+etal2025 | Neptune Plus | ETH
Zurich`; rows (143), columns (25) and header unchanged. No field, tier, data type, description or
`Keyed By` value changed. `audit_keys_vs_literature.py` moved one count: `Integration Time per
Cycle` now scores scalar=9, unclear=2 (was 10 and 1), because the ETH cell holds one value per cup
configuration. Its verdict (OVER-DECLARED, KEEP) is unchanged.

**All passes.**
- `recompose_all_20260812.py --check`: 16 MATCH, 0 DIFFERS. The six single-collector TAPPs compose
  with `SingleCollector` in their recipes. That covers Rule 6.8's second composition and a
  structurally different consumer: the LA TAPPs carry three mode columns, the Solution TAPPs none.
- `check_field_ownership.py`: Doubly-Charged → ICPMS; Detector Configuration and Pulse/Analog →
  SingleCollector.
- `build_module_register.py --check` and `build_schema_spec_counts.py`: current.
- `audit_keys_vs_literature.py` regenerated after each pass. Apart from file names and row
  positions, no finding was added, removed or changed; pass 4's one moved count is given above.
- `validate_tapp.py`: 0 ERROR / 0 WARN before each save.
- **One reference was fixed by hand after pass 3.** `TAPP_Composed_Variants.csv` still named LA-MC
  U-Pb v76. `compose_tapp.py --out` advances that register's path references, and pass 3 removed
  LA-MC U-Pb's row without composing it, so nothing advanced its reference. The validator caught it
  (`doc-stale-version-ref`), and the path was set to v77. A script that bumps a TAPP without
  composing it must update this register itself.
