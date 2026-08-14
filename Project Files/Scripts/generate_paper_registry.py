"""
generate_paper_registry.py
==========================
Writes paper_registry.csv for the TAPPs project.

Schema:
  Citation Key | DOI | PDF Filename | File Location
  + one column per TAPP technique that appears in any registered paper

Technique column names match the "Proposed TAPP Name" in TAPP_Planning_Table.xlsx.

Cell values (bare labels only — no explanatory notes):
  "Detailed"   Dedicated method description with instrument model + conditions;
               useful as a source for a future TAPP literature assessment.
  "Brief"      Technique mentioned (possibly with instrument name or facility)
               but no protocol parameters given; not useful as a TAPP source alone.
  "N"          Technique not used in this paper.

Rule: Every value must be traceable to a specific sentence or section
read directly from the source PDF in the current session, NOT inferred
from session summaries or common knowledge. When a paper is added to
the registry during a literature assessment session, the registry must
be updated in the same session using values read from the PDF.

Papers registered (21 as of 2026-05-14):
  EPMA papers: Ma2015, Hu2020, Liu2016, Ma2017, Frank2023, Broussard2026,
    Seifert2026, Pang2016, McCoy2025, Zega2025, Barnes2025
  LA-ICP-MS papers: BZhang2022, Chernonozhkin2021, Chernonozhkin2024,
    Masuda2024, Mittlefehldt2024, Nakanishi2022, Navarro2024,
    Zhang2022, Liu2024, Liu2025

LA-ICP-MS sub-technique reclassification (2026-05-14):
  The single "Laser Ablation ICP-MS" column was replaced with 4 specific
  sub-technique columns matching the updated TAPP Planning Table (rows 7–7c).
  BZhang2022, Chernonozhkin2021, Mittlefehldt2024, Nakanishi2022, Navarro2024,
    Liu2024, Liu2025, Liu2016  → LA-Q/SF-ICP-MS: Detailed
  Zhang2022                    → LA-MC-ICP-MS: Detailed (LA-MC-ICP-MS Rb-Sr dating)
  Chernonozhkin2024            → LA-ICP-ToF-MS: Detailed (micrometeorite imaging)
  Masuda2024                   → LA-ICP-TQ-MS: Detailed  (CAI REE mapping, iCAP TQ)
"""

import csv, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..',
                   'Project Files', 'Registers & Planning', 'paper_registry.csv')

FIXED_COLS = ['Citation Key', 'DOI', 'PDF Filename', 'File Location']

# Technique columns — names match TAPP Planning Table "Proposed TAPP Name".
# Only techniques present in ≥1 paper are included.
TECH_COLS = [
    'Electron Probe Microanalysis (EPMA)',
    'Scanning Electron Microscopy (SEM / FIB-SEM)',
    'Transmission Electron Microscopy (TEM / STEM)',
    'Raman Vibrational Spectroscopy',
    'X-ray Diffraction (XRD)',
    'Secondary Ion Mass Spectrometry (SIMS / NanoSIMS / SHRIMP)',
    'Time-of-Flight SIMS (ToF-SIMS)',
    'X-ray Absorption Near Edge Structure (XANES)',
    'Laser Ablation Q/SF-ICP-MS (LA-Q/SF-ICP-MS)',
    'Laser Ablation MC-ICP-MS (LA-MC-ICP-MS)',
    'Laser Ablation ICP-ToF-MS (LA-ICP-ToF-MS)',
    'Laser Ablation ICP-TQ-MS (LA-ICP-TQ-MS)',
    'Solution ICP-MS',
    'Multi-Collector ICP-MS (MC-ICP-MS)',
    'Laser Assisted Fluorination – IRMS (LAF)',
    'Accelerator Mass Spectrometry (AMS)',
    'Static Noble Gas & Nitrogen Mass Spectrometry (Noble Gas MS)',
]

HEADER = FIXED_COLS + TECH_COLS
EPMA = 'EPMA'

