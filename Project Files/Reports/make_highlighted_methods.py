#!/usr/bin/env python3
"""
Produce a highlighted copy of EPMA_Reference_Methods_Section_v77.md in which every
span of text that fills an EPMA TAPP field is wrapped in <mark>...</mark>.

Highlighted = information a TAPP field asks for (values, choices, identifiers, rules
and outcomes). Not highlighted = connective prose, pointers to tables and supplements,
rationale that is not part of a field, and context the TAPP does not ask for.

Spans are located as (context, span, occurrence) in the clean text, then inserted from
the end backwards, so the clean file stays the single source. The script fails if a
context is missing or if two spans overlap. Table 1 data cells are all TAPP values
and are highlighted cell by cell.
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'EPMA_Reference_Methods_Section_v77.md')
OUT = os.path.join(HERE, 'EPMA_Reference_Methods_Section_v77_highlighted.md')

# (context, span-within-context or None for the whole context, occurrence of context)
M = [
 # 2.1
 ('epoxy mounts', None, 0), ('of carbonaceous-chondrite material', None, 0),
 ('EX-CC-01 (IGSN:EXAMPLE0001)', 'EX-CC-01', 0), ('IGSN:EXAMPLE0001', None, 0),
 ('EX-CC-02 (IGSN:EXAMPLE0002)', 'EX-CC-02', 0), ('IGSN:EXAMPLE0002', None, 0),
 ('olivine and pyroxene, Fe–Ti–Cr oxides (magnetite, chromite, ilmenite), sulfides (pyrrhotite, pentlandite), phosphates (apatite, merrillite) and carbonates (calcite, dolomite, breunnerite)', None, 0),
 ('dry-polished with diamond to a final 0.25 µm and carbon coated to 20 nm', None, 0),
 ('additionally Ar-ion polished after the final diamond step', None, 0),
 ('Particle P2 of that mount was partly plucked during ion polishing, and all analyses of it lie on the fragment that remained', None, 0),
 ('imaged in backscattered electrons (BSE) and mapped by energy-dispersive spectrometry (EDS) for Mg, Si, Fe, Ca, S and P on a field-emission SEM at 15 kV and 1 nA', None, 0),
 ('registered to stage coordinates, and each analysis point is marked with its label on the BSE image of its particle', None, 0),
 ('Each point analysis was treated as one analytical result', None, 0),
 ('labelled by particle and point number', None, 0),
 ('Each X-ray map was treated as one result for its mapped area, without reporting its pixels individually', None, 0),
 ('at least 5 µm across for focused-beam analysis, or at least 10 µm across for phosphates and carbonates', None, 0),
 ('at least 3 µm (5 µm for defocused or rastered beams) from grain boundaries, cracks and inclusions visible in BSE', None, 0),
 ('its phase identity was confirmed from its EDS spectrum before WDS acquisition began', None, 0),
 ('Map areas were chosen to include every target phase present in a particle', None, 0),
 ('53 point analyses and two maps: 29 points and map M1 on EX-CC-01, and 24 points and map M2 on EX-CC-02', None, 0),
 # 2.2
 ('JEOL JXA-8530F Plus electron microprobe', 'JEOL', 0),
 ('JEOL JXA-8530F Plus electron microprobe', 'JXA-8530F Plus', 0),
 ('Schottky field-emission source', None, 0),
 ('at the Example Microanalysis Laboratory (ROR', 'Example Microanalysis Laboratory', 0),
 ('https://ror.org/0example00', None, 0),
 ('EML-EPMA-CC v2, *EPMA-WDS+EDS major and minor elements in carbonaceous-chondrite silicates, oxides, sulfides, phosphates and carbonates*', None, 0),
 ('doi:10.0000/example.epma-cc.v2', None, 0),
 ('developed by the laboratory', None, 0), ('January 2025', None, 0),
 ('Example et al. (2025)', None, 0),
 ('combines wavelength-dispersive (WDS) and energy-dispersive (EDS) spectrometry', None, 0),
 ('covers point analysis and X-ray mapping by both', None, 0),
 ('five JEOL wavelength-dispersive spectrometers', None, 0),
 ('LDE1/TAP (Sp1), TAP/PETJ (Sp2), PETJ/LIF (Sp3), PETH/LIFH (Sp4) and LIF/PETL (Sp5)', None, 0),
 ('integrated silicon drift detector, with a 30 mm² active area, an ultra-thin polymer window and a 40° take-off angle', None, 0),
 ('low-pressure P10 gas-flow proportional counters', None, 0), ('sealed Xe counters', None, 0),
 ('Probe for EPMA v13 (Probe Software)', None, 0),
 ('quantified in Probe for EPMA v13', 'Probe for EPMA v13', 0),
 ('CalcImage v13', None, 0), ('XMapTools 4', None, 0),
 ('Analyst A (ORCID 0000-0000-0000-0000)', None, 0), ('12 to 14 April 2026', None, 0),
 ('EML-2026-0412-A', None, 0),
 # 2.3
 ("15 kV, the laboratory's standard operating voltage", None, 0),
 ('focused 1 µm beam at 20 nA', None, 0), ('defocused to 5 µm at 8 nA', None, 0),
 ('focused beam rastered over 5 × 5 µm at 4 nA', None, 0), ('focused beam at 50 nA', None, 0),
 ('Na, K, F and Cl were measured in the first acquisition pass on every point', None, 0),
 ('time-dependent intensity corrections were applied to Na (linear) and to F in apatite (exponential)', None, 0),
 ('measured with the Faraday cup before each point and at the start of each map line, and intensities were normalised to it', None, 0),
 ('Primary standards were re-measured at the start and end of the session, and drift in their intensities was interpolated linearly with time', None, 0),
 ('Si, Mg, Fe, Ca and S were measured by EDS', None, 0),
 ('Ti, Al, Cr, Mn, Na, K, P, F, Cl, Ni and Co were measured by WDS', None, 0),
 ('oxygen was calculated by stoichiometry from cation valences, and carbon as CO₂ by stoichiometry in carbonates only', None, 0),
 ('OH was calculated by difference assuming F + Cl + OH = 1 atom per formula unit (Ketcham 2015)', None, 0),
 ('Zn was also measured by WDS', None, 0),
 ('correct the overlap of Zn Lα on Na Kα', None, 0),
 ('acquired in three passes', 'three passes', 0),
 ('first pass measured F, Na, K, Cl and Zn', 'F, Na, K, Cl and Zn', 0),
 ('the second Al, P, Ti, Cr and Mn', 'Al, P, Ti, Cr and Mn', 0),
 ('The third measured Co and Ni', 'Co and Ni', 0),
 ('Ni counted on Sp4 and Sp5 at the same time and the two intensities aggregated', None, 0),
 ('live time of 30 s', None, 0),
 ('Differential pulse-height analysis was used for F and Na', None, 0),
 ('integral mode for all other elements', None, 0),
 ('peak counting times of 40 s for Co and Ni', None, 0), ('raised them to 60 s', None, 0),
 ('All other conditions were as registered', None, 0),
 ('measured at two off-peak positions for every WDS element', None, 0),
 ('(Table 1) and interpolated linearly', 'interpolated linearly', 0),
 ('an exponential fit', None, 0),
 ('Detection limits are 3σ of the background', '3σ of the background', 0),
 ('Measured only to correct its Lα overlap on Na Kα', None, 0),
 ('40 / 40 s in the registered procedure', None, 0),
 ('accepted values of Jarosewich et al. (1980)', None, 0),
 ("stoichiometric compounds or use the supplier's certified values", None, 0),
 # 2.4
 ('P1 of EX-CC-01 as map M1, and P1 of EX-CC-02 as map M2', None, 0),
 ('stage scan with the beam held fixed', None, 0),
 ('2 µm in both X and Y', None, 0), ('30 ms per pixel', None, 0),
 ('Na (Sp2, TAP), Al (Sp1, TAP), P (Sp3, PETJ), Cr (Sp4, LIFH) and Ni (Sp5, LIF)', None, 0),
 ('An EDS spectrum image', 'EDS spectrum image', 0),
 ('point spectra and spectrum images only; no line scans were made', None, 0),
 ('512 × 512 pixels', None, 0), ('1.024 × 1.024 mm', None, 0),
 ('384 × 256 pixels', None, 0), ('0.768 × 0.512 mm', None, 0),
 ('mean-atomic-number (MAN) calibration (Donovan and Tingle 1996)', None, 0),
 # 2.5
 ('Armstrong/Love–Scott φ(ρz) matrix correction (Armstrong 1995)', None, 0),
 ('FFAST (Chantler et al. 2005)', None, 0),
 ('applied pixel by pixel in CalcImage', None, 0),
 ('logarithmic expression and spectrometer-specific constants of 1.1–1.5 µs', None, 0),
 ('filter fitting — a top-hat filter followed by least-squares fitting to measured standard spectra', None, 0),
 ('removed the EDS background in both points and maps', None, 0),
 ('no externally calibrated conversion factor was used for any reported quantity', None, 0),
 ('IUPAC 2021 standard atomic weights (Prohaska et al. 2022)', None, 0),
 ('Three X-ray line overlaps were corrected quantitatively, with the correction iterated together with the matrix correction', None, 0),
 ('overlap of Fe Kβ on Co Kα', 'Fe Kβ on Co Kα', 0), ('Co-free Rockport fayalite', None, 0),
 ('Cr Kβ on Mn Kα', None, 0), ('Mn-free synthetic Cr₂O₃', None, 0),
 ('and Zn Lα on Na Kα on', 'Zn Lα on Na Kα', 0), ('Na-free synthetic ZnS', None, 0),
 ('No other element required an overlap correction', None, 0),
 ('the apparent concentration measured on Ni- and Co-free synthetic forsterite was subtracted as a blank', None, 0),
 ('35 ± 9 µg/g for Ni and 22 ± 8 µg/g for Co (n = 5)', None, 0),
 ('No other element was blank-corrected', None, 0),
 ('the oxygen equivalent of F and Cl was subtracted from the total', None, 0),
 ('SiO₂, TiO₂, Al₂O₃, Cr₂O₃, FeO (total Fe as FeO), MnO, MgO, CaO, Na₂O, K₂O, P₂O₅, NiO and CoO as oxides in wt%', None, 0),
 ('S, F and Cl as elements in wt%', None, 0),
 ('the oxygen equivalent of F and Cl, CO₂ by stoichiometry for carbonates, and analytical totals', None, 0),
 ('atoms per formula unit (apfu)', None, 0),
 ('normalised to a fixed anion basis for each phase: 4 O for olivine and spinels, 6 O for pyroxene and dolomite, 3 O for calcite, and 13 anions for apatite (Ketcham 2015)', None, 0),
 ('element concentrations in wt% per pixel, a phase map, and modal abundances in area %', None, 0),
 ('No other normalisation or standards-based correction was applied', None, 0),
 ('Mean compositions are reported for each phase in each sample', None, 0),
 ('between 98.5 and 101.5 wt% for silicates, oxides and sulfides, between 96.0 and 101.5 wt% for apatite (whose OH is calculated by difference), or between 98.0 and 102.0 wt% for carbonates (with CO₂ by stoichiometry)', None, 0),
 ('within ±0.03 apfu of the ideal value', None, 0),
 ('could not overlap a second phase in the post-analysis BSE image', None, 0),
 ('drifted by more than 1% during the analysis', None, 0),
 ('Of the 53 points acquired, 45 passed', None, 0),
 ('Four were excluded for totals outside the window: EX-CC-01 P3-02 and P3-05 (apatite), and EX-CC-02 P1-03 and P1-07 (dolomite)', None, 0),
 ('Three were excluded because they overlapped a neighbouring phase: EX-CC-01 P2-07 and P2-09 (pyrrhotite beside pentlandite), and EX-CC-02 P1-16 (calcite at a grain boundary)', None, 0),
 ('One, EX-CC-02 P2-05, was excluded for beam-current drift', None, 0),
 # 2.6
 ('accepted values from Jarosewich et al. (1980)', None, 0),
 ('San Carlos olivine USNM 111312/444 (n = 9)', None, 0),
 ('Kakanui augite USNM 122142 (n = 6)', None, 0),
 ('Durango apatite USNM 104021 (n = 6)', None, 0),
 ('chromite USNM 117075 (n = 5)', None, 0),
 ('calcite USNM 136321 (n = 6)', None, 0),
 ('0.4–0.7% for oxides above 10 wt%, 0.9–1.6% for FeO and Al₂O₃, 2–4% for TiO₂, Na₂O, F and Cl, and 4% for NiO in San Carlos olivine', None, 0),
 ('within ±1.2% relative for all major oxides and within ±2.6% for the minor oxides and halogens', None, 0),
 ('3σ of the background counts', None, 0),
 ('0.3 wt% per pixel for the WDS elements and 0.7 wt% for the EDS elements', None, 0),
 ('1σ uncertainty predicted from counting statistics on the peak and on any subtracted background or blank', None, 0),
 ('0.5% relative for SiO₂ and MgO and about 10% for NiO at 0.03 wt%', None, 0),
 ('18–26% during point analysis and 24–31% during spectrum imaging', None, 0),
 ('MSWD of its contributing analyses about their mean, using their counting-statistics uncertainties', None, 0),
 ('0.9 (NiO) to 2.3 (CaO)', None, 0), ('FeO reached 4.6', '4.6', 0),
 ('No anomalies, instrument modifications or other departures from the registered procedure occurred beyond those noted above', None, 0),
 # 2.7
 ('coupled workflow with SEM and NanoSIMS', 'SEM and NanoSIMS', 0),
 ('SEM imaging came first', None, 0),
 ('EPMA followed because it is non-destructive', None, 0),
 ('the carbon coat was replaced with gold for NanoSIMS oxygen-isotope analysis of the carbonates at the Example Isotope Laboratory, which came last because sputtering destroys the analysed volume', None, 0),
 ('The EPMA composition of each carbonate was used to select the matrix-matched carbonate reference material for the NanoSIMS instrumental mass-fractionation correction', None, 0),
 ('DOI pending', None, 0),
 ('included in the same submission as this dataset', None, 0),
 # acknowledgements and data availability
 ('Example Agency award EX-INST-0001', None, 0),
 ('award EX-DEV-0002', None, 0),
 ('Example Agency award EX-SCI-0003', None, 0),
 ('EML-2026-0412-A', None, 1),
 ('doi:10.0000/example.epma-cc.v2', None, 1),
 ('The coupled NanoSIMS data are included in the same submission', 'included in the same submission', 0),
]

LEGEND = ('> **Highlighting.** <mark>Highlighted</mark> text is information that fills a field of '
          'EPMA TAPP v77: a value, a choice, an identifier, a rule or an outcome. Text that is not '
          'highlighted is what joins that information into readable prose: connecting phrases, '
          'pointers to tables and supplements, rationale the TAPP does not ask for, and citations '
          'of methods literature. Every cell of Table 1 is highlighted. Generated from '
          '`EPMA_Reference_Methods_Section_v77.md` by `make_highlighted_methods.py`.\n\n')


def find_nth(text, sub, n, start=0):
    i = text.find(sub, start)
    while i != -1 and n:
        i = text.find(sub, i + 1); n -= 1
    return i


def main():
    text = open(SRC, encoding='utf-8').read()
    body_start = text.index('## 2. Methods')
    body_end = text.index('### Supplementary material')
    spans = []
    for ctx, span, occ in M:
        c = find_nth(text, ctx, occ, body_start)
        if c == -1 or c >= body_end:
            sys.exit('context not found: %r (occurrence %d)' % (ctx, occ))
        s = c if span is None else text.index(span, c)
        e = s + len(span or ctx)
        if span is not None and e > c + len(ctx):
            sys.exit('span outside its context: %r' % span)
        spans.append((s, e))

    # Table 1: every data cell, except placeholders
    t_start = text.index('| Element | Line |')
    t_end = text.index('\n\n', t_start)
    lines = text[t_start:t_end].split('\n')
    offset = t_start
    for li, line in enumerate(lines):
        if li >= 2:
            pos = 0
            for cell in line.split('|')[1:-1]:
                pos = line.index('|', pos) + 1
                raw = cell.strip()
                if raw and raw != '—':
                    s = offset + pos + cell.index(raw)
                    spans.append((s, s + len(raw)))
        offset += len(line) + 1

    spans.sort()
    for (a, b), (c, d) in zip(spans, spans[1:]):
        if c < b:
            sys.exit('overlapping spans: %r / %r' % (text[a:b], text[c:d]))
    for s, e in reversed(spans):
        text = text[:s] + '<mark>' + text[s:e] + '</mark>' + text[e:]
    text = text.replace('\n---\n\n## 2. Methods', '\n' + LEGEND + '---\n\n## 2. Methods', 1)
    open(OUT, 'w', encoding='utf-8').write(text)

    # share of methods prose (tables excluded) that carries TAPP information
    body = text[text.index('## 2. Methods'):text.index('### Supplementary material')]
    prose = '\n'.join(l for l in body.split('\n') if not l.startswith(('|', '#')))
    marked = ' '.join(re.findall(r'<mark>(.*?)</mark>', prose))
    total = len(re.sub(r'</?mark>', '', prose).split())
    print('wrote %s — %d highlighted spans; %d of %d words of prose highlighted (%.0f%%)'
          % (os.path.basename(OUT), len(spans), len(marked.split()), total,
             100 * len(marked.split()) / total))


if __name__ == '__main__':
    main()
