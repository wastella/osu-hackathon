"""Prints every number quoted on the page. Standard library only.

Usage: python3 analysis/check.py data/Sleep_health_and_lifestyle_dataset.csv
"""
import csv
import statistics as st
import sys
from collections import Counter

QUALITY, HOURS = "Quality of Sleep", "Sleep Duration"
STRESS, EXERCISE, STEPS = "Stress Level", "Physical Activity Level", "Daily Steps"

rows = list(csv.DictReader(open(sys.argv[1])))
profile = lambda r: tuple(v for k, v in r.items() if k != "Person ID")
copies = Counter(profile(r) for r in rows)
distinct = list({profile(r): r for r in rows}.values())


def r(x, y, rs=rows):
    """Pearson r, or None when one side has no variation."""
    xs, ys = [float(p[x]) for p in rs], [float(p[y]) for p in rs]
    return st.correlation(xs, ys) if len(set(xs)) > 1 and len(set(ys)) > 1 else None


def avg(col, rs):
    return st.mean(float(p[col]) for p in rs)


print("1. The gap")
for name, col in [("stress", STRESS), ("exercise", EXERCISE), ("steps", STEPS)]:
    print(f"  {name:9} vs sleep quality: r = {r(col, QUALITY):+.2f}, r^2 = {r(col, QUALITY) ** 2:.0%}")
for col, levels in [(STRESS, ("3", "8")), (EXERCISE, ("30", "90"))]:
    for level in levels:
        rs = [p for p in rows if p[col] == level]
        print(f"  {col} {level}: quality {avg(QUALITY, rs):.1f}, hours {avg(HOURS, rs):.1f} (n={len(rs)})")

print("2. Inside each occupation with at least 30 people (r with sleep quality)")
for occ, n in Counter(p["Occupation"] for p in rows).most_common():
    if n < 30:
        continue
    rs = [p for p in rows if p["Occupation"] == occ]
    s, e, h = r(STRESS, QUALITY, rs), r(EXERCISE, QUALITY, rs), r(STRESS, HOURS, rs)
    if s is None:
        print(f"  {occ:12} n={n:3}  no variation: {set((p[STRESS], p[EXERCISE], p[QUALITY]) for p in rs)}")
    else:
        print(f"  {occ:12} n={n:3}  stress {s:+.2f}  exercise {e:+.2f}  (stress vs hours {h:+.2f})")

print("3. Duplicates")
top, top_n = copies.most_common(1)[0]
print(f"  {len(rows)} rows, {len(distinct)} distinct, {len(rows) - len(distinct)} copies ({1 - len(distinct) / len(rows):.0%})")
print(f"  most repeated profile appears {top_n} times: {top[:3]}")
for name, col in [("stress", STRESS), ("exercise", EXERCISE), ("steps", STEPS)]:
    print(f"  {name:9} all rows {r(col, QUALITY):+.2f}, distinct rows {r(col, QUALITY, distinct):+.2f}")

print("What this does not show")
print(f"  stress vs hours of sleep, all rows: r = {r(STRESS, HOURS):+.2f}")
ages = [int(p["Age"]) for p in rows]
print(f"  person IDs sorted by age: {ages == sorted(ages)}")
older_women = [p for p in rows if p["Gender"] == "Female" and int(p["Age"]) >= 50]
for label, is_nurse in [("nurses", True), ("other women", False)]:
    rs = [p for p in older_women if (p["Occupation"] == "Nurse") == is_nurse]
    print(f"  women 50+, {label}: {sum(p['Sleep Disorder'] == 'Sleep Apnea' for p in rs)} of {len(rs)} have sleep apnea")
