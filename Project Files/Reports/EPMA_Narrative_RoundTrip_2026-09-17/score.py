import csv, collections, os
HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.abspath(os.path.join(HERE,'..','..','..'))
rec=list(csv.DictReader(open(os.path.join(HERE,'reconstruction.csv'))))
rows=list(csv.reader(open(os.path.join(ROOT,'EPMA','EPMA_TAPP_v77.csv'),encoding='utf-8-sig')))
h=rows[0]; s=h.index('Literature Assessment'); m=h.index('Purpose')+1
truth=[]; sec=0
for r in rows[1:]:
    if not r[2].strip() and not r[3].strip():
        if r[0].strip(): sec+=1
        continue
    truth.append(dict(section=sec,name=r[0],C=r[2],D=r[3],I=r[8],modes=''.join(r[m:s])))
# alignment: v77 field order -> recon row indices (first index = primary row)
A=[[0],[1],[2],[3],[4],[5],[6],[7],[8],[9],[10],[11],[12],[13],[14],[15,16],[17],[18],
   [19],[20],[23],[21],[24],[25],[22],[26],
   [27],[28],[29],[30],[31],[32],[33],
   [34],[36],[35],[37],[38],[39,40],[41],[42],[43],[44],[45],[46],[47],[48],[49],[52,53],[50],[51],[54],[55],[56],[58],[57],[59],[60],[61],[62],[63],
   [64],[65],[66],[67],[68],[69],[70],[71],[72],[75],[76,77,78],[73,74],[79,80,81,82],[83],
   [84,85,86],[87,88,89],[90,91,92],[93],[94],[96,97],[95],[98,99,100],[101,102],[103],[104],[105,106],[107]]
assert len(A)==len(truth)==88
used=sorted(i for a in A for i in a); assert used==list(range(len(rec))), 'every recon row mapped exactly once'
res=collections.defaultdict(list); detail=[]
for t,a in zip(truth,A):
    p=rec[a[0]]
    got=dict(section=int(p['section']),C=p['procedure_tier'],D=p['analysis_tier'],I=p['keyed_by'],
             modes=p['eds_point']+p['eds_mapping']+p['wds_point']+p['wds_mapping'])
    ok={k:got[k]==t[k] for k in ['section','C','D','I','modes']}
    for k,v in ok.items(): res[k].append(v)
    res['all'].append(all(ok.values()))
    cells=sum(x==y for x,y in zip(got['modes'],t['modes']))
    res['modecells'].append(cells)
    if not all(ok.values()) or len(a)>1:
        detail.append((t['name'],len(a),{k:(got[k],t[k]) for k in ok if not ok[k]},[rec[i]['confidence'] for i in a]))
n=88
for k in ['section','C','D','I','modes','all']:
    print(f'{k:8} {sum(res[k])}/{n}  {100*sum(res[k])/n:.1f}%')
print('mode cells', sum(res['modecells']),'/',n*4)
conf=collections.Counter(r['confidence'] for r in rec); print('confidence',conf)
print('\nsplits / errors:')
for d in detail: print(' ',d)
# confidence vs correctness on primary rows
cc=collections.defaultdict(lambda:[0,0])
for t,a,ok in zip(truth,A,res['all']):
    c=rec[a[0]]['confidence']; cc[c][0]+=ok; cc[c][1]+=1
print('\nprimary-row confidence vs all-correct:',dict(cc))
