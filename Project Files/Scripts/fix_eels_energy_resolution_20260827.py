#!/usr/bin/env python3
"""Re-extract the two mis-filed `EELS Energy Resolution` literature cells (TEM).

Both held an Fe-valence determination METHOD in a field typed `Numeric (eV FWHM)`:

  Cymes2023 (Nion UltraSTEM200-X)  "Integral white-line intensity ratio I(L3)/I(L2) -> Van Aken
                                    & Liebscher (2002) ... MLLS fitting of Fe L2,3 ELNES ..."
  Mo2022    (Hitachi HF5000)       "Peak position and lineshape comparison to reference standards
                                    (qualitative Fe valence state determination: Fe0, Fe2+, Fe3+)"

Re-read from the sources in TEM/:

  Mo et al. 2022, methods: "the energy resolution at the zero-loss peak was 0.5-0.7 eV FWHM"
      -> attested, record as reported.
  Cymes et al. 2023, "STEM, EDS, and EELS Measurements": names the instrument and detectors but
      defers collection details to the supporting information ("see supporting information for
      EELS and EDS collection details, Fig. S1"). No energy resolution in the accessible text.
      -> `N` per lit_assessment.md: applicable to the procedure, not directly stated.
      NOT `N/A` -- both procedures used EELS, so the concept plainly applies.

The displaced valence-method text is NOT relocated here: no TEM field holds an ELNES chemical-state
determination method. That gap is reported, not silently filled.
"""
import csv, json, os, re, shutil, subprocess, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
DATE = "2026-08-27"
FIELD = "EELS Energy Resolution"
FIX = {
    "Cymes2023 | Apollo 17 soil 71501 pyroxene (1pyx + 2pyx) | HAADF-STEM + Dual EELS + EDS (NRL Nion UltraSTEM200-X)": "N",
    "Mo2022 | Chang'E-5 lunar soil CE5C0400YJFM00505 | TEM-EELS (Shanghai Institute of Ceramics CAS Hitachi HF5000)": "0.5–0.7",
}

def main(apply=False):
    reg = json.load(open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    entry = next(e for e in reg["composed"] if os.path.basename(e["tapp"]).startswith("TEM_"))
    rel = entry["tapp"]
    rows = list(csv.reader(open(os.path.join(ROOT, rel), newline="", encoding="utf-8-sig")))
    hdr = rows[0]; upd = hdr.index("Last Update")
    row = next(r for r in rows[1:] if r and r[0].strip() == FIELD)
    n = 0
    for col, new in FIX.items():
        if col not in hdr:
            raise SystemExit("column not found: %r" % col[:60])
        i = hdr.index(col)
        while len(row) <= i: row.append("")
        print("  [%s]\n     was: %s\n     now: %s\n" % (col[:60], row[i][:95], new))
        row[i] = new; n += 1
    if n != 2: raise SystemExit("expected 2 fixes, made %d" % n)
    while len(row) <= upd: row.append("")
    row[upd] = DATE

    newrel = re.sub(r"_v(\d+)\.csv$", lambda m: "_v%d.csv" % (int(m.group(1)) + 1), rel)
    print("  %s -> %s" % (os.path.basename(rel), os.path.basename(newrel)))
    if not apply:
        print("(dry run — pass --apply to write)"); return

    with open(os.path.join(ROOT, newrel), "w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(rows)
    entry["tapp"] = newrel; reg["generated"] = DATE
    with open(os.path.join(ROOT, "composed_tapps.json"), "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    cv = os.path.join(ROOT, "Project Files", "Registers & Planning", "TAPP_Composed_Variants.csv")
    if os.path.exists(cv):
        crows = list(csv.reader(open(cv, newline="", encoding="utf-8-sig")))
        ob, nb = os.path.basename(rel), os.path.basename(newrel)
        for r in crows[1:]:
            for i, c in enumerate(r):
                if ob in c: r[i] = c.replace(ob, nb)
        with open(cv, "w", newline="", encoding="utf-8-sig") as fh: csv.writer(fh).writerows(crows)
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    old = os.path.join(ROOT, rel); shutil.move(old, os.path.join(sup, os.path.basename(old)))
    x = old[:-4] + ".xlsx"
    if os.path.exists(x): shutil.move(x, os.path.join(sup, os.path.basename(x)))
    gen = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
    r = subprocess.run([sys.executable, gen, newrel], cwd=ROOT, capture_output=True, text=True)
    print("  xlsx:", (r.stdout.strip().splitlines() or ["(none)"])[-1][:80])
    s = os.path.join(ROOT, "Project Files", "Scripts", "sync_current_tapps.py")
    r = subprocess.run([sys.executable, s, "--apply"], cwd=ROOT, capture_output=True, text=True)
    print("  mirror:", (r.stdout.strip().splitlines() or ["synced"])[-1][:80])

if __name__ == "__main__":
    main("--apply" in sys.argv)
