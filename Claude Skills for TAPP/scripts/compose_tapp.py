#!/usr/bin/env python3
"""
compose_tapp.py — build a TAPP CSV from a source file plus one or more modules.

A module is a block of fields shared across TAPPs (Group 1 today; a
Geochronology module and per-system modules later). The module owns the field
names, descriptions, tiers and data types; each consuming TAPP owns its own
examples, comments, dates and mode flags. Composing regenerates the consuming
TAPP so shared content lives in exactly one place, rather than being copied into
every TAPP and kept in step by hand (Rule 4).

Usage
-----
    # See what composing would change, without writing
    python3 compose_tapp.py --source LA-Q:SF-ICP-MS/LA-Q:SF-ICPMS_TAPP_v5.csv \
                            --module Group1 --diff

    # Write the composed TAPP
    python3 compose_tapp.py --source <in.csv> --module Group1 --out <out.csv>

    # Verify a TAPP already matches what composition would produce
    python3 compose_tapp.py --source <in.csv> --module Group1 --check

`--source` may be either a full TAPP (the module's target group is replaced) or
a partial TAPP with the target group absent (the module is inserted).

Column ownership
----------------
Declared per module in `modules/Module_<name>.json`:

  owned_columns     taken from the module, overwriting the source
  consumer_columns  preserved from the source, matched by field name
  mode flags        preserved from the source; `mode_flag_default` for new fields
  sentinel column   N on group headers, empty on data rows
  lit assessment    preserved from the source, matched by field name

Fields the source has under the target group but the module does not are
reported as `dropped` and are NOT silently discarded — composition refuses to
run unless `--allow-drop` is given.
"""

from __future__ import annotations

import argparse
import csv
import datetime
import json
import os
import re
import sys

SENTINEL_HEADER = "Literature Assessment"
COL_ITEM, COL_DESC, COL_C, COL_D, COL_TYPE, COL_EXAMPLE, COL_COMMENT, COL_UPDATE = range(8)
COL_KEYEDBY = 8  # Rule 7 — module-owned; see conventions.md Rule 7.5
COL_PURPOSE = 9    # Column J — consumer-owned, never module-owned
FIRST_MODE_COL = 10
LETTER = {c: i for i, c in enumerate("ABCDEFGHIJ")}

def owned_for(name, owned, manifest):
    """Rule 7.5 — a module may let a consuming TAPP override Keyed By for named
    fields, listed in the manifest as keyed_by_overridable. Every other module-owned
    column still reports DIFFERS on divergence."""
    if COL_KEYEDBY in owned and name in manifest.get("keyed_by_overridable", []):
        return [i for i in owned if i != COL_KEYEDBY]
    return owned


# Stamped into Last Update for fields a module CREATES. Existing fields keep the
# consumer's own date, so recomposing on a later day is still a no-op and --check
# continues to report MATCH.
TODAY = datetime.date.today().isoformat()

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(HERE)
ROOT = os.path.dirname(SKILL_DIR)


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #

def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.reader(f))


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        csv.writer(f).writerows(rows)


def load_module(name):
    base = os.path.join(SKILL_DIR, "modules", f"Module_{name}")
    csv_path, json_path = base + ".csv", base + ".json"
    for p in (csv_path, json_path):
        if not os.path.exists(p):
            sys.exit(f"error: module file not found: {p}")
    with open(json_path, encoding="utf-8") as f:
        manifest = json.load(f)
    return manifest, read_csv(csv_path)


def is_group_header(row):
    a = row[COL_ITEM].strip() if row else ""
    return bool(a) and bool(re.match(r"^\d+\.\s", a))


def is_separator(row, hi=COL_UPDATE):
    return not any((row[i].strip() if i < len(row) else "") for i in range(COL_ITEM, hi + 1))


def sentinel_index(header):
    return next((i for i, h in enumerate(header) if h.strip() == SENTINEL_HEADER), None)


# --------------------------------------------------------------------------- #
# Composition
# --------------------------------------------------------------------------- #


