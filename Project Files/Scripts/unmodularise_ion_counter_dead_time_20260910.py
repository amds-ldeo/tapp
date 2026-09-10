#!/usr/bin/env python3
"""Take `Ion Counter Dead Time` out of Module_ICPMS so its key can vary by technique.

    python3 "Project Files/Scripts/unmodularise_ion_counter_dead_time_20260910.py" [--apply]

WHY. The field is keyed `monitored property` in all nine ICP-MS TAPPs, which in a
SINGLE-COLLECTOR instrument asserts one dead time per monitored mass. There is one detector
and therefore one dead time. Proposal_Monitored_Property_2026-09-10 §1 named this as a live
over-declaration and §5 showed the fix — `(none)` in the six single-collector TAPPs — but it
could not be applied: Column I is module-owned and **Rule 6.5 forbids a module expressing two
values for one field**. So the field has to leave the module first. That is this change.

After it, the field is TAPP-owned in all nine, and the divergence is registered:
    `monitored property` — LA-MC, LA-MC UPb, Solution MC   (nine-cup array plus seven ion counters)
    `(none)`             — LA-Q, LA-Q UPb, LA-SF, LA-SF UPb, Solution Q, Solution SF

THE REMOVAL PATH WAS UNTESTED, AND IS NOW TESTED. conventions.md §6.9 listed "Field removal by
a module is untested — behaviour when a module does not define a field the source has is still
blocked by the drop guard rather than handled by design." That guard lives on the
`replace_group` path, which rebuilds a group from the module and would indeed delete the row.
Module_ICPMS uses the **blocks** path instead, which updates fields in place and inserts only
what is absent. Verified in a sandbox before touching anything real: removing the field from
the module and recomposing left the consumer at the same 125 rows and 124 fields, with the
`Ion Counter Dead Time` row **byte-identical to the source**, field order unchanged, nothing
lost and nothing gained. The drop guard did not fire, because on the blocks path a source field
the module does not define is simply not the module's business. conventions.md is updated.

ONE THING COMPOSITION DOES NOT DO is clear the row's `Source: ICP-MS module` comment, which
becomes false the moment the field leaves the module. That is cleared here explicitly; leaving
it would tell the next reader to edit a module that no longer defines the field.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODULES = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
FIELD   = "Ion Counter Dead Time"
DATE    = "2026-09-10"
NEWVER  = "14"
MULTI   = ("LA-MC-ICPMS_TAPP", "LA-MC-ICPMS_UPb_TAPP", "Solution_MC-ICP-MS_TAPP")


def main(apply=False):
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    plan = []
    for e in reg["composed"]:
        if not any(m["name"] == "ICPMS" for m in e["modules"]):
            continue
        rel = e["tapp"]
        new = re.sub(r"_v(\d+)\.csv$", lambda m: "_v%d.csv" % (int(m.group(1)) + 1), rel)
        base = os.path.basename(rel).rsplit("_v", 1)[0]
        key = "monitored property" if base in MULTI else "(none)"
        plan.append((e, rel, new, base, key))
        print("  %-40s -> %-30s I=%s" % (os.path.basename(rel), os.path.basename(new), key))
    print("\n  Module_ICPMS v13 -> v%s, %s removed from the 'session' block" % (NEWVER, FIELD))
    if not apply:
        print("\n(dry run — pass --apply to write)"); return 0

    # --- 1. remove from the module -------------------------------------------
    p = os.path.join(MODULES, "Module_ICPMS.csv")
    rows = list(csv.reader(io.open(p, newline="", encoding="utf-8-sig")))
    keep = [r for r in rows if not (r and r[0].strip() == FIELD)]
    if len(keep) != len(rows) - 1:
        print("  !! expected to remove exactly one row"); return 1
    with io.open(p, "w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(keep)
    j = os.path.join(MODULES, "Module_ICPMS.json")
    d = json.load(io.open(j, encoding="utf-8"))
    for b in d["blocks"]:
        if FIELD in b["fields"]:
            b["fields"] = [f for f in b["fields"] if f != FIELD]
    d["version"] = NEWVER
    note = d.get("notes", "")
    d["notes"] = (note + "\n\n2026-09-10: `Ion Counter Dead Time` REMOVED (39 -> 38 fields). Not a "
                  "retirement — the field stays in all nine consumers, now TAPP-owned, so its Column I "
                  "can differ by technique: `monitored property` where a multi-collector array exists, "
                  "`(none)` in the single-collector Q and SF TAPPs, which have one detector and "
                  "therefore one dead time. Rule 6.5 forbids a module holding both, so the field had to "
                  "leave. This is the library's first use of the blocks path's removal behaviour; it "
                  "leaves the consumer row untouched, verified before the change.").strip()
    with io.open(j, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False); fh.write("\n")
    print("  Module_ICPMS: %s removed, manifest -> v%s" % (FIELD, NEWVER))

    # --- 2. recompose, then set the now-TAPP-owned columns --------------------
    def flags(mods):
        o = []
        for m in mods:
            s = m["name"]
            if m.get("blocks"): s += ":" + (m["blocks"] if isinstance(m["blocks"], str) else ",".join(m["blocks"]))
            o += ["--module", s]
        return o
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    for e, rel, new, base, key in plan:
        q = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)]
                           + flags(e["modules"]) + ["--out", os.path.join(ROOT, new)],
                           cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (rel, q.stdout[-1500:], q.stderr[-700:]))
        np_ = os.path.join(ROOT, new)
        rr = list(csv.reader(io.open(np_, newline="", encoding="utf-8-sig")))
        h = rr[0]; iI = h.index("Keyed By"); iU = h.index("Last Update"); iG = h.index("Comments")
        row = next((r for r in rr[1:] if r and r[0].strip() == FIELD), None)
        if row is None:
            raise SystemExit("%s: %s vanished on recomposition" % (new, FIELD))
        row[iI] = key
        row[iU] = DATE
        if row[iG].strip().startswith("Source:"):
            row[iG] = ""                       # no longer module-supplied
        with io.open(np_, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rr)
        old = os.path.join(ROOT, rel)
        for f in (old, old[:-4] + ".xlsx"):
            if os.path.exists(f): shutil.move(f, os.path.join(sup, os.path.basename(f)))
        q = subprocess.run([sys.executable, XLSX, new], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0: raise SystemExit("xlsx failed %s\n%s" % (new, q.stderr[-700:]))
        e["tapp"] = new
        for m in e["modules"]:
            if m["name"] == "ICPMS": m["version"] = NEWVER
        print("  %-34s I=%s" % (os.path.basename(new), key))

    reg["generated"] = DATE
    with io.open(os.path.join(ROOT, "composed_tapps.json"), "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    for s in ("build_module_register.py", "sync_current_tapps.py", "build_schema_spec_counts.py"):
        subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", s), "--apply"],
                       cwd=ROOT, capture_output=True, text=True)
    print("  registers, schema spec and mirror refreshed")
    return 0


sys.exit(main("--apply" in sys.argv))
