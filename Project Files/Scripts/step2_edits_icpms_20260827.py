# (Field, Variant_TAPPs, Sentence_no) -> (new_B, to_Purpose, note)
#   text = rewrite · "" = delete the sentence (W2) · None = KEEP unchanged, logged as a decision
E = {
# --- W2: tier restatements -------------------------------------------------------------------
("delta or epsilon Value Reference Standard","Sol-MC","2"):(
 "The reporting reference is a per-study or per-publication decision.","",
 "W2 — 'and is specified at analysis level' is carried by C=N/A + D=Basic; that the choice is per-study is not"),
("Doubly-Charged Species Production","LA-MC,LA-MC_UPb,LA-Q,LA-Q_UPb,LA-SF,LA-SF_UPb","2"):(
 "The acceptable threshold is typically <1% or <3%.","",
 "W2 — 'the procedure should specify the threshold; the measured value for each session is recorded here' is the C/D split in words; the threshold values themselves are real content"),
("Number of Replicates","LA-MC,LA-MC_UPb,LA-Q,LA-Q_UPb,LA-SF,LA-SF_UPb,Sol-Q,Sol-SF","3"):(
 "","",
 "W2 DELETE — 'the procedure registers an intended count where it has one; the analysis records the count actually acquired' is exactly C=Advanced (procedure-level optional) plus D=Basic (analysis-level mandatory). Nothing survives the strip"),
# --- W5.2: key restatements. The LOCUS stays, the cardinality goes to Column I -----------------
("Dwell Time per Mass","LA-Q,LA-Q_UPb,LA-SF,LA-SF_UPb","1"):(
 "Count time (dwell time) per mass position, in milliseconds.","",
 "W5.2 — 'for each measured isotope' is carried by Keyed By: channel; 'per mass position' is the locus, not the cardinality, and stays"),
("Dwell Time per Mass","Sol-Q,Sol-SF","1"):(
 "Integration time spent at the mass peak per sweep (ms).","",
 "W5.2 — 'on each mass peak' becomes the locus without the cardinality, which Keyed By: channel carries"),
("Dwell Time per Mass","Sol-Q,Sol-SF","2"):(
 "","",
 "W5.2 DELETE — 'may differ between masses where per-mass dwell times are programmed' states the per-channel key CONDITIONALLY. conventions.md 7.3.2 (decided today) has Column I declare the finest key unconditionally, so the condition is now expressed by a simple procedure's keyed table having one row. Nothing survives"),
("Mass Resolution Assignment","LA-MC,LA-MC_UPb,LA-SF,LA-SF_UPb,Sol-SF","1"):(
 "Mass resolution mode used for acquisition.","",
 "W5.2 — 'assigned to each acquired mass' is carried by Keyed By: channel; S3 keeps the per-mass explanation together with its reason"),
("Reaction Product Ion / Mass-Shift Transition","LA-Q,LA-Q_UPb,Sol-Q","1"):(
 "Where a monitored mass is produced by a reaction in the collision/reaction cell, the precursor ion, the reagent gas and the product ion measured.","",
 "W5.2 — 'For each monitored mass' is carried by Keyed By: channel; recast as an APPLICABILITY condition, which Column I cannot express, rather than dropping the qualification entirely"),
# --- W5.1: Column I is derived from these, or they say what Column I cannot --------------------
("Error Correlation Between Reported Quantities","LA-MC_UPb,LA-Q_UPb,LA-SF_UPb,Sol-MC","1"):(
 None,"",
 "W5.1 KEEP — Keyed By is `pair: reported property` and this sentence is what ENUMERATES the pair ('together with the pair it applies to'). The field establishes the domain; stripping it would orphan the key"),
("Mass Resolution Assignment","LA-MC,LA-MC_UPb,LA-SF,LA-SF_UPb,Sol-SF","3"):(
 None,"",
 "W5.1 KEEP — this sentence is the JUSTIFICATION of the key: why the assignment is per acquired mass rather than per element. Column I records the verdict, only this records the reasoning (cf. WDS Spectrometer Channel S2)"),
("Monitored Masses","LA-MC,LA-MC_UPb,LA-Q,LA-Q_UPb,LA-SF,LA-SF_UPb,Sol-Q,Sol-SF","1"):(
 None,"",
 "W5.1 KEEP — Keyed By is `defines: channel per analyte` in 6 of the 8 consumers, so Column I is DERIVED from this sentence. 'where they serve one' is also a real qualification Column I cannot carry. NOTE the 2-of-8 `analyte` variant is the separately registered keyed-by divergence, untouched here"),
# --- W1: straddles -----------------------------------------------------------------------------
("Collision/Reaction Gas Mixture Ratio","LA-Q,LA-Q_UPb,Sol-Q","2"):(
 "Recorded separately from the gas identity.",
 "The proportions change reaction efficiency and interference suppression independently of which gases are used.",
 "W1 — the scope boundary stays in Description; why the proportions are recorded apart is rationale"),
("Total Integration Time per Output Data Point","LA-Q,LA-Q_UPb,LA-SF,LA-SF_UPb","2"):(
 "Not recoverable from Dwell Time per Mass alone, because settling time is not captured there.",
 "Sets the time resolution of the downhole signal.",
 "W1 — the scope boundary against Dwell Time per Mass stays; what the value sets is rationale"),
("Triple Scanning Mode","LA-SF,LA-SF_UPb,Sol-SF","3"):(
 "",
 "Triple scanning affects the effective integration time per cycle.",
 "W1+W2 — the rationale moves to Purpose; the remaining half ('and should be reported') is carried by S1, which already asks for the Y/N, so nothing survives in Description"),
}
