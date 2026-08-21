# One-shot scripts (already applied)

Every script here made a change that is already applied to the TAPPs and version-bumped. They are
kept as the audit trail for how the library reached its current state — several are cited in
`Claude Skills for TAPP/references/precedents.md`.

**They are deliberately NOT path-corrected for this folder.** Rewriting already-applied history would
falsify the audit trail. Each computes its library root as its own directory, which is no longer
correct here, so re-running one from this location fails immediately on import rather than operating on
the wrong directory. If you ever need to re-run one, copy it to the library root first.

`audit_colI_vs_litassess_20260812.py` is superseded by
`Claude Skills for TAPP/scripts/audit_keys_vs_literature.py` — the same tool promoted into the skill as
a standing Phase 3 step (Rule 7.12). Run the skill copy, not this one.
