#!/usr/bin/env python3
"""Three Column B descriptions still name the axis by its old key, or state cardinality.

    python3 "Project Files/Scripts/fix_stale_channel_descriptions_20260910.py" [--apply]

Found by the consistency sweep after the 2026-09-10 `monitored property` retrofit. Column I is
clean library-wide — 0 fields keyed `channel` — but the rename does not touch Column B, and
three descriptions were left behind. Two of the three also breach the Column B cardinality rule
(SKILL.md common mistake 5: "Cardinality stated in Column B is the same mistake one column
over"), which is why the fix removes the claim rather than renaming it.

  Instrument Sensitivity    Module_ICPMS v14 -> v15, 9 consumers
      "with the isotope or channel it was measured on" -> "monitored property".
      A plain rename; the sentence states what the value is reported against, not how many
      values there are.

  Integration Time per Cycle   Module_MCICPMS v10 -> v11, 3 consumers
      "Where different isotope channels use different integration schemes, record the time for
      each channel." REMOVED, not renamed. Rule 7.12 already adjudicated this field as the
      7.11 G3 case and settled it by declaring the finest key UNCONDITIONALLY — the sentence
      restates a conditional cardinality that Column I now carries outright.

  Ion Counter Dead Time     TAPP-owned in all 9 since earlier today
      "Dead time of each ion-counting detector channel" -> "Dead time of the ion-counting
      detector(s)". The "each ... channel" phrasing asserted a per-channel cardinality that is
      now FALSE in six of the nine TAPPs, where the field is `(none)` because a single-collector
      instrument has one detector and therefore one dead time. This is the description
      contradicting its own key, which is exactly what the Column B rule exists to prevent.

NOT CHANGED — five other Column B/F mentions of "channel" are legitimate physical usage, not
the Rule 7 key, and renaming them would make the library harder to read:
`CL Acquisition Mode` and `CL Detector Configuration` (multi-channel PMT hardware),
`EDS Energy Range` ("2048 channels" of a spectrum), `EELS Energy Dispersion` ("eV per channel").
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODULES = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-10"
BUMP    = {"ICPMS": "15", "MCICPMS": "11"}

EDITS = {
"Instrument Sensitivity": (
  "Instrument sensitivity achieved in the session, with the isotope or channel it was measured on",
  "Instrument sensitivity achieved in the session, with the isotope or monitored property it was measured on"),
"Integration Time per Cycle": (
  "Duration of signal integration per measurement cycle (seconds). Where different isotope channels use different integration schemes, record the time for each channel.",
  "Duration of signal integration per measurement cycle (seconds)."),
"Ion Counter Dead Time": (
  "Dead time of each ion-counting detector channel, used in the dead-time correction",
  "Dead time of the ion-counting detector(s), used in the dead-time correction"),
}
MODULE_OF = {"Instrument Sensitivity": "ICPMS", "Integration Time per Cycle": "MCICPMS"}
TAPP_OWNED = {"Ion Counter Dead Time"}


def edit_row(rows, h, field, apply=True):
    iB = h.index("Description"); iU = h.index("Last Update")
    old, new = EDITS[field]
    for r in rows[1:]:
        if r and r[0].strip() == field:
            if old not in r[iB]:
                return None
            if apply:
                r[iB] = r[iB].replace(old, new, 1)
                while len(r) <= iU: r.append("")
                r[iU] = DATE
            return True
    return None


def main(apply=False):
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    touched = {m for m in BUMP}
    plan = []
    for e in reg["composed"]:
        if any(m["name"] in touched for m in e["modules"]):
            rel = e["tapp"]
            plan.append((e, rel, re.sub(r"_v(\d+)\.csv$",
                        lambda m: "_v%d.csv" % (int(m.group(1)) + 1), rel)))
    for _, rel, new in plan:
        print("  %-40s -> %s" % (os.path.basename(rel), os.path.basename(new)))
    print("\n  modules: %s" % ", ".join("%s->v%s" % kv for kv in BUMP.items()))
    print("  %d TAPP(s) bumped; Ion Counter Dead Time edited in place (TAPP-owned)" % len(plan))
    if not apply:
        print("\n(dry run — pass --apply to write)"); return 0

    for fld, mod in MODULE_OF.items():
        p = os.path.join(MODULES, "Module_%s.csv" % mod)
        rows = list(csv.reader(io.open(p, newline="", encoding="utf-8-sig")))
        if edit_row(rows, rows[0], fld) is None:
            print("  !! %s: anchor not found in Module_%s" % (fld, mod)); return 1
        with io.open(p, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rows)
        j = os.path.join(MODULES, "Module_%s.json" % mod)
        d = json.load(io.open(j, encoding="utf-8")); d["version"] = BUMP[mod]
        with io.open(j, "w", encoding="utf-8") as fh:
            json.dump(d, fh, indent=2, ensure_ascii=False); fh.write("\n")
        print("  Module_%s: %s description corrected, manifest -> v%s" % (mod, fld, BUMP[mod]))

    def flags(mods):
        o = []
        for m in mods:
            s = m["name"]
            if m.get("blocks"): s += ":" + (m["blocks"] if isinstance(m["blocks"], str) else ",".join(m["blocks"]))
            o += ["--module", s]
        return o
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    for e, rel, new in plan:
        q = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)]
                           + flags(e["modules"]) + ["--out", os.path.join(ROOT, new)],
                           cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed %s\n%s" % (rel, q.stdout[-1200:]))
        np_ = os.path.join(ROOT, new)
        rr = list(csv.reader(io.open(np_, newline="", encoding="utf-8-sig")))
        for fld in TAPP_OWNED:
            edit_row(rr, rr[0], fld)          # silent if absent or already correct
        with io.open(np_, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rr)
        old = os.path.join(ROOT, rel)
        for f in (old, old[:-4] + ".xlsx"):
            if os.path.exists(f): shutil.move(f, os.path.join(sup, os.path.basename(f)))
        q = subprocess.run([sys.executable, XLSX, new], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0: raise SystemExit("xlsx failed %s" % new)
        e["tapp"] = new
        for m in e["modules"]:
            if m["name"] in BUMP: m["version"] = BUMP[m["name"]]
        print("  %s" % os.path.basename(new))
    reg["generated"] = DATE
    with io.open(os.path.join(ROOT, "composed_tapps.json"), "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    for s in ("build_module_register.py", "sync_current_tapps.py", "build_schema_spec_counts.py"):
        subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", s), "--apply"],
                       cwd=ROOT, capture_output=True, text=True)
    print("  registers, schema spec and mirror refreshed")
    return 0


sys.exit(main("--apply" in sys.argv))
