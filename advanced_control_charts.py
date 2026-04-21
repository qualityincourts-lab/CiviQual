"""Advanced control charts: CUSUM (V-mask and tabular) and EWMA."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from PySide6.QtWidgets import QComboBox, QPushButton

from ui_common import ToolPanel, make_double_spin


@dataclass
class CUSUMResult:
    values: np.ndarray
    target: float
    sigma: float
    k: float
    h: float
    high: np.ndarray
    low: np.ndarray
    signals_high: list[int]
    signals_low: list[int]


def cusum(values: np.ndarray, target: float, sigma: float,
          k: float = 0.5, h: float = 5.0) -> CUSUMResult:
    k_abs = k * sigma
    h_abs = h * sigma
    ch = np.zeros_like(values, dtype=float)
    cl = np.zeros_like(values, dtype=float)
    signals_h, signals_l = [], []
    for i, x in enumerate(values):
        prev_h = ch[i - 1] if i > 0 else 0.0
        prev_l = cl[i - 1] if i > 0 else 0.0
        ch[i] = max(0.0, prev_h + x - target - k_abs)
        cl[i] = min(0.0, prev_l + x - target + k_abs)
        if ch[i] > h_abs:
            signals_h.append(i)
        if cl[i] < -h_abs:
            signals_l.append(i)
    return CUSUMResult(values, target, sigma, k_abs, h_abs, ch, cl, signals_h, signals_l)


@dataclass
class EWMAResult:
    values: np.ndarray
    z: np.ndarray
    ucl: np.ndarray
    lcl: np.ndarray
    center: float
    lam: float
    l_sigma: float
    signals: list[int]


def ewma(values: np.ndarray, target: float, sigma: float,
         lam: float = 0.2, L: float = 3.0) -> EWMAResult:
    z = np.zeros_like(values, dtype=float)
    prev = target
    for i, x in enumerate(values):
        z[i] = lam * x + (1 - lam) * prev
        prev = z[i]
    i = np.arange(1, len(values) + 1)
    factor = np.sqrt(lam / (2 - lam) * (1 - (1 - lam) ** (2 * i)))
    ucl = target + L * sigma * factor
    lcl = target - L * sigma * factor
    signals = [k for k in range(len(values)) if z[k] > ucl[k] or z[k] < lcl[k]]
    return EWMAResult(values, z, ucl, lcl, target, lam, L, signals)


class AdvancedControlCharts(ToolPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(
            "Advanced Control Charts (CUSUM / EWMA)",
            "Detect small persistent shifts in process mean.",
            parent,
        )
        self.data_handler = data_handler
        self.chart_combo = QComboBox()
        self.chart_combo.addItems(["CUSUM (tabular)", "EWMA"])
        self.col_combo = QComboBox()
        self.target = make_double_spin(0.0)
        self.sigma = make_double_spin(1.0)
        self.param1 = make_double_spin(0.5, 0.01, 100, 0.05, 3)  # k or lambda
        self.param2 = make_double_spin(5.0, 0.1, 100, 0.5, 2)    # h or L

        self.add_control("Chart", self.chart_combo)
        self.add_control("Column", self.col_combo)
        self.add_control("Target (mu0)", self.target)
        self.add_control("Sigma", self.sigma)
        self.add_control("k / lambda", self.param1)
        self.add_control("h / L", self.param2)

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
            self.show_error("Select a column.")
            return
        arr = df[col].dropna().astype(float).values
        self.figure.clear()
        ax = self.figure.add_subplot(1, 1, 1)

        if self.chart_combo.currentText().startswith("CUSUM"):
            r = cusum(arr, self.target.value(), self.sigma.value(),
                      self.param1.value(), self.param2.value())
            idx = np.arange(1, len(arr) + 1)
            ax.plot(idx, r.high, marker="o", color="#6d132a", label="C+")
            ax.plot(idx, r.low, marker="s", color="#dcad73", label="C-")
            ax.axhline(r.h, color="#c0392b", linestyle="--", label="±h")
            ax.axhline(-r.h, color="#c0392b", linestyle="--")
            ax.set_title("CUSUM Chart")
            ax.legend()
            msg = f"Signals high: {r.signals_high} · Signals low: {r.signals_low}"
        else:
            r = ewma(arr, self.target.value(), self.sigma.value(),
                     self.param1.value(), self.param2.value())
            idx = np.arange(1, len(arr) + 1)
            ax.plot(idx, r.z, marker="o", color="#6d132a", label="Z")
            ax.plot(idx, r.ucl, color="#c0392b", linestyle="--", label="UCL")
            ax.plot(idx, r.lcl, color="#c0392b", linestyle="--", label="LCL")
            ax.axhline(r.center, color="#dcad73", label="Target")
            ax.set_title("EWMA Chart")
            ax.legend()
            msg = f"Signals at: {r.signals}"
        self.figure.tight_layout()
        self.canvas.draw()
        self.results_text.setHtml(f"<h3>Result</h3><p>{msg}</p>")