def stamp_source_comment(composed, manifest, module_rows):
    """Rule 6.11 — a module may declare `source_comment`, a short provenance label
    written into Column G for the fields it contributes. Used by the geochronology
    family so a reader of a system variant can see which fields came from the
    Geochronology / system module rather than from the instrument TAPP.

    Only ever fills an EMPTY Column G, so consumer annotation is never clobbered and
    recomposition stays idempotent. A Layer 3 module labels only the fields its blocks
    insert; its Column F overlays sit on fields another module owns and keep that
    module's label (or none, for general fields).
    """
    label = manifest.get("source_comment")
    if not label:
        return composed
    blocks = manifest.get("blocks")
    if blocks is not None:
        owned_names = {n for b in blocks for n in b["fields"]}
    else:
        owned_names = {r[COL_ITEM].strip() for r in module_rows[1:]
                       if r and r[COL_ITEM].strip() and not is_group_header(r)}
    for r in composed:
        if not r or r[COL_ITEM].strip() not in owned_names:
            continue
        cur = r[COL_COMMENT] if COL_COMMENT < len(r) else ""
        if not cur.strip():
            r[COL_COMMENT] = label
    return composed


def compose(source_rows, manifest, module_rows):
    rows, report = _compose(source_rows, manifest, module_rows)
    return stamp_source_comment(rows, manifest, module_rows), report


def _compose(source_rows, manifest, module_rows):
    """Return (composed_rows, report).

    Two placements are supported:

      replace_group  the module supplies the whole of `target_group`; the
                     group's existing rows are replaced by the module block.

      insert_before  the module supplies a block of fields inside an existing
                     group, inserted immediately before `anchor_field`. Fields
                     already present in the source are updated in place rather
                     than duplicated. Nothing is removed.
    """
    if manifest.get("blocks") is not None:
        return compose_overlay(source_rows, manifest, module_rows)
    if manifest.get("placement") == "insert_before":
        return compose_insert(source_rows, manifest, module_rows)

    header = source_rows[0]
    width = len(header)
    sent = sentinel_index(header)
    mode_span = range(FIRST_MODE_COL, sent) if sent is not None else range(FIRST_MODE_COL, width)
    lit_span = range(sent + 1, width) if sent is not None else range(width, width)

    owned = [LETTER[c] for c in manifest["owned_columns"]]
    target = manifest["target_group"]
    default_flag = manifest.get("mode_flag_default", "Y")

    # Index the source's existing rows for the target group, by field name.
    existing, group, start, end = {}, None, None, None
    for n, row in enumerate(source_rows[1:], start=1):
        if is_group_header(row):
            if group == target and start is not None and end is None:
                # The replaced block ends at the last field of the target group.
                # Back up over the separator row(s) so they are preserved, not
                # swallowed along with the group content.
                end = n
                while end - 1 > start and is_separator(source_rows[end - 1]):
                    end -= 1
            group = row[COL_ITEM].strip()
            if group == target:
                start = n
            continue
        if group == target and not is_separator(row):
            existing[row[COL_ITEM].strip()] = row
    if start is not None and end is None:
        # Target group is the last group in the file.
        end = len(source_rows)
        while end - 1 > start and is_separator(source_rows[end - 1]):
            end -= 1
    group_bounds = (start, end)

    module_fields = [r[COL_ITEM].strip() for r in module_rows[1:]
                     if r and r[COL_ITEM].strip() and not is_group_header(r)]
    dropped = [k for k in existing if k not in module_fields]
    added = [k for k in module_fields if k not in existing]

    # Build the replacement block.
    group_start = start
    block, overrides = [], []
    for mrow in module_rows[1:]:
        if not mrow or not mrow[COL_ITEM].strip():
            continue
        name = mrow[COL_ITEM].strip()
        out = [""] * width

        if is_group_header(mrow):
            # Preserve whatever the source's own group header row carried beyond the
            # sentinel — the library's convention is 'N' in every literature
            # assessment column on a group header, and a module cannot know how many
            # such columns a consumer has. Writing the row from scratch would drop
            # them and leave this group's header inconsistent with the other five.
            src_hdr = source_rows[group_start] if group_start is not None else None
            if src_hdr:
                for i in range(sent + 1 if sent is not None else width, width):
                    out[i] = src_hdr[i] if i < len(src_hdr) else ""
            out[COL_ITEM] = name
            for i in mode_span:
                out[i] = "N"
            if sent is not None:
                out[sent] = "N"
            block.append(out)
            continue

        src = existing.get(name)

        # Consumer-owned and dynamic columns come from the source when available.
        if src:
            for i in range(width):
                out[i] = src[i] if i < len(src) else ""
        else:
            for i in mode_span:
                out[i] = default_flag
            out[COL_UPDATE] = TODAY
        if sent is not None:
            out[sent] = ""

        # Module-owned columns overwrite.
        for i in owned_for(name, owned, manifest):
            before = out[i]
            out[i] = mrow[i] if i < len(mrow) else ""
            if src and before != out[i]:
                overrides.append((name, "ABCDEFGHIJ"[i], before, out[i]))

        block.append(out)

    # Splice the block into the source.
    if group_bounds[0] is None:
        composed = [header] + block + [[""] * width] + [r for r in source_rows[1:]]
    else:
        s, e = group_bounds
        composed = [header] + block + [r for r in source_rows[e:]]

    report = {
        "dropped": dropped,
        "added": added,
        "overrides": overrides,
        "module_fields": len(module_fields),
    }
    return composed, report


