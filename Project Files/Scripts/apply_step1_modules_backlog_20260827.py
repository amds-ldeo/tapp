#!/usr/bin/env python3
"""Step 1 (MOVE ONLY) for the 49 module rows never covered by the 2026-08-25 module routing.

Those 49 entered their modules AFTER that pass: Module_ICPMS's 26 merged descriptions (2026-08-26),
Module_LaserAblation's 11 (Internal Standard Approach 2026-08-26 + 10 transferred 2026-08-27), and
the two modules built on 2026-08-27, CompositionQC and CollisionCell.

Writes Description and Purpose in the MODULE. Composition then carries the Purpose default to every
consumer whose own cell is empty — which only became possible when that propagation was fixed
earlier today; before it, Purpose written here would have reached nobody.

Guards per row: routing covers every sentence, Column B keeps at least one sentence (M1), and
Description + Purpose reproduce the original's exact multiset of words.
"""
import argparse, csv, json, os, sys
ROOT="/Users/ruolin/Documents/Astromat/TAPPs"
sys.path.insert(0, os.path.join(ROOT,"Project Files","Scripts"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tapp_segment, mod_routes
MODDIR=os.path.join(ROOT,"Claude Skills for TAPP","modules"); DATE="2026-08-27"

def main(apply=False):
    items=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"mod_items.json")))
    by=( {(i["module"],i["field"]):i for i in items} )
    log=[]; touched={}; refused=[]
    for (mod,field),it in sorted(by.items()):
        routes=["D"]+[mod_routes.R[(it["n"],s)][0] for s in range(2,len(it["sents"])+1)]
        D=" ".join(s for s,r in zip(it["sents"],routes) if r=="D")
        P=" ".join(s for s,r in zip(it["sents"],routes) if r=="P")
        if not D: refused.append((mod,field,"M1: Description would be emptied")); continue
        if sorted((D+" "+P).split())!=sorted(it["text"].split()):
            refused.append((mod,field,"word multiset not preserved")); continue
        if not P: continue
        touched.setdefault(mod,[]).append((field,D,P))
        log.append([mod,field,it["text"],D,P])
    if refused:
        print("REFUSED:",refused); return
    for mod,rows in sorted(touched.items()):
        print("  Module_%-16s %d field(s) gain a Purpose"%(mod,len(rows)))
        for f,_,_ in rows: print("       %s"%f)
    print("\n  %d module row(s) split · %d module(s) to bump"%(len(log),len(touched)))
    if not apply: print("\n(dry run — pass --apply to write)"); return
    for mod,rows in touched.items():
        p=os.path.join(MODDIR,"Module_%s.csv"%mod)
        csvrows=list(csv.reader(open(p,newline="",encoding="utf-8-sig"))); h=csvrows[0]
        pi=h.index("Purpose"); ui=h.index("Last Update")
        idx={r[0].strip():r for r in csvrows[1:] if r and r[0].strip()}
        for f,D,P in rows:
            r=idx[f]
            while len(r)<=max(pi,ui): r.append("")
            r[1]=D
            prev=r[pi].strip()
            r[pi]=(prev+" "+P).strip() if prev else P
            r[ui]=DATE
        with open(p,"w",newline="",encoding="utf-8-sig") as fh: csv.writer(fh).writerows(csvrows)
        j=os.path.join(MODDIR,"Module_%s.json"%mod)
        man=json.load(open(j,encoding="utf-8")); old=man["version"]; man["version"]=str(int(old)+1)
        man.setdefault("decisions",[]).append(
          "2026-08-27: Step 1 of the Description/Purpose split applied to the %d field(s) of this "
          "module that post-dated the 2026-08-25 module routing. Move only — no text reworded or "
          "deleted. Routing recorded in analysis/Step1_Routing_MODULES_BACKLOG_2026-08-27.csv. The "
          "Purpose text reaches consumers because overlay-default propagation was fixed on "
          "2026-08-27; written before that fix it would have stayed in the module and reached "
          "nobody."%len(rows))
        with open(j,"w",encoding="utf-8") as fh: json.dump(man,fh,indent=4,ensure_ascii=False); fh.write("\n")
        print("  Module_%s v%s -> v%s"%(mod,old,man["version"]))
    out=os.path.join(ROOT,"Claude Skills for TAPP","analysis","Step1_Routing_MODULES_BACKLOG_2026-08-27.csv")
    rows=[["Module","Field","Sentence_no","STEP1_route","Rule","STEP2_flag","Reason","Sentence_TEXT_UNCHANGED"]]
    for (mod,field),it in sorted(by.items()):
        for s,txt in enumerate(it["sents"],1):
            rt,fl,rs=mod_routes.R.get((it["n"],s),("D","","M1 — defining sentence, never moves"))
            rule=("M1" if s==1 else "M2" if rt=="P" else
                  "M4+M5" if ("STRADDLE" in fl and "REDUNDANT" in fl) else
                  "M4" if "STRADDLE" in fl else "M5" if "REDUNDANT" in fl else "M3")
            rows.append([mod,field,s,rt,rule,fl,rs,txt])
    csv.writer(open(out,"w",newline="",encoding="utf-8-sig")).writerows(rows)
    print("  routing -> %s (%d rows)"%(os.path.basename(out),len(rows)-1))
if __name__=="__main__":
    a=argparse.ArgumentParser(); a.add_argument("--apply",action="store_true"); main(a.parse_args().apply)
