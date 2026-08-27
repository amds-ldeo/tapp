# W1 — split: definition/instruction stays in Description, rationale moves to Purpose.
E = {
("Applicable Sample Dimension Range","XCT","5"):(
 "The lower bound is a practical guideline: ~10 voxels across the smallest dimension.",
 "Samples spanning fewer than that are difficult to characterize reliably.",
 "W1 — the bound is the definition; why the guideline exists is rationale"),
("Beam Raster Dimensions","SEM,SEMcomp","2"):(
 "Applicable when Beam Mode = Rastered; defines the effective spatial footprint of the measurement.",
 "Distributes dose over a larger area to reduce beam damage on sensitive phases.",
 "W1 — applicability and footprint are definitional; the dose argument is rationale"),
("Camera Length","TEM","2"):(
 "Must be calibrated to convert pixel distances to d-spacings.",
 "Controls the mapping between reciprocal-space scattering angle and detector position.",
 "W1 — the calibration obligation is the instruction; what it controls is rationale"),
("Detector Binning","XCT","2"):(
 "Binning combines adjacent pixels (e.g., 2×2 combines 4 pixels into one).",
 "Reduces effective resolution while increasing per-pixel SNR and reducing file size.",
 "W1 — what binning IS stays; the three-way trade-off is rationale"),
("EBSD Step Size","SEM,SEMimg","2"):(
 "Must be smaller than the smallest grain of interest.",
 "Only then are grain boundary positions and intragrain orientation gradients resolved.",
 "W1 — the constraint on the value stays; what it buys is rationale"),
("EDS Dead Time","EPMA,SEM,SEMcomp","2"):(
 "This field documents the resulting percentage as a session QC metric.",
 "EDS dead time correction is managed automatically by the detector electronics.",
 "W1 — what the field holds stays; how the correction is handled is rationale"),
("EDS Dead Time","TEM","2"):(
 "This field documents the resulting percentage as a session QC metric.",
 "EDS dead time correction is managed automatically by the detector electronics.",
 "W1 — as the EPMA/SEM variant"),
("HAADF Collection Angles","TEM","3"):(
 "Inner angle can be derived from camera length and detector geometry.",
 "The inner angle is the most critical.",
 "W1 — how to derive it stays; its importance is rationale. Kept 'most critical' verbatim: an earlier draft read 'the more critical of the two', which asserts a comparison between inner and outer angles that the source does not make"),
("Lift-out Method","FIB,SEM","2"):(
 "In-situ lift-out uses a micromanipulator inside the FIB-SEM chamber.",
 "It is the standard method for small or precious specimens.",
 "W1 — what the method IS stays; when it is preferred is rationale"),
("Map Area","SEM,SEMcomp","2"):(
 "Complements the map's pixel-grid dimensions by recording the physical scale of the mapped region.",
 "Useful for direct comparison across datasets acquired with different step sizes.",
 "W1 — the relation to the pixel grid is definitional; the comparability argument is rationale"),
("Protective Coating Deposition","FIB,SEM","2"):(
 "E-beam deposition should be applied as the initial layer.",
 "It causes less surface damage than ion-beam deposition.",
 "W1 — the instruction stays; the comparative reason is rationale"),
("Ring Artifact Severity and Correction Outcome","XCT","2"):(
 "Note that ring correction algorithms modify image intensity in narrow annular bands.",
 "In samples containing linear geological features oriented tangentially to the rotation axis, ring correction can alter or introduce spurious linear features in those orientations.",
 "W1 — the instruction and the mechanism stay; the consequence for linear features is rationale"),
("Sample Preparation Notes","XCT","2"):(
 "Note any exceptions.",
 "XCT is typically non-destructive, with no surface preparation required.",
 "W1 — the instruction stays; the technique fact behind it is rationale"),
("STEM Dwell Time per Pixel","TEM","2"):(
 "For dose-sensitive materials, minimize dwell and compensate with frame averaging.",
 "Longer dwell improves signal-to-noise but increases total specimen dose.",
 "W1 — the instruction stays; the SNR/dose trade-off is rationale"),
("Sub-volume Stitching and Registration Method","XCT","3"):(
 "Where rotational mismatch has been corrected via raw projection re-alignment, document it here.",
 "Rotational mismatch artifacts have been identified in continuous-rotation acquisitions (~0.35° misalignment in Eckley et al. 2025).",
 "W1 — the instruction stays; the published finding behind it is rationale, and survives under W3 as an external citation"),
("Technique per Analyte","SEM,SEMcomp","2"):(
 "Required when a procedure employs both EDS and WDS simultaneously.",
 "Each element is assigned to the detector appropriate to its concentration range, line overlap situation, or required precision.",
 "W1 — the CONDITIONAL obligation stays (real content under W3); the assignment rationale moves"),
# --- straddles that resolve with nothing moving: splitting would break the sentence -----------
("Cross-Validation Outcome","XCT","3"):(None,"",
 "W1 resolves to NO SPLIT — the caveat is the grammatical OBJECT of the instruction ('note that BSE provides a 2D section...'). Extracting it leaves an instruction with nothing to note"),
("Partial Volume Effect Criteria","XCT","5"):(
 "State whether the criterion follows the Withers et al. (2021) convention — a feature must span at least 3 voxels to be positively identified and at least 10 for reliable shape and volume characterisation — or is SNR-limited, PVE-limited or analyst-defined.",
 "",
 "W1 resolves in place — moving the citation to Purpose would leave 'that convention' in Description with no antecedent. Recast so the antecedent is explicit; nothing moves. External-standard citation is real content under W3"),
("Sample Mounting Method","XCT","2"):(None,"",
 "W1 resolves to NO SPLIT — revised. 'should transmit X-rays at the selected voltage without dominating beam attenuation' is ONE constraint on the material, not an instruction plus a reason; the second half states the threshold the first half must meet"),
}