def compose_overlay(source_rows, manifest, module_rows):
    """Placement for Layer 3 system modules, which do two different things.

    A system module (U-Pb, Ar-Ar, …) both:

      overlays  fields introduced by a lower-layer module — supplying only the
                consumer-owned columns (typically F, the per-system examples and
                allowed values) and leaving names, tiers and descriptions alone;
      inserts   its own extension fields, for which it owns A–F.

    Rows are routed by name: a row listed in some block's `fields` is an
    insertion; any other row is an overlay applied wherever the field is found.
    Blocks may target different groups, so one module can contribute to Group 2
    and Group 5 in a single pass.
    """
    header = source_rows[0]
    width = len(header)
    sent = sentinel_index(header)
    mode_span = range(FIRST_MODE_COL, sent) if sent is not None else range(FIRST_MODE_COL, width)

    owned = [LETTER[c] for c in manifest["owned_columns"]]
    overlay_cols = [LETTER[c] for c in manifest.get("overlay_columns", manifest["owned_columns"])]
    default_flag = manifest.get("mode_flag_default", "Y")
    blocks = manifest["blocks"]
    wanted = manifest.get("_selected_blocks")
    # A conditional module's blocks are NOT universal — each carries an applies_when
    # condition and the consuming TAPP selects explicitly. Composing all of them by
    # default silently adds fields the TAPP deliberately omitted, which `--check` will
    # not catch: it compares cells in rows that exist and does not treat an ADDED row
    # as a difference. Require the selection rather than guessing it.
    if manifest.get("conditional") and wanted is None:
        return source_rows, {"error": (
            f"module '{manifest['module']}' is conditional — name the blocks explicitly, e.g. "
            f"--module {manifest['module']}:{','.join(b['name'] for b in blocks[:2])} , or "
            f"--module {manifest['module']}:all . Recorded per-consumer selections are in "
            f"composed_tapps.json."), "dropped": [], "added": [], "overrides": [], "module_fields": 0}
    if wanted == ["all"]:
        wanted = None          # explicit opt-in to every block
    if wanted is not None:
        named = {b.get("name") for b in blocks if b.get("name")}
        unknown = set(wanted) - named
        if unknown:
            return source_rows, {"error": f"unknown block(s) {sorted(unknown)}; "
                                          f"this module defines {sorted(named)}",
                                 "dropped": [], "added": [], "overrides": [], "module_fields": 0}
        blocks = [b for b in blocks if b.get("name") in wanted]
    inserted_names = {n for b in blocks for n in b["fields"]}

    module_by_name = {}
    for mrow in module_rows[1:]:
        if mrow and mrow[COL_ITEM].strip() and not is_group_header(mrow):
            module_by_name[mrow[COL_ITEM].strip()] = mrow

    composed = [r[:] for r in source_rows]
    overlaid, added, missing, overrides = [], [], [], []

    # 1. Overlays — everything not claimed by a block.
    index = {r[COL_ITEM].strip(): i for i, r in enumerate(composed)
             if r and r[COL_ITEM].strip() and not is_group_header(r)}
    for name, mrow in module_by_name.items():
        if name in inserted_names:
            continue
        if name not in index:
            missing.append(name)
            continue
        row = composed[index[name]]
        for i in overlay_cols:
            before = row[i] if i < len(row) else ""
            val = mrow[i] if i < len(mrow) else ""
            if not val:
                continue
            if before != val:
                overrides.append((name, "ABCDEFGHIJ"[i], before, val))
            row[i] = val
        overlaid.append(name)

    # 2. Insertions — one block at a time, recomputing positions as rows shift.
    for block in blocks:
        target = block["target_group"]
        anchor = block.get("anchor_field")
        group, anchor_idx, last_idx = None, None, None
        for n, row in enumerate(composed[1:], start=1):
            if is_group_header(row):
                group = row[COL_ITEM].strip()
                continue
            if group != target or is_separator(row):
                continue
            last_idx = n
            if anchor and row[COL_ITEM].strip() == anchor:
                anchor_idx = n
        at = anchor_idx if anchor_idx is not None else (last_idx + 1 if last_idx else None)
        if at is None:
            missing.append(f"{target} (group not found)")
            continue

        # Rebuild the name index each block — earlier blocks may have shifted rows.
        present = {r[COL_ITEM].strip(): i for i, r in enumerate(composed)
                   if r and r[COL_ITEM].strip() and not is_group_header(r)}

        new_rows = []
        for name in block["fields"]:
            mrow = module_by_name.get(name)
            if mrow is None:
                missing.append(name)
                continue

            if name in present:
                # Already in the source — update the module-owned columns in place.
                # Inserting instead would duplicate the field and blank the consumer's
                # Column F, which is what happens when a module is composed back into
                # the TAPP it was extracted from.
                row = composed[present[name]]
                for i in owned_for(name, owned, manifest):
                    before = row[i] if i < len(row) else ""
                    val = mrow[i] if i < len(mrow) else ""
                    if before != val:
                        overrides.append((name, "ABCDEFGHIJ"[i], before, val))
                    row[i] = val
                overlaid.append(name)
                continue

            out = [""] * width
            for i in owned_for(name, owned, manifest):
                out[i] = mrow[i] if i < len(mrow) else ""
            for i in mode_span:
                out[i] = default_flag
            out[COL_UPDATE] = TODAY
            if sent is not None:
                out[sent] = ""
            new_rows.append(out)
            added.append(name)
        composed[at:at] = new_rows

    return composed, {
        "dropped": [],
        "added": added,
        "updated": overlaid,
        "missing": missing,
        "overrides": overrides,
        "module_fields": len(added) + len(overlaid),
    }


