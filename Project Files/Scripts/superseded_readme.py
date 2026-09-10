#!/usr/bin/env python3
"""Write a README skeleton into a dated `Superseded TAPPs/` folder.

    python3 superseded_readme.py 2026-09-08        # one date
    python3 superseded_readme.py --all             # every dated folder that lacks one
    python3 superseded_readme.py --all --dry       # report only

    from superseded_readme import write_skeleton   # called by the bump scripts
    write_skeleton(ROOT, "2026-09-08")

WHY THIS EXISTS. Eleven dated folders accumulated; three had a README and eight did not.
The three that did are the interesting ones — structural RETIREMENTS, where a TAPP was
decomposed into modules, a stale branch archived, or a TAPP split in two — and they were
written by hand because each needed an argument made. The eight that did not are routine
version bumps, where nobody wrote one because nothing felt worth saying, and the result is
that the provenance of a bump is recoverable only by reading git history and guessing which
patch script caused which version to move.

The derived half of that document needs no judgement: which versions were superseded, by
what, and how many files. This script writes that half at park time and leaves clearly
marked TODOs for the half that does need judgement — why the bump happened, and what was
verified. A skeleton with TODOs in it is a visible debt; a missing README is an invisible one.

SAFETY. An existing README is never overwritten without --force. That protects both the
hand-written retirement notes and any skeleton somebody has since filled in.
"""

import csv, glob, os, re, sys

DATED = re.compile(r"^\d{4}-\d{2}-\d{2}$")
VERS  = re.compile(r"^(.+)_v([\d.]+)\.(csv|xlsx)$")
TODO  = "TODO"


def _current_versions(root):
    """base stem -> current version, read from the Rule 12 mirror."""
    out = {}
    for f in glob.glob(os.path.join(root, "Current TAPPs", "*.csv")):
        m = VERS.match(os.path.basename(f))
        if m: out[m.group(1)] = m.group(2)
    return out


def _survey(folder, current):
    """(rows, n_files, subdirs) for one dated folder."""
    names = sorted(os.listdir(folder))
    subdirs = [n for n in names if os.path.isdir(os.path.join(folder, n))]
    files = [n for n in names if not os.path.isdir(os.path.join(folder, n))
             and n != "README.md"]
    rows = []
    for n in sorted(f for f in files if f.endswith(".csv")):
        m = VERS.match(n)
        if not m:
            rows.append((n, "", "not a versioned TAPP file")); continue
        stem, ver = m.group(1), m.group(2)
        rows.append((stem, ver, current.get(stem, "")))
    return rows, len(files), subdirs


def render(date, rows, n_files, subdirs):
    L = []
    L.append("# Superseded TAPPs — %s\n" % date)
    L.append("Retained for reference and provenance. **Do not develop against these, and do not "
             "register\nprocedures using them.** Folders beginning `Superseded` are excluded from "
             "`validate_tapp.py`\ndiscovery.\n")
    L.append("> **%s — skeleton.** The table below is generated from the folder contents. The "
             "prose\n> sections marked %s still need writing: say WHY these versions were "
             "superseded and what\n> was verified, then delete this block. See `../2026-09-09/"
             "README.md` for a routine bump and\n> `../2026-08-10/README.md` for a retirement.\n"
             % (TODO, TODO))

    if subdirs:
        L.append("## Folders\n")
        for d in subdirs:
            L.append("- **`%s/`** — %s: what this held and what replaced it." % (d, TODO))
        L.append("")

    if rows:
        L.append("## What was superseded, and by what\n")
        L.append("| Superseded | Successor |")
        L.append("|---|---|")
        for stem, ver, cur in rows:
            if not ver:
                L.append("| `%s` | %s — %s |" % (stem, TODO, cur)); continue
            succ = ("`v%s`" % cur) if cur else ("%s — no current TAPP of this name; retired?" % TODO)
            L.append("| `%s_v%s` | %s |" % (stem, ver, succ))
        n_versions = len([r for r in rows if r[1]])
        L.append("\n%d version(s), %d file(s) (CSV + xlsx).\n" % (n_versions, n_files))

    L.append("## Why\n")
    L.append("%s — what change caused these bumps, and which script applied it. Name the script so "
             "the\nfolder is traceable to the edit.\n" % TODO)
    L.append("## Verification\n")
    L.append("%s — what was run and what it reported. `validate_tapp.py` and, where a Column I key "
             "or a\nliterature column was touched, `audit_keys_vs_literature.py` (Rule 7.12). State "
             "whether any\nfield, tier, data type or `Keyed By` value changed.\n" % TODO)
    return "\n".join(L)


def write_skeleton(root, date, force=False, quiet=False):
    """Write the skeleton for one dated folder. Returns the path, or None if skipped."""
    folder = os.path.join(root, "Superseded TAPPs", date)
    if not os.path.isdir(folder):
        if not quiet: print("  superseded_readme: no folder %s" % date)
        return None
    dst = os.path.join(folder, "README.md")
    if os.path.exists(dst) and not force:
        if not quiet: print("  superseded_readme: %s already has a README — left alone" % date)
        return None
    rows, n_files, subdirs = _survey(folder, _current_versions(root))
    with open(dst, "w", encoding="utf-8") as fh:
        fh.write(render(date, rows, n_files, subdirs))
    if not quiet:
        print("  superseded_readme: wrote %s/README.md (%d version(s), %d file(s)) — %s sections "
              "need filling in" % (date, len([r for r in rows if r[1]]), n_files, TODO))
    return dst


def main(argv):
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    force = "--force" in argv
    dry   = "--dry" in argv
    args  = [a for a in argv if not a.startswith("--")]

    if "--all" in argv:
        base = os.path.join(root, "Superseded TAPPs")
        dates = sorted(d for d in os.listdir(base)
                       if DATED.match(d) and os.path.isdir(os.path.join(base, d)))
    elif args:
        dates = args
    else:
        print(__doc__); return 2

    todo = [d for d in dates
            if force or not os.path.exists(os.path.join(root, "Superseded TAPPs", d, "README.md"))]
    if not todo:
        print("  every dated folder already has a README — nothing to do"); return 0
    if dry:
        print("  would write a skeleton into: %s" % ", ".join(todo)); return 0
    for d in todo:
        write_skeleton(root, d, force=force)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
