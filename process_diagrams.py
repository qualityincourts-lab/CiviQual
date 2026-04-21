"""Lean process diagram rendering: SIPOC, RACI, swim lane, VSM, fishbone.

Each function draws onto a matplotlib Figure so it can be embedded in a Qt
canvas. The diagrams are schematic rather than production-grade graphics,
which is consistent with a practitioner-oriented analytics tool.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon

BURGUNDY = "#6d132a"
GOLD = "#dcad73"
GRAY = "#b2b2b2"
WHITE = "#ffffff"
DARK = "#1f1f1f"


def _cell(ax, x, y, w, h, text, facecolor=WHITE, edgecolor=BURGUNDY, weight="normal"):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.02",
                                facecolor=facecolor, edgecolor=edgecolor,
                                linewidth=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            color=DARK, wrap=True, fontsize=8.5, weight=weight)


def draw_sipoc(fig: Figure, suppliers, inputs, processes, outputs, customers,
               title: str = "SIPOC Diagram") -> None:
    fig.clear()
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xlim(0, 5)
    columns = [suppliers, inputs, processes, outputs, customers]
    headers = ["Suppliers", "Inputs", "Process", "Outputs", "Customers"]
    max_rows = max(len(c) for c in columns) if columns else 1
    ax.set_ylim(0, max_rows + 1.2)

    for i, (header, col) in enumerate(zip(headers, columns)):
        _cell(ax, i + 0.05, max_rows + 0.2, 0.9, 0.8, header,
              facecolor=BURGUNDY, weight="bold")
        for j, item in enumerate(col):
            _cell(ax, i + 0.05, max_rows - j - 0.8, 0.9, 0.8, str(item))
        # Text colour override for header cell
    # Re-draw headers with white text
    for i, header in enumerate(headers):
        ax.text(i + 0.5, max_rows + 0.6, header, ha="center", va="center",
                color=WHITE, fontsize=10, weight="bold")

    ax.set_title(title, color=DARK, fontsize=12, weight="bold")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect("auto")
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()


def draw_raci(fig: Figure, tasks: list[str], roles: list[str], matrix: list[list[str]],
              title: str = "RACI Matrix") -> None:
    """matrix[i][j] is one of 'R', 'A', 'C', 'I', or ''."""
    fig.clear()
    ax = fig.add_subplot(1, 1, 1)
    n_tasks = len(tasks)
    n_roles = len(roles)
    ax.set_xlim(0, n_roles + 2)
    ax.set_ylim(0, n_tasks + 1.2)

    # Header row
    _cell(ax, 0, n_tasks + 0.2, 2, 0.8, "Task", facecolor=BURGUNDY, weight="bold")
    ax.text(1, n_tasks + 0.6, "Task", ha="center", va="center",
            color=WHITE, weight="bold")
    for j, role in enumerate(roles):
        _cell(ax, 2 + j, n_tasks + 0.2, 1, 0.8, role, facecolor=BURGUNDY,
              weight="bold")
        ax.text(2.5 + j, n_tasks + 0.6, role, ha="center", va="center",
                color=WHITE, weight="bold")

    # Task rows
    for i, task in enumerate(tasks):
        y = n_tasks - i - 0.8
        _cell(ax, 0, y, 2, 0.8, task)
        for j in range(n_roles):
            assign = matrix[i][j] if i < len(matrix) and j < len(matrix[i]) else ""
            color = {
                "R": GOLD, "A": BURGUNDY, "C": GRAY, "I": "#e8e8e8"
            }.get(assign, WHITE)
            _cell(ax, 2 + j, y, 1, 0.8, assign, facecolor=color)

    ax.set_title(title, color=DARK, fontsize=12, weight="bold")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()


def draw_fishbone(fig: Figure, effect: str,
                  causes: dict[str, list[str]],
                  title: str = "Fishbone (Ishikawa) Diagram") -> None:
    fig.clear()
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)

    # Spine
    ax.plot([0.5, 8.5], [3, 3], color=DARK, linewidth=2)
    # Head
    ax.add_patch(FancyBboxPatch((8.5, 2.3), 1.3, 1.4,
                                boxstyle="round,pad=0.05",
                                facecolor=BURGUNDY, edgecolor=BURGUNDY))
    ax.text(9.15, 3, effect, ha="center", va="center",
            color=WHITE, weight="bold", fontsize=9)

    # Branches: alternate top/bottom
    cats = list(causes.keys())
    n = len(cats)
    slots = np.linspace(1, 7.5, max(n, 1))
    for i, cat in enumerate(cats):
        top = i % 2 == 0
        x_tip = slots[i]
        y_tip = 3
        if top:
            x_label = x_tip - 1.2
            y_label = 5.2
        else:
            x_label = x_tip - 1.2
            y_label = 0.8
        ax.plot([x_label + 1.2, x_tip], [y_label, y_tip], color=DARK, linewidth=1.4)
        ax.text(x_label, y_label, cat, color=DARK, weight="bold", fontsize=9)

        # Sub-causes as short twigs
        sub = causes[cat]
        for k, s in enumerate(sub):
            frac = (k + 1) / (len(sub) + 1)
            midx = x_label + 1.2 + (x_tip - (x_label + 1.2)) * frac
            midy = y_label + (y_tip - y_label) * frac
            direction = 0.6 if top else -0.6
            ax.plot([midx, midx - 0.7], [midy, midy + direction * 0.25],
                    color=GRAY, linewidth=0.8)
            ax.text(midx - 0.75, midy + direction * 0.3, s,
                    ha="right" if top else "right",
                    va="bottom" if top else "top",
                    fontsize=7.5, color=DARK)

    ax.set_title(title, color=DARK, fontsize=12, weight="bold")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()


def draw_process_map(fig: Figure, steps: list[str], title: str = "Process Map") -> None:
    fig.clear()
    ax = fig.add_subplot(1, 1, 1)
    n = len(steps)
    ax.set_xlim(0, max(n, 1) * 2 + 1)
    ax.set_ylim(0, 3)
    for i, step in enumerate(steps):
        _cell(ax, i * 2 + 0.2, 1, 1.6, 1, step, facecolor=GOLD)
        if i < n - 1:
            ax.annotate("", xy=(i * 2 + 2, 1.5), xytext=(i * 2 + 1.8, 1.5),
                        arrowprops=dict(arrowstyle="->", color=BURGUNDY, lw=1.5))
    ax.set_title(title, color=DARK, fontsize=12, weight="bold")
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()


def draw_swim_lane(fig: Figure, lanes: dict[str, list[str]],
                   title: str = "Swim Lane Diagram") -> None:
    fig.clear()
    ax = fig.add_subplot(1, 1, 1)
    lane_names = list(lanes.keys())
    n_lanes = len(lane_names)
    max_steps = max((len(v) for v in lanes.values()), default=1)
    ax.set_xlim(0, max_steps * 2 + 2)
    ax.set_ylim(0, n_lanes * 1.3 + 0.5)

    for i, lane in enumerate(lane_names):
        y = n_lanes * 1.3 - (i + 1) * 1.3
        ax.add_patch(Rectangle((1.8, y + 0.05), max_steps * 2 + 0.1, 1.2,
                               facecolor="#f7eee2", edgecolor=GOLD))
        ax.text(0.9, y + 0.65, lane, ha="center", va="center",
                color=DARK, weight="bold", fontsize=9)
        for j, step in enumerate(lanes[lane]):
            _cell(ax, 2 + j * 2, y + 0.3, 1.6, 0.7, step, facecolor=BURGUNDY)
            ax.text(2 + j * 2 + 0.8, y + 0.65, step, ha="center", va="center",
                    color=WHITE, fontsize=8, weight="bold")

    ax.set_title(title, color=DARK, fontsize=12, weight="bold")
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()


def draw_vsm(fig: Figure, steps: list[dict],
             title: str = "Value Stream Map") -> None:
    """Each step dict: {'name': str, 'cycle_time': float, 'wait_time': float}."""
    fig.clear()
    ax = fig.add_subplot(1, 1, 1)
    n = len(steps)
    ax.set_xlim(0, n * 2 + 1)
    ax.set_ylim(0, 5)
    for i, step in enumerate(steps):
        _cell(ax, i * 2 + 0.2, 2, 1.6, 1, step.get("name", f"Step {i+1}"),
              facecolor=GOLD)
        ax.text(i * 2 + 1, 1.5, f"C/T {step.get('cycle_time', 0):.1f}",
                ha="center", color=DARK, fontsize=8)
        if i < n - 1:
            ax.annotate("", xy=(i * 2 + 2, 2.5), xytext=(i * 2 + 1.8, 2.5),
                        arrowprops=dict(arrowstyle="->", color=BURGUNDY))
            ax.text(i * 2 + 1.9, 2.8,
                    f"W {step.get('wait_time', 0):.1f}",
                    ha="center", color=BURGUNDY, fontsize=7)

    total_ct = sum(s.get("cycle_time", 0) for s in steps)
    total_wait = sum(s.get("wait_time", 0) for s in steps)
    total = total_ct + total_wait
    pce = 100 * total_ct / total if total else 0.0
    ax.text(0.2, 0.5,
            f"Total Cycle: {total_ct:.1f}   Total Wait: {total_wait:.1f}   "
            f"PCE: {pce:.1f}%",
            color=DARK, fontsize=9, weight="bold")
    ax.set_title(title, color=DARK, fontsize=12, weight="bold")
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()
