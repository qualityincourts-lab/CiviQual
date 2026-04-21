"""Planning tools: FMEA (Risk Priority Number) and Control Plan template."""

from __future__ import annotations

import pandas as pd
from PySide6.QtWidgets import (
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
)

from ui_common import ToolPanel, df_to_html


class PlanningTools(ToolPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(
            "Planning Tools (FMEA / Control Plan)",
            "Score failure modes using the Risk Priority Number (S × O × D).",
            parent,
        )
        self.kind = QComboBox()
        self.kind.addItems(["FMEA", "Control Plan"])
        self.add_control("Tool", self.kind)
        self.kind.currentTextChanged.connect(self._rebuild_table)

        self.table = QTableWidget()
        self._rebuild_table(self.kind.currentText())
        add_row = QPushButton("Add row")
        add_row.clicked.connect(lambda: self.table.setRowCount(self.table.rowCount() + 1))
        self.add_control("", add_row)
        self.add_control("Worksheet", self.table)
        self.set_run_handler(self._run)

    def _rebuild_table(self, kind: str) -> None:
        if kind == "FMEA":
            cols = ["Item / Function", "Failure Mode", "Effect", "Severity (1-10)",
                    "Cause", "Occurrence (1-10)", "Current Controls",
                    "Detection (1-10)", "RPN"]
        else:
            cols = ["Process Step", "Key Input (X)", "Spec / Tolerance",
                    "Measurement Method", "Sample Size", "Frequency",
                    "Control Method", "Reaction Plan"]
        self.table.setColumnCount(len(cols))
        self.table.setRowCount(10)
        self.table.setHorizontalHeaderLabels(cols)
        for i in range(10):
            for j in range(len(cols)):
                self.table.setItem(i, j, QTableWidgetItem(""))

    def _run(self) -> None:
        kind = self.kind.currentText()
        rows = []
        n_cols = self.table.columnCount()
        for i in range(self.table.rowCount()):
            row = []
            any_data = False
            for j in range(n_cols):
                item = self.table.item(i, j)
                txt = item.text() if item else ""
                row.append(txt)
                if txt.strip():
                    any_data = True
            if any_data:
                rows.append(row)

        if not rows:
            self.show_error("Enter at least one row.")
            return

        headers = [self.table.horizontalHeaderItem(j).text() for j in range(n_cols)]
        df = pd.DataFrame(rows, columns=headers)

        if kind == "FMEA":
            # Calculate RPN for each row
            def _compute_rpn(row):
                try:
                    s = float(row["Severity (1-10)"])
                    o = float(row["Occurrence (1-10)"])
                    d = float(row["Detection (1-10)"])
                    return int(s * o * d)
                except (ValueError, TypeError):
                    return ""
            df["RPN"] = df.apply(_compute_rpn, axis=1)
            df_sorted = df.copy()
            # Sort numeric RPN descending; empty values go last
            df_sorted["_rpn_sort"] = pd.to_numeric(df_sorted["RPN"], errors="coerce")
            df_sorted = df_sorted.sort_values("_rpn_sort", ascending=False, na_position="last")
            df_sorted = df_sorted.drop(columns=["_rpn_sort"])
            html = "<h3>FMEA (sorted by RPN)</h3>" + df_to_html(df_sorted)
        else:
            html = "<h3>Control Plan</h3>" + df_to_html(df)

        self.results_text.setHtml(html)

        # For FMEA, plot top RPN bars
        self.figure.clear()
        if kind == "FMEA" and "RPN" in df.columns:
            ax = self.figure.add_subplot(1, 1, 1)
            numeric = pd.to_numeric(df["RPN"], errors="coerce").fillna(0)
            labels = df["Failure Mode"].astype(str)
            order = numeric.sort_values(ascending=True).index
            ax.barh(labels.loc[order], numeric.loc[order], color="#6d132a")
            ax.set_xlabel("RPN")
            ax.set_title("Failure Modes by RPN")
            self.figure.tight_layout()
        self.canvas.draw()
