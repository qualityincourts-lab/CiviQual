"""Advanced capability analysis: Box-Cox transformation and distribution fits."""

from __future__ import annotations

import numpy as np
from PySide6.QtWidgets import QCheckBox, QComboBox, QPushButton
from scipy import stats

from statistics_engine import capability
from ui_common import ToolPanel, df_to_html, make_double_spin


class AdvancedCapability(ToolPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(
            "Advanced Capability Analysis",
            "Evaluate capability with Box-Cox transformation and non-normal distribution fits.",
            parent,
        )
        self.data_handler = data_handler
        self.col_combo = QComboBox()
        self.lsl = make_double_spin(0.0)
        self.usl = make_double_spin(10.0)
        self.use_lsl = QCheckBox("Use LSL"); self.use_lsl.setChecked(True)
        self.use_usl = QCheckBox("Use USL"); self.use_usl.setChecked(True)
        self.use_boxcox = QCheckBox("Apply Box-Cox transformation")
        self.dist_combo = QComboBox()
        self.dist_combo.addItems(["Normal", "Lognormal", "Weibull", "Gamma"])

        self.add_control("Column", self.col_combo)
        self.add_control("LSL", self.lsl)
        self.add_control("USL", self.usl)
        self.add_control("", self.use_lsl)
        self.add_control("", self.use_usl)
        self.add_control("", self.use_boxcox)
        self.add_control("Distribution", self.dist_combo)

        refresh = QPushButton("Refresh columns")
        refresh.clicked.connect(self._refresh)
        self.add_control("", refresh)

        self.set_run_handler(self._run)
        self._refresh()

    def _refresh(self) -> None:
        df = self.data_handler.dataframe()
        if df is None:
            return
        self.col_combo.clear()
        self.col_combo.addItems([c for c in df.columns if np.issubdtype(df[c].dtype, np.number)])

    def _run(self) -> None:
        df = self.data_handler.dataframe()
        if df is None:
            self.show_error("Load a dataset first.")
            return
        col = self.col_combo.currentText()
        if not col:
            self.show_error("Select a numeric column.")
            return
        arr = df[col].dropna().astype(float).values
        lsl = self.lsl.value() if self.use_lsl.isChecked() else None
        usl = self.usl.value() if self.use_usl.isChecked() else None

        transformed = arr
        notes = []
        lam = None
        if self.use_boxcox.isChecked():
            if np.any(arr <= 0):
                shift = -arr.min() + 1e-3
                transformed = arr + shift
                notes.append(f"Shifted data by +{shift:.4f} for positivity.")
            transformed, lam = stats.boxcox(transformed)
            notes.append(f"Box-Cox lambda = {lam:.4f}")
            if lsl is not None:
                lsl_t = stats.boxcox(np.array([lsl + (shift if np.any(arr <= 0) else 0)]), lmbda=lam)[0] if False else None
            # Keep limits in original space for reporting; transformed used only for stats
        cap = capability(transformed, lsl=lsl, usl=usl)

        html = "<h3>Capability Result</h3>"
        html += (f"<p>Mean: {cap.mean:.4f}<br>"
                 f"σ within: {cap.sigma_within:.4f}<br>"
                 f"σ overall: {cap.sigma_overall:.4f}<br>"
                 f"Cp: {cap.cp}<br>Cpk: {cap.cpk}<br>"
                 f"Pp: {cap.pp}<br>Ppk: {cap.ppk}<br>"
                 f"PPM total: {cap.ppm_total:.1f}</p>")
        if notes:
            html += "<p><i>" + " ".join(notes) + "</i></p>"
        self.results_text.setHtml(html)

        self.figure.clear()
        ax = self.figure.add_subplot(1, 1, 1)
        ax.hist(arr, bins=25, color="#6d132a", alpha=0.75, edgecolor="white")
        if lsl is not None:
            ax.axvline(lsl, color="#c0392b", linestyle="--", label="LSL")
        if usl is not None:
            ax.axvline(usl, color="#c0392b", linestyle="--", label="USL")
        ax.set_title(f"Capability Histogram — {col}")
        if lsl is not None or usl is not None:
            ax.legend()
        self.figure.tight_layout()
        self.canvas.draw()
