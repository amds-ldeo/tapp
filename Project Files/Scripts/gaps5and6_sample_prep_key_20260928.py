#!/usr/bin/env python3
"""Gaps 5 and 6 of analysis/Pending_Gaps_2026-09-24_Reference_Example.md.

    python3 "Project Files/Scripts/gaps5and6_sample_prep_key_20260928.py" [--apply]

GAP 5. `Sample Preparation Method` is keyed `(none)` in all 16 TAPPs (Module_Core owns Column I).
Rule 13 already says each sample "may carry its own preparation history" and that "`sample` keys
identity and preparation"; the module never followed. Re-keyed `(none)` -> `sample`. Tiers stay
C=Basic, D=Editable: the procedure registers a preparation, each sample inherits it and may deviate.
Attested by Seifert+2026 (EPMA: "one mount ion-polished before carbon coating"), 1 of 128 cells,
and required by Rule 13 regardless. Under Rule 7.3.2 the finest attested key is declared
unconditionally, so a session whose samples share one preparation fills one row per sample with
the same value. The procedure level is unchanged by the projection rule (conventions 7.3.3, written
alongside this script): `sample` has a C=N/A definer, so it drops out at procedure level.

Not the amds-ldeo/tapp#7 situation. #7 moved `Sample Persistent Identifier` to C=N/A because an
IGSN identifies samples and a registered procedure has none. A preparation is a method the procedure
does specify, so C=Basic keyed by `sample` is coherent.

GAP 6. `Monitored Elements` (EPMA, SEM, SEM_Composition; TAPP-owned) gains one sentence: a target
species determined by stoichiometry or by difference has no monitored element. The TAPPs already
allowed this (O and C in EPMA); nothing said so.

Every TAPP is recomposed (all 16 consume Core), so each gets one version bump carrying both changes.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "Project Files", "Scripts"))
from superseded_readme import write_skeleton

MODULES = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-28"
PREP    = "Sample Preparation Method"
MON     = "Monitored Elements"

MON_OLD = ("Specific elements monitored in this procedure, grouped by the target species they serve where "
           "they serve one. Includes elements monitored only to correct an interference, which serve no "
           "target species and so have no parent. The target species list is given by the Target Species "
           "field and is never inferred from the elements appearing here.")
MON_ADD = (" A target species determined by stoichiometry or by difference, rather than measured, has no "
           "monitored element.")

DECISION = (
    "2026-09-28 v9. `Sample Preparation Method` Keyed By `(none)` -> `sample` (gap 5 of "
    "analysis/Pending_Gaps_2026-09-24_Reference_Example.md). Rule 13 already assigns preparation to the "
    "`sample` key; the module had not followed. Tiers unchanged (C=Basic, D=Editable): the procedure "
    "registers the preparation, each sample inherits it and may deviate. Attested by Seifert+2026 (EPMA, "
    "one mount ion-polished); declared unconditionally under 7.3.2. Procedure-level shape is unchanged by "
    "the projection rule, conventions 7.3.3 (new this date).")


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
    hdr = mrows[0]; iI = hdr.index("Keyed By"); iU = hdr.index("Last Update")
    prep = next(r for r in mrows if r and r[0] == PREP)
    if prep[iI] != "(none)":
        raise SystemExit("PREMISE: Module_Core %s is keyed %r, not (none)" % (PREP, prep[iI]))

    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    plan = []
    for e in reg["composed"]:
        rel = e["tapp"]
        rows = rows_of(os.path.join(ROOT, rel))
        h = rows[0]
        r = next((r for r in rows[1:] if r and r[0].strip() == PREP), None)
        if r is None or r[h.index("Keyed By")] != "(none)":
            raise SystemExit("PREMISE: %s %s not keyed (none)" % (os.path.basename(rel), PREP))
        m = next((r for r in rows[1:] if r and r[0].strip() == MON), None)
        if m is not None and not m[1].startswith(MON_OLD):
            raise SystemExit("PREMISE: %s %s description differs from the shared text" % (os.path.basename(rel), MON))
        new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), rel)
        plan.append((e, rel, new, m is not None))
        print("  %-40s -> %-30s%s" % (os.path.basename(rel), os.path.basename(new),
                                       "  + Monitored Elements sentence" if m is not None else ""))
    mj = os.path.join(MODULES, "Module_Core.json")
    d = json.load(io.open(mj, encoding="utf-8"))
    newver = str(int(d["version"]) + 1)
    print("\n  Module_Core v%s -> v%s: %s keyed (none) -> sample; %d consumers"
          % (d["version"], newver, PREP, len(plan)))
    if not apply:
        print("\n(dry run — pass --apply to write)"); return 0

    prep[iI] = "sample"; prep[iU] = DATE
    write(mcsv, mrows)
    d["version"] = newver
    d["decisions"].append(DECISION)
    with io.open(mj, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False); fh.write("\n")

    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    for e, rel, new, has_mon in plan:
        np_ = os.path.join(ROOT, new)
        q = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)]
                           + flags(e["modules"]) + ["--out", np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (rel, q.stdout[-1500:], q.stderr[-700:]))
        rr = rows_of(np_); h = rr[0]; jU = h.index("Last Update"); jI = h.index("Keyed By")
        for r in rr[1:]:
            if not r:
                continue
            if r[0].strip() == PREP:
                if r[jI] != "sample":
                    raise SystemExit("%s: composition did not carry the new key" % new)
                r[jU] = DATE
            if has_mon and r[0].strip() == MON:
                r[1] = r[1].replace(MON_OLD, MON_OLD + MON_ADD, 1); r[jU] = DATE
        write(np_, rr)
        old = os.path.join(ROOT, rel)
        for f in (old, old[:-4] + ".xlsx"):
            if os.path.exists(f):
                shutil.move(f, os.path.join(sup, os.path.basename(f)))
        q = subprocess.run([sys.executable, XLSX, np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("xlsx failed %s\n%s" % (new, q.stderr[-700:]))
        print("  composed %s" % os.path.basename(new))

    rp = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(io.open(rp, encoding="utf-8"))
    news = {os.path.basename(n).rsplit("_v", 1)[0]: n for _, _, n, _ in plan}
    for e in reg["composed"]:
        stem = os.path.basename(e["tapp"]).rsplit("_v", 1)[0]
        if stem in news:
            e["tapp"] = news[stem]
            for m in e["modules"]:
                if m["name"] == "Core":
                    m["version"] = newver
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
