#!/usr/bin/env python3
"""Feature engineering for the Sleep Health and Lifestyle dataset.

Reads  data/Sleep_health_and_lifestyle_dataset.csv  (never modified)
Writes data/sleep_engineered.csv  (all original columns unchanged + new features)

Run from the repo root:  python3 scripts/engineer_features.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "Sleep_health_and_lifestyle_dataset.csv"
DST = ROOT / "data" / "sleep_engineered.csv"

SEED = 42
K = 5  # chosen from the silhouette comparison printed below (best of k=3..5, stable across seeds)
K_CANDIDATES = range(2, 8)
MIN_OCC_N = 5  # occupations smaller than this get NaN z-scores

NUMERIC = [
    "Age", "Sleep Duration", "Quality of Sleep", "Physical Activity Level",
    "Stress Level", "Heart Rate", "Daily Steps",
]
CLUSTER_FEATURES = NUMERIC + ["systolic", "diastolic", "bmi_ordinal"]


def bp_stage(sys_, dia):
    """ACC/AHA 2017 blood pressure categories."""
    if sys_ >= 140 or dia >= 90:
        return "Stage 2"
    if sys_ >= 130 or dia >= 80:
        return "Stage 1"
    if sys_ >= 120:
        return "Elevated"
    return "Normal"


def name_clusters(centroids):
    """Map cluster label -> human-readable name from centroids (original units).

    A rule cascade rather than a hard-coded label map, so names stay attached to
    the right cluster even if KMeans numbers the clusters differently.
    """
    remaining = centroids.copy()
    names = {}

    def take(label, name):
        names[label] = name
        remaining.drop(index=label, inplace=True)

    take(remaining["Physical Activity Level"].idxmax(), "High-Activity High-Stress")
    take(remaining["Sleep Duration"].idxmax(), "Low-Activity Deep Sleepers")
    take(remaining["systolic"].idxmax(), "Well-Rested Hypertensive")
    take(remaining["Sleep Duration"].idxmin(), "Stressed Short Sleepers")
    take(remaining.index[0], "Balanced Healthy")
    assert remaining.empty, "name_clusters assumes K == 5"
    return names


def main():
    # Read everything as strings so original columns are written back untouched
    # (and so the literal "None" in Sleep Disorder is not turned into NaN).
    raw = pd.read_csv(SRC, dtype=str, keep_default_na=False)
    orig_cols = list(raw.columns)
    df = raw.copy()

    num = raw[NUMERIC].apply(pd.to_numeric)

    # 1. Blood pressure
    bp = raw["Blood Pressure"].str.split("/", expand=True).astype(int)
    df["systolic"] = bp[0]
    df["diastolic"] = bp[1]
    df["pulse_pressure"] = df["systolic"] - df["diastolic"]
    df["mean_arterial_pressure"] = (df["diastolic"] + df["pulse_pressure"] / 3).round(2)
    df["bp_stage"] = [bp_stage(s, d) for s, d in zip(df["systolic"], df["diastolic"])]

    # 2. Rate pressure product
    df["rate_pressure_product"] = num["Heart Rate"] * df["systolic"]

    # 3. Steps per active minute (NaN if activity is 0)
    activity = num["Physical Activity Level"].where(num["Physical Activity Level"] > 0)
    df["steps_per_active_minute"] = (num["Daily Steps"] / activity).round(2)

    # 4. Sleep debt and sleeper type
    df["sleep_debt_hours"] = (7 - num["Sleep Duration"]).clip(lower=0).round(1)
    df["sleeper_type"] = np.select(
        [num["Sleep Duration"] < 7, num["Sleep Duration"] > 9], ["Short", "Long"], "Adequate"
    )

    # 5. Quality residual from OLS: quality ~ duration (fit on all 374 rows)
    slope, intercept = np.polyfit(num["Sleep Duration"], num["Quality of Sleep"], 1)
    df["quality_residual"] = (
        num["Quality of Sleep"] - (intercept + slope * num["Sleep Duration"])
    ).round(3)

    # 6. Within-occupation z-scores (sample std, ddof=1); NaN for tiny/constant groups
    occ = raw["Occupation"]
    occ_n = occ.map(occ.value_counts())
    for col, new in [
        ("Sleep Duration", "sleep_duration_z_occ"),
        ("Quality of Sleep", "quality_of_sleep_z_occ"),
        ("Stress Level", "stress_level_z_occ"),
    ]:
        g = num[col].groupby(occ)
        mean, std = g.transform("mean"), g.transform("std")
        ok = (occ_n >= MIN_OCC_N) & (std > 0)
        df[new] = ((num[col] - mean) / std.where(ok)).round(3)

    # 7. BMI
    df["bmi_clean"] = raw["BMI Category"].replace({"Normal Weight": "Normal"})
    df["bmi_ordinal"] = df["bmi_clean"].map({"Normal": 0, "Overweight": 1, "Obese": 2})
    assert df["bmi_ordinal"].notna().all(), "unexpected BMI category"
    df["bmi_ordinal"] = df["bmi_ordinal"].astype(int)

    # 8. Sleep disorder flag
    df["has_sleep_disorder"] = (raw["Sleep Disorder"] != "None").astype(int)

    # 9. Profiles: rows identical on every original column except Person ID
    profile_cols = [c for c in orig_cols if c != "Person ID"]
    df["profile_id"] = raw.groupby(profile_cols, sort=False).ngroup() + 1  # order of first appearance
    df["profile_count"] = df.groupby("profile_id")["profile_id"].transform("size")

    # 10. Archetypes: KMeans on the distinct profiles only
    feats = pd.concat([num, df[["systolic", "diastolic", "bmi_ordinal", "profile_id"]]], axis=1)
    profiles = feats.drop_duplicates("profile_id").set_index("profile_id")[CLUSTER_FEATURES]
    X = StandardScaler().fit_transform(profiles)

    print(f"Clustering {len(profiles)} distinct profiles on {len(CLUSTER_FEATURES)} standardized features")
    print("  k  silhouette  inertia  sizes")
    models = {}
    for k in K_CANDIDATES:
        km = KMeans(n_clusters=k, n_init=20, random_state=SEED).fit(X)
        models[k] = km
        sizes = sorted(np.bincount(km.labels_).tolist(), reverse=True)
        mark = "  <- chosen" if k == K else ""
        print(f"  {k}  {silhouette_score(X, km.labels_):.3f}       {km.inertia_:7.1f}  {sizes}{mark}")

    labels = pd.Series(models[K].labels_, index=profiles.index)
    centroids = profiles.groupby(labels).mean()
    names = name_clusters(centroids)
    df["archetype"] = df["profile_id"].map(labels.map(names))

    summary = centroids.round(2)
    summary.index = summary.index.map(names)
    summary.insert(0, "n_profiles", labels.map(names).value_counts())
    summary.insert(1, "n_rows", df["archetype"].value_counts())
    print("\nArchetype centroids (original units, mean over distinct profiles):")
    with pd.option_context("display.width", 250, "display.max_columns", 30):
        print(summary)

    df.to_csv(DST, index=False)
    print(f"\nWrote {DST.relative_to(ROOT)}: {len(df)} rows, {len(df.columns)} columns "
          f"({len(df.columns) - len(orig_cols)} new)")


if __name__ == "__main__":
    main()
