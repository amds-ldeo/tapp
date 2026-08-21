#!/usr/bin/env python3
"""
Add the ICP-MS back-end fields the Solution TAPPs were missing, ahead of Phase 3.

Triage of the 10 LA-only candidates (all confirmed absent from Solution Q/SF/MC):

  ADD    ICP Tuning                                  description technique-neutral; attested 6/11
  ADD    Instrument Warm-up / Session Duration Limit  description technique-neutral; attested 3/11 partial
  ADD    Ion Counter Dead Time                        its own description says it is DISTINCT from
                                                      pulse/analog cross-calibration, which is what
                                                      Solution Q/SF already have
  ADD    Instrument Sensitivity  (NEW NAME)           LA's `Sensitivity as Useful Yield` is Numeric (%)
                                                      keyed by analyte and argues useful yield beats
                                                      cps/ppb *because of spot size, fluence and rep
                                                      rate* -- an LA-only rationale. Solution work
                                                      reports cps per unit concentration. Different
                                                      field, so a different name (user decision,
                                                      2026-08-14).

  FIX    Make-up Gas Flow Rate                        NOT a duplicate of LA's `Plasma / Make-up Gas
                                                      Addition`. The Solution description scoped it to
                                                      desolvation only ("Record 'N/A' if no desolvation
                                                      system is used"), but Lu et al. 2007 Table 1a
                                                      reports "Make-up Ar gas flow rate 0.25 l/min" on a
                                                      cooled Scott chamber with NO desolvator -- an
                                                      attested value the field could not hold. Broadened,
                                                      and E made compound so the gas can be named
                                                      (N2 addition for sensitivity enhancement).

  DEFER  Background Count Time      shared with 6 LA tables; its description is laser-framed ("laser off
                                    or shutter closed") and generalising it is a 9-TAPP Rule 4
                                    propagation + Rule 7.8.9 Column B harmonisation, not a local add.
                                    Concept IS attested: Lu 2007 pseudo-FI step 1 = 40 s background;
                                    Desem 2022 blank determination before each acquisition. MC already
                                    has `Baseline Measurement Approach`, which covers approach+timing.
  DEFER  Fusion Flux and Dilution Ratio    no assessed procedure uses fusion; decide after the MC round
  NO     Signal Smoothing           squid/ARIS devices exist because ablation is pulsed
  NO     Sample Introduction        Module_SolutionIntroduction is its Solution counterpart
  NO     Multi-Run Sequential Analysis Design   framed on "the same sample location"

Also fills the four new rows in the existing Q (5) and SF (6) literature columns, from the same PDFs
read on 2026-08-14. Sources keyed as in build_newfield_lit_drafts_20260814.py.
"""
import csv, os, sys, shutil

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
APPLY = "--apply" in sys.argv
DATE = "2026-08-14"

SPECS = {
 "Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v22.csv": ("Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v23.csv", 5),
 "Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v23.csv": ("Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v24.csv", 6),
 "Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v21.csv": ("Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v22.csv", 0),
}

D_TUNE = ("Description of the approach used to optimise ICP plasma conditions prior to analysis, "
 "including the reference material used for tuning and the acceptance criteria (e.g., oxide production "
 "threshold, sensitivity targets, mass calibration).")
D_WARM = ("Minimum warm-up time required after plasma ignition before analyses begin, and any maximum "
 "session duration enforced to maintain stable operating conditions. These constraints are part of the "
 "procedure and cannot be varied by the analyst.")
D_SENS = ("Instrument sensitivity achieved in the session, expressed as detected signal per unit "
 "concentration or per unit mass of analyte delivered, together with the isotope it was measured on and "
 "the conditions it applies to (uptake rate, resolution mode, cone set). Records what the instrument "
 "actually delivered; the sensitivity a procedure requires before analyses may begin is part of the "
 "tuning acceptance criteria.")
D_DEAD = ("Dead time of each ion-counting detector channel, used in the dead-time correction applied to "
 "high count rates. Distinct from pulse/analog cross-calibration, which relates the two detector modes "
 "rather than correcting counting losses within the pulse-counting mode.")
D_MAKEUP = ("Supplementary gas flow added to the sample-carrying stream upstream of the plasma, with the "
 "gas identity where it is not argon. Argon make-up is used to maintain total gas delivery where a "
 "desolvation system removes solvent load, and also to trim total flow where no desolvator is fitted. "
 "Small nitrogen additions are used to enhance sensitivity for some elements. Record 'None' explicitly "
 "where no supplementary gas is added, to distinguish it from not reported.")

