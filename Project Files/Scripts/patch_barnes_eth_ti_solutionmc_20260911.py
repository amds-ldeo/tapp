#!/usr/bin/env python3
"""Correct five Barnes 2025 ETH Zurich literature cells in Solution MC-ICP-MS (v78 -> v79).

  python3 patch_barnes_eth_ti_solutionmc_20260911.py            # dry run
  python3 patch_barnes_eth_ti_solutionmc_20260911.py --apply

The follow-up that patch_faraday_barnes_solutionmc_20260911.py reported and deliberately did not
make. That script corrected two cells in the same column (Monitored Masses, Collector
Configuration) and found five more that disagree with the ETH passage.

SOURCE. Barnes et al. 2025, Nature Astronomy 9, 1785–1802 (EPMA/ folder). The paper describes two
Ti procedures back to back: "ETH Zurich." (p.7–8), then "LLNL." (p.8). Every value below was read
from the PDF in reading-order text (PyMuPDF `get_text()`) in the session that wrote this script,
and carries its PDF page. `pdftotext -layout` was not used: it interleaves the two columns.

WHAT WENT WRONG. Three of the five cells had borrowed from outside the ETH passage:
  * Integration Time per Cycle read "4 s", LLNL's value ("50 cycles with 4 s integration time
    each", p.8). ETH used 8.39 s and 4.19 s for its two cup configurations (p.8).
  * Analytical Accuracy quoted "±0.16 and ±0.26 ε50Ti". ±0.16 is ETH's ε50Ti; ±0.26 is LLNL's
    ("16 analyses of BCR-2 and BHVO-2 are ±0.29 ε46Ti, ±0.16 ε48Ti and ±0.26 ε50Ti", p.8). Its
    quoted phrase "under conditions similar to the methods used" is from neither Ti procedure: it
    is the ion-chromatography section's comparison of water extractions ("done under conditions
    similar to the methods used for Bennu", p.8). One cell, three sources.
The other three were incomplete rather than borrowed:
  * Reported Variables and Units and Isotope Ratio Reported gave only ε50Ti / 50Ti; the paper
    reports εiTi "where i refers to the isotope masses 46Ti, 48Ti and 50Ti" (p.8).
  * Mass Bias Correction Strategy gave only bracketing; the data were first normalised internally
    to 49Ti/47Ti = 0.749766 with the exponential law (p.8).

WHAT CHANGES — five literature cells, one column. Literature columns are TAPP-owned: Columns A–E
and I of Integration Time per Cycle (Module_MCICPMS), Reported Variables and Units (Module_Core)
and Analytical Accuracy (Module_ICPMS) belong to modules, but literature columns do not, so
composition cannot revert these edits. Isotope Ratio Reported and Mass Bias Correction Strategy
are TAPP-owned outright. No field, tier, data type, description or `Keyed By` value changes.
"""

import csv, io, json, os, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from superseded_readme import write_skeleton

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REL  = "Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v78.csv"
NEW  = "Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v79.csv"
DATE = "2026-09-11"
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
KEY  = "Barnes+etal2025 | ETH"

