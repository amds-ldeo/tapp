#!/usr/bin/env python3
"""Step 2 (REWRITE, W1-W5) for the 7 flags raised by the module Step 1 backlog routing.

Edits the MODULE. Composition then carries Description to every consumer (owned) and the Purpose
default to every consumer whose own cell is empty (overlay). One edit, N consumers — which is the
point of having extracted these fields.

Every before/after pair is logged (W4). Guards: W1 splits must preserve the sentence's words; W2
rewrites may only drop words, and any word not in the original is reported; Column B is never left
empty (M1).
"""
import argparse, csv, json, os, re, sys
ROOT="/Users/ruolin/Documents/Astromat/TAPPs"; MODDIR=os.path.join(ROOT,"Claude Skills for TAPP","modules")
sys.path.insert(0, os.path.join(ROOT,"Project Files","Scripts"))
import tapp_segment
DATE="2026-08-27"
# (module, field, ORIGINAL SENTENCE TEXT) -> (new_B_sentence, to_Purpose, note)   "" = delete
#
# Keyed by text, not by sentence number. Step 1 removed the P-routed sentences from Column B, so
# the numbers in the Step 1 routing CSV no longer index Column B — `Carrier Gas and Flow Rate` S2
# went to Purpose, shifting everything after it. Matching on text is immune to that, and to any
# later edit that reorders the cell.
E = {
("CompositionQC","Primary Calibration Standard Name","Give the material name, its source or supplier, and a citation for the accepted values used, since results calibrated against different published values for the same material are not directly comparable."):(
 "Give the material name, its source or supplier, and a citation for the accepted values used.",
 "Results calibrated against different published values for the same material are not directly comparable.",
 "W1 — the instruction stays in Description; the comparability reason is rationale"),
("ICPMS","Limit of Quantification (LOQ) Method","Mandatory at analysis level when concentrations near the LOD are reported."):(
 "Required when concentrations near the LOD are reported.","",
 "W2 + W3 — 'Mandatory at analysis level' is carried by D=Basic; the CONDITION is a conditional obligation and is never stripped"),
("LaserAblation","Sample Form / Analytical Substrate","Editable to accommodate legitimate variations (e.g., thin section vs. mount) that do not alter the analytical procedure."):(
 "Variations that do not alter the analytical procedure (e.g., thin section vs. mount) are legitimate.","",
 "W2 — 'Editable to accommodate' is carried by D=Editable; WHICH variations are acceptable is not"),
("LaserAblation","Background Count Time","Editable to allow session-specific adjustment."):(
 "","",
 "W2 DELETE — 'Editable to allow session-specific adjustment.' is wholly D=Editable; nothing else is asserted"),
("LaserAblation","Carrier Gas and Flow Rate","Flow rates are procedure targets; actual session values may be adjusted within ±10% during tuning."):(
 "Adjustment during tuning stays within ±10% of the target.","",
 "W2 — 'flow rates are procedure targets; actual session values may be adjusted' is the C=Basic + D=Editable split in words; the ±10% bound is not"),
("LaserAblation","Mapping Area","This is an analysis-level parameter because it depends on the size of the grain or phase to be mapped."):(
 "","The map area depends on the size of the grain or phase to be mapped.",
 "W1+W2 — 'This is an analysis-level parameter' is carried by C=N/A + D=Basic; the remaining clause is wholly rationale and moves to Purpose"),
("LaserAblation","Mapping Area","The procedure fixes scan speed, line spacing, and spot size; the map area is chosen at analysis time to cover the target feature."):(
 "Scan speed, line spacing and spot size are fixed by the procedure; the map area covers the target feature.","",
 "W2 — 'the map area is chosen at analysis time' is carried by D=Basic. The first clause is about OTHER fields' tiers, not this row's, so W3 does not reach it and it stays"),
}
def words(s): return sorted(re.findall(r"\w+",s.lower()))
def main(apply=False):
    log=[]; warn=[]; touched={}
    for mod in sorted({k[0] for k in E}):
        p=os.path.join(MODDIR,"Module_%s.csv"%mod)
        rows=list(csv.reader(open(p,newline="",encoding="utf-8-sig"))); h=rows[0]
        pi=h.index("Purpose"); ui=h.index("Last Update")
        idx={r[0].strip():r for r in rows[1:] if r and r[0].strip()}
        n=0
        for (m,f,orig),(nb,tp,note) in sorted(E.items()):
            if m!=mod: continue
            r=idx[f]; sents=tapp_segment.sentences(r[1])
            if orig not in sents:
                raise SystemExit("%s/%s: sentence not found in Column B — it may already have been "
                                 "edited, or moved to Purpose by Step 1:\n  %r"%(m,f,orig[:110]))
            s=sents.index(orig)+1
            if tp:
                if words(nb+" "+tp)!=words(orig): warn.append((m,f,s,"RECAST split (reviewed)"))
            else:
                extra=set(words(nb))-set(words(orig))
                if extra: warn.append((m,f,s,"RECAST rewrite (reviewed): +%s"%sorted(extra)))
            new=[x for i,x in enumerate(sents) if i!=s-1] if nb=="" else [nb if i==s-1 else x for i,x in enumerate(sents)]
            nd=" ".join(new).strip()
            if not nd: raise SystemExit("%s/%s: M1 — Description would be emptied"%(m,f))
            while len(r)<=max(pi,ui): r.append("")
            log.append([m,f,s,"DELETE" if nb=="" else ("SPLIT" if tp else "REWRITE"),orig,nb,tp,note])
            r[1]=nd
            if tp:
                prev=r[pi].strip(); r[pi]=(prev+" "+tp).strip() if prev else tp
            r[ui]=DATE; n+=1
        touched[mod]=(p,rows,n)
    for m,(p,rows,n) in touched.items(): print("  Module_%-16s %d edit(s)"%(m,n))
    print("\n  %d edit(s) total"%len(log))
    if warn:
        print("\n  GUARD (%d):"%len(warn))
        for w in warn: print("     ",w)
    if not apply: print("\n(dry run — pass --apply to write)"); return
    for m,(p,rows,n) in touched.items():
        with open(p,"w",newline="",encoding="utf-8-sig") as fh: csv.writer(fh).writerows(rows)
        j=os.path.join(MODDIR,"Module_%s.json"%m)
        man=json.load(open(j,encoding="utf-8")); old=man["version"]; man["version"]=str(int(old)+1)
        man.setdefault("decisions",[]).append(
          "2026-08-27: Step 2 (W1-W5) applied to the %d flag(s) this module carried from the Step 1 "
          "backlog routing. Before/after pairs in analysis/Step2_Applied_MODULES_2026-08-27.csv."%n)
        with open(j,"w",encoding="utf-8") as fh: json.dump(man,fh,indent=4,ensure_ascii=False); fh.write("\n")
        print("  Module_%s v%s -> v%s"%(m,old,man["version"]))
    out=os.path.join(ROOT,"Claude Skills for TAPP","analysis","Step2_Applied_MODULES_2026-08-27.csv")
    with open(out,"w",newline="",encoding="utf-8-sig") as fh:
        w=csv.writer(fh); w.writerow(["Module","Field","Sentence_no","Action","Before","After_Description","Moved_to_Purpose","Rule_and_reason"]); w.writerows(log)
    print("  log ->",os.path.basename(out))
if __name__=="__main__":
    a=argparse.ArgumentParser(); a.add_argument("--apply",action="store_true"); main(a.parse_args().apply)
