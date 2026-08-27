# new_B: text = rewrite · "" = delete the sentence (W2) · None = KEEP unchanged, logged as a decision
E = {
# --- W5.1 KEEP — Column I is derived FROM these, or they say what Column I cannot ------------
("EDS Detection Limit","TEM","1"):(None,"","W5.1 KEEP — names the key correctly and then RECONCILES it with the analyte set ('these being the same set'), an equivalence Column I cannot express"),
("EELS Edges","TEM","2"):(None,"","W5.1 KEEP — `defines: channel per analyte`; Column I is derived FROM this sentence, which is where the edge-to-analyte relation is established"),
("WDS Spectrometer Channel","EPMA,SEM,SEMcomp","1"):(None,"","W5.1 KEEP — `defines:` form; stripping the relation this field establishes would orphan Column I"),
("WDS Spectrometer Channel","EPMA,SEM,SEMcomp","2"):(None,"","W5.1 KEEP — this sentence is the JUSTIFICATION of the key (why the assignment, not the analyte, is the unit). Column I records the verdict; only this records the reasoning"),
# --- revised on reading: a per-branch cardinality contrast Column I cannot hold ---------------
("Dwell Time per Pixel","EPMA","2"):(None,"","KEEP — revised from the queue's W5.2. S2 and S3 form one WDS-vs-EDS contrast: WDS carries one value per spectrometer, EDS a single value. Column I holds ONE key for the field and cannot say the cardinality differs by mode"),
("Dwell Time per Pixel","EPMA","3"):(None,"","KEEP — the EDS half of the same contrast; stripping either half breaks it"),
# --- W5.2 STRIP — Column I already names the axis and the prose adds nothing ------------------
("Diffracting Crystal","EPMA,SEM,SEMcomp","1"):("Analyzing crystal (monochromator).","","W5.2 — 'used on each spectrometer assignment' carried by Keyed By: channel"),
("EPMA Technique per Analyte","EPMA","1"):("Whether the measurement was made by WDS or EDS.","","W5.2 — 'each analyte' carried by Keyed By: analyte, and by the field name"),
("EPMA Technique per Analyte","EPMA","2"):("Applies where a procedure uses both WDS and EDS.","","W5.2 — 'some elements to WDS and others to EDS' is the per-analyte key in words; the APPLICABILITY condition is not, and survives"),
("Interference Correction Standard","EPMA","1"):("Reference material used to quantify and calibrate the interference correction.","","W5.2 — 'for this analyte' carried by Keyed By: analyte"),
("Interference Correction Standard","SEM,SEMcomp","1"):("Reference material used to quantify and calibrate the interference correction.","","W5.2 — 'for each affected analyte' carried by Keyed By: analyte; partial coverage is already what a consumer must assume of any key (conventions.md 7.3.1)"),
("Interference Corrections Applied","EPMA,SEM,SEMcomp","1"):("Whether a spectral interference correction was applied.","","W5.2 — 'for each analyte' carried by Keyed By: analyte"),
("Interfering Elements","EPMA","1"):("Element(s) whose X-ray lines overlap with the measured peak, requiring a correction.","","W5.2 — 'for this analyte' carried by Keyed By: analyte"),
("Interfering Elements","SEM,SEMcomp","1"):("Element(s) whose X-ray lines overlap with the measured peak, requiring a correction.","","W5.2 — 'for one or more analytes' carried by Keyed By: analyte"),
("Peak Counting Time","EPMA,SEM,SEMcomp","1"):("Time spent counting X-ray intensity at the peak position, in seconds.","","W5.2 — 'on each spectrometer assignment' carried by Keyed By: channel"),
("Proportional Counter / Detector","EPMA,SEM,SEMcomp","1"):("Type of detector used.","","W5.2 — 'on each spectrometer assignment' carried by Keyed By: channel"),
("Technique per Analyte","SEM,SEMcomp","1"):("Records which X-ray detection technique (EDS or WDS) was used to collect the measurement.","","W5.2 — 'For each analyte' carried by Keyed By: analyte, and by the field name"),
("X-ray Line","EPMA,SEM,SEMcomp","1"):("X-ray emission line measured.","","W5.2 — 'on each spectrometer assignment' carried by Keyed By: channel"),
# --- W5.4 resolved: drop the axis word entirely, and the analyte/reported-property clash with it
("Analytical Accuracy","EPMA,SEM,SEMcomp","2"):("Include reference material, reference value source, and the measured value.","","W5.4 RESOLVED — the description said 'per-analyte' where Keyed By says `reported property`, a conflict raised 2026-08-12 and never dispositioned. Removing the axis word retires the conflict rather than adjudicating which term is right: Column I carries the axis, so Column B does not need to name it"),
("Analytical Precision","EPMA,SEM,SEMcomp","2"):("Include reference material name, number of analyses (n), and the measured value.","","W5.4 RESOLVED — as Analytical Accuracy; 'number of analyses (n)' is real content and survives"),
}
# Deferred: needs a SCOPE decision, not a wording edit — the four sharers disagree.
DEFER = {
("Dwell Time per Pixel","FIB,SEM,SEMcomp,SEMimg","3"):
 "SCOPE, not wording. The sentence describes WDS mapping. SEM and SEM_Composition declare WDS modes; "
 "SEM_FIBSEM and SEM_Imaging declare none, so for them it documents a mode they do not have. One shared "
 "text, four sharers, and the right answer differs per TAPP — resolving it means either dropping the "
 "sentence from two sub-TAPPs (diverging the description) or deciding the sub-TAPPs may carry parent "
 "text. That is the same class as the 2026-08-24 out-of-scope column drop, and belongs with it.",
}
