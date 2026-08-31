#!/usr/bin/env python3
"""Mark illustrative Column F lists with `e.g.,` (2026-08-31).

Follow-up to the 2026-08-30 `Other: specify` sweep, which found that option ONLY ever appeared
where Column F was written as a pipe-separated member list — the controlled-list convention —
and never on a list prefixed `e.g.,`. Stripping it left 66 fields whose Column F still LOOKS
like a vocabulary while the type says `Text (free)`, `Integer` or `Numeric (...)`. A member
list on a free-text type is a smell: either the field is mis-typed, or the list is examples
wearing a vocabulary's clothes.

Measured against the literature, it is overwhelmingly the latter. Of the 57 fields with
attested cells, **44 have ZERO cells matching any listed member**, at distinctness ratios of
0.85-1.00 — `Digestion Acid(s)`, `Interfering Species`, `Nebulizer Type`, `Analysis Sequence`
and the rest are illustrating a shape, not enumerating a domain.

Two rules decide it, and neither invents anything:

  * `Numeric (...)`, `Numeric + unit`, `Numeric pair` and `Integer` are ALWAYS illustrative.
    There is no controlled list of numbers; Column F on a numeric field can only ever be
    examples. These take `e.g.,` regardless of attestation.
  * `Text (free)` takes `e.g.,` where the evidence says illustrative — at most 25% of attested
    cells matching a member, on 3 or more cells.

HELD BACK, not marked: the handful where the list IS doing work and the field may be genuinely
mis-typed — `Isotope Dilution Data Reduction Method` (62% bare, 13 cells),
`Sampler and Skimmer Cone Material` (50%, 10), `Isotope Dilution Spike` (50%, 12),
`Internal Standard Element` (43%, 14), `Detector Configuration` (50%, 6). Those want a Column E
retype, which is module-owned for most of them, and that is a separate decision from a
cosmetic prefix. Fields with NO attested cells are held too — nothing to judge them on.

Column F is TAPP-owned or overlay on every module involved, so this is a TAPP-level edit with
no module changes and no type changes anywhere.
"""
import csv, json, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-08-31"
FLAG = {"Y", "N", "-"}
NOT = re.compile(r"^(n/?a\b|n\s*\(|not\s+(stated|reported|specified|given))", re.I)
TAG = re.compile(r"\s*\[P[\d, ]+\]\s*$")
PARENS = re.compile(r"\s*\([^)]*\)")
NUMERIC = re.compile(r"^(Integer|Numeric\b)")

def norm(s): return re.sub(r"\s+", " ", s.strip().strip("'\"")).lower()

def survey(mirror):
    rec = {}
    for f in sorted(mirror.glob("*.csv")):
        fh = open(f, encoding="utf-8-sig"); rd = csv.DictReader(fh); hdr = rd.fieldnames
        pc = hdr[hdr.index("Literature Assessment") + 1:] if "Literature Assessment" in hdr else []
        for r in rd:
            dt = (r.get("Data Type") or "").strip(); ex = r.get("Example / Allowed Content") or ""
            if dt.startswith("Controlled list") or not ex.strip(): continue
            if ex.strip().lower().startswith("e.g") or "|" not in ex: continue
            a = rec.setdefault(r["Metadata Item"], {"num": True, "att": 0, "bare": 0})
            a["num"] = a["num"] and bool(NUMERIC.match(dt))
            A = {norm(v) for v in ex.split("|") if v.strip()}
            As = {norm(PARENS.sub("", v)) for v in ex.split("|") if v.strip()}
            for h in pc:
                v = TAG.sub("", (r.get(h) or "").strip())
                if not v or v in FLAG or NOT.match(v): continue
                a["att"] += 1
                if norm(v) in A or norm(PARENS.sub("", v)) in As: a["bare"] += 1
    mark, hold = set(), {}
    for it, a in rec.items():
        if a["num"]: mark.add(it); continue
        if a["att"] < 3: hold[it] = f"only {a['att']} attested cell(s)"; continue
        bp = a["bare"] / a["att"]
        if bp <= 0.25: mark.add(it)
        else: hold[it] = f"{bp*100:.0f}% bare on {a['att']} cells — possible mis-type"
    return mark, hold

def main():
    dry = "--apply" not in sys.argv
    mark, hold = survey(ROOT / "Current TAPPs")
    print(f"MARK with 'e.g.,': {len(mark)} fields     HELD: {len(hold)} fields")
    for it, why in sorted(hold.items()): print(f"   hold  {it[:46]:46s} {why}")
    seen = {}
    for p in sorted(ROOT.glob("*/*_TAPP_v*.csv")):
        if any(x in p.parts for x in ("Archive", "Superseded TAPPs", "Current TAPPs")): continue
        m = re.fullmatch(r"(.+)_v(\d+)", p.stem)
        if not m: continue
        base, ver = m.group(1), int(m.group(2))
        if ver > seen.get(base, (-1, None))[0]: seen[base] = (ver, p)
    tot = 0
    for base, (ver, src) in sorted(seen.items()):
        rows = list(csv.reader(open(src, encoding="utf-8-sig")))
        hdr = rows[0]
        iA, iF, iU = hdr.index("Metadata Item"), hdr.index("Example / Allowed Content"), hdr.index("Last Update")
        n = 0
        for r in rows[1:]:
            if len(r) <= iU or r[iA] not in mark: continue
            ex = r[iF].strip()
            if not ex or ex.lower().startswith("e.g") or "|" not in ex: continue
            r[iF] = "e.g., " + ex; r[iU] = STAMP; n += 1
        if not n: continue
        print(f"  {base:24s} v{ver} -> v{ver+1}   {n} cell(s)")
        tot += n
        if not dry:
            dst = src.parent / f"{base}_v{ver+1}.csv"
            shutil.copyfile(src, dst)
            with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
    print(f"\n{'DRY RUN — ' if dry else ''}{tot} cells across {len(mark)} fields")
    return 0

sys.exit(main())
