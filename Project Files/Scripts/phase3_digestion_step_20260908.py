#!/usr/bin/env python3
"""Phase 3: fill `Digestion Step` from the sources, and correct the neighbouring cells that reading
them exposed.

The 2026-09-08 re-type (Integer -> Text (free)) left the definer empty in every column whose digestion
was attested only through its consumers. This pass reads the 15 source PDFs and enumerates the members.
Every value below is quoted or paraphrased from the paper named in the column header, applying Column
B's grain rule: an evaporation or dry-down carrying no attack of its own belongs to the step it follows;
an identical attack repeated on the residue is a repeat; a final uptake is not a step.

It also corrects six neighbouring cells that the reading falsified -- see NEIGHBOUR below. Those were
not sought; they surfaced because a definer forces you to read the sequence rather than count it.
"""
import csv, os, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
MC = "Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v70.csv"
Q  = "Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v76.csv"
SF = "Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v72.csv"

# {file: {column index: value}} -- indices verified against the header before writing
STEPS = {
 MC: {
  11: ("1: HF-HNO3 (-HClO4), closed Savillex beakers on a hotplate | 2: inverse aqua regia. "
       "Both steps stated; conditions not given beyond 'on a hotplate'."),
  12: ("1: 5 ml HNO3 (50%), hot plate below 70 deg C, taken to dryness | 2: 3 ml concentrated HNO3 + "
       "2 ml HCl (50%), sealed PTFE vessel, 70 deg C, taken to dryness. The subsequent 4 ml 2% HNO3 is "
       "the final uptake, not a step."),
  13: ("Iron meteorites, 1: aqua regia (3:1 HCl-HNO3), 120 deg C, 24 h on a hot plate. Basalts, "
       "1: HF-HNO3 (2:1), 150 deg C, 48 h on a hot plate | 2: 'several steps of aqua regia', number "
       "not stated. Both routes then converted to chloride and taken up in 0.25 ml 10 M HCl."),
  14: ("1: HF/HNO3 in 3:1 proportion with a few drops of HClO4, hot plate 160 deg C, 2 weeks | "
       "2: evaporated to dryness and redissolved in a 2:1 mixture of HCl:HNO3, 1 week on a hot plate. "
       "\"These steps were performed twice to ensure complete digestion\" -- the PAIR is repeated, so "
       "under the 2026-09-08 grain rule the members are 2, not 4. The subsequent concentrated HNO3 and "
       "3 M HNO3 are dry-down and uptake, not steps. Resolves the cell left open on 2026-09-08."),
  15: ("Untreated crystals, 1: 29 M HF in a PFA microcapsule inside a Parr vessel, 215 deg C, 48 h. "
       "Chemically abraded crystals (19 zircons), 1: 12-h partial dissolution in 29 M HF at 215 deg C "
       "under pressure, after annealing at 900 deg C for 60 h | 2: the same complete digestion. The "
       "annealing is a pre-treatment, not a digestion step."),
  17: "N/A - reference material solutions, no digestion.",
  18: "N/A - reference material solutions, no digestion.",
  19: ("1: concentrated HF/HNO3, closed Teflon bombs, 130 deg C, >48 h | 2: after evaporation of the "
       "HF/HNO3, 6N HCl at 130 deg C to dissolve fluoride complexes. Samples were then evaporated to "
       "dryness and were ready for chemistry."),
  21: ("Bulk and chondrule route, 1: 3:1 7 M HNO3 : 28 M HF in Parr bombs, 3 days (1 day at 150 deg C, "
       "2 days at 210 deg C) | 2: dried down and taken up in aqua regia, 2 further days on a hotplate. "
       "Si route, 1: NaOH fusion in silver crucibles, 720 deg C, 13 min, the fusion cake dissolved in "
       "Milli-Q water and acidified with HNO3 -- a fusion rather than an acid digestion."),
  22: ("1: 3:2 concentrated HF : double-distilled HNO3 in PFA vials, hotplate 150 deg C, about 1 week | "
       "2: dried down, dissolved in 1 ml concentrated HNO3, with 1 ml H2O2 added slowly in 0.1 ml "
       "increments | 3: dried down, dissolved in double-distilled HCl. The final 5 ml 2% HNO3 is the "
       "uptake, not a step."),
  23: ("1: concentrated HF and HNO3 in a 3:1 ratio, closed beaker, 170 deg C, 48 h | 2: fluxing in "
       "concentrated HNO3 and HCl, with 1 ml H2O2 added slowly during the HNO3 flux to remove organics. "
       "The 5 ml 0.5 M HNO3 is the uptake, not a step."),
  24: "Coordinated dissolution shared with the WUSTL split - see the WUSTL column.",
 },
 Q: {
  13: ("Basalts, andesites and NIST SRM 612/614/616, 1: HF-HClO4 with the Sm spike in an ultrasonic "
       "bath, then dried to decompose fluorides; final uptake in 0.5 mol/l HNO3. Peridotites and "
       "carbonaceous chondrites, 1: HF with the Sm spike in a TFE bomb at 245 deg C | 2: dried with "
       "HClO4; final uptake in 0.5 mol/l HNO3."),
  15: ("1: HF decomposition, by the bomb method or the ultrasonic method depending on the material | "
       "2: evaporation then re-dissolution in 0.5 mol/l HF, fluorides removed by centrifuging."),
  17: ("Te route (tri-acid), 1: 750 uL HNO3 (14 M) + 1.5 ml HCl (10 M) + 2.5 ml HF (29 M) in closed PP "
       "tubes on a heating block, 2 h at 110 deg C | 2: evaporation at 120 deg C then re-dissolution in "
       "250 uL HNO3 (14 M) with heating; brought to 10 ml with Milli-Q. Se route (microwave-assisted), "
       "1: 3 ml HNO3 + 0.5 ml H2O2 + 0.25 ml HF, ramp to 210 deg C held 10 min -- Se is volatile above "
       "70 deg C and is not compatible with the tri-acid route."),
 },
 SF: {
  11: ("Rock chips, 1: concentrated HF (3 ml, 100 deg C, 48 h, then evaporation) | 2: concentrated HNO3 "
       "(2 x 1 ml, 100 deg C, 12 h) | 3: 5 M HNO3 (5 ml, 100 deg C, 15 h). Soil total-dissolution "
       "fraction, 1: concentrated HNO3 (3 ml, 80 deg C, 48 h) to destroy organics, this leachate "
       "discarded | 2: concentrated HF (4 ml, 100 deg C, 48 h, then evaporation) | 3: concentrated HNO3 "
       "(2 x 1 ml, 100 deg C) | 4: 6 M HCl (5 ml, 80 deg C, 15 h). Soil aqua-regia fraction, 1: 3 ml "
       "aqua regia (3:1 HCl:HNO3), shaken."),
  13: ("1: HF decomposition, by the bomb method or the ultrasonic method depending on the material | "
       "2: evaporation then re-dissolution in 0.5 mol/l HF, fluorides removed by centrifuging."),
  16: ("1: 1-2 ml HF (24 mol/l) + 0.2 ml HNO3 (14 mol/l) -- non-refractory samples on a hotplate, 12 h "
       "at 130 deg C in closed Savillex PFA vials; refractory samples (e.g. granites, zircon-bearing) "
       "stirred 7 days at 180 deg C in Parr bombs, the bombs opened after 3 days and refilled with "
       "0.5 ml HF | 2: evaporation to incipient dryness at ~80 deg C, re-dissolution in a few drops of "
       "HNO3 (14 mol/l) and evaporation again, repeated twice to remove insoluble fluorides | 3: 2 ml "
       "HCl (6 mol/l), heated at 80 deg C, then evaporated at 50 deg C to form chlorides. The 5 ml "
       "HNO3 (7 mol/l) is the final uptake, not a step."),
 },
}

