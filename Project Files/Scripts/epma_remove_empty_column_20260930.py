#!/usr/bin/env python3
"""EPMA: remove the empty, unheaded literature column before Neuman+2025 (EPMA v86 -> v87, 2026-09-30).

    python3 "Project Files/Scripts/epma_remove_empty_column_20260930.py" [--apply]

EPMA v86 carried a literature column with an empty header and no content in any row, between
Barnes+2025 (NHM London) and Neuman+2025. It described no procedure; it rendered as a blank column in
the xlsx and shifted Neuman+2025 to column index 30. No field content changes. The Neuman+2025 header,
which alone among the headers is split over three lines, is rewritten onto one line with the ` | `
separators the others use. The user decided the removal on 2026-09-30.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-30"


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
    h = rr[0]; s = h.index("Literature Assessment")
    drop = [j for j in range(s + 1, len(h)) if not h[j].strip()]
    if len(drop) != 1:
        raise SystemExit("PREMISE: expected 1 unheaded literature column, found %d" % len(drop))
    j = drop[0]
    full = [r for r in rr[1:] if len(r) > j and r[j].strip()]
    if full:
        raise SystemExit("PREMISE: the unheaded column is not empty (%d cells)" % len(full))
    out = [[c for k, c in enumerate(r) if k != j] for r in rr]
    for k, c in enumerate(out[0]):
        if c.startswith("Neuman+2025") and "\n" in c:
            out[0][k] = " | ".join(x.strip(" |") for x in c.split("\n"))
    return out


def main(apply=False):
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    e = next(x for x in reg["composed"] if os.path.basename(x["tapp"]).startswith("EPMA_TAPP_v"))
    rel = e["tapp"]; new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), rel)
    old = rows_of(os.path.join(ROOT, rel)); rr = edit(old)
    s = rr[0].index("Literature Assessment")
    print("  %s -> %s: %d -> %d columns, %d literature columns" % (os.path.basename(rel), os.path.basename(new),
          len(old[0]), len(rr[0]), len(rr[0]) - s - 1))
    print("  headers:", [h.split(" | ")[0] for h in rr[0][s + 1:]])
    if not apply:
        print("\n(dry run — pass --apply to write)"); return 0
    np_ = os.path.join(ROOT, new)
    q = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)] + flags(e["modules"])
                       + ["--out", np_], cwd=ROOT, capture_output=True, text=True)
    if q.returncode != 0:
        raise SystemExit("compose failed\n%s\n%s" % (q.stdout[-1500:], q.stderr[-700:]))
    write(np_, edit(rows_of(np_)))
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE)
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
