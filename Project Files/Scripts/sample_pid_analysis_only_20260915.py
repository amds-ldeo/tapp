#!/usr/bin/env python3
"""`Sample Persistent Identifier` becomes analysis-only: C Advanced -> N/A (Module_Core v6 -> v7).

    python3 "Project Files/Scripts/sample_pid_analysis_only_20260915.py" [--apply]

WHY. amds-ldeo/tapp#7 (Stephen Richard): the field is C=Advanced / D=Advanced, but it identifies the
samples listed in `Sample Name`, which is C=N/A — "it's coupled to sample name which is analysis
only". Rule 13's own reasoning agrees: C=N/A on `Sample Name` is "correct and deliberate … the
procedure is sample-neutral and specifies nothing about which samples it will be applied to". The
same holds for the samples' identifiers. And the field is typed `URI / IGSN`: a registered procedure
has no sample to hold an IGSN for.

WHAT IS SUPERSEDED. precedents.md recorded C=Advanced (2026-08-08) so that "a procedure may declare
that it expects samples to carry a persistent identifier". That is a policy statement, not an
identifier. A `URI / IGSN` field cannot hold it, and no procedure column in the library ever put one
there. If a procedure-level IGSN policy is wanted, it is a different field.

WHAT CHANGES. Column C only, in the module, reaching all 16 consumers by recomposition. D stays
Advanced (optional at analysis time, since IGSN registration is not universal). C=N/A with D=Advanced
is a legal pair: README §5 maps it to "absent" from the procedure schema, "optional, supplied fresh"
in the analysis schema. Keyed By stays `sample`. Last Update is stamped on the one row.
"""

import csv, io, json, os, re, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from superseded_readme import write_skeleton

ROOT    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODULES = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-15"
FIELD   = "Sample Persistent Identifier"

DECISION = (
    "%s v7. `Sample Persistent Identifier` C Advanced -> N/A; D stays Advanced. amds-ldeo/tapp#7: "
    "the field identifies the samples listed in `Sample Name` (C=N/A), and Rule 13's ground for that, "
    "a sample-neutral procedure, applies equally to their identifiers. Typed `URI / IGSN`, it has "
    "nothing to hold at procedure level. The 2026-08-08 reason for C=Advanced, that a procedure could "
    "declare it expects IGSNs, is a policy, not an identifier; if it is wanted, it is a separate "
    "field. No procedure column ever held a value here at procedure level." % DATE)


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
    mrow = next(r for r in mrows if r and r[0] == FIELD)
    if (mrow[2], mrow[3], mrow[4], mrow[8]) != ("Advanced", "Advanced", "URI / IGSN", "sample"):
        raise SystemExit("PREMISE: module row is %r" % (mrow[2:5] + [mrow[8]],))
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    plan = []
    for e in reg["composed"]:
        if not any(m["name"] == "Core" for m in e["modules"]):
            continue
        rel = e["tapp"]
        r = next((r for r in rows_of(os.path.join(ROOT, rel))[1:] if r and r[0].strip() == FIELD), None)
        if r is None or (r[2], r[3]) != ("Advanced", "Advanced"):
            raise SystemExit("PREMISE: %s row is %r" % (rel, r and r[2:4]))
        new = re.sub(r"_v(\d+)\.csv$", lambda m: "_v%d.csv" % (int(m.group(1)) + 1), rel)
        plan.append((e, rel, new))
        print("  %-38s -> %s" % (os.path.basename(rel), os.path.basename(new)))
    if len(plan) != 16:
        raise SystemExit("PREMISE: expected 16 Core consumers, found %d" % len(plan))
    mj = os.path.join(MODULES, "Module_Core.json")
    d = json.load(io.open(mj, encoding="utf-8"))
    newver = str(int(d["version"]) + 1)
    print("\n  Module_Core v%s -> v%s: %s C Advanced -> N/A; %d consumers; date %s"
          % (d["version"], newver, FIELD, len(plan), DATE))
    if not apply:
        print("\n(dry run — pass --apply to write)"); return 0

    mrow[2] = "N/A"; mrow[7] = DATE
    write(mcsv, mrows)
    d["version"] = newver
    d["decisions"].append(DECISION)
    with io.open(mj, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False); fh.write("\n")

    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    for e, rel, new in plan:
        np_ = os.path.join(ROOT, new)
        q = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)]
                           + flags(e["modules"]) + ["--out", np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (rel, q.stdout[-1500:], q.stderr[-700:]))
        rr = rows_of(np_); iU = rr[0].index("Last Update")
        row = next(r for r in rr[1:] if r and r[0].strip() == FIELD)
        if row[2] != "N/A":
            raise SystemExit("%s: composition did not set C" % new)
        row[iU] = DATE
        write(np_, rr)
        old = os.path.join(ROOT, rel)
        for f in (old, old[:-4] + ".xlsx"):
            if os.path.exists(f): shutil.move(f, os.path.join(sup, os.path.basename(f)))
        q = subprocess.run([sys.executable, XLSX, np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0: raise SystemExit("xlsx failed %s\n%s" % (new, q.stderr[-700:]))
        print("  composed %s" % os.path.basename(new))

    rp = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(io.open(rp, encoding="utf-8"))          # re-read: compose --out records itself
    news = {os.path.basename(n).rsplit("_v", 1)[0]: n for _, _, n in plan}
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
    write_skeleton(ROOT, DATE)               # after the sync: it reads successors from the mirror
    return 0


sys.exit(main("--apply" in sys.argv))
