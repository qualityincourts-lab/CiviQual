"""Shared Qt widgets and helpers used by all CiviQual tool panels."""

from __future__ import annotations

from typing import Callable, Optional

import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QDoubleSpinBox, QFormLayout, QGroupBox, QHBoxLayout,
    QLabel, QPushButton, QSpinBox, QTableView, QTableWidget, QTableWidgetItem,
    QTextEdit, QVBoxLayout, QWidget,
)

BURGUNDY = "#6d132a"
GOLD = "#dcad73"


class ToolPanel(QWidget):
    """Base class for every tool tab: left controls, right chart/results."""

    def __init__(self, title: str, description: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)

        header = QLabel(f"<b style='color:{BURGUNDY}'>{title}</b>")
        header.setTextFormat(Qt.RichText)
        outer.addWidget(header)
        if description:
            desc = QLabel(description)
            desc.setWordWrap(True)
            desc.setStyleSheet("color: #555;")
            outer.addWidget(desc)

        body = QHBoxLayout()
        outer.addLayout(body, 1)

        self._controls_box = QGroupBox("Inputs")
        self._controls_layout = QFormLayout(self._controls_box)
        body.addWidget(self._controls_box, 0)

        right = QVBoxLayout()
        body.addLayout(right, 1)

        self.figure = Figure(figsize=(6, 4.5), facecolor="white")
        self.canvas = FigureCanvasQTAgg(self.figure)
        right.addWidget(self.canvas, 2)

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setStyleSheet(
            f"background:#fff; border:1px solid {GOLD};"
        )
        right.addWidget(self.results_text, 1)

        self._run_button = QPushButton("Run Analysis")
        self._run_button.setStyleSheet(
            f"background:{BURGUNDY}; color:white; padding:6px 12px; font-weight:bold;"
        )
        right.addWidget(self._run_button)

    # Convenience wrappers -------------------------------------------------
    def add_control(self, label: str, widget: QWidget) -> None:
        self._controls_layout.addRow(label, widget)

    def set_run_handler(self, handler: Callable[[], None]) -> None:
        self._run_button.clicked.connect(handler)

    def show_error(self, msg: str) -> None:
        self.results_text.setHtml(f"<span style='color:#c0392b'>{msg}</span>")


def df_to_html(df: pd.DataFrame, max_rows: int = 200) -> str:
    """Render a dataframe as simple HTML for the results pane."""
    return df.head(max_rows).to_html(classes="civiqual-table", border=0,
                                     float_format=lambda v: f"{v:.4f}")


def make_column_combo(columns: list[str]) -> QComboBox:
    cb = QComboBox()
    cb.addItems(columns)
    return cb


def make_double_spin(value=0.0, minimum=-1e9, maximum=1e9, step=0.1, decimals=3) -> QDoubleSpinBox:
    sb = QDoubleSpinBox()
    sb.setRange(minimum, maximum)
    sb.setSingleStep(step)
    sb.setDecimals(decimals)
    sb.setValue(value)
    return sb


def make_int_spin(value=1, minimum=1, maximum=10000) -> QSpinBox:
    sb = QSpinBox()
    sb.setRange(minimum, maximum)
    sb.setValue(value)
    return sb


def dataframe_table(df: pd.DataFrame, parent: Optional[QWidget] = None) -> QTableWidget:
    table = QTableWidget(parent)
    table.setRowCount(len(df))
    table.setColumnCount(len(df.columns))
    table.setHorizontalHeaderLabels([str(c) for c in df.columns])
    for i, (_, row) in enumerate(df.iterrows()):
        for j, val in enumerate(row.tolist()):
            table.setItem(i, j, QTableWidgetItem(str(val)))
    table.resizeColumnsToContents()
    return table