# name: (B, C, D, E, I, {tapp_key: F})
NEW = {
 "ICP Tuning": (D_TUNE, "Advanced", "Editable", "Text (free)", "(none)", {
   "Q":  "e.g., 'Daily optimisation of autolens voltages on a 10 ng/ml Mg-Co-Rh-Ce-Pb-U solution; nebuliser gas set for maximum sensitivity with CeO+/Ce+ and Ce2+/Ce+ <2.5%' | 'Daily tune on 10 ppb Mg-In-U; CeO/Ce constrained within 3%'",
   "SF": "e.g., 'Daily tune on 5 ng/ml Be-Rh-U to maximise sensitivity across the mass range; CeO+/Ce+ <2 permil' | 'Tuned to ~1000 kcps/ppb Pb while maintaining flat-topped peaks' | 'Optimised on 11B, 115In and 175Lu, with 2.5x10^6 cps/ppb on 115In set as an operational criterion; medium-resolution tune on 56Fe for separation from 40Ar16O'",
   "MC": "e.g., 'Daily tune on the bracketing standard at run concentration; optimised for maximum intensity and peak flatness with UO+/U+ <0.5%' | 'Tuned on 100 ng/ml Nd; oxide production monitored on CeO+/Ce+'"}),
 "Instrument Warm-up / Session Duration Limit": (D_WARM, "Advanced", "Read-Only", "Text (free)", "(none)", {
   "Q":  "e.g., 'Rock solution flushed through for 30 min before tuning' | '>=30 min warm-up after plasma ignition; no session duration limit' | 'Sessions <=5 h, the interval over which blanks remain stable'",
   "SF": "e.g., '>=1 h warm-up after plasma ignition' | 'Instrument conditioned with a matrix-matched solution before the first sample; no session duration limit'",
   "MC": "e.g., '>=1 h warm-up after plasma ignition; sessions <=12 h' | '30 min warm-up; no session duration limit'"}),
 "Instrument Sensitivity": (D_SENS, "N/A", "Advanced", "Numeric + unit / Text", "channel", {
   "Q":  "e.g., '~40 kHz per ppb 115In at 60 ul/min uptake' | '0.04 count pg-1 ml (111Cd); 0.5 (115In); 0.5 (205Tl); 0.6 (209Bi)'",
   "SF": "e.g., '~1000 kcps/ppb 208Pb (Attom, deflector peak jump)' | '~2.5x10^6 cps/ppb 115In (low resolution)' | '~5000 cps nM-1 for Co after pre-concentration'",
   "MC": "e.g., '100 V/ppm total Nd on 10^11 ohm amplifiers' | '40 V per ppm 208Pb with desolvating nebuliser'"}),
 "Ion Counter Dead Time": (D_DEAD, "Basic", "Editable", "Numeric (ns)", "channel", {
   "Q":  "e.g., '23' | '35 ns, determined from a Th calibration series and checked quarterly' | 'N/A (analog detection only)'",
   "SF": "e.g., '23' | '20 ns, determined from a U calibration series' | 'N/A (analog detection only)'",
   "MC": "e.g., '23 ns (SEM behind L4)' | '20 ns each on the four ion counters' | 'N/A (Faraday cups only)'"}),
}

# literature cells, order = the TAPP's existing literature columns
LIT = {
 "Q": {
  "ICP Tuning": [
   'Autolens voltages "set by optimizing a solution of 10 ng/ml Mg, Co, Rh, Ce, Pb and U"; "The nebulizer gas flow rate was optimized to obtain maximum signal intensities for Mg, Co, Rh, Ce, Pb and U, while keeping the CeO+/Ce+ and Ce2+/Ce+ ratios below 2.5%" [H sec 3.1]',
   '"The instrument sensitivity was optimized daily using a 10 ppb Mg-In-U standard"; "Plasma robustness was monitored by constraining CeO/Ce ratio within 3% to refrain formation of polyatomic oxides" [Y sec 2]',
   'N',
   'N',
   'Partially -- an oxide acceptance criterion is registered in the operating conditions, "Oxide forming rate <1% (CeO+/Ce+)" [Lu Table 1a]; no tuning solution or tuning procedure stated'],
  "Instrument Warm-up / Session Duration Limit": [
   'Partially -- instrument conditioning before tuning is stated: "Drift was minimized by flushing through a rock solution for 30 min before tuning the instrument for a run" [H sec 3.1]. No warm-up time after plasma ignition and no session duration limit stated',
   'Partially -- session duration is characterised but not enforced: "blanks for all isotopes were stable during a typical run (~5 hr)" [Y sec 3.2]',
   'N', 'N', 'N'],
  "Instrument Sensitivity": [
   'N',
   '"The sensitivity of the instrument is ~40 kHz for 1 ppb 115In at a sample uptake rate of 60 ul/min" [Y sec 2]; per-isotope sensitivity in CPS/ppb tabulated [Table 1]',
   'Per-isotope sensitivity in count pg-1 ml: 111Cd 0.04, 115In 0.5, 149Sm 0.09, 205Tl 0.5, 209Bi 0.6 [M Table 1]',
   'N', 'N'],
  "Ion Counter Dead Time": ['N','N','N','N','N'],
 },
 "SF": {
  "ICP Tuning": [
   '"The instrument was tuned to provide ~1000 kcps/ppb Pbtotal while maintaining flat-topped peaks" [D sec 2.4]',
   '"The instrument was tuned using a 5 ng mL-1 solution containing Be, Rh and U in order to maximize the sensitivity covering the low-mid-high mass range. MO+/M+ ratios measured for Ce under the routine experiment conditions maintained at less than 2 permil" [Li sec 2.1]',
   'Partially -- an oxide acceptance criterion is registered in the operating conditions, "Oxide forming rate <1% (CeO+/Ce+)" [Lu Table 1b]; no tuning solution or tuning procedure stated',
   '"At the start of each day, prior to any sample analysis, the instrument was first tuned to produce maximum sensitivity and stability while also maintaining low oxide formation ... using a 5ppb solution of In"; "Further tuning using a 5ppb solution of Fe in the medium resolution mode ensured maximum separation of the 56Fe peak from the 40Ar16O peak"; oxide formation "typically below 5%", above 10% causing problems [Mi sec 2.4]',
   '"Instrumental sensitivity was optimized on 11B, 115In, and 175Lu", with sensitivities "set as operational criteria"; "in medium resolution tuning, the instrument was optimized on 56Fe to achieve a mass resolution" [Ms sec 3.1, sec 2.3]',
   'N'],
  "Instrument Warm-up / Session Duration Limit": [
   'N','N','N','N',
   'Partially -- "The instrument was conditioned with a 10 [ppb solution]" before analysis, and detector mode was "kept fixed through the entire run to avoid detection mode switch induced changes in sensitivity" [Ms sec 3.1]. No warm-up time or session duration limit stated',
   'N'],
  "Instrument Sensitivity": [
   '"tuned to provide ~1000 kcps/ppb Pbtotal" [D sec 2.4]',
   'N', 'N',
   '"~5000 cps nM-1" for Co and "~3100 cps nM-1" for Mn from standard additions, highest observed 3560 cps nM-1; "Observed count rates for this solution were in general ~1,000,000 cps" for a 5 ppb In solution [Mi sec 2.4, sec 3.2]',
   '"a typical sensitivity of ~2.5 x 10^6 cps/ppb on 115In"; per-matrix sensitivity for 1 ppb 11B and 1 ppb 115In tabulated across spray chamber, injector and acid matrix combinations [Ms sec 3.1, Table 2]',
   'N'],
  "Ion Counter Dead Time": ['N','N','N','N','N','N'],
 },
}

