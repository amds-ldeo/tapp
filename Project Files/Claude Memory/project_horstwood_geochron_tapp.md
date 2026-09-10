---
name: project-horstwood-geochron-tapp
description: "Standalone TAPP exercise built from Horstwood et al. 2016's community reporting standard, compared against LA-Q/SF-ICP-MS TAPP and Solution MC-ICP-MS TAPP; produced a general cross-TAPP field now retrofitted into all TAPPs as Rule 5, and a working Q/SF/MC sub-TAPP filtering mechanism"
metadata:
  type: project
---
A TAPP built from Table 3 of Horstwood et al. (2016, *Geostandards and Geoanalytical Research*
40(3):311-332) — a human-workshop-derived community reporting standard for LA-ICP-MS U-(Th-)Pb
geochronology — as a deliberate COMPARISON EXERCISE against this project's AI-assisted,
seed-paper-driven workflow. Not an official TAPP. Lives in
`LA-ICP-MS Geochronology (Horstwood Test)/`, at v5 (122 fields).

**The durable finding, and the reason to keep this memory.** Filtering v5 into Q / SF / MC
sub-TAPPs from its flag columns showed **95 of 121 fields (79%) are fully general across all
three ICP-MS types; only 26 need instrument-scoping.** That is a data-backed argument for NOT
splitting a technique into per-instrument TAPPs, and for using flag columns where per-instrument
filtering is genuinely needed. It is the same argument that declined a separate MC-ICP-MS/MS
TAPP on 2026-08-31 — see [[project-tapp-datatype-two-type-scheme]].

**It also originated Rule 5.** "Constants and Reference Values Used" came out of this exercise
and is now mandatory library-wide — see [[project-tapp-rule5-constants-retrofit]].

The v1–v5 changelog and the deliverables list are dropped as dated; both are re-findable in that
folder and in git.
