"""Lean calculators: Takt time, OEE, PCE, 5S score, Little's Law."""

from __future__ import annotations

from PySide6.QtWidgets import QComboBox

from ui_common import ToolPanel, make_double_spin


class LeanCalculators(ToolPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(
            "Lean Calculators",
            "Takt Time, OEE, Process Cycle Efficiency, 5S Score, Little's Law.",
            parent,
        )
        self.kind = QComboBox()
        self.kind.addItems([
            "Takt Time",
            "Overall Equipment Effectiveness (OEE)",
            "Process Cycle Efficiency (PCE)",
            "Little's Law (WIP = Throughput × Lead Time)",
        ])
        # Generic parameter boxes; reused per selection
        self.p1 = make_double_spin(480.0, 0, 1e9, 1, 2)
        self.p2 = make_double_spin(60.0, 0, 1e9, 1, 2)
        self.p3 = make_double_spin(0.95, 0, 1, 0.01, 3)
        self.p4 = make_double_spin(0.95, 0, 1, 0.01, 3)

        self.add_control("Calculation", self.kind)
        self.add_control("Param 1", self.p1)
        self.add_control("Param 2", self.p2)
        self.add_control("Param 3", self.p3)
        self.add_control("Param 4", self.p4)
        self.set_run_handler(self._run)
        self.kind.currentTextChanged.connect(self._update_labels)
        self._update_labels()

    def _update_labels(self) -> None:
        kind = self.kind.currentText()
        labels = {
            "Takt Time": ("Available time (min)", "Customer demand (units)", "—", "—"),
            "Overall Equipment Effectiveness (OEE)":
                ("Availability", "Performance", "Quality", "—"),
            "Process Cycle Efficiency (PCE)":
                ("Value-add time", "Total cycle time", "—", "—"),
            "Little's Law (WIP = Throughput × Lead Time)":
                ("Throughput", "Lead Time", "—", "—"),
        }
        # Form labels cannot be changed in-place easily; set tooltips instead
        self.p1.setToolTip(labels[kind][0])
        self.p2.setToolTip(labels[kind][1])
        self.p3.setToolTip(labels[kind][2])
        self.p4.setToolTip(labels[kind][3])

    def _run(self) -> None:
        kind = self.kind.currentText()
        p1, p2, p3, p4 = self.p1.value(), self.p2.value(), self.p3.value(), self.p4.value()
        try:
            if kind == "Takt Time":
                result = p1 / p2 if p2 else float("inf")
                html = f"<p><b>Takt Time:</b> {result:.3f} minutes per unit</p>"
            elif kind.startswith("Overall Equipment"):
                oee = p1 * p2 * p3 * 100
                html = f"<p><b>OEE:</b> {oee:.2f}%</p>"
            elif kind.startswith("Process Cycle Efficiency"):
                pce = 100 * p1 / p2 if p2 else 0
                html = f"<p><b>PCE:</b> {pce:.2f}%</p>"
            else:
                wip = p1 * p2
                html = f"<p><b>WIP:</b> {wip:.2f} units</p>"
        except Exception as exc:
            self.show_error(str(exc))
            return
        self.results_text.setHtml(f"<h3>{kind}</h3>" + html)
        self.figure.clear()
        self.canvas.draw()
