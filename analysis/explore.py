import csv, sys, statistics as st
from collections import Counter, defaultdict
rows=list(csv.DictReader(open(sys.argv[1])))
print(len(rows))
cols=[c for c in rows[0] if c!='Person ID']
uniq=Counter(tuple(r[c] for c in cols) for r in rows)
print('unique profiles',len(uniq), 'max dup', uniq.most_common(3))
for c in ['Gender','Occupation','BMI Category','Sleep Disorder','Stress Level','Quality of Sleep']:
    print(c, Counter(r[c] for r in rows).most_common())
num=['Age','Sleep Duration','Quality of Sleep','Physical Activity Level','Stress Level','Heart Rate','Daily Steps']
def corr(a,b):
    x=[float(r[a]) for r in rows]; y=[float(r[b]) for r in rows]
    return st.correlation(x,y)
for i,a in enumerate(num):
    print(a.ljust(25),' '.join(f'{corr(a,b):6.2f}' for b in num))
occ=defaultdict(list)
for r in rows: occ[r['Occupation']].append(r)
for o,rs in sorted(occ.items(), key=lambda kv:-len(kv[1])):
    m=lambda c: st.mean(float(r[c]) for r in rs)
    d=Counter(r['Sleep Disorder'] for r in rs)
    g=Counter(r['Gender'] for r in rs)
    print(f"{o:22}{len(rs):4} dur{m('Sleep Duration'):5.2f} q{m('Quality of Sleep'):5.2f} str{m('Stress Level'):5.2f} act{m('Physical Activity Level'):6.1f} steps{m('Daily Steps'):7.0f} hr{m('Heart Rate'):5.1f} age{m('Age'):5.1f}", dict(d), dict(g))
# person id order vs vars
print('age by id quartile', [st.mean(float(r['Age']) for r in rows[i:i+94]) for i in range(0,374,94)])
