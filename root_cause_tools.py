"""Root cause analysis tools: 5 Whys, Is / Is Not matrix, Cause-and-Effect."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
    QLabel, QHBoxLayout, QComboBox,
)

from ui_common import ToolPanel


class RootCauseTools(ToolPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(
            "Root Cause Tools",
            "Structured tools for root cause identification: 5 Whys and Is / Is Not.",
            parent,
        )
        self.kind = QComboBox()
        self.kind.addItems(["5 Whys", "Is / Is Not"])
        self.problem = QLineEdit()
        self.problem.setPlaceholderText("Problem statement")
        self.add_control("Tool", self.kind)
        self.add_control("Problem", self.problem)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setRowCount(5)
        self.table.setHorizontalHeaderLabels(["Column A", "Column B"])
        for i in range(5):
            for j in range(2):
                self.table.setItem(i, j, QTableWidgetItem(""))

        # Inject the table into the results area
        wrapper = QVBoxLayout()
        wrapper.addWidget(self.table)
        self.results_text.setHtml("Use the table to capture inputs; click Run to render a summary.")
        self.set_run_handler(self._run)

        self.kind.currentTextChanged.connect(self._update_headers)
        self._update_headers(self.kind.currentText())

    def _update_headers(self, text: str) -> None:
        if text == "5 Whys":
            self.table.setRowCount(5)
            self.table.setHorizontalHeaderLabels(["Why", "Because"])
        else:
            self.table.setRowCount(5)
            self.table.setHorizontalHeaderLabels(["Is", "Is Not"])

    def _run(self) -> None:
        problem = self.problem.text() or "(no problem stated)"
        kind = self.kind.currentText()
        rows = []
        for i in range(self.table.rowCount()):
            a = self.table.item(i, 0).text() if self.table.item(i, 0) else ""
            b = self.table.item(i, 1).text() if self.table.item(i, 1) else ""
            if a or b:
                rows.append((a, b))
        html = f"<h3>{kind}</h3><p><b>Problem:</b> {problem}</p>"
        if kind == "5 Whys":
            for i, (why, because) in enumerate(rows, 1):
                html += f"<p><b>Why #{i}:</b> {why}<br><i>Because:</i> {because}</p>"
        else:
            html += "<table border='0'><tr><th>Is</th><th>Is Not</th></tr>"
            for a, b in rows:
                html += f"<tr><td>{a}</td><td>{b}</td></tr>"
            html += "</table>"
        self.results_text.setHtml(html)
