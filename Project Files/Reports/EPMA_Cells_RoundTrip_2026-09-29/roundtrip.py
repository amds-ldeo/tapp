#!/usr/bin/env python3
"""EPMA cells round-trip (2026-09-29): can a procedure be regenerated from its literature cells alone?

    python3 roundtrip.py            # writes records/*.json and prints both stages

Stage 1 (mechanical). For each EPMA literature column, build a procedure record from the TAPP and the
cells only: fields with a procedure tier (C = Basic or Advanced), each classified as
  structured      a keyed or definer cell parsed into members and values (conventions 7.3.4)
  text            an unkeyed field, or a field keyed only by session domains (one value under 7.3.3)
  not stated      N          not applicable   N/A
  commentary only N with stated text after ' — '
  not assessed    blank
Stage 2 (fidelity). Each fact in facts.py (stated in the paper's EPMA methods) is looked up in the
record: recovered structured / as text / only in commentary / under the wrong member / in another
field / absent.
"""

import csv, io, json, os, re, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "Claude Skills for TAPP", "scripts"))
sys.path.insert(0, HERE)
import keyed_cells as K
from facts import FACTS

VERSION = sys.argv[1] if len(sys.argv) > 1 else "v84"      # e.g. `python3 roundtrip.py v85`
SRC = os.path.join(ROOT, "Current TAPPs", "EPMA_TAPP_%s.csv" % VERSION)
if not os.path.exists(SRC):                      # superseded: read the parked copy
    import glob
    SRC = (glob.glob(os.path.join(ROOT, "EPMA", "EPMA_TAPP_%s.csv" % VERSION))
           + glob.glob(os.path.join(ROOT, "Superseded TAPPs", "*", "EPMA_TAPP_%s.csv" % VERSION)))[0]


def norm(s):
    s = (s or "").casefold()
    for a, b in (("μ", "µ"), ("–", "-"), ("—", "-"), ("α", "a"), ("β", "b"), ("kev", "kv"), ("×", "x")):
        s = s.replace(a, b)
    return re.sub(r"\s+", "", s)


def columns(h):
    s = h.index("Literature Assessment"); out = {}
    for j in range(s + 1, len(h)):
        lab = h[j].replace("\n", " ")
        if not lab.strip():
            continue
        key = lab.split("|")[0].strip()
        if key == "Barnes+2025":
            key += "#JEOL" if "JEOL" in lab else "#Cameca"
        out[key] = j
    return out


def record(rows, j):
    """One column -> {field: {"status", "key", "value"}} for procedure-level fields."""
    rec = {}
    for r in rows[1:]:
        if not r or r[2].strip() not in ("Basic", "Advanced"):
            continue
        f, key, cell = r[0].strip(), r[8].strip(), r[j].strip()
        kind, doms = K.procedure_domains(key)
        struct, comment = K.split_commentary(cell)
        e = {"key": key, "cell": cell}
        if not cell:
            e["status"] = "not assessed"
        elif K.is_marker(cell):
            e["status"] = "not applicable" if struct.startswith("N/A") else (
                "commentary only" if comment else "not stated")
        elif kind in ("definer", "definer_per"):
            ms, errs = K.parse_definer(cell)
            e["status"] = "unparsed" if errs else "structured"
            e["value"] = [{"member": m, "parent": p} for m, p in ms]
        elif kind in ("plain", "pair"):
            ents, errs = K.parse_keyed(cell, levels=2 if len(doms) == 2 else 1, pair=(kind == "pair"))
            e["status"] = "unparsed" if errs else "structured"
            e["value"] = [{"members": n, "value": (v if isinstance(v, str) else [{"members": a, "value": b} for a, b in v])}
                          for n, v in ents]
        else:
            e["status"] = "text"; e["value"] = struct
        rec[f] = e
    return rec


def lookup(entries, member):
    """Value for a member in a parsed one-level list: explicit, else `all`, else `other`."""
    got = {K.norm(n): v for names, v in entries for n in names}
    return got.get(K.norm(member), got.get("all", got.get("other")))


