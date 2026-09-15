#!/usr/bin/env python3
"""Split `Sampling Unit` into `Sampling Unit Type` and `Sampling Unit Name` (Module_Core v7 -> v8).

    python3 "Project Files/Scripts/split_sampling_unit_20260915.py" [--apply]

amds-ldeo/tapp#8. Design, evidence and the five decisions (D1-D5, all taken as recommended):
`Project Files/Design Notes/Proposal_Sampling_Unit_Identity_2026-09-15.md`.

THE DEFECT. `Sampling Unit` was keyed `defines: sampling unit` while its values are TYPES (Grain | Spot
| Phase ...). A type cannot list the members of a domain (7.4a), so the 46 field-instances keyed
`sample > sampling unit` had child tables with no rows to attach to, and nothing tied a unit to its
sample. Rule 9 had meant the one field to carry both the type (procedure) and the units (analysis);
one D=Basic cell cannot hold both, and the sentence saying so was deleted on 2026-08-25.

WHAT THIS DOES, per TAPP (all 16, the field being Core-owned and universal):
  * renames the row `Sampling Unit` -> `Sampling Unit Type` BEFORE composing (compose matches rows by
    name, so a renamed module field would otherwise be ADDED beside the old row — see
    bump_samplingunitselection_20260901.py); the type's literature cells travel with the row;
  * composes, which re-keys it `(none)`, sets D=Read-Only (D3) and inserts `Sampling Unit Name`
    (`defines: sample > sampling unit`, D1; C=N/A, D=Basic, Text (free));
  * moves the new row to immediately after the type (the blocks path appends at group end), fills its
    Column F example and Column J purpose (composition fills neither on an inserted row), and stamps
    Last Update on both rows. Its literature cells stay blank: never asked (Phase 3 backlog).

The 46 consumers are not touched. Their key `sample > sampling unit` now resolves to a definer that
lists the domain and carries each unit's parent sample.
"""

import csv, io, json, os, re, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from superseded_readme import write_skeleton

ROOT    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODULES = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-15"
OLD, TYPE, NAME = "Sampling Unit", "Sampling Unit Type", "Sampling Unit Name"

TYPE_ROW = {
    "B": ("The kind of physical subdivision of the sample to which one row of reported values "
          "corresponds — the unit that is analysed and reported, as distinct from the sample as a "
          "whole. Where units nest (e.g. confined tracks within grains), state both levels. The units "
          "themselves are listed in Sampling Unit Name."),
    "C": "Basic", "D": "Read-Only", "E": "Controlled list / Text", "I": "(none)",
}
NAME_ROW = {
    "B": ("The name or label of each sampling unit analysed in this session, as the laboratory records "
          "it, together with the sample it belongs to — e.g. a spot number, a grain label, a map or "
          "region-of-interest name, or an aliquot identifier. Where units are too numerous to name "
          "individually, such as map pixels or reconstructed voxels, name the acquisition area they "
          "belong to instead."),
    "C": "N/A", "D": "Basic", "E": "Text (free)", "I": "defines: sample > sampling unit",
    "F": ("e.g., NWA 8657-1: spots 1–24 | Zircon mount ZM-3: grains Z1–Z30 | Core 73001: map areas "
          "A1–A5 | Bennu aggregate OREX-803015-100: aliquot for Ti"),
    "J": ("Gives every field keyed by sampling unit a row to attach its values to, and ties each unit "
          "to the sample it belongs to; without it those fields collapse to one value per session."),
}
COL = {c: i for i, c in enumerate("ABCDEFGHIJ")}

DECISION = (
    "2026-09-15 v8. `Sampling Unit` split into `Sampling Unit Type` ((none), C=Basic, D=Read-Only) and "
    "`Sampling Unit Name` (defines: sample > sampling unit, C=N/A, D=Basic, Text (free)); "
    "amds-ldeo/tapp#8. The old field was keyed as the definer of `sampling unit` but held types, which "
    "cannot list a domain's members (7.4a), leaving 46 consumer field-instances with no rows and no "
    "link to their sample. Rule 9 had meant one field to carry type and units together; one D=Basic "
    "cell cannot. The containment definer form is new and makes the parent REQUIRED, unlike `per`. "
    "Decisions D1-D5 and evidence: Project Files/Design Notes/Proposal_Sampling_Unit_Identity_2026-09-15.md.")


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


