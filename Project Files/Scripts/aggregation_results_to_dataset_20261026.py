#!/usr/bin/env python3
"""Rules in the TAPP, results in the dataset: Module_Aggregation v5 -> v6, Module_UPb v10 -> v11.

    python3 "Project Files/Scripts/aggregation_results_to_dataset_20261026.py" [--apply]

PROBLEM. An EPMA team member, reviewing the v88 workbook, read 5.13-5.15 as unnecessary: users have
their own acceptance criteria, and complete one TAPP per analytical setup. RD's ruling (2026-10-26):
fields that capture actual results belong in the dataset, not the metadata record. Combined Results
(which points went into each mean, how many) and the outcome half of the inclusion criteria are
results on samples; so are the values of the dispersion and other statistics. The line that keeps
precision, accuracy and detection limits in the TAPP: those characterise the measurement's
performance, not a sample.

The literature agrees. In EPMA every "Partially" cell for the inclusion criteria attests a count
("n = 6, 6, ...") and none of the 14 papers states a rule; the dispersion statistic is named in
methods text ("one standard deviation of the mean") and its values sit in the tables.

CHANGE. Reverses the 2026-09-28 design (gap3_combined_results_20260928.py). Module text is already
in place in Module_Aggregation.csv (applied by hand 2026-10-26 after RD approved the draft,
analysis/Aggregation_Results_To_Dataset_DRAFT_2026-10-26.md); this script asserts it and does the rest:
  * `Combined Results` and `Other Statistics` RETIRED. Composition inserts and never deletes, so the
    rows are removed from each source before composing. Their literature cells leave with them;
    the superseded versions keep them.
  * `Analysis Inclusion and Rejection Criteria` — rules only; D Basic -> Editable; key
    `combined result` -> `(none)`, the pre-v5 key.
  * `Goodness-of-Fit or Dispersion Statistic` — which statistic, not its value; C N/A -> Basic,
    D Basic -> Editable; key -> `reported property`, the pre-v5 key.
  * `Combination Method` — gains its "In the dataset:" sentence.
  * Key `combined result` is left with no definer and no consumer: retired under 7.4a-c.
  * Overlays (F, J). Aggregation fills them only where a consumer has nothing, so a consumer still
    holding the v5 default verbatim is blanked first and receives the v6 default. Module_UPb
    overrides wherever it supplies a value, so its own two rows are rewritten here.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "Project Files", "Scripts"))
from superseded_readme import write_skeleton

MODULES = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-10-26"
INC, GOF = "Analysis Inclusion and Rejection Criteria", "Goodness-of-Fit or Dispersion Statistic"
CM, CR, OS = "Combination Method", "Combined Results", "Other Statistics"
RETIRED = (CR, OS)

# v5 overlay defaults: a consumer still holding one of these never chose its own text.
OLD_J = {
    INC: "Criteria and outcome are combined in one field because neither is interpretable without the "
         "other, following the precision/accuracy precedent.",
    GOF: "Answers whether a combined result is defensible as a single population. The value cannot be "
         "known before the analysis.",
}
UPB_F = {
    INC: "e.g., 'Analyses discordant beyond -5% to +10% rejected; Pb*/Pbc < 20 rejected' | "
         "'All analyses included, no filter applied'",
    GOF: "e.g., 'MSWD with probability of fit' | 'MSWD with probability of fit; Model-3 regression where "
         "MSWD exceeds the stated cutoff'",
}
AGG_DECISION = (
    "2026-10-26 v6. Rules in the TAPP, results in the dataset (RD, from an EPMA team member's review of "
    "the v88 workbook). `Combined Results` and `Other Statistics` retired: both held results on samples. "
    "Inclusion Criteria keeps the rules only (D Basic -> Editable; key combined result -> (none)); "
    "Goodness-of-Fit names the statistic, not its value (C N/A -> Basic, D -> Editable; key -> reported "
    "property). Both keys are the pre-v5 ones: v5 re-keyed them only because outcome counts and statistic "
    "values differ per combined value, and those now go to the dataset. Each field that hands values to the "
    "dataset ends with an 'In the dataset:' sentence. Reverses v5's 'criteria and outcome in one field': "
    "the precision/accuracy precedent it cited is measurement performance, which stays in the TAPP; the "
    "outcome is a sample result. See analysis/Aggregation_Results_To_Dataset_DRAFT_2026-10-26.md.")
UPB_DECISION = (
    "2026-10-26 v11. Overlay rows for Inclusion Criteria and Goodness-of-Fit follow Module_Aggregation v6: "
    "examples state rules and statistics, not outcomes and values; Purpose text takes the v6 defaults.")


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


def bump_json(name, decision):
    p = os.path.join(MODULES, "Module_%s.json" % name)
    d = json.load(io.open(p, encoding="utf-8"))
    d["version"] = str(int(d["version"]) + 1)
    d["decisions"].append(decision)
    return p, d


def dump_json(p, d):
    json.dump(d, io.open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    io.open(p, "a", encoding="utf-8").write("\n")


def main(apply=False):
    agg = os.path.join(MODULES, "Module_Aggregation.csv"); ar = rows_of(agg); h = ar[0]
    iI, iJ, iF, iU = h.index("Keyed By"), h.index("Purpose"), h.index("Example / Allowed Content"), h.index("Last Update")
    by = {r[0]: r for r in ar[1:] if r}
    assert not set(RETIRED) & set(by), "PREMISE: retired fields still in Module_Aggregation.csv"
    assert by[INC][iI] == "(none)" and by[GOF][iI] == "reported property", "PREMISE: v6 keys not in place"
    assert "In the dataset:" in by[INC][1] and "In the dataset:" in by[GOF][1] and "In the dataset:" in by[CM][1]
    aj = json.load(io.open(os.path.join(MODULES, "Module_Aggregation.json"), encoding="utf-8"))
    assert aj["version"] == "5", "PREMISE: Aggregation already bumped"
    assert all(f not in b["fields"] for b in aj["blocks"] for f in RETIRED), "PREMISE: manifest blocks"
    upb = os.path.join(MODULES, "Module_UPb.csv"); ur = rows_of(upb)
    ub = {r[0]: r for r in ur[1:] if r}
    assert ub[INC][iJ] == OLD_J[INC] and ub[GOF][iJ] == OLD_J[GOF], "PREMISE: UPb overlay J"

    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    plan = [(e, e["tapp"], re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), e["tapp"]))
            for e in reg["composed"] if any(m["name"] == "Aggregation" for m in e["modules"])]
    lost = {}
    for _, rel, new in plan:
        src = rows_of(os.path.join(ROOT, rel)); s = src[0].index("Literature Assessment")
        n = sum(1 for r in src if r and r[0].strip() in RETIRED for v in r[s + 1:] if v.strip())
        lost[rel] = n
        print("  %-38s -> %-38s %3d literature cells leave with the retired rows" % (
            os.path.basename(rel), os.path.basename(new), n))
    print("\n  Module_Aggregation v5->v6, Module_UPb v10->v11; %d consumers; %d literature cells retired"
          % (len(plan), sum(lost.values())))
    if not apply:
        print("\n(dry run — pass --apply to write)"); return 0

    # --- modules ---------------------------------------------------------------------------
    p, d = bump_json("Aggregation", AGG_DECISION); dump_json(p, d); aggver = d["version"]
    for f in (INC, GOF):
        ub[f][iF], ub[f][iJ], ub[f][iU] = UPB_F[f], by[f][iJ], DATE
    write(upb, ur)
    p, d = bump_json("UPb", UPB_DECISION); dump_json(p, d); upbver = d["version"]

    # --- consumers ---------------------------------------------------------------------------
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    for e, rel, new in plan:
        np_ = os.path.join(ROOT, new)
        src = rows_of(os.path.join(ROOT, rel))
        hdr = src[0]; jJ = hdr.index("Purpose")
        src = [r for r in src if not (r and r[0].strip() in RETIRED)]
        for r in src:
            if r and r[0].strip() in OLD_J and r[jJ] == OLD_J[r[0].strip()]:
                r[jJ] = ""                       # still the v5 default: let v6's arrive
        write(np_, src)
        q = subprocess.run([sys.executable, COMPOSE, "--source", np_] + flags(e["modules"]) + ["--out", np_],
                           cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (rel, q.stdout[-1500:], q.stderr[-700:]))
        rr = rows_of(np_); h2 = rr[0]; kU, kJ, kI = h2.index("Last Update"), h2.index("Purpose"), h2.index("Keyed By")
        names = [r[0].strip() for r in rr if r]
        for f in RETIRED:
            assert f not in names, "%s: %s survived" % (new, f)
        for f in (INC, GOF, CM):
            assert names.count(f) == 1, "%s: %s appears %d times" % (new, f, names.count(f))
        for r in rr[1:]:
            if r and r[0].strip() in (INC, GOF, CM):
                r[kU] = DATE
            if r and r[0].strip() in OLD_J:
                assert r[kJ] == by[r[0].strip()][iJ], "%s: %s Purpose not the v6 default" % (new, r[0])
                assert r[kI] == by[r[0].strip()][iI], "%s: %s key" % (new, r[0])
        write(np_, rr)
        for f in (os.path.join(ROOT, rel), os.path.join(ROOT, rel)[:-4] + ".xlsx"):
            if os.path.exists(f):
                shutil.move(f, os.path.join(sup, os.path.basename(f)))
        q = subprocess.run([sys.executable, XLSX, np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("xlsx failed %s\n%s" % (new, q.stderr[-700:]))
        print("  composed %s" % os.path.basename(new))

    rp = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(io.open(rp, encoding="utf-8"))
    news = {os.path.basename(n).rsplit("_v", 1)[0]: n for _, _, n in plan}
    vers = {"Aggregation": aggver, "UPb": upbver}
    for e in reg["composed"]:
        stem = os.path.basename(e["tapp"]).rsplit("_v", 1)[0]
        if stem in news:
            e["tapp"] = news[stem]
            for m in e["modules"]:
                if m["name"] in vers:
                    m["version"] = vers[m["name"]]
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
