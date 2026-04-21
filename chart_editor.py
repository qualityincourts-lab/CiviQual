"""Chart editor: post-hoc customization of the most recently rendered chart."""

from __future__ import annotations

from PySide6.QtWidgets import QLineEdit, QSpinBox, QComboBox, QPushButton

from ui_common import ToolPanel, make_int_spin


class ChartEditor(ToolPanel):
    """A simple chart titler/relabeler that operates on the panel's own figure.

    In practice the user renders a chart elsewhere and then switches to this
    tab to fine-tune the title, axis labels, and aspect. This panel keeps its
    own demonstration chart so it remains useful standalone.
    """

    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(
            "Chart Editor",
            "Adjust the title, axis labels, grid, and aspect of a chart.",
            parent,
        )
        self.title_edit = QLineEdit()
        self.xlabel_edit = QLineEdit()
        self.ylabel_edit = QLineEdit()
        self.grid_combo = QComboBox(); self.grid_combo.addItems(["on", "off"])
        self.width = make_int_spin(8, 4, 20)
        self.height = make_int_spin(5, 3, 20)

        self.add_control("Title", self.title_edit)
        self.add_control("X-axis label", self.xlabel_edit)
        self.add_control("Y-axis label", self.ylabel_edit)
        self.add_control("Grid", self.grid_combo)
        self.add_control("Width (inches)", self.width)
        self.add_control("Height (inches)", self.height)

        self.set_run_handler(self._apply)
        self._draw_demo()

    def _draw_demo(self) -> None:
        import numpy as np
        self.figure.clear()
        ax = self.figure.add_subplot(1, 1, 1)
        x = np.arange(1, 21)
        y = np.random.default_rng(42).normal(10, 1.5, 20)
        ax.plot(x, y, marker="o", color="#6d132a")
        ax.axhline(y.mean(), color="#dcad73")
        ax.set_title("Demo Chart")
        ax.set_xlabel("Observation")
        ax.set_ylabel("Value")
        ax.grid(True, linestyle=":", alpha=0.6)
        self.figure.tight_layout()
        self.canvas.draw()

    def _apply(self) -> None:
        if not self.figure.axes:
            return
        ax = self.figure.axes[0]
        if self.title_edit.text():
            ax.set_title(self.title_edit.text())
        if self.xlabel_edit.text():
            ax.set_xlabel(self.xlabel_edit.text())
        if self.ylabel_edit.text():
            ax.set_ylabel(self.ylabel_edit.text())
        ax.grid(self.grid_combo.currentText() == "on",
                linestyle=":", alpha=0.6)
        self.figure.set_size_inches(self.width.value(), self.height.value())
        self.figure.tight_layout()
        self.canvas.draw()
        self.results_text.setHtml("<p>Chart updated.</p>")
