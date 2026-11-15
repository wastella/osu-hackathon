# Sleep on It

Project for the OH/IO high school hackathon, Challenge #1: the Sleep, Health & Lifestyle data analytics challenge.

**Open [`site/index.html`](site/index.html) in a browser.** It is a single self-contained page: a scrolling "night sky" in which each of the 374 people in the dataset is a star, and the stars rearrange into a new chart for each chapter of the story.

## The story

1. **Stress is the loudest signal.** Stress level vs sleep quality: r = −0.90 (−0.81 vs hours). Going from stress 3 to stress 8, average quality drops from 9.0 to 5.9 and sleep drops by about 2 hours.
2. **Exercise barely registers overall.** Activity minutes vs sleep quality: r = +0.19. Daily steps: +0.02.
3. **Simpson's paradox.** Split by occupation, the slope comes back with opposite signs: doctors +0.85, engineers −0.54. The pooled flat line hides both.
4. **Occupations form constellations.** 84% of nurses have sleep apnea, 91% of salespeople and 68% of teachers have insomnia, 90% of engineers have no disorder.
5. **BMI sorts disorders even better.** 93% of normal-BMI people have no disorder, while 87% of overweight people have one. But occupation is confounded with gender, age and BMI: all 73 nurses are women, average age 52, and 90% are overweight.
6. **Too clean to be real.** Among women aged 50+, 89% of nurses have sleep apnea and 0% of other women do.
7. **374 rows, 132 people.** 242 rows (65%) are exact duplicates; one profile appears 13 times. Person IDs are sorted perfectly by age. The headline correlations still hold on the 132 unique profiles (stress vs quality −0.88), but the dataset looks generated, so the findings describe the dataset rather than real workers.

The page ends with a **sleep-twin finder** (pick a stress level, activity, steps, age and BMI to see the nearest profiles in the data) and a ledger of which claims the data supports and which it doesn't, such as "stress causes poor sleep."

## Layout

| Path | What it is |
|---|---|
| `site/template.html` | Page source (HTML, CSS, D3.js). The CSV is injected at `__CSV__`. |
| `site/build.mjs` | Inlines the dataset into the template and writes `site/index.html`. |
| `site/index.html` | Built, self-contained page. |
| `analysis/explore.py`, `analysis/explore2.py` | Standard-library Python scripts that reproduce every number in the story. |
| `data/` | The Kaggle CSV (gitignored). |

## Reproduce

Download the [Sleep Health and Lifestyle Dataset](https://www.kaggle.com/datasets/uom190346a/sleep-health-and-lifestyle-dataset) and unzip it into `data/`, then:

```sh
python3 analysis/explore.py data/Sleep_health_and_lifestyle_dataset.csv
python3 analysis/explore2.py data/Sleep_health_and_lifestyle_dataset.csv
node site/build.mjs        # rebuilds site/index.html after editing the template
```

Notes: "Normal Weight" is merged into "Normal" for BMI. Correlations are Pearson r on all 374 rows unless noted otherwise.
