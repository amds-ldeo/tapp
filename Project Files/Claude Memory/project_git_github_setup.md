---
name: project-git-github-setup
description: TAPPs is a git repo pushing to github.com/amds-ldeo/tapp on branch master; allowlist .gitignore; save with tapp-save.sh
metadata:
  type: project
---

Set up 2026-08-21. The TAPPs root is a git repository whose `origin` is the
**public** repo `https://github.com/amds-ldeo/tapp.git`. The branch is
**`master`**, not `main` — match it, do not rename.

`.gitignore` is an **allowlist**: `/*` ignores every root-level entry, then
five folders and two files are re-included — `Archive/`, `Claude Skills for
TAPP/`, `Current TAPPs/`, `Project Files/`, `Superseded TAPPs/`,
`composed_tapps.json`, `README_TAPP_for_Schema_Generation.md`. To track a new
root folder you must add `!/Folder Name/` — otherwise it is silently invisible
to git.

**Why:** the per-technique folders (EPMA/, SEM/, TEM/, LA-*/, Solution */,
XCT/, ...) hold ~614 MB of copyrighted publisher PDFs, 86% of the project by
size. They must never reach GitHub. An allowlist fails safe; a denylist would
leak any new paper folder. See [[project-tapp-folder-layout]].

**How to apply:** after any version bump or `sync_current_tapps.py` run, save
the record with `"Project Files/Scripts/tapp-save.sh" "message"` (add `-n` to
preview). Because `Current TAPPs/` mirrors only live versions (Rule 12), a
bump shows up as deletions of the superseded .xlsx there — that is correct,
and the old bytes stay recoverable from git history. Never force-push: the
pre-2026-08-21 commits (2edbaa0, baf33dc) are the only surviving copy of 16
intermediate TAPP versions.

**`tapp-save.sh` has two gates, and both refuse rather than warn.** (1) The schema
spec's generated counts must be current, checked when a `Current TAPPs/` CSV or the spec
itself is staged. (2) Added 2026-09-10: `validate_tapp.py` must report **0 ERROR and 0
WARN**. It runs on every save regardless of what is staged, because the incident that
prompted it was caused by markdown — committing the memory snapshot handed the doc scan
26 more `.md` files and produced 28 WARNs that nothing noticed for a day. ERROR has no
override. WARN takes `--allow-warn`, placed before the message, for a save you have
looked at and want anyway. Both gates unstage on refusal, so a refused save leaves the
index as it was. Cost is about half a second.

The repository is **PUBLIC**. Anything committed is published and indexable — check
before adding notes, exports or anything carrying local paths or personal data. The
memory snapshot at `Project Files/Claude Memory/` is sanitised for this reason; see
[[project_tapp_skill_sync]] for the sync scripts' conventions.
