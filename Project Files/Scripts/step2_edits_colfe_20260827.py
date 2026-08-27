E = {
# --- pure re-listing of the controlled list: W2 deletes, Column F carries it -----------------
("Analytical Sub-mode","TEM","2"):("","","W2 DELETE — verbatim re-listing of the TEM Imaging values in Column F, which groups them the same way. S1 and S5 keep the definition and the multi-value instruction (M1)"),
("Analytical Sub-mode","TEM","3"):("","","W2 DELETE — as S2, STEM Imaging values"),
("Analytical Sub-mode","TEM","4"):("","","W2 DELETE — as S2, Electron Diffraction values"),
("Detector Binning","XCT","3"):("","","W2 DELETE — Column F's first value is literally '1×1 (no binning)'"),
# --- Column E restatement, with real formatting guidance after it ----------------------------
("Beam Current","FIB,SEM,SEMcomp,SEMimg","3"):("For sub-nA values use decimal notation (e.g., 0.4 nA).","","W2 — 'Express in nA' carried by Data Type `Numeric (nA)`; the sub-nA notation guidance is not"),
# --- KEEP: Column F NAMES these values but does not carry what the sentence adds --------------
("Background Correction Method","EPMA,SEM,SEMcomp","2"):(None,"","KEEP — revised. Column F lists all 11 methods FLAT; it does not say which apply to WDS and which to EDS. The detector-to-method mapping is content Column F lacks"),
("Background Correction Method","EPMA,SEM,SEMcomp","3"):(None,"","KEEP — the EDS half of the same mapping"),
("BSE Detector Type","FIB,SEM,SEMimg","4"):(None,"","KEEP — Column F names 'segmented, composition mode' and 'segmented, topography mode' but not the MECHANISM ('segments summed', 'differential signal between segments'), which is what this sentence adds. NOTE: this flag should have been withdrawn during Step 1 — the withdrawal was written but silently failed to apply"),
("EDS Spectral Processing Type","EPMA,SEM,SEMcomp","3"):(None,"","KEEP — Column F names the approaches; it does not carry their SEQUENCE ('followed by peak integration') or WHEN they apply ('for overlapping peaks')"),
("EDS Spectral Processing Type","TEM","3"):(None,"","KEEP — as the EPMA/SEM variant"),
("Output Bit Depth","XCT","2"):(None,"","KEEP — Column F names the bit depths; the gray-level counts are content it lacks, and S3's dynamic-range point depends on them"),
}
