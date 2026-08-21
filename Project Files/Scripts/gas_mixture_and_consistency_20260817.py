#!/usr/bin/env python3
"""
Add the cell-gas mixture field, and fix the cross-TAPP inconsistencies the consistency audit found.

NEW FIELD  `Collision/Reaction Gas Mixture Ratio` -> LA-Q, LA-Q_UPb, Solution Q
  Two independent attestations, one production:
    Wu et al. 2023 (LA-Q)     "the commonly used 1:9 NH3-He mixture", and high-purity He pre-mixed
                              with NH3 before the cell to test mixture composition
    Gil-Diaz et al. 2020 (Sol Q, XSeries 2)  "collision cell with He:H2 mixture at 92% : 8% to
                              minimise 40Ar37Cl interferences"  <- production procedure
  `Collision Gas Type` already offers `He+H2`, so the mixture IDENTITY had a home; the PROPORTIONS
  did not. Added to the same three TAPPs as `Reaction Product Ion / Mass-Shift Transition`, for the
  same reason: attested in LA-Q and Solution Q, and the U-Pb variant follows its parent. Not
  provisioned into the MC or SF TAPPs.

AUDIT FIXES — Column E is a definition column (Rule 6.4 module-owned letters; TAPP-owned here but the
same argument applies), so divergence in it is a defect, unlike Column F which is consumer-owned.

  1. `Collision Gas Type`  E: `Text (free)` (4 LA) vs `Controlled list` (2 Solution)
     -> `Controlled list / Text` in all 6, F = `He | H2 | He+H2 | N/A | None`.
     The compound is the right type now that mixtures need a qualifying answer. Per the conventions,
     a compound whose first component is `Controlled list` offers `N/A | None` but NOT
     `Other: specify` — the `/ Text` component already grants the unlisted answer.

  2. `Reaction Gas Type`   same divergence, same fix, F = `NH3 | O2 | CH4 | N/A | None`.
     The LA variants also used unicode subscripts (NH₃, O₂, CH₄) against the Solution ASCII forms;
     ASCII adopted, since these are controlled values that a consumer will match on.

  3. `Collision Gas Type` and `Reaction Gas Type` RE-KEYED `(none)` -> `channel`.
     The 2026-08-17 CRC re-key was incomplete: `CRC Configuration` became `channel` but the gases
     that define the mode did not. Gil-Diaz attests per-channel gas identity directly — its iCAP-TQ
     column reads "He for KED; O2 for the mass-shift mode" — so a `(none)` key cannot hold what is
     already extracted into the TAPP. Rule 7.12: the key is the finest axis attested in reported data.

     NOT re-keyed: `Collision Gas Flow Rate`, `Reaction Gas Flow Rate`, `Cell Exit Discrimination
     Voltage`. They plainly co-vary with the mode by physics, but no paper in the corpus states them
     per channel, and 7.12 decides on attestation rather than on what is physically possible. Flagged
     rather than assumed.

  4. `Dwell Time per Mass`  E: `Text (free)` (4 LA) vs `Numeric (ms) / Text` (2 Solution)
     -> `Numeric (ms) / Text` in all 6. It is a number with a unit that sometimes needs a per-mass
     list; the compound says exactly that and the bare text form loses the unit.

NOT divergent, confirmed by the same audit and recorded so it is not re-checked: `Monitored Masses`
(the `analyte` vs `defines: channel per analyte` split is the registered entry in
KEYED_BY_TECHNIQUE_DEPENDENT, with its rationale), and every field added this session —
`ICP Tuning`, `Instrument Warm-up / Session Duration Limit`, `Instrument Sensitivity`,
`Ion Counter Dead Time`, `Reaction Product Ion / Mass-Shift Transition`, `CRC Configuration` — each
uniform in C, D, E and I across every TAPP holding it.
"""
import csv, os, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
APPLY = "--apply" in sys.argv
DATE = "2026-08-17"
MIX = "Collision/Reaction Gas Mixture Ratio"

MIX_B = ("Where the collision or reaction cell is supplied with a mixture of gases rather than a single "
         "gas, the identities and proportions of that mixture. Recorded separately from the gas identity "
         "because the proportions change reaction efficiency and interference suppression independently "
         "of which gases are used. Record 'N/A' where a single gas is used.")