# (field, guard on the old value, new value). A guard is either the exact old value or
# ("contains", fragment); the script refuses if any old value is not what was read.
EDITS = [
("Integration Time per Cycle", "4 s",
 "8.39 s for the first cup configuration and 4.19 s for the second — \"A sample measurement "
 "consisted of 40 cycles with 8.39 s integration time for the first configuration and 4.19 s for "
 "the second\" (p.8). The 4 s in the same paper is the LLNL procedure's (p.8), not this one"),
("Reported Variables and Units", "ε50Ti",
 "ε46Ti, ε48Ti and ε50Ti (parts per 10^4) relative to an in-house Alfa Aesar Ti wire standard, "
 "εiTi = [(iTi/47Ti)sample/(iTi/47Ti)standard − 1] × 10^4, \"where i refers to the isotope masses "
 "46Ti, 48Ti and 50Ti\" (p.8)"),
("Isotope Ratio Reported", "50Ti",
 "46Ti/47Ti, 48Ti/47Ti, 50Ti/47Ti — εiTi is defined on iTi/47Ti \"where i refers to the isotope "
 "masses 46Ti, 48Ti and 50Ti\" (p.8)"),
("Mass Bias Correction Strategy", "Standard-sample bracketing",
 "Internal normalization to 49Ti/47Ti = 0.749766 using the exponential law, plus bracketing "
 "against an in-house Alfa Aesar Ti wire standard — \"the isotope data were normalized to a "
 "49Ti/47Ti ratio of 0.749766 (ref. 72), using the exponential law\"; results reported \"applying "
 "the sample–standard bracketing method\" (p.8)"),
("Analytical Accuracy and Assessment Method", ("contains", "±0.26 ε50Ti"),
 "BHVO-2 and the Agua Zarcas (CM2) chondrite analysed alongside Bennu — \"To verify the accuracy "
 "and reproducibility of these measurements, the terrestrial rock standard BHVO-2 and the Agua "
 "Zarcas (CM2) chondrite were analysed alongside the Bennu sample. The analytical uncertainties of "
 "9 analyses of BHVO-2 are ±0.17 ε46Ti, ±0.09 ε48Ti and ±0.16 ε50Ti (2 s.d.)\" (p.8). No accepted "
 "values or offsets are stated. The ±0.26 ε50Ti in the same paper is the LLNL procedure's (16 "
 "analyses of BCR-2 and BHVO-2, p.8), not this one"),
]


def col(header, key):
    parts = [p.strip().lower() for p in key.split("|")]
    hits = [i for i, h in enumerate(header) if all(p in " ".join(h.split()).lower() for p in parts)]
    if len(hits) != 1:
        raise SystemExit("column key %r matched %d columns" % (key, len(hits)))
    return hits[0]


def ok(old, guard):
    return guard[1] in old if isinstance(guard, tuple) else old == guard


def main(apply=False):
    rows = list(csv.reader(io.open(os.path.join(ROOT, REL), newline="", encoding="utf-8-sig")))
    h = rows[0]
    lit0 = h.index("Literature Assessment")
    j = col(h, KEY)
    if j <= lit0:
        raise SystemExit("%s is not a literature column" % KEY)
    for field, guard, new in EDITS:
        r = next(r for r in rows[1:] if r and r[0].strip() == field)
        old = r[j].strip()
        if not ok(old, guard):
            raise SystemExit("REFUSING: %s / %s holds %r, not what was read" % (field, KEY, old[:90]))
        r[j] = new
        print("  %-42s\n      was: %s\n      now: %s" % (field, old[:110], new[:110]))
    print("\n  %d cell(s) changed in %s" % (len(EDITS), h[j]))
    if not apply:
        print("(dry run — pass --apply to write)")
        return 0

    with io.open(os.path.join(ROOT, NEW), "w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(rows)
    subprocess.run([sys.executable, XLSX, os.path.join(ROOT, NEW)], cwd=ROOT, check=True,
                   capture_output=True, text=True)
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE)
    os.makedirs(sup, exist_ok=True)
    old = os.path.join(ROOT, REL)
    for f in (old, old[:-4] + ".xlsx"):
        if os.path.exists(f):
            shutil.move(f, os.path.join(sup, os.path.basename(f)))
    reg_p = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(open(reg_p, encoding="utf-8"))
    e = next(e for e in reg["composed"] if e["tapp"] == REL)
    e["tapp"] = NEW                          # or compose_tapp edits the superseded copy
    with open(reg_p, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    p = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts",
                        "sync_current_tapps.py"), "--apply"], cwd=ROOT, capture_output=True, text=True)
    print("  wrote %s; parked %s; registry advanced; mirror: %s"
          % (os.path.basename(NEW), os.path.basename(REL),
             (p.stdout.strip().splitlines() or ["synced"])[-1][:80]))
    write_skeleton(ROOT, DATE)               # after the sync: it reads successors from the mirror
    return 0


sys.exit(main("--apply" in sys.argv))
