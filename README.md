# Sleep on It

Project for the OH/IO high school hackathon, Challenge #1: the Sleep, Health & Lifestyle data analytics challenge.

**Open [`site/index.html`](site/index.html) in a browser.** It is one self-contained file with no network dependencies.

## The claim

**Sleep quality tracks stress, not exercise.** In this dataset, stress level accounts for 81% of the variation in how people rate their sleep (r = −0.90). Daily exercise accounts for 4% (r = +0.19).

The page checks the claim three ways:

1. **The gap.** Sleep quality plotted against stress falls along a line. Plotted against exercise it doesn't. People at stress 3 rate their sleep 9.0; at stress 8, 5.9. People active 90 minutes a day rate it 7.1, against 7.4 for people active 30.
2. **Inside every occupation.** Stress is negative in all six occupations we can measure (−0.75 to −0.98). Exercise flips sign: +0.96 for accountants, −0.54 for engineers.
3. **Without duplicates.** Only 132 of the 374 rows are distinct. On those, stress is −0.88 and exercise is +0.29.

And it says what the data does not show: that stress causes bad sleep, that exercise doesn't help, or anything about real workers. Stress and sleep quality are both self-ratings on the same scale, and the dataset looks generated (two thirds of rows are copies, IDs are sorted by age).

## Layout

| Path | What it is |
|---|---|
| `site/template.html` | Page source (HTML, CSS, plain JavaScript). The CSV is injected at `__CSV__`. |
| `site/build.mjs` | Inlines the dataset into the template and writes `site/index.html`. |
| `site/index.html` | Built page. |
| `analysis/check.py` | Standard-library Python script that prints every number quoted on the page. |
| `data/` | The Kaggle CSV (gitignored). |

## Reproduce

Download the [Sleep Health and Lifestyle Dataset](https://www.kaggle.com/datasets/uom190346a/sleep-health-and-lifestyle-dataset) and unzip it into `data/`, then:

```sh
python3 analysis/check.py data/Sleep_health_and_lifestyle_dataset.csv
node site/build.mjs        # rebuilds site/index.html after editing the template
```

Correlations are Pearson r. Distinct rows match on every column except Person ID.
