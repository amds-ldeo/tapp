#!/usr/bin/env python3
"""Step 1 (MOVE ONLY) for the 339 TAPP-owned Description cells in the 7 non-ICP-MS TAPPs.

Applies analysis/Step1_Routing_NONICPMS_2026-08-27.csv, reviewed and approved 2026-08-27.

No text is reworded, added or deleted (M6). Each Description is segmented, and each sentence is
written back to Column B or to Column J `Purpose` exactly as the routing CSV records.

Routing is looked up by the cell's OWN segmented text, not by field name plus a recorded variant
label. A cell whose wording has drifted since the CSV was reviewed will therefore fail to match and
be SKIPPED and reported, rather than silently split against a routing that was decided for
different words. (This is the guard the ICP-MS slice pass established.)

Refuses to write any row unless:
  * the routing covers every sentence of the cell;
  * Column B keeps at least one sentence (M1 — a Description is never emptied);
  * Description + Purpose reproduce the original's exact multiset of words.

Rows whose sentences all route to Description are left completely untouched — there is nothing to
move, so they are not rewritten and not restamped.
"""
from __future__ import annotations
import argparse, csv, json, os, re, shutil, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
if not os.path.exists(os.path.join(ROOT, "composed_tapps.json")):
    ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
sys.path.insert(0, os.path.join(ROOT, "Project Files", "Scripts"))
import tapp_segment

DATE = "2026-08-27"
CSVP = os.path.join(ROOT, "Claude Skills for TAPP", "analysis",
                    "Step1_Routing_NONICPMS_2026-08-27.csv")

def load_routing():
    """(field, tuple-of-sentences) -> tuple-of-routes, from the reviewed CSV."""
    per = {}
    for r in csv.DictReader(open(CSVP, newline="", encoding="utf-8-sig")):
        key = (r["Field"], r["Variant_TAPPs"])
        per.setdefault(key, []).append((int(r["Sentence_no"]), r["STEP1_route"],
                                        r["Sentence_TEXT_UNCHANGED"]))
    out = {}
    for (field, _variants), rows in per.items():
        rows.sort()
        if [n for n, _, _ in rows] != list(range(1, len(rows) + 1)):
            raise SystemExit("routing CSV: non-contiguous sentence numbers for %r" % field)
        out[(field, tuple(t for _, _, t in rows))] = tuple(rt for _, rt, _ in rows)
    return out

def module_owned(entry, modcache):
    own = set()
    for m in entry["modules"]:
        name = m["name"]
        if name not in modcache:
            p = os.path.join(ROOT, "Claude Skills for TAPP", "modules", "Module_%s.csv" % name)
            rows = list(csv.reader(open(p, newline="", encoding="utf-8-sig")))
            modcache[name] = {r[0].strip() for r in rows[1:] if r and r[0].strip()}
        own |= modcache[name]
    return own

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    routing = load_routing()
    reg = json.load(open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    modcache = {}
    renames, misses, refused = [], [], []
    tot_split = tot_seen = 0

    for e in sorted(reg["composed"], key=lambda x: x["tapp"]):
        rel = e["tapp"]
        base = os.path.basename(rel)
        if "ICP" in base:
            continue
        own = module_owned(e, modcache)
        rows = list(csv.reader(open(os.path.join(ROOT, rel), newline="", encoding="utf-8-sig")))
        h = rows[0]
        ib, iu, ip = h.index("Description"), h.index("Last Update"), h.index("Purpose")
        nsplit = nseen = 0
        for r in rows[1:]:
            if not r or not r[0].strip():
                continue
            field = r[0].strip()
            desc = (r[ib].strip() if len(r) > ib else "")
            if field in own or not desc:
                continue
            nseen += 1
            sents = tuple(tapp_segment.sentences(desc))
            routes = routing.get((field, sents))
            if routes is None:
                misses.append((base, field))
                continue
            D = " ".join(s for s, rt in zip(sents, routes) if rt == "D")
            P = " ".join(s for s, rt in zip(sents, routes) if rt == "P")
            if not D:
                refused.append((base, field, "M1: Description would be emptied")); continue
            if sorted((D + " " + P).split()) != sorted(desc.split()):
                refused.append((base, field, "word multiset not preserved")); continue
            if not P:
                continue                      # nothing moves; leave the row alone
            while len(r) <= max(iu, ip): r.append("")
            r[ib] = D
            prev = r[ip].strip()
            r[ip] = (prev + " " + P).strip() if prev else P
            r[iu] = DATE
            nsplit += 1
        tot_split += nsplit; tot_seen += nseen
        print("  %-34s %3d TAPP-owned cell(s), %3d gained a Purpose" % (base.split("_TAPP")[0], nseen, nsplit))
        if not nsplit:
            continue
        new = re.sub(r"_v(\d+)\.csv$", lambda m: "_v%d.csv" % (int(m.group(1)) + 1), rel)
        renames.append((e, rel, new, rows))

    print("\n  %d TAPP-owned cell(s) seen · %d gained a Purpose · %d TAPP(s) to bump"
          % (tot_seen, tot_split, len(renames)))
    if misses:
        print("\n  NO ROUTING MATCH — skipped (%d):" % len(misses))
        for m in misses[:12]: print("     ", m)
    if refused:
        print("\n  REFUSED BY GUARD (%d):" % len(refused))
        for m in refused[:12]: print("     ", m)
    if misses or refused:
        print("\n  Nothing written: resolve the above first.")
        return
    if not a.apply:
        print("\n(dry run — pass --apply to write)"); return

    for e, rel, new, rows in renames:
        with open(os.path.join(ROOT, new), "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rows)
        e["tapp"] = new
    reg["generated"] = DATE
    with open(os.path.join(ROOT, "composed_tapps.json"), "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")

    pm = {os.path.basename(o): os.path.basename(n) for _, o, n, _ in renames}
    cv = os.path.join(ROOT, "Project Files", "Registers & Planning", "TAPP_Composed_Variants.csv")
    if os.path.exists(cv):
        crows = list(csv.reader(open(cv, newline="", encoding="utf-8-sig")))
        for r in crows[1:]:
            for i, c in enumerate(r):
                for o, n in pm.items():
                    if o in c: r[i] = c.replace(o, n)
        with open(cv, "w", newline="", encoding="utf-8-sig") as fh: csv.writer(fh).writerows(crows)

    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    gen = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
    for _, rel, new, _ in renames:
        old = os.path.join(ROOT, rel)
        if os.path.exists(old): shutil.move(old, os.path.join(sup, os.path.basename(old)))
        x = old[:-4] + ".xlsx"
        if os.path.exists(x): shutil.move(x, os.path.join(sup, os.path.basename(x)))
        subprocess.run([sys.executable, gen, new], cwd=ROOT, capture_output=True, text=True)
    s = os.path.join(ROOT, "Project Files", "Scripts", "sync_current_tapps.py")
    p = subprocess.run([sys.executable, s, "--apply"], cwd=ROOT, capture_output=True, text=True)
    print("  mirror:", (p.stdout.strip().splitlines() or ["synced"])[-1][:80])

if __name__ == "__main__":
    main()
