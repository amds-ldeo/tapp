#!/usr/bin/env python3
"""EPMA: assess the remaining blank literature cells (2026-09-29).

    python3 "Project Files/Scripts/epma_remaining_fields_20260929.py" [--apply]

Finishes EPMA's literature assessment, part of finishing EPMA before its v85-edition documents are
written. Every value is read from the paper (EPMA methods, table notes, acknowledgements, data
availability) and written in the keyed-value notation (conventions 7.3.4).

Lab-internal fields — sampled first, per references/lit_assessment.md:
  * Laboratory ID and Procedure Start Date: 0 of 12 papers state them. Left BLANK by decision, as
    for Session Identifier; they are what registration exists to capture.
  * Funding Source for Procedure Development: 3 of 12 state facility or instrument support (the Caltech
    GPS facility's NSF grants in Ma+2015 and Ma+2017; K-ALFAA operations and instrumentation in
    Zega+2025). Assessed: those three filled, `N` elsewhere.
The other session-only identifiers (Procedure DOI, Session Identifier, analysis dates, Coupled
Procedure DOI) stay blank by the 2026-09-16 decision.

Also corrected on the way:
  * Neuman+2025's k-ratio sat in Normalization / Standards-Based Correction; it is the calibration
    factor, and moves to Calibration Factor and Determination Method.
  * Liu+2016_Cal's inclusion cell cited "mineral means (n = 7, n = 13)": those are Table 3's LA-ICP-MS
    averages (ppm). The microprobe averages are the two glass rows, "EMP avg (n = 73)" and "avg (n = 14)".
  * Barnes+2025 (both) and Neuman+2025 had `N` for study funding although the acknowledgements state it.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-29"
D = " — "
ALL = ["Ma+2015", "Hu+2020", "Liu+2016_UT", "Liu+2016_Cal", "Ma+2017", "Frank+2023", "Broussard+2026", "Seifert+2026",
       "Pang+2016", "McCoy+2025_SI", "McCoy+2025_UA", "Zega+2025", "Barnes+2025#JEOL", "Barnes+2025#Cameca", "Neuman+2025"]
WDS_STATED = {"Ma+2015", "Ma+2017", "Broussard+2026", "Pang+2016", "McCoy+2025_UA", "Neuman+2025"}
OSIRIS = "NASA NNH09ZDA007O under contract NNM10AA11C (New Frontiers Program)"
MA15_OX = "SiO2, TiO2, Al2O3, FeO, MgO, CaO, Na2O, K2O, Cr2O3, MnO"
MA17_OX = "SiO2, TiO2, Al2O3, FeO, CaO, Na2O, K2O"
LIU_OX = "SiO2, TiO2, Al2O3, Cr2O3, MgO, CaO, MnO, FeO, NiO, Na2O, K2O, P2O5"
LIU_T3 = "Table 3: 'Glass inclusion EMP avg (n = 73) 1σ' and the impact-melt 'avg (n = 14) 1σ', whose average 'only included the glassy regions of the impact melt pockets'"

# field -> {column: value}; "*" = every column not otherwise listed, but only where the cell is blank
EDITS = {
  "Funding Source for Procedure Development": {
    "Ma+2015": "NSF EAR-0318518; NSF DMR-0080065" + D + "'SEM, EBSD and EPMA analyses were carried out at the Caltech GPS Division Analytical Facility, which is supported, in part, by NSF Grants EAR-0318518 and DMR-0080065'",
    "Ma+2017": "NSF EAR-0318518; NSF EAR-1322082; NSF DMR-0080065" + D + "'SEM, EBSD, EPMA, and Raman measurements were carried out at the Geological and Planetary Science Division Analytical Facility at Caltech, which is supported in part by NSF grants EAR-0318518, EAR-1322082, and DMR-0080065'",
    "Zega+2025": ("NASA Planetary Science Enabling Facilities 80NSSC23K0327; NASA Planetary Major Equipment NNX12AL47G and "
                  "NNX15AJ22G; NASA Early Career Award 80NSSC20K1087; NSF Major Research Instrumentation 1531243 and 0619599; "
                  "Gordon and Betty Moore Foundation; State of Arizona Technology and Research Initiative Fund" + D +
                  "acknowledged 'for supporting K-ALFAA operations' and 'for supporting the instrumentation in K-ALFAA'; "
                  "which award bought the microprobe is not stated"),
    "*": "N",
  },
  "Funding Source for Analysis": {
    "Ma+2015": "DOE Cooperative Agreement DE-NA0001982; NSF EAR 322082; NASA NNN13D465T; NASA Cosmochemistry NNX11AG58G and NNX12AH63G; NSF EAR 1344942 and 1440005" + D + "acknowledged author by author for the study as a whole; none is attributed to the microprobe work",
    "Hu+2020": "NSFC 41573057, 41430105 and 41973062; China Scholarship Council 201804910284; IGGCAS key research program IGGCAS-201905" + D + "'This study was financially supported by ...'",
    "Liu+2016_UT": "NASA Cosmochemistry NNX11AG58G and NNN13D465T; NSF EAR-1226270; NSF EAR-1019770" + D + "'We acknowledge partial support by ...'",
    "Liu+2016_Cal": "NASA Cosmochemistry NNX11AG58G and NNN13D465T; NSF EAR-1226270; NSF EAR-1019770" + D + "'We acknowledge partial support by ...'",
    "Ma+2017": "NNSA Stewardship Science Academic Alliances, DOE Cooperative Agreements DE-NA0001982 and DESC0005278; NASA NNX12AJ01G" + D + "'This work was supported in part by ...'",
    "Frank+2023": "NASA NNX11AG78G, 13-COS13-0026, NNX14AI19G and 80NSSC18K0586; NASA Cosmochemistry and Emerging Worlds Programs" + D + "'This work was supported by ...'",
    "Broussard+2026": "NASA 80NSSC22K1689; NASA 80NSSC24K1284; McDonnell Center for the Space Sciences" + D + "'Individual funding was provided by ...'",
    "Seifert+2026": OSIRIS + "; NASA Postdoctoral Program" + D + "acknowledgements",
    "Pang+2016": "NSFC 41373065; State Key Laboratory for Mineral Deposits Research ZZKT-201322; Fundamental Research Funds for the Central Universities" + D + "'This study was supported by grants from ...'",
    "McCoy+2025_SI": OSIRIS + D + "'This material is based on work supported by ...'; individual grants are also listed by person (80NSSC22K1692, MR/T020261/1, ST/V000675/1, 22EXPOSITO)",
    "McCoy+2025_UA": OSIRIS + D + "'This material is based on work supported by ...'; individual grants are also listed by person (80NSSC22K1692, MR/T020261/1, ST/V000675/1, 22EXPOSITO)",
    "Zega+2025": OSIRIS + D + "'This material is based upon work supported by ...'; the K-ALFAA facility and instrumentation support is under Funding Source for Procedure Development",
    "Barnes+2025#JEOL": OSIRIS + D + "acknowledged with the named authors; further grants are listed by person across many laboratories, and none is attributed to the microprobe work",
    "Barnes+2025#Cameca": OSIRIS + D + "acknowledged with the named authors; further grants are listed by person across many laboratories, and none is attributed to the microprobe work",
    "Neuman+2025": "NASA ANGSA program 80NSSC19K0958" + D + "'We thank NASA for support of the ANGSA program (Grant 80NSSC19K0958)'",
  },
  "Coupled Dataset or Publication Reference": {
    "Hu+2020": "https://doi.org/10.1016/j.gca.2020.07.021" + D + "'Supplementary data to this article can be found online at ...'",
    "Frank+2023": "same submission" + D + "'All data are included within the manuscript'",
    "Broussard+2026": "N" + D + "'The data that support the findings of this study are available from the corresponding author upon reasonable request'",
    "Seifert+2026": "astromat.org, at the DOIs in Table S1" + D + "'Instrument data products that support the findings of this study will be available via astromat.org at the DOIs given in Table S1'",
    "Pang+2016": "Supplementary Information at www.nature.com/srep" + D + "'Supplementary information accompanies this paper at http://www.nature.com/srep'; the EPMA data are in Supplementary Tables 1–4",
    "McCoy+2025_SI": "astromat.org, at the DOIs in Extended Data Table 3" + D + "'Instrument data supporting the experimental results from the samples analysed in this study will be available from Astromat (astromat.org) at the DOIs listed in Extended Data Table 3'",
    "McCoy+2025_UA": "astromat.org, at the DOIs in Extended Data Table 3" + D + "as for the Smithsonian procedure",
    "Neuman+2025": "Ogliore (2025)" + D + "'The quantitative EPMA image data and coregistered image sets are available in Ogliore (2025)'",
    "*": "N",
  },
  "Sample Persistent Identifier": {
    "Ma+2017": "USNM 7619" + D + "Smithsonian catalogue number: 'The Zagami thin section (USNM 7619)'; no IGSN",
    "Seifert+2026": "OREX-803079-0; OREX-803080-0" + D + "NASA curation numbers of the mounts, not IGSN",
    "*": "N",
  },
  "Normalization / Standards-Based Correction": {"Neuman+2025": "N" + D + "the k-ratio is the calibration, and is under Calibration Factor and Determination Method"},
  "Calibration Factor and Determination Method": {
    "Neuman+2025": ("all: k-ratio against the calibration standard" + D + "'the k-ratio (k = (P-B)smp/(P-B)std) is the background "
                    "corrected relative peak X-ray intensity (P-B) at each pixel in the map compared to the calibration standard', "
                    "with 'C = k × ZAF'"),
    "*": "N",
  },
  "Constants and Reference Values Used": {"*": "N"},
  "EDS Acquisition Mode": {"*": None},          # filled below: N/A where WDS is stated, else N
  "Interfering Elements": {"*": "N"},
  "Interference Correction Standard": {
    "Hu+2020": "N" + D + "the Cr Kb correction on Mn Ka is stated, but no correction standard is named", "*": "N"},
  "Procedural Blank Level": {"*": "N/A" + D + "no chemical separation, so there is no procedural blank"},
  "Other Statistics": {"*": "N"},
  "Combined Results": {
    "Ma+2015": ("wormy type tissintite (n = 6); maskelynite associated with wormy tissintite (n = 6); rimming tissintite "
                "(n = 6); maskelynite associated with rimming tissintite (n = 9); maskelynite away from melt pockets (n = 17); "
                "pigeonite surrounding tissintite (n = 7); fayalite surrounding tissintite (n = 5)" + D + "the columns of Table 1"),
    "Ma+2017": ("type liebermannite (n = 6); the second liebermannite (n = 2); the third liebermannite (n = 3); lingunite next "
                "to type liebermannite (n = 3); maskelynite near type liebermannite (n = 5); maskelynite near the 2nd "
                "liebermannite (n = 4)" + D + "the columns of Table 1, where the paper prints 'Maskeleyite'"),
    "Liu+2016_UT": "glass inclusion average (n = 73); impact-melt glass average (n = 14)" + D + LIU_T3,
    "Liu+2016_Cal": "glass inclusion average (n = 73); impact-melt glass average (n = 14)" + D + LIU_T3,
    "Broussard+2026": "dolomite (n = 37); magnesite (n = 23)" + D + "'Dolomite contains 2.0 ± 0.4 wt% Fe and 3.0 ± 0.9 wt% Mn (n = 37)'; 'Magnesite contains 14.5 ± 2.7 wt% Fe and 4.6 ± 2.5 wt % Mn (n = 23)'",
    "Pang+2016": ("orthopyroxene (n = 12); augite (n = 14); clinopyroxene in the eclogitic assemblage of zoned veins (n = 13); "
                  "clinopyroxene in thin melt veins and edge zones (n = 19)" + D + "'based on 12 analyses', '14 analyses' (p.2); "
                  "Ca-Esk components '41 ± 8 mol% on average; based on 13 analyses' in the former, '34 ± 7 mol% on average; 19 "
                  "analyses' in the latter (p.4)"),
    "Seifert+2026": "N" + D + "Table 1 reports one column per apatite grain; no combined value is stated",
    "*": "N",
  },
  "Combination Method": {
    "Ma+2015": MA15_OX + ": mean of n point analyses per phase and textural setting; other: N" + D + "Table 1 notes a and b",
    "Ma+2017": MA17_OX + ": mean of n point analyses per occurrence; other: N" + D + "Table 1 notes b and c",
    "Liu+2016_UT": LIU_OX + ": average of n microprobe analyses per glass type; other: N" + D + LIU_T3,
    "Liu+2016_Cal": LIU_OX + ": average of n microprobe analyses per glass type; other: N" + D + LIU_T3,
    "Broussard+2026": "Element concentrations in the carbonates: mean per carbonate phase; other: N" + D + "dolomite n = 37, magnesite n = 23 (p.5)",
    "Pang+2016": ("En, Fs, Wo: average per pyroxene phase; Ca-Eskola component: average per clinopyroxene setting; other: N"
                  + D + "'The average compositions ... of orthopyroxene ... based on 12 analyses'; 'Ca-Esk components (41 ± 8 mol% on average; based on 13 analyses)'"),
    "*": "N",
  },
  "Goodness-of-Fit or Dispersion Statistic": {
    "Ma+2015": MA15_OX + ": one standard deviation of the mean; other: N" + D + "Table 1 note b: 'Errors given inside parentheses are one standard deviation of the mean based on all of the analyses'",
    "Ma+2017": MA17_OX + ": one standard deviation of the mean; other: N" + D + "Table 1 note c, same wording",
    "Liu+2016_UT": LIU_OX + ": 1σ, one standard deviation of the average; other: N" + D + "Table 3 note b: '1σ is 1 standard deviation of the average'",
    "Liu+2016_Cal": LIU_OX + ": 1σ, one standard deviation of the average; other: N" + D + "Table 3 note b",
    "Broussard+2026": "N" + D + "the carbonate means are given as '±' values ('2.0 ± 0.4 wt% Fe') without naming the statistic",
    "Pang+2016": "N" + D + "the averages are given as '±' values ('41 ± 8 mol%') without naming the statistic",
    "*": "N",
  },
  "Target Material of Sampling Unit": {
    "Ma+2015": "each unit is named by its material: tissintite (wormy, rimming), maskelynite (three settings), pigeonite, fayalite" + D + "Table 1",
    "Ma+2017": "liebermannite (type, second and third occurrences); lingunite (next to type liebermannite); maskelynite (near type and near second liebermannite)" + D + "Table 1",
    "Seifert+2026": "Phosphate (apatite) for every grain, Ap. #1 onward" + D + "Table 1",
    "*": "N",
  },
  "Analysis Inclusion and Rejection Criteria": {
    "Liu+2016_Cal": ("Partially — contributing counts are stated for the glass averages ('EMP avg (n = 73)' and 'avg (n = 14)', Table 3, p.9). "
                     "No acceptance or rejection rule is stated. The table's n = 7 and n = 13 are LA-ICP-MS averages, not microprobe ones"),
  },
}
OVERWRITE_OK = {  # cells that hold a value and are deliberately rewritten
    ("Funding Source for Analysis", "Barnes+2025#JEOL"), ("Funding Source for Analysis", "Barnes+2025#Cameca"),
    ("Funding Source for Analysis", "Neuman+2025"), ("Coupled Dataset or Publication Reference", "Neuman+2025"),
    ("Normalization / Standards-Based Correction", "Neuman+2025"), ("Calibration Factor and Determination Method", "Neuman+2025"),
    ("Analysis Inclusion and Rejection Criteria", "Liu+2016_Cal"),
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


def columns(h):
    s = h.index("Literature Assessment"); out = {}
    for j in range(s + 1, len(h)):
        lab = h[j].replace("\n", " ")
        if not lab.strip():
            continue
        key = lab.split("|")[0].strip()
        if key == "Barnes+2025":
            key += "#JEOL" if "JEOL" in lab else "#Cameca"
        out[key] = j
    assert sorted(out) == sorted(ALL), sorted(out)
    return out


def edit(rr, report):
    cols = columns(rr[0]); by = {r[0].strip(): r for r in rr[1:] if r and r[0].strip()}
    for f, spec in EDITS.items():
        r = by[f]
        for c in ALL:
            j = cols[c]; old = r[j]
            if c in spec:
                v = spec[c]
            elif "*" in spec and not old.strip():
                v = spec["*"]
            else:
                continue
            if f == "EDS Acquisition Mode":
                if old.strip():
                    continue
                v = ("N/A" + D + "WDS procedure") if c in WDS_STATED else ("N" + D + "WDS or EDS is not stated")
            if old.strip() and old != v and (f, c) not in OVERWRITE_OK and c in spec:
                raise SystemExit("PREMISE: [%s] %s already holds %r" % (c, f, old[:60]))
            if old != v:
                report.append((c, f, old, v)); r[j] = v
    return rr


def main(apply=False):
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    e = next(x for x in reg["composed"] if os.path.basename(x["tapp"]).startswith("EPMA_TAPP_v"))
    rel = e["tapp"]; new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), rel)
    report = []
    edit(rows_of(os.path.join(ROOT, rel)), report)
    print("  %s -> %s: %d cells" % (os.path.basename(rel), os.path.basename(new), len(report)))
    if "--show" in sys.argv:
        for c, f, old, v in report:
            print("  [%s] %s\n      was: %s\n      now: %s" % (c, f, old[:100], v[:140]))
    if not apply:
        print("\n(dry run — pass --apply to write; --show lists every change)"); return 0
    np_ = os.path.join(ROOT, new)
    q = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)] + flags(e["modules"])
                       + ["--out", np_], cwd=ROOT, capture_output=True, text=True)
    if q.returncode != 0:
        raise SystemExit("compose failed\n%s\n%s" % (q.stdout[-1500:], q.stderr[-700:]))
    write(np_, edit(rows_of(np_), []))
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE)
    for f in (os.path.join(ROOT, rel), os.path.join(ROOT, rel)[:-4] + ".xlsx"):
        shutil.move(f, os.path.join(sup, os.path.basename(f)))
    q = subprocess.run([sys.executable, XLSX, np_], cwd=ROOT, capture_output=True, text=True)
    if q.returncode != 0:
        raise SystemExit("xlsx failed\n%s" % q.stderr[-700:])
    rp = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(io.open(rp, encoding="utf-8"))
    for x in reg["composed"]:
        if x["tapp"] == rel:
            x["tapp"] = new
    with io.open(rp, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    for s in ("build_module_register.py", "sync_current_tapps.py", "build_schema_spec_counts.py"):
        q = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", s), "--apply"],
                           cwd=ROOT, capture_output=True, text=True)
        print("  %s: %s" % (s, (q.stdout.strip().splitlines() or ["ok"])[-1][:90]))
    return 0


sys.exit(main("--apply" in sys.argv))
