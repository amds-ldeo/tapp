#!/usr/bin/env python3
"""Lab-XCT: assess Sample Preparation Method, retire Sample Preparation Notes (Lab-XCT v46 -> v47, 2026-09-30).

    python3 "Project Files/Scripts/labxct_retire_prep_notes_20260930.py" [--apply]

Sample Preparation Method (Module_Core; keyed `sample`) was added to Lab-XCT on 2026-08-27 to hold the
preparation forms that had been squeezed into the TAPP-local free-text Sample Preparation Notes, but its
14 literature cells were left `N`. Every value below was re-read from the source PDF on 2026-09-30.
`sample` is session-only, so under 7.3.3 each cell is one value plus ` — ` commentary; Richard C-I
names its samples in the commentary (the Seifert+2026 precedent).

With Method filled, Notes had nothing left: forms and preparation steps are Method's (Core's description
covers "the preparation that brought it to that form"), holders and containment are Sample Mounting
Method's, and post-scan steps were outside Notes' own "before scanning" scope. The user decided on
2026-09-30 to retire it, to narrow Method's Column F to forms (the two holder terms duplicated Sample
Mounting Method's vocabulary), and to carry the two containment facts into Sample Mounting Method.

Module-owned columns (A-E, I of Method) are untouched; only consumer-owned F, H and literature cells move.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-30"

METHOD, NOTES, MOUNT = "Sample Preparation Method", "Sample Preparation Notes", "Sample Mounting Method"

OLD_F = ("Bulk specimen or fragment (as received) | Core or trimmed billet | Powder or crushed split | "
         "Mounted in tube, straw or pipette tip | Sealed or bagged for containment | "
         "Polished block or epoxy mount | N/A | None")
NEW_F = ("Bulk specimen or fragment (as received) | Separated grain or crystal | Core or trimmed billet | "
         "Powder or crushed split | Polished section or chip | Polished block or epoxy mount | N/A | None")

# header first line -> Method cell, in column order. Richard B appears twice (whole-sample + ROI scan).
METHOD_CELLS = [
    ("Eckley 2024", "N"),       # the scan record gives only "Sample type: Asteroid Bennu particle"
    ("Genge et al. 2025", "Bulk specimen or fragment — \"The sample was decanted for Nano-XCT. During the "
     "mounting process the sample split into two along fractures (parts A and B)\" (p.7); resin embedding "
     "and polishing followed XCT (\"After nano-XCT analysis the sample was embedded in a Specifix resin\", p.7)"),
    ("Neuman et al. 2025 /", "Bulk specimen or fragment — drive tube scanned unopened: \"Prior to opening and "
     "processing, Apollo drive tubes 73001 and 73002 were transported to the UTCT Facility\" (Shearer et al. "
     "2024, p.27); \"NASA curators removed the stainless-steel outer sleeve of 73002 and triple sealed the "
     "aluminum inner sleeve in teflon\" (Neuman et al. 2025, p.4)"),
    ("Neuman et al. 2025", "Bulk specimen or fragment — drive tube scanned unopened; \"It was thus decided to "
     "leave the core in its stainless steel outer sleeve for scanning\" (pp.4–5)"),
    ("Shearer et al. 2024", "Bulk specimen or fragment — core scanned inside the unopened 73001 CSVC: \"Before "
     "piercing and gas extraction of the 73001 CSVC, an XCT scan of the bottom portion was collected\" (p.26); "
     "Fig. 7 shows the core \"still within the CSVC\" (p.27)"),
    ("Shearer et al. 2024", "Bulk specimen or fragment (as received) — extracted particles >4 mm \"are "
     "individually bagged and XCT scanned for classification and characterization without destructive "
     "chipping, sectioning, or dust removal\" (p.26)"),
    ("Tomkinson et al. 2015", "Bulk specimen or fragment — \"a single 2.7 g chip\" (p.3), characterised "
     "\"Prior to destructive sampling\" (p.3); \"The entire 2.7 g chip was scanned by XCT\" (p.6)"),
    ("Glavin et al. 2023", "Powder or crushed split — chips \"lightly crushed by hand\", then \"further ground "
     "down by hand with a pestle until no visible fragments could be observed\", vortex mixed 3 min and "
     "\"split into two approximately equal mass portions\" (p.3); Murchison B (4.6430 g) was scanned"),
    ("Nascimento-Dias", "Bulk specimen or fragment — \"fragments of about 4 mm of both meteorites were "
     "analyzed through X-ray micro-CT\" (p.5)"),
    ("Richard et al. 2019", "Separated grain or crystal — \"a single olivine phenocryst (1.0 mm large) "
     "separated from Sample A\" (p.2); epoxy mounting \"carried out after HRXCT analysis\" (Fig. 1, p.4)"),
    ("Richard et al. 2019", "Bulk specimen or fragment (as received) — Sample B, a 3 × 5 × 2 cm synthetic "
     "quartz monocrystal: \"No sectioning was carried out prior to HRXCT scanning\" (p.2)"),
    ("Richard et al. 2019", "Bulk specimen or fragment (as received) — Sample B, a 3 × 5 × 2 cm synthetic "
     "quartz monocrystal: \"No sectioning was carried out prior to HRXCT scanning\" (p.2)"),
    ("Richard et al. 2019", "Polished section or chip; Bulk specimen or fragment (as received) — varies by "
     "sample. C: quartz lamella \"doubly polished to reach a 0.4 mm thickness for optical microscopy and HRXCT "
     "analyses\" (p.2). D, E: \"No sectioning was carried out prior to HRXCT scanning\", each scanned entirely "
     "(p.6). F: \"a chip (3×4×0.2 mm) of a doubly polished thick section\" (p.6). G, H: \"chips (5×5×0.5 mm) of "
     "doubly polished thick sections\" (p.6). I: \"a chip (3×4×0.15 mm) of a doubly polished thick section\" (p.7)"),
    ("Tait 2014", "Core or trimmed billet — \"An 8 mm diameter core was drilled from the Watson 012 sample "
     "and then scanned\" (p.9)"),
]

# Sample Mounting Method: literature column (1-based after the sentinel) -> (expected old, new)
MOUNT_CELLS = {
    4: ("Custom PVC tube", "Custom PVC tube; core left in its stainless-steel outer sleeve — \"It was thus "
        "decided to leave the core in its stainless steel outer sleeve for scanning. The core was positioned "
        "for scanning in a custom PVC tube mount\" (Neuman et al. 2025, pp.4–5)"),
    5: ("N", "Sealed container (the unopened 73001 CSVC); stage holder N — \"Before piercing and gas "
        "extraction of the 73001 CSVC, an XCT scan of the bottom portion was collected\" (p.26); Fig. 7 "
        "shows the core \"still within the CSVC\" (p.27)"),
}


def rows_of(p):
    return list(csv.reader(io.open(p, newline="", encoding="utf-8-sig")))


def write(p, rows):
    with io.open(p, "w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(rows)


def flags(mods):
    o = []
    for m in mods:
        s = m["name"]
        if m.get("blocks"):
            s += ":" + (m["blocks"] if isinstance(m["blocks"], str) else ",".join(m["blocks"]))
        o += ["--module", s]
    return o


def edit(rr):
    rr = [list(r) for r in rr]
    h = rr[0]; s = h.index("Literature Assessment"); lit = list(range(s + 1, len(h)))
    idx = {r[0]: i for i, r in enumerate(rr) if r and r[0]}
    for f in (METHOD, NOTES, MOUNT):
        if f not in idx:
            raise SystemExit("PREMISE: %s missing" % f)
    if len(lit) != len(METHOD_CELLS):
        raise SystemExit("PREMISE: %d literature columns, expected %d" % (len(lit), len(METHOD_CELLS)))
    m = rr[idx[METHOD]]
    if m[5] != OLD_F:
        raise SystemExit("PREMISE: Method Column F changed:\n%r" % m[5])
    if any(m[j] != "N" for j in lit):
        raise SystemExit("PREMISE: Method literature cells are no longer all N")
    for j, (hdr, val) in zip(lit, METHOD_CELLS):
        if h[j].split("\n")[0] != hdr:
            raise SystemExit("PREMISE: column %d header %r, expected %r" % (j, h[j].split("\n")[0], hdr))
        m[j] = val
    m[5] = NEW_F; m[7] = DATE
    mt = rr[idx[MOUNT]]
    for k, (old, new) in MOUNT_CELLS.items():
        if mt[s + k] != old:
            raise SystemExit("PREMISE: Mounting cell %d is %r, expected %r" % (k, mt[s + k], old))
        mt[s + k] = new
    mt[7] = DATE
    del rr[idx[NOTES]]
    return rr


def main(apply=False):
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    e = next(x for x in reg["composed"] if os.path.basename(x["tapp"]).startswith("Lab-XCT_TAPP_v"))
    rel = e["tapp"]; new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), rel)
    old = rows_of(os.path.join(ROOT, rel)); rr = edit(old)
    print("  %s -> %s: %d -> %d rows" % (os.path.basename(rel), os.path.basename(new), len(old), len(rr)))
    o = {r[0]: r for r in old if r and r[0]}; n = {r[0]: r for r in rr if r and r[0]}
    ch = [(f, j) for f in n for j in range(len(n[f])) if o[f][j] != n[f][j]]
    for f in sorted({c[0] for c in ch}):
        cols = [old[0][j].split("\n")[0] if j > 8 else "ABCDEFGHI"[j] for g, j in ch if g == f]
        print("  %-24s %2d cells: %s" % (f, len(cols), ", ".join(cols)))
    print("  removed rows: %s" % sorted(set(o) - set(n)))
    if not apply:
        print("\n(dry run — pass --apply to write)"); return 0
    np_ = os.path.join(ROOT, new)
    q = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)] + flags(e["modules"])
                       + ["--out", np_], cwd=ROOT, capture_output=True, text=True)
    if q.returncode != 0:
        raise SystemExit("compose failed\n%s\n%s" % (q.stdout[-1500:], q.stderr[-700:]))
    write(np_, edit(rows_of(np_)))
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE)
    os.makedirs(sup, exist_ok=True)
    for f in (os.path.join(ROOT, rel), os.path.join(ROOT, rel)[:-4] + ".xlsx"):
        shutil.move(f, os.path.join(sup, os.path.basename(f)))
    q = subprocess.run([sys.executable, XLSX, np_], cwd=ROOT, capture_output=True, text=True)
    if q.returncode != 0:
        raise SystemExit("xlsx failed\n%s" % q.stderr[-700:])
    rp = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(io.open(rp, encoding="utf-8"))
    for x in reg["composed"]:
        if x["tapp"] == rel:
            x["tapp"] = new
    with io.open(rp, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    for s in ("build_module_register.py", "sync_current_tapps.py", "build_schema_spec_counts.py"):
        q = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", s), "--apply"],
                           cwd=ROOT, capture_output=True, text=True)
        print("  %s: %s" % (s, (q.stdout.strip().splitlines() or ["ok"])[-1][:90]))
    return 0


sys.exit(main("--apply" in sys.argv))
