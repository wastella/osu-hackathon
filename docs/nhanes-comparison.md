# How does the Sleep Health dataset compare with real people?

The Kaggle Sleep Health and Lifestyle dataset is synthetic. To see how realistic it is, we compared it with NHANES, a real health survey of Americans run by the CDC.

**Short answer:** the synthetic data gets the averages roughly right, but it greatly exaggerates how strongly sleep, weight, age and blood pressure are linked.

## What we compared

| | Kaggle | NHANES |
|---|---|---|
| Source | Synthetic | Real CDC survey, 2009–2012 |
| Rows used | 374 (132 distinct people) | 3,320 |
| Who | Ages 27–59, all employed | Ages 27–59, currently working |

We filtered NHANES to the same age range and to working adults so the two groups are as alike as possible.

## Where the synthetic data matches reality

| Measure | Kaggle | NHANES |
|---|---|---|
| Mean sleep hours | 7.13 | 6.79 |
| Sleeping under 7 hours | 41% | 38% |
| Mean heart rate | 70 | 72 |
| Share overweight | 40% | 37% |

## Where it does not

| Measure | Kaggle | NHANES |
|---|---|---|
| Share obese | 3% | 36% |
| Share with normal BMI | 58% | 27% |
| Mean blood pressure | 129/85 | 119/73 |
| Sleep problem rate, overweight | 87% | 20% |
| Sleep problem rate, normal BMI | 7% | 24% |
| Sleep problem rate, women | 56% | 28% |
| Sleep problem rate, men | 28% | 19% |
| Short sleep, ages 40–49 | 63% | 41% |
| Short sleep, less active people | 75% | 43% |
| Short sleep, more active people | 16% | 35% |

## Relationships are far too strong

Correlation runs from −1 to 1; values near 0 mean no link.

| Relationship | Kaggle | NHANES |
|---|---|---|
| BMI vs sleep problem | 0.79 | 0.02 |
| BMI vs systolic blood pressure | 0.74 | 0.20 |
| Age vs systolic blood pressure | 0.61 | 0.25 |
| Sleep hours vs heart rate | −0.52 | 0.01 |
| Age vs sleep hours | 0.35 | −0.04 |
| Activity vs sleep hours | 0.34 | 0.08 |

## Key takeaways

- **BMI is the biggest gap.** In the Kaggle data, being overweight almost guarantees a sleep disorder. In real data, BMI barely predicts reported sleep trouble.
- **Real people are noisier.** Every link is much weaker in NHANES, and real sleep hours vary more (standard deviation 1.18 vs 0.80).
- **Older people do not sleep more.** The Kaggle data has 50–59-year-olds sleeping the most (7.6 hours). NHANES shows no age trend.
- **The direction is usually right; the strength is not.** Where NHANES shows any link at all, it mostly points the same way as Kaggle, just far more weakly.

## Caveats

- **"Sleep problem" means different things.** Kaggle records a diagnosed insomnia or sleep apnea label. NHANES asks whether you have ever told a doctor you have trouble sleeping. This explains some of the gap in overall rates, but not why the Kaggle rate tracks BMI so closely.
- **"Active" means different things.** Kaggle: at or above the median daily activity minutes. NHANES: a yes/no answer about moderate or vigorous activity.
- **NHANES sleep is in whole hours**, so the under-7-hours share is only roughly comparable.
- **Only 10 Kaggle rows are obese**, so figures for that group are unreliable.
- **NHANES is from 2009–2012**, and we did not test how much the working-adults filter changes the results.
- **Correlation is not causation** in either dataset.

## Reproduce

```
python3 scripts/engineer_features.py
python3 scripts/nhanes_comparison.py
```

- Full results: `data/nhanes_comparison.csv`
- NHANES source: `data/external/nhanes/NHANES.csv`, from the [NHANES R package](https://github.com/ProjectMOSAIC/NHANES) (CDC/NCHS data, 2009–2012)
- Kaggle source: [Sleep Health and Lifestyle Dataset](https://www.kaggle.com/datasets/uom190346a/sleep-health-and-lifestyle-dataset)
