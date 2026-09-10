#!/usr/bin/env python3
"""Mirror the out-of-repo Claude memory directory into the repo, sanitised.

    python3 "Project Files/Scripts/sync_memory_snapshot.py"          # dry run
    python3 "Project Files/Scripts/sync_memory_snapshot.py" --apply

SOURCE OF TRUTH IS OUTSIDE THE REPO. The live notes are at
`~/.claude/projects/<slugified-repo-path>/memory/`, which Claude reads and writes
directly. This script only makes a committed BACKUP of them; editing the snapshot in the
repo changes nothing that any session will ever read.

WHY IT SANITISES. `amds-ldeo/tapp` is a PUBLIC repository. The live notes carry two
things that are noise to a reader and needless exposure in public:

  * absolute home paths (`/Users/ruolin/...`) — the local filesystem layout
  * `originSessionId` and `modified` frontmatter — internal Claude session identifiers

Both are rewritten or dropped here. Nothing else is altered: the body text, the `name`,
`description` and `type` frontmatter, and the `[[wiki-links]]` are copied through
verbatim, so the snapshot is still readable as the notes it mirrors.

The scrub is re-applied on every run, so a later refresh cannot quietly reintroduce a
home path that someone added to a note in the meantime.
"""

import os, re, shutil, sys

DROP_KEYS = ("originSessionId", "modified")


def memory_dir(root):
    """~/.claude/projects/<abs repo path with / -> ->/memory — derived, not hardcoded."""
    slug = root.replace("/", "-")
    return os.path.join(os.path.expanduser("~"), ".claude", "projects", slug, "memory")


def scrub(text, root):
    out = []
    for ln in text.split("\n"):
        stripped = ln.strip()
        if any(stripped.startswith(k + ":") for k in DROP_KEYS):
            continue                                    # frontmatter only ever at line start
        ln = ln.replace(root + "/", "").replace(root, "(repo root)")
        ln = ln.replace(os.path.expanduser("~") + "/", "~/")
        ln = ln.replace(os.path.expanduser("~"), "~")
        out.append(ln)
    return "\n".join(out)


def main(apply=False):
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    src = memory_dir(root)
    dst = os.path.join(root, "Project Files", "Claude Memory")
    if not os.path.isdir(src):
        print("  no memory directory at %s" % src); return 1

    names = sorted(f for f in os.listdir(src) if f.endswith(".md"))
    if apply:
        os.makedirs(dst, exist_ok=True)
        # drop snapshot files whose source note is gone, so a deletion propagates
        for f in sorted(os.listdir(dst)):
            if f.endswith(".md") and f != "README.md" and f not in names:
                os.remove(os.path.join(dst, f)); print("  removed (source gone): %s" % f)

    changed = clean = 0
    for n in names:
        body = scrub(open(os.path.join(src, n), encoding="utf-8").read(), root)
        target = os.path.join(dst, n)
        old = open(target, encoding="utf-8").read() if os.path.exists(target) else None
        if old == body:
            clean += 1; continue
        changed += 1
        print("  %s %s" % ("update" if old is not None else "add   ", n))
        if apply:
            open(target, "w", encoding="utf-8").write(body)

    print("\n  %d note(s): %d to write, %d already current" % (len(names), changed, clean))
    if apply:
        leaks = []
        for n in names:
            t = open(os.path.join(dst, n), encoding="utf-8").read()
            if "/Users/" in t or any(k + ":" in t for k in DROP_KEYS):
                leaks.append(n)
        if leaks:
            print("  !! scrub incomplete in: %s" % ", ".join(leaks)); return 1
        print("  verified: no absolute home paths, no session identifiers")
    else:
        print("(dry run — pass --apply to write)")
    return 0


sys.exit(main("--apply" in sys.argv))
