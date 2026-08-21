#!/usr/bin/env python3
"""Split the combined instrument field into `Instrument Manufacturer` + `Instrument Model`.

Six electron-beam TAPPs already carry the pair; ten carry one combined field under three names
(`ICP-MS Manufacturer & Model` x6, `Instrument Make and Model` x3, `CT System Manufacturer and
Model` x1). Splitting the ten rather than merging the six is the direction that ADDS information:
`Instrument Manufacturer` is a Controlled list and therefore a discovery facet — "find every
procedure run on a JEOL" — which free-text make-and-model cannot support.

The combined field's existing Column F content ("Thermo Scientific iCAP TQ") is already in the form
the SEM/TEM `Instrument Model` field uses, so the rename carries its examples across unchanged; only
the new Manufacturer row needs a vocabulary, supplied per technique below.

Phase 1 (this script): rename the combined field to `Instrument Model` in the ten, and insert an
`Instrument Manufacturer` row immediately before it. Column B/C/D/E/I are left for Module_Core to
supply at composition — the point of the module is that it owns those.

  --dry (default) / --apply
"""
import argparse, csv, glob, json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
REG = os.path.join(ROOT, "composed_tapps.json")
DATE = "2026-08-14"
COL_A, COL_C, COL_D, COL_E, COL_F, COL_H = 0, 2, 3, 4, 5, 7
GROUP = "3. Instrument & Software"
MANUF, MODEL = "Instrument Manufacturer", "Instrument Model"
COMBINED = {"ICP-MS Manufacturer & Model", "Instrument Make and Model",
            "CT System Manufacturer and Model"}

ICPMS_VENDORS = ("Thermo Fisher Scientific | Agilent | PerkinElmer | Nu Instruments | "
                 "Analytik Jena | Shimadzu | Other: specify | Unknown")
VOCAB = {
    "LA-": ICPMS_VENDORS, "Solution_": ICPMS_VENDORS,
    "Lab-XCT": ("Nikon | Zeiss | Bruker | GE / Waygate | North Star Imaging | RX Solutions | "
                "Custom-built | Other: specify | Unknown"),
}


def vocab_for(name):
    for k, v in VOCAB.items():
        if name.startswith(k) or k in name:
            return v
    sys.exit(f"FATAL: no manufacturer vocabulary defined for {name}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true"); ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(); apply = a.apply and not a.dry

    reg = json.load(open(REG, encoding="utf-8"))
    bumps, split, already = [], 0, 0

    for e in reg["composed"]:
        p = os.path.join(ROOT, e["tapp"])
        base = os.path.basename(p)[:-4]
        rows = list(csv.reader(open(p, newline="", encoding="utf-8-sig")))
        names = [r[COL_A].strip() if r else "" for r in rows]

        if MANUF in names and MODEL in names:
            already += 1
            print(f"  {base:34s} already split — untouched")
            continue

        hits = [i for i, r in enumerate(rows) if r and r[COL_A].strip() in COMBINED
                and ((len(r) > COL_C and r[COL_C].strip()) or (len(r) > COL_D and r[COL_D].strip()))]
        if len(hits) != 1:
            sys.exit(f"FATAL: {base} has {len(hits)} combined instrument field(s), expected 1")
        i = hits[0]
        row = rows[i]
        old = row[COL_A].strip()

        # guard: must be in Group 3, or the insert lands in the wrong group
        grp = None
        for r in rows[1:i + 1]:
            if r and r[COL_A].strip() and not ((len(r) > COL_C and r[COL_C].strip())
                                               or (len(r) > COL_D and r[COL_D].strip())):
                grp = r[COL_A].strip()
        if grp != GROUP:
            sys.exit(f"FATAL: {base}: combined field sits in {grp!r}, expected {GROUP!r}")

        new = [""] * len(row)
        new[COL_A] = MANUF
        new[COL_E] = "Controlled list"
        new[COL_F] = vocab_for(base)
        new[COL_H] = DATE
        # mode flags / sentinel / literature columns: copy applicability from the field it joins,
        # blanking the literature cells since no paper was assessed against a field that did not exist
        hdr = rows[0]
        sent = next((j for j, h in enumerate(hdr) if h.strip() == "Literature Assessment"), len(hdr))
        for j in range(9, sent):
            new[j] = row[j] if j < len(row) else "Y"
        for j in range(sent, len(new)):
            new[j] = ""

        row[COL_A] = MODEL
        row[COL_H] = DATE
        rows.insert(i, new)
        split += 1
        print(f"  {base:34s} {old!r} -> {MODEL!r}, + {MANUF!r} above it")

        m = re.search(r"_v(\d+)\.csv$", os.path.basename(p))
        newp = re.sub(r"_v\d+\.csv$", f"_v{int(m.group(1)) + 1}.csv", p)
        if os.path.exists(newp):
            sys.exit(f"FATAL: {os.path.basename(newp)} exists")
        bumps.append((p, newp))
        if apply:
            with open(newp, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)

    print(f"\n{split} TAPP(s) split, {already} already had the pair")
    if not apply:
        print("(dry run — pass --apply to write)")
        return

    pathmap = {os.path.basename(o): os.path.basename(n) for o, n in bumps}
    for e in reg["composed"]:
        b = os.path.basename(e["tapp"])
        if b in pathmap:
            e["tapp"] = e["tapp"].replace(b, pathmap[b])
    reg["generated"] = DATE
    with open(REG, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    print(f"  composed_tapps.json — {len(pathmap)} path(s) updated")
    print("\nNEXT: add both fields to Module_Core, bump it, then recompose all 16.")


if __name__ == "__main__":
    main()
