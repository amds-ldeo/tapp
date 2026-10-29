#!/usr/bin/env python3
"""Issues #18 and #21: EPMA's dwell/live-time split, and what Analytical Precision says it measures.

    python3 "Project Files/Scripts/dwell_live_precision_20261029.py" [--apply]

FINDINGS (amds-ldeo/tapp #18, #21; checked against Current TAPPs/ 2026-10-28).
  #18  EPMA's `Dwell Time per Pixel` said "For EDS: total live-time per spectrum per pixel", while
       EPMA's `EDS Live Time per Point or Pixel` said "In EPMA, acquisition is always per point" and
       was flagged N for EDS Mapping. So EPMA put a detector live time in a beam-dwell field. SEM
       already has the split right (live time Y for EDS Mapping, per point or per pixel), and Rule 2
       asks for the same description, tiers and mode flags for EDS across EPMA and SEM.
  #21  `Analytical Precision` (EPMA, SEM, SEM_Composition) opened "Reproducibility of repeated
       measurements…". In ISO 5725 reproducibility is precision across laboratories; within one lab,
       repeats are repeatability (one session) or intermediate precision (across sessions). The
       session-scoped fields in the ICP-MS TAPPs already use those terms.

CHANGE. All three fields are TAPP-owned (check_field_ownership.py).
  * EPMA `EDS Live Time per Point or Pixel`: description made identical to SEM's (Rule 2); EDS
    Mapping flag N -> Y; a mapping example added. The rename history it carried is in precedents.md.
  * EPMA `Dwell Time per Pixel`: the beam's dwell; for EDS the real time, with the live time pointed
    at its own field. Key unchanged (technique-dependent key register).
  * `Analytical Precision` in all three: "Precision", plus which conditions the repeats were under.
Literature cells are not re-read: none of EPMA's 15 procedures is an EDS procedure, so every
live-time cell stays N/A, and the precision cells answer the same question as before.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "Project Files", "Scripts"))
from superseded_readme import write_skeleton

COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-10-29"
LT, DT, AP = "EDS Live Time per Point or Pixel", "Dwell Time per Pixel", "Analytical Precision"
STEMS   = ("EPMA_TAPP", "SEM_TAPP", "SEM_Composition_TAPP")

AP_OLD = ("Reproducibility of repeated measurements on the same or equivalent reference material, expressed as "
          "1-sigma relative standard deviation (%). Include reference material name, number of analyses (n), and "
          "the measured value.")
AP_NEW = ("Precision of repeated measurements on the same or equivalent reference material, expressed as 1-sigma "
          "relative standard deviation (%). State whether the repeats were made within one session "
          "(repeatability) or across sessions (intermediate precision, in ISO 5725 terms). Include reference "
          "material name, number of analyses (n), and the measured value.")
DT_OLD = ("Time spent acquiring X-ray signal at each pixel during X-ray mapping, in milliseconds. For WDS: one value "
          "per spectrometer assignment per pixel. For EDS: total live-time per spectrum per pixel, a single value.")
DT_NEW = ("Time the electron beam dwells on each pixel (step position) during X-ray mapping, in milliseconds. For "
          "WDS: one value per spectrometer assignment per pixel. For EDS: a single value, the real (clock) time per "
          "pixel; the detector live time, which excludes dead time, is recorded in EDS Live Time per Point or Pixel.")
LT_NEW = "EDS spectral acquisition live time per analysis point or per pixel in seconds."
LT_F   = ("e.g., 30 | 60 | 120", "e.g., 30 | 60 | 120 | 0.005 (mapping)")


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


def edit(stem, rr):
    """Apply this TAPP's edits in place; return the fields changed."""
    h = rr[0]
    iB, iF, iU = h.index("Description"), h.index("Example / Allowed Content"), h.index("Last Update")
    by = {r[0].strip(): r for r in rr[1:] if r}
    done = []
    r = by[AP]; assert r[iB] == AP_OLD, "PREMISE: %s %s" % (stem, AP)
    r[iB], r[iU] = AP_NEW, DATE; done.append(AP)
    if stem == "EPMA_TAPP":
        r = by[DT]; assert r[iB] == DT_OLD, "PREMISE: EPMA %s" % DT
        r[iB], r[iU] = DT_NEW, DATE; done.append(DT)
        r = by[LT]; iM = h.index("EDS Mapping")
        assert r[iM] == "N" and r[iF] == LT_F[0], "PREMISE: EPMA %s" % LT
        r[iB], r[iF], r[iM], r[iU] = LT_NEW, LT_F[1], "Y", DATE; done.append(LT)
    return done


def main(apply=False):
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    plan = []
    for e in reg["composed"]:
        stem = os.path.basename(e["tapp"]).rsplit("_v", 1)[0]
        if stem in STEMS:
            new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), e["tapp"])
            done = edit(stem, rows_of(os.path.join(ROOT, e["tapp"])))   # premises checked on a copy
            plan.append((e, stem, e["tapp"], new))
            print("  %-28s -> %-28s %s" % (os.path.basename(e["tapp"]), os.path.basename(new), "; ".join(done)))
    assert len(plan) == 3, "expected 3 TAPPs, found %d" % len(plan)
    if not apply:
        print("\n(dry run — pass --apply to write)"); return 0

    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    for e, stem, rel, new in plan:
        np_ = os.path.join(ROOT, new)
        rr = rows_of(os.path.join(ROOT, rel))
        edit(stem, rr)
        write(np_, rr)
        q = subprocess.run([sys.executable, COMPOSE, "--source", np_] + flags(e["modules"]) + ["--out", np_],
                           cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (rel, q.stdout[-1500:], q.stderr[-700:]))
        assert rows_of(np_) == rr, "compose changed %s: a module owns an edited cell" % new
        for f in (os.path.join(ROOT, rel), os.path.join(ROOT, rel)[:-4] + ".xlsx"):
            if os.path.exists(f):
                shutil.move(f, os.path.join(sup, os.path.basename(f)))
        q = subprocess.run([sys.executable, XLSX, np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("xlsx failed %s\n%s" % (new, q.stderr[-700:]))
        print("  wrote %s" % os.path.basename(new))

    rp = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(io.open(rp, encoding="utf-8"))
    news = {stem: new for _, stem, _, new in plan}
    for e in reg["composed"]:
        stem = os.path.basename(e["tapp"]).rsplit("_v", 1)[0]
        if stem in news:
            e["tapp"] = news[stem]
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
