#!/usr/bin/env python3
"""
Incorporate the three reviewed literature-assessment drafts into their TAPPs.

  Solution_Q-ICP-MS_TAPP_v23  -> v24   12 fields filled in the 5 existing literature columns
  Solution_SF-ICP-MS_TAPP_v24 -> v25   12 fields filled in the 6 existing literature columns
  Solution_MC-ICP-MS_TAPP_v22 -> v23   14 NEW literature columns, all 121 content fields

Drafts (kept on disk as the cited record):
  Solution Q-ICP-MS/Solution_Q-ICP-MS_lit_assessment_draft_newfields_2026-08-14.csv
  Solution SF-ICP-MS/Solution_SF-ICP-MS_lit_assessment_draft_newfields_2026-08-14.csv
  Solution MC-ICP-MS/Solution_MC-ICP-MS_lit_assessment_draft_2026-08-14.csv

Per lit_assessment.md, the bracketed source keys used for review ("[Ho sec 2.3]") are STRIPPED on
incorporation; the drafts retain them. The strip is restricted to the declared source keys so that
legitimate bracketed text survives — "[Ca]Matrix" in the SF draft is the case that forced this.
"""
import csv, os, re, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
APPLY = "--apply" in sys.argv

KEYS = r'Bu|Cr|Ho|Hu|IM|Ni|No|Pr|Sc|vK|Br|Ba|Lo|Lu|Li|Mi|Ms|H|Y|M|D|W'
CITE = re.compile(r'\s*\[(?:' + KEYS + r')\b[^\]]*\]')

def strip(v):
    return CITE.sub('', v).strip()

JOBS = [
 ("Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v23.csv",
  "Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v24.csv",
  "Solution Q-ICP-MS/Solution_Q-ICP-MS_lit_assessment_draft_newfields_2026-08-14.csv", "fill"),
 ("Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v24.csv",
  "Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v25.csv",
  "Solution SF-ICP-MS/Solution_SF-ICP-MS_lit_assessment_draft_newfields_2026-08-14.csv", "fill"),
 ("Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v22.csv",
  "Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v23.csv",
  "Solution MC-ICP-MS/Solution_MC-ICP-MS_lit_assessment_draft_2026-08-14.csv", "add"),
]

for src, dst, draft, mode in JOBS:
    rows = list(csv.reader(open(os.path.join(ROOT, src), encoding='utf-8-sig')))
    d = list(csv.reader(open(os.path.join(ROOT, draft), encoding='utf-8-sig')))
    dhdr, dmap = d[0][1:], {r[0]: r[1:] for r in d[1:] if r and r[0].strip()}
    hdr = rows[0]
    si = hdr.index('Literature Assessment')
    ncol_before = len(hdr)
    changed = 0

    if mode == "fill":
        lit = hdr[si + 1:]
        assert lit == dhdr, f"column headers differ:\n  TAPP  {lit}\n  draft {dhdr}"
        for r in rows[1:]:
            if not r or not r[0].strip() or r[0] not in dmap:
                continue
            vals = [strip(v) for v in dmap[r[0]]]
            if all(v == '' for v in vals):
                continue
            # only fill cells that are currently empty; never overwrite an existing extraction
            for k, v in enumerate(vals):
                if not (r[si + 1 + k] or '').strip() and v:
                    r[si + 1 + k] = v
                    changed += 1
    else:
        assert len(hdr) == si + 1, f"{src} already has literature columns"
        rows[0] = hdr + list(dhdr)
        for r in rows[1:]:
            if not r or not r[0].strip():
                rows[rows.index(r)] = r + [''] * len(dhdr) if False else r
                while len(r) < len(rows[0]):
                    r.append('')
                continue
            vals = dmap.get(r[0])
            if vals is None:                       # group header rows
                vals = ['N'] * len(dhdr)
            else:
                vals = [strip(v) for v in vals]
            r.extend(vals)
            changed += sum(1 for v in vals if v and v != 'N')

    assert all(len(r) == len(rows[0]) for r in rows), "ragged rows"
    print(f"{'WROTE' if APPLY else 'DRY '} {os.path.basename(dst):38} "
          f"cols {ncol_before}->{len(rows[0])}, {changed} literature cells written")
    if APPLY:
        with open(os.path.join(ROOT, dst), "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerows(rows)

if not APPLY:
    print("\ndry run — rerun with --apply")
