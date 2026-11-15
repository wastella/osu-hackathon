"""Draw the comparison figures in conference-slide style, as PNGs in charts/slides/.

Run from the repo root (after scripts/nhanes_comparison.py):
    python3 scripts/make_slide_figures.py

Style: white background, no titles (the slide title carries the takeaway), no
gridlines, lines and bars labelled directly, fonts of 18 pt or more, 300 dpi.
One accent colour marks the synthetic data; the real data is dark grey.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "nhanes_comparison.csv"
OUT = ROOT / "charts" / "slides"

SYN, REAL = "#2a78d6", "#4d4d4d"
INK = "#000000"
SIZE = (12, 5.2)
FS = 20

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans"],
        "font.size": FS,
        "text.color": INK,
        "axes.labelcolor": INK,
        "axes.edgecolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "axes.labelsize": FS,
        "xtick.labelsize": FS,
        "ytick.labelsize": FS,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, dpi=300)
    plt.close(fig)
    print("wrote", OUT / name)


def lookup(df, section, metric_prefix):
    d = df[(df["section"] == section) & df["metric"].str.startswith(metric_prefix)]
    return d.set_index("group")[["kaggle", "nhanes"]]


def grouped_bars(table, groups, ylabel, ymax, name):
    fig, ax = plt.subplots(figsize=SIZE)
    fig.subplots_adjust(left=0.1, right=0.98, top=0.95, bottom=0.12)
    width = 0.34
    for i, g in enumerate(groups):
        for offset, col, colour, label in (
            (-width / 2, "kaggle", SYN, "Synthetic"),
            (width / 2, "nhanes", REAL, "Real"),
        ):
            v = table.loc[g, col]
            ax.bar(i + offset, v, width - 0.03, color=colour)
            # The first group also names each series, so no legend is needed.
            text = f"{label}\n{v:.0f}%" if i == 0 else f"{v:.0f}%"
            ax.text(i + offset, v + ymax * 0.015, text, ha="center", va="bottom", fontsize=FS)
    ax.set_xticks(range(len(groups)), groups)
    ax.tick_params(axis="x", length=0)
    ax.set_ylim(0, ymax)
    ax.set_ylabel(ylabel)
    save(fig, name)


def fig_correlations(df):
    names = {
        "bmi_ord vs sleep_problem": "BMI and sleep problems",
        "bmi_ord vs systolic": "BMI and blood pressure",
        "age vs systolic": "Age and blood pressure",
        "sleep_hours vs heart_rate": "Sleep hours and heart rate",
        "age vs sleep_hours": "Age and sleep hours",
        "active vs sleep_hours": "Activity and sleep hours",
    }
    d = df[df["section"].str.startswith("Correlation")].set_index("group").loc[list(names)]
    d = d.assign(gap=(d["kaggle"] - d["nhanes"]).abs()).sort_values("gap")
    fig, ax = plt.subplots(figsize=SIZE)
    fig.subplots_adjust(left=0.33, right=0.97, top=0.9, bottom=0.17)
    y = list(range(len(d)))
    ax.axvline(0, color=INK, linewidth=1)
    ax.hlines(y, d["nhanes"], d["kaggle"], color="#bdbdbd", linewidth=3, zorder=1)
    ax.scatter(d["kaggle"], y, s=220, color=SYN, zorder=2)
    ax.scatter(d["nhanes"], y, s=220, color=REAL, zorder=2)
    top = d.iloc[-1]
    ax.text(top["kaggle"], y[-1] + 0.35, "Synthetic", ha="center", va="bottom", fontsize=FS)
    ax.text(top["nhanes"], y[-1] + 0.35, "Real", ha="center", va="bottom", fontsize=FS,
            bbox=dict(facecolor="white", edgecolor="none", pad=3))
    ax.set_yticks(y, [names[g] for g in d.index])
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(-1, 1)
    ax.set_xticks([-1, -0.5, 0, 0.5, 1], ["−1", "−0.5", "0", "0.5", "1"])
    ax.set_ylim(-0.6, len(d) - 0.1)
    ax.set_xlabel("Correlation (0 = no link, ±1 = perfect link)")
    save(fig, "correlations.png")


def fig_activity(df):
    t = lookup(df, "By activity", "% sleeping under 7 h")
    fig, ax = plt.subplots(figsize=SIZE)
    fig.subplots_adjust(left=0.1, right=0.98, top=0.95, bottom=0.12)
    for col, colour, label in (("kaggle", SYN, "Synthetic"), ("nhanes", REAL, "Real")):
        lo, hi = t.loc["Less active", col], t.loc["More active", col]
        ax.plot([0, 1], [lo, hi], color=colour, linewidth=4, marker="o", markersize=14)
        ax.text(-0.04, lo, f"{lo:.0f}%", ha="right", va="center", fontsize=FS)
        ax.text(1.04, hi, f"{hi:.0f}%  {label}", ha="left", va="center", fontsize=FS)
    ax.set_xticks([0, 1], ["Less active", "More active"])
    ax.tick_params(axis="x", length=0)
    ax.set_xlim(-0.45, 1.6)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Sleeping under 7 hours (%)")
    save(fig, "activity_short_sleep.png")


def fig_data_cliff():
    """When AI training is projected to use up public human-written text.

    Numbers are quoted from Villalobos et al. (2024), "Will we run out of data?
    Limits of LLM scaling based on human-generated data" (arXiv:2211.04325):
    80% confidence interval 2026-2032, with 2028 as the central case.
    """
    lo, hi, central = 2026, 2032, 2028
    fig, ax = plt.subplots(figsize=(12, 2.1))
    fig.subplots_adjust(left=0.03, right=0.97, top=0.98, bottom=0.42)
    ax.barh(0, hi - lo, left=lo, height=0.5, color="#bdbdbd")
    ax.scatter([central], [0], s=320, color=SYN, zorder=3)
    ax.text(central, 0.42, f"{central}", ha="center", va="bottom", fontsize=FS)
    ax.text(hi + 0.15, 0, "80% interval", ha="left", va="center", fontsize=FS)
    ax.set_xlim(2023.5, 2034.5)
    ax.set_ylim(-0.45, 1.0)
    ax.set_xticks(range(2024, 2035, 2))
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Year AI runs out of new human-written text")
    save(fig, "data_cliff.png")


def main():
    df = pd.read_csv(DATA)
    fig_correlations(df)
    grouped_bars(
        lookup(df, "By BMI", "% with sleep disorder"),
        ["Normal", "Overweight"],
        "People with a sleep problem (%)",
        100,
        "sleep_problem_by_bmi.png",
    )
    grouped_bars(
        lookup(df, "BMI mix", "% of sample"),
        ["Normal", "Overweight", "Obese"],
        "Share of sample (%)",
        75,
        "bmi_mix.png",
    )
    fig_activity(df)
    fig_data_cliff()


if __name__ == "__main__":
    main()
