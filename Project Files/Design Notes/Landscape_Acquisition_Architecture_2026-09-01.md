# Landscape: acquisition architecture across all 68 planned techniques

**2026-09-01.** Written to answer a typology question: are the four procedure shapes we had been
working with exhaustive? They are not. This note classifies every technique in
`TAPP_Planning_Table.csv` on two axes, shows where the 16 built TAPPs actually sit, and names the
three structural families with zero coverage.

⚠ **Confidence.** Classification is from technique names, property types and data formats in the
planning table, plus the papers already read for the built TAPPs. It is a **first cut to direct
Phase 0 work**, not an adjudication. Each cell should be confirmed when its TAPP is scoped. The
built rows and the three papers cited below are firm; the rest are informed reading.

---

## The two axes

**E — how material reaches the measurement**

| | |
|---|---|
| `E0` **none** | nothing is removed; the instrument probes the sample in place |
| `E1` **one-time bulk** | dissolved, fused or combusted once; one homogeneous pool feeds the analyser |
| `E2` **parallel in-situ** | many independent extractions from different locations — replicated, **reorderable** |
| `E3` **serial stepped** | repeated extraction from the *same* material — cumulative, exhaustive, **not reorderable** |
| `E4` **continuous separation** | one injection, continuous elution feeding the analyser over time |

**A — how the analyser produces values**

| | |
|---|---|
| `A0` **non-instrumental** | counting, titration, gravimetry |
| `A1` **simultaneous** | all channels read at once — cup array, ToF, flat panel, dispersed spectrum on a CCD |
| `A2` **sequential scan** | the analyser steps an addressable axis — quadrupole mass scan, WDS spectrometer sequence |
| `A3` **multi-pass batch** | acquisition split into discrete configurations run in sequence — magnet steps, LR/MR passes, multi-dynamic cups |
| `A4c` **sweep that collapses** | a physical parameter is swept and the sweep is consumed before reporting — CT angles, an FID |
| `A4r` **sweep that IS reported** | the swept variable is the reported axis — mass vs temperature, intensity vs 2θ |

**The E2/E3 distinction is the one the four-type model collapsed.** A 40-spot LA session and a
47-step degassing experiment both produce "many extractions", but spots are independent material you
may reorder, while heating steps are cumulative — each removes what the next cannot get. The first is
`sampling unit`; the second has no key at all.

**A4c/A4r is the distinction that decides whether a swept axis needs a key.** Both sweep. Only `A4r`
survives into the reported table.

---

## Coverage

| | A0 non-instr | A1 simultaneous | A2 seq. scan | A3 multi-pass | A4c sweep→collapses | A4r sweep→REPORTED |
|---|---|---|---|---|---|---|
| **E0 none** | 1 | 9 | 2 | — | 7 (**1** built) | 13 |
| **E1 bulk** | 1 | 3 (**1** built) | 1 (**1** built) | 4 (**1** built) | 1 | — |
| **E2 in-situ** | — | 9 (**3** built) | 4 (**2** built) | 1 (**1** built) | 1 | 2 |
| **E3 stepped** | — | 2 | 1 | 1 | — | — |
| **E4 separation** | — | 1 | 3 | — | — | 1 |

**21 of 30 cells are occupied. Only 7 contain a built TAPP.** Every structural problem this session
hit — channel facets, stepped extraction, nested sampling units — sits at the edge of those 7.

### Three families with zero coverage

| family | count | why it is not reachable with today's structure |
|---|---|---|
| **`A4r` — the swept variable is reported** | **16** | The sweep survives into the reported table. This is the condition Rule 7.12 cares about, and **no built TAPP exercises it**: Lab-XCT is `A4c`, so it gave no warning. |
| **`E3` — serial stepped extraction** | **4** | No key. Péron & Mukhopadhyay 2025 populates two nested sample-side levels (capsule → heating step) — the **G2 nested sampling unit** question conventions.md defers pending a live case. |
| **`E4` — continuous separation** | **5** | Retention time is a *continuous* second acquisition axis. Fits the `channel` gloss ("a position on the axis the instrument steps through") but is untested and unlike any built case. |

`A4r` is the largest single gap in the library and the least anticipated: 16 techniques, spanning
thermal (DSC, TGA, dilatometry, thermal conductivity), mechanical (compression, direct shear,
nanoindentation, seismic velocity), spectroscopic (XRD, Mössbauer, XANES, VNMIR, NanoIR) and magnetic
(TDM). They share one shape — **a property measured as a function of an imposed condition** — and the
library has never built one.

### Compound cases worth naming now

- **`8` Static NGMS = `E3 × A3`** — the only doubly-compound cell. Stepped heating **and** magnet-step
  passes. Meshik et al. 2011 runs six magnet steps (2 Kr, 2 Xe, 2 baseline); Péron & Mukhopadhyay 2025
  runs two Xe steps per gas per heating step.