MIX_F = {
 "LA-Q-ICP-MS":       "e.g., 'NH3:He 1:9' | 'High-purity NH3, no mixture' | 'N/A (single gas)' | 'None'",
 "LA-Q-ICP-MS_UPb":   "e.g., 'NH3:He 1:9' | 'High-purity NH3, no mixture' | 'N/A (single gas)' | 'None'",
 "Solution_Q-ICP-MS": "e.g., 'He:H2 92% : 8%' | 'N/A (single gas)' | 'None'",
}
# literature cells for the new row, by column header substring
MIX_LIT = {
 "Wu+etal2023": ("Both forms stated: '1:9 NH3-He mixture' identified as common practice and found less "
                 "effective than high-purity NH3; high-purity He (>99.999%) pre-mixed with NH3 before the "
                 "reaction cell to test the effect of mixture composition on reaction efficiency"),
 "Thermo XSeries 2": "He:H2 mixture at 92% : 8%, used to minimise 40Ar37Cl interferences",
}

GAS = {
 "Collision Gas Type": ("Controlled list / Text", "He | H2 | He+H2 | N/A | None"),
 "Reaction Gas Type":  ("Controlled list / Text", "NH3 | O2 | CH4 | N/A | None"),
}
DWELL_E = "Numeric (ms) / Text"

JOBS = [
 ("LA-Q-ICP-MS/LA-Q-ICP-MS_TAPP_v23.csv",              "LA-Q-ICP-MS/LA-Q-ICP-MS_TAPP_v24.csv",              "LA-Q-ICP-MS",       1),
 ("LA-Q-ICP-MS/LA-Q-ICP-MS_UPb_TAPP_v23.csv",          "LA-Q-ICP-MS/LA-Q-ICP-MS_UPb_TAPP_v24.csv",          "LA-Q-ICP-MS_UPb",   1),
 ("Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v27.csv",  "Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v28.csv",  "Solution_Q-ICP-MS", 1),
 ("LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v20.csv",             "LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v21.csv",             "LA-MC-ICPMS",       0),
 ("LA-MC-ICP-MS/LA-MC-ICPMS_UPb_TAPP_v20.csv",         "LA-MC-ICP-MS/LA-MC-ICPMS_UPb_TAPP_v21.csv",         "LA-MC-ICPMS_UPb",   0),
 ("Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v24.csv","Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v25.csv","Solution_MC-ICP-MS",0),
 ("LA-SF-ICP-MS/LA-SF-ICP-MS_TAPP_v22.csv",            "LA-SF-ICP-MS/LA-SF-ICP-MS_TAPP_v23.csv",            "LA-SF-ICP-MS",      0),
 ("LA-SF-ICP-MS/LA-SF-ICP-MS_UPb_TAPP_v23.csv",        "LA-SF-ICP-MS/LA-SF-ICP-MS_UPb_TAPP_v24.csv",        "LA-SF-ICP-MS_UPb",  0),
]

for src, dst, key, add_mix in JOBS:
    p = os.path.join(ROOT, src)
    rows = list(csv.reader(open(p, encoding='utf-8-sig')))
    hdr = rows[0]; ncol = len(hdr)
    si = hdr.index('Literature Assessment') if 'Literature Assessment' in hdr else ncol
    acts = []

    for r in rows[1:]:
        if not r or not r[0].strip():
            continue
        if r[0] in GAS:
            e, f = GAS[r[0]]
            if (r[4], r[5], r[8]) != (e, f, 'channel'):
                r[4], r[5], r[8], r[7] = e, f, 'channel', DATE
                acts.append(f"{r[0].split()[0]} gas E+key")
        if r[0] == "Dwell Time per Mass" and r[4] != DWELL_E:
            r[4], r[7] = DWELL_E, DATE
            acts.append("dwell E")

    if add_mix:
        anchor = max(i for i, r in enumerate(rows) if r and r[0] == "Reaction Gas Flow Rate")
        new = [MIX, MIX_B, "Advanced", "Editable", "Text (free)", MIX_F[key], "", DATE, "channel"]
        new += [""] * (ncol - len(new))
        for k in range(9, si):          # mode flag columns, if any
            new[k] = "Y"
        for k in range(si + 1, ncol):   # literature columns
            new[k] = "N"
            for frag, val in MIX_LIT.items():
                if frag in hdr[k]:
                    new[k] = val
        rows.insert(anchor + 1, new)
        acts.append(f"added {MIX}")

    assert all(len(r) == ncol for r in rows), f"{key}: ragged"
    if not acts:
        print(f"SKIP  {os.path.basename(src):36} nothing to change")
        continue
    print(f"{'WROTE' if APPLY else 'DRY '} {os.path.basename(dst):36} " + "; ".join(sorted(set(acts))))
    if APPLY:
        with open(os.path.join(ROOT, dst), "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerows(rows)

if not APPLY:
    print("\ndry run — rerun with --apply")
