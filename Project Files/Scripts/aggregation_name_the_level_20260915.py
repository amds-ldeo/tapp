#!/usr/bin/env python3
"""Module_Aggregation v3 -> v4: both descriptions name the level they aggregate (amds-ldeo/tapp#4).

    python3 "Project Files/Scripts/aggregation_name_the_level_20260915.py" [--apply]

THE QUESTION. `Analysis Inclusion and Rejection Criteria` decided "which individual analyses
contribute to a reported aggregate result" and called itself distinct from "within-analysis outlier
filtering, which removes anomalous points inside a single analysis". Stephen Richard asked what an
"analysis" is and what a "point" is; schema generation has to place the field at one level, and
"analysis" names three things in this library (the session record, the act, one acquisition).

WHAT THE CORPUS SAYS, read from every literature cell of the field and of `Spike / Outlier Filtering
Approach` on 2026-09-15:

  * The contributing units come at THREE levels, not one: replicate measurements of one solution or
    location (most Solution papers), spots or grains within a sample (Wu 2023, 246 spots -> 236 in
    the weighted mean; Module_UPb's own example counts grains), and independent aliquots or
    digestions (Willbold 2005). "Replicate" alone — first proposed — would have excluded the last
    two. The new word is "individual result": one acquisition's own value of the reported quantity.
  * The boundary with filtering is BASIS, not unit. The old text put "points inside a single
    analysis" on one side and "whole analyses" on the other, but `Spike / Outlier Filtering
    Approach` attests whole acquisitions discarded on signal grounds (Nakanishi 2022, Chernonozhkin
    2021: spots dropped for inclusion signals). Signal-based discards stay there — its description
    already says "before the reported value is calculated" and is not changed. Result-based
    selection (discordance, dispersion, blank contribution) is this field.
  * The "point" is a cycle (simultaneous collection) or a scan or sweep (sequential collection) —
    one level under two names; `Total Integration Time per Output Data Point` defines an output data
    point as one sweep. The new text names cycles and scans without naming either field, because
    neither exists in all 13 consumers (EPMA, SEM, SEM_Composition and TEM have neither) and a
    pointer to an absent field is a known defect class.

NOT CHANGED. The field name (a rename ripples through registers, documents and the downstream schema;
the description now carries the definition). Tiers, data type, key. The key stays `(none)` but is
FLAGGED: the outcome counts vary per aggregate, which argues for a key — a Rule 7 question, not a
wording one. Columns F and J are consumer-owned and untouched.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODULES = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-15"
INC     = "Analysis Inclusion and Rejection Criteria"
GOF     = "Goodness-of-Fit or Dispersion Statistic"

TEXT = {
    INC: (
        "The rules determining which individual analyses contribute to a reported aggregate result, "
        "together with the outcome of applying them: how many analyses were acquired, how many were "
        "included, and on what grounds any were excluded. Distinct from within-analysis outlier "
        "filtering, which removes anomalous points inside a single analysis: this field decides which "
        "whole analyses enter the reported value.",
        "The rules determining which individual results contribute to a reported aggregate value, "
        "together with the outcome of applying them: how many results were obtained, how many were "
        "included, and on what grounds any were excluded. An individual result is the value of the "
        "reported quantity obtained from one acquisition: a replicate measurement of the same solution "
        "or location, a spot or grain within a sample, or an independently prepared aliquot or "
        "digestion, whichever the procedure aggregates. Distinct from filtering the acquired signal "
        "during data reduction (removing spikes, cycles or scans, or discarding an acquisition whose "
        "signal is compromised): this field records which finished results enter the reported value, "
        "and on what grounds."),
    GOF: (
        "The statistic reported to show whether scatter among the contributing analyses exceeds what "
        "analytical uncertainty alone predicts, together with its value. The procedure may still state "
        "an acceptance threshold, which belongs with the inclusion criteria.",
        "The statistic reported to show whether scatter among the contributing individual results "
        "exceeds what analytical uncertainty alone predicts, together with its value. The procedure "
        "may still state an acceptance threshold, which belongs with the inclusion criteria."),
}

DECISION = (
    "2026-09-15 v4. Both descriptions name the level they aggregate (amds-ldeo/tapp#4). 'Individual "
    "analyses' became 'individual results': one acquisition's own value of the reported quantity, "
    "which the corpus attests at three levels - solution or location replicates, spots or grains "
    "within a sample (Wu 2023; Module_UPb's grain example), independent aliquots or digestions "
    "(Willbold 2005). 'Replicate' alone would have excluded the last two. The boundary with "
    "within-reduction filtering was redrawn by BASIS, not unit: Spike / Outlier Filtering Approach "
    "attests whole acquisitions discarded on signal grounds (Nakanishi 2022, Chernonozhkin 2021), so "
    "signal-based discards stay there and result-based selection is here. The 'point' of the old text "
    "is a cycle or a scan/sweep, one level under two names. Field name, tiers, type unchanged. Key "
    "stays (none) but is flagged: outcome counts vary per aggregate, a Rule 7 question.")


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
    mcsv = os.path.join(MODULES, "Module_Aggregation.csv")
    mrows = rows_of(mcsv)
    for name, (old, _) in TEXT.items():
        r = next(r for r in mrows if r and r[0] == name)
        if r[1] != old:
            raise SystemExit("PREMISE: %s description is not the text #4 was filed against" % name)
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    plan = []
    for e in reg["composed"]:
        if not any(m["name"] == "Aggregation" for m in e["modules"]):
            continue
        rel = e["tapp"]
        rows = rows_of(os.path.join(ROOT, rel))
        for name, (old, _) in TEXT.items():
            r = next((r for r in rows[1:] if r and r[0].strip() == name), None)
            if r is None or r[1] != old:
                raise SystemExit("PREMISE: %s %s does not carry the module text" % (os.path.basename(rel), name))
        new = re.sub(r"_v(\d+)\.csv$", lambda m: "_v%d.csv" % (int(m.group(1)) + 1), rel)
        plan.append((e, rel, new))
        print("  %-38s -> %s" % (os.path.basename(rel), os.path.basename(new)))
    mj = os.path.join(MODULES, "Module_Aggregation.json")
    d = json.load(io.open(mj, encoding="utf-8"))
    newver = str(int(d["version"]) + 1)
    print("\n  Module_Aggregation v%s -> v%s: 2 descriptions; %d consumers" % (d["version"], newver, len(plan)))
    if not apply:
        print("\n(dry run — pass --apply to write)"); return 0

    for r in mrows:
        if r and r[0] in TEXT:
            r[1] = TEXT[r[0]][1]; r[7] = DATE
    write(mcsv, mrows)
    d["version"] = newver
    d["decisions"].append(DECISION)
    with io.open(mj, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False); fh.write("\n")

    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    for e, rel, new in plan:
        np_ = os.path.join(ROOT, new)
        q = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)]
                           + flags(e["modules"]) + ["--out", np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (rel, q.stdout[-1500:], q.stderr[-700:]))
        rr = rows_of(np_); iU = rr[0].index("Last Update")
        for r in rr[1:]:
            if r and r[0].strip() in TEXT:
                if r[1] != TEXT[r[0].strip()][1]:
                    raise SystemExit("%s: composition did not carry the new %s text" % (new, r[0]))
                r[iU] = DATE
        write(np_, rr)
        old = os.path.join(ROOT, rel)
        for f in (old, old[:-4] + ".xlsx"):
            if os.path.exists(f): shutil.move(f, os.path.join(sup, os.path.basename(f)))
        q = subprocess.run([sys.executable, XLSX, np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0: raise SystemExit("xlsx failed %s\n%s" % (new, q.stderr[-700:]))
        print("  composed %s" % os.path.basename(new))

    rp = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(io.open(rp, encoding="utf-8"))          # re-read: compose --out records itself
    news = {os.path.basename(n).rsplit("_v", 1)[0]: n for _, _, n in plan}
    for e in reg["composed"]:
        stem = os.path.basename(e["tapp"]).rsplit("_v", 1)[0]
        if stem in news:
            e["tapp"] = news[stem]
            for m in e["modules"]:
                if m["name"] == "Aggregation": m["version"] = newver
    reg["generated"] = DATE
    with io.open(rp, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    for s in ("build_module_register.py", "sync_current_tapps.py", "build_schema_spec_counts.py"):
        q = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", s), "--apply"],
                           cwd=ROOT, capture_output=True, text=True)
        print("  %s: %s" % (s, (q.stdout.strip().splitlines() or ["ok"])[-1][:90]))
    return 0


sys.exit(main("--apply" in sys.argv))