papers = [
    # ── Ma et al. 2015 ─────────────────────────────────────────────────────
    # Source: Ma et al, 2015.pdf read directly for EPMA assessment.
    # Coupled technique detail assessed by re-reading same PDF.
    {
        'Citation Key': 'Ma2015',
        'DOI': '10.1016/j.epsl.2015.03.057',
        'PDF Filename': 'Ma et al, 2015.pdf',
        'File Location': EPMA,
        'Electron Probe Microanalysis (EPMA)':
            'Detailed',
        'Scanning Electron Microscopy (SEM / FIB-SEM)':
            'Brief',
        'Transmission Electron Microscopy (TEM / STEM)': 'N',
        'Raman Vibrational Spectroscopy':
            'Brief',
        'X-ray Diffraction (XRD)':
            'Brief',
        'Secondary Ion Mass Spectrometry (SIMS / NanoSIMS / SHRIMP)': 'N',
        'Time-of-Flight SIMS (ToF-SIMS)': 'N',
        'X-ray Absorption Near Edge Structure (XANES)': 'N',
        'Laser Ablation Q/SF-ICP-MS (LA-Q/SF-ICP-MS)': 'N',
        'Laser Ablation MC-ICP-MS (LA-MC-ICP-MS)': 'N',
        'Laser Ablation ICP-ToF-MS (LA-ICP-ToF-MS)': 'N',
        'Laser Ablation ICP-TQ-MS (LA-ICP-TQ-MS)': 'N',
        'Solution ICP-MS': 'N',
        'Multi-Collector ICP-MS (MC-ICP-MS)': 'N',
        'Laser Assisted Fluorination – IRMS (LAF)': 'N',
        'Accelerator Mass Spectrometry (AMS)': 'N',
        'Static Noble Gas & Nitrogen Mass Spectrometry (Noble Gas MS)': 'N',
    },
    # ── Hu et al. 2020 ─────────────────────────────────────────────────────
    # Source: Hu et al, 2020.pdf read directly for EPMA assessment.
    {
        'Citation Key': 'Hu2020',
        'DOI': '10.1016/j.gca.2019.06.012',
        'PDF Filename': 'Hu et al, 2020.pdf',
        'File Location': EPMA,
        'Electron Probe Microanalysis (EPMA)':
            'Detailed',
        'Scanning Electron Microscopy (SEM / FIB-SEM)':
            'Brief',
        'Transmission Electron Microscopy (TEM / STEM)': 'N',
        'Raman Vibrational Spectroscopy':
            'Brief',
        'X-ray Diffraction (XRD)': 'N',
        'Secondary Ion Mass Spectrometry (SIMS / NanoSIMS / SHRIMP)': 'N',
        'Time-of-Flight SIMS (ToF-SIMS)': 'N',
        'X-ray Absorption Near Edge Structure (XANES)': 'N',
        'Laser Ablation Q/SF-ICP-MS (LA-Q/SF-ICP-MS)': 'N',
        'Laser Ablation MC-ICP-MS (LA-MC-ICP-MS)': 'N',
        'Laser Ablation ICP-ToF-MS (LA-ICP-ToF-MS)': 'N',
        'Laser Ablation ICP-TQ-MS (LA-ICP-TQ-MS)': 'N',
        'Solution ICP-MS': 'N',
        'Multi-Collector ICP-MS (MC-ICP-MS)': 'N',
        'Laser Assisted Fluorination – IRMS (LAF)': 'N',
        'Accelerator Mass Spectrometry (AMS)': 'N',
        'Static Noble Gas & Nitrogen Mass Spectrometry (Noble Gas MS)': 'N',
    },
    # ── Liu et al. 2016 ────────────────────────────────────────────────────
    # Source: Liu 2016 PDF read directly; LA-ICP-MS methods confirmed on p.4.
    {
        'Citation Key': 'Liu2016',
        'DOI': '10.1111/maps.12726',
        'PDF Filename': 'Meteorit   Planetary Scien - 2016 - Liu - Mineral chemistry of the Tissint meteorite  Indications of two‐stage.pdf',
        'File Location': EPMA,
        'Electron Probe Microanalysis (EPMA)':
            'Detailed',
        'Scanning Electron Microscopy (SEM / FIB-SEM)':
            'Brief',
        'Transmission Electron Microscopy (TEM / STEM)': 'N',
        'Raman Vibrational Spectroscopy': 'N',
        'X-ray Diffraction (XRD)': 'N',
        'Secondary Ion Mass Spectrometry (SIMS / NanoSIMS / SHRIMP)': 'N',
        'Time-of-Flight SIMS (ToF-SIMS)': 'N',
        'X-ray Absorption Near Edge Structure (XANES)': 'N',
        'Laser Ablation Q/SF-ICP-MS (LA-Q/SF-ICP-MS)': 'Detailed',
        'Laser Ablation MC-ICP-MS (LA-MC-ICP-MS)': 'N',
        'Laser Ablation ICP-ToF-MS (LA-ICP-ToF-MS)': 'N',
        'Laser Ablation ICP-TQ-MS (LA-ICP-TQ-MS)': 'N',
        'Solution ICP-MS': 'N',
        'Multi-Collector ICP-MS (MC-ICP-MS)': 'N',
        'Laser Assisted Fluorination – IRMS (LAF)': 'N',
        'Accelerator Mass Spectrometry (AMS)': 'N',
        'Static Noble Gas & Nitrogen Mass Spectrometry (Noble Gas MS)': 'N',
    },
    # ── Ma et al. 2017/2018 ────────────────────────────────────────────────
    # Source: Ma 2017 PDF read directly for EPMA assessment.
    {
        'Citation Key': 'Ma2017',
        'DOI': '10.1111/maps.13000',
        'PDF Filename': 'Meteorit   Planetary Scien - 2017 - Ma - Liebermannite  KAlSi3O8  a new shock‐metamorphic  high‐pressure mineral from the.pdf',
        'File Location': EPMA,
        'Electron Probe Microanalysis (EPMA)':
            'Detailed',
        'Scanning Electron Microscopy (SEM / FIB-SEM)':
            'Brief',
        'Transmission Electron Microscopy (TEM / STEM)': 'N',
        'Raman Vibrational Spectroscopy':
            'Brief',
        'X-ray Diffraction (XRD)':
            'Brief',
        'Secondary Ion Mass Spectrometry (SIMS / NanoSIMS / SHRIMP)': 'N',
        'Time-of-Flight SIMS (ToF-SIMS)': 'N',
        'X-ray Absorption Near Edge Structure (XANES)': 'N',
        'Laser Ablation Q/SF-ICP-MS (LA-Q/SF-ICP-MS)': 'N',
        'Laser Ablation MC-ICP-MS (LA-MC-ICP-MS)': 'N',
        'Laser Ablation ICP-ToF-MS (LA-ICP-ToF-MS)': 'N',
        'Laser Ablation ICP-TQ-MS (LA-ICP-TQ-MS)': 'N',
        'Solution ICP-MS': 'N',
        'Multi-Collector ICP-MS (MC-ICP-MS)': 'N',
        'Laser Assisted Fluorination – IRMS (LAF)': 'N',
        'Accelerator Mass Spectrometry (AMS)': 'N',
        'Static Noble Gas & Nitrogen Mass Spectrometry (Noble Gas MS)': 'N',
    },
    # ── Frank et al. 2023 ─────────────────────────────────────────────────
    # Source: Frank 2023 PDF read directly; SIMS methods confirmed pp.4–5.
    {
        'Citation Key': 'Frank2023',
        'DOI': '10.1111/maps.14083',
        'PDF Filename': 'Meteorit   Planetary Scien - 2023 - Frank - Calcium‐aluminum‐rich inclusion found in the Ivuna CI chondrite  Are CI.pdf',
        'File Location': EPMA,
        'Electron Probe Microanalysis (EPMA)':
            'Detailed',
        'Scanning Electron Microscopy (SEM / FIB-SEM)':
            'Brief',
        'Transmission Electron Microscopy (TEM / STEM)':
            'Brief',
        'Raman Vibrational Spectroscopy': 'N',
        'X-ray Diffraction (XRD)': 'N',
        'Secondary Ion Mass Spectrometry (SIMS / NanoSIMS / SHRIMP)':
            'Detailed',
        'Time-of-Flight SIMS (ToF-SIMS)': 'N',
        'X-ray Absorption Near Edge Structure (XANES)': 'N',
        'Laser Ablation Q/SF-ICP-MS (LA-Q/SF-ICP-MS)': 'N',
        'Laser Ablation MC-ICP-MS (LA-MC-ICP-MS)': 'N',
        'Laser Ablation ICP-ToF-MS (LA-ICP-ToF-MS)': 'N',
        'Laser Ablation ICP-TQ-MS (LA-ICP-TQ-MS)': 'N',
        'Solution ICP-MS': 'N',
        'Multi-Collector ICP-MS (MC-ICP-MS)': 'N',
        'Laser Assisted Fluorination – IRMS (LAF)': 'N',
        'Accelerator Mass Spectrometry (AMS)': 'N',
        'Static Noble Gas & Nitrogen Mass Spectrometry (Noble Gas MS)': 'N',
    },
    # ── Broussard et al. 2026 ─────────────────────────────────────────────
    # Source: Broussard 2026 PDF read directly; MC-ICP-MS/LAF/AMS confirmed p.4,8.
    {
        'Citation Key': 'Broussard2026',
        'DOI': '10.1111/maps.70138',
        'PDF Filename': 'Meteorit   Planetary Scien - 2026 - Broussard - CI chondrite Oued Chebeika 002 links asteroids Bennu and Ryugu to common.pdf',
        'File Location': EPMA,
        'Electron Probe Microanalysis (EPMA)':
            'Detailed',
        'Scanning Electron Microscopy (SEM / FIB-SEM)':
            'Brief',
        'Transmission Electron Microscopy (TEM / STEM)': 'N',
        'Raman Vibrational Spectroscopy': 'N',
        'X-ray Diffraction (XRD)':
            'Brief',
        'Secondary Ion Mass Spectrometry (SIMS / NanoSIMS / SHRIMP)': 'N',
        'Time-of-Flight SIMS (ToF-SIMS)': 'N',
        'X-ray Absorption Near Edge Structure (XANES)': 'N',
        'Laser Ablation Q/SF-ICP-MS (LA-Q/SF-ICP-MS)': 'N',
        'Laser Ablation MC-ICP-MS (LA-MC-ICP-MS)': 'N',
        'Laser Ablation ICP-ToF-MS (LA-ICP-ToF-MS)': 'N',
        'Laser Ablation ICP-TQ-MS (LA-ICP-TQ-MS)': 'N',
        'Solution ICP-MS':
            'Brief',
        'Multi-Collector ICP-MS (MC-ICP-MS)':
            'Detailed',
        'Laser Assisted Fluorination – IRMS (LAF)':
            'Detailed',
        'Accelerator Mass Spectrometry (AMS)':
            'Detailed',
        'Static Noble Gas & Nitrogen Mass Spectrometry (Noble Gas MS)': 'N',
    },
    # ── Seifert et al. 2026 ───────────────────────────────────────────────
    # Source: Seifert 2026 PDF read directly; TEM methods confirmed p.3;
    # SIMS confirmed as future work only (not used in this paper).
    {
        'Citation Key': 'Seifert2026',
        'DOI': '10.1111/maps.70167',
        'PDF Filename': 'Meteorit   Planetary Scien - 2026 - Seifert - Apatite in Bennu samples indicates multiple stages of aqueous alteration.pdf',
        'File Location': EPMA,
        'Electron Probe Microanalysis (EPMA)':
            'Detailed',
        'Scanning Electron Microscopy (SEM / FIB-SEM)':
            'Brief',
        'Transmission Electron Microscopy (TEM / STEM)':
            'Detailed',
        'Raman Vibrational Spectroscopy': 'N',
        'X-ray Diffraction (XRD)': 'N',
        'Secondary Ion Mass Spectrometry (SIMS / NanoSIMS / SHRIMP)':
            'N',
        'Time-of-Flight SIMS (ToF-SIMS)': 'N',
        'X-ray Absorption Near Edge Structure (XANES)': 'N',
        'Laser Ablation Q/SF-ICP-MS (LA-Q/SF-ICP-MS)': 'N',
        'Laser Ablation MC-ICP-MS (LA-MC-ICP-MS)': 'N',
        'Laser Ablation ICP-ToF-MS (LA-ICP-ToF-MS)': 'N',
        'Laser Ablation ICP-TQ-MS (LA-ICP-TQ-MS)': 'N',
        'Solution ICP-MS': 'N',
        'Multi-Collector ICP-MS (MC-ICP-MS)': 'N',
        'Laser Assisted Fluorination – IRMS (LAF)': 'N',
        'Accelerator Mass Spectrometry (AMS)': 'N',
        'Static Noble Gas & Nitrogen Mass Spectrometry (Noble Gas MS)': 'N',
    },
    # ── Pang et al. 2016 ──────────────────────────────────────────────────
    # Source: Pang 2016 PDF read directly for EPMA assessment.
    {
        'Citation Key': 'Pang2016',
        'DOI': '10.1038/srep26063',
        'PDF Filename': 'srep26063.pdf',
        'File Location': EPMA,
        'Electron Probe Microanalysis (EPMA)':
            'Detailed',
        'Scanning Electron Microscopy (SEM / FIB-SEM)':
            'Brief',
        'Transmission Electron Microscopy (TEM / STEM)': 'N',
        'Raman Vibrational Spectroscopy': 'N',
        'X-ray Diffraction (XRD)': 'N',
        'Secondary Ion Mass Spectrometry (SIMS / NanoSIMS / SHRIMP)': 'N',
        'Time-of-Flight SIMS (ToF-SIMS)': 'N',
        'X-ray Absorption Near Edge Structure (XANES)': 'N',
        'Laser Ablation Q/SF-ICP-MS (LA-Q/SF-ICP-MS)': 'N',
        'Laser Ablation MC-ICP-MS (LA-MC-ICP-MS)': 'N',
        'Laser Ablation ICP-ToF-MS (LA-ICP-ToF-MS)': 'N',
        'Laser Ablation ICP-TQ-MS (LA-ICP-TQ-MS)': 'N',
        'Solution ICP-MS': 'N',
        'Multi-Collector ICP-MS (MC-ICP-MS)': 'N',
        'Laser Assisted Fluorination – IRMS (LAF)': 'N',
        'Accelerator Mass Spectrometry (AMS)': 'N',
        'Static Noble Gas & Nitrogen Mass Spectrometry (Noble Gas MS)': 'N',
    },
    # ── McCoy et al. 2025 ─────────────────────────────────────────────────
    # Source: McCoy 2025 PDF (s41586-024-08495-6.pdf) read directly;
    # ToF-SIMS/XANES methods confirmed p.8.
    {
        'Citation Key': 'McCoy2025',
        'DOI': '10.1038/s41586-024-08495-6',
        'PDF Filename': 's41586-024-08495-6.pdf',
        'File Location': EPMA,
        'Electron Probe Microanalysis (EPMA)':
            'Detailed',
        'Scanning Electron Microscopy (SEM / FIB-SEM)':
            'Detailed',
        'Transmission Electron Microscopy (TEM / STEM)':
            'Detailed',
        'Raman Vibrational Spectroscopy': 'N',
        'X-ray Diffraction (XRD)':
            'Detailed',
        'Secondary Ion Mass Spectrometry (SIMS / NanoSIMS / SHRIMP)': 'N',
        'Time-of-Flight SIMS (ToF-SIMS)':
            'Detailed',
        'X-ray Absorption Near Edge Structure (XANES)':
            'Detailed',
        'Laser Ablation Q/SF-ICP-MS (LA-Q/SF-ICP-MS)': 'N',
        'Laser Ablation MC-ICP-MS (LA-MC-ICP-MS)': 'N',
        'Laser Ablation ICP-ToF-MS (LA-ICP-ToF-MS)': 'N',
        'Laser Ablation ICP-TQ-MS (LA-ICP-TQ-MS)': 'N',
        'Solution ICP-MS': 'N',
        'Multi-Collector ICP-MS (MC-ICP-MS)': 'N',
        'Laser Assisted Fluorination – IRMS (LAF)': 'N',
        'Accelerator Mass Spectrometry (AMS)': 'N',
        'Static Noble Gas & Nitrogen Mass Spectrometry (Noble Gas MS)': 'N',
    },
    # ── Zega et al. 2025 ──────────────────────────────────────────────────
    # Source: Zega 2025 PDF (s41561-025-01741-0.pdf) read directly;
    # SEM/TEM/XANES/XRD methods confirmed pp.9–10.
    {
        'Citation Key': 'Zega2025',
        'DOI': '10.1038/s41561-025-01741-0',
        'PDF Filename': 's41561-025-01741-0.pdf',
        'File Location': EPMA,
        'Electron Probe Microanalysis (EPMA)':
            'Detailed',
        'Scanning Electron Microscopy (SEM / FIB-SEM)':
            'Detailed',
        'Transmission Electron Microscopy (TEM / STEM)':
            'Detailed',
        'Raman Vibrational Spectroscopy': 'N',
        'X-ray Diffraction (XRD)':
            'Detailed',
        'Secondary Ion Mass Spectrometry (SIMS / NanoSIMS / SHRIMP)': 'N',
        'Time-of-Flight SIMS (ToF-SIMS)': 'N',
        'X-ray Absorption Near Edge Structure (XANES)':
            'Detailed',
        'Laser Ablation Q/SF-ICP-MS (LA-Q/SF-ICP-MS)': 'N',
        'Laser Ablation MC-ICP-MS (LA-MC-ICP-MS)': 'N',
        'Laser Ablation ICP-ToF-MS (LA-ICP-ToF-MS)': 'N',
        'Laser Ablation ICP-TQ-MS (LA-ICP-TQ-MS)': 'N',
        'Solution ICP-MS': 'N',
        'Multi-Collector ICP-MS (MC-ICP-MS)': 'N',
        'Laser Assisted Fluorination – IRMS (LAF)': 'N',
        'Accelerator Mass Spectrometry (AMS)': 'N',
        'Static Noble Gas & Nitrogen Mass Spectrometry (Noble Gas MS)': 'N',
    },
    # ── Barnes et al. 2025 ────────────────────────────────────────────────
    # Source: Barnes 2025 PDF read directly for EPMA assessment (pp.11–13)
    # and coupled technique detail (pp.9–13 for SIMS/Noble gas/LAF/SEM).
    # MC-ICP-MS methods not fully read (K, Ti, Cu, Zn isotopes are primary
    # results; method section present but specific pages not extracted).
    {
        'Citation Key': 'Barnes2025',
        'DOI': '10.1038/s41550-025-02631-6',
        'PDF Filename': "Barnes et al. 2025 (The variety and origin of materials accreted by Bennu's parent asteroid).pdf",
        'File Location': EPMA,
        'Electron Probe Microanalysis (EPMA)':
            'Detailed',
        'Scanning Electron Microscopy (SEM / FIB-SEM)':
            'Detailed',
        'Transmission Electron Microscopy (TEM / STEM)': 'N',
        'Raman Vibrational Spectroscopy': 'N',
        'X-ray Diffraction (XRD)': 'N',
        'Secondary Ion Mass Spectrometry (SIMS / NanoSIMS / SHRIMP)':
            'Detailed',
        'Time-of-Flight SIMS (ToF-SIMS)': 'N',
        'X-ray Absorption Near Edge Structure (XANES)': 'N',
        'Laser Ablation Q/SF-ICP-MS (LA-Q/SF-ICP-MS)': 'N',
        'Laser Ablation MC-ICP-MS (LA-MC-ICP-MS)': 'N',
        'Laser Ablation ICP-ToF-MS (LA-ICP-ToF-MS)': 'N',
        'Laser Ablation ICP-TQ-MS (LA-ICP-TQ-MS)': 'N',
        'Solution ICP-MS':
            'Brief',
        'Multi-Collector ICP-MS (MC-ICP-MS)':
            'Detailed',
        'Laser Assisted Fluorination – IRMS (LAF)':
            'Detailed',
        'Accelerator Mass Spectrometry (AMS)': 'N',
        'Static Noble Gas & Nitrogen Mass Spectrometry (Noble Gas MS)':
            'Detailed',
    },

    # ════════════════════════════════════════════════════════════════════════
    # LA-ICP-MS Validation Papers (assessed 2026-05-13/14)
    # All 10 PDFs in: LA-ICP-MS/Validation Papers/
    # LA-ICP-MS technique values confirmed by direct PDF reading in same session.
    # Other technique values assigned based on what agents explicitly reported.
    # ════════════════════════════════════════════════════════════════════════

    # ── B. Zhang et al. 2022 (GCA 323) ──────────────────────────────────
    # LA-ICP-MS: Full methods Section 2.2 (pp.4–5); instrument, conditions,
    #   analytes, standards, corrections all stated. Detailed.
    # EPMA: Section 2.5 names Brown University CAMECA SX-100; WDS/EDS mapping
    #   described but no operating conditions (kV, beam current, etc.). Brief.
    # SEM: BSE maps mentioned; no protocol parameters. Brief.
    {
        'Citation Key': 'BZhang2022',
        'DOI': '10.1016/j.gca.2022.02.004',
        'PDF Filename': 'B. Zhang et al, 2022.pdf',
        'File Location': 'LA-ICP-MS/Validation Papers',
        'Electron Probe Microanalysis (EPMA)': 'Brief',
        'Scanning Electron Microscopy (SEM / FIB-SEM)': 'Brief',
        'Transmission Electron Microscopy (TEM / STEM)': 'N',
        'Raman Vibrational Spectroscopy': 'N',
        'X-ray Diffraction (XRD)': 'N',
        'Secondary Ion Mass Spectrometry (SIMS / NanoSIMS / SHRIMP)': 'N',
        'Time-of-Flight SIMS (ToF-SIMS)': 'N',
        'X-ray Absorption Near Edge Structure (XANES)': 'N',
        'Laser Ablation Q/SF-ICP-MS (LA-Q/SF-ICP-MS)': 'Detailed',
        'Laser Ablation MC-ICP-MS (LA-MC-ICP-MS)': 'N',
        'Laser Ablation ICP-ToF-MS (LA-ICP-ToF-MS)': 'N',
        'Laser Ablation ICP-TQ-MS (LA-ICP-TQ-MS)': 'N',
        'Solution ICP-MS': 'N',
        'Multi-Collector ICP-MS (MC-ICP-MS)': 'N',
        'Laser Assisted Fluorination – IRMS (LAF)': 'N',
        'Accelerator Mass Spectrometry (AMS)': 'N',
        'Static Noble Gas & Nitrogen Mass Spectrometry (Noble Gas MS)': 'N',
    },

    # ── Chernonozhkin et al. 2021 (Chem Geol 562) ───────────────────────
    # LA-ICP-MS: Full methods (main paper pp.2–5 + appendices); three
    #   distinct protocols (raster, multi-run, spot on phosphate). Detailed.
    {
        'Citation Key': 'Chernonozhkin2021',
        'DOI': '10.1016/j.chemgeo.2020.119996',
        'PDF Filename': 'Chernonozhkin et al, 2021.pdf',
        'File Location': 'LA-ICP-MS/Validation Papers',
        'Electron Probe Microanalysis (EPMA)': 'N',
        'Scanning Electron Microscopy (SEM / FIB-SEM)': 'N',
        'Transmission Electron Microscopy (TEM / STEM)': 'N',
        'Raman Vibrational Spectroscopy': 'N',
        'X-ray Diffraction (XRD)': 'N',
        'Secondary Ion Mass Spectrometry (SIMS / NanoSIMS / SHRIMP)': 'N',
        'Time-of-Flight SIMS (ToF-SIMS)': 'N',
        'X-ray Absorption Near Edge Structure (XANES)': 'N',
        'Laser Ablation Q/SF-ICP-MS (LA-Q/SF-ICP-MS)': 'Detailed',
        'Laser Ablation MC-ICP-MS (LA-MC-ICP-MS)': 'N',
        'Laser Ablation ICP-ToF-MS (LA-ICP-ToF-MS)': 'N',
        'Laser Ablation ICP-TQ-MS (LA-ICP-TQ-MS)': 'N',
        'Solution ICP-MS': 'N',
        'Multi-Collector ICP-MS (MC-ICP-MS)': 'N',
        'Laser Assisted Fluorination – IRMS (LAF)': 'N',
        'Accelerator Mass Spectrometry (AMS)': 'N',
        'Static Noble Gas & Nitrogen Mass Spectrometry (Noble Gas MS)': 'N',
    },

    # ── Chernonozhkin et al. 2024 (JAAS 39, 1050–1056) ──────────────────
    # LA-ICP-MS: LA-ICP-ToF-MS raster mapping on micrometeorites; full
    #   instrument, laser, and data reduction conditions described. Detailed.
    {
        'Citation Key': 'Chernonozhkin2024',
        'DOI': '10.1039/d3ja00335c',
        'PDF Filename': 'Chernonozhkin et al, 2024.pdf',
        'File Location': 'LA-ICP-MS/Validation Papers',
        'Electron Probe Microanalysis (EPMA)': 'N',
        'Scanning Electron Microscopy (SEM / FIB-SEM)': 'N',
        'Transmission Electron Microscopy (TEM / STEM)': 'N',
        'Raman Vibrational Spectroscopy': 'N',
        'X-ray Diffraction (XRD)': 'N',
        'Secondary Ion Mass Spectrometry (SIMS / NanoSIMS / SHRIMP)': 'N',
        'Time-of-Flight SIMS (ToF-SIMS)': 'N',
        'X-ray Absorption Near Edge Structure (XANES)': 'N',
        'Laser Ablation Q/SF-ICP-MS (LA-Q/SF-ICP-MS)': 'N',
        'Laser Ablation MC-ICP-MS (LA-MC-ICP-MS)': 'N',
        'Laser Ablation ICP-ToF-MS (LA-ICP-ToF-MS)': 'Detailed',
        'Laser Ablation ICP-TQ-MS (LA-ICP-TQ-MS)': 'N',
        'Solution ICP-MS': 'N',
        'Multi-Collector ICP-MS (MC-ICP-MS)': 'N',
        'Laser Assisted Fluorination – IRMS (LAF)': 'N',
        'Accelerator Mass Spectrometry (AMS)': 'N',
        'Static Noble Gas & Nitrogen Mass Spectrometry (Noble Gas MS)': 'N',
    },

    # ── Masuda et al. 2024 (M&PS 59, 2260–2275) ─────────────────────────
    # LA-ICP-MS: msfsLA (multiple-spot femtosecond LA) + iCAP TQ; full
    #   Table 2 of instrument conditions; analytes, IS approach, DRS. Detailed.
    {
        'Citation Key': 'Masuda2024',
        'DOI': '10.1111/maps.14190',
        'PDF Filename': 'Meteorit   Planetary Scien - 2024 - Masuda - Distribution analysis of rare earth elements in fine‐grained CAIs of the.pdf',
        'File Location': 'LA-ICP-MS/Validation Papers',
        'Electron Probe Microanalysis (EPMA)': 'N',
        'Scanning Electron Microscopy (SEM / FIB-SEM)': 'N',
        'Transmission Electron Microscopy (TEM / STEM)': 'N',
        'Raman Vibrational Spectroscopy': 'N',
        'X-ray Diffraction (XRD)': 'N',
        'Secondary Ion Mass Spectrometry (SIMS / NanoSIMS / SHRIMP)': 'N',
        'Time-of-Flight SIMS (ToF-SIMS)': 'N',
        'X-ray Absorption Near Edge Structure (XANES)': 'N',
        'Laser Ablation Q/SF-ICP-MS (LA-Q/SF-ICP-MS)': 'N',
        'Laser Ablation MC-ICP-MS (LA-MC-ICP-MS)': 'N',
        'Laser Ablation ICP-ToF-MS (LA-ICP-ToF-MS)': 'N',
        'Laser Ablation ICP-TQ-MS (LA-ICP-TQ-MS)': 'Detailed',
        'Solution ICP-MS': 'N',
        'Multi-Collector ICP-MS (MC-ICP-MS)': 'N',
        'Laser Assisted Fluorination – IRMS (LAF)': 'N',
        'Accelerator Mass Spectrometry (AMS)': 'N',
        'Static Noble Gas & Nitrogen Mass Spectrometry (Noble Gas MS)': 'N',
    },

    # ── Mittlefehldt 2024 (GCA, Appendix A; accepted 10 Aug 2024) ────────
    # LA-ICP-MS: Section 3.3; instrument, analytes, IS approach, standards,
    #   all key conditions reported for JSC SF-ICP-MS. Detailed.
    # DOI: not printed in this appendix PDF; associated with GCA main paper.
    {
        'Citation Key': 'Mittlefehldt2024',
        'DOI': 'N',
        'PDF Filename': 'Mittlefehldt, 2024 Appendix A.pdf',
        'File Location': 'LA-ICP-MS/Validation Papers',
        'Electron Probe Microanalysis (EPMA)': 'N',
        'Scanning Electron Microscopy (SEM / FIB-SEM)': 'N',
        'Transmission Electron Microscopy (TEM / STEM)': 'N',
        'Raman Vibrational Spectroscopy': 'N',
        'X-ray Diffraction (XRD)': 'N',
        'Secondary Ion Mass Spectrometry (SIMS / NanoSIMS / SHRIMP)': 'N',
        'Time-of-Flight SIMS (ToF-SIMS)': 'N',
        'X-ray Absorption Near Edge Structure (XANES)': 'N',
        'Laser Ablation Q/SF-ICP-MS (LA-Q/SF-ICP-MS)': 'Detailed',
        'Laser Ablation MC-ICP-MS (LA-MC-ICP-MS)': 'N',
        'Laser Ablation ICP-ToF-MS (LA-ICP-ToF-MS)': 'N',
        'Laser Ablation ICP-TQ-MS (LA-ICP-TQ-MS)': 'N',
        'Solution ICP-MS': 'N',
        'Multi-Collector ICP-MS (MC-ICP-MS)': 'N',
        'Laser Assisted Fluorination – IRMS (LAF)': 'N',
        'Accelerator Mass Spectrometry (AMS)': 'N',
        'Static Noble Gas & Nitrogen Mass Spectrometry (Noble Gas MS)': 'N',
    },

    # ── Nakanishi et al. 2022 (GCA 319, 254–270) ────────────────────────
    # LA-ICP-MS: Section 2.2; fs-LA-Q-ICP-MS; instrument, laser, analytes,
    #   IS, standards, DRS all stated. Detailed.
    {
        'Citation Key': 'Nakanishi2022',
        'DOI': '10.1016/j.gca.2021.11.009',
        'PDF Filename': 'Nakanishi et al, 2022.pdf',
        'File Location': 'LA-ICP-MS/Validation Papers',
        'Electron Probe Microanalysis (EPMA)': 'N',
        'Scanning Electron Microscopy (SEM / FIB-SEM)': 'N',
        'Transmission Electron Microscopy (TEM / STEM)': 'N',
        'Raman Vibrational Spectroscopy': 'N',
        'X-ray Diffraction (XRD)': 'N',
        'Secondary Ion Mass Spectrometry (SIMS / NanoSIMS / SHRIMP)': 'N',
        'Time-of-Flight SIMS (ToF-SIMS)': 'N',
        'X-ray Absorption Near Edge Structure (XANES)': 'N',
        'Laser Ablation Q/SF-ICP-MS (LA-Q/SF-ICP-MS)': 'Detailed',
        'Laser Ablation MC-ICP-MS (LA-MC-ICP-MS)': 'N',
        'Laser Ablation ICP-ToF-MS (LA-ICP-ToF-MS)': 'N',
        'Laser Ablation ICP-TQ-MS (LA-ICP-TQ-MS)': 'N',
        'Solution ICP-MS': 'N',
        'Multi-Collector ICP-MS (MC-ICP-MS)': 'N',
        'Laser Assisted Fluorination – IRMS (LAF)': 'N',
        'Accelerator Mass Spectrometry (AMS)': 'N',
        'Static Noble Gas & Nitrogen Mass Spectrometry (Noble Gas MS)': 'N',
    },

    # ── Navarro et al. 2024 (ACS Earth Space Chem 8) ────────────────────
    # LA-ICP-MS: Two protocols (spot + raster); ns-LA-SF-ICP-MS; full
    #   instrument, laser, analytes, standards, IS described. Detailed.
    {
        'Citation Key': 'Navarro2024',
        'DOI': '10.1021/acsearthspacechem.3c00283',
        'PDF Filename': 'Navarro et al, 2024.pdf',
        'File Location': 'LA-ICP-MS/Validation Papers',
        'Electron Probe Microanalysis (EPMA)': 'N',
        'Scanning Electron Microscopy (SEM / FIB-SEM)': 'N',
        'Transmission Electron Microscopy (TEM / STEM)': 'N',
        'Raman Vibrational Spectroscopy': 'N',
        'X-ray Diffraction (XRD)': 'N',
        'Secondary Ion Mass Spectrometry (SIMS / NanoSIMS / SHRIMP)': 'N',
        'Time-of-Flight SIMS (ToF-SIMS)': 'N',
        'X-ray Absorption Near Edge Structure (XANES)': 'N',
        'Laser Ablation Q/SF-ICP-MS (LA-Q/SF-ICP-MS)': 'Detailed',
        'Laser Ablation MC-ICP-MS (LA-MC-ICP-MS)': 'N',
        'Laser Ablation ICP-ToF-MS (LA-ICP-ToF-MS)': 'N',
        'Laser Ablation ICP-TQ-MS (LA-ICP-TQ-MS)': 'N',
        'Solution ICP-MS': 'N',
        'Multi-Collector ICP-MS (MC-ICP-MS)': 'N',
        'Laser Assisted Fluorination – IRMS (LAF)': 'N',
        'Accelerator Mass Spectrometry (AMS)': 'N',
        'Static Noble Gas & Nitrogen Mass Spectrometry (Noble Gas MS)': 'N',
    },

    # ── Zhang et al. 2022 (At. Spectrosc. 43, 7–14) ─────────────────────
    # LA-ICP-MS: In situ Rb-Sr dating using LA-MC-ICP-MS; full instrument,
    #   laser, IS, standards, data reduction described. Detailed.
    # MC-ICP-MS: Integrated with LA; Neptune Plus described with full
    #   collector configuration and mass resolution. Detailed.
    {
        'Citation Key': 'Zhang2022',
        'DOI': '10.46770/AS.2022.007',
        'PDF Filename': 'Zhang et al, 2022.pdf',
        'File Location': 'LA-ICP-MS/Validation Papers',
        'Electron Probe Microanalysis (EPMA)': 'N',
        'Scanning Electron Microscopy (SEM / FIB-SEM)': 'N',
        'Transmission Electron Microscopy (TEM / STEM)': 'N',
        'Raman Vibrational Spectroscopy': 'N',
        'X-ray Diffraction (XRD)': 'N',
        'Secondary Ion Mass Spectrometry (SIMS / NanoSIMS / SHRIMP)': 'N',
        'Time-of-Flight SIMS (ToF-SIMS)': 'N',
        'X-ray Absorption Near Edge Structure (XANES)': 'N',
        'Laser Ablation Q/SF-ICP-MS (LA-Q/SF-ICP-MS)': 'N',
        'Laser Ablation MC-ICP-MS (LA-MC-ICP-MS)': 'Detailed',
        'Laser Ablation ICP-ToF-MS (LA-ICP-ToF-MS)': 'N',
        'Laser Ablation ICP-TQ-MS (LA-ICP-TQ-MS)': 'N',
        'Solution ICP-MS': 'N',
        'Multi-Collector ICP-MS (MC-ICP-MS)': 'N',
        'Laser Assisted Fluorination – IRMS (LAF)': 'N',
        'Accelerator Mass Spectrometry (AMS)': 'N',
        'Static Noble Gas & Nitrogen Mass Spectrometry (Noble Gas MS)': 'N',
    },

    # ── Liu et al. 2024 (JAAS 39) ────────────────────────────────────────
    # LA-ICP-MS: fs-LA-ICP-MS using Li-borate glass fusion for trace element
    #   determination; Resonetics laser, Agilent 7900, full conditions. Detailed.
    {
        'Citation Key': 'Liu2024',
        'DOI': '10.1039/d4ja00275j',
        'PDF Filename': 'Liu et al, 2024.pdf',
        'File Location': 'LA-ICP-MS/Validation Papers',
        'Electron Probe Microanalysis (EPMA)': 'N',
        'Scanning Electron Microscopy (SEM / FIB-SEM)': 'N',
        'Transmission Electron Microscopy (TEM / STEM)': 'N',
        'Raman Vibrational Spectroscopy': 'N',
        'X-ray Diffraction (XRD)': 'N',
        'Secondary Ion Mass Spectrometry (SIMS / NanoSIMS / SHRIMP)': 'N',
        'Time-of-Flight SIMS (ToF-SIMS)': 'N',
        'X-ray Absorption Near Edge Structure (XANES)': 'N',
        'Laser Ablation Q/SF-ICP-MS (LA-Q/SF-ICP-MS)': 'Detailed',
        'Laser Ablation MC-ICP-MS (LA-MC-ICP-MS)': 'N',
        'Laser Ablation ICP-ToF-MS (LA-ICP-ToF-MS)': 'N',
        'Laser Ablation ICP-TQ-MS (LA-ICP-TQ-MS)': 'N',
        'Solution ICP-MS': 'N',
        'Multi-Collector ICP-MS (MC-ICP-MS)': 'N',
        'Laser Assisted Fluorination – IRMS (LAF)': 'N',
        'Accelerator Mass Spectrometry (AMS)': 'N',
        'Static Noble Gas & Nitrogen Mass Spectrometry (Noble Gas MS)': 'N',
    },

    # ── Liu et al. 2025 (GCA 393, 170–181) ──────────────────────────────
    # LA-ICP-MS: Two protocols (silicate glass + sulfide); ns-LA-Q-ICP-MS;
    #   Resonetics 193 nm ArF + Agilent 7900 Q; Analyte HE cell; full
    #   conditions in Table 1. Detailed.
    {
        'Citation Key': 'Liu2025',
        'DOI': '10.1016/j.gca.2025.01.017',
        'PDF Filename': 'Liu et al, 2025.pdf',
        'File Location': 'LA-ICP-MS/Validation Papers',
        'Electron Probe Microanalysis (EPMA)': 'N',
        'Scanning Electron Microscopy (SEM / FIB-SEM)': 'N',
        'Transmission Electron Microscopy (TEM / STEM)': 'N',
        'Raman Vibrational Spectroscopy': 'N',
        'X-ray Diffraction (XRD)': 'N',
        'Secondary Ion Mass Spectrometry (SIMS / NanoSIMS / SHRIMP)': 'N',
        'Time-of-Flight SIMS (ToF-SIMS)': 'N',
        'X-ray Absorption Near Edge Structure (XANES)': 'N',
        'Laser Ablation Q/SF-ICP-MS (LA-Q/SF-ICP-MS)': 'Detailed',
        'Laser Ablation MC-ICP-MS (LA-MC-ICP-MS)': 'N',
        'Laser Ablation ICP-ToF-MS (LA-ICP-ToF-MS)': 'N',
        'Laser Ablation ICP-TQ-MS (LA-ICP-TQ-MS)': 'N',
        'Solution ICP-MS': 'N',
        'Multi-Collector ICP-MS (MC-ICP-MS)': 'N',
        'Laser Assisted Fluorination – IRMS (LAF)': 'N',
        'Accelerator Mass Spectrometry (AMS)': 'N',
        'Static Noble Gas & Nitrogen Mass Spectrometry (Noble Gas MS)': 'N',
    },
]

# ── Write CSV ─────────────────────────────────────────────────────────────
with open(OUT, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=HEADER)
    writer.writeheader()
    for p in papers:
        writer.writerow(p)

print(f"Written: {OUT}")
print(f"  Papers: {len(papers)}  |  Columns: {len(HEADER)}")
print(f"\nDetailed/Brief/N summary:")
for tech in TECH_COLS:
    d = sum(1 for p in papers if p[tech].startswith('Detailed'))
    b = sum(1 for p in papers if p[tech].startswith('Brief'))
    n = sum(1 for p in papers if p[tech] == 'N' or p[tech].startswith('N —'))
    if d + b > 0:
        print(f"  {tech[:55]:<55} D={d} B={b} N={n}")
