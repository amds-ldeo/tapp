#!/usr/bin/env python3
"""Extract `Analyte` into its own module (1 field, 13 consumers).

Analyte is not universal — it applies only to procedures that determine chemical composition — so it
could not join Module_Core, which is unconditional. No composition module is possible either: only
three fields have its footprint and the other two are already Module_Aggregation. So it stands alone.

  --dry (default) / --apply
"""
import argparse, csv, glob, json, os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
MODDIR = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
CUR = os.path.join(ROOT, "Current TAPPs")
REG = os.path.join(ROOT, "composed_tapps.json")
MREG = os.path.join(ROOT, "Project Files", "Registers & Planning", "TAPP_Module_Register.csv")
DATE, NAME, FIELD = "2026-08-14", "Analyte", "Analyte"
GROUP, ANCHOR = "4. Measurement Information", "Reported Variables and Units"


def idx(p):
    rows = list(csv.reader(open(p, encoding="utf-8-sig")))
    ki = [i for i, h in enumerate(rows[0]) if h.strip().lower().startswith("keyed by")][0]
    o, g = {}, None
    for r in rows[1:]:
        if not r or not r[0].strip():
            continue
        C = r[2].strip() if len(r) > 2 else ""
        D = r[3].strip() if len(r) > 3 else ""
        if not (C or D):
            g = r[0].strip(); continue
        o[r[0].strip()] = (g, r, ki)
    return o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true"); ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(); apply = a.apply and not a.dry

    T = {os.path.basename(p)[:-4]: idx(p) for p in sorted(glob.glob(os.path.join(CUR, "*.csv")))}
    holders = sorted(t for t in T if FIELD in T[t])

    sig = {tuple(T[t][FIELD][1][i] for i in (1, 2, 3, 4)) + (T[t][FIELD][1][T[t][FIELD][2]],)
           for t in holders}
    if len(sig) != 1:
        sys.exit(f"FATAL: {FIELD} is not uniform across its {len(holders)} holders ({len(sig)} variants)")
    if {T[t][FIELD][0] for t in holders} != {GROUP}:
        sys.exit(f"FATAL: {FIELD} does not sit in {GROUP} everywhere")
    placements = len(holders)
    if placements < 10:
        sys.exit(f"FATAL: {placements} placements is below Rule 6.10's threshold of 10")
    print(f"guard OK — {FIELD} uniform in {len(holders)}/16, group {GROUP}, "
          f"{placements} placements (threshold 10)")

    def fields_of(m):
        p = os.path.join(MODDIR, f"Module_{m}.csv")
        return {r[0].strip() for r in list(csv.reader(open(p, encoding="utf-8-sig")))[1:]
                if r and r[0].strip() and ((len(r) > 2 and r[2].strip()) or (len(r) > 3 and r[3].strip()))}
    mine = frozenset(holders)
    rels = []
    for p in sorted(glob.glob(os.path.join(MODDIR, "Module_*.csv"))):
        m = os.path.basename(p)[7:-4]
        other = frozenset(t for t in T if fields_of(m) <= set(T[t]))
        rel = ("IDENTICAL" if mine == other else "subset" if mine < other
               else "superset" if mine > other else "overlapping, neither contained")
        rels.append(f"{m} ({len(other)}): {rel}")
    ident = [r for r in rels if "IDENTICAL" in r]
    print(f"Rule 6.15 prong 1 — identical footprints: {ident or 'none'}")

    src = holders[0]
    _, row, ki = T[src][FIELD]
    out = [["Metadata Item", "Description / Purpose", "Procedure-Level Tier", "Analysis-Level Tier",
            "Data Type", "Example / Allowed Content", "Comments", "Last Update", "Keyed By"],
           [FIELD, row[1], row[2], row[3], row[4], "", "", "", row[ki]]]
    man = {
        "module": NAME, "title": "Analyte", "layer": 2, "version": "1",
        "source_of_truth": f"modules/Module_{NAME}.csv",
        "owned_columns": ["A", "B", "C", "D", "E", "I"],
        "overlay_columns": ["F"],
        "consumer_columns": ["F", "G", "H"],
        "mode_flag_default": "Y",
        "conditional": False,
        "applies_when": ("The procedure determines chemical composition. Omit for techniques that "
                         "resolve no chemical species — imaging, tomography, sample preparation."),
        "blocks": [{"name": "analyte", "target_group": GROUP, "placement": "insert_before",
                    "anchor_field": ANCHOR, "fields": [FIELD]}],
        "sub_module_test": (
            f"Run {DATE} under Rule 6.15. Footprint {len(holders)} consumers — every TAPP that "
            f"determines a chemical composition. Prong 1 returned an IDENTICAL footprint against "
            f"Module_Aggregation: the same 13 TAPPs, exactly. Prong 2 refused the merger. 'Which "
            f"chemical species does this procedure determine' and 'which analyses contribute to the "
            f"reported value' are not one subject, and a registrant hunting for the analyte list "
            f"would not open a module about aggregation. The two conditions select the same TAPPs "
            f"because determining a composition and aggregating analyses happen to co-occur across "
            f"this library's techniques, not because they are one component — co-extension is not "
            f"coherence. Core (16/16) cannot absorb it: Core is unconditional and Analyte is absent "
            f"from Lab-XCT, SEM_FIBSEM and SEM_Imaging. No composition module is possible either — "
            f"only three fields share this footprint and the other two are already Aggregation."),
        "notes": (
            f"Single-field module, legitimate under Rule 6.10 as amended {DATE}: the threshold is ten "
            f"placements (fields x consumers), and this is {placements}. Analyte previously belonged "
            f"to no module, and was one of the seven near-universal fields the schema-generation work "
            f"flagged as duplicated across the library.\n\n"
            f"Rule 7 is safe. In all {len(holders)} consumers Analyte is the sole `defines: analyte`; "
            f"in the three TAPPs that omit it there is no definer AND no field keyed by `analyte`. "
            f"The module's applicability condition and the Rule 7 invariant have the same footprint, "
            f"so omitting the module can never strand a consumer with an undefined key.\n\n"
            f"Anchored on `{ANCHOR}` — a Core field, present in all 16 and in the same group, so the "
            f"anchor cannot go missing in a future consumer."),
        "decisions": [
            f"{DATE} v1. Field text taken unchanged from the library, which was verified uniform "
            f"across all {len(holders)} holders first; composition is therefore a no-op and no "
            f"consumer needs a version bump.",
            "Compose AFTER Core: the block anchors on Reported Variables and Units, owned by Core.",
        ],
    }

    if not apply:
        print(f"\nwould write Module_{NAME}.csv (1 field) + .json (1 block, anchored on {ANCHOR!r})")
        print(f"would add {NAME} v1 to {len(holders)} consumer(s) and the module register")
        print(f"consumers: {[t.replace('_TAPP','') for t in holders]}")
        print("\n(dry run — pass --apply to write)")
        return

    with open(os.path.join(MODDIR, f"Module_{NAME}.csv"), "w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(out)
    with open(os.path.join(MODDIR, f"Module_{NAME}.json"), "w", encoding="utf-8") as fh:
        json.dump(man, fh, indent=4, ensure_ascii=False); fh.write("\n")
    print(f"\nwrote Module_{NAME}.csv + .json")

    reg = json.load(open(REG, encoding="utf-8"))
    n = 0
    for e in reg["composed"]:
        if os.path.basename(e["tapp"])[:-4] in holders and \
           not any(m["name"] == NAME for m in e["modules"]):
            e["modules"].append({"name": NAME, "version": "1"}); n += 1
    reg["generated"] = DATE
    with open(REG, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    print(f"composed_tapps.json: +{NAME} on {n} consumer(s)")

    rows = list(csv.reader(open(MREG, newline="", encoding="utf-8-sig")))
    rows.append([NAME, "2", man["title"], "1", "1", "1", f"{len(holders)} TAPP(s)", "active"])
    rows[1:] = sorted(rows[1:], key=lambda r: r[0].lower())
    with open(MREG, "w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(rows)
    print(f"module register: + {NAME}")

    bad = []
    for t in holders:
        e = next(x for x in reg["composed"] if os.path.basename(x["tapp"])[:-4] == t)
        r = subprocess.run([sys.executable, os.path.join(ROOT, "Claude Skills for TAPP",
                                                         "scripts", "compose_tapp.py"),
                            "--source", e["tapp"], "--module", NAME, "--check"],
                           capture_output=True, text=True, cwd=ROOT)
        if r.returncode:
            bad.append(t)
    print(f"verify: {len(holders) - len(bad)}/{len(holders)} --check MATCH"
          + (f"  ** {bad} DIFFER **" if bad else ""))


if __name__ == "__main__":
    main()
