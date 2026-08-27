# (Field, Variant_TAPPs, Sentence_no) -> (new_Description_sentence, text_to_append_to_Purpose, note)
# ""  in slot 1 = sentence deleted from Column B (W2, recording which column carries it)
E = {
# --- "registered by the procedure" — trailing tier assertion, clause excision only -------------
("Accelerating Voltage","XCT","1"):("X-ray tube accelerating voltage in kilovolts (kV).","","W2 — 'registered by the procedure' carried by C=Basic"),
("Exposure Time per Projection","XCT","1"):("Duration of X-ray exposure for each individual projection image frame, in seconds.","","W2 — 'as registered by the procedure' carried by C=Basic"),
("Frames Averaged per Projection","XCT","1"):("Number of individual detector frames acquired and averaged to produce each saved projection image.","","W2 — 'as registered by the procedure' carried by C=Advanced"),
("Source-to-Detector Distance (SDD)","XCT","1"):("Distance from the X-ray source focal spot to the detector surface, in mm.","","W2 — 'as registered by the procedure' carried by C=Advanced"),
("Source-to-Object Distance (SOD)","XCT","1"):("Distance from the X-ray source focal spot to the centre of the sample rotation axis, in mm.","","W2 — 'as registered by the procedure' carried by C=Advanced"),
("Tube Current","XCT","1"):("X-ray tube current in microamperes (µA).","","W2 — 'registered by the procedure' carried by C=Basic"),
("X-ray Power","XCT","1"):("X-ray tube power in watts (W).","","W2 — 'registered by the procedure' carried by C=Advanced"),
# --- "Procedure-level / Analysis-level <noun> of X" — strip the tier word --------------------
("Cross-Validation Procedure Requirement","XCT","1"):("Specification of what independent analytical validation is required to confirm CT segmentation results, phase identification, or quantitative measurements.","","W2 — 'Procedure-level' carried by C=Advanced; 'specification' still separates this from its Outcome twin"),
("Partial Volume Effect Criteria","XCT","1"):("Specification of how partial volume effects (PVE) are managed in quantitative analysis.","","W2 — 'Procedure-level' carried by C=Advanced"),
("VOI Selection Criteria","XCT","1"):("Rules specifying how the Volume of Interest (VOI) is to be defined for quantitative analysis.","","W2 — 'Procedure-level' carried by C=Advanced"),
("Cross-Validation Outcome","XCT","1"):("Record of what independent validation was performed and its result.","","W2 — 'Analysis-level' carried by C=N/A + D=Advanced; 'record' still separates this from its Requirement twin"),
("Partial Volume Effect Assessment","XCT","1"):("Record of PVE severity and how it was handled.","","W2 — 'Analysis-level' and 'in this specific analysis' both carried by C=N/A + D=Advanced"),
("Sub-volume Overlap","XCT","1"):("Actual number of reconstructed slices overlapping between adjacent sub-volumes.","","W2 — 'as used in this analysis' carried by C=N/A + D=Basic; 'Actual' survives and distinguishes it from the procedure minimum"),
("VOI Applied","XCT","1"):("Actual Volume of Interest used, including dimensions or defining criteria.","","W2 — 'in this specific analysis' carried by C=N/A + D=Basic; 'Actual' survives"),
# --- "Analysis-level companion to X" — the pairing is content, the tier word is not ----------
("Beam Hardening Correction Parameter","XCT","3"):("Companion to Beam Hardening Correction Method.","","W2 — 'Analysis-level' carried by C=Advanced + D=Editable; naming the pair is kept"),
("VOI Applied","XCT","2"):("Companion to VOI Selection Criteria.","","W2 — 'Analysis-level' carried by C=N/A + D=Basic; naming the pair is kept"),
# --- wholly a tier restatement — W2 deletes, recording the carrier ---------------------------
("Minimum Sub-volume Overlap","XCT","2"):("","","W2 DELETE — the sentence is nothing but the procedure-level tier, carried by C=Basic"),
("Reconstruction Convolution Filter","XCT","3"):("","","W2 DELETE — 'a deliberate procedure-level tradeoff' is carried by C=Advanced; the tradeoff itself is already in Purpose"),
("Voxel Size and Image Stack Dimensions","FIB,SEM","2"):("","","W2 DELETE — 'Determined at analysis time.' is nothing but C=N/A + D=Basic"),
# --- "Determined at analysis time based on X" — tier stripped, the basis survives ------------
("Map Area","EPMA","2"):("Based on the sample feature or region of interest.","","W2 — 'Determined at analysis time' carried by C=N/A + D=Basic"),
("Map Dimensions","EPMA","2"):("Based on the area of interest and selected step size.","","W2 — as Map Area"),
("EDS Map Dimensions","SEM,SEMcomp","2"):("Based on the area of interest and selected pixel size.","","W2 — as Map Area"),
# --- "procedure specifies X; analysts do Y" — the C/D split goes, the extra obligation stays --
("Accelerating Voltage","EPMA","2"):("Justify any deviation from the standard operating voltage.","","W2 — the specify/record split is carried by C=Basic + D=Editable; the justification requirement is not, and survives"),
("Accelerating Voltage","TEM","3"):("Justify any deviation from the standard operating voltage.","","W2 — as EPMA"),
("EBSD Phase List","SEM,SEMimg","2"):("Phases may be added for specific sample compositions beyond the expected suite for the target material.","","W2 — the specify/add split is carried by C=Basic + D=Editable; what may be added, and beyond what, is not"),
("EELS Edges","TEM","3"):("The edge list may be narrowed at analysis time.","","W2 — the register/confirm split is carried by C=Basic + D=Editable; that the list may SHRINK is not"),
("EELS Energy Loss Range","TEM","2"):("The target range covers the registered analyte edges; the actual range acquired may differ.","","W2 — the document/record split is carried by C=Basic + D=Editable; the target-vs-actual distinction is not"),
("Peak Counting Time","EPMA,SEM,SEMcomp","2"):("Adjustments stay within procedure-defined bounds.","","W2 — the specify/adjust split is carried by C=Basic + D=Editable; the bound on adjustment is not"),
("Sample Preparation Details","TEM","2"):("Includes session-specific observations and deviations from the procedure standard.","","W2 — 'Analysts record' is carried by D=Editable; what the field holds is definitional and stays"),
("Beam Hardening Correction Method","XCT","4"):("The specific correction parameter value is recorded separately.","","W2 — 'procedure-level design choice ... at analysis level' is carried by C=Basic + D=Read-Only; that the parameter lives elsewhere is not"),
("Ring Artifact Correction Method","XCT","3"):("Whether correction was applied and its outcome are recorded separately in Group 6.","","W2 — the procedure/analysis split is carried by C=Advanced + D=Editable; the pointer to Group 6 is not"),
("Output Bit Depth","XCT","4"):("A required output bit depth may be specified if downstream analysis workflows depend on a consistent grayscale range.","","W2 + W3 — 'the analyst confirms or adjusts at analysis time' is carried by D=Editable; the CONDITIONAL obligation is real content and is never stripped"),
("Exposure Time per Projection","XCT","3"):("Adjustment is warranted for samples that are unusually dense or unusually transparent.","","W2 — 'may be adjusted within procedure-allowed bounds' is carried by D=Editable; WHEN to adjust is not"),
("Voxel Size","XCT","3"):("Record the achieved voxel size as reported by the reconstruction software, which may differ slightly from the target due to final geometric calibration.","","W2 — 'At analysis level' carried by D=Editable; the instruction and the target/achieved discrepancy survive"),
# --- dual-flagged: STRADDLE + REDUNDANT ------------------------------------------------------
("Number of Sub-volumes","XCT","2"):("","The number of sub-volumes depends on the length of the specific sample being scanned and cannot be fixed in the procedure in advance.","W1+W2 — 'This is an analysis-level parameter:' carried by C=N/A + D=Basic; the remaining clause is wholly rationale and moves to Purpose. S1 keeps the definition (M1)"),
("Sample Mass","XCT","3"):("","The actual sample mass depends on the specific sample being scanned, not on the procedure design.","W1+W2 — 'This is an analysis-level field:' carried by C=N/A; the rest is rationale and moves to Purpose. S1 keeps the definition (M1)"),
("Voxel Size","XCT","2"):("The target voxel size is set based on the smallest feature to be resolved (target voxel size ≤ ~1/3 of that feature size; see the criterion recorded under Partial Volume Effect Criteria).","","W1+W2 — 'The procedure registers' carried by C=Basic. The straddle resolves with NOTHING moving to Purpose: the surviving half is a design criterion, i.e. how to set the value, which is instruction not rationale"),
}
