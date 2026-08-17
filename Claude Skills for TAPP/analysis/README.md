# Analysis artifacts

Evidence behind the module architecture (Rule 6 in `../references/conventions.md`). Kept here
rather than with the TAPPs they were derived from, because those TAPPs have been superseded and
these files are still cited.

| File | What it is |
|---|---|
| `Test4_Tier_Difference_Triage.csv` | All 26 tier differences between the LA-ICP-MS Geochronology TAPP and LA-Q/SF-ICP-MS, each classified drift / principled / bug. Established that 81% were drift and that only two differences were genuinely geochronology-exclusive. Cited in Rule 6.1 and in `precedents.md`. |
| `Test5_Geochronology_Module_CrossSystem.csv` | 15 candidate module fields against 6 dating systems (U-Pb ID-TIMS, Ar-Ar, Re-Os, (U-Th)/He, fission track, luminescence). Established which recur and which are general rather than geochronology-specific. |
| `MC-ICP-MS_Technology_Update_2026-07-29.txt` | Background note on MC-ICP-MS instrumentation. Copy; the original stays with the superseded Horstwood exercise. |

## Column B / Column I survey (2026-08-12)

Evidence behind the Rule 7.3 notation gaps. Prompted by `Monitored Masses` declaring
`defines: channel` while its description asserts an undeclared `analyte` key. Read-only survey — no
TAPP was modified; lint baseline stayed 0 ERROR / 0 WARN. Built by
`../../Project Files/Scripts/survey_colB_colI_20260812.py` and
`../../Project Files/Scripts/build_colI_survey_findings_20260812.py`.

| File | What it is |
|---|---|
| `Survey_ColB_ColI_Report_2026-08-12.md` | The report. Establishes that 5 of the 8 definer field names in the library carry an undeclared second key or an inexpressible domain shape; that 46 Column B rows still carry the `Analyte-Specific` label Rule 7.6 retired from Column G; and that 89 of 252 shared field names carry substantively divergent descriptions, none of them module-owned. Identifies three distinct notation gaps and recommends a separator. |
| `Survey_ColI_Findings_2026-08-12.csv` | 20 adjudicated findings in 8 classes, 92 affected rows, each with evidence quote, module-vs-TAPP owner and proposed action. Plus 19 field names adjudicated as false positives — almost all `per X` denoting a rate, unit, count or schedule rather than a key — recorded so a future sweep does not re-raise them. |
| `Survey_ColB_vs_ColI_AxisA_2026-08-12.csv` | Raw sweep: 321 cardinality-language hits in Column B, classified REDUNDANT / EXTRA / CONFLICT against Column I. Over-inclusive by design; the findings CSV is the adjudicated form. |
| `Survey_ColB_vs_ColI_AxisB_definers_2026-08-12.csv` | All 70 definer rows under 8 distinct field names — the complete population for the reported defect, so that class is closed rather than sampled. |

## Column B uniformity triage (2026-08-12)

| File | What it is |
|---|---|
| `Triage_ColB_Uniformity_2026-08-12.csv` | All 89 substantively divergent shared field names, each classified PRINCIPLED / MIXED / PARAPHRASE / SUPERSET / DRIFT with its basis and every variant's full text and owning TAPPs. Evidence behind Rule 7.8.9 and behind `COLB_DIVERGENCE_TRIAGED` in `validate_tapp.py`. Regenerated after the 2026-08-12 harmonisation pass: 71 entries remain (PRINCIPLED 54, MIXED 17), the MIXED set being the residual backlog. Built by `../../Project Files/Scripts/triage_colB_uniformity_20260812.py`; harmonisation applied by `../../Project Files/Scripts/One-shot (applied)/patch_colB_harmonise_20260812.py`. |
