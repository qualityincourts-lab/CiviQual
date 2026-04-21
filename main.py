"""CiviQual Stats — Application entry point.

Implements the DMAIC-structured application shell: menu, toolbar, status bar,
and five phase tabs (Define, Measure, Analyze, Improve, Control). Each tab
hosts the Free tools relevant to that phase and — if the license manager
reports Pro — the corresponding Pro tools.
"""

from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path

# High-DPI settings MUST be set before QApplication is instantiated
os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QLabel, QMainWindow, QMessageBox,
    QStatusBar, QTabWidget, QToolBar, QVBoxLayout, QWidget,
)

import free_tools as ft
from data_handler import DataHandler
from license_manager import LicenseManager
from version import __app_name__, __version__, __edition__, __publisher__, __website__


# ---------------------------------------------------------------------------
# Phase configuration
# ---------------------------------------------------------------------------
# Each phase has a list of (label, free_class, pro_class_or_None) triples.
# Pro classes are resolved lazily in _build_phase_tab() so the app still
# launches if a Pro module has an import error.
PHASE_CONFIG = {
    "Define": [
        ("SIPOC", ft.SIPOCPanel, None),
        ("Process Map", ft.ProcessMapPanel, None),
        ("RACI", ft.RACIPanel, None),
        ("Data Sampling", ft.DataSamplingPanel, None),
        ("Split Worksheet", ft.SplitWorksheetPanel, None),
    ],
    "Measure": [
        ("4-Up Chart", ft.FourUpPanel, None),
        ("Descriptive Stats", ft.DescriptivePanel, None),
        ("Control Charts (XmR)", ft.ControlChartsPanel, None),
        ("Capability", ft.CapabilityPanel, None),
        ("Probability Plot", ft.ProbabilityPlotPanel, None),
        ("Histogram", ft.HistogramPanel, None),
        ("Box Plot", ft.BoxPlotPanel, None),
        ("Run Chart", ft.RunChartPanel, None),
        ("★ MSA", None, "msa.MSA"),
        ("★ Sample Size", None, "sample_size.SampleSize"),
        ("★ Adv Capability", None, "advanced_capability.AdvancedCapability"),
    ],
    "Analyze": [
        ("ANOVA", ft.ANOVAPanel, None),
        ("Correlation", ft.CorrelationPanel, None),
        ("Pareto", ft.ParetoPanel, None),
        ("Swim Lane", ft.SwimLanePanel, None),
        ("VSM", ft.VSMPanel, None),
        ("Fishbone", ft.FishbonePanel, None),
        ("★ Hypothesis Tests", None, "hypothesis_tests.HypothesisTests"),
        ("★ DOE", None, "doe.DOE"),
        ("★ Regression", None, "multiple_regression.MultipleRegression"),
        ("★ Root Cause", None, "root_cause_tools.RootCauseTools"),
        ("★ Data Tools", None, "data_tools.DataTools"),
    ],
    "Improve": [
        ("ROI Calculator", ft.ROICalculatorPanel, None),
        ("★ Solution Tools", None, "solution_tools.SolutionTools"),
        ("★ Lean Calculators", None, "lean_calculators.LeanCalculators"),
    ],
    "Control": [
        ("Control Chart Review", ft.ControlChartReviewPanel, None),
        ("★ CUSUM / EWMA", None, "advanced_control_charts.AdvancedControlCharts"),
        ("★ Planning Tools", None, "planning_tools.PlanningTools"),
        ("★ Chart Editor", None, "chart_editor.ChartEditor"),
    ],
}


