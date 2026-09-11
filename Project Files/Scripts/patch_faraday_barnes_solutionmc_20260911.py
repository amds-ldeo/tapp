#!/usr/bin/env python3
"""Correct six Solution MC-ICP-MS literature cells against the source PDFs (v76 -> v77).

  python3 patch_faraday_barnes_solutionmc_20260911.py            # dry run
  python3 patch_faraday_barnes_solutionmc_20260911.py --apply

Found while checking amds-ldeo/tapp#6 (whether Solution MC genuinely lacks `Detector
Configuration`), which meant reading every Solution MC paper for its detector description.

SOURCE RULE. Every value below was read from the PDF in the session that wrote this script, in
reading-order text (PyMuPDF), and carries its PDF page. `pdftotext -layout` was NOT used for
quoting: it interleaves the two columns of a journal page, which is how the Barnes-ETH cell below
came to splice two sentences.

WHAT CHANGES — literature columns only. Columns A–E and I of `Faraday Cup Array Configuration` and
`Collector Configuration` are owned by Module_MCICPMS; literature columns are not, so composition
cannot revert these edits.

  Faraday Cup Array Configuration — the field asks for the number of Faraday cups and whether an
  ion counter is present.
    * Craddock 2008 — was `N`; the paper states "equipped with nine Faraday Cups" (p.3).
    * Nowell 2008, Nu Plasma (NIGL) — was `N`; the paper states a "7 Faraday 'U–Pb' collector
      block" (p.4).
    * Nie 2019 — was "Three collectors used", which is how many collectors the procedure USED
      (that belongs in `Collector Configuration`, which already holds it). The paper states the
      array: "equipped with nine Faraday collectors" (p.8).
    * Nowell 2008, Neptune (Durham) — quote kept, page added, and the SEM ion counter the same
      paper uses for abundance sensitivity (p.3) recorded; the field asks for its presence.

  Barnes 2025, ETH Zurich (Ti) — the paper describes two Ti procedures back to back, ETH then LLNL.
    * Monitored Masses — the cell quoted "all five Ti isotopes as well as 44Ca, 45Sc, 51V, 52Cr and
      53Cr were collected in one line", a sentence that does not exist: it joins ETH's opening to
      LLNL's Neoma setup. 45Sc is LLNL's. ETH used two configurations (p.8).
    * Collector Configuration — held only the opening clause; now lists both configurations.

LEFT AS `N`, deliberately. Hopp, Schönbächler, Barnes-ETH and Ibáñez-Mejía name the cups the
masses were measured on but never describe the array; workflow.md's inference rule applies.

NOT FIXED HERE, reported instead: four further Barnes-ETH cells disagree with the ETH passage
(Integration Time per Cycle, Reported Variables and Units, Isotope Ratio Reported, Mass Bias
Correction Strategy); a fifth (Analytical Accuracy) cites a value not found in it.
"""

import csv, io, json, os, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from superseded_readme import write_skeleton

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REL  = "Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v76.csv"
NEW  = "Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v77.csv"
DATE = "2026-09-11"
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")

# (field, column key, guard on the old value, new value). A guard is either the exact old value
# or ("contains", fragment); the script refuses if any old value is not what was read.
EDITS = [
("Faraday Cup Array Configuration", "Craddock+etal2008", "N",
 "Nine Faraday cups — \"equipped with nine Faraday Cups\" (p.3); Table 1 gives detection system "
 "\"Faraday cups\" and acquisition mode \"Static, analogue detectors\" (p.3). No ion counter stated"),
("Faraday Cup Array Configuration", "Nowell+etal2008 | Nu Plasma", "N",
 "Seven Faraday cups — \"fitted with a 7 Faraday ‘U–Pb’ collector block and 10^11 Ω resistor "
 "amplifiers which permitted maximum beam sizes of 10 V per channel\" (p.4). No ion counter stated"),
("Faraday Cup Array Configuration", "Nie+Dauphas2019", "Three collectors used",
 "Nine Faraday collectors — \"The MC-ICPMS at the University of Chicago is equipped with nine "
 "Faraday collectors\" (p.8). No ion counter stated"),
("Faraday Cup Array Configuration", "Nowell+etal2008 | Neptune", ("contains", "The Durham Neptune has a 9 Faraday collector array"),
 "\"The Durham Neptune has a 9 Faraday collector array equipped with 10^11 Ω resistor amplifiers "
 "which allow a maximum beam of 50 V per channel\" (p.3). An SEM ion counter is also present — "
 "abundance sensitivity \"was determined by scanning the low mass tail of a 30 V 192Os beam using "
 "the SEM\" (p.3); its position is not stated"),
("Monitored Masses", "Barnes+etal2025 | ETH", ("contains", "45Sc"),
 "⁴⁶Ti, ⁴⁷Ti, ⁴⁸Ti, ⁴⁹Ti, ⁵⁰Ti (Ti); ⁴⁴Ca, ⁵¹V, ⁵²Cr, ⁵³Cr (interference monitors, no target "
 "species) — \"Titanium isotopes were collected in two cup configurations. First, all five Ti "
 "isotopes and 44Ca were measured enabling correction of the Ca interference on 46Ti and 48Ti. The "
 "second configuration included 49Ti, 50Ti, 51V, 52Cr and 53Cr to correct for isobaric interferences "
 "from V and Cr on 50Ti\" (p.8). ⁴⁵Sc belongs to the LLNL procedure in the same paper, not this one"),
("Collector Configuration", "Barnes+etal2025 | ETH", "\"Titanium isotopes were collected in two cup configurations\"",
 "Two cup configurations: (1) ⁴⁶Ti–⁵⁰Ti and ⁴⁴Ca; (2) ⁴⁹Ti, ⁵⁰Ti, ⁵¹V, ⁵²Cr, ⁵³Cr — \"Titanium "
 "isotopes were collected in two cup configurations\" (p.8). Cup positions are not stated"),
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
    for field, key, guard, new in EDITS:
        j = col(h, key)
        if j <= lit0:
            raise SystemExit("%s is not a literature column" % key)
        r = next(r for r in rows[1:] if r and r[0].strip() == field)
        old = r[j].strip()
        if not ok(old, guard):
            raise SystemExit("REFUSING: %s / %s holds %r, not what was read" % (field, key, old[:90]))
        r[j] = new
        print("  %-32s %-28s\n      was: %s\n      now: %s" % (field, key, old[:110], new[:110]))
    print("\n  %d cell(s) changed" % len(EDITS))
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
    print("  wrote %s; parked v76; registry advanced; mirror: %s"
          % (os.path.basename(NEW), (p.stdout.strip().splitlines() or ["synced"])[-1][:80]))
    write_skeleton(ROOT, DATE)               # after the sync: it reads successors from the mirror
    return 0


sys.exit(main("--apply" in sys.argv))