# Cells the reading falsified. {file: {column index: {field: new value}}}
NEIGHBOUR = {
 MC: {
  14: {"Digestion Acid(s)":
        "HF/HNO3 in 3:1 proportion with a few drops of HClO4, then -- after evaporation to dryness -- a "
        "2:1 mixture of HCl:HNO3; dried down and dissolved in concentrated HNO3, diluted in 3 M HNO3 "
        "and centrifuged. The first HF/HNO3-HClO4 attack was missing from this cell before 2026-09-08.",
       "Digestion Temperature": "160 deg C (hot plate)",
       "Digestion Duration":
        "2 weeks for the HF-HNO3-HClO4 step and 1 week for the HCl-HNO3 step, the pair performed twice"},
  15: {"Digestion Duration":
        "48 h at 215 deg C in a Parr vessel. The 60 h previously recorded here is the chemical-abrasion "
        "ANNEALING at 900 deg C, not a digestion; the abrasion leach itself is 12 h."},
  21: {"Digestion Temperature":
        "150 deg C for 1 day then 210 deg C for 2 days (Parr bomb); hotplate for the aqua regia step; "
        "720 deg C for the NaOH fusion (Si route). The 130 deg C 10 M HCl step previously recorded here "
        "is Cr(VI) speciation during column chemistry, not a digestion.",
       "Digestion Duration":
        "3 days in the Parr bomb (1 + 2 days) then 2 days in aqua regia; 13 min for the NaOH fusion. "
        "The 3 h and >1 week previously recorded here are Cr speciation during column chemistry."},
  22: {"Digestion Temperature": "150 deg C (hotplate). The 70 and 140 deg C previously recorded here "
        "belong to the carbonate-removal pre-treatment and to the cosmogenic-radionuclide dissolution, "
        "which are different preparations in the same paper.",
       "Digestion Duration": "About 1 week for the HF-HNO3 step. The 20 h previously recorded here is "
        "the cosmogenic-radionuclide dissolution, a different preparation."},
 },
 SF: {
  11: {"Digestion Acid(s)":
        "Rock chips: concentrated HF, then concentrated HNO3, then 5 M HNO3. Soil total dissolution: "
        "concentrated HNO3 organic-destruction leach (discarded), then concentrated HF, then "
        "concentrated HNO3, then 6 M HCl. Soil aqua-regia fraction: 3 ml aqua regia (3:1 HCl:HNO3)."},
  16: {"Digestion Acid(s)":
        "HF (1-2 ml, 24 mol/l) + HNO3 (0.2 ml, 14 mol/l), with 0.5 ml HF added mid-run for the "
        "refractory route; then HNO3 (14 mol/l) twice to remove insoluble fluorides; then HCl "
        "(6 mol/l) to form chlorides. Final uptake in 5 ml HNO3 (7 mol/l)."},
 },
}


def main(apply=False):
    for rel in (MC, Q, SF):
        p = os.path.join(ROOT, rel)
        rows = list(csv.reader(open(p, newline="", encoding="utf-8-sig")))
        h = rows[0]
        by = {r[0].strip(): r for r in rows[1:] if r and r[0].strip()}
        step = by["Digestion Step"]
        for i, v in STEPS.get(rel, {}).items():
            print("  %-28s [%2d] %-46s %r -> set" % (
                os.path.basename(rel), i, h[i][:46].replace("\n", " "), step[i][:22]))
            step[i] = v
        for i, fields in NEIGHBOUR.get(rel, {}).items():
            for f, v in fields.items():
                print("  %-28s [%2d] NEIGHBOUR %-28s %r -> set" % (
                    os.path.basename(rel), i, f, by[f][i][:26]))
                by[f][i] = v
        if apply:
            with open(p, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
    print("  written" if apply else "  (dry run -- pass --apply)")


if __name__ == "__main__":
    main("--apply" in sys.argv)