- **`16` Pyrolysis-GC-MS = `E3` then `E4`** — stepped pyrolysis feeding chromatography feeding MS.
  Two extraction architectures stacked in one procedure; nothing in the library resembles it.
- **`59` INAA = `E1 × A3`** with a **temporal** pass axis — irradiate once, then count the same sample
  repeatedly as isotopes decay. The passes are separated by days, not seconds.
- **`23`/`24`/`25` SIMS, ToF-SIMS, SNMS** are `E2` for spot work but become `E3` the moment depth
  profiling is used — the mode flag changes the extraction architecture.
- **`4` APT = `E3 × A1`** — field evaporation is serial, cumulative and destructive.

---

## What this implies for keys

| axis | key today | status |
|---|---|---|
| parallel locations (`E2`) | `sampling unit` | settled |
| **serial extraction steps (`E3`)** | **none** | **G2 nested sampling unit — open, noble gas is the live case** |
| acquisition passes (`A3`) | `channel` facet, inline | re-openable at Phase 0 under 7.12.1 |
| collapsing sweep (`A4c`) | `channel` | settled — Lab-XCT works |
| **reported sweep (`A4r`)** | `channel` for the address | ⚠ **untested; the swept value is also reported data** |
| continuous separation (`E4`) | `channel` (retention time) | untested |

**`A4r` deserves the same scrutiny `E3` got.** In TGA the temperature setpoint is simultaneously the
channel address *and* the index of the reported curve. That is the only configuration where an axis is
both, and no rule currently covers it. It should be settled in the Phase 0 of whichever `A4r` technique
is built first — on the 7.4a–c invariants, per 7.12.1, not on whether data happens to exist yet.

---

## Recommended sequencing

1. **NGMS Phase 0** (`E3 × A3`) — forces G2 nesting *and* the `acquisition pass` question, with three
   papers already read. Highest structural yield per unit effort.
2. **One `A4r` technique** — TGA or XRD are the simplest. Settles the address-and-index question before
   16 techniques inherit whatever is decided ad hoc.
3. **One `E4` technique** — GC-MS, which also has the largest downstream family.

Fission track (`27`, `E0 × A0`) remains the nominated G2 case in conventions.md, but noble gas is
better attested and would settle the same question sooner.

---

## Full classification

