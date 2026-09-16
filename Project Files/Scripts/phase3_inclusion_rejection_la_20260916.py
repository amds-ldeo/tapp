#!/usr/bin/env python3
"""Phase 3 for `Analysis Inclusion and Rejection Criteria` — batch 2: the laser-ablation family
(26 cells, 4 TAPPs).

    python3 "Project Files/Scripts/phase3_inclusion_rejection_la_20260916.py" [--apply]

Same two rules as batch 1 (unit = individual result; the split with signal filtering is by basis),
and this corpus is where they bite hardest. Three cases worth naming, because each would be an easy
error:

  * MITTLEFEHLDT 2024 states the fullest inclusion/rejection rule in the library — automatic filters
    on analysis sums and stoichiometry, Grubb's test at p<0.01 to reject and p<0.05 to tag, an
    arbitrary FeO ceiling for one weathered meteorite, and a zoning profile dropped from a mean. All
    of it is stated for the EMPA data (p.3). This is the LA-ICP-MS column, and the no-borrowing rule
    applies: the LA cell records what the paper says about the LA data, not the microprobe's filters.
  * CHERNONOZHKIN 2021 drops whole results — "where significant spikes in individual transient
    LA-ICP-MS signals were observed ..., results were not included in Table 1" (p.6). Whole results,
    but the basis is the signal, so it belongs to `Spike / Outlier Filtering Approach` and the cell
    here says so.
  * ZHANG 2022 excludes two meteorites "from the fractional-crystallization modeling" (p.5). That is
    an interpretive exclusion downstream of the reported values, not a rule about which results make
    them, and the cell says which it is.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-16"
FIELD = "Analysis Inclusion and Rejection Criteria"

NAKANISHI = ("Partially — the contributing counts are stated per grain, the reported ratios being \"the mean Re/Os "
             "abundance ratios for each of the 1–3 analytical spots measured by LA-ICP-MS\" (p.8). No acceptance or "
             "rejection rule is stated for the LA data; the 233/235 > 0.2 rejection (p.4) is a rule for the N-TIMS Os "
             "measurements, not for these spot analyses, and is not borrowed")
LIU2024 = ("Partially — each reported value is the mean of a stated count, \"fs-LA-ICP-MS (n = 9 spots)\" against "
           "\"SN-ICP-MS (n = 5)\" (Table 2, p.8), with a 95% confidence interval. No acceptance or rejection rule, and "
           "no acquired-versus-included count, is stated")
LIU2025 = ("N — no rule for admitting or rejecting individual results is stated. The one documented exclusion is at "
           "sample level and before analysis: \"Capsules that had lost significant weight were discarded\" after the "
           "leak check (p.2)")
LIU2016 = ("Partially — the reported values are means of stated counts (\"n = 7\", \"n = 13\", table p.9). No "
           "acceptance or rejection rule is stated; the plateau-region screening of each spot is signal-based and is "
           "recorded under Spike / Outlier Filtering Approach")
BZHANG = ("Partially — the rule stated is one of combination rather than rejection: for Ge, Sb, Re, Os and Ir the "
          "reported value is \"calculated from the mean of the spot average (Appendix 2) and the raster average in "
          "this table\" (Table 3 note, p.4). No acceptance or rejection rule for individual results is stated. The "
          "exclusion of \"Binya and Fitzwater Pass ... from the fractional-crystallization modeling of group IIIF\" "
          "(p.5) is an interpretive exclusion downstream of the reported values, not a rule about which results make "
          "them")
CHERN_SIGNAL = ("N — whole results are dropped, but on signal grounds: \"where significant spikes in individual "
                "transient LA-ICP-MS signals were observed (e.g. Ca in CMS 04071 and Seymchan and Ni in Brahin and "
                "Seymchan), results were not included in Table 1\" (p.6). By basis that belongs to Spike / Outlier "
                "Filtering Approach; no result-based selection rule is stated")
CHERN_MAP = (CHERN_SIGNAL + ". For the maps, \"The P-rich veinlets were excluded from the maps prior to the "
             "calculation of the correlation coefficients\" (appendix C), which masks pixels within a result rather "
             "than admitting or excluding results")
MITTLE = ("Partially — the reported values are averages per meteorite (Table E4 of the data file), with the complete "
          "set of analyses also released (p.6); trace-element chromatograms were \"scrutinized for unanticipated "
          "interferences, improperly chosen backgrounds or other problems\" (p.5). No acceptance or rejection rule is "
          "stated for the LA data. The paper's detailed filters — analysis sums 100 ± 2%, stoichiometry limits, "
          "Grubb's test rejecting at p<0.01 and tagging at p<0.05, an FeO ceiling of 17.5 wt% for Phillips County, and "
          "a zoning profile excluded from that mean — are stated for the EMPA data (p.3) and are not borrowed here")
NAVARRO_SP = ("N — no acceptance or rejection rule and no contributing count are stated; the reported bulk composition "
              "is the integration of the acquired signal rather than a selection among results")
NAVARRO_MAP = ("Partially — the reported values integrate a stated number of points per phase, \"176 kamacite points "
               "(211,060 µm2) and 1,173 plessite points (1,712,297 µm2)\" (Table 5, p.12). The points are assigned to "
               "a phase rather than admitted or rejected, and no rejection rule is stated")

LAQ = {"Nakanishi": NAKANISHI, "Liu et al. 2024": LIU2024,
       "Liu et al. 2025 (GCA 393) Experimental silicate glass": LIU2025,
       "Liu et al. 2025 (GCA 393) Experimental sulfide": LIU2025,
       "Liu et al. 2016 (M&PS 51) Tissint martian meteorite Silicates": LIU2016,
       "Liu et al. 2016 (M&PS 51) Tissint martian meteorite Phosphate": LIU2016}
LASF = {"Zhang et al. 2022 (GCA 323)": BZHANG,
        "Chernonozhkin et al. 2021 (Chem Geol 562) Pallasite olivine Raster": CHERN_MAP,
        "Chernonozhkin et al. 2021 (Chem Geol 562) Pallasite olivine Line": CHERN_SIGNAL,
        "Chernonozhkin et al. 2021 (Chem Geol 562) Pallasite phosphate": CHERN_SIGNAL,
        "Mittlefehldt": MITTLE,
        "Navarro et al. 2024 (ACS ESC 8) Iron meteorites Spot": NAVARRO_SP,
        "Navarro et al. 2024 (ACS ESC 8) Iron meteorites Raster": NAVARRO_MAP}

CELLS = {
 "LA-Q-ICP-MS/LA-Q-ICP-MS_TAPP_v87.csv": dict(LAQ),
 "LA-Q-ICP-MS/LA-Q-ICP-MS_UPb_TAPP_v87.csv": dict(LAQ),
 "LA-SF-ICP-MS/LA-SF-ICP-MS_TAPP_v84.csv": dict(LASF),
 "LA-SF-ICP-MS/LA-SF-ICP-MS_UPb_TAPP_v85.csv": dict(LASF),
}


def col(header, key):
    k = " ".join(key.split()).lower()
    hits = [i for i, h in enumerate(header) if " ".join(h.split()).lower().startswith(k)]
    if len(hits) != 1:
        raise SystemExit("column key %r matched %d columns" % (key, len(hits)))
    return hits[0]


def main(apply=False):
    plan = []
    for rel, cells in CELLS.items():
        rows = list(csv.reader(io.open(os.path.join(ROOT, rel), newline="", encoding="utf-8-sig")))
        h = rows[0]; s = h.index("Literature Assessment")
        lit = [i for i in range(s + 1, len(h)) if h[i].strip()]
        row = next(r for r in rows if r and r[0].strip() == FIELD)
        m = {col(h, k): v for k, v in cells.items()}
        if len(m) != len(cells):
            raise SystemExit("%s: two keys matched one column" % rel)
        unhandled = [" ".join(h[i].split())[:60] for i in lit if i not in m and not row[i].strip()]
        if unhandled:
            raise SystemExit("%s: blank columns with no value: %s" % (rel, unhandled))
        for i, v in m.items():
            if row[i].strip():
                raise SystemExit("REFUSING: %s %s already holds %r" % (rel, h[i][:40], row[i][:60]))
            row[i] = v
        new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), rel)
        plan.append((rel, new, rows, len(m)))
        print("  %-40s %2d cells -> %s" % (os.path.basename(rel), len(m), os.path.basename(new)))
    print("\n  %d cells in %d TAPPs" % (sum(p[3] for p in plan), len(plan)))
    if not apply:
        print("(dry run — pass --apply to write)"); return 0

    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    rp = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(io.open(rp, encoding="utf-8"))
    for rel, new, rows, _ in plan:
        with io.open(os.path.join(ROOT, new), "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rows)
        subprocess.run([sys.executable, XLSX, os.path.join(ROOT, new)], cwd=ROOT, check=True,
                       capture_output=True, text=True)
        old = os.path.join(ROOT, rel)
        for f in (old, old[:-4] + ".xlsx"):
            if os.path.exists(f): shutil.move(f, os.path.join(sup, os.path.basename(f)))
        next(e for e in reg["composed"] if e["tapp"] == rel)["tapp"] = new
    with io.open(rp, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    p = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", "sync_current_tapps.py"),
                        "--apply"], cwd=ROOT, capture_output=True, text=True)
    print("  written; parked; registry advanced; mirror:", (p.stdout.strip().splitlines() or ["synced"])[-1][:70])
    return 0


sys.exit(main("--apply" in sys.argv))
