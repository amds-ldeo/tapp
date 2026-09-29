#!/usr/bin/env python3
"""Column F of keyed fields describes one member's value — conventions 7.3.4 (2026-09-29).

    python3 "Project Files/Scripts/colf_value_only_20260929.py" [--apply]

PROBLEM. Column F is what one input box accepts: the schema builds a field's enum or examples from it
(schema spec §6) and the form draws one input per member from Column I. 33 keyed rows carried member
labels instead — 'SiO2: 0.02 wt%', 'Smithsonian anorthite (Si Ka, Al Ka, Ca Ka)', 'Si=Sp1; Ti=Sp2',
'ArCl+ on 75As' — in at least four notations. A label breaks a controlled list's enumeration and
misleads on a text field. Each row below was read by hand; the value is kept, the member label goes.

Also:
  * `Acquisition Pass` (a definer): its example becomes a parseable definer list ('Pass 1 (LR, …);
    Pass 2 (…)'), since 'Pass 1: LR' reads as member: value under 7.3.4.
  * `Plasma Thermal Mode` loses 'Mixed: specify mode per analytical sub-run'. The field is keyed by
    acquisition pass, so a procedure with a cool-plasma pass records each pass's mode. This REVERSES
    the 2026-08-30 harmonisation that added `Mixed` to Solution MC; recorded in precedents.md.

Modules: Module_UPb owns Column F on its overlay rows (Age Calculation Method, Procedural Blank
Level), so those are edited there and arrive by composition. Module_ICPMS carries default Column F
that seeds new consumers, and five defaults carried labels; they are cleaned so new TAPPs do not
inherit them. Both modules are bumped. Column F is otherwise consumer-owned (Rule 6.4), so the TAPP
rows are edited after composition.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "Project Files", "Scripts"))
from superseded_readme import write_skeleton

MODULES = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-29"

E, S, SC, T = "EPMA", "SEM", "SEM_Composition", "TEM"
LAMC, LAMCU, LAQ, LAQU, LASF, LASFU = ("LA-MC-ICPMS", "LA-MC-ICPMS_UPb", "LA-Q-ICP-MS",
                                       "LA-Q-ICP-MS_UPb", "LA-SF-ICP-MS", "LA-SF-ICP-MS_UPb")
SMC, SQ, SSF = "Solution_MC-ICP-MS", "Solution_Q-ICP-MS", "Solution_SF-ICP-MS"
LA6 = {LAMC, LAMCU, LAQ, LAQU, LASF, LASFU}
ICP9 = LA6 | {SMC, SQ, SSF}
UPB3 = {LAMCU, LAQU, LASFU}
ESS = {E, S, SC}

PTM_NEW = "Normal plasma (>1000 W RF) | Cool plasma (≤900 W RF) | N/A | None"
AP_NEW = ("e.g., 'Pass 1 (LR, M/dm 300); Pass 2 (MR, M/dm 4000)' | 'Pass 1 (KED, He, on-mass); Pass 2 "
          "(MS/MS, O2 mass-shift)' | 'Pre-ablation; Run 1 (major, MR, 30 um); Run 2 (trace, LR, 130 um)' "
          "| 'Single pass'")
ICWM_NEW = "e.g., '2SE = 2SD/sqrt(n), n = 45 cycles' | '+/-0.001-0.002 (2SE)' | '~2.6% (2SE)' | 'N/A'"
CS_NEW = ("e.g., External calibration | Isotope dilution | Isotope dilution (67Zn spike) | "
          "External calibration + standard addition | N/A | None")

# (field, TAPP stems, old-value prefix, new value). The prefix is a premise: the row must still hold
# what was reviewed on 2026-09-29, and every listed stem must match exactly once.
TAPP_EDITS = [
    ("Analytical Accuracy", {S, SC}, "e.g., 'SiO2: +0.5% relative to GeoReM accepted value",
     "e.g., '+0.5% relative to GeoReM accepted value' | '-1.2%'"),
    ("Analytical Accuracy", {E}, "e.g., 'SiO2: +0.5% relative to GeoReM preferred value",
     "e.g., '+0.5% relative to GeoReM preferred value' | '-1.2% relative to accepted value'"),
    ("Analytical Accuracy and Assessment Method", {SMC}, "e.g., % deviation from published δ56Fe",
     "e.g., % deviation from the published compilation value | Agreement with the certified value of "
     "the spike solution | Z-score relative to interlaboratory consensus | N/A | None"),
    ("Analytical Accuracy and Assessment Method", LA6, "e.g., 'Within ±5% of GeoReM preferred values for most REEs",
     "e.g., 'Within ±5% of GeoReM preferred values (n = 15)' | '+8% (known matrix sensitivity)' | "
     "'±3% vs. GeoReM (n = 20)'"),
    ("Analytical Precision", {E}, "e.g., 'SiO2: 0.5% 1-sigma RSD",
     "e.g., '0.5% 1-sigma RSD (n = 20)' | '1.2% 1-sigma RSD (n = 15)'"),
    ("Analytical Precision", {S, SC}, "e.g., 'SiO2: 0.8% 1-sigma RSD",
     "e.g., '0.8% 1-sigma RSD (n = 10)' | '1.5%'"),
    ("Beam Damage Minimization", {E}, "e.g., 'Na measured first with 10 um defocused beam at 5 nA'",
     "e.g., 'Na measured first with 10 um defocused beam at 5 nA' | 'Time-resolved acquisition "
     "extrapolated to t=0 for Na and K' | 'None required'"),
    ("Beam Damage Minimization", {S, SC}, "'Beam defocused to 5 µm; current reduced to 2 nA for hydrous phases'",
     "e.g., 'Beam defocused to 5 µm; current reduced to 2 nA'"),
    ("Between-Session (Long-Term) Analytical Precision and Assessment Method", LA6, "e.g., '2σ RSD = 3% for Eu/Eu*",
     "e.g., '2σ RSD = 3% across 12 sessions over 8 months' | '1σ RSD = 2% across 17 sessions over "
     "3 years (n = 85 analyses)'"),
    ("Between-Session (Long-Term) Analytical Precision and Assessment Method", {SMC}, "e.g., 2SD = 0.030‰ on δ56Fe",
     "e.g., 2SD = 0.030‰ (n = 23 sessions; Dauphas et al. 2009) | 2SD = 0.005‰ (n > 50 analyses) | N/A | None"),
    ("Calibration Strategy per Target Species", ICP9, "External calibration (all target species)", CS_NEW),
    ("Counting Statistics Error", ESS, "e.g., 'SiO2: +-0.04 wt% (1-sigma)'",
     "e.g., '+-0.04 wt% (1-sigma)' | '+-0.03 wt% (1-sigma)'"),
    ("Detection Limit", LA6, "e.g., '0.003 ng g⁻¹ (La)",
     "e.g., '0.003 ng g⁻¹' | '0.005 ng g⁻¹' | '0.02 µg g⁻¹'"),
    ("Detection Limit", {E}, "e.g., 'SiO2: 0.02 wt%", "e.g., '0.02 wt%' | '0.03 wt%' | '0.04 wt%'"),
    ("Detection Limit", {S, SC}, "e.g., 'SiO2: 0.04 wt%", "e.g., '0.04 wt%' | '0.03 wt%' | '0.05 wt%'"),
    ("Dwell Time per Mass", {LAQ, LAQU, LASF, LASFU}, "e.g., 6 ms (most isotopes)", "e.g., 6 | 10 | 35"),
    ("EDS Detection Limit", {T}, "e.g., 'Typical ~0.5–1 wt% for light elements",
     "e.g., '~0.5–1 wt%' | '~0.1–0.5 wt%' | 'Not determined' | N/A"),
    ("EELS Detection Limit", {T}, "e.g., 'C K-edge detection limit",
     "e.g., '~0.1 at% (60 kV)' | '~10 ppm' | 'Not determined' | N/A"),
    ("Error Correlation Between Reported Quantities", {LAMCU, SMC, LAQU, LASFU}, "e.g., 'rho(206Pb/238U, 207Pb/235U) = 0.83",
     "e.g., '0.83, from the data reduction software error propagation' | '0.31 (double-spike inversion covariance)'"),
    ("Faraday Cup Amplifier Resistor Values", {SMC}, "e.g., All cups: 10¹¹ Ω", "e.g., 10¹¹ Ω | 10¹³ Ω | N/A | None"),
    ("Instrument Sensitivity", LA6, "e.g., '0.42% useful yield (U, method",
     "e.g., '0.42% useful yield (method of Horstwood et al. 2016)' | '0.1% useful yield' | "
     "'1.2 x 10^6 cps/ppb' | 'N/A'"),
    ("Instrument Sensitivity", {SMC, SQ, SSF}, "e.g., '572 V/ppm total Zr'",
     "e.g., '572 V/ppm' | '~2.5 x 10^6 cps/ppb' | '0.04 count pg-1 ml' | '0.1% useful yield' | 'N/A'"),
    ("Inter-Pass Data Dependency", LA6, "e.g., Single run | Two sequential runs",
     "e.g., Run 1 (Cr concentration, used as the internal standard) | Pre-ablation pass (surface "
     "cleaning only)"),
    ("Interference Correction Method", LA6, "e.g., 'Mathematical correction: ⁸⁷Sr",
     lambda old: old.replace(" by >90% for ⁶⁰Ni and ⁷¹Ga'", " by >90%'")),
    ("Interference Correction Standard", ESS, "e.g., 'Synthetic TiO2 (for Ti Kb on V correction)'",
     "e.g., 'Synthetic TiO2 (Ti Kb overlap)' | 'Chromite USNM 117075 (Cr Kb overlap)'"),
    ("Interfering Elements", {E}, "e.g., 'Ti Kb overlaps V Ka' | 'Cr Kb overlaps Mn Ka' | 'Ba La",
     "e.g., 'Ti Kb' | 'Cr Kb' | 'Ba La'"),
    ("Interfering Elements", {S, SC}, "e.g., 'Ti Kb overlaps V Ka' | 'Cr Kb overlaps Mn Ka' | 'S Ka",
     "e.g., 'Ti Kb' | 'Cr Kb' | 'S Ka'"),
    ("Interfering Species", LA6, "e.g., '⁸⁷Rb on ⁸⁷Sr",
     "e.g., '⁸⁷Rb' | '¹⁷⁰Yb²⁺' | '⁴⁰Ar³¹P⁺' | '⁴⁴Ca¹⁶O⁺' | '¹³⁷Ba¹⁶O⁺' | 'None'"),
    ("Interfering Species", {SMC}, "e.g., 54Cr+ on 54Fe+",
     "e.g., 54Cr+ | 58Ni+ | 204Hg+ (corrected via the 202Hg monitor) | 238U abundance-sensitivity tail | "
     "238UH+ | None | N/A"),
    ("Interfering Species", {SQ}, "e.g., ArCl+ on 75As", "e.g., ArCl+ | MoO+ | Ba2+ | BaO+ | None | N/A"),
    ("Interfering Species", {SSF}, "e.g., BaO+ on Eu isotopes", "e.g., BaO+ | Zr2+ | Oxides | None | N/A"),
    ("Internal (Within-Measurement) Analytical Precision and Assessment Method", ICP9,
     "e.g., '2SE = 2SD/sqrt(n), n = 45 cycles' | '+/-0.001-0.002 (2SE) on 206Pb/204Pb'", ICWM_NEW),
    ("Mass Resolution Assignment", {LAMC, LAMCU, LASF, LASFU}, "e.g., LR: Ag, Cd",
     "e.g., LR (m/Δm ≈ 300) | MR | HR | N/A | None"),
    ("Mass Resolution Assignment", {SSF}, "e.g., LR: Ag, Cd", "e.g., LR | MR (m/Δm ~2500) | HR | N/A | None"),
    ("Mass Resolution Assignment", {SMC}, "e.g., HR: K; LR: Cu, Zn", "e.g., LR | MR | HR | N/A | None"),
    ("Plasma Thermal Mode", ICP9, "Normal plasma (>1000 W RF) | Cool plasma (≤900 W RF) | Mixed", PTM_NEW),
    ("Primary Calibration Standard Name", {E}, "e.g., 'Smithsonian anorthite (Si Ka",
     "e.g., 'Smithsonian anorthite' | 'Amelia albite' | 'Synthetic fayalite' | 'SrF2'"),
    ("Primary Calibration Standard Name", {S, SC}, "e.g., 'Smithsonian anorthite (Si, Al, Ca)'",
     "e.g., 'Smithsonian anorthite' | 'Synthetic fayalite' | 'Pure element foil' | "
     "'Alloy standard (Micro-Analysis Consultants)'"),
    ("Primary Calibration Standard Name", {SMC}, "e.g., IRMM-014 (Fe isotopes",
     "e.g., IRMM-014 (Taylor et al. 1992) | CRM-112a / SRM-960 | NIST SRM 981 | JMC Lyon Zn standard | "
     "NIST SRM 3102a | In-house single-element standard solution: specify | N/A | None"),
    ("WDS Spectrometer Channel", ESS, "e.g., 'Si=Sp1;",
     "e.g., 'Sp1' | 'Sp2+Sp3 (aggregate intensity counting)' | 'Sp4'"),
    ("Within-Session Analytical Precision and Assessment Method", LA6, "e.g., '1σ RSD = 1.5% for Ba",
     "e.g., '1σ RSD = 1.5% (n = 5 per session)' | 'Mapping: 4% 1σ RSD across 3 map areas at session "
     "start and end (n = 3)'"),
    ("Within-Session Analytical Precision and Assessment Method", {SMC}, "e.g., 2SD = 0.03‰ on δ56Fe",
     "e.g., 2SD = 0.03‰ (n = 10) | 2σ = 0.004‰ (n = 9 brackets) | N/A | None"),
    ("delta or epsilon Value Reference Standard", {SMC}, "e.g., IRMM-014 (Fe;",
     "e.g., IRMM-014 (Taylor et al. 1992) | CRM-112a / SRM-960 | NIST SRM 981 | NIST SRM 3102a | "
     "Sn_IPGP (in-house standard) | JMC Lyon | N/A | None"),
    ("Acquisition Pass", ICP9, "e.g., 'Pass 1: LR (M/dm 300)", AP_NEW),
]
# module -> [(field, old prefix, new)]
MODULE_EDITS = {
    "UPb": [
        ("Age Calculation Method", "e.g., 206Pb/238U and 207Pb/235U date equations",
         "e.g., Decay equation with the Jaffey et al. (1971) decay constants | Wetherill concordia intercept | "
         "Tera-Wasserburg concordia intercept | 238U/206Pb-207Pb/206Pb isochron"),
        ("Procedural Blank Level", "e.g., 'Total procedural Pb blank 0.6",
         "e.g., '0.6 +/- 0.3 pg total procedural blank; blank composition 206Pb/204Pb = 18.55, "
         "207Pb/204Pb = 15.50, 208Pb/204Pb = 38.08 (long-term lab average, n = 42)' | "
         "'Gas blank 120 counts/s, subtracted per analysis'"),
    ],
    "ICPMS": [
        ("Instrument Sensitivity", "e.g., '572 V/ppm total Zr'", "e.g., '572 V/ppm' | '~2.5 x 10^6 cps/ppb' | '0.04 count pg-1 ml'"),
        ("Internal (Within-Measurement) Analytical Precision and Assessment Method",
         "e.g., '2SE = 2SD/sqrt(n), n = 45 cycles' | '+/-0.001-0.002 (2SE) on 206Pb/204Pb'", ICWM_NEW),
        ("Plasma Thermal Mode", "Normal plasma | Cool plasma | Mixed: specify", "Normal plasma | Cool plasma | N/A | None"),
        ("Calibration Strategy per Target Species", "External calibration (all target species)", CS_NEW),
        ("Interfering Species", "ArCl+ on 75As", "e.g., ArCl+ | MoO+ | Ba2+ | None | N/A"),
        ("Acquisition Pass", "e.g., 'Pass 1: LR (M/dm 300)", AP_NEW),
    ],
}
DECISION = ("2026-09-29. Column F of keyed fields describes one member's value (conventions 7.3.4): member "
            "labels removed from the examples of %s. Consumers' Column F is edited to match "
            "(colf_value_only_20260929.py).")


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


def newval(new, old):
    return new(old) if callable(new) else new


def edit_tapp(stem, rr, hits):
    h = rr[0]; iU = h.index("Last Update"); iF = 5
    for k, (field, stems, old, new) in enumerate(TAPP_EDITS):
        if stem not in stems:
            continue
        rows = [r for r in rr[1:] if r and r[0].strip() == field]
        if len(rows) != 1:
            raise SystemExit("PREMISE: %s has %d rows named %r" % (stem, len(rows), field))
        r = rows[0]
        want = newval(new, r[iF])
        if r[iF] == want:              # already delivered (module overlay) — nothing to do
            hits[k].add(stem); continue
        if not r[iF].startswith(old):
            raise SystemExit("PREMISE: %s %r Column F is %r" % (stem, field, r[iF][:90]))
        r[iF] = want; r[iU] = DATE
        hits[k].add(stem)
    return rr


def main(apply=False):
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    stems_needed = set().union(*[s for _, s, _, _ in TAPP_EDITS]) | UPB3
    plan = []
    for e in reg["composed"]:
        stem = os.path.basename(e["tapp"]).rsplit("_TAPP_v", 1)[0]
        if stem in stems_needed:
            new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), e["tapp"])
            plan.append((e, stem, new))
    missing = stems_needed - {s for _, s, _ in plan}
    if missing:
        raise SystemExit("PREMISE: no composed TAPP for %s" % missing)

    # modules: premise-check and stage
    staged = {}
    for mod, edits in MODULE_EDITS.items():
        p = os.path.join(MODULES, "Module_%s.csv" % mod)
        mrows = rows_of(p); iF = mrows[0].index("Example / Allowed Content"); iU = mrows[0].index("Last Update")
        for field, old, new in edits:
            r = [x for x in mrows[1:] if x and x[0].strip() == field]
            if len(r) != 1 or not r[0][iF].startswith(old):
                raise SystemExit("PREMISE: Module_%s %r Column F is %r" % (mod, field, r[0][iF][:90] if r else None))
            r[0][iF] = new; r[0][iU] = DATE
        staged[mod] = (p, mrows)
        print("  Module_%s: %d Column F defaults/overlays" % (mod, len(edits)))

    # dry: TAPP edits against current files (overlay rows are checked after composition on apply)
    hits = [set() for _ in TAPP_EDITS]
    for e, stem, new in plan:
        edit_tapp(stem, rows_of(os.path.join(ROOT, e["tapp"])), hits)
    for k, (field, stems, _, _) in enumerate(TAPP_EDITS):
        if hits[k] != stems:
            raise SystemExit("PREMISE: %r matched %s, expected %s" % (field, sorted(hits[k]), sorted(stems)))
    print("  %d TAPP rows edited across %d TAPPs: %s"
          % (sum(len(h) for h in hits), len(plan), ", ".join(sorted(s for _, s, _ in plan))))
    if not apply:
        print("\n(dry run — pass --apply to write)"); return 0

    newver = {}
    for mod, (p, mrows) in staged.items():
        write(p, mrows)
        jp = os.path.join(MODULES, "Module_%s.json" % mod)
        d = json.load(io.open(jp, encoding="utf-8"))
        d["version"] = newver[mod] = str(int(d["version"]) + 1)
        d.setdefault("decisions", []).append(DECISION % ", ".join(f for f, _, _ in MODULE_EDITS[mod]))
        with io.open(jp, "w", encoding="utf-8") as fh:
            json.dump(d, fh, indent=2, ensure_ascii=False); fh.write("\n")

    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    hits = [set() for _ in TAPP_EDITS]
    for e, stem, new in plan:
        rel = e["tapp"]; np_ = os.path.join(ROOT, new)
        q = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)]
                           + flags(e["modules"]) + ["--out", np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (rel, q.stdout[-1500:], q.stderr[-700:]))
        rr = rows_of(np_)
        if stem in UPB3:                        # the overlay rows arrived by composition
            for field, _, overlay in MODULE_EDITS["UPb"]:
                r = [x for x in rr if x and x[0].strip() == field][0]
                if r[5] != overlay:
                    raise SystemExit("%s: composition did not deliver the %s overlay" % (stem, field))
                r[rr[0].index("Last Update")] = DATE
        write(np_, edit_tapp(stem, rr, hits))
        for f in (os.path.join(ROOT, rel), os.path.join(ROOT, rel)[:-4] + ".xlsx"):
            if os.path.exists(f):
                shutil.move(f, os.path.join(sup, os.path.basename(f)))
        q = subprocess.run([sys.executable, XLSX, np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("xlsx failed %s\n%s" % (new, q.stderr[-700:]))
        print("  wrote %s" % os.path.basename(new))

    rp = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(io.open(rp, encoding="utf-8"))
    news = {os.path.basename(n).rsplit("_v", 1)[0]: n for _, _, n in plan}
    for e in reg["composed"]:
        s = os.path.basename(e["tapp"]).rsplit("_v", 1)[0]
        if s in news:
            e["tapp"] = news[s]
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