| # | Technique | Group | E | A | note |
|---|---|---|---|---|---|
| 1 | Electron Probe Microanalysis (EPMA) **✔built** | Electron Beam Microana | `E2` | `A2` | EPMA — spot/raster; WDS spectrometer sequence (+EDS simultaneous) |
| 2 | Scanning Electron Microscopy (SEM / FIB-SEM) **✔built** | Electron Beam Microana | `E2` | `A1` | SEM/FIB-SEM — EDS simultaneous; imaging is a raster |
| 3 | Transmission Electron Microscopy (TEM / STEM **✔built** | Electron Beam Microana | `E2` | `A1` | TEM/STEM — EDS/EELS |
| 4 | Atom Probe Tomography (APT) | Electron Beam Microana | `E3` | `A1` | APT — field evaporation is serial, cumulative, destructive; ToF readout |
| 5 | Solution Q-ICP-MS **✔built** | Mass Spectrometry – IC | `E1` | `A2` | Solution Q-ICP-MS — quadrupole mass scan |
| 5a | Solution SF-ICP-MS **✔built** | Mass Spectrometry – IC | `E1` | `A3` | Solution SF-ICP-MS — LR/MR resolution passes |
| 6 | Multi-Collector ICP-MS (MC-ICP-MS) **✔built** | Mass Spectrometry – IC | `E1` | `A1` | MC-ICP-MS — cup array (+multi-dynamic = A3) |
| 7 | Laser Ablation Q-ICP-MS (LA-Q-ICP-MS) **✔built** | Mass Spectrometry – IC | `E2` | `A2` | LA-Q-ICP-MS |
| 7a | Laser Ablation SF-ICP-MS (LA-SF-ICP-MS) **✔built** | Mass Spectrometry – IC | `E2` | `A3` | LA-SF-ICP-MS |
| 7b | Laser Ablation MC-ICP-MS (LA-MC-ICP-MS) **✔built** | Mass Spectrometry – IC | `E2` | `A1` | LA-MC-ICP-MS |
| 7c | Laser Ablation ICP-ToF-MS (LA-ICP-ToF-MS) | Mass Spectrometry – IC | `E2` | `A1` | LA-ICP-ToF-MS — ToF simultaneous |
| 7d | Laser Ablation ICP-TQ-MS (LA-ICP-TQ-MS) | Mass Spectrometry – IC | `E2` | `A2` | LA-ICP-TQ-MS — + cell modes |
| 8 | Static Noble Gas & Nitrogen Mass Spectrometr | Mass Spectrometry – No | `E3` | `A3` | Static NGMS — stepped heating/crushing x magnet steps  <-- the compound case |
| 10 | Resonance Ionization TOF Noble Gas MS (RI-TO | Mass Spectrometry – No | `E3` | `A1` | RI-TOF-NGMS — stepped extraction, ToF readout |
| 11 | GC-MS / GC-C-IRMS | Mass Spectrometry – Or | `E4` | `A2` | GC-MS / GC-C-IRMS — chromatographic elution |
| 12 | FTICR-MS | Mass Spectrometry – Or | `E1` | `A4c` | FTICR-MS — transient Fourier-transformed to frequency channels |
| 13 | DESI-Orbitrap MS | Mass Spectrometry – Or | `E2` | `A4c` | DESI-Orbitrap — surface desorption; FT readout |
| 14 | Liquid Chromatography–MS (LC / LC-MS) | Mass Spectrometry – Or | `E4` | `A2` | LC-MS |
| 15 | Microprobe Two-Step Laser MS (µL2MS) | Mass Spectrometry – Or | `E2` | `A1` | uL2MS — laser desorption spot, ToF |
| 16 | Pyrolysis-GC-MS | Mass Spectrometry – Or | `E3` | `A2` | Pyrolysis-GC-MS — stepped pyrolysis THEN chromatography: E3 and E4 stacked |
| 17 | Thermal Ionization Mass Spectrometry (TIMS) | Mass Spectrometry – Is | `E1` | `A3` | TIMS — peak jumping / multi-dynamic |
| 18 | Accelerator Mass Spectrometry (AMS) | Mass Spectrometry – Is | `E1` | `A1` | AMS |
| 19 | Elemental Analyzer – IRMS (EA-IRMS) | Mass Spectrometry – Is | `E1` | `A1` | EA-IRMS — combustion then GC separation, multicollector |
| 20 | Laser Assisted Fluorination – IRMS (LAF) | Mass Spectrometry – Is | `E2` | `A1` | LAF-IRMS — laser fluorination spot |
| 21 | Capillary Electrophoresis – MS (CE-MS) | Mass Spectrometry – Is | `E4` | `A2` | CE-MS |
| 22 | Ion Chromatography (IC) | Mass Spectrometry – Is | `E4` | `A4r` | IC — conductivity vs retention time IS the report |
| 23 | Secondary Ion Mass Spectrometry (SIMS / Nano | Mass Spectrometry – Su | `E2` | `A1` | SIMS/NanoSIMS — depth profiling makes it E3 |
| 24 | Time-of-Flight SIMS (ToF-SIMS) | Mass Spectrometry – Su | `E2` | `A1` | ToF-SIMS — depth profiling makes it E3 |
| 25 | Secondary Neutral Mass Spectrometry (SNMS) | Mass Spectrometry – Su | `E2` | `A2` | SNMS — depth profiling makes it E3 |
| 27 | Fission Track Analysis | Mass Spectrometry – Su | `E0` | `A0` | Fission track — etch then count optically; non-instrumental readout |
| 28 | Raman Vibrational Spectroscopy | Optical & Vibrational  | `E0` | `A1` | Raman — dispersed spectrum read simultaneously on CCD |
| 29 | VNMIR Spectroscopy (Vis-NIR-MIR) | Optical & Vibrational  | `E0` | `A4r` | VNMIR — reflectance vs wavelength IS the report |
| 30 | Nanoscale Infrared Mapping (NanoIR) | Optical & Vibrational  | `E0` | `A4r` | NanoIR — absorption vs wavenumber, mapped |
| 31 | Nuclear Magnetic Resonance Spectroscopy (NMR | Optical & Vibrational  | `E0` | `A4c` | NMR — FID Fourier-transformed |
| 32 | X-ray Absorption Near Edge Structure (XANES) | Optical & Vibrational  | `E0` | `A4r` | XANES — absorption vs incident energy IS the report |
| 33 | Mössbauer Spectroscopy | Optical & Vibrational  | `E0` | `A4r` | Mossbauer — absorption vs source velocity IS the report |
| 34 | X-ray Photoelectron Spectroscopy (XPS) | Optical & Vibrational  | `E0` | `A2` | XPS — binding-energy scan |
| 35 | Cathodoluminescence Spectroscopy (CL – stand | Optical & Vibrational  | `E0` | `A1` | CL — dispersed spectrum |
| 36 | X-ray Diffraction (XRD) | X-ray Methods | `E0` | `A4r` | XRD — intensity vs 2theta IS the report |
| 37 | X-ray Fluorescence Spectroscopy (XRF) | X-ray Methods | `E0` | `A1` | XRF — EDS simultaneous (WDS variant is A2) |
| 38 | X-ray Computed Tomography (XCT) **✔built** | X-ray Methods | `E0` | `A4c` | XCT — angle sweep collapses in reconstruction  <-- the only A4 built |
| 38a | Synchrotron X-ray Computed Tomography | X-ray Methods | `E0` | `A4c` | Synchrotron XCT |
| 38b | Muon X-ray Emmision Spectroscopy | X-ray Methods | `E0` | `A1` | Muon X-ray Emission Spectroscopy |
| 38c | Neutron + X-ray Computed Tomography (NCT+XCT | X-ray Methods | `E0` | `A4c` | NCT+XCT — dual modality, both collapse |
| 39 | Visible Light Microscopy (VLM) | Microscopy & Imaging | `E0` | `A1` | VLM |
| 40 | Fluorescence Microscopy (UVFM) | Microscopy & Imaging | `E0` | `A1` | UVFM |
| 41 | Structured Light Scanning (SLS) / 3D Shape | Microscopy & Imaging | `E0` | `A4c` | Structured Light Scanning — projected pattern sequence collapses to a mesh |
| 42 | Quantitative Reflective Imaging System (QRIS | Microscopy & Imaging | `E0` | `A1` | QRIS |
| 43 | Lock-in Thermography (LIT) | Microscopy & Imaging | `E0` | `A4c` | Lock-in Thermography — modulation frequency collapses to amplitude/phase |
| 44 | Confocal Laser Scanning Microscopy (CLSM) | Microscopy & Imaging | `E0` | `A4c` | CLSM — z-stack collapses to a 3D volume |
| 45 | Particle Size Frequency Distribution (PSFD) | Physical Properties | `E0` | `A1` | PSFD |
| 46 | Gas Pycnometry (GPYC) | Physical Properties | `E1` | `A3` | Gas Pycnometry — repeated gas expansions |
| 47 | Seismic Velocities & Rock Ultrasonic Elastic | Physical Properties | `E0` | `A4r` | Seismic velocities — V vs confining pressure IS the report |
| 48 | Nanoindentation & Microindentation (NI-MI) | Physical Properties | `E2` | `A4r` | Nanoindentation — load-displacement curve per indent IS the report |
| 49 | Angle of Repose Measurement (ARM) | Physical Properties | `E0` | `A1` | Angle of Repose |
| 50 | Compression Test (COMPT) | Physical Properties | `E0` | `A4r` | Compression Test — stress-strain curve IS the report |
| 51 | Direct Shear Strength Measurement (DSSM) | Physical Properties | `E0` | `A4r` | Direct Shear — stress vs displacement IS the report |
| 52 | Atomic Force Microscopy (AFM) | Physical Properties | `E2` | `A4r` | AFM — force-distance curve per point |
| 53 | Synchrotron X-ray Fluorescence (S-XRF) Mappi | Physical Properties | `E2` | `A1` | S-XRF mapping — rastered, simultaneous readout |
| 54 | Differential Scanning Calorimetry (DSC) | Thermal & Calorimetric | `E0` | `A4r` | DSC — heat flow vs temperature IS the report |
| 55 | Thermogravimetric Analysis (TGA) | Thermal & Calorimetric | `E0` | `A4r` | TGA — mass vs temperature IS the report |
| 56 | Mini Cryogen-Free Measurement System / Therm | Thermal & Calorimetric | `E0` | `A4r` | Thermal conductivity vs temperature |
| 57 | Capacitance Dilatometry (CAPD) | Thermal & Calorimetric | `E0` | `A4r` | Capacitance Dilatometry — dimension vs temperature |
| 59 | Instrumental Neutron Activation Analysis (IN | NEW – Not in BDD List | `E1` | `A3` | INAA — irradiate once, then COUNT REPEATEDLY at different decay times |
| 61 | Wet Chemistry / Gravimetric Analysis | NEW – Not in BDD List | `E1` | `A0` | Wet chemistry / gravimetric — non-instrumental readout |
| 62 | Prompt Gamma Neutron Activation Analysis (PG | NEW – Not in BDD List | `E0` | `A2` | PGNAA — in-beam gamma spectrum |
| 63 | High-Performance Liquid Chromatography (HPLC | NEW – Not in BDD List | `E4` | `A1` | HPLC |
| TDM | Temperature-Dependent Magnetization (TDM) | Physical Properties | `E0` | `A4r` | Temperature-Dependent Magnetization — M vs T IS the report |

---

**Sources.** `TAPP_Planning_Table.csv` (68 named techniques); the 16 built TAPPs; Shuster & Farley 2005,
Meshik et al. 2011, Péron & Mukhopadhyay 2025 for the `E3`/`A3` cases. Typology and the E2/E3 and
A4c/A4r distinctions were derived in the 2026-09-01 discussion that also produced conventions.md 7.12.1.
