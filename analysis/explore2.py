import csv, sys, statistics as st
from collections import Counter, defaultdict
rows=list(csv.DictReader(open(sys.argv[1])))
for r in rows:
    if r['BMI Category']=='Normal Weight': r['BMI Category']='Normal'
    s,d=map(int,r['Blood Pressure'].split('/')); r['sys']=s; r['dia']=d
def tab(key, rs=rows):
    g=defaultdict(Counter)
    for r in rs: g[key(r)][r['Sleep Disorder']]+=1
    for k in sorted(g): 
        n=sum(g[k].values()); print(f"  {str(k):28} n={n:3}", {d:f"{g[k][d]/n:.0%}" for d in ['None','Insomnia','Sleep Apnea']})
print('BMI'); tab(lambda r:r['BMI Category'])
print('Gender'); tab(lambda r:r['Gender'])
print('Age band'); tab(lambda r:int(r['Age'])//10*10)
print('Gender x age'); tab(lambda r:(r['Gender'],int(r['Age'])//10*10))
print('Hypertension (sys>=130)'); tab(lambda r:r['sys']>=140)
print('Female nurses vs other females 50+'); tab(lambda r:(r['Occupation']=='Nurse'), [r for r in rows if r['Gender']=='Female' and int(r['Age'])>=50])
print('BMI of nurses', Counter(r['BMI Category'] for r in rows if r['Occupation']=='Nurse'))
# dedup correlations
cols=[c for c in rows[0] if c not in('Person ID','sys','dia')]
seen={};
for r in rows: seen.setdefault(tuple(r[c] for c in cols), r)
u=list(seen.values())
def corr(a,b,rs): return st.correlation([float(r[a]) for r in rs],[float(r[b]) for r in rs])
for a,b in [('Stress Level','Quality of Sleep'),('Sleep Duration','Quality of Sleep'),('Physical Activity Level','Quality of Sleep'),('Daily Steps','Quality of Sleep'),('Physical Activity Level','Sleep Duration')]:
    print(a,b, f"all {corr(a,b,rows):.2f} unique {corr(a,b,u):.2f}")
# within-occupation stress-quality
for o in ['Nurse','Doctor','Engineer','Lawyer','Teacher','Accountant','Salesperson']:
    rs=[r for r in rows if r['Occupation']==o]
    try: print(o, f"stress~qual {corr('Stress Level','Quality of Sleep',rs):.2f}  act~qual {corr('Physical Activity Level','Quality of Sleep',rs):.2f}")
    except Exception as e: print(o,e)
# stress level -> mean quality & duration & n
print('stress table')
for s in range(3,9):
    rs=[r for r in rows if int(r['Stress Level'])==s]
    print(s,len(rs), round(st.mean(float(r['Quality of Sleep']) for r in rs),2), round(st.mean(float(r['Sleep Duration']) for r in rs),2), round(st.mean(float(r['Heart Rate']) for r in rs),1), round(st.mean(float(r['Physical Activity Level']) for r in rs),1))
print('activity bins')
for lo in range(30,100,15):
    rs=[r for r in rows if lo<=int(r['Physical Activity Level'])<lo+15]
    if rs: print(lo,len(rs), round(st.mean(float(r['Quality of Sleep']) for r in rs),2), round(st.mean(float(r['Sleep Duration']) for r in rs),2), Counter(r['Occupation'] for r in rs).most_common(3))
print('unique values: dur',sorted(set(float(r['Sleep Duration']) for r in rows)))
print('activity',sorted(set(int(r['Physical Activity Level']) for r in rows)))
print('steps',sorted(set(int(r['Daily Steps']) for r in rows)))
print('hr', sorted(set(int(r['Heart Rate']) for r in rows)))
print('bp', Counter(r['Blood Pressure'] for r in rows).most_common(30))
# 'good sleepers' q>=8 & dur>=7.5
g=[r for r in rows if int(r['Quality of Sleep'])>=8 and float(r['Sleep Duration'])>=7.5]; b=[r for r in rows if int(r['Quality of Sleep'])<=6]
for name,rs in [('good',g),('poor',b)]:
    print(name,len(rs),{c:round(st.mean(float(r[c]) for r in rs),1) for c in ['Stress Level','Physical Activity Level','Daily Steps','Heart Rate','Age']}, Counter(r['BMI Category'] for r in rs), Counter(r['Sleep Disorder'] for r in rs))
