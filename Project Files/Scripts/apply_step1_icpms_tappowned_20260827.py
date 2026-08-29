#!/usr/bin/env python3
"""Step 1 (MOVE ONLY) for the 105 TAPP-owned Description cells in the 9 ICP-MS TAPPs.

Applies analysis/Step1_Routing_ICPMS_TAPPOWNED_2026-08-27.csv, reviewed and approved 2026-08-27.

Same method and same guards as the non-ICP-MS pass. No text is reworded, added or deleted (M6);
each Description is segmented and each sentence written back to Column B or Column J exactly as
routed. Routing is looked up by the cell's OWN segmented text, never by field name plus a recorded
variant label, so a cell whose wording drifted since review fails to match and is SKIPPED and
reported rather than split against a routing decided for different words.

Refuses to write any row unless the routing covers every sentence, Column B keeps at least one
sentence (M1), and Description + Purpose reproduce the original's exact multiset of words.
Module-owned rows are never touched.
"""
from __future__ import annotations
import argparse, csv, json, os, re, shutil, subprocess, sys
ROOT="/Users/ruolin/Documents/Astromat/TAPPs"
sys.path.insert(0, os.path.join(ROOT,"Project Files","Scripts"))
import tapp_segment
DATE="2026-08-27"
CSVP=os.path.join(ROOT,"Claude Skills for TAPP","analysis","Step1_Routing_ICPMS_TAPPOWNED_2026-08-27.csv")

def load_routing():
    per={}
    for r in csv.DictReader(open(CSVP,newline="",encoding="utf-8-sig")):
        per.setdefault((r["Field"],r["Variant_TAPPs"]),[]).append(
            (int(r["Sentence_no"]),r["STEP1_route"],r["Sentence_TEXT_UNCHANGED"]))
    out={}
    for (f,_v),rows in per.items():
        rows.sort()
        if [n for n,_,_ in rows]!=list(range(1,len(rows)+1)):
            raise SystemExit("non-contiguous sentence numbers for %r"%f)
        out[(f,tuple(t for _,_,t in rows))]=tuple(rt for _,rt,_ in rows)
    return out

def main(apply=False):
    routing=load_routing()
    reg=json.load(open(os.path.join(ROOT,"composed_tapps.json"),encoding="utf-8"))
    MODDIR=os.path.join(ROOT,"Claude Skills for TAPP","modules"); mc={}
    renames,misses,refused=[],[],[]
    tot_split=tot_seen=0
    for e in sorted(reg["composed"],key=lambda x:x["tapp"]):
        rel=e["tapp"]; base=os.path.basename(rel)
        if "ICP" not in base: continue
        own=set()
        for m in e["modules"]:
            n=m["name"]
            if n not in mc:
                rows=list(csv.reader(open(os.path.join(MODDIR,"Module_%s.csv"%n),newline="",encoding="utf-8-sig")))
                mc[n]={r[0].strip() for r in rows[1:] if r and r[0].strip()}
            own|=mc[n]
        rows=list(csv.reader(open(os.path.join(ROOT,rel),newline="",encoding="utf-8-sig")))
        h=rows[0]; ib,iu,ip=h.index("Description"),h.index("Last Update"),h.index("Purpose")
        nsplit=nseen=0
        for r in rows[1:]:
            if not r or not r[0].strip(): continue
            f=r[0].strip(); desc=(r[ib].strip() if len(r)>ib else "")
            if f in own or not desc: continue
            nseen+=1
            sents=tuple(tapp_segment.sentences(desc))
            routes=routing.get((f,sents))
            if routes is None: misses.append((base,f)); continue
            D=" ".join(s for s,rt in zip(sents,routes) if rt=="D")
            P=" ".join(s for s,rt in zip(sents,routes) if rt=="P")
            if not D: refused.append((base,f,"M1: Description would be emptied")); continue
            if sorted((D+" "+P).split())!=sorted(desc.split()):
                refused.append((base,f,"word multiset not preserved")); continue
            if not P: continue
            while len(r)<=max(iu,ip): r.append("")
            r[ib]=D
            prev=r[ip].strip()
            r[ip]=(prev+" "+P).strip() if prev else P
            r[iu]=DATE; nsplit+=1
        tot_split+=nsplit; tot_seen+=nseen
        print("  %-34s %3d TAPP-owned cell(s), %2d gained a Purpose"%(base.split("_TAPP")[0],nseen,nsplit))
        if nsplit:
            new=re.sub(r"_v(\d+)\.csv$",lambda m:"_v%d.csv"%(int(m.group(1))+1),rel)
            renames.append((e,rel,new,rows))
    print("\n  %d cell(s) seen · %d gained a Purpose · %d TAPP(s) to bump"%(tot_seen,tot_split,len(renames)))
    if misses: print("\n  NO ROUTING MATCH (%d):"%len(misses),misses[:10])
    if refused: print("\n  REFUSED BY GUARD (%d):"%len(refused),refused[:10])
    if misses or refused: print("\n  Nothing written."); return
    if not apply: print("\n(dry run — pass --apply to write)"); return
    for e,rel,new,rows in renames:
        with open(os.path.join(ROOT,new),"w",newline="",encoding="utf-8-sig") as fh: csv.writer(fh).writerows(rows)
        e["tapp"]=new
    reg["generated"]=DATE
    with open(os.path.join(ROOT,"composed_tapps.json"),"w",encoding="utf-8") as fh:
        json.dump(reg,fh,indent=2,ensure_ascii=False); fh.write("\n")
    pm={os.path.basename(o):os.path.basename(n) for _,o,n,_ in renames}
    cv=os.path.join(ROOT,"Project Files","Registers & Planning","TAPP_Composed_Variants.csv")
    if os.path.exists(cv):
        cr=list(csv.reader(open(cv,newline="",encoding="utf-8-sig")))
        for r in cr[1:]:
            for i,c in enumerate(r):
                for o,n in pm.items():
                    if o in c: r[i]=c.replace(o,n)
        with open(cv,"w",newline="",encoding="utf-8-sig") as fh: csv.writer(fh).writerows(cr)
    sup=os.path.join(ROOT,"Superseded TAPPs",DATE); os.makedirs(sup,exist_ok=True)
    gen=os.path.join(ROOT,"Claude Skills for TAPP","scripts","tapp_to_xlsx.py")
    for _,rel,new,_ in renames:
        old=os.path.join(ROOT,rel)
        if os.path.exists(old): shutil.move(old,os.path.join(sup,os.path.basename(old)))
        x=old[:-4]+".xlsx"
        if os.path.exists(x): shutil.move(x,os.path.join(sup,os.path.basename(x)))
        subprocess.run([sys.executable,gen,new],cwd=ROOT,capture_output=True,text=True)
    s=os.path.join(ROOT,"Project Files","Scripts","sync_current_tapps.py")
    p=subprocess.run([sys.executable,s,"--apply"],cwd=ROOT,capture_output=True,text=True)
    print("  mirror:",(p.stdout.strip().splitlines() or ["synced"])[-1][:80])
if __name__=="__main__":
    a=argparse.ArgumentParser(); a.add_argument("--apply",action="store_true")
    main(a.parse_args().apply)
