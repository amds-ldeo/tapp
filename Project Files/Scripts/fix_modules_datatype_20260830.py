#!/usr/bin/env python3
"""Bring the modules into line with the Data Type reclassification, and fix the B5/B6
descriptions (2026-08-30).

WHY THIS EXISTS — a Rule 6 violation on my part. Commits 1 and 2 retyped Column E directly
in the TAPP CSVs for six fields that are MODULE-OWNED. `validate_tapp.py` does not check
module/TAPP agreement -- that is `compose_tapp.py --check`'s job, and it was never run as a
gate. The TAPPs are correct and the modules were stale, so recomposing any consumer would
have silently reverted the retypes. Caught by running `--check` before editing a module.

  Module_ICPMS                 Plasma Thermal Mode                 -> Controlled list / Text
  Module_LaserAblation         Sample Form / Analytical Substrate  -> Controlled list / Text
  Module_LaserAblation         Laser Beam Energy Profile           -> Controlled list
  Module_CollisionCell         CRC Configuration                   -> Controlled list / Text
  Module_SolutionIntroduction  Chromatographic Separation Applied  -> Controlled list / Text
  Module_SolutionIntroduction  Desolvation System                  -> Controlled list / Text

Also strips `Other: specify` from 19 module Column F rows the commit-2 sweep missed because
it only walked TAPP CSVs. F is `overlay` on most modules and `owned` on UPb; either way a
stale option there seeds it into any newly composed TAPP.

B5 -- `Plasma Thermal Mode` Column B is pinned to the RF-POWER axis. Of 11 distinct attested
cells, 8 answer RF power and 3 answer wet/dry aerosol state, and those 3 duplicate
`Desolvation System` sentence for sentence. Solvent loading genuinely affects plasma thermal
state, so the field was not being misused -- but two axes cannot share one cell, and
`Desolvation System` already carries the other.

B6 -- `Collision Gas Type` / `Reaction Gas Type` are NOT redundant (physical energy
discrimination vs ion-molecule chemistry) but the boundary was unstated and O2 is attested
BOTH ways in the same paper. Both descriptions now state the boundary. Adding O2 to
`Collision Gas Type`'s Column F is a TAPP-level edit, done separately -- the module does not
own F for CollisionCell.
"""
import csv, json, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MD = ROOT / "Claude Skills for TAPP" / "modules"
STAMP = "2026-08-30"

TYPES = {
 "Module_ICPMS": {"Plasma Thermal Mode": "Controlled list / Text"},
 "Module_LaserAblation": {"Sample Form / Analytical Substrate": "Controlled list / Text",
                          "Laser Beam Energy Profile": "Controlled list"},
 "Module_CollisionCell": {"Collision/Reaction Cell (CRC) Configuration": "Controlled list / Text"},
 "Module_SolutionIntroduction": {"Chromatographic Separation Applied": "Controlled list / Text",
                                 "Desolvation System": "Controlled list / Text"},
}
DESCS = {
 "Module_ICPMS": {"Plasma Thermal Mode":
   "Whether the ICP plasma is operated under cool plasma (<=900 W RF) or normal (hot) plasma "
   "(>1000 W RF) conditions, with the RF power that defines it. This field records the "
   "RF-POWER axis only. Solvent loading also affects plasma thermal state, but dry versus wet "
   "aerosol is recorded by Desolvation System — do not answer this field with 'dry plasma' or "
   "'wet plasma'. Document independently of the RF Power field."},
 "Module_CollisionCell": {
  "Collision Gas Type":
   "Type of collision gas introduced into the collision/reaction cell for PHYSICAL energy "
   "discrimination (KED), where an inert gas thermalizes ions and polyatomic interferences are "
   "retarded by their larger collision cross-section. Typically He. Record a gas here when it "
   "is used without intended chemistry; where the same gas is also used to drive a mass shift, "
   "record that use under Reaction Gas Type — O2 is attested in both roles. Record 'None' if "
   "the cell is in STD mode, and 'N/A' where Collision/Reaction Cell (CRC) Configuration does "
   "not include KED or the instrument has no cell.",
  "Reaction Gas Type":
   "Type of reactive gas introduced into the cell for interference removal through ION-MOLECULE "
   "CHEMISTRY, either on-mass or by mass shift. Common reaction gases include NH₃ (e.g., for "
   "Fe, Ca, K isotopes), O₂ (e.g., for As, Ge, Te mass shift) and CH₄. The distinction from "
   "Collision Gas Type is the mechanism, not the gas: record a gas here when a reaction is "
   "intended. Record 'None' if no reactive gas is used, and 'N/A' where Collision/Reaction "
   "Cell (CRC) Configuration does not include a reaction mode or the instrument has no cell."},
}

def strip_other(ex):
    return " | ".join(p.strip() for p in ex.split("|")
                      if p.strip().strip("'\"").lower() != "other: specify")

def main():
    dry = "--apply" not in sys.argv
    tot = {"type": 0, "desc": 0, "strip": 0}
    touched = set()
    for m in sorted(MD.glob("*.csv")):
        name = m.stem
        rows = list(csv.reader(open(m, encoding="utf-8-sig")))
        hdr = rows[0]
        iA, iB = hdr.index("Metadata Item"), hdr.index("Description")
        iE, iF = hdr.index("Data Type"), hdr.index("Example / Allowed Content")
        iU = hdr.index("Last Update")
        hits = []
        for r in rows[1:]:
            if len(r) <= iU: continue
            it = r[iA]; ch = False
            if it in TYPES.get(name, {}) and r[iE].strip() != TYPES[name][it]:
                hits.append(("type", it, r[iE], TYPES[name][it])); r[iE] = TYPES[name][it]
                tot["type"] += 1; ch = True
            if it in DESCS.get(name, {}) and r[iB] != DESCS[name][it]:
                hits.append(("desc", it, "", "")); r[iB] = DESCS[name][it]
                tot["desc"] += 1; ch = True
            if "Other: specify" in r[iF]:
                r[iF] = strip_other(r[iF]); tot["strip"] += 1; ch = True
                hits.append(("strip", it, "", ""))
            if ch: r[iU] = STAMP
        if not hits: continue
        touched.add(name)
        print(f"{name}: " + ", ".join(f"{k}×{sum(1 for a,*_ in hits if a==k)}"
                                      for k in ("type","desc","strip")
                                      if any(a==k for a,*_ in hits)))
        for a, it, o, n in hits:
            if a == "type": print(f"     type  {it[:44]:44s} {o} -> {n}")
            elif a == "desc": print(f"     desc  {it}")
        if not dry:
            with open(m, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
    # version bumps
    for name in sorted(touched):
        j = MD / f"{name}.json"
        d = json.loads(j.read_text())
        old = d.get("version")
        # `version` is stored as a STRING in the module JSONs — bump numerically, keep the type
        new = str(int(old) + 1) if str(old).isdigit() else old
        if new == old:
            print(f"  ABORT: could not bump {name}.json version {old!r}"); return 1
        print(f"  {name}.json  version {old} -> {new}")
        if not dry:
            d["version"] = new
            j.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print(f"\n{'DRY RUN — ' if dry else ''}type {tot['type']} | desc {tot['desc']} | "
          f"strip {tot['strip']} | modules touched {len(touched)}")
    return 0

sys.exit(main())
