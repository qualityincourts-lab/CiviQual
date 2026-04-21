"""Sample size calculators for mean, proportion, and ANOVA."""

from __future__ import annotations

import numpy as np
from PySide6.QtWidgets import QComboBox
from scipy import stats

from ui_common import ToolPanel, make_double_spin, make_int_spin


class SampleSize(ToolPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(
            "Sample Size Calculator",
            "Determine the sample size required to achieve a target power.",
            parent,
        )
        self.kind = QComboBox()
        self.kind.addItems([
            "Mean — one sample",
            "Mean — two sample",
            "Proportion — one sample",
            "Proportion — two sample",
        ])
        self.effect = make_double_spin(0.5, 0.001, 100, 0.05, 3)
        self.sigma = make_double_spin(1.0, 0.001, 1e6, 0.1, 3)
        self.p1 = make_double_spin(0.5, 0.001, 0.999, 0.01, 3)
        self.p2 = make_double_spin(0.6, 0.001, 0.999, 0.01, 3)
        self.alpha = make_double_spin(0.05, 0.001, 0.5, 0.01, 3)
        self.power = make_double_spin(0.80, 0.5, 0.999, 0.01, 3)

        self.add_control("Type", self.kind)
        self.add_control("Effect size (delta)", self.effect)
        self.add_control("Sigma (for means)", self.sigma)
        self.add_control("p1 (for proportions)", self.p1)
        self.add_control("p2 (for proportions)", self.p2)
        self.add_control("Alpha", self.alpha)
        self.add_control("Power (1 - beta)", self.power)

        self.set_run_handler(self._run)

    def _run(self) -> None:
        alpha = self.alpha.value()
        power = self.power.value()
        z_alpha = stats.norm.ppf(1 - alpha / 2)
        z_beta = stats.norm.ppf(power)

        kind = self.kind.currentText()
        try:
            if kind.startswith("Mean — one"):
                n = ((z_alpha + z_beta) * self.sigma.value() / self.effect.value()) ** 2
                detail = f"σ = {self.sigma.value()}, δ = {self.effect.value()}"
            elif kind.startswith("Mean — two"):
                n = 2 * ((z_alpha + z_beta) * self.sigma.value() / self.effect.value()) ** 2
                detail = f"Per group. σ = {self.sigma.value()}, δ = {self.effect.value()}"
            elif kind.startswith("Proportion — one"):
                p = self.p1.value()
                n = ((z_alpha * np.sqrt(p * (1 - p)) + z_beta * np.sqrt(p * (1 - p))) /
                     self.effect.value()) ** 2
                detail = f"p = {p}"
            else:
                p1 = self.p1.value(); p2 = self.p2.value()
                p_bar = (p1 + p2) / 2
                n = ((z_alpha * np.sqrt(2 * p_bar * (1 - p_bar)) +
                      z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) /
                     abs(p1 - p2)) ** 2
                detail = f"Per group. p1 = {p1}, p2 = {p2}"
        except ZeroDivisionError:
            self.show_error("Effect size cannot be zero.")
            return

        n_ceil = int(np.ceil(n))
        self.results_text.setHtml(
            f"<h3>Required sample size</h3>"
            f"<p><b>n = {n_ceil}</b> ({detail}; α = {alpha}, power = {power})</p>"
            f"<p>Exact (unrounded): {n:.3f}</p>"
        )

        # Power curve plot
        self.figure.clear()
        ax = self.figure.add_subplot(1, 1, 1)
        ns = np.arange(5, max(n_ceil * 2, 50))
        if kind.startswith("Mean"):
            se = self.sigma.value() / np.sqrt(ns) * (np.sqrt(2) if "two" in kind else 1)
            z = self.effect.value() / se
        else:
            se = np.sqrt(self.p1.value() * (1 - self.p1.value()) / ns)
            z = self.effect.value() / se if "one" in kind else abs(self.p1.value() - self.p2.value()) / se
        powers = 1 - stats.norm.cdf(z_alpha - z)
        ax.plot(ns, powers, color="#6d132a", linewidth=1.6)
        ax.axhline(power, color="#dcad73", linestyle="--", label=f"Target {power}")
        ax.axvline(n_ceil, color="#c0392b", linestyle="--", label=f"n = {n_ceil}")
        ax.set_xlabel("Sample size"); ax.set_ylabel("Power")
        ax.set_title("Power vs sample size")
        ax.legend()
        self.figure.tight_layout()
        self.canvas.draw()