def main(apply=False):
    mcsv = os.path.join(MODULES, "Module_Core.csv")
    mrows = rows_of(mcsv)
    hdr = mrows[0]
    old = [r for r in mrows if r and r[0] == OLD]
    if len(old) != 1 or any(r and r[0] in (TYPE, NAME) for r in mrows):
        raise SystemExit("PREMISE: Module_Core must hold exactly one `Sampling Unit` and no Type/Name row")
    if (old[0][2], old[0][3], old[0][8]) != ("Basic", "Basic", "defines: sampling unit"):
        raise SystemExit("PREMISE: module row is %r" % ([old[0][2], old[0][3], old[0][8]],))
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    plan = []
    for e in reg["composed"]:
        if not any(m["name"] == "Core" for m in e["modules"]):
            continue
        rel = e["tapp"]
        rr = rows_of(os.path.join(ROOT, rel))
        if sum(1 for r in rr if r and r[0].strip() == OLD) != 1 or any(r and r[0].strip() in (TYPE, NAME) for r in rr):
            raise SystemExit("PREMISE: %s does not hold exactly one `Sampling Unit`" % os.path.basename(rel))
        new = re.sub(r"_v(\d+)\.csv$", lambda m: "_v%d.csv" % (int(m.group(1)) + 1), rel)
        plan.append((e, rel, new, len(rr)))
        print("  %-38s -> %s" % (os.path.basename(rel), os.path.basename(new)))
    if len(plan) != 16:
        raise SystemExit("PREMISE: expected 16 Core consumers, found %d" % len(plan))
    mj = os.path.join(MODULES, "Module_Core.json")
    d = json.load(io.open(mj, encoding="utf-8"))
    newver = str(int(d["version"]) + 1)
    print("\n  Module_Core v%s -> v%s: rename + re-key + re-tier 1 field, add 1 field; %d consumers"
          % (d["version"], newver, len(plan)))
    if not apply:
        print("\n(dry run — pass --apply to write)"); return 0

    # --- 1. the module ---------------------------------------------------------------
    i = mrows.index(old[0])
    t = old[0]
    t[0] = TYPE
    for c, v in TYPE_ROW.items():
        t[COL[c]] = v
    t[COL["H"]] = DATE
    n = [""] * len(hdr)
    n[0] = NAME
    for c in ("B", "C", "D", "E", "I", "J"):
        n[COL[c]] = NAME_ROW[c]
    n[COL["H"]] = DATE
    mrows.insert(i + 1, n)
    write(mcsv, mrows)
    for b in d["blocks"]:
        if OLD in b["fields"]:
            k = b["fields"].index(OLD)
            b["fields"][k:k + 1] = [TYPE, NAME]
    d["version"] = newver
    d["decisions"].append(DECISION)
    with io.open(mj, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=4, ensure_ascii=False); fh.write("\n")
    print("  Module_Core written (v%s)" % newver)

    # --- 2. the TAPPs ----------------------------------------------------------------
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    for e, rel, new, nrows in plan:
        src, dst = os.path.join(ROOT, rel), os.path.join(ROOT, new)
        rr = rows_of(src)
        for r in rr:
            if r and r[0].strip() == OLD:
                r[0] = TYPE                                  # rename BEFORE composing
        write(dst, rr)
        q = subprocess.run([sys.executable, COMPOSE, "--source", dst] + flags(e["modules"])
                           + ["--out", dst], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (new, q.stdout[-1500:], q.stderr[-700:]))
        rr = rows_of(dst)
        ti = [k for k, r in enumerate(rr) if r and r[0].strip() == TYPE]
        ni = [k for k, r in enumerate(rr) if r and r[0].strip() == NAME]
        if len(ti) != 1 or len(ni) != 1 or any(r and r[0].strip() == OLD for r in rr):
            raise SystemExit("%s: expected one Type and one Name row and no `Sampling Unit`" % new)
        name_row = rr.pop(ni[0])
        ti = [k for k, r in enumerate(rr) if r and r[0].strip() == TYPE][0]
        rr.insert(ti + 1, name_row)                          # place it directly after the type
        h = rr[0]
        name_row[h.index("Example / Allowed Content")] = NAME_ROW["F"]
        name_row[h.index("Purpose")] = NAME_ROW["J"]
        for r in (rr[ti], name_row):
            r[h.index("Last Update")] = DATE
        if len(rr) != nrows + 1:
            raise SystemExit("%s: row count %d, expected %d" % (new, len(rr), nrows + 1))
        write(dst, rr)
        for f in (src, src[:-4] + ".xlsx"):
            if os.path.exists(f): shutil.move(f, os.path.join(sup, os.path.basename(f)))
        q = subprocess.run([sys.executable, XLSX, dst], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0: raise SystemExit("xlsx failed %s\n%s" % (new, q.stderr[-700:]))
        print("  composed %s" % os.path.basename(new))

    # --- 3. the registry, re-read: compose_tapp --out records compositions itself ------------
    rp = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(io.open(rp, encoding="utf-8"))
    news = {os.path.basename(nw).rsplit("_v", 1)[0]: nw for _, _, nw, _ in plan}
    for e in reg["composed"]:
        stem = os.path.basename(e["tapp"]).rsplit("_v", 1)[0]
        if stem in news:
            e["tapp"] = news[stem]
            for m in e["modules"]:
                if m["name"] == "Core": m["version"] = newver
    reg["generated"] = DATE
    with io.open(rp, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    for s in ("build_module_register.py", "sync_current_tapps.py", "build_schema_spec_counts.py"):
        q = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", s), "--apply"],
                           cwd=ROOT, capture_output=True, text=True)
        print("  %s: %s" % (s, (q.stdout.strip().splitlines() or ["ok"])[-1][:90]))
    write_skeleton(ROOT, DATE)
    return 0


sys.exit(main("--apply" in sys.argv))
