#!/usr/bin/env python3
"""The keyed-value notation (conventions 7.3.4): parse a literature-assessment cell into members and values.

A literature cell holds every member's value for one procedure, flattened into one cell. Column I
says what the members are; the definer cell in the same column names them. This module is the one
grammar shared by validate_tapp.py and the form generator (Project Files/Reports/build_form.py).

    cell        := marker | structured [" — " commentary]
    marker      := "N" | "N/A" , optionally followed by " (…)" — no structure is read
    structured  := entry (";" entry)*                      separators at top level only
    entry       := members ": " value                      one procedure-level domain
                 | members " [" structured "]"             two domains (A x B): outer members, inner entries
    members     := member ("," member)*  | "all" | "other"
    member      := name | name " & " name                  "&" joins the two members of a pair: key
    definer     := dentry (";" dentry)*
    dentry      := dmember ("," dmember)* [" → " parent]   parent binding for `defines: A per B`
    dmember     := id [" (" gloss ")"]                     the gloss is not part of the id

"Top level" means outside (), [] and double quotes, so a value may contain any separator inside
brackets, or be quoted whole. The member/value colon must be followed by a space: `He:H2` and
`10:30` do not split. Everything after the first top-level " — " is commentary (evidence, quotes)
and is never parsed.
"""

import re

EMDASH = " — "
ARROWS = (" → ", " -> ")
RESERVED = {"all", "other"}
SESSION_DOMAINS = {"sample", "sampling unit", "combined result"}      # dropped under 7.3.3
MARKER_RE = re.compile(r"^N(/A)?(\s*\(.*\))?\.?$", re.S)
OPEN, CLOSE = "([", ")]"
QUOTES = '"“”'


def _scan(s):
    """Yield (index, char, depth, in_quote) for every character of s."""
    depth, q = 0, False
    for i, c in enumerate(s):
        if c in QUOTES:
            yield i, c, depth, True          # a quote mark is never a separator
            q = not q
            continue
        if not q and c in CLOSE:
            depth = max(0, depth - 1)
        yield i, c, depth, q                 # brackets report the depth outside them
        if not q and c in OPEN:
            depth += 1


def split_top(s, sep):
    """Split s on sep where sep starts at top level."""
    out, start, i = [], 0, 0
    top = {i for i, c, d, q in _scan(s) if d == 0 and not q}
    while i <= len(s) - len(sep):
        if i in top and s.startswith(sep, i) and all(j in top for j in range(i, i + len(sep))):
            out.append(s[start:i]); i += len(sep); start = i
        else:
            i += 1
    out.append(s[start:])
    return out


def find_top(s, sep):
    parts = split_top(s, sep)
    return -1 if len(parts) == 1 else len(parts[0])


def unquote(s):
    s = s.strip()
    if len(s) > 1 and s[0] in QUOTES and s[-1] in QUOTES:
        return s[1:-1].strip()
    return s


def strip_gloss(s):
    """'Silicate mineral (olivine, pyroxene)' -> 'Silicate mineral'. Quoted names keep everything."""
    s = s.strip()
    if s and s[0] in QUOTES:
        return unquote(s)
    if s.endswith(")"):
        depth = 0
        for i in range(len(s) - 1, -1, -1):
            if s[i] == ")":
                depth += 1
            elif s[i] == "(":
                depth -= 1
                if depth == 0:
                    head = s[:i].strip()
                    return head if head else s
    return s


def norm(s):
    return re.sub(r"\s+", " ", unquote(s)).strip().casefold()


def split_commentary(cell):
    cell = (cell or "").strip()
    i = find_top(cell, EMDASH)
    return (cell, "") if i < 0 else (cell[:i].strip(), cell[i + len(EMDASH):].strip())


def is_marker(cell):
    """Blank, N or N/A (with an optional reason) — nothing to parse."""
    s, _ = split_commentary(cell)
    return not s or bool(MARKER_RE.match(s))


