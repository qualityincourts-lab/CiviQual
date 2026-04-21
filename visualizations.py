"""Matplotlib chart rendering helpers for CiviQual Stats.

All functions take a matplotlib Figure or Axes and draw onto it. They do not
create standalone windows; the UI embeds the figures in FigureCanvasQTAgg.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from scipy import stats

# Brand palette from the Logo Guideline
BURGUNDY = "#6d132a"
GOLD = "#dcad73"
GRAY = "#b2b2b2"
DARK = "#1f1f1f"
SIGNAL = "#c0392b"


def configure_axes(ax, title: str = "", xlabel: str = "", ylabel: str = "") -> None:
    ax.set_title(title, color=DARK, fontsize=11, weight="bold")
    ax.set_xlabel(xlabel, color=DARK)
    ax.set_ylabel(ylabel, color=DARK)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(colors=DARK)
    ax.grid(True, linestyle=":", color=GRAY, alpha=0.6)


# ---------------------------------------------------------------------------
def draw_xmr(fig: Figure, result, label: str = "Value") -> None:
    fig.clear()
    ax1 = fig.add_subplot(2, 1, 1)
    ax2 = fig.add_subplot(2, 1, 2)

    idx = np.arange(1, len(result.values) + 1)
    ax1.plot(idx, result.values, marker="o", color=BURGUNDY, linewidth=1.2)
    ax1.axhline(result.x_center, color=GOLD, linewidth=1.2)
    ax1.axhline(result.x_ucl, color=SIGNAL, linewidth=1.0, linestyle="--")
    ax1.axhline(result.x_lcl, color=SIGNAL, linewidth=1.0, linestyle="--")
    for s in result.signals:
        ax1.plot(idx[s["index"]], result.values[s["index"]],
                 marker="o", color=SIGNAL, markersize=8, markerfacecolor="none")
    configure_axes(ax1, "Individuals (X) Chart", "Observation", label)

    mr_idx = np.arange(2, len(result.values) + 1)
    ax2.plot(mr_idx, result.moving_range[1:], marker="s", color=BURGUNDY, linewidth=1.2)
    ax2.axhline(result.mr_center, color=GOLD, linewidth=1.2)
    ax2.axhline(result.mr_ucl, color=SIGNAL, linewidth=1.0, linestyle="--")
    ax2.axhline(result.mr_lcl, color=SIGNAL, linewidth=1.0, linestyle="--")
    configure_axes(ax2, "Moving Range (mR) Chart", "Observation", "Moving Range")

    fig.tight_layout()


def draw_xbar_r(fig: Figure, result) -> None:
    fig.clear()
    ax1 = fig.add_subplot(2, 1, 1)
    ax2 = fig.add_subplot(2, 1, 2)
    idx = np.arange(1, len(result.subgroup_means) + 1)
    ax1.plot(idx, result.subgroup_means, marker="o", color=BURGUNDY)
    ax1.axhline(result.xbar_center, color=GOLD)
    ax1.axhline(result.xbar_ucl, color=SIGNAL, linestyle="--")
    ax1.axhline(result.xbar_lcl, color=SIGNAL, linestyle="--")
    configure_axes(ax1, "X-bar Chart", "Subgroup", "Subgroup Mean")

    ax2.plot(idx, result.subgroup_ranges, marker="s", color=BURGUNDY)
    ax2.axhline(result.r_center, color=GOLD)
    ax2.axhline(result.r_ucl, color=SIGNAL, linestyle="--")
    ax2.axhline(result.r_lcl, color=SIGNAL, linestyle="--")
    configure_axes(ax2, "R Chart", "Subgroup", "Range")
    fig.tight_layout()


def draw_histogram(fig: Figure, values, bins: int = 20,
                   lsl: Optional[float] = None, usl: Optional[float] = None,
                   title: str = "Histogram") -> None:
    fig.clear()
    ax = fig.add_subplot(1, 1, 1)
    arr = np.asarray(values, dtype=float)
    arr = arr[~np.isnan(arr)]
    ax.hist(arr, bins=bins, color=BURGUNDY, alpha=0.75, edgecolor="white")
    # Overlay normal density scaled to the histogram
    mu, sigma = float(np.mean(arr)), float(np.std(arr, ddof=1))
    if sigma > 0:
        x = np.linspace(arr.min(), arr.max(), 200)
        pdf = stats.norm.pdf(x, mu, sigma)
        pdf_scaled = pdf * arr.size * (arr.max() - arr.min()) / bins
        ax.plot(x, pdf_scaled, color=GOLD, linewidth=2)
    if lsl is not None:
        ax.axvline(lsl, color=SIGNAL, linestyle="--", label="LSL")
    if usl is not None:
        ax.axvline(usl, color=SIGNAL, linestyle="--", label="USL")
    if lsl is not None or usl is not None:
        ax.legend()
    configure_axes(ax, title, "Value", "Frequency")
    fig.tight_layout()


def draw_box(fig: Figure, values, title: str = "Box Plot") -> None:
    fig.clear()
    ax = fig.add_subplot(1, 1, 1)
    arr = np.asarray(values, dtype=float)
    arr = arr[~np.isnan(arr)]
    bp = ax.boxplot(arr, vert=True, patch_artist=True,
                    boxprops=dict(facecolor=GOLD, edgecolor=BURGUNDY),
                    medianprops=dict(color=BURGUNDY, linewidth=2),
                    whiskerprops=dict(color=BURGUNDY),
                    capprops=dict(color=BURGUNDY),
                    flierprops=dict(marker="o", markerfacecolor=SIGNAL,
                                    markeredgecolor=SIGNAL))
    configure_axes(ax, title, "", "Value")
    fig.tight_layout()
    return bp


def draw_probability_plot(fig: Figure, values, title: str = "Normal Probability Plot") -> None:
    fig.clear()
    ax = fig.add_subplot(1, 1, 1)
    arr = np.asarray(values, dtype=float)
    arr = arr[~np.isnan(arr)]
    (osm, osr), (slope, intercept, r) = stats.probplot(arr, dist="norm")
    ax.plot(osm, osr, "o", color=BURGUNDY)
    ax.plot(osm, slope * osm + intercept, color=GOLD, linewidth=1.5)
    ax.text(0.02, 0.95, f"r = {r:.4f}", transform=ax.transAxes,
            verticalalignment="top", color=DARK)
    configure_axes(ax, title, "Theoretical Quantile", "Ordered Values")
    fig.tight_layout()


def draw_pareto(fig: Figure, df: pd.DataFrame, title: str = "Pareto Chart") -> None:
    fig.clear()
    ax1 = fig.add_subplot(1, 1, 1)
    ax2 = ax1.twinx()
    ax1.bar(df["category"], df["count"], color=BURGUNDY)
    ax2.plot(df["category"], df["cumulative_percent"], marker="o", color=GOLD)
    ax2.axhline(80, color=SIGNAL, linestyle="--")
    ax1.set_xticklabels(df["category"], rotation=40, ha="right")
    configure_axes(ax1, title, "Category", "Count")
    ax2.set_ylabel("Cumulative %", color=DARK)
    ax2.set_ylim(0, 105)
    fig.tight_layout()


def draw_scatter(fig: Figure, x, y, xlabel: str = "X", ylabel: str = "Y",
                 title: str = "Scatter Plot", fit: bool = True) -> None:
    fig.clear()
    ax = fig.add_subplot(1, 1, 1)
    xa = np.asarray(x, dtype=float)
    ya = np.asarray(y, dtype=float)
    ax.scatter(xa, ya, color=BURGUNDY, alpha=0.75)
    if fit and xa.size > 1:
        slope, intercept = np.polyfit(xa, ya, 1)
        xs = np.linspace(xa.min(), xa.max(), 100)
        ax.plot(xs, slope * xs + intercept, color=GOLD, linewidth=1.5)
        ax.text(0.02, 0.95, f"y = {slope:.3f}x + {intercept:.3f}",
                transform=ax.transAxes, verticalalignment="top", color=DARK)
    configure_axes(ax, title, xlabel, ylabel)
    fig.tight_layout()


def draw_run_chart(fig: Figure, result, title: str = "Run Chart") -> None:
    fig.clear()
    ax = fig.add_subplot(1, 1, 1)
    idx = np.arange(1, len(result.values) + 1)
    ax.plot(idx, result.values, marker="o", color=BURGUNDY, linewidth=1.2)
    ax.axhline(result.median, color=GOLD, linewidth=1.2, label=f"Median = {result.median:.2f}")
    ax.legend()
    configure_axes(ax, title, "Observation", "Value")
    fig.tight_layout()


def draw_four_up(fig: Figure, values, capability_result=None,
                 title: str = "Watson 4-Up Analysis") -> None:
    """Four-panel analytical view: histogram, run, XmR, probability plot."""
    fig.clear()
    arr = np.asarray(values, dtype=float)
    arr = arr[~np.isnan(arr)]

    ax1 = fig.add_subplot(2, 2, 1)
    ax1.hist(arr, bins=20, color=BURGUNDY, alpha=0.8, edgecolor="white")
    configure_axes(ax1, "Histogram", "Value", "Frequency")

    ax2 = fig.add_subplot(2, 2, 2)
    idx = np.arange(1, arr.size + 1)
    med = float(np.median(arr))
    ax2.plot(idx, arr, marker="o", color=BURGUNDY)
    ax2.axhline(med, color=GOLD)
    configure_axes(ax2, "Run Chart", "Observation", "Value")

    ax3 = fig.add_subplot(2, 2, 3)
    mr = np.abs(np.diff(arr))
    mr_bar = float(np.mean(mr))
    sigma = mr_bar / 1.128
    x_bar = float(np.mean(arr))
    ucl = x_bar + 3 * sigma
    lcl = x_bar - 3 * sigma
    ax3.plot(idx, arr, marker="o", color=BURGUNDY)
    ax3.axhline(x_bar, color=GOLD)
    ax3.axhline(ucl, color=SIGNAL, linestyle="--")
    ax3.axhline(lcl, color=SIGNAL, linestyle="--")
    configure_axes(ax3, "Individuals (X) Chart", "Observation", "Value")

    ax4 = fig.add_subplot(2, 2, 4)
    (osm, osr), (slope, intercept, r) = stats.probplot(arr, dist="norm")
    ax4.plot(osm, osr, "o", color=BURGUNDY)
    ax4.plot(osm, slope * osm + intercept, color=GOLD, linewidth=1.5)
    configure_axes(ax4, "Normal Probability Plot", "Theoretical", "Ordered")

    fig.suptitle(title, color=DARK, fontsize=13, weight="bold")
    fig.tight_layout()


def draw_attribute_chart(fig: Figure, result, title: Optional[str] = None) -> None:
    fig.clear()
    ax = fig.add_subplot(1, 1, 1)
    idx = np.arange(1, len(result.values) + 1)
    ax.plot(idx, result.values, marker="o", color=BURGUNDY)
    ax.axhline(result.center, color=GOLD)
    # UCL / LCL may vary per point for p and u charts.
    ucl = np.asarray(result.ucl)
    lcl = np.asarray(result.lcl)
    if ucl.size == 1 or np.allclose(ucl, ucl[0]):
        ax.axhline(float(ucl.flat[0]), color=SIGNAL, linestyle="--")
    else:
        ax.step(idx, ucl, where="mid", color=SIGNAL, linestyle="--")
    if lcl.size == 1 or np.allclose(lcl, lcl[0]):
        ax.axhline(float(lcl.flat[0]), color=SIGNAL, linestyle="--")
    else:
        ax.step(idx, lcl, where="mid", color=SIGNAL, linestyle="--")
    configure_axes(ax,
                   title or f"{result.chart_type}-chart",
                   "Subgroup", "Proportion / Count")
    fig.tight_layout()
