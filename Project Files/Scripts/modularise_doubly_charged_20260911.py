#!/usr/bin/env python3
"""Move the two Doubly-Charged fields into Module_ICPMS and give them to Solution MC (v15 -> v16).

    python3 "Project Files/Scripts/modularise_doubly_charged_20260911.py" [--apply]

WHY. `Doubly-Charged Species Monitor` and `Doubly-Charged Species Production` sat in 8 of the 9
ICP-MS TAPPs — every one but Solution MC — and were therefore duplicated rather than composed
(amds-ldeo/tapp#6, group A). Report_Solution_ICPMS_NewFields_and_ICPMS_Module_2026-08-14 §4.3 held
them back: a second module at footprint 8 fails Rule 6.15, and whether Solution MC genuinely lacks
them "needs Solution MC's Phase 3". That review exists now (14 procedures), and on 2026-09-11 all
14 papers were read for these fields:

  * 0 of 14 report a tuning-time M²⁺/M⁺ ratio or production rate — but neither do the Q and SF
    papers (1 of 15), so the literature does not distinguish MC from the other analysers.
  * 2 of 14 name doubly-charged ions as interferences (Craddock 2008: ⁶⁴Zn²⁺ and kin on the S
    masses; Pringle & Moynier 2017: Er²⁺/Yb²⁺ on m/z 84–88). That is `Interfering Species`
    content, which Module_ICPMS already owns; it is recorded here as `N (...)`, following the
    LA-MC Zhang 2022 cell.

So the placement rests on the module's own subject — "what every ICP-MS procedure shares once the
sample has reached the plasma, independent of … the analyser". Doubly-charged ions form in the
plasma. Footprint 9 = the module's footprint: no new module, no Rule 6.15 question.

WHAT THE MODULE OWNS. A–E and I, as for every Module_ICPMS field. Values are the carriers' own:
Production already agrees in all 8; Monitor had two descriptions, and the fuller LA text (which
already calls itself "Analogous to Oxide Production Method and Threshold") is taken. Tiers stay at
C=Advanced, D=Editable.

SIDE EFFECTS OF COMPOSITION, all by design:
  * Column G gains `Source: ICP-MS module` on both rows in all nine (it fills only an empty G).
  * Column J (Purpose) is an overlay DEFAULT: it fills only an empty cell. The six LA copies of
    Production had none and receive the module's text; no existing Purpose is changed.
  * Solution MC's two rows are inserted at the end of Group 4 — the blocks path has no anchor.
    Composition does not fill F or J on an inserted row, so this script does, from the module
    defaults, and fills the literature cells from the 2026-09-11 reading.

LEFT OPEN, deliberately. Production asks for "both the threshold and the measured value" — the
conflation the Oxide Production pair was split to avoid (precedents.md). Not split here: the
literature attests only thresholds, never a measured value, which is the case precedents.md's XCT
entry says the split does not earn its keep. Once the fields are module-owned it is one edit.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODULES = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-11"
MON     = "Doubly-Charged Species Monitor"
PROD    = "Doubly-Charged Species Production"
ANCHOR  = "Oxide Production Method and Threshold"      # listed after this in the module

MODULE_ROWS = [
    [MON,
     "The mass ratio monitored to estimate doubly-charged ion (M²⁺) formation during instrument "
     "tuning. The monitor species and the mass positions monitored should be stated explicitly. "
     "Analogous to Oxide Production Method and Threshold for oxide monitoring.",
     "Advanced", "Editable", "Text (free)",
     "e.g., Ba²⁺/Ba⁺ (m/z 69/138) | Ce²⁺/Ce⁺ (m/z 70/140) | ²³⁸U²⁺/²³⁸U⁺ (m/z 119/238) | N/A | None",
     "", DATE, "(none)",
     "Doubly-charged ions appear at half the mass of the parent ion and can cause isobaric "
     "interferences on target species in that mass region."],
    [PROD,
     "Measured percentage of doubly-charged ion production for the monitored species at the time "
     "of instrument tuning. The acceptable threshold is typically <1% or <3%. Record both the "
     "threshold and the measured value.",
     "Advanced", "Editable", "Text (free)",
     "e.g., Ce²⁺/Ce⁺ < 3% (threshold); 1.8% (measured) | N/A | None",
     "", DATE, "(none)",
     "Elevated doubly-charged production indicates incomplete ionization and potential "
     "interference on elements at approximately half the mass of abundant matrix components."],
]

# Solution MC literature cells, read from the PDFs on 2026-09-11 (reading-order text, PDF pages).
NOTE = "no M²⁺ tuning monitor or production ratio is stated"
SOLMC_LIT = {
    MON: {"Craddock+etal2008":
          "N (⁶⁴Zn²⁺, ⁶⁶Zn²⁺ and ⁶⁸Zn²⁺ are listed as interferences on the S masses, Table 2, p.4, "
          "and resolved by mass resolution, p.5; " + NOTE + ")",
          "Pringle+Moynier2017":
          "N (\"double-charged Er or Yb isotopes\" are named as interferences that the chemistry "
          "separates from Rb, p.2; " + NOTE + ")"},
    PROD: {},
}

DECISION = (
    "2026-09-11 v16. `Doubly-Charged Species Monitor` and `Doubly-Charged Species Production` "
    "added to the session block, completing the ICP-MS footprint. They were in 8 of the 9 "
    "consumers, all but Solution MC, and were held back on 2026-08-14 (Report §4.3) until "
    "Solution MC's literature could say whether it genuinely lacks them. It cannot "
    "distinguish: 0 of 14 Solution MC procedures report a tuning-time M2+/M+ ratio, and "
    "neither do the Q and SF papers (1 of 15). Two MC papers name doubly-charged ions as "
    "interferences (Craddock 2008, Pringle & Moynier 2017), which is Interfering Species "
    "content. The placement rests on this module's subject: doubly-charged ions form in the "
    "plasma, independent of the analyser. Monitor's two descriptions harmonised to the fuller "
    "LA text; Production already agreed in all 8. Tiers kept at the carriers' C=Advanced, "
    "D=Editable. OPEN: Production asks for both threshold and measured value, the conflation "
    "the oxide pair was split to avoid; not split, because the measured half is unattested. "
    "amds-ldeo/tapp#6.")


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


def col(header, key):
    hits = [i for i, h in enumerate(header) if key.lower() in " ".join(h.split()).lower()]
    if len(hits) != 1:
        raise SystemExit("column key %r matched %d columns" % (key, len(hits)))
    return hits[0]


def main(apply=False):
    by_name = {r[0]: r for r in MODULE_ROWS}
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    plan = []
    for e in reg["composed"]:
        if not any(m["name"] == "ICPMS" for m in e["modules"]):
            continue
        rel = e["tapp"]
        new = re.sub(r"_v(\d+)\.csv$", lambda m: "_v%d.csv" % (int(m.group(1)) + 1), rel)
        rows = rows_of(os.path.join(ROOT, rel))
        have = {r[0].strip(): r for r in rows[1:] if r and r[0].strip() in (MON, PROD)}
        # Premise checks: carriers already hold the module's values except Monitor's Q/SF text.
        for name, r in have.items():
            m = by_name[name]
            for i in (2, 3, 4, 8):
                if r[i] != m[i]:
                    raise SystemExit("PREMISE: %s %s col %d is %r, module says %r"
                                     % (os.path.basename(rel), name, i, r[i], m[i]))
            if name == PROD and r[1] != m[1]:
                raise SystemExit("PREMISE: %s Production description differs" % os.path.basename(rel))
        plan.append((rel, new, sorted(have)))
        print("  %-38s -> %-30s has: %s" % (os.path.basename(rel), os.path.basename(new),
                                            ", ".join(n.split()[-1] for n in sorted(have)) or "NONE (insert)"))
    carriers = [p for p in plan if len(p[2]) == 2]
    lacking = [p for p in plan if not p[2]]
    if len(plan) != 9 or len(carriers) != 8 or len(lacking) != 1 or "Solution_MC" not in lacking[0][0]:
        raise SystemExit("PREMISE: expected 8 carriers plus Solution MC lacking both")
    mcsv = os.path.join(MODULES, "Module_ICPMS.csv")
    mrows = rows_of(mcsv)
    if any(r and r[0] in by_name for r in mrows):
        raise SystemExit("PREMISE: Module_ICPMS already defines one of the fields")
    mj = os.path.join(MODULES, "Module_ICPMS.json")
    d = json.load(io.open(mj, encoding="utf-8"))
    newver = str(int(d["version"]) + 1)
    print("\n  Module_ICPMS v%s -> v%s: %d -> %d fields" % (d["version"], newver, len(mrows) - 1, len(mrows) + 1))
    if not apply:
        print("\n(dry run — pass --apply to write)"); return 0

    # --- 1. the module -----------------------------------------------------------
    at = next(i for i, r in enumerate(mrows) if r and r[0] == ANCHOR) + 1
    mrows[at:at] = [r[:] for r in MODULE_ROWS]
    write(mcsv, mrows)
    for b in d["blocks"]:
        if ANCHOR in b["fields"]:
            k = b["fields"].index(ANCHOR) + 1
            b["fields"][k:k] = [MON, PROD]
    d["version"] = newver
    d["decisions"].append(DECISION)
    with io.open(mj, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False); fh.write("\n")
    print("  Module_ICPMS written (v%s)" % newver)

    # --- 2. recompose every consumer to its new version --------------------------
    mods = {e["tapp"]: e["modules"] for e in reg["composed"]}
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    for rel, new, have in plan:
        q = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)]
                           + flags(mods[rel]) + ["--out", os.path.join(ROOT, new)],
                           cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (rel, q.stdout[-1500:], q.stderr[-700:]))
        np_ = os.path.join(ROOT, new)
        rr = rows_of(np_); h = rr[0]
        iF, iU, iJ = h.index("Example / Allowed Content"), h.index("Last Update"), h.index("Purpose")
        got = [r for r in rr[1:] if r and r[0].strip() in (MON, PROD)]
        if sorted(r[0] for r in got) != [MON, PROD]:
            raise SystemExit("%s: expected exactly one row of each field, got %s" % (new, [r[0] for r in got]))
        for r in got:
            r[iU] = DATE
            if not have:                                   # Solution MC: inserted rows
                m = by_name[r[0].strip()]
                r[iF], r[iJ] = m[5], m[9]
                s = h.index("Literature Assessment")
                for j in range(s + 1, len(h)):
                    if h[j].strip():
                        r[j] = "N"
                for key, v in SOLMC_LIT[r[0].strip()].items():
                    r[col(h, key)] = v
        write(np_, rr)
        old = os.path.join(ROOT, rel)
        for f in (old, old[:-4] + ".xlsx"):
            if os.path.exists(f): shutil.move(f, os.path.join(sup, os.path.basename(f)))
        q = subprocess.run([sys.executable, XLSX, np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0: raise SystemExit("xlsx failed %s\n%s" % (new, q.stderr[-700:]))
        print("  composed %s" % os.path.basename(new))

    # --- 3. the registry: re-read, because compose_tapp --out records compositions itself ----
    rp = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(io.open(rp, encoding="utf-8"))
    news = {os.path.basename(n).rsplit("_v", 1)[0]: n for _, n, _ in plan}
    for e in reg["composed"]:
        stem = os.path.basename(e["tapp"]).rsplit("_v", 1)[0]
        if stem in news:
            e["tapp"] = news[stem]
            for m in e["modules"]:
                if m["name"] == "ICPMS": m["version"] = newver
    reg["generated"] = DATE
    with io.open(rp, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    for s in ("build_module_register.py", "sync_current_tapps.py", "build_schema_spec_counts.py"):
        q = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", s), "--apply"],
                           cwd=ROOT, capture_output=True, text=True)
        print("  %s: %s" % (s, (q.stdout.strip().splitlines() or ["ok"])[-1][:90]))
    return 0


sys.exit(main("--apply" in sys.argv))
