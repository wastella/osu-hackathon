# Synthetic vs. Real Sleep Data 

This dataset is boring. Analyzing it traditionally won't prove to be fruitful because there simply isn't much you can do with a dataset this remedial. The key insight here, then, is why the dataset is so remedial. The reason, and our main hypothesis, is because it is synthetic. Synthetic data can be very useful, but only if done right. We're going to argue that this is a **bad** synthetic dataset because it is not realistically distributed. That means every other team's insights about the data should be taken with huge skepticism, and you should artificially deflate their conclusions. To do this, we compared it with NHANES, a real health survey of Americans run by the CDC.

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

## Three lessons about synthetic data

**1. Rules without noise are not data.** In the Kaggle data, 87% of overweight people have a sleep disorder against 7% of normal-weight people (correlation 0.79). In NHANES the rates are 20% and 24% (correlation 0.02). The generator seems to have turned a textbook belief into a near-certain rule. Real health outcomes have many causes, so a good generator must keep the randomness: each variable should only partly predict the others.

**2. Get the population mix right first.** Only 3% of the Kaggle sample is obese, against 36% of real working adults. With that group missing, "Overweight" has to carry every bad outcome and stops meaning what it means in real life. If the basic proportions are wrong, every comparison between groups is wrong too.

**3. The right direction can hide the wrong size.** Exercise helps sleep in both datasets, but short sleep falls from 75% to 16% with activity in Kaggle and only from 43% to 35% in NHANES: a 59-point effect against an 8-point one. Because the result sounds sensible, nobody questions it. Effect sizes must be calibrated against real data, and believable results need checking as much as surprising ones.

## Data used

The Kaggle data behind this comparison is saved as `data/kaggle_comparison_subset.csv` (all 374 rows). It has six original columns and five derived ones:

- **Original:** `Person ID`, `Gender`, `Age`, `Sleep Duration`, `Physical Activity Level`, `Heart Rate`
- **`systolic`, `diastolic`:** the `Blood Pressure` text (e.g. `126/83`) split into two numbers
- **`bmi_clean`, `bmi_ordinal`:** BMI category with "Normal Weight" merged into "Normal", and the same as 0/1/2
- **`has_sleep_disorder`:** 1 if the person has insomnia or sleep apnea, otherwise 0

These are simple cleanups of the original columns, not new information.
