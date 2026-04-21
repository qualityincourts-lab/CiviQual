"""Measurement Systems Analysis (Gage R&R).

Implements the AIAG ANOVA method for crossed Gage R&R. Input expected:
long-format dataframe with columns Part, Operator, Measurement.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from PySide6.QtWidgets import QComboBox, QFileDialog, QPushButton
from scipy import stats

from ui_common import ToolPanel, df_to_html


@dataclass
class MSAResult:
    variance_components: pd.DataFrame
    pct_study_variation: pd.DataFrame
    pct_contribution: pd.DataFrame
    ndc: float


def gage_rr_anova(df: pd.DataFrame, part_col: str, op_col: str, value_col: str,
                  total_tolerance: float | None = None) -> MSAResult:
    parts = df[part_col].astype(str).values
    ops = df[op_col].astype(str).values
    y = df[value_col].astype(float).values

    part_levels = np.unique(parts)
    op_levels = np.unique(ops)
    n_parts = len(part_levels)
    n_ops = len(op_levels)

    # Cell structure: replicates per (part, operator)
    reps_per_cell = []
    cell_means = np.zeros((n_parts, n_ops))
    for i, p in enumerate(part_levels):
        for j, o in enumerate(op_levels):
            vals = y[(parts == p) & (ops == o)]
            cell_means[i, j] = np.mean(vals)
            reps_per_cell.append(len(vals))
    r = int(min(reps_per_cell))
    if r < 2:
        raise ValueError("Gage R&R ANOVA method requires at least 2 replicates per cell.")

    part_means = np.mean(cell_means, axis=1)
    op_means = np.mean(cell_means, axis=0)
    grand_mean = np.mean(cell_means)

    ss_parts = n_ops * r * np.sum((part_means - grand_mean) ** 2)
    ss_ops = n_parts * r * np.sum((op_means - grand_mean) ** 2)

    ss_total = np.sum((y - grand_mean) ** 2)

    # Interaction SS (between cells minus main effects)
    ss_cells = r * np.sum((cell_means - grand_mean) ** 2)
    ss_interaction = ss_cells - ss_parts - ss_ops
    ss_equip = ss_total - ss_cells  # within-cell repeatability

    df_parts = n_parts - 1
    df_ops = n_ops - 1
    df_int = df_parts * df_ops
    df_equip = n_parts * n_ops * (r - 1)

    ms_parts = ss_parts / df_parts
    ms_ops = ss_ops / df_ops if df_ops > 0 else 0.0
    ms_int = ss_interaction / df_int if df_int > 0 else 0.0
    ms_equip = ss_equip / df_equip if df_equip > 0 else 0.0

    # Variance components (AIAG ANOVA method; pool interaction if p > 0.25)
    if ms_int > 0:
        f_int = ms_int / ms_equip if ms_equip > 0 else float("inf")
        p_int = 1 - stats.f.cdf(f_int, df_int, df_equip) if ms_equip > 0 else 0.0
    else:
        p_int = 1.0
    pooled = p_int > 0.25

    if pooled:
        ms_repeat = (ss_interaction + ss_equip) / (df_int + df_equip)
        var_repeat = ms_repeat
        var_int = 0.0
        var_op = max((ms_ops - ms_repeat) / (n_parts * r), 0) if n_parts * r > 0 else 0
        var_part = max((ms_parts - ms_repeat) / (n_ops * r), 0) if n_ops * r > 0 else 0
    else:
        var_repeat = ms_equip
        var_int = max((ms_int - ms_equip) / r, 0) if r > 0 else 0
        var_op = max((ms_ops - ms_int) / (n_parts * r), 0) if n_parts * r > 0 else 0
        var_part = max((ms_parts - ms_int) / (n_ops * r), 0) if n_ops * r > 0 else 0

    var_reprod = var_op + var_int
    var_grr = var_repeat + var_reprod
    var_total = var_grr + var_part

    rows = [
        ("Repeatability (EV)", var_repeat),
        ("Reproducibility (AV)", var_reprod),
        ("Part-to-Part (PV)", var_part),
        ("Total Gage R&R", var_grr),
        ("Total Variation (TV)", var_total),
    ]
    vc = pd.DataFrame(rows, columns=["Source", "Variance"])
    vc["StdDev"] = np.sqrt(vc["Variance"])
    vc["Study Var (5.15 * SD)"] = 5.15 * vc["StdDev"]

    sv_total = np.sqrt(var_total)
    vc["% Study Variation"] = 100 * vc["StdDev"] / sv_total if sv_total > 0 else 0.0
    vc["% Contribution"] = 100 * vc["Variance"] / var_total if var_total > 0 else 0.0
    if total_tolerance is not None and total_tolerance > 0:
        vc["% Tolerance"] = 100 * (5.15 * vc["StdDev"]) / total_tolerance
    ndc = 1.41 * np.sqrt(var_part) / np.sqrt(var_grr) if var_grr > 0 else float("inf")

    return MSAResult(
        variance_components=vc,
        pct_study_variation=vc[["Source", "% Study Variation"]],
        pct_contribution=vc[["Source", "% Contribution"]],
        ndc=float(ndc),
    )


class MSA(ToolPanel):
    """Pro: Measurement Systems Analysis UI."""

    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(
            "Measurement Systems Analysis (Gage R&R)",
            "Crossed ANOVA method. Requires Part, Operator, and Measurement columns.",
            parent,
        )
        self.data_handler = data_handler

        self.part_combo = QComboBox()
        self.op_combo = QComboBox()
        self.val_combo = QComboBox()
        self.add_control("Part column", self.part_combo)
        self.add_control("Operator column", self.op_combo)
        self.add_control("Measurement column", self.val_combo)

        refresh = QPushButton("Refresh columns")
        refresh.clicked.connect(self._populate_columns)
        self.add_control("", refresh)
        self._populate_columns()
        self.set_run_handler(self._run)

    def _populate_columns(self) -> None:
        df = self.data_handler.dataframe()
        if df is None:
            return
        cols = df.columns.tolist()
        for cb in (self.part_combo, self.op_combo, self.val_combo):
            cb.clear()
            cb.addItems(cols)

    def _run(self) -> None:
        df = self.data_handler.dataframe()
        if df is None:
            self.show_error("Load a dataset first.")
            return
        try:
            result = gage_rr_anova(df, self.part_combo.currentText(),
                                   self.op_combo.currentText(),
                                   self.val_combo.currentText())
        except Exception as exc:
            self.show_error(str(exc))
            return
        html = "<h3>Variance Components</h3>"
        html += df_to_html(result.variance_components.round(4))
        html += f"<p><b>Number of Distinct Categories (ndc):</b> {result.ndc:.2f}</p>"
        self.results_text.setHtml(html)

        self.figure.clear()
        ax = self.figure.add_subplot(1, 1, 1)
        bars = result.variance_components["Source"].iloc[:4]
        vals = result.variance_components["% Contribution"].iloc[:4]
        ax.bar(bars, vals, color="#6d132a")
        ax.set_ylabel("% Contribution")
        ax.set_title("Variance Component Contribution")
        ax.tick_params(axis="x", rotation=30)
        self.figure.tight_layout()
        self.canvas.draw()