def group4_bounds(rows):
    s = e = None
    for i, r in enumerate(rows):
        if r and r[0].startswith('4. '): s = i
        if r and r[0].startswith('5. '): e = i; break
    return s, e

changed = []
for src, (dst, nlit) in SPECS.items():
    key = "Q" if "Q-ICP" in src else ("SF" if "SF-ICP" in src else "MC")
    path = os.path.join(ROOT, src)
    rows = list(csv.reader(open(path, encoding='utf-8-sig')))
    ncol = len(rows[0])
    before = len(rows)
    g4s, g4e = group4_bounds(rows)

    def row_for(name):
        B, C, D, E, I, F = NEW[name]
        r = [name, B, C, D, E, F[key], "", DATE, I] + [""] * (ncol - 9)
        if nlit and key in LIT and name in LIT[key]:
            cells = LIT[key][name]
            assert len(cells) == nlit, f"{name}: {len(cells)} cells for {nlit} columns"
            r[10:10 + nlit] = cells
        return r

    # block 1 -- after Plasma Thermal Mode
    anchor = next(i for i in range(g4s, g4e) if rows[i] and rows[i][0] == "Plasma Thermal Mode")
    block1 = [row_for(n) for n in ("ICP Tuning", "Instrument Warm-up / Session Duration Limit",
                                   "Instrument Sensitivity")]
    rows[anchor + 1:anchor + 1] = block1
    g4e += len(block1)
    # block 2 -- last field of Group 4
    last = max(i for i in range(g4s, g4e) if rows[i] and rows[i][0].strip())
    rows[last + 1:last + 1] = [row_for("Ion Counter Dead Time")]

    # Make-up Gas Flow Rate description + data type fix
    fixed = False
    for r in rows:
        if r and r[0] == "Make-up Gas Flow Rate":
            r[1] = D_MAKEUP
            r[4] = "Numeric (L/min) / Text"
            r[5] = ("e.g., '0.25 (Ar, no desolvator fitted)' | '0.85 Ar + 4 ml/min N2 "
                    "(sensitivity enhancement)' | 'None'")
            r[7] = DATE
            fixed = True
    assert fixed, f"Make-up Gas Flow Rate not found in {src}"

    assert len(rows) == before + 4, f"row count {before} -> {len(rows)}"
    assert all(len(r) == ncol for r in rows), "ragged row"
    changed.append((src, dst, before, len(rows)))
    if APPLY:
        out = os.path.join(ROOT, dst)
        with open(out, "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerows(rows)

for src, dst, b, a in changed:
    print(f"{'WROTE' if APPLY else 'DRY '} {os.path.basename(dst):38} rows {b} -> {a} (+4 fields, Make-up Gas fixed)")
if not APPLY:
    print("\ndry run -- rerun with --apply")
