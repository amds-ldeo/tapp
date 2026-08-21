#!/usr/bin/env python3
"""
Draft recommendations for the 12 SolutionIntroduction Column B decisions.

Criteria applied, from the module reconciliation record and Rule 6:
  INSTRUCTION  - does it tell the user what to enter?
  BOUNDARY     - does it fix scope, and separate this field from adjacent ones?
  CONSEQUENCE  - does it say why the value matters, or what it trades off?
Disqualifiers:
  SOURCE LEAK        - commentary about what a paper contains
  TECHNIQUE-SPECIFIC - a module description must not name Q, SF or MC

The technique-specific disqualifier needs a distinction that decided four rows:
naming an ANALYSER ("prior to MC-ICP-MS analysis") is disqualifying, because the
module is consumed by three. Naming a PURPOSE ("for isotope-ratio work") is not
— it is a conditional that is true and useful for any consumer doing that work,
which is what 6.5 contemplates. Several MC variants carry excellent consequence
content wrapped in analyser-naming; those are adopted with the wrapper removed
rather than rejected.

Writes Winner / Rationale / Adopted description into the worksheet.
NOTHING IS APPLIED TO THE MODULE — this is a review artifact.
"""
import csv
from pathlib import Path

ROOT = Path("/Users/ruolin/Documents/Astromat/TAPPs")
WS = ROOT / "SolutionIntroduction_Reconciliation_WORKSHEET.csv"

