#!/usr/bin/env python3
"""Rule 14 sweep: the method stays in the TAPP, the per-analysis value goes to the dataset.

    python3 "Project Files/Scripts/rule14_sweep_20261027.py" [--apply]

FINDINGS. analysis/Rule14_Dataset_Value_Sweep_2026-10-26.md read all 358 fields against
conventions.md 14.1 and found six holding results on samples. RD (2026-10-27) agreed five, plus the
rename and the Detection Limit sentence. Analysis Location/Spot Coordinates STAYS: coordinates are a
property of the sampling unit, not a measurement or a statistic of one. In 0 of 194 literature cells
does any methods section state these values; Internal Precision's 9 positive cells name the
statistic, not a value.

CHANGE.
  * Module_CompositionQC — `Counting Statistics Error`: how the predicted uncertainty is computed,
    and its sigma level. Key sample > sampling unit x reported property -> reported property;
    D Basic -> Editable. `Detection Limit` gains a dataset sentence for per-analysis limits.
  * Module_ICPMS — `Internal (Within-Measurement) Analytical Precision and Assessment Method`: the
    statistic and the cycles it is computed over. Same re-key; D Basic -> Editable.
  * Module_Geochronology — `Radiogenic Fraction of Measured Signal` RETIRED; its dataset sentence
    moves to `Inherited or Initial Signal Correction`. Module_UPb drops its overlay row.
  * Module_UPb — `Discordance Definition and Values` RENAMED `Discordance Definition`: the formula
    only. Renamed in each source before composing, so its row and literature cells are kept.
  * TAPP-owned (Rule 10) — `Error Correlation Between Reported Quantities`: which pairs, and how the
    coefficient is obtained. D Basic -> Editable; type -> Text (free).
  * Consumer-owned examples (F) that held values are rewritten.
Literature cells are not re-read: every cell of the changed fields is N (or names a statistic),
and a field asking for less cannot turn an N into a Y. Radiogenic Fraction's 13 cells, all N,
leave with it.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "Project Files", "Scripts"))
from superseded_readme import write_skeleton

MODULES = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-10-27"
CSE, DL = "Counting Statistics Error", "Detection Limit"
IP = "Internal (Within-Measurement) Analytical Precision and Assessment Method"
RF, IISC = "Radiogenic Fraction of Measured Signal", "Inherited or Initial Signal Correction"
DOLD, DNEW = "Discordance Definition and Values", "Discordance Definition"
EC = "Error Correlation Between Reported Quantities"
COLS = "ABCDEFGHIJ"

CSE_B = ("How the uncertainty predicted from counting statistics — the theoretical limit set by the Poisson "
         "distribution of the counts accumulated — is computed for each reported quantity, and the sigma level "
         "it is quoted at. It is derived from the counts on the target species together with those on any "
         "background or blank subtracted from it. Distinct from the scatter actually observed within a "
         "measurement or between repeated measurements, which is recorded separately. In the dataset: report, "
         "for each analysis and reported quantity, the counting-statistics uncertainty at the stated sigma level.")
DL_ADD = " In the dataset: report the detection limit of each analysis, where the procedure computes one."
IP_B = ("How the precision of a single measurement is assessed from the scatter of the cycles, sweeps or "
        "integrations that make it up: the statistic (2SE, 2SD, 1s RSD) and the number of cycles it is computed "
        "over, for each reported quantity. Distinct from Counting Statistics Error, which records how the "
        "uncertainty predicted from the counts is computed rather than the scatter observed. In the dataset: "
        "report, for each measurement and reported quantity, the internal precision as the stated statistic.")
IP_F = "e.g., '2SE = 2SD/sqrt(n), n = 45 cycles' | '2SE of individual measurements' | 'N/A'"
IISC_ADD = (" In the dataset: report, for each analysis, the radiogenic fraction of the measured signal "
            "(for U-Pb, Pb*/Pbc; for Ar-Ar, %40Ar*).")
DIS_B = ("How discordance between the 206Pb/238U, 207Pb/235U and 207Pb/206Pb chronometers is defined for this "
         "procedure: state the formula used. The rule for excluding discordant analyses belongs in Analysis "
         "Inclusion and Rejection Criteria. In the dataset: report the discordance of each analysis.")
DIS_F = "e.g., '100 x (1 - [206Pb/238U date] / [207Pb/206Pb date])' | '2-sigma concordia ellipse overlap'"
EC_B = ("Which pairs of reported quantities have uncertainties that are not independent, and how the correlation "
        "coefficient between each pair is obtained. In the dataset: report, for each analysis, the correlation "
        "coefficient of each such pair.")
EC_F = "e.g., 'From the data reduction software error propagation' | 'Double-spike inversion covariance'"
EC_J = ("Concordia and isochron regressions cannot be reconstructed without the coefficients. This field says "
        "how they were obtained; the dataset carries them.")
# consumer-owned Column F: value examples -> method examples
F_MAP = {
    (CSE, "e.g., '+-0.04 wt% (1-sigma)' | '+-0.03 wt% (1-sigma)'"):
        "e.g., '1-sigma, from the counts on the peak and on the subtracted background'",
    (CSE, "e.g., '2SE predicted from counting statistics over 45 cycles' | '~0.6% (1 sigma), counting statistics plus propagated uncertainties' | 'N/A'"):
        "e.g., '2SE predicted from counting statistics over 45 cycles' | '1 sigma, counting statistics plus propagated uncertainties' | 'N/A'",
    (IP, "e.g., '2SE = 2SD/sqrt(n), n = 45 cycles' | '+/-0.001-0.002 (2SE)' | '~2.6% (2SE)' | 'N/A'"): IP_F,
    (EC, "e.g., '0.83, from the data reduction software error propagation' | '0.31 (double-spike inversion covariance)'"): EC_F,
}
DECISION = {
    "CompositionQC": ("2026-10-27 v{v}. Rule 14 sweep (analysis/Rule14_Dataset_Value_Sweep_2026-10-26.md). Counting "
                      "Statistics Error records how the predicted uncertainty is computed and its sigma level; the "
                      "per-analysis value goes to the dataset. Re-keyed sample > sampling unit x reported property -> "
                      "reported property; D Basic -> Editable. Detection Limit gains a dataset sentence for per-analysis "
                      "limits; the field itself is measurement performance and stays."),
    "ICPMS": ("2026-10-27 v{v}. Rule 14 sweep. Internal (Within-Measurement) Analytical Precision records the statistic "
              "and the cycles it is computed over; the per-measurement value goes to the dataset. Re-keyed sample > "
              "sampling unit x reported property -> reported property; D Basic -> Editable; example without values."),
    "Geochronology": ("2026-10-27 v{v}. Rule 14 sweep. Radiogenic Fraction of Measured Signal retired: a value per "
                      "analysis, with nothing procedural left (0 of 13 literature cells attest it in methods text). "
                      "Its dataset sentence moves to Inherited or Initial Signal Correction."),
    "UPb": ("2026-10-27 v{v}. Rule 14 sweep. Discordance Definition and Values renamed Discordance Definition: the "
            "formula only, the values going to the dataset; example without values. Overlay row for Radiogenic "
            "Fraction of Measured Signal removed with the field (Module_Geochronology v9)."),
}


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


def col(h, name):
    return h.index(name)


def main(apply=False):
    mods = {m: os.path.join(MODULES, "Module_%s.csv" % m) for m in DECISION}
    M = {m: rows_of(p) for m, p in mods.items()}
    by = {m: {r[0]: r for r in rs[1:] if r} for m, rs in M.items()}
    h = M["CompositionQC"][0]
    iB, iC, iD, iE, iF, iU, iI, iJ = (col(h, c) for c in ("Description", "Procedure-Level Tier", "Analysis-Level Tier",
        "Data Type", "Example / Allowed Content", "Last Update", "Keyed By", "Purpose"))
    assert by["CompositionQC"][CSE][iI] == "sample > sampling unit x reported property", "PREMISE: CSE key"
    assert "In the dataset:" not in by["CompositionQC"][DL][iB], "PREMISE: DL already done"
    assert by["ICPMS"][IP][iI] == "sample > sampling unit x reported property", "PREMISE: IP key"
    assert RF in by["Geochronology"] and RF in by["UPb"] and DOLD in by["UPb"], "PREMISE: Geochronology/UPb rows"
    vers = {m: json.load(io.open(p[:-4] + ".json", encoding="utf-8"))["version"] for m, p in mods.items()}

    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    plan = []
    for e in reg["composed"]:
        src = rows_of(os.path.join(ROOT, e["tapp"]))
        names = {r[0].strip() for r in src if r}
        if any(m["name"] in DECISION for m in e["modules"]) or EC in names:
            new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), e["tapp"])
            plan.append((e, e["tapp"], new))
            print("  %-36s -> %-36s %s" % (os.path.basename(e["tapp"]), os.path.basename(new),
                  ",".join(sorted(m["name"] for m in e["modules"] if m["name"] in DECISION)) + (" +EC" if EC in names else "")))
    print("\n  modules %s; %d consumers" % (", ".join("%s v%s->v%d" % (m, v, int(v) + 1) for m, v in vers.items()), len(plan)))
    if not apply:
        print("\n(dry run — pass --apply to write)"); return 0

    # --- modules ----------------------------------------------------------------------------
    r = by["CompositionQC"][CSE]; r[iB], r[iI], r[iD], r[iU] = CSE_B, "reported property", "Editable", DATE
    r = by["CompositionQC"][DL]; r[iB] += DL_ADD; r[iU] = DATE
    r = by["ICPMS"][IP]; r[iB], r[iI], r[iD], r[iF], r[iU] = IP_B, "reported property", "Editable", IP_F, DATE
    r = by["Geochronology"][IISC]; r[iB] += IISC_ADD; r[iU] = DATE
    r = by["UPb"][DOLD]; r[0], r[iB], r[iF], r[iU] = DNEW, DIS_B, DIS_F, DATE
    M["Geochronology"] = [x for x in M["Geochronology"] if not (x and x[0] == RF)]
    M["UPb"] = [x for x in M["UPb"] if not (x and x[0] == RF)]
    newver = {}
    for m, p in mods.items():
        write(p, M[m])
        jp = p[:-4] + ".json"; d = json.load(io.open(jp, encoding="utf-8"))
        d["version"] = str(int(d["version"]) + 1); newver[m] = d["version"]
        d["decisions"].append(DECISION[m].format(v=d["version"]))
        for b in d.get("blocks", []):
            b["fields"] = [DNEW if f == DOLD else f for f in b["fields"] if f != RF]
        json.dump(d, io.open(jp, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        io.open(jp, "a", encoding="utf-8").write("\n")

    # --- consumers ----------------------------------------------------------------------------
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    for e, rel, new in plan:
        np_ = os.path.join(ROOT, new)
        src = rows_of(os.path.join(ROOT, rel))
        src = [x for x in src if not (x and x[0].strip() == RF)]
        for x in src:
            if x and x[0].strip() == DOLD:
                x[0] = DNEW
        write(np_, src)
        q = subprocess.run([sys.executable, COMPOSE, "--source", np_] + flags(e["modules"]) + ["--out", np_],
                           cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (rel, q.stdout[-1500:], q.stderr[-700:]))
        rr = rows_of(np_); hh = rr[0]
        names = [x[0].strip() for x in rr if x]
        assert RF not in names and DOLD not in names, new
        for f in (DNEW, CSE, IP, IISC, EC, DL):
            assert names.count(f) <= 1, "%s: %s x%d" % (new, f, names.count(f))
        for x in rr[1:]:
            n = x[0].strip() if x else ""
            if n == EC:
                x[1], x[3], x[4], x[9] = EC_B, "Editable", "Text (free)", EC_J
            if (n, x[5] if x else "") in F_MAP:
                x[5] = F_MAP[(n, x[5])]
            if n in (DNEW, CSE, IP, IISC, EC, DL):
                x[7] = DATE
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
    for e in reg["composed"]:
        stem = os.path.basename(e["tapp"]).rsplit("_v", 1)[0]
        if stem in news:
            e["tapp"] = news[stem]
            for m in e["modules"]:
                if m["name"] in newver:
                    m["version"] = newver[m["name"]]
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
