#!/usr/bin/env python3
"""Re-express the 9 `Digestion Step` literature cells that the re-type left holding a count.

Integer -> Text (free) makes a bare count the wrong content: the cell must now name the members the
consumers hang values on. Every replacement below is drawn from the SAME TAPP's neighbouring
`Digestion Acid(s)` / `Digestion Temperature` / `Digestion Duration` cells -- no paper was re-read in
this pass -- and applies Column B's new grain rule: an evaporation carrying no attack of its own is
part of the step it follows, and an identical attack repeated on the residue is a repeat, not a new
step. Where the neighbouring cells cannot settle the grain, the cell says so rather than guessing.
"""
import csv, os, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
FIELD = "Digestion Step"

EDITS = {
 "Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v70.csv": {
  "Hu+etal2022": (
    "Not settled by the source as extracted: \"These steps were performed twice\" (recorded under "
    "Digestion Acid(s)) may be one HCl-HNO3 (2:1) hot-plate attack repeated on the residue -- a repeat "
    "under the 2026-09-08 grain rule -- or two distinct attacks. Needs re-reading; flagged 2026-09-08."),
  "Nie+Dauphas2019": (
    "1: 4 ml 28 M HF + 2 ml 15 M HNO3 + 1 ml 10 M HClO4 | 2: not stated | 3: not stated. The paper "
    "numbers three steps of concentrated HF-HNO3-HCl-HClO4 but gives the composition only of step (i)."),
  "Schönbächler+etal2025": (
    "Main route 1: concentrated HF-HNO3 | 2: HNO3-HCl | 3: HNO3-H2O2. Ivuna high-PT route 1: "
    "concentrated HF-HNO3, 3 days | 2: concentrated HCl, 2 days."),
 },
 "Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v76.csv": {
  "Hu+Gao2008": (
    "1: concentrated HNO3 (1 ml) + concentrated HF (1 ml), bomb 190 deg C / 48 h | 2: HNO3 (1.5 ml) + "
    "ultra-pure water (2.5 ml), bomb 150 deg C overnight. The paper numbers five operations (section "
    "3.3); the two intervening HNO3 fumings to dryness carry no attack of their own and are part of "
    "step 1 under the 2026-09-08 grain rule. This cell previously read \"2\" beside \"five steps "
    "explicitly numbered\" -- the contradiction an Integer definer could not resolve."),
  "Yu+etal2005": (
    "1: ambient dissolution in 0.075 M HNO3 (section 2). A single attack, though the paper does not "
    "describe it as a digestion -- Digestion Acid(s) records N/A on that reading."),
  "LopezGarcia+etal2026": (
    "1: 0.2 mL HF + 0.1 mL HNO3 + 0.4 mL water | 2: 0.2 mL HNO3 + 0.2 mL HCl + 0.2 mL H2O2 | 3: 0.2 mL "
    "HNO3 + 0.2 mL H2O2. The paper describes four heating stages; on the recorded acid mixtures these "
    "span three distinct attacks, the remaining stages being evaporation and uptake within a step."),
 },
 "Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v72.csv": {
  "Li+etal2016": (
    "1: 6 M HCl (1.5 ml) + 8 M HNO3 (0.5 ml), 130 deg C / 48 h | 2: evaporation then re-dissolution in "
    "10 M HCl (1.5 ml). Step 2 changes the acid, so it is a distinct attack rather than an evaporation "
    "belonging to step 1 (section 2.3.1)."),
  "Misra+etal2014": (
    "1: 1 M HNO3, minimum volume for dissolution, ambient (section 2.4)."),
 },
}


def main(apply=False):
    for rel, edits in EDITS.items():
        p = os.path.join(ROOT, rel)
        rows = list(csv.reader(open(p, newline="", encoding="utf-8-sig")))
        h = rows[0]
        row = next(r for r in rows[1:] if r and r[0].strip() == FIELD)
        done = set()
        for i, col in enumerate(h):
            for tag, txt in edits.items():
                if col.startswith(tag):
                    print("  %-34s %-24s %s" % (os.path.basename(rel), tag, repr(row[i])[:52]))
                    row[i] = txt; done.add(tag)
        missing = set(edits) - done
        if missing:
            raise SystemExit("%s: no column matched %s" % (rel, missing))
        if apply:
            with open(p, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
    print("  (dry run)" if not apply else "  written")


if __name__ == "__main__":
    main("--apply" in sys.argv)
