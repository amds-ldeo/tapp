RELOC = {
 "Blank / Background Correction Method": [
   "For spot and transect analysis: typically the mean of a pre-ablation gas blank interval is subtracted per isotope per analysis.",
   "For mapping: background may be subtracted per raster line, per map session, or using a separate gas blank map acquired under identical conditions.",
   "In MC-ICP-MS, on-peak zero subtraction (aspirating the same acid matrix as samples while measuring background at the analyte masses with beam deflector or from baseline cycles at the start of each block) is standard.",
   "For low-level analyses, procedural blank must be measured and subtracted."],
 "Signal Integration Time": [
   "Not applicable to mapping analysis: for mapping, the equivalent concept is the per-pixel cycle time, determined by the spectrometer dwell time settings.",
   "Calculated from blocks \u00d7 cycles per block \u00d7 integration time per cycle."],
 "Signal Integration Interval Method": [
   "For spot/transect analysis: involves identifying and excluding transient start/end instabilities within the time-resolved signal.",
   "In MC-ICP-MS, all cycles within a block are typically used unless signal instability is detected."],
 "Interface Cone Configuration": [
   "For Neptune-type instruments, H-cones (standard) and X-cones (high-sensitivity, ~3\u00d7 higher transmission) are common options."],
 "Interfering Species": [
   "For Q-ICP-MS, common interferences include ArCl+ on 75As, MoO+ species on Cd isotopes, and BaO+ on Eu.",
   "Includes direct isobars (e.g., 54Cr+ on 54Fe+, 58Ni+ on 58Fe+), abundance sensitivity tailing (e.g., 238U tail on 235U and 236U in U isotope measurements), and hydride interferences (e.g., 238UH+ at mass 239)."],
 "Sampler and Skimmer Cone Material": [
   "Aluminium (Al) cones are used in some SF-ICP-MS labs for enhanced sensitivity at high resolution.",
   "Platinum (Pt) cones are used for HCl-rich matrices (e.g., 6 M HCl in Fe chemistry procedures) due to greater corrosion resistance."],
 "Memory Effect Mitigation": [
   "For mapping, the mitigation strategy involves controlling scan speed relative to washout time to ensure each pixel signal is sufficiently free of the preceding pixel\u2019s contribution."],
 "Internal Standard Element": [
   'For mapping procedures using oxide-sum normalization, report "None (oxide-sum normalization)" and cite the method reference.'],
 "Mass Resolution Setting": [
   "Multi-resolution procedures assign individual analytes to specific modes (documented in Group 4 under Mass Resolution Assignment)."],
 "Isotope Dilution Data Reduction Method": [
   "Spike must have been added before digestion for accurate equilibration."],
 "Per-Analyte Calibration Strategy": [
   "For procedures producing isotope ratios only (no concentration output), record \'Not applicable (isotope ratios only)\'.",
   "For double-spike procedures that simultaneously yield concentrations, record the ID calculation approach."],
 "Analysis Sequence": [
   "For SSB procedures, each sample is bracketed by two standards (standard\u2013sample\u2013standard); the bracketing standard is the same isotopic material as the zero-delta reference."],
}
