# Claude Memory — snapshot

**This folder is a backup. It is not read by anything.** The live notes are outside the repository, at
`~/.claude/projects/<slugified-repo-path>/memory/`, which is where Claude reads and writes them.
Editing a file here changes nothing any session will ever see — edit the live note, then re-run the
sync below.

Refresh:

```
python3 "Project Files/Scripts/sync_memory_snapshot.py"          # dry run
python3 "Project Files/Scripts/sync_memory_snapshot.py" --apply
```

## What these notes are

Working memory accumulated while developing the TAPP library — decisions and their reasoning, where
they are recorded, and the traps that have already cost time. `MEMORY.md` is the index; one file per
fact. They exist because the reasoning behind a Column I key or a retired vocabulary term is not
recoverable from the CSVs, and only partly from git.

They are **notes, not specification.** Where a note and the library disagree, the library is right:
`Claude Skills for TAPP/references/conventions.md` holds the rules, `precedents.md` the decisions,
and `Project Files/Design Notes/TAPP_Development_Log.md` the dated record. A note also reflects what
was true when it was written — several carry explicit corrections for exactly that reason, and one
was corrected on 2026-09-10 after asserting for weeks that the skill installation held only
`SKILL.md` when it in fact held all 83 files.

## Sanitisation

`amds-ldeo/tapp` is a **public** repository, so the sync rewrites two things on every run:

| Live note | Snapshot |
|---|---|
| `/Users/<user>/Documents/Astromat/TAPPs/EPMA/…` | `EPMA/…` (repo-relative) |
| other absolute home paths | `~/…` |
| `originSessionId:`, `modified:` frontmatter | dropped |

Body text, `name` / `description` / `type` frontmatter, and `[[wiki-links]]` are copied verbatim, so
the snapshot still reads as the notes it mirrors. The scrub re-runs each time rather than only on
first copy, so a home path added to a note later cannot slip through, and the script fails loudly if
anything survives it. A deleted live note is removed from the snapshot too, so this does not
accumulate notes that were retired on purpose.
