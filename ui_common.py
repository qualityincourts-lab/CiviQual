"""Shared Qt widgets and helpers used by all CiviQual tool panels."""

from __future__ import annotations

from typing import Callable, Optional

import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QDoubleSpinBox, QFileDialog, QFormLayout, QGroupBox, QHBoxLayout,
    QLabel, QMessageBox, QPushButton, QSpinBox, QSplitter, QTableView,
    QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget,
)

BURGUNDY = "#6d132a"
GOLD = "#dcad73"


class ToolPanel(QWidget):
    """Base class for every tool tab: left controls, right chart/results.

    Layout:
        +--------+--------------------------------+
        | Inputs | [Chart canvas]                 |
        |        |   (vertical splitter — drag)   |
        |        | [Results text — scrollable]    |
        |        | [Run Analysis] [Save Chart...] |
        +--------+--------------------------------+

    The splitter starts ~80/20 in favour of the canvas so charts have room
    to breathe (4-Up especially); the results box remains scrollable when
    its content overflows.
    """

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

        right_widget = QWidget()
        right = QVBoxLayout(right_widget)
        right.setContentsMargins(0, 0, 0, 0)
        body.addWidget(right_widget, 1)

        self.figure = Figure(figsize=(6, 4.5), facecolor="white")
        self.canvas = FigureCanvasQTAgg(self.figure)

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setStyleSheet(
            f"background:#fff; border:1px solid {GOLD};"
        )

        # Vertical splitter so the user can resize chart vs. results pane.
        self._chart_results_splitter = QSplitter(Qt.Orientation.Vertical)
        self._chart_results_splitter.addWidget(self.canvas)
        self._chart_results_splitter.addWidget(self.results_text)
        self._chart_results_splitter.setStretchFactor(0, 4)
        self._chart_results_splitter.setStretchFactor(1, 1)
        self._chart_results_splitter.setSizes([800, 200])
        self._chart_results_splitter.setChildrenCollapsible(False)
        right.addWidget(self._chart_results_splitter, 1)

        button_row = QHBoxLayout()
        self._run_button = QPushButton("Run Analysis")
        self._run_button.setStyleSheet(
            f"background:{BURGUNDY}; color:white; padding:6px 12px; font-weight:bold;"
        )
        button_row.addWidget(self._run_button)

        self._save_chart_button = QPushButton("Save Chart…")
        self._save_chart_button.setStyleSheet(
            f"background:white; color:{BURGUNDY}; padding:6px 12px; "
            f"border:1px solid {BURGUNDY};"
        )
        self._save_chart_button.clicked.connect(self._save_chart)
        button_row.addWidget(self._save_chart_button)
        button_row.addStretch(1)
        right.addLayout(button_row)

    # Convenience wrappers -------------------------------------------------
    def add_control(self, label: str, widget: QWidget) -> None:
        self._controls_layout.addRow(label, widget)

    def set_run_handler(self, handler: Callable[[], None]) -> None:
        self._run_button.clicked.connect(handler)

    def show_error(self, msg: str) -> None:
        self.results_text.setHtml(f"<span style='color:#c0392b'>{msg}</span>")

    def _save_chart(self) -> None:
        """Save the current matplotlib figure to a user-chosen file."""
        safe_title = "".join(c for c in self.title if c.isalnum() or c in "-_ ").strip()
        default_name = f"{safe_title.replace(' ', '_')}.png" if safe_title else "chart.png"
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Chart", default_name,
            "PNG image (*.png);;PDF (*.pdf);;SVG (*.svg);;JPEG (*.jpg)",
        )
        if not path:
            return
        try:
            self.figure.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
        except Exception as e:
            QMessageBox.critical(self, "Save Chart", f"Could not save chart:\n{e}")


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
