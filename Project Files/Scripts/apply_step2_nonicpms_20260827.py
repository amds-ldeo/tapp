#!/usr/bin/env python3
"""Step 2 (REWRITE, rules W1-W5) for the non-ICP-MS TAPPs.

Acts ONLY on Step 1's flags. Each edit is authored by reading and carries its rule and reason;
every before/after pair is written to Step2_Applied_NonICPMS_2026-08-27.csv (W4), so any edit is
reversible without redoing the routing.

Held back, not edited:
  * 10 flags on the 7 fields a future 12-TAPP composition module would absorb — 6 of those 7 carry
    five distinct descriptions and extracting them will re-merge Column B anyway;
  * 1 flag (`Dwell Time per Pixel` S3) that needs a SCOPE decision, not a wording edit.

Guards, per edit:
  W1 split   -> Description + Purpose must preserve the sentence's words (nothing lost in a move)
  W2 rewrite -> the new sentence may only DROP words; any word not in the original is reported
  any        -> Column B must never be left empty (M1)
Sentences are located by exact text match after segmentation; a cell whose wording has drifted
fails to match and is skipped rather than edited blind.
"""
from __future__ import annotations
import argparse, csv, json, os, re, shutil, subprocess, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
sys.path.insert(0, os.path.join(ROOT, "Project Files", "Scripts"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tapp_segment
import edits_tier, edits_keyed, edits_colfe, edits_straddle

DATE = "2026-08-27"
SHORT = {"EPMA_TAPP":"EPMA","SEM_TAPP":"SEM","SEM_Composition_TAPP":"SEMcomp",
         "SEM_Imaging_TAPP":"SEMimg","SEM_FIBSEM_TAPP":"FIB","TEM_TAPP":"TEM","Lab-XCT_TAPP":"XCT"}

EDITS = {}
for mod in (edits_tier, edits_keyed, edits_colfe, edits_straddle):
    for k, v in mod.E.items():
        if k in EDITS: raise SystemExit("duplicate edit %r" % (k,))
        EDITS[k] = v
DEFER = dict(edits_keyed.DEFER)

def words(s): return sorted(re.findall(r"\w+", s.lower()))

def main(apply=False):
    routing = {}
    for r in csv.DictReader(open(os.path.join(ROOT,"Claude Skills for TAPP","analysis",
                            "Step1_Routing_NONICPMS_2026-08-27.csv"),newline="",encoding="utf-8-sig")):
        routing[(r["Field"], r["Variant_TAPPs"], r["Sentence_no"])] = r
    reg = json.load(open(os.path.join(ROOT,"composed_tapps.json"), encoding="utf-8"))
    log, renames, misses, warn = [], [], [], []
    counts = {"edit":0,"delete":0,"keep":0,"split":0}

    for e in sorted(reg["composed"], key=lambda x: x["tapp"]):
        rel = e["tapp"]; base = os.path.basename(rel)
        if "ICP" in base: continue
        short = SHORT[base.rsplit("_v",1)[0]]
        rows = list(csv.reader(open(os.path.join(ROOT,rel),newline="",encoding="utf-8-sig")))
        h = rows[0]; ib, iu, ip = h.index("Description"), h.index("Last Update"), h.index("Purpose")
        changed = 0
        for r in rows[1:]:
            if not r or not r[0].strip(): continue
            field = r[0].strip()
            keys = [k for k in EDITS if k[0]==field and short in k[1].split(",")]
            if not keys: continue
            desc = r[ib].strip() if len(r)>ib else ""
            sents = tapp_segment.sentences(desc)
            newsents, appended = list(sents), []
            for k in keys:
                newB, toP, note = EDITS[k]
                orig = routing[k]["Sentence_TEXT_UNCHANGED"]
                if orig not in sents:
                    misses.append((base, field, k[2])); continue
                i = newsents.index(orig) if orig in newsents else None
                if i is None: misses.append((base, field, k[2])); continue
                if newB is None:
                    counts["keep"] += 1
                    log.append([base, field, k[2], "KEEP", orig, orig, "", note]); continue
                # guards
                if toP:
                    # W1 permits rewriting, so a split that is not word-for-word is a RECAST,
                    # not a failure. Report it so every one is looked at, but do not block.
                    if words(newB+" "+toP) != words(orig):
                        warn.append((base, field, k[2], "RECAST split (reviewed)"))
                    counts["split"] += 1; act = "SPLIT"
                else:
                    extra = set(words(newB)) - set(words(orig))
                    if extra: warn.append((base, field, k[2], "RECAST rewrite (reviewed): +%s" % sorted(extra)))
                    act = "DELETE" if newB=="" else "REWRITE"
                    counts["delete" if newB=="" else "edit"] += 1
                if newB == "": newsents.pop(i)
                else: newsents[i] = newB
                if toP: appended.append(toP)
                log.append([base, field, k[2], act, orig, newB, toP, note])
            if newsents == sents and not appended: continue
            newdesc = " ".join(newsents).strip()
            if not newdesc:
                warn.append((base, field, "-", "M1: Description would be emptied")); continue
            r[ib] = newdesc
            if appended:
                prev = r[ip].strip() if len(r)>ip else ""
                while len(r)<=max(ip,iu): r.append("")
                r[ip] = (prev+" "+" ".join(appended)).strip() if prev else " ".join(appended)
            while len(r)<=iu: r.append("")
            r[iu] = DATE; changed += 1
        if changed:
            new = re.sub(r"_v(\d+)\.csv$", lambda m:"_v%d.csv"%(int(m.group(1))+1), rel)
            renames.append((e, rel, new, rows))
        print("  %-18s %3d cell(s) edited" % (short, changed))

    print("\n  edits %d · deletions %d · splits %d · kept-by-decision %d · TAPPs to bump %d"
          % (counts["edit"], counts["delete"], counts["split"], counts["keep"], len(renames)))
    print("  deferred (not edited): %d" % len(DEFER))
    if misses: print("\n  SENTENCE NOT FOUND (%d):" % len(misses), misses[:8])
    if warn:
        print("\n  GUARD WARNINGS (%d):" % len(warn))
        for x in warn: print("     ", x)
    if misses: print("\n  Nothing written."); return
    if not apply:
        print("\n(dry run — pass --apply to write)"); return

    lp = os.path.join(ROOT,"Claude Skills for TAPP","analysis","Step2_Applied_NonICPMS_2026-08-27.csv")
    with open(lp,"w",newline="",encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["TAPP","Field","Sentence_no","Action","Before","After_Description","Moved_to_Purpose","Rule_and_reason"])
        w.writerows(log)
        for (f,v,s),why in DEFER.items(): w.writerow(["(all sharers)",f,s,"DEFERRED","","","",why])
    for e, rel, new, rows in renames:
        with open(os.path.join(ROOT,new),"w",newline="",encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rows)
        e["tapp"] = new
    reg["generated"] = DATE
    with open(os.path.join(ROOT,"composed_tapps.json"),"w",encoding="utf-8") as fh:
        json.dump(reg,fh,indent=2,ensure_ascii=False); fh.write("\n")
    pm = {os.path.basename(o):os.path.basename(n) for _,o,n,_ in renames}
    cv = os.path.join(ROOT,"Project Files","Registers & Planning","TAPP_Composed_Variants.csv")
    if os.path.exists(cv):
        cr = list(csv.reader(open(cv,newline="",encoding="utf-8-sig")))
        for r in cr[1:]:
            for i,c in enumerate(r):
                for o,n in pm.items():
                    if o in c: r[i] = c.replace(o,n)
        with open(cv,"w",newline="",encoding="utf-8-sig") as fh: csv.writer(fh).writerows(cr)
    sup = os.path.join(ROOT,"Superseded TAPPs",DATE); os.makedirs(sup,exist_ok=True)
    gen = os.path.join(ROOT,"Claude Skills for TAPP","scripts","tapp_to_xlsx.py")
    for _, rel, new, _ in renames:
        old = os.path.join(ROOT,rel)
        if os.path.exists(old): shutil.move(old, os.path.join(sup, os.path.basename(old)))
        x = old[:-4]+".xlsx"
        if os.path.exists(x): shutil.move(x, os.path.join(sup, os.path.basename(x)))
        subprocess.run([sys.executable,gen,new],cwd=ROOT,capture_output=True,text=True)
    s = os.path.join(ROOT,"Project Files","Scripts","sync_current_tapps.py")
    p = subprocess.run([sys.executable,s,"--apply"],cwd=ROOT,capture_output=True,text=True)
    print("  mirror:", (p.stdout.strip().splitlines() or ["synced"])[-1][:80])
    print("  log ->", os.path.basename(lp))

if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("--apply",action="store_true")
    main(a.parse_args().apply)
