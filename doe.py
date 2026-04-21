"""Design of Experiments: 2^k full factorial generator and analysis."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

import numpy as np
import pandas as pd
from PySide6.QtWidgets import QComboBox, QLineEdit, QPushButton, QSpinBox
from scipy import stats

from ui_common import ToolPanel, df_to_html, make_int_spin


@dataclass
class DOEResult:
    design: pd.DataFrame
    effects: pd.DataFrame
    anova: pd.DataFrame


def full_factorial(factor_names: list[str], levels: int = 2,
                   replicates: int = 1) -> pd.DataFrame:
    coded_levels = [-1, 1] if levels == 2 else list(range(-1, levels - 1))
    runs = list(product(coded_levels, repeat=len(factor_names)))
    rows = []
    for rep in range(1, replicates + 1):
        for run in runs:
            rows.append(list(run) + [rep])
    cols = factor_names + ["Replicate"]
    return pd.DataFrame(rows, columns=cols)


def analyze_factorial(design: pd.DataFrame, factor_names: list[str],
                      response: str) -> DOEResult:
    df = design.copy()
    if response not in df.columns:
        raise ValueError(f"Response column '{response}' not in design.")
    y = df[response].astype(float).values

    # Build the model matrix up to 2-factor interactions (screening focus).
    X_terms: dict[str, np.ndarray] = {}
    for f in factor_names:
        X_terms[f] = df[f].astype(float).values
    for i in range(len(factor_names)):
        for j in range(i + 1, len(factor_names)):
            a, b = factor_names[i], factor_names[j]
            X_terms[f"{a}:{b}"] = X_terms[a] * X_terms[b]

    mean_y = float(np.mean(y))
    effects = []
    ss_effects = {}
    n = len(y)
    for name, col in X_terms.items():
        # Effect = 2 * regression coefficient for coded -1/+1 factors
        effect = 2 * float(np.mean(col * y))
        effects.append((name, effect))
        # SS = N * effect^2 / 4 (balanced 2-level design)
        ss_effects[name] = n * effect * effect / 4

    ss_total = float(np.sum((y - mean_y) ** 2))
    ss_model = sum(ss_effects.values())
    ss_error = max(ss_total - ss_model, 0.0)
    df_model = len(X_terms)
    df_error = n - df_model - 1
    ms_error = ss_error / df_error if df_error > 0 else 0.0

    anova_rows = []
    for name, ss in ss_effects.items():
        f_stat = ss / ms_error if ms_error > 0 else float("inf")
        p = 1 - stats.f.cdf(f_stat, 1, df_error) if df_error > 0 and ms_error > 0 else float("nan")
        anova_rows.append((name, ss, 1, ss, f_stat, p))
    anova_rows.append(("Error", ss_error, df_error, ms_error, "", ""))
    anova_rows.append(("Total", ss_total, n - 1, "", "", ""))
    anova = pd.DataFrame(anova_rows, columns=["Source", "SS", "DF", "MS", "F", "p"])
    effects_df = pd.DataFrame(effects, columns=["Term", "Effect"])
    effects_df["|Effect|"] = effects_df["Effect"].abs()
    effects_df = effects_df.sort_values("|Effect|", ascending=False).reset_index(drop=True)
    return DOEResult(design=df, effects=effects_df, anova=anova)


class DOE(ToolPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(
            "Design of Experiments (2^k Factorial)",
            "Generate a full factorial design or analyze an existing DOE dataset.",
            parent,
        )
        self.data_handler = data_handler

        self.factors_edit = QLineEdit("Speed, Feed, Depth")
        self.reps_spin = make_int_spin(1, 1, 20)
        self.response_combo = QComboBox()
        self.add_control("Factors (comma-separated)", self.factors_edit)
        self.add_control("Replicates", self.reps_spin)
        self.add_control("Response column", self.response_combo)

        gen = QPushButton("Generate design")
        gen.clicked.connect(self._generate)
        self.add_control("", gen)
        refresh = QPushButton("Refresh columns")
        refresh.clicked.connect(self._refresh_cols)
        self.add_control("", refresh)

        self.set_run_handler(self._analyze)
        self._refresh_cols()

    def _refresh_cols(self) -> None:
        df = self.data_handler.dataframe()
        if df is None:
            return
        self.response_combo.clear()
        self.response_combo.addItems(df.columns.tolist())

    def _generate(self) -> None:
        factors = [s.strip() for s in self.factors_edit.text().split(",") if s.strip()]
        reps = self.reps_spin.value()
        design = full_factorial(factors, levels=2, replicates=reps)
        self.data_handler.set_dataframe(design)
        self._refresh_cols()
        self.results_text.setHtml(
            "<h3>Generated Design</h3>" + df_to_html(design)
            + "<p>Populate a Response column, then click Run Analysis.</p>"
        )

    def _analyze(self) -> None:
        df = self.data_handler.dataframe()
        if df is None:
            self.show_error("Generate or load a design first.")
            return
        factors = [s.strip() for s in self.factors_edit.text().split(",") if s.strip()]
        response = self.response_combo.currentText()
        try:
            result = analyze_factorial(df, factors, response)
        except Exception as exc:
            self.show_error(str(exc))
            return
        html = "<h3>Effects (sorted by magnitude)</h3>"
        html += df_to_html(result.effects.round(4))
        html += "<h3>ANOVA</h3>" + df_to_html(result.anova.round(4))
        self.results_text.setHtml(html)

        # Pareto of effects
        self.figure.clear()
        ax = self.figure.add_subplot(1, 1, 1)
        ax.barh(result.effects["Term"][::-1], result.effects["|Effect|"][::-1],
                color="#6d132a")
        ax.set_xlabel("|Effect|")
        ax.set_title("Pareto of Effects")
        self.figure.tight_layout()
        self.canvas.draw()
