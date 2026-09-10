#!/usr/bin/env python3
"""§4 of Proposal_Monitored_Property_2026-09-10: the definer moves to the measurand list.

    python3 "Project Files/Scripts/restructure_monitored_property_20260910.py" [--apply]

Follows retrofit_monitored_property_20260910.py, which renamed the key. This changes SHAPE:
the field that enumerates monitored properties becomes the definer, and the field that
records where each one was measured becomes an attribute keyed by it.

  MC-ICP-MS (3)   `Collector Configuration`   defines -> `monitored property` (an attribute:
                  which collector each monitored mass was assigned to)
                  `Monitored Masses`          `target species` -> the definer
                                              ADDED to Solution MC-ICP-MS, which lacked it
  EPMA/SEM (3)    `WDS Spectrometer Channel`  defines -> `monitored property`
                  `Monitored Elements`        NEW FIELD, the definer

WHY THIS DISSOLVES A REGISTERED DIVERGENCE. `Monitored Masses` was `defines: ... per target
species` in the six single-collector TAPPs but a plain `target species` consumer in LA-MC, and
absent from Solution MC. The register recorded the reason: "defines ... where there is no
collector array; target species where the cup array defines the channel". Once the mass list
is the definer everywhere and the collector assignment is an attribute, that entry has no
cause. Marked dormant, not deleted — the house treatment for a registered divergence that
stops occurring.

`Monitored Elements` IS TAPP-OWNED, not a module field. Rule 6's admission test asks whether a
field recurs AND does not already exist elsewhere. It recurs in exactly the three electron-beam
TAPPs — but so do all four of its siblings (`WDS Spectrometer Channel`, `X-ray Line`,
`Diffracting Crystal`, `WDS PHA Setting`), and every one of them is TAPP-owned. The WDS block
was never modularised, and admitting one member of it to a module while the rest stay behind
would split the block across two ownership regimes for no gain. Its A-E and I are written
byte-identical in all three so the cross-TAPP uniformity checks stay quiet.

ITS LITERATURE CELLS ARE LEFT BLANK, DELIBERATELY. references/lit_assessment.md says never to
leave a cell blank, and that rule governs a column being assessed. This is the other case: a
field added AFTER those columns were assessed, where blank is the only honest value — it means
"not yet assessed against this source", which `N` ("assessed, not stated") would misreport. The
same distinction the 2026-09-09 re-extraction turned on. Phase 3 for `Monitored Elements` (15
EPMA procedures) and for `Monitored Masses` in Solution MC (8 procedures) is OUTSTANDING and is
not attempted here; deriving the values from the neighbouring `Target Species` or `X-ray Line`
cells would be exactly the folded-in-neighbour defect repaired on 2026-09-09.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODULES = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-10"
DEFINER = "defines: monitored property per target species"

MON_EL_B = ("Specific elements monitored in this procedure, grouped by the target species they serve "
            "where they serve one. Includes elements monitored only to correct an interference, which "
            "serve no target species and so have no parent. The target species list is given by the "
            "Target Species field and is never inferred from the elements appearing here. The X-ray "
            "line, diffracting crystal, spectrometer assignment and counting times used for each "
            "monitored element are recorded in their own fields, keyed to this one.")
MON_EL_F = ("e.g., 'Si, Al, K, Na, Ca, Fe, Mg, Ti, Cr, Mn' | 'Fe, Mg, Si, Ca (determined); Cr "
            "(monitored to correct the Kbeta overlap on Mn)' | N/A | None")
# copied from `Target Species` / `X-ray Line`, which agree in each of the three TAPPs
MODES = {"EPMA_TAPP": "YYYY", "SEM_TAPP": "NNYYYYNNNNN", "SEM_Composition_TAPP": "YYYY"}


def load(p):
    return list(csv.reader(io.open(p, newline="", encoding="utf-8-sig")))


def save(p, rows):
    with io.open(p, "w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(rows)


def idx(h):
    return (h.index("Keyed By"), h.index("Last Update"), h.index("Literature Assessment"))


def main(apply=False):
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    plan = []
    for e in reg["composed"]:
        rel = e["tapp"]
        base = os.path.basename(rel).rsplit("_v", 1)[0]
        rows = load(os.path.join(ROOT, rel))
        names = {r[0].strip() for r in rows[1:] if r and r[0].strip()}
        job = []
        if "Collector Configuration" in names: job.append("demote-collector")
        if base in MODES:                      job.append("electron-beam")
        if "Monitored Masses" in names and base.startswith(("LA-MC", "Solution_MC")): job.append("promote-mm")
        if base.startswith("Solution_MC"):     job.append("add-mm")
        if not job: continue
        new = re.sub(r"_v(\d+)\.csv$", lambda m: "_v%d.csv" % (int(m.group(1)) + 1), rel)
        plan.append((e, rel, new, base, job))
        print("  %-40s -> %-26s %s" % (os.path.basename(rel), os.path.basename(new), ",".join(job)))
    print("\n  Module_MCICPMS v9 -> v10 (Collector Configuration Column I)")
    print("  %d TAPP(s) bumped" % len(plan))
    if not apply:
        print("\n(dry run — pass --apply to write)"); return 0

    # --- module: the collector assignment stops being a definer ----------------
    mc = os.path.join(MODULES, "Module_MCICPMS.csv")
    rows = load(mc); h = rows[0]; iI, iU, _ = h.index("Keyed By"), h.index("Last Update"), None
    for r in rows[1:]:
        if r and r[0].strip() == "Collector Configuration":
            r[iI] = "monitored property"; r[iU] = DATE
    save(mc, rows)
    mj = os.path.join(MODULES, "Module_MCICPMS.json")
    d = json.load(io.open(mj, encoding="utf-8")); d["version"] = "10"
    with io.open(mj, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False); fh.write("\n")
    print("  Module_MCICPMS: Collector Configuration -> monitored property, manifest v10")

    # --- TAPP-owned edits, applied to the CURRENT file before composing --------
    for e, rel, new, base, job in plan:
        p = os.path.join(ROOT, rel); rows = load(p); h = rows[0]
        iI, iU, iS = idx(h)
        width = len(h)
        if "promote-mm" in job:
            for r in rows[1:]:
                if r and r[0].strip() == "Monitored Masses":
                    r[iI] = DEFINER; r[iU] = DATE
        if "electron-beam" in job:
            for r in rows[1:]:
                if r and r[0].strip() == "WDS Spectrometer Channel":
                    r[iI] = "monitored property"; r[iU] = DATE
        # insert the new definer immediately after Target Species — the chain reading order
        if "electron-beam" in job or "add-mm" in job:
            at = next(i for i, r in enumerate(rows) if r and r[0].strip() == "Target Species")
            if "electron-beam" in job:
                row = [""] * width
                row[0] = "Monitored Elements"; row[1] = MON_EL_B
                row[2] = "Basic"; row[3] = "Read-Only"; row[4] = "Text (free)"
                row[5] = MON_EL_F; row[6] = ""; row[7] = DATE; row[iI] = DEFINER
                for k, ch in enumerate(MODES[base]):
                    row[10 + k] = ch
            else:
                src = next(r for r in load(os.path.join(
                    ROOT, "LA-MC-ICP-MS", "LA-MC-ICPMS_TAPP_v73.csv"))[1:]
                    if r and r[0].strip() == "Monitored Masses")
                row = [""] * width
                for k in range(8):
                    row[k] = src[k] if k < len(src) else ""
                row[7] = DATE; row[iI] = DEFINER          # Solution TAPPs have no mode flags
            rows.insert(at + 1, row)
            print("  %-40s inserted %s" % (os.path.basename(rel), row[0]))
        save(p, rows)

    # --- compose / copy, stamp, park -------------------------------------------
    def flags(mods):
        o = []
        for m in mods:
            s = m["name"]
            if m.get("blocks"): s += ":" + (m["blocks"] if isinstance(m["blocks"], str) else ",".join(m["blocks"]))
            o += ["--module", s]
        return o
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    for e, rel, new, base, job in plan:
        if any(m["name"] == "MCICPMS" for m in e["modules"]):
            q = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)]
                               + flags(e["modules"]) + ["--out", os.path.join(ROOT, new)],
                               cwd=ROOT, capture_output=True, text=True)
            if q.returncode != 0:
                raise SystemExit("compose failed %s\n%s\n%s" % (rel, q.stdout[-1500:], q.stderr[-600:]))
            print("  composed %s" % os.path.basename(new))
        else:
            shutil.copyfile(os.path.join(ROOT, rel), os.path.join(ROOT, new))
            print("  copied   %s" % os.path.basename(new))
        old = os.path.join(ROOT, rel)
        for f in (old, old[:-4] + ".xlsx"):
            if os.path.exists(f): shutil.move(f, os.path.join(sup, os.path.basename(f)))
        q = subprocess.run([sys.executable, XLSX, new], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0: raise SystemExit("xlsx failed %s\n%s" % (new, q.stderr[-800:]))
        e["tapp"] = new
        for m in e["modules"]:
            if m["name"] == "MCICPMS": m["version"] = "10"
    reg["generated"] = DATE
    with io.open(os.path.join(ROOT, "composed_tapps.json"), "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    for s in ("build_module_register.py", "sync_current_tapps.py"):
        subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", s), "--apply"],
                       cwd=ROOT, capture_output=True, text=True)
    subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts",
                                                 "build_schema_spec_counts.py"), "--apply"],
                   cwd=ROOT, capture_output=True, text=True)
    print("  registers, schema spec and mirror refreshed")
    return 0


sys.exit(main("--apply" in sys.argv))