def compose_insert(source_rows, manifest, module_rows):
    """Insert a module block inside an existing group, before `anchor_field`."""
    header = source_rows[0]
    width = len(header)
    sent = sentinel_index(header)
    mode_span = range(FIRST_MODE_COL, sent) if sent is not None else range(FIRST_MODE_COL, width)

    owned = [LETTER[c] for c in manifest["owned_columns"]]
    target = manifest["target_group"]
    anchor = manifest["anchor_field"]
    default_flag = manifest.get("mode_flag_default", "Y")

    # Locate the anchor row inside the target group.
    group, anchor_idx = None, None
    existing = {}
    for n, row in enumerate(source_rows[1:], start=1):
        if is_group_header(row):
            group = row[COL_ITEM].strip()
            continue
        if group != target or is_separator(row):
            continue
        name = row[COL_ITEM].strip()
        existing[name] = n
        if name == anchor:
            anchor_idx = n
    if anchor_idx is None:
        return source_rows, {"error": f"anchor field {anchor!r} not found in group {target!r}",
                             "dropped": [], "added": [], "overrides": [], "module_fields": 0}

    composed = [r[:] for r in source_rows]
    added, overrides, updated = [], [], []
    new_rows = []

    for mrow in module_rows[1:]:
        if not mrow or not mrow[COL_ITEM].strip() or is_group_header(mrow):
            continue
        name = mrow[COL_ITEM].strip()

        if name in existing:
            # Already present: overwrite module-owned columns in place.
            row = composed[existing[name]]
            for i in owned_for(name, owned, manifest):
                before = row[i] if i < len(row) else ""
                val = mrow[i] if i < len(mrow) else ""
                if before != val:
                    overrides.append((name, "ABCDEFGHIJ"[i], before, val))
                row[i] = val
            updated.append(name)
            continue

        out = [""] * width
        for i in owned_for(name, owned, manifest):
            out[i] = mrow[i] if i < len(mrow) else ""
        for i in mode_span:
            out[i] = default_flag
        out[COL_UPDATE] = TODAY
        if sent is not None:
            out[sent] = ""
        new_rows.append(out)
        added.append(name)

    composed[anchor_idx:anchor_idx] = new_rows

    return composed, {
        "dropped": [],
        "added": added,
        "updated": updated,
        "overrides": overrides,
        "module_fields": len(added) + len(updated),
    }


