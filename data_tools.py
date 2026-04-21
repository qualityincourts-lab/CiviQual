"""Data preparation tools: outlier detection, transformations, and filters."""

from __future__ import annotations

import numpy as np
import pandas as pd
from PySide6.QtWidgets import QComboBox, QPushButton

from ui_common import ToolPanel, df_to_html


class DataTools(ToolPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(
            "Data Preparation Tools",
            "Identify outliers, apply transformations, and filter rows.",
            parent,
        )
        self.data_handler = data_handler
        self.action = QComboBox()
        self.action.addItems([
            "Outlier detection (IQR)",
            "Outlier detection (3-sigma)",
            "Log transform",
            "Square-root transform",
            "Z-score standardize",
            "Remove rows with missing values",
        ])
        self.col_combo = QComboBox()

        self.add_control("Action", self.action)
        self.add_control("Column", self.col_combo)

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
        action = self.action.currentText()

        if action == "Remove rows with missing values":
            cleaned = df.dropna()
            removed = len(df) - len(cleaned)
            self.data_handler.set_dataframe(cleaned)
            self.results_text.setHtml(f"<p>Removed {removed} rows with missing values.</p>")
            self.figure.clear(); self.canvas.draw()
            return

        if not col:
            self.show_error("Select a numeric column.")
            return
        arr = df[col].dropna().astype(float).values

        if action.startswith("Outlier detection (IQR)"):
            q1, q3 = np.percentile(arr, [25, 75])
            iqr = q3 - q1
            low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            mask = (df[col] < low) | (df[col] > high)
            out_df = df.loc[mask]
            html = f"<h3>IQR Outliers</h3><p>Bounds: [{low:.4f}, {high:.4f}]. Found {len(out_df)} outliers.</p>"
            html += df_to_html(out_df.head(50))
            self.results_text.setHtml(html)
            self._boxplot(arr, col)
        elif action.startswith("Outlier detection (3-sigma)"):
            mu, sd = arr.mean(), arr.std(ddof=1)
            low, high = mu - 3 * sd, mu + 3 * sd
            mask = (df[col] < low) | (df[col] > high)
            out_df = df.loc[mask]
            html = f"<h3>3-Sigma Outliers</h3><p>Bounds: [{low:.4f}, {high:.4f}]. Found {len(out_df)} outliers.</p>"
            html += df_to_html(out_df.head(50))
            self.results_text.setHtml(html)
            self._boxplot(arr, col)
        elif action == "Log transform":
            new_col = f"log_{col}"
            if np.any(df[col] <= 0):
                shift = -df[col].min() + 1e-3
                df[new_col] = np.log(df[col] + shift)
                note = f"Shifted by +{shift:.4f} before log."
            else:
                df[new_col] = np.log(df[col])
                note = ""
            self.data_handler.set_dataframe(df)
            self._histogram_compare(arr, df[new_col].dropna().values, col, new_col, note)
        elif action == "Square-root transform":
            new_col = f"sqrt_{col}"
            if np.any(df[col] < 0):
                shift = -df[col].min() + 1e-3
                df[new_col] = np.sqrt(df[col] + shift)
                note = f"Shifted by +{shift:.4f} before sqrt."
            else:
                df[new_col] = np.sqrt(df[col])
                note = ""
            self.data_handler.set_dataframe(df)
            self._histogram_compare(arr, df[new_col].dropna().values, col, new_col, note)
        elif action == "Z-score standardize":
            new_col = f"z_{col}"
            mu, sd = arr.mean(), arr.std(ddof=1)
            df[new_col] = (df[col] - mu) / sd if sd > 0 else 0
            self.data_handler.set_dataframe(df)
            self._histogram_compare(arr, df[new_col].dropna().values, col, new_col, "")

    def _boxplot(self, arr, col) -> None:
        self.figure.clear()
        ax = self.figure.add_subplot(1, 1, 1)
        ax.boxplot(arr, vert=True, patch_artist=True,
                   boxprops=dict(facecolor="#dcad73", edgecolor="#6d132a"),
                   medianprops=dict(color="#6d132a", linewidth=2))
        ax.set_title(f"Box plot — {col}")
        self.figure.tight_layout()
        self.canvas.draw()

    def _histogram_compare(self, before, after, name_before, name_after, note) -> None:
        self.figure.clear()
        ax1 = self.figure.add_subplot(1, 2, 1)
        ax1.hist(before, bins=20, color="#6d132a", alpha=0.8, edgecolor="white")
        ax1.set_title(name_before)
        ax2 = self.figure.add_subplot(1, 2, 2)
        ax2.hist(after, bins=20, color="#dcad73", alpha=0.9, edgecolor="white")
        ax2.set_title(name_after)
        self.figure.tight_layout()
        self.canvas.draw()
        html = f"<p>Added column <b>{name_after}</b>.</p>"
        if note:
            html += f"<p><i>{note}</i></p>"
        self.results_text.setHtml(html)