REC = {
"Sample Aliquot Mass or Volume": (
    "Q/SF", "LOW",
    "MC narrows the back-calculation clause to 'in isotope dilution procedures'. That is one use "
    "case among several — the mass is equally needed for straight concentration work. Q/SF is the "
    "more general statement and already covers ID. Nothing is lost.",
    "Mass (mg) of solid material digested or volume (mL) of liquid taken for dissolution. Used for "
    "yield calculations and concentration back-calculation."),

"Number of Digestion Steps": (
    "synthesized (Q/SF + MC)", "LOW",
    "Both variants are identical except for the worked example, and the two examples give the two "
    "canonical reasons a second step is needed: refractory residue (Q/SF) and fluoride-complex "
    "destruction (MC). Neither subsumes the other, so both are kept.",
    "Total number of distinct acid digestion steps required to dissolve the sample. Some procedures "
    "require multiple sequential steps — for example, an initial open-beaker HF–HNO3 dissolution "
    "followed by a second closed-vessel step for residues retaining refractory minerals, or by an "
    "aqua regia reflux to destroy fluoride complexes."),

"Digestion Vessel Type": (
    "SF/MC", "LOW",
    "SF and MC add a concrete consequence — which vessel class is required for complete silicate "
    "digestion — that tells the user how to choose. Q states only that vessel type matters, without "
    "saying what follows from it.",
    "Type of vessel used for acid digestion. Vessel type constrains maximum temperature and pressure "
    "and determines suitability for refractory mineral dissolution (e.g., Parr bombs required for "
    "complete silicate digestion at high temperatures)."),

"Digestion Acid(s)": (
    "MC", "LOW",
    "MC is a strict superset of SF and adds real consequence content: incomplete dissolution "
    "fractionates isotopes. The clause is conditional ('for isotope ratio work'), naming a purpose "
    "rather than an analyser, so it generalises to any consumer doing that work.",
    "Acid mixture used for sample dissolution. Record acid type(s) and concentration(s) where known "
    "(e.g., concentrated HF–HNO3 in Parr bombs is standard for silicate dissolution). For "
    "isotope-ratio work, complete matrix dissolution is required to avoid isotopic fractionation "
    "during partial dissolution."),

"Chromatographic Separation Applied": (
    "synthesized (SF + MC, generalised)", "HIGH — please read",
    "MC has by far the best reasoning — it says WHY separation is needed (variable mass bias, "
    "isobaric interference) where Q/SF only say it is common. But MC names the analyser twice "
    "('prior to MC-ICP-MS analysis', 'mandatory for solution MC-ICP-MS'), which disqualifies it as "
    "module text. Adopted here is SF's general frame carrying MC's reasoning, with the analyser "
    "references converted to the purpose they actually denote. This is the row where a separation "
    "chemist may disagree with the phrasing 'usually mandatory for isotope-ratio procedures'.",
    "Whether chromatographic separation of element groups (e.g., using ion exchange resin) was "
    "performed prior to analysis. Separation may be required to remove matrix elements that cause "
    "variable mass bias, to eliminate isobaric interferences, or to isolate an element group before "
    "measurement (e.g., Fe and Cu–Zn for isotope dilution, Hf separation from REE, removal of Cr and "
    "Ni from Fe fractions). It is usually mandatory for isotope-ratio procedures and optional for "
    "concentration measurement. Record resin type and elution matrix conditions if applied. Record "
    "'None' if the direct digestion solution is analyzed."),

"Final Solution Matrix": (
    "synthesized (MC + SF, generalised)", "MEDIUM",
    "MC contributes the strongest consequence in the whole module — molarity must be matched between "
    "samples and bracketing standards or mass bias shifts. SF contributes a second real fact, that "
    "trace HF may be added to keep HFSE in solution, but wraps it in 'some SF-ICP-MS procedures', "
    "which names an analyser. Both facts are kept, both generalised.",
    "Acid type and concentration of the final dissolved sample solution introduced to the instrument. "
    "Directly affects instrument response and ion transmission. For isotope-ratio procedures, acid "
    "molarity must be precisely matched between samples and bracketing standards to avoid "
    "matrix-induced mass bias offsets. Procedures targeting HFSE may add trace HF to the final "
    "solution to keep those elements in solution."),

"Nebulizer Type": (
    "Q", "MEDIUM — boundary issue",
    "This is the one case where the majority variant is the worse one. SF and MC say the nebulizer "
    "'affects droplet size distribution and uptake rate' — but `Sample Uptake Rate` is a separate "
    "field in this same module, so that wording blurs the boundary between two adjacent fields. Q's "
    "'sample introduction efficiency' names the property the nebulizer actually governs and keeps "
    "the two distinct. 2-of-3 agreement is not evidence here.",
    "Type and material of the pneumatic nebulizer used for sample introduction. Affects droplet size "
    "distribution and sample introduction efficiency."),

"Spray Chamber Type and Cooling Temperature": (
    "MC (trimmed)", "LOW",
    "MC adds two clauses. The second is genuine boundary content — it explains that a spray chamber "
    "may sit downstream of a desolvating nebulizer, which is how this field relates to `Desolvation "
    "System`. The first ('Scott double-pass and cyclonic are standard') merely restates Column F and "
    "is dropped, per 6.4.",
    "Type of spray chamber and cooling temperature if thermostatted (°C). Chamber type and "
    "temperature control aerosol droplet size and the solvent vapor load reaching the plasma. In some "
    "procedures a spray chamber is placed downstream of a desolvating nebulizer to improve signal "
    "stability."),

"Desolvation System": (
    "synthesized (MC, generalised)", "MEDIUM",
    "MC alone states the TRADE-OFF — desolvation buys sensitivity but costs mass bias stability — "
    "which is the most valuable kind of consequence content because it tells the user when not to "
    "use it. Its 'Frequently used in MC-ICP-MS' wrapper is removed. Q's ApexQ and SF's Aridus-I "
    "product examples are dropped from the description; Column F already lists both.",
    "Desolvating nebulizer or membrane desolvator used upstream of the plasma to reduce solvent load. "
    "Lowers oxide production rates and increases sensitivity, and is commonly used for low-abundance "
    "analytes or small sample sizes. Note the trade-off: desolvation can introduce additional "
    "instrumental mass bias instability relative to wet plasma introduction. Record 'None' if not "
    "used."),

"Nebulizer Gas Flow Rate": (
    "MC", "LOW",
    "MC adds 'and stability. Adjusted daily to optimize signal.' That is instruction content, and it "
    "is also the justification for the field's D=Editable tier — it tells the analyst this is a "
    "session-tuned parameter rather than a fixed procedure commitment.",
    "Flow rate of the carrier argon gas delivered through the nebulizer (L/min). Controls aerosol "
    "transport and strongly influences signal sensitivity and stability. Adjusted daily to optimize "
    "signal."),

"Wash Time Between Samples": (
    "MC", "LOW",
    "MC adds a conditional consequence — incomplete washout cross-contaminates samples of differing "
    "isotopic composition — that names a purpose, not an analyser, and is equally true of isotope "
    "dilution work on a quadrupole.",
    "Duration of instrument rinse between successive sample solutions (seconds). Controls carryover "
    "and memory effects. For isotope-ratio work, complete washout is critical to prevent "
    "cross-contamination between samples with differing isotopic compositions."),

"Internal Standard Concentration": (
    "Q/SF", "LOW",
    "MC renames the subject to 'the internal normalization standard element' — 'normalization' is "
    "MC mass-bias terminology, and the singular excludes the multi-element internal standardization "
    "that is routine on Q and SF. Q/SF's wording also matches the field name. Minor residue: "
    "'(µg/L or ppb)' duplicates the Data Type `Numeric (µg/L)`; worth dropping when the module is "
    "next edited, but not changed here.",
    "Target concentration of internal standard element(s) in all measured solutions (µg/L or ppb)."),
}


def main():
    rows = list(csv.DictReader(open(WS, encoding="utf-8-sig")))
    cols = list(rows[0].keys())
    if "Attention" not in cols:
        cols.insert(cols.index("Rationale"), "Attention")
    n = 0
    for r in rows:
        r.setdefault("Attention", "")
        f = r["Field"]
        if f in REC:
            winner, attn, rationale, adopted = REC[f]
            r["Winner"], r["Attention"] = winner, attn
            r["Rationale"], r["Adopted description"] = rationale, adopted
            n += 1
        elif r["Status"].startswith(("NO DECISION", "PRE-DECIDED")):
            r["Attention"] = "resolved"
    with open(WS, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"drafted {n} recommendations into {WS.name}\n")
    for r in rows:
        if r["Field"] in REC:
            print(f"  {r['Attention'][:22]:22s} {r['Field'][:42]:42s} -> {r['Winner']}")


if __name__ == "__main__":
    main()