def row_diff(a_rows, b_rows, header):
    """Cell-level diff keyed by field name, for --diff / --check."""
    def index(rows):
        d = {}
        for n, r in enumerate(rows[1:], start=2):
            if r and r[COL_ITEM].strip() and not is_group_header(r):
                d[r[COL_ITEM].strip()] = (n, r)
        return d

    A, B = index(a_rows), index(b_rows)
    diffs = []
    for name in B:
        if name not in A:
            continue
        (_, ra), (nb, rb) = A[name], B[name]
        for i in range(max(len(ra), len(rb))):
            x = ra[i] if i < len(ra) else ""
            y = rb[i] if i < len(rb) else ""
            if x != y:
                col = header[i] if i < len(header) else f"col{i}"
                diffs.append((nb, name, col, x, y))
    order_a = [n for n in A]
    order_b = [n for n in B if n in A]
    order_changed = [n for n in order_b if n in order_a] != [n for n in order_a if n in order_b]
    return diffs, order_changed


TAPP_NAME_RE = re.compile(r"_TAPP_v\d+\.csv$")


def record_composition(out_path, specs, quiet=False):
    """Write what was just composed into composed_tapps.json.

    Rule 6.9 recorded this as an open item: the register was maintained by hand and this script
    neither read nor wrote it, so the record of which modules built which TAPP could drift from the
    library silently — and twice did (6.13). The tool that performs the composition is the one that
    knows it happened, so it is the one that records it.

    Only writes for a real TAPP inside the library. Composing to a scratch path is a normal thing to
    do while testing and must not touch the register.
    """
    base = os.path.basename(out_path)
    if not TAPP_NAME_RE.search(base):
        if not quiet:
            print(f"  (not recorded: {base} is not a versioned TAPP filename)")
        return
    try:
        rel = os.path.relpath(out_path, ROOT)
    except ValueError:
        rel = None
    if rel is None or rel.startswith(os.pardir):
        if not quiet:
            print("  (not recorded: output is outside the library root)")
        return

    reg_path = os.path.join(ROOT, "composed_tapps.json")
    try:
        with open(reg_path, encoding="utf-8") as fh:
            reg = json.load(fh)
    except (OSError, ValueError) as exc:
        print(f"  WARNING: could not read composed_tapps.json ({exc}); composition NOT recorded")
        return

    entries = reg.setdefault("composed", [])
    entry = next((e for e in entries if os.path.basename(e.get("tapp", "")) == base), None)
    if entry is None:
        # Same TAPP at a previous version — carry the entry forward, keeping its notes.
        stem = TAPP_NAME_RE.sub("", base)
        entry = next((e for e in entries
                      if TAPP_NAME_RE.sub("", os.path.basename(e.get("tapp", ""))) == stem), None)
        if entry is not None:
            entry["tapp"] = rel
        else:
            entry = {"tapp": rel, "modules": []}
            entries.append(entry)
    else:
        entry["tapp"] = rel

    mods = entry.setdefault("modules", [])
    for spec in specs:
        name, _, blocks = spec.partition(":")
        try:
            manifest, _ = load_module(name)
            version = str(manifest.get("version", ""))
        except SystemExit:
            version = ""
        rec = next((m for m in mods if m.get("name") == name), None)
        if rec is None:
            rec = {"name": name}
            mods.append(rec)
        if version:
            rec["version"] = version
        if blocks:
            rec["blocks"] = blocks
        elif "blocks" in rec:
            del rec["blocks"]

    reg["generated"] = TODAY
    with open(reg_path, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    if not quiet:
        print(f"  recorded in composed_tapps.json: {', '.join(specs)}")

    # TAPP_Composed_Variants.csv carries a path column for the system variants. It is the second
    # register that goes stale on a bump, and validate_tapp.py reports that at WARN
    # (doc-stale-version-ref). Keeping it in step here rather than leaving it to the operator is the
    # whole point of recording from inside the tool that did the composing.
    variants = os.path.join(ROOT, "Project Files", "Registers & Planning",
                            "TAPP_Composed_Variants.csv")
    if not os.path.exists(variants):
        return
    stem = TAPP_NAME_RE.sub("", base)
    try:
        with open(variants, newline="", encoding="utf-8-sig") as fh:
            rows = list(csv.reader(fh))
    except OSError:
        return
    hits = 0
    for row in rows[1:]:
        for i, cell in enumerate(row):
            cell = cell.strip()
            if not cell.endswith(".csv"):
                continue
            if TAPP_NAME_RE.sub("", os.path.basename(cell)) == stem and os.path.basename(cell) != base:
                row[i] = rel
                hits += 1
    if hits:
        with open(variants, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rows)
        if not quiet:
            print(f"  updated TAPP_Composed_Variants.csv ({hits} path reference)")


def main():
    ap = argparse.ArgumentParser(description="Compose a TAPP from a source plus modules.")
    ap.add_argument("--source", required=True, help="source TAPP CSV (relative to library root or absolute)")
    ap.add_argument("--module", required=True, action="append",
                    help="module name, e.g. Group1. Append ':block1,block2' to compose only "
                         "selected blocks of a module whose fields are conditionally applicable, "
                         "e.g. --module ReportingCore:aggregation,blank")
    ap.add_argument("--out", help="write composed TAPP here")
    ap.add_argument("--diff", action="store_true", help="show what composition would change")
    ap.add_argument("--check", action="store_true", help="exit 1 if the source differs from the composed result")
    ap.add_argument("--allow-drop", action="store_true", help="permit fields present in source but absent from module")
    ap.add_argument("--no-record", action="store_true",
                    help="do not record this composition in composed_tapps.json (default is to "
                         "record whenever --out writes a versioned TAPP inside the library)")
    args = ap.parse_args()

    src_path = args.source if os.path.isabs(args.source) else os.path.join(ROOT, args.source)
    if not os.path.exists(src_path):
        sys.exit(f"error: source not found: {src_path}")
    source_rows = read_csv(src_path)
    header = source_rows[0]

    composed = source_rows
    reports = []
    for spec in args.module:
        name, _, blocks = spec.partition(":")
        manifest, module_rows = load_module(name)
        if blocks:
            manifest["_selected_blocks"] = [b.strip() for b in blocks.split(",") if b.strip()]
        composed, rep = compose(composed, manifest, module_rows)
        rep["name"] = spec
        reports.append(rep)

    print(f"source : {os.path.relpath(src_path, ROOT)}")
    print(f"modules: {', '.join(args.module)}")
    for rep in reports:
        if rep.get("error"):
            print(f"\n[{rep['name']}] ERROR: {rep['error']}")
            return 2
        print(f"\n[{rep['name']}] {rep['module_fields']} module field(s)")
        if rep["added"]:
            print(f"  added   ({len(rep['added'])}): {rep['added']}")
        if rep.get("updated"):
            print(f"  overlaid ({len(rep['updated'])}): {rep['updated']}")
        if rep.get("missing"):
            print(f"  MISSING from source ({len(rep['missing'])}): {rep['missing']}")
            print("  (a system module overlays fields supplied by a lower-layer module —"
                  " compose that module first)")
        if rep["dropped"]:
            print(f"  DROPPED ({len(rep['dropped'])}): {rep['dropped']}")
        if rep["overrides"]:
            print(f"  module-owned columns overwritten: {len(rep['overrides'])}")

    blocked = [r for r in reports if r["dropped"]] and not args.allow_drop
    if blocked:
        print("\nrefusing to compose: source has fields the module does not define.")
        print("re-run with --allow-drop if that is intended.")
        return 2

    if args.diff or args.check:
        diffs, order_changed = row_diff(source_rows, composed, header)
        print(f"\n{'=' * 92}")
        print(f"DIFF vs source — {len(diffs)} cell(s) would change"
              f"{'; field order also differs' if order_changed else ''}")
        print("=" * 92)
        by_col = {}
        for n, name, col, old, new in diffs:
            by_col.setdefault(col, []).append((n, name, old, new))
        for col, items in by_col.items():
            print(f"\n  column: {col}   ({len(items)} cell(s))")
            for n, name, old, new in items:
                print(f"    row {n:>3}  {name}")
                print(f"          source   : {old[:110]}")
                print(f"          composed : {new[:110]}")
        if args.check:
            ok = not diffs and not order_changed
            print(f"\n{'MATCH' if ok else 'DIFFERS'}")
            return 0 if ok else 1

    if args.out:
        out_path = args.out if os.path.isabs(args.out) else os.path.join(ROOT, args.out)
        write_csv(out_path, composed)
        print(f"\nwrote {os.path.relpath(out_path, ROOT)}  ({len(composed)} rows)")
        if args.no_record:
            print("  (--no-record: composed_tapps.json not updated)")
        else:
            record_composition(out_path, args.module)

    return 0


if __name__ == "__main__":
    sys.exit(main())
