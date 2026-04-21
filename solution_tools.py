"""Solution selection tools: PICK chart and impact/effort matrix."""

from __future__ import annotations

import numpy as np
from PySide6.QtWidgets import (
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout,
)

from ui_common import ToolPanel


class SolutionTools(ToolPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(
            "Solution Selection Tools",
            "PICK chart (Possible, Implement, Challenge, Kill) and impact/effort matrix.",
            parent,
        )
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setRowCount(10)
        self.table.setHorizontalHeaderLabels(["Solution", "Impact (1-10)", "Effort (1-10)"])
        for i in range(10):
            for j in range(3):
                self.table.setItem(i, j, QTableWidgetItem(""))

        add_row = QPushButton("Add row")
        add_row.clicked.connect(lambda: self.table.setRowCount(self.table.rowCount() + 1))
        self.add_control("", add_row)
        self.add_control("Solutions", self.table)

        self.set_run_handler(self._run)

    def _run(self) -> None:
        items = []
        for i in range(self.table.rowCount()):
            name = self.table.item(i, 0).text() if self.table.item(i, 0) else ""
            try:
                impact = float(self.table.item(i, 1).text()) if self.table.item(i, 1) and self.table.item(i, 1).text() else None
                effort = float(self.table.item(i, 2).text()) if self.table.item(i, 2) and self.table.item(i, 2).text() else None
            except ValueError:
                continue
            if name and impact is not None and effort is not None:
                items.append((name, impact, effort))

        if not items:
            self.show_error("Enter at least one solution with impact and effort values.")
            return

        self.figure.clear()
        ax = self.figure.add_subplot(1, 1, 1)
        for name, impact, effort in items:
            if impact >= 5 and effort < 5:
                color = "#2e7d32"; label = "Implement"
            elif impact >= 5 and effort >= 5:
                color = "#6d132a"; label = "Challenge"
            elif impact < 5 and effort < 5:
                color = "#dcad73"; label = "Possible"
            else:
                color = "#c0392b"; label = "Kill"
            ax.scatter(effort, impact, s=180, color=color, alpha=0.85)
            ax.annotate(name, (effort, impact), xytext=(6, 6),
                        textcoords="offset points", fontsize=8)

        ax.axvline(5, color="#b2b2b2", linewidth=1)
        ax.axhline(5, color="#b2b2b2", linewidth=1)
        ax.set_xlim(0, 10); ax.set_ylim(0, 10)
        ax.set_xlabel("Effort"); ax.set_ylabel("Impact")
        ax.set_title("PICK Chart")
        ax.text(2.5, 9.5, "IMPLEMENT", fontsize=10, weight="bold", color="#2e7d32")
        ax.text(7.5, 9.5, "CHALLENGE", fontsize=10, weight="bold", color="#6d132a")
        ax.text(2.5, 0.5, "POSSIBLE", fontsize=10, weight="bold", color="#dcad73")
        ax.text(7.5, 0.5, "KILL", fontsize=10, weight="bold", color="#c0392b")
        self.figure.tight_layout()
        self.canvas.draw()

        html = "<h3>PICK Classification</h3><ul>"
        for name, impact, effort in items:
            quadrant = ("Implement" if impact >= 5 and effort < 5 else
                        "Challenge" if impact >= 5 else
                        "Possible" if effort < 5 else "Kill")
            html += f"<li><b>{name}</b>: Impact={impact}, Effort={effort} → {quadrant}</li>"
        html += "</ul>"
        self.results_text.setHtml(html)