def _resolve(path: str):
    """Import 'module.ClassName' and return the class object."""
    mod_name, cls_name = path.rsplit(".", 1)
    mod = __import__(mod_name, fromlist=[cls_name])
    return getattr(mod, cls_name)


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_handler = DataHandler()
        self.license_manager = LicenseManager()

        self.setWindowTitle(f"{__app_name__} v{__version__} — {__edition__}")
        self.resize(1280, 820)

        # Icon (optional)
        icon_path = Path(__file__).parent / "civiqual_icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Order matters: status bar before central widget so panels can post
        # status messages during construction.
        self._setup_statusbar()
        self._setup_menus()
        self._setup_toolbar()
        self._setup_central_widget()
        self._update_status()

    # ------------------------------------------------------------------
    def _setup_statusbar(self) -> None:
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self._status_label = QLabel()
        self.status.addPermanentWidget(self._status_label)

    def _setup_menus(self) -> None:
        mb = self.menuBar()
        file_menu = mb.addMenu("&File")
        open_act = QAction("&Open Data…", self)
        open_act.triggered.connect(self._open_file)
        file_menu.addAction(open_act)
        file_menu.addSeparator()
        quit_act = QAction("E&xit", self)
        quit_act.triggered.connect(self.close)
        file_menu.addAction(quit_act)

        license_menu = mb.addMenu("&License")
        load_license = QAction("Install License File…", self)
        load_license.triggered.connect(self._install_license)
        license_menu.addAction(load_license)
        show_license = QAction("License Status…", self)
        show_license.triggered.connect(self._show_license_status)
        license_menu.addAction(show_license)

        help_menu = mb.addMenu("&Help")
        guide_act = QAction("User &Guide", self)
        guide_act.triggered.connect(self._open_user_guide)
        help_menu.addAction(guide_act)
        about_act = QAction("&About", self)
        about_act.triggered.connect(self._about)
        help_menu.addAction(about_act)

    def _setup_toolbar(self) -> None:
        tb = QToolBar("Main")
        tb.setMovable(False)
        self.addToolBar(tb)
        open_act = QAction("Open Data", self)
        open_act.triggered.connect(self._open_file)
        tb.addAction(open_act)

    def _setup_central_widget(self) -> None:
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        for phase, items in PHASE_CONFIG.items():
            tab = self._build_phase_tab(items)
            self.tabs.addTab(tab, phase)
        self.setCentralWidget(self.tabs)

    def _build_phase_tab(self, items: list[tuple]) -> QWidget:
        sub_tabs = QTabWidget()
        sub_tabs.setTabPosition(QTabWidget.West)
        for label, free_cls, pro_path in items:
            if free_cls is not None:
                panel = free_cls(self.data_handler, self.license_manager)
                sub_tabs.addTab(panel, label)
            elif pro_path is not None:
                if self.license_manager.is_pro:
                    try:
                        pro_cls = _resolve(pro_path)
                        panel = pro_cls(self.data_handler, self.license_manager)
                        sub_tabs.addTab(panel, label)
                    except Exception as exc:
                        placeholder = QWidget()
                        lay = QVBoxLayout(placeholder)
                        lay.addWidget(QLabel(
                            f"Pro module '{pro_path}' failed to load:\n{exc}\n\n"
                            f"{traceback.format_exc(limit=2)}"))
                        sub_tabs.addTab(placeholder, label)
                else:
                    placeholder = QWidget()
                    lay = QVBoxLayout(placeholder)
                    lay.addWidget(QLabel(
                        f"🔒 {label} is a Pro feature.\n\n"
                        "Install a Pro license from the License menu to enable this tool."
                    ))
                    sub_tabs.addTab(placeholder, label)
        return sub_tabs

    # ------------------------------------------------------------------
    def _open_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Open dataset", "",
            "Tabular files (*.csv *.tsv *.xlsx *.xls *.xlsm *.txt)"
        )
        if not path:
            return
        try:
            df = self.data_handler.load_file(path)
        except Exception as exc:
            QMessageBox.critical(self, "Load error", str(exc))
            return
        self.status.showMessage(f"Loaded {Path(path).name} — {len(df)} rows", 5000)
        self._update_status()
        # Notify every panel that columns may have changed
        self._refresh_all_panels()

    def _refresh_all_panels(self) -> None:
        for i in range(self.tabs.count()):
            phase_tab = self.tabs.widget(i)
            if isinstance(phase_tab, QTabWidget):
                for j in range(phase_tab.count()):
                    panel = phase_tab.widget(j)
                    for attr in ("_refresh", "_refresh_cols", "_populate_columns"):
                        fn = getattr(panel, attr, None)
                        if callable(fn):
                            try:
                                fn()
                            except Exception:
                                pass

    def _install_license(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Pro license file", "", "License file (*.json)"
        )
        if not path:
            return
        dest = self.license_manager.license_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy(path, dest)
        QMessageBox.information(
            self, "License installed",
            f"Installed to {dest}. Please restart the application for Pro tools to appear."
        )

    def _show_license_status(self) -> None:
        QMessageBox.information(
            self, "License Status",
            f"Edition: {self.license_manager.edition}\n\n"
            f"{self.license_manager.status_text()}"
        )

    def _open_user_guide(self) -> None:
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices
        guide = Path(__file__).parent / "docs" / "user_guide.html"
        if guide.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(guide)))
        else:
            QMessageBox.information(self, "User Guide",
                                    "The bundled user_guide.html was not found.")

    def _about(self) -> None:
        QMessageBox.about(
            self,
            f"About {__app_name__}",
            f"<h3>{__app_name__} v{__version__}</h3>"
            f"<p>{__edition__}</p>"
            f"<p>Published by {__publisher__}</p>"
            f"<p><a href='{__website__}'>{__website__}</a></p>"
            f"<p>Edition: <b>{self.license_manager.edition}</b></p>",
        )

    def _update_status(self) -> None:
        edition = self.license_manager.edition
        color = "#2e7d32" if self.license_manager.is_pro else "#6d132a"
        src = self.data_handler.source()
        src_txt = src.name if src else "no dataset loaded"
        self._status_label.setText(
            f"<span style='color:{color};font-weight:bold'>{edition}</span>"
            f" &nbsp; · &nbsp; {src_txt}"
        )


# ---------------------------------------------------------------------------
def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(__app_name__)
    app.setOrganizationName(__publisher__)
    w = MainWindow()
    w.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