def score(rec, field, member, tokens):
    toks = [norm(t) for t in tokens]
    hit = lambda s: any(t in norm(s) for t in toks)
    e = rec.get(field)
    if e is None:
        return "field not in record"
    struct, comment = K.split_commentary(e["cell"])
    if e["status"] == "not assessed":
        where = [g for g, x in rec.items() if g != field and hit(K.split_commentary(x["cell"])[0])]
        return "not assessed" + (" (found in %s)" % where[0] if where else "")
    if e["status"] in ("not stated", "not applicable", "commentary only"):
        if hit(comment):
            return "commentary only"
        where = [g for g, x in rec.items() if g != field and hit(K.split_commentary(x["cell"])[0])]
        return "in another field: %s" % where[0] if where else "absent"
    if member and e["status"] == "structured" and "value" in e and isinstance(e["value"], list) and e["value"] \
            and "members" in e["value"][0]:
        ents = [(x["members"], x["value"]) for x in e["value"]]
        if "/" in member:
            outer, inner = member.split("/", 1)
            blk = lookup(ents, outer)
            v = lookup([(x["members"], x["value"]) for x in blk], inner) if isinstance(blk, list) else None
        else:
            v = lookup(ents, member)
        if v is not None and hit(v):
            return "structured"
        return "wrong member or missing member" if hit(struct) else ("commentary only" if hit(comment) else "absent")
    if hit(struct):
        return "structured" if e["status"] == "structured" else "text"
    if hit(comment):
        return "commentary only"
    where = [g for g, x in rec.items() if g != field and hit(K.split_commentary(x["cell"])[0])]
    return "in another field: %s" % where[0] if where else "absent"


def main():
    rows = list(csv.reader(io.open(SRC, newline="", encoding="utf-8-sig")))
    cols = columns(rows[0])
    recdir = os.path.join(HERE, "records" if VERSION == "v84" else "records_" + VERSION)
    os.makedirs(recdir, exist_ok=True)
    st1 = Counter(); per_col1 = {}
    st2 = Counter(); per_col2 = {}; misses = []
    for key, j in cols.items():
        rec = record(rows, j)
        with io.open(os.path.join(recdir, re.sub(r"[^A-Za-z0-9+_#-]", "_", key) + ".json"), "w",
                     encoding="utf-8") as fh:
            json.dump({"procedure_column": rows[0][j].replace("\n", " "), "tapp": "EPMA_TAPP_" + VERSION,
                       "fields": rec}, fh, indent=1, ensure_ascii=False)
        c = Counter(e["status"] for e in rec.values()); st1.update(c); per_col1[key] = c
        c2 = Counter()
        for field, member, tokens, src in FACTS.get(key, []):
            res = score(rec, field, member, tokens)
            cat = res.split(" (")[0].split(":")[0]
            c2[cat] += 1
            if cat != "structured" and cat != "text":
                misses.append((key, field, member, res, src))
        st2.update(c2); per_col2[key] = c2

    n1 = sum(st1.values())
    print("STAGE 1 — procedure-level cells of %d columns (%s): %d" % (len(cols), os.path.basename(SRC), n1))
    for k, v in st1.most_common():
        print("  %-18s %5d  %3.0f%%" % (k, v, 100 * v / n1))
    n2 = sum(st2.values())
    print("\nSTAGE 2 — %d stated facts, recovered as:" % n2)
    for k, v in st2.most_common():
        print("  %-32s %4d  %3.0f%%" % (k, v, 100 * v / n2))
    print("\nper procedure (structured + text / facts):")
    for key, c in per_col2.items():
        ok = c["structured"] + c["text"]; t = sum(c.values())
        print("  %-20s %3d / %3d  %3.0f%%   %s" % (key, ok, t, 100 * ok / t if t else 0,
              ", ".join("%s %d" % (k, v) for k, v in c.items() if k not in ("structured", "text"))))
    print("\nfacts not recovered as structure or text:")
    for key, field, member, res, src in misses:
        print("  [%s] %s%s -> %s  («%s»)" % (key, field, " [%s]" % member if member else "", res, src[:70]))


if __name__ == "__main__":
    main()
