"""Draw the four synthetic-vs-real comparison charts as PNGs in charts/.

Run from the repo root (after scripts/nhanes_comparison.py):
    python3 scripts/make_charts.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "nhanes_comparison.csv"
OUT = ROOT / "charts"

KAGGLE, NHANES = "#2a78d6", "#eb6834"  # blue = synthetic, orange = real, in every chart
SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
K_LABEL, N_LABEL = "Synthetic", "Real"

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.size": 12,
        "text.color": INK,
        "axes.labelcolor": MUTED,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "axes.edgecolor": GRID,
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
    }
)


def new_fig(title, size=(8, 4.8)):
    fig, ax = plt.subplots(figsize=size)
    fig.subplots_adjust(top=0.8, bottom=0.1, left=0.1, right=0.95)
    fig.text(0.5, 0.95, title, fontsize=16, fontweight="bold", va="top", ha="center")
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(length=0)
    return fig, ax


def save(fig, name):
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / name, dpi=200)
    plt.close(fig)
    print("wrote", OUT / name)


def lookup(df, section, metric_prefix):
    d = df[(df["section"] == section) & df["metric"].str.startswith(metric_prefix)]
    return d.set_index("group")[["kaggle", "nhanes"]]


def grouped_bars(ax, table, groups):
    width = 0.36
    for i, g in enumerate(groups):
        for offset, col, colour in ((-width / 2, "kaggle", KAGGLE), (width / 2, "nhanes", NHANES)):
            v = table.loc[g, col]
            ax.bar(i + offset, v, width - 0.03, color=colour,
                   label={"kaggle": K_LABEL, "nhanes": N_LABEL}[col] if i == 0 else None)
            ax.text(i + offset, v + 1.5, f"{v:.0f}%", ha="center", va="bottom", fontsize=12)
    ax.set_xticks(range(len(groups)), groups, fontsize=12, color=INK)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="upper left", ncols=2, bbox_to_anchor=(0, 1.14))


def chart_correlations(df):
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
    fig, ax = new_fig(
        "Correlations between measures",
    )
    fig.subplots_adjust(left=0.33)
    y = range(len(d))
    ax.axvline(0, color=MUTED, linewidth=1)
    ax.hlines(y, d["nhanes"], d["kaggle"], color=GRID, linewidth=3, zorder=1)
    ax.scatter(d["kaggle"], y, s=110, color=KAGGLE, label=K_LABEL, zorder=2)
    ax.scatter(d["nhanes"], y, s=110, color=NHANES, label=N_LABEL, zorder=2)
    ax.set_yticks(y, [names[g] for g in d.index], fontsize=12, color=INK)
    ax.set_xlim(-1, 1)
    ax.set_xticks([-1, -0.5, 0, 0.5, 1])
    ax.set_ylim(-0.6, len(d) - 0.4)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines["bottom"].set_visible(False)
    ax.legend(frameon=False, loc="upper left", ncols=2, bbox_to_anchor=(0, 1.12))
    save(fig, "1_correlations.png")


def chart_bmi_sleep_problem(df):
    t = lookup(df, "By BMI", "% with sleep disorder")
    fig, ax = new_fig(
        "Sleep problem rate by BMI category",
    )
    grouped_bars(ax, t, ["Normal", "Overweight"])
    save(fig, "2_sleep_problem_by_bmi.png")


def chart_bmi_mix(df):
    t = lookup(df, "BMI mix", "% of sample")
    fig, ax = new_fig(
        "BMI categories",
    )
    grouped_bars(ax, t, ["Normal", "Overweight", "Obese"])
    ax.set_ylim(0, 75)
    ax.set_yticks([0, 25, 50, 75], ["0%", "25%", "50%", "75%"])
    save(fig, "3_bmi_mix.png")


def chart_activity(df):
    t = lookup(df, "By activity", "% sleeping under 7 h")
    fig, ax = new_fig(
        "Short sleep by activity level",
    )
    fig.subplots_adjust(left=0.2, right=0.8)
    for col, colour, label in (("kaggle", KAGGLE, K_LABEL), ("nhanes", NHANES, N_LABEL)):
        lo, hi = t.loc["Less active", col], t.loc["More active", col]
        ax.plot([0, 1], [lo, hi], color=colour, linewidth=2.5, marker="o", markersize=9, label=label)
        ax.text(-0.05, lo, f"{lo:.0f}%", ha="right", va="center", fontsize=12)
        ax.text(1.05, hi, f"{hi:.0f}%", ha="left", va="center", fontsize=12)
    ax.set_xticks([0, 1], ["Less active", "More active"], fontsize=12, color=INK)
    ax.set_xlim(-0.25, 1.25)
    ax.set_ylim(0, 100)
    ax.set_yticks([])
    ax.legend(frameon=False, loc="upper left", ncols=2, bbox_to_anchor=(0, 1.14))
    save(fig, "4_activity_short_sleep.png")


def main():
    df = pd.read_csv(DATA)
    chart_correlations(df)
    chart_bmi_sleep_problem(df)
    chart_bmi_mix(df)
    chart_activity(df)


if __name__ == "__main__":
    main()
