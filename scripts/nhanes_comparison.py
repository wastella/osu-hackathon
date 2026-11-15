"""Compare the synthetic Kaggle sleep dataset with real NHANES 2009-2012 survey data.

Run from the repo root:  python3 scripts/nhanes_comparison.py
Writes data/nhanes_comparison.csv (long format: section, group, metric, kaggle, nhanes, n).

NHANES sample used: ages 27-59 (the Kaggle age range) and currently working,
because everyone in the Kaggle data has an occupation.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
KAGGLE = ROOT / "data" / "sleep_engineered.csv"
NHANES = ROOT / "data" / "external" / "nhanes" / "NHANES.csv"
OUT = ROOT / "data" / "nhanes_comparison.csv"

AGE_BINS = [26, 39, 49, 59]
AGE_LABELS = ["27-39", "40-49", "50-59"]
BMI_ORDER = ["Normal", "Overweight", "Obese"]


SUBSET_OUT = ROOT / "data" / "kaggle_comparison_subset.csv"
# The Kaggle columns this comparison actually uses: the original ones first,
# then the only engineered features it relies on.
SUBSET_COLS = [
    "Person ID", "Gender", "Age", "Sleep Duration", "Physical Activity Level", "Heart Rate",
    "systolic", "diastolic", "bmi_clean", "bmi_ordinal", "has_sleep_disorder",
]


def load_kaggle() -> pd.DataFrame:
    k = pd.read_csv(KAGGLE, keep_default_na=False, na_values=[""])
    k[SUBSET_COLS].to_csv(SUBSET_OUT, index=False)
    return pd.DataFrame(
        {
            "gender": k["Gender"],
            "age": k["Age"],
            "age_band": pd.cut(k["Age"], AGE_BINS, labels=AGE_LABELS),
            "bmi_cat": k["bmi_clean"],
            "bmi_ord": k["bmi_ordinal"],
            "sleep_hours": k["Sleep Duration"],
            "short_sleep": (k["Sleep Duration"] < 7).astype(float),
            "heart_rate": k["Heart Rate"],
            "systolic": k["systolic"],
            "diastolic": k["diastolic"],
            # Kaggle: diagnosed insomnia or sleep apnea.
            "sleep_problem": k["has_sleep_disorder"].astype(float),
            # Kaggle: at or above the median minutes of daily activity.
            "active": (
                k["Physical Activity Level"] >= k["Physical Activity Level"].median()
            ).astype(float),
        }
    )


def load_nhanes() -> pd.DataFrame:
    n = pd.read_csv(NHANES)
    n = n[n["Age"].between(27, 59) & (n["Work"] == "Working")].copy()
    bmi_map = {
        "12.0_18.5": None,  # underweight: no Kaggle equivalent, excluded from BMI splits
        "18.5_to_24.9": "Normal",
        "25.0_to_29.9": "Overweight",
        "30.0_plus": "Obese",
    }
    bmi_cat = n["BMI_WHO"].map(bmi_map)
    # A diastolic reading of 0 is a measurement artefact, not a real value.
    dia = n["BPDiaAve"].where(n["BPDiaAve"] > 0)
    return pd.DataFrame(
        {
            "gender": n["Gender"].str.capitalize(),
            "age": n["Age"],
            "age_band": pd.cut(n["Age"], AGE_BINS, labels=AGE_LABELS),
            "bmi_cat": bmi_cat,
            "bmi_ord": bmi_cat.map({"Normal": 0, "Overweight": 1, "Obese": 2}),
            "sleep_hours": n["SleepHrsNight"],
            "short_sleep": (n["SleepHrsNight"] < 7).where(n["SleepHrsNight"].notna()).astype(float),
            "heart_rate": n["Pulse"],
            "systolic": n["BPSysAve"],
            "diastolic": dia,
            # NHANES: ever told a doctor you have trouble sleeping (not a diagnosis).
            "sleep_problem": n["SleepTrouble"].map({"Yes": 1.0, "No": 0.0}),
            "active": n["PhysActive"].map({"Yes": 1.0, "No": 0.0}),
        }
    )


METRICS = {
    "sleep_hours": "Mean sleep hours",
    "short_sleep": "% sleeping under 7 h",
    "sleep_problem": "% with sleep disorder (Kaggle) / sleep trouble (NHANES)",
    "heart_rate": "Mean heart rate",
    "systolic": "Mean systolic BP",
    "diastolic": "Mean diastolic BP",
}
PCT = {"short_sleep", "sleep_problem"}


def summarize(k, n, section, by=None, order=None, metrics=METRICS):
    rows = []
    groups = [("All", k, n)] if by is None else [
        (g, k[k[by] == g], n[n[by] == g]) for g in order
    ]
    for label, kg, ng in groups:
        for col, name in metrics.items():
            scale = 100 if col in PCT else 1
            rows.append(
                {
                    "section": section,
                    "group": label,
                    "metric": name,
                    "kaggle": round(kg[col].mean() * scale, 2) if len(kg) else None,
                    "nhanes": round(ng[col].mean() * scale, 2) if len(ng) else None,
                    "kaggle_n": int(kg[col].notna().sum()),
                    "nhanes_n": int(ng[col].notna().sum()),
                }
            )
    return rows


def share(k, n, section, col, order):
    rows = []
    for g in order:
        rows.append(
            {
                "section": section,
                "group": g,
                "metric": "% of sample",
                "kaggle": round((k[col] == g).sum() / k[col].notna().sum() * 100, 2),
                "nhanes": round((n[col] == g).sum() / n[col].notna().sum() * 100, 2),
                "kaggle_n": int((k[col] == g).sum()),
                "nhanes_n": int((n[col] == g).sum()),
            }
        )
    return rows


def correlations(k, n):
    pairs = [
        ("age", "sleep_hours"),
        ("age", "systolic"),
        ("bmi_ord", "sleep_hours"),
        ("bmi_ord", "systolic"),
        ("bmi_ord", "sleep_problem"),
        ("sleep_hours", "heart_rate"),
        ("sleep_hours", "sleep_problem"),
        ("sleep_hours", "systolic"),
        ("active", "sleep_hours"),
        ("heart_rate", "systolic"),
    ]
    rows = []
    for a, b in pairs:
        nn = n[[a, b]].dropna().astype(float)
        kk = k[[a, b]].dropna().astype(float)
        rows.append(
            {
                "section": "Correlation (Pearson r)",
                "group": f"{a} vs {b}",
                "metric": "r",
                "kaggle": round(kk[a].corr(kk[b]), 3),
                "nhanes": round(nn[a].corr(nn[b]), 3),
                "kaggle_n": len(kk),
                "nhanes_n": len(nn),
            }
        )
    return rows


def main():
    k, n = load_kaggle(), load_nhanes()
    rows = []
    rows += summarize(k, n, "Overall")
    rows += [
        {
            "section": "Overall",
            "group": "All",
            "metric": "Std dev of sleep hours",
            "kaggle": round(k["sleep_hours"].std(), 2),
            "nhanes": round(n["sleep_hours"].std(), 2),
            "kaggle_n": int(k["sleep_hours"].notna().sum()),
            "nhanes_n": int(n["sleep_hours"].notna().sum()),
        }
    ]
    rows += share(k, n, "BMI mix", "bmi_cat", BMI_ORDER)
    rows += summarize(k, n, "By BMI", "bmi_cat", BMI_ORDER)
    rows += summarize(k, n, "By gender", "gender", ["Female", "Male"])
    rows += summarize(k, n, "By age band", "age_band", AGE_LABELS)
    rows += summarize(
        k, n, "By activity", "active", [1.0, 0.0],
        metrics={"sleep_hours": METRICS["sleep_hours"], "short_sleep": METRICS["short_sleep"]},
    )
    rows += correlations(k, n)

    out = pd.DataFrame(rows)
    out["group"] = out["group"].replace({1.0: "More active", 0.0: "Less active"})
    out["diff"] = (out["kaggle"] - out["nhanes"]).round(2)
    out.to_csv(OUT, index=False)
    print(f"Kaggle rows: {len(k)}   NHANES rows (27-59, working): {len(n)}")
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
