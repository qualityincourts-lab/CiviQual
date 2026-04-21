"""Hypothesis testing widget: one and two sample t-tests, z-tests,
F-test of variances, chi-square independence, and two-proportion z-test.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from PySide6.QtWidgets import QComboBox, QPushButton
from scipy import stats

from ui_common import ToolPanel, df_to_html, make_double_spin


TESTS = [
    "One-sample t-test",
    "Two-sample t-test (Welch)",
    "Paired t-test",
    "One-sample z-test",
    "F-test (equality of variances)",
    "Chi-square independence",
    "Two-proportion z-test",
]


class HypothesisTests(ToolPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(
            "Hypothesis Tests",
            "Classical parametric tests. Choose a test and supply the required inputs.",
            parent,
        )
        self.data_handler = data_handler
        self.test_combo = QComboBox()
        self.test_combo.addItems(TESTS)
        self.col_a = QComboBox()
        self.col_b = QComboBox()
        self.mu0 = make_double_spin(0.0)
        self.alpha = make_double_spin(0.05, 0.001, 0.5, 0.01, 3)

        self.add_control("Test", self.test_combo)
        self.add_control("Column A / X", self.col_a)
        self.add_control("Column B / Y (if needed)", self.col_b)
        self.add_control("Mu0 (if one-sample)", self.mu0)
        self.add_control("Alpha", self.alpha)

        refresh = QPushButton("Refresh columns")
        refresh.clicked.connect(self._refresh)
        self.add_control("", refresh)

        self.set_run_handler(self._run)
        self._refresh()

    def _refresh(self) -> None:
        df = self.data_handler.dataframe()
        if df is None:
            return
        cols = df.columns.tolist()
        for c in (self.col_a, self.col_b):
            c.clear()
            c.addItem("")
            c.addItems(cols)

    def _run(self) -> None:
        df = self.data_handler.dataframe()
        if df is None:
            self.show_error("Load a dataset first.")
            return
        test = self.test_combo.currentText()
        a = self.col_a.currentText()
        b = self.col_b.currentText()
        alpha = self.alpha.value()

        try:
            result = self._dispatch(df, test, a, b, self.mu0.value(), alpha)
        except Exception as exc:
            self.show_error(str(exc))
            return

        stat, p, detail = result
        verdict = "REJECT H0" if p < alpha else "FAIL TO REJECT H0"
        html = f"<h3>{test}</h3>"
        html += f"<p><b>Statistic:</b> {stat:.4f} &middot; <b>p-value:</b> {p:.4g} &middot; "
        html += f"<b>Decision at α={alpha}:</b> {verdict}</p>"
        html += f"<p>{detail}</p>"
        self.results_text.setHtml(html)

        self.figure.clear()
        ax = self.figure.add_subplot(1, 1, 1)
        if a:
            arr = df[a].dropna().astype(float).values
            ax.hist(arr, bins=20, color="#6d132a", alpha=0.8, edgecolor="white")
            ax.axvline(arr.mean(), color="#dcad73", linewidth=2, label="Mean")
            ax.set_title(f"Distribution of {a}")
            ax.legend()
        self.figure.tight_layout()
        self.canvas.draw()

    def _dispatch(self, df, test, a, b, mu0, alpha):
        x = df[a].dropna().astype(float).values if a else None
        y = df[b].dropna().astype(float).values if b else None

        if test == "One-sample t-test":
            stat, p = stats.ttest_1samp(x, popmean=mu0)
            return float(stat), float(p), f"H0: mean = {mu0}"
        if test == "Two-sample t-test (Welch)":
            stat, p = stats.ttest_ind(x, y, equal_var=False)
            return float(stat), float(p), "H0: mean(A) = mean(B), Welch's correction"
        if test == "Paired t-test":
            if len(x) != len(y):
                raise ValueError("Paired t-test requires equal-length samples.")
            stat, p = stats.ttest_rel(x, y)
            return float(stat), float(p), "H0: mean(A-B) = 0"
        if test == "One-sample z-test":
            mean = x.mean(); sd = x.std(ddof=1); n = x.size
            stat = (mean - mu0) / (sd / np.sqrt(n))
            p = 2 * (1 - stats.norm.cdf(abs(stat)))
            return float(stat), float(p), f"H0: mean = {mu0}, sigma estimated"
        if test == "F-test (equality of variances)":
            f = x.var(ddof=1) / y.var(ddof=1)
            df1, df2 = x.size - 1, y.size - 1
            p = 2 * min(stats.f.cdf(f, df1, df2), 1 - stats.f.cdf(f, df1, df2))
            return float(f), float(p), "H0: var(A) = var(B)"
        if test == "Chi-square independence":
            # Columns are treated as categorical labels; tabulate then test.
            table = pd.crosstab(df[a], df[b])
            chi2, p, dof, _ = stats.chi2_contingency(table)
            return float(chi2), float(p), f"DoF = {dof}"
        if test == "Two-proportion z-test":
            # Interpret A and B as 0/1 indicator columns
            if not set(np.unique(x)).issubset({0, 1}) or not set(np.unique(y)).issubset({0, 1}):
                raise ValueError("Two-proportion z-test needs 0/1 indicator columns.")
            p1 = x.mean(); p2 = y.mean()
            p_pool = (x.sum() + y.sum()) / (x.size + y.size)
            se = np.sqrt(p_pool * (1 - p_pool) * (1 / x.size + 1 / y.size))
            z = (p1 - p2) / se if se > 0 else 0.0
            p = 2 * (1 - stats.norm.cdf(abs(z)))
            return float(z), float(p), f"p1={p1:.3f}, p2={p2:.3f}"
        raise ValueError(f"Unknown test: {test}")
