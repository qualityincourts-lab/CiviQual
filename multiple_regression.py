"""Multiple linear regression via ordinary least squares (OLS)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from PySide6.QtWidgets import QListWidget, QComboBox, QPushButton, QAbstractItemView
from scipy import stats

from ui_common import ToolPanel, df_to_html


def ols(X: np.ndarray, y: np.ndarray) -> dict:
    n, p = X.shape
    XtX = X.T @ X
    XtX_inv = np.linalg.pinv(XtX)
    beta = XtX_inv @ X.T @ y
    y_hat = X @ beta
    resid = y - y_hat
    ss_res = float(np.sum(resid ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    dfe = n - p
    mse = ss_res / dfe if dfe > 0 else 0.0
    se_beta = np.sqrt(np.diag(XtX_inv) * mse)
    t_stats = beta / se_beta
    p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), df=dfe))
    adj_r2 = 1 - (1 - r2) * (n - 1) / dfe if dfe > 0 else r2
    return {
        "beta": beta, "se": se_beta, "t": t_stats, "p": p_values,
        "r2": r2, "adj_r2": adj_r2, "residuals": resid, "fitted": y_hat,
        "mse": mse, "dfe": dfe,
    }


class MultipleRegression(ToolPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(
            "Multiple Regression",
            "Fit Y ~ intercept + beta1*X1 + beta2*X2 + ... using OLS.",
            parent,
        )
        self.data_handler = data_handler
        self.y_combo = QComboBox()
        self.x_list = QListWidget()
        self.x_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.add_control("Response Y", self.y_combo)
        self.add_control("Predictors X (ctrl+click)", self.x_list)

        refresh = QPushButton("Refresh columns")
        refresh.clicked.connect(self._refresh)
        self.add_control("", refresh)
        self.set_run_handler(self._run)
        self._refresh()

    def _refresh(self) -> None:
        df = self.data_handler.dataframe()
        if df is None:
            return
        cols = [c for c in df.columns if np.issubdtype(df[c].dtype, np.number)]
        self.y_combo.clear(); self.y_combo.addItems(cols)
        self.x_list.clear(); self.x_list.addItems(cols)

    def _run(self) -> None:
        df = self.data_handler.dataframe()
        if df is None:
            self.show_error("Load a dataset first.")
            return
        y_name = self.y_combo.currentText()
        x_names = [i.text() for i in self.x_list.selectedItems()]
        if not y_name or not x_names:
            self.show_error("Select a response and at least one predictor.")
            return
        clean = df[[y_name] + x_names].dropna()
        y = clean[y_name].astype(float).values
        X = clean[x_names].astype(float).values
        X = np.column_stack([np.ones(len(y)), X])
        out = ols(X, y)

        coef_df = pd.DataFrame({
            "Term": ["(Intercept)"] + x_names,
            "Coefficient": out["beta"],
            "SE": out["se"],
            "t": out["t"],
            "p": out["p"],
        })
        html = "<h3>Coefficients</h3>" + df_to_html(coef_df.round(4))
        html += f"<p>R² = {out['r2']:.4f} · Adjusted R² = {out['adj_r2']:.4f} · DFE = {out['dfe']}</p>"
        self.results_text.setHtml(html)

        self.figure.clear()
        ax1 = self.figure.add_subplot(1, 2, 1)
        ax1.scatter(out["fitted"], y, color="#6d132a", alpha=0.75)
        mn, mx = min(y.min(), out["fitted"].min()), max(y.max(), out["fitted"].max())
        ax1.plot([mn, mx], [mn, mx], color="#dcad73", linewidth=1.5)
        ax1.set_xlabel("Fitted"); ax1.set_ylabel("Observed")
        ax1.set_title("Observed vs Fitted")

        ax2 = self.figure.add_subplot(1, 2, 2)
        ax2.scatter(out["fitted"], out["residuals"], color="#6d132a", alpha=0.75)
        ax2.axhline(0, color="#dcad73")
        ax2.set_xlabel("Fitted"); ax2.set_ylabel("Residuals")
        ax2.set_title("Residuals vs Fitted")
        self.figure.tight_layout()
        self.canvas.draw()