def procedure_domains(keyed_by):
    """Column I -> (kind, [procedure-level domains]) after projection (7.3.3).

    kind: 'none' | 'definer' | 'definer_per' | 'plain' | 'pair' | 'session'.
    """
    k = (keyed_by or "").strip()
    if k in ("", "(none)"):
        return "none", []
    m = re.match(r"^defines:\s*(.+?)\s+per\s+(.+)$", k)
    if m:
        return "definer_per", [m.group(1).strip(), m.group(2).strip()]
    m = re.match(r"^defines:\s*(.+)$", k)
    if m:
        dom = m.group(1).strip()
        return ("session", []) if (">" in dom or dom in SESSION_DOMAINS) else ("definer", [dom])
    m = re.match(r"^pair:\s*(.+)$", k)
    if m:
        return "pair", [m.group(1).strip()]
    parts = [p.strip() for p in re.split(r"\s+x\s+|\s*>\s*", k) if p.strip()]
    kept = [p for p in parts if p not in SESSION_DOMAINS]
    return ("plain", kept) if kept else ("session", [])


def parse_definer(cell):
    """-> ([(member_id, parent_or_None)], errors)."""
    s, _ = split_commentary(cell)
    out, errs = [], []
    for ent in split_top(s, ";"):
        ent = ent.strip()
        if not ent:
            continue
        parent = None
        for a in ARROWS:
            i = find_top(ent, a)
            if i >= 0:
                ent, parent = ent[:i], unquote(ent[i + len(a):])
                break
        for mem in split_top(ent, ","):
            mid = strip_gloss(mem)
            if not mid:
                continue
            if ": " in mid or len(mid) > 60:
                errs.append("not a member list: %r" % mid[:60])
            out.append((mid, parent))
    return out, errs


def _entries(s, levels, errs, pair=False):
    """-> list of (members, value-or-dict)."""
    out = []
    for ent in split_top(s, ";"):
        ent = ent.strip()
        if not ent:
            continue
        if levels == 2:
            i = find_top(ent, " [")
            if i < 0 or not ent.endswith("]"):
                errs.append("two-level entry needs 'members [inner]': %r" % ent[:50]); continue
            mems, inner = ent[:i], ent[i + 2:-1]
            val = _entries(inner, 1, errs)
        else:
            i = find_top(ent, ": ")
            if i < 0:
                errs.append("no 'member: value' in %r" % ent[:50]); continue
            mems, val = ent[:i], ent[i + 2:].strip()
            if not val:
                errs.append("empty value after %r" % mems[:30])
        names = [unquote(m) for m in split_top(mems, ",") if m.strip()]
        if not names:
            errs.append("no member before the value in %r" % ent[:50]); continue
        if pair and not all(n in RESERVED or " & " in n for n in names):
            errs.append("pair key needs 'a & b' members: %r" % mems[:50])
        out.append((names, val))
    return out


def parse_keyed(cell, levels=1, pair=False):
    """-> (entries, errors). entries: [(members, value)] or, for levels=2, [(members, [(members, value)])]."""
    s, _ = split_commentary(cell)
    errs = []
    ents = _entries(s, levels, errs, pair)
    seen = set()
    flat = [n for names, _ in ents for n in names]
    for n in flat:
        if norm(n) in seen and norm(n) not in RESERVED:
            errs.append("member %r appears twice" % n)
        seen.add(norm(n))
    if "all" in [norm(n) for n in flat] and len(flat) > 1:
        errs.append("'all' must be the only member")
    if "other" in [norm(n) for n in flat]:
        last = ents[-1][0] if ents else []
        if [norm(n) for n in last] != ["other"]:
            errs.append("'other' must be alone, in the last entry")
    return ents, errs


