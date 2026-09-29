#!/usr/bin/env python3
"""Gap 3 of analysis/Pending_Gaps_2026-09-24_Reference_Example.md.

    python3 "Project Files/Scripts/gap3_combined_results_20260928.py" [--apply]

PROBLEM. Statistics on averaged or otherwise combined values had nothing to attach to. The inclusion
outcome was keyed `(none)`, and the dispersion statistic was keyed by `reported property` alone. So a
session reporting FeO means for both olivine and pyroxene could hold only one statistic. In addition,
no field outside geochronology said whether a reported variable was a single result or a combination.

WHY NOT ONE KEY PER TAPP (the design first agreed, withdrawn 2026-09-28 before implementation). The
literature cells show combined values at different levels inside a single TAPP:
  * EPMA — per phase within a sample (Liu 2016, Pang 2016, Broussard 2026, Ma 2015), and per grain
    (Ma 2017, "each Table 1 column is the mean of n point analyses of one occurrence").
  * LA-Q-ICP-MS — per grain (Nakanishi 2022), per aliquot (Liu 2024, a fused disc), per phase (Liu
    2016) and per sample (Wu 2023, 236 of 246 spots).
The 2026-09-16 precedent reached the same conclusion: the axis needed is the combined value itself.

CHANGE (Module_Aggregation v4 -> v5; 13 consumers):
  * NEW `Combined Results` — `defines: combined result`, C=N/A, D=Basic. A session-only list, one
    entry per combined value, naming what it combines. Its definer is C=N/A, so under 7.3.3 the key
    drops out at procedure level.
  * NEW `Combination Method` — keyed `reported property`, C=Basic, D=Editable. Whether each reported
    variable is combined, how, and over what. It generalises `Age Model`, which leaves
    Module_Geochronology (v7 -> v8). The U-Pb examples move with it (Module_UPb overlay row renamed).
  * `Analysis Inclusion and Rejection Criteria` — `(none)` -> `combined result`. The procedure
    states the rules once (projection) and the session gives the outcome per combined result. The
    field is not split.
  * `Goodness-of-Fit or Dispersion Statistic` — `reported property` -> `combined result x reported
    property`.
  * NEW `Other Statistics` — `combined result x reported property`, C=N/A, D=Advanced.
  * "Aggregate" wording is removed from the descriptions.
Module_Geochronology also corrects `Age Calculation Method`, which pointed at "Age Model and
Software", a name retired before this date.
Literature cells for the three new fields are left blank: they have not been assessed.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "Project Files", "Scripts"))
from superseded_readme import write_skeleton

MODULES = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-28"
INC, GOF = "Analysis Inclusion and Rejection Criteria", "Goodness-of-Fit or Dispersion Statistic"
CM, CR, OS = "Combination Method", "Combined Results", "Other Statistics"

INC_B = ("The rules determining which individual results contribute to a combined result, together with "
         "the outcome of applying them: how many results were obtained, how many were included, and on "
         "what grounds any were excluded. An individual result is the value of the reported quantity "
         "obtained from one acquisition: a replicate measurement of the same solution or location, a spot "
         "or grain within a sample, or an independently prepared aliquot or digestion, whichever the "
         "procedure combines. Distinct from filtering the acquired signal during data reduction (removing "
         "spikes, cycles or scans, or discarding an acquisition whose signal is compromised): this field "
         "records which finished results enter the combined result, and on what grounds.")
GOF_B = ("The statistic reported to show whether scatter among the individual results contributing to a "
         "combined result exceeds what analytical uncertainty alone predicts, together with its value. The "
         "procedure may still state an acceptance threshold, which belongs with the inclusion criteria.")
GOF_J = ("Answers whether a combined result is defensible as a single population. The value cannot be known "
         "before the analysis.")
NEW = {
    CM: [CM,
         "Whether the reported variable is an individual result or combines several, and if combined, how: "
         "the statistical model used, including any criteria governing which model is applied, and what the "
         "individual results are combined over (for example per grain, per phase within a sample, or per "
         "sample). Record 'Not combined' where each individual result is reported on its own. Record the "
         "model only; the software implementing it belongs in Data Processing Software.",
         "Basic", "Editable", "Text (free)",
         "e.g., Arithmetic mean per phase within each sample | Weighted mean with MSWD-based uncertainty "
         "expansion | York (1969) isochron regression | Not combined",
         "", DATE, "reported property",
         "A methodological choice that changes the result: an arithmetic and a weighted mean of the same "
         "data, or a Model-1 and a Model-3 regression, give different values and different uncertainties."],
    CR: [CR,
         "The reported values that are obtained by averaging or otherwise combining several individual "
         "results, each named with what it combines and the individual results that contribute to it.",
         "N/A", "Basic", "Text (free)",
         "e.g., 'Olivine, sample A, 8 points' | 'Zircon weighted-mean date, sample B, 236 of 246 spots' | "
         "'Isochron, sample C, 36 runs'",
         "", DATE, "defines: combined result",
         "Gives the inclusion outcome and the dispersion statistics a row to attach to when a session "
         "reports more than one combined value of the same variable, such as FeO in olivine and FeO in "
         "pyroxene."],
    OS: [OS,
         "Any statistic reported for a combined result beyond the dispersion statistic, with the statistic "
         "named and its value.",
         "N/A", "Advanced", "Text (free)",
         "e.g., 'Standard error of the mean' | '95% confidence interval' | 'Probability of fit, p = 0.12'",
         "", DATE, "combined result x reported property", ""],
}
AGG_DECISION = (
    "2026-09-28 v5. Gap 3 of analysis/Pending_Gaps_2026-09-24_Reference_Example.md. New `Combined Results` "
    "(defines: combined result, session only), `Combination Method` (per reported property; generalises "
    "Module_Geochronology's `Age Model`), `Other Statistics`. Inclusion Criteria re-keyed (none) -> combined "
    "result; Goodness-of-Fit re-keyed reported property -> combined result x reported property. A per-TAPP "
    "grouping key was agreed first and withdrawn before implementation: combined values sit at different "
    "levels within one TAPP (EPMA per phase and per grain; LA-Q per grain, aliquot, phase and sample).")
GEO_DECISION = (
    "2026-09-28 v8. `Age Model` removed: it moves to Module_Aggregation as `Combination Method`, the same "
    "field for every reported variable rather than for ages only (gap 3). `Age Calculation Method` "
    "description corrected: it pointed at 'Age Model and Software', a name retired before this date.")
UPB_DECISION = "2026-09-28 v9. Overlay row `Age Model` renamed `Combination Method`, following Module_Aggregation v5 / Module_Geochronology v8."
AGECALC_OLD = "Distinct from Age Model and Software, which records how multiple analyses are combined into a single reported result."
AGECALC_NEW = "Distinct from Combination Method, which records whether and how individual results are combined into a single reported value."


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


def main(apply=False):
    agg = os.path.join(MODULES, "Module_Aggregation.csv"); ar = rows_of(agg); h = ar[0]
    iI, iU, iJ = h.index("Keyed By"), h.index("Last Update"), h.index("Purpose")
    by = {r[0]: r for r in ar[1:] if r}
    assert by[INC][iI] == "(none)" and by[GOF][iI] == "reported property", "PREMISE: Aggregation keys"
    assert not ({CM, CR, OS} & set(by)), "PREMISE: new fields already present"
    geo = os.path.join(MODULES, "Module_Geochronology.csv"); gr = rows_of(geo)
    assert any(r and r[0] == "Age Model" for r in gr), "PREMISE: Age Model not in Geochronology"
    assert any(r and r[0] == "Age Calculation Method" and AGECALC_OLD in r[1] for r in gr), "PREMISE: Age Calc text"
    upb = os.path.join(MODULES, "Module_UPb.csv"); ur = rows_of(upb)
    assert any(r and r[0] == "Age Model" for r in ur), "PREMISE: UPb overlay row"

    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    plan = [(e, e["tapp"], re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), e["tapp"]))
            for e in reg["composed"] if any(m["name"] == "Aggregation" for m in e["modules"])]
    for _, rel, new in plan:
        print("  %-38s -> %s" % (os.path.basename(rel), os.path.basename(new)))
    print("\n  Module_Aggregation v4->v5 (3 new fields, 2 re-keyed); Geochronology -Age Model; UPb overlay renamed; %d consumers" % len(plan))
    if not apply:
        print("\n(dry run — pass --apply to write)"); return 0

    # --- modules ---------------------------------------------------------------------------
    by[INC][1], by[INC][iI], by[INC][iU] = INC_B, "combined result", DATE
    by[GOF][1], by[GOF][iI], by[GOF][iJ], by[GOF][iU] = GOF_B, "combined result x reported property", GOF_J, DATE
    out = [h]
    for r in ar[1:]:
        if r and r[0] == INC:
            out += [NEW[CM], NEW[CR]]
        out.append(r)
        if r and r[0] == GOF:
            out.append(NEW[OS])
    write(agg, out)
    p, d = bump_json("Aggregation", AGG_DECISION)
    for b in d["blocks"]:
        if b["name"] == "inclusion":
            b["fields"] = [CM, CR, INC]
        if b["name"] == "dispersion":
            b["fields"] = [GOF, OS]
    json.dump(d, io.open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    io.open(p, "a", encoding="utf-8").write("\n"); aggver = d["version"]

    gh = gr[0]; gU = gh.index("Last Update")
    gout = [gr[0]]
    for r in gr[1:]:
        if r and r[0] == "Age Model":
            continue
        if r and r[0] == "Age Calculation Method":
            r[1] = r[1].replace(AGECALC_OLD, AGECALC_NEW); r[gU] = DATE
        gout.append(r)
    write(geo, gout)
    p, d = bump_json("Geochronology", GEO_DECISION)
    json.dump(d, io.open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    io.open(p, "a", encoding="utf-8").write("\n"); geover = d["version"]

    for r in ur:
        if r and r[0] == "Age Model":
            r[0] = CM
    write(upb, ur)
    p, d = bump_json("UPb", UPB_DECISION)
    json.dump(d, io.open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    io.open(p, "a", encoding="utf-8").write("\n"); upbver = d["version"]

    # --- consumers ---------------------------------------------------------------------------
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    for e, rel, new in plan:
        np_ = os.path.join(ROOT, new)
        src = rows_of(os.path.join(ROOT, rel))
        hdr = src[0]; jU = hdr.index("Last Update")
        # Age Model leaves Geochronology, which inserts rather than overlays and so never drops a
        # stale row. Remove it from the source before composing; nothing assessed is lost (0 cells).
        s = hdr.index("Literature Assessment")
        for r in src:
            if r and r[0].strip() == "Age Model":
                assert not any(x.strip() for x in r[s + 1:]), "PREMISE: Age Model has literature cells in %s" % rel
        src = [r for r in src if not (r and r[0].strip() == "Age Model")]
        write(np_, src)
        q = subprocess.run([sys.executable, COMPOSE, "--source", np_] + flags(e["modules"]) + ["--out", np_],
                           cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (rel, q.stdout[-1500:], q.stderr[-700:]))
        rr = rows_of(np_); h2 = rr[0]; kI, kU = h2.index("Keyed By"), h2.index("Last Update")
        names = [r[0].strip() for r in rr if r]
        for f in (CM, CR, OS):
            assert names.count(f) == 1, "%s: %s appears %d times" % (new, f, names.count(f))
        assert "Age Model" not in names, new
        for r in rr[1:]:
            if r and r[0].strip() in (INC, GOF, CM, CR, OS, "Age Calculation Method"):
                r[kU] = DATE
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
    vers = {"Aggregation": aggver, "Geochronology": geover, "UPb": upbver}
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
    write_skeleton(ROOT, DATE)          # skips: this date's README exists and is extended by hand
    return 0


sys.exit(main("--apply" in sys.argv))