def check_cell(cell, keyed_by, definer_members):
    """Validate one literature cell of a field. definer_members: {domain: set(normalised ids) or None}.

    -> (status, messages); status in {'skip', 'ok', 'unparsed', 'unknown-member'}.
    """
    if is_marker(cell):
        return "skip", []
    kind, doms = procedure_domains(keyed_by)
    if kind in ("none", "session"):
        return "skip", []
    if kind in ("definer", "definer_per"):
        mems, errs = parse_definer(cell)
        if errs:
            return "unparsed", errs
        if kind == "definer_per":
            known = definer_members.get(doms[1])
            bad = [p for _, p in mems if p and norm(p) != "none" and known is not None and norm(p) not in known]
            unbound = [m for m, p in mems if p is None and known is not None and norm(m) not in known]
            msgs = (["parent %r is not a member of %s" % (p, doms[1]) for p in bad]
                    + ["%r has no '→ parent' and no %s of the same name" % (m, doms[1]) for m in unbound])
            if msgs:
                return "unknown-member", msgs
        return "ok", []
    levels = 2 if len(doms) == 2 else 1
    ents, errs = parse_keyed(cell, levels, pair=(kind == "pair"))
    if errs:
        return "unparsed", errs
    msgs = []

    def check(names, dom):
        known = definer_members.get(dom)
        if known is None:
            return
        for n in names:
            parts = n.split(" & ") if kind == "pair" else [n]
            for p in parts:
                if norm(p) not in RESERVED and norm(p) not in known:
                    msgs.append("%r is not a member of %s" % (p, dom))

    for names, val in ents:
        check(names, doms[0])
        if levels == 2:
            for inner, _ in val:
                check(inner, doms[1])
    return ("unknown-member", msgs) if msgs else ("ok", [])


def values_by_member(cell, members):
    """For a one-level keyed cell: -> (all_value_or_None, {member: value}) using the definer's member order."""
    ents, errs = parse_keyed(cell)
    if errs:
        return None, {}
    allv, per, other = None, {}, None
    for names, val in ents:
        for n in names:
            if norm(n) == "all":
                allv = val
            elif norm(n) == "other":
                other = val
            else:
                per[norm(n)] = val
    out = {m: per.get(norm(m), other or "") for m in members} if not allv else {}
    return allv, out


if __name__ == "__main__":          # self-test
    assert split_commentary('Si, Al: TAP — "quoted; text"') == ("Si, Al: TAP", '"quoted; text"')
    assert is_marker("N") and is_marker("N/A — mapping only") and is_marker("N (not stated)")
    e, x = parse_keyed("Si, Al, Ca: anorthite; Na: albite (Amelia); other: N")
    assert not x and e[0] == (["Si", "Al", "Ca"], "anorthite") and e[2] == (["other"], "N"), (e, x)
    e, x = parse_keyed("all: 20 s — 'on peak'")
    assert not x and e == [(["all"], "20 s")]
    e, x = parse_keyed("20 s")
    assert x
    e, x = parse_keyed("He: He:H2 92% : 8%")          # only the first ': ' splits
    assert not x and e == [(["He"], "He:H2 92% : 8%")], e
    e, x = parse_keyed("Plešovice [206Pb/238U date: within 1%; all: N]", levels=2)
    assert not x and e[0][0] == ["Plešovice"], (e, x)
    m, x = parse_definer("Silicate mineral (olivine, pyroxene); Oxide (chromite) — note")
    assert [a for a, _ in m] == ["Silicate mineral", "Oxide"] and not x, m
    m, x = parse_definer("206Pb, 207Pb → Pb; 202Hg → none")
    assert m == [("206Pb", "Pb"), ("207Pb", "Pb"), ("202Hg", "none")], m
    assert procedure_domains("combined result x reported property") == ("plain", ["reported property"])
    assert procedure_domains("sample > sampling unit") == ("session", [])
    st, _ = check_cell("Fe: LIFL; Zn: TAP", "monitored property", {"monitored property": {"fe", "mg"}})
    assert st == "unknown-member"
    print("keyed_cells self-test passed")
