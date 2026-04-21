"""Free-tier tool panels.

All Free tools are gathered into one module to keep the import surface small.
Each class is a subclass of ToolPanel and is instantiated by main.py for the
appropriate DMAIC tab.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QLineEdit, QPushButton, QSpinBox,
    QTableWidget, QTableWidgetItem,
)

import process_diagrams
import statistics_engine as se
import visualizations as viz
from ui_common import ToolPanel, df_to_html, make_double_spin, make_int_spin


# ---------------------------------------------------------------------------
# Define phase
# ---------------------------------------------------------------------------
class SIPOCPanel(ToolPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(
            "SIPOC Diagram",
            "Map Suppliers, Inputs, Process, Outputs, and Customers. Enter one item per line.",
            parent,
        )
        from PySide6.QtWidgets import QPlainTextEdit
        self.suppliers = QPlainTextEdit()
        self.inputs = QPlainTextEdit()
        self.process = QPlainTextEdit()
        self.outputs = QPlainTextEdit()
        self.customers = QPlainTextEdit()
        for w, placeholder in [
            (self.suppliers, "Suppliers"),
            (self.inputs, "Inputs"),
            (self.process, "Process steps"),
            (self.outputs, "Outputs"),
            (self.customers, "Customers"),
        ]:
            w.setPlaceholderText(placeholder)
            w.setMaximumHeight(80)
        self.add_control("Suppliers", self.suppliers)
        self.add_control("Inputs", self.inputs)
        self.add_control("Process", self.process)
        self.add_control("Outputs", self.outputs)
        self.add_control("Customers", self.customers)
        self.set_run_handler(self._run)

    @staticmethod
    def _lines(widget) -> list[str]:
        return [ln for ln in widget.toPlainText().splitlines() if ln.strip()]

    def _run(self) -> None:
        process_diagrams.draw_sipoc(
            self.figure,
            self._lines(self.suppliers),
            self._lines(self.inputs),
            self._lines(self.process),
            self._lines(self.outputs),
            self._lines(self.customers),
        )
        self.canvas.draw()
        self.results_text.setHtml("<p>SIPOC diagram rendered.</p>")


class ProcessMapPanel(ToolPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__("Process Map",
                         "High-level linear process map. One step per line.", parent)
        from PySide6.QtWidgets import QPlainTextEdit
        self.steps = QPlainTextEdit()
        self.steps.setPlaceholderText("One step per line")
        self.add_control("Steps", self.steps)
        self.set_run_handler(self._run)

    def _run(self) -> None:
        steps = [s for s in self.steps.toPlainText().splitlines() if s.strip()]
        if not steps:
            self.show_error("Enter at least one step.")
            return
        process_diagrams.draw_process_map(self.figure, steps)
        self.canvas.draw()
        self.results_text.setHtml(f"<p>{len(steps)} steps rendered.</p>")


class RACIPanel(ToolPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(
            "RACI Matrix",
            "Enter tasks (rows) and roles (columns). Assign R, A, C, or I.",
            parent,
        )
        self.roles_edit = QLineEdit("Clerk, Deputy Clerk, CMO, Judge")
        self.add_control("Roles (comma-separated)", self.roles_edit)
        self.table = QTableWidget(5, 5)
        self.table.setHorizontalHeaderLabels(
            ["Task", "Role 1", "Role 2", "Role 3", "Role 4"])
        for i in range(5):
            for j in range(5):
                self.table.setItem(i, j, QTableWidgetItem(""))
        self.add_control("Tasks x Roles", self.table)
        rebuild = QPushButton("Apply roles")
        rebuild.clicked.connect(self._apply_roles)
        self.add_control("", rebuild)
        self.set_run_handler(self._run)

    def _apply_roles(self) -> None:
        roles = [r.strip() for r in self.roles_edit.text().split(",") if r.strip()]
        self.table.setColumnCount(len(roles) + 1)
        headers = ["Task"] + roles
        self.table.setHorizontalHeaderLabels(headers)
        for i in range(self.table.rowCount()):
            for j in range(1, self.table.columnCount()):
                if self.table.item(i, j) is None:
                    self.table.setItem(i, j, QTableWidgetItem(""))

    def _run(self) -> None:
        roles = [r.strip() for r in self.roles_edit.text().split(",") if r.strip()]
        tasks = []
        matrix = []
        for i in range(self.table.rowCount()):
            task_item = self.table.item(i, 0)
            if not task_item or not task_item.text().strip():
                continue
            tasks.append(task_item.text())
            row = []
            for j in range(len(roles)):
                item = self.table.item(i, j + 1)
                row.append(item.text().strip().upper() if item else "")
            matrix.append(row)
        if not tasks:
            self.show_error("Enter at least one task.")
            return
        process_diagrams.draw_raci(self.figure, tasks, roles, matrix)
        self.canvas.draw()
        self.results_text.setHtml(f"<p>RACI: {len(tasks)} tasks × {len(roles)} roles.</p>")


class DataSamplingPanel(ToolPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(
            "Data Sampling",
            "Draw a random, systematic, or range-based sample from the loaded dataset.",
            parent,
        )
        self.data_handler = data_handler
        self.kind = QComboBox()
        self.kind.addItems(["Random", "Systematic (every k)", "Observation range"])
        self.size = make_int_spin(30, 1, 100000)
        self.start = make_int_spin(1, 1, 100000)
        self.end = make_int_spin(100, 1, 100000)
        self.add_control("Method", self.kind)
        self.add_control("Sample size / every-k", self.size)
        self.add_control("Start (range)", self.start)
        self.add_control("End (range)", self.end)
        self.set_run_handler(self._run)

    def _run(self) -> None:
        df = self.data_handler.dataframe()
        if df is None:
            self.show_error("Load a dataset first.")
            return
        kind = self.kind.currentText()
        if kind == "Random":
            n = min(self.size.value(), len(df))
            sample = df.sample(n=n, random_state=42).reset_index(drop=True)
        elif kind.startswith("Systematic"):
            k = self.size.value()
            sample = df.iloc[::max(k, 1)].reset_index(drop=True)
        else:
            start = max(self.start.value() - 1, 0)
            end = min(self.end.value(), len(df))
            sample = df.iloc[start:end].reset_index(drop=True)
        self.data_handler.set_dataframe(sample)
        self.results_text.setHtml(
            f"<p>Kept {len(sample)} rows.</p>" + df_to_html(sample.head(50))
        )
        self.figure.clear(); self.canvas.draw()


class SplitWorksheetPanel(ToolPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(
            "Split Worksheet",
            "Split the loaded dataset by a grouping column and export each group.",
            parent,
        )
        self.data_handler = data_handler
        self.col = QComboBox()
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self._refresh)
        self.add_control("Group column", self.col)
        self.add_control("", refresh)
        self.set_run_handler(self._run)
        self._refresh()

    def _refresh(self) -> None:
        df = self.data_handler.dataframe()
        if df is None:
            return
        self.col.clear(); self.col.addItems(df.columns.tolist())

    def _run(self) -> None:
        df = self.data_handler.dataframe()
        if df is None:
            self.show_error("Load a dataset first."); return
        col = self.col.currentText()
        if not col:
            self.show_error("Select a column."); return
        from pathlib import Path
        out_dir = Path.home() / "CiviQualSplits"
        out_dir.mkdir(exist_ok=True)
        groups = df.groupby(col)
        lines = []
        for name, group in groups:
            safe = "".join(c for c in str(name) if c.isalnum() or c in "-_")
            fn = out_dir / f"{col}_{safe}.csv"
            group.to_csv(fn, index=False)
            lines.append(f"<li>{fn.name} ({len(group)} rows)</li>")
        self.results_text.setHtml(
            f"<h3>Split complete</h3><p>Output directory: {out_dir}</p><ul>" +
            "\n".join(lines) + "</ul>"
        )


# ---------------------------------------------------------------------------
# Measure phase
# ---------------------------------------------------------------------------
class _SingleColumnPanel(ToolPanel):
    """Utility base class for tools that take a single numeric column."""

    def __init__(self, data_handler, license_manager, title, description, parent=None):
        super().__init__(title, description, parent)
        self.data_handler = data_handler
        self.col = QComboBox()
        self.add_control("Column", self.col)
        refresh = QPushButton("Refresh columns")
        refresh.clicked.connect(self._refresh)
        self.add_control("", refresh)
        self._refresh()

    def _refresh(self) -> None:
        df = self.data_handler.dataframe()
        if df is None:
            return
        self.col.clear()
        self.col.addItems([c for c in df.columns if np.issubdtype(df[c].dtype, np.number)])

    def _arr(self) -> np.ndarray | None:
        df = self.data_handler.dataframe()
        if df is None:
            self.show_error("Load a dataset first."); return None
        col = self.col.currentText()
        if not col:
            self.show_error("Select a numeric column."); return None
        return df[col].dropna().astype(float).values


class FourUpPanel(_SingleColumnPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(data_handler, license_manager,
                         "Watson 4-Up Chart",
                         "Histogram, run chart, X chart, and probability plot.", parent)
        self.set_run_handler(self._run)

    def _run(self) -> None:
        arr = self._arr()
        if arr is None:
            return
        viz.draw_four_up(self.figure, arr, title=f"4-Up — {self.col.currentText()}")
        self.canvas.draw()
        d = se.descriptive(arr)
        self.results_text.setHtml(
            f"<p>n = {d.n} · mean = {d.mean:.4f} · sd = {d.std:.4f} · "
            f"95% CI = [{d.ci95_lower:.3f}, {d.ci95_upper:.3f}]</p>"
        )


class DescriptivePanel(_SingleColumnPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(data_handler, license_manager,
                         "Descriptive Statistics",
                         "Summary statistics and normality tests.", parent)
        self.set_run_handler(self._run)

    def _run(self) -> None:
        arr = self._arr()
        if arr is None:
            return
        d = se.descriptive(arr)
        ad = se.anderson_darling(arr)
        rows = [
            ("n", d.n), ("Mean", f"{d.mean:.4f}"),
            ("Std Dev", f"{d.std:.4f}"), ("SEM", f"{d.sem:.4f}"),
            ("Min", f"{d.min:.4f}"), ("Q1", f"{d.q1:.4f}"),
            ("Median", f"{d.median:.4f}"), ("Q3", f"{d.q3:.4f}"),
            ("Max", f"{d.max:.4f}"),
            ("Skewness", f"{d.skewness:.4f}"),
            ("Kurtosis", f"{d.kurtosis:.4f}"),
            ("95% CI (mean)", f"[{d.ci95_lower:.3f}, {d.ci95_upper:.3f}]"),
            ("Anderson-Darling stat", f"{ad.statistic:.4f}"),
            ("Anderson-Darling p", f"{ad.p_value:.4g}"),
        ]
        tbl = "<table border='0'>" + "".join(
            f"<tr><td><b>{k}</b></td><td>{v}</td></tr>" for k, v in rows
        ) + "</table>"
        self.results_text.setHtml(f"<h3>Descriptive Statistics</h3>{tbl}")
        viz.draw_histogram(self.figure, arr, title=self.col.currentText())
        self.canvas.draw()


class ControlChartsPanel(_SingleColumnPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(data_handler, license_manager,
                         "Control Charts (XmR)",
                         "Individuals and moving range chart with Western Electric rules.",
                         parent)
        self.set_run_handler(self._run)

    def _run(self) -> None:
        arr = self._arr()
        if arr is None:
            return
        result = se.xmr_chart(arr)
        viz.draw_xmr(self.figure, result, label=self.col.currentText())
        self.canvas.draw()
        html = f"<p>X̄ = {result.x_center:.4f} · σ̂ = {result.sigma_hat:.4f}</p>"
        html += f"<p>X-UCL = {result.x_ucl:.4f} · X-LCL = {result.x_lcl:.4f}</p>"
        html += f"<p>MR̄ = {result.mr_center:.4f} · MR-UCL = {result.mr_ucl:.4f}</p>"
        if result.signals:
            html += "<h3>Rule signals</h3><ul>"
            for s in result.signals:
                html += f"<li>Point {s['index']+1}: Rule {s['rule']} — {s['description']}</li>"
            html += "</ul>"
        else:
            html += "<p>No control-rule signals detected.</p>"
        self.results_text.setHtml(html)


class CapabilityPanel(_SingleColumnPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(data_handler, license_manager,
                         "Process Capability",
                         "Cp, Cpk, Pp, Ppk with PPM projections.", parent)
        self.lsl = make_double_spin(0.0)
        self.usl = make_double_spin(10.0)
        self.use_lsl = QCheckBox("Use LSL"); self.use_lsl.setChecked(True)
        self.use_usl = QCheckBox("Use USL"); self.use_usl.setChecked(True)
        self.add_control("LSL", self.lsl)
        self.add_control("USL", self.usl)
        self.add_control("", self.use_lsl)
        self.add_control("", self.use_usl)
        self.set_run_handler(self._run)

    def _run(self) -> None:
        arr = self._arr()
        if arr is None:
            return
        lsl = self.lsl.value() if self.use_lsl.isChecked() else None
        usl = self.usl.value() if self.use_usl.isChecked() else None
        cap = se.capability(arr, lsl=lsl, usl=usl)
        viz.draw_histogram(self.figure, arr, lsl=lsl, usl=usl,
                           title=f"Capability — {self.col.currentText()}")
        self.canvas.draw()
        html = (f"<p>Mean = {cap.mean:.4f} · σ within = {cap.sigma_within:.4f} · "
                f"σ overall = {cap.sigma_overall:.4f}</p>"
                f"<p>Cp = {cap.cp} · Cpk = {cap.cpk}<br>"
                f"Pp = {cap.pp} · Ppk = {cap.ppk}</p>"
                f"<p>PPM below LSL = {cap.ppm_below:.1f} · "
                f"PPM above USL = {cap.ppm_above:.1f} · "
                f"PPM total = {cap.ppm_total:.1f}</p>")
        self.results_text.setHtml(html)


class ProbabilityPlotPanel(_SingleColumnPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(data_handler, license_manager,
                         "Normal Probability Plot",
                         "Visual check for normality.", parent)
        self.set_run_handler(self._run)

    def _run(self) -> None:
        arr = self._arr()
        if arr is None:
            return
        viz.draw_probability_plot(self.figure, arr,
                                  title=f"Probability Plot — {self.col.currentText()}")
        self.canvas.draw()
        ad = se.anderson_darling(arr)
        self.results_text.setHtml(
            f"<p>Anderson-Darling stat = {ad.statistic:.4f} · "
            f"p = {ad.p_value:.4g} · "
            f"{'Normal at 0.05' if ad.normal_at_95 else 'Rejects normality at 0.05'}</p>"
        )


class HistogramPanel(_SingleColumnPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(data_handler, license_manager,
                         "Histogram",
                         "Frequency histogram with overlaid normal density.", parent)
        self.bins = make_int_spin(20, 5, 200)
        self.add_control("Bins", self.bins)
        self.set_run_handler(self._run)

    def _run(self) -> None:
        arr = self._arr()
        if arr is None:
            return
        viz.draw_histogram(self.figure, arr, bins=self.bins.value(),
                           title=self.col.currentText())
        self.canvas.draw()
        self.results_text.setHtml(f"<p>n = {arr.size}</p>")


class BoxPlotPanel(_SingleColumnPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(data_handler, license_manager,
                         "Box Plot",
                         "Quartile-based distribution view.", parent)
        self.set_run_handler(self._run)

    def _run(self) -> None:
        arr = self._arr()
        if arr is None:
            return
        viz.draw_box(self.figure, arr, title=self.col.currentText())
        self.canvas.draw()
        d = se.descriptive(arr)
        self.results_text.setHtml(
            f"<p>Q1 = {d.q1:.3f} · Median = {d.median:.3f} · Q3 = {d.q3:.3f} · "
            f"IQR = {d.q3 - d.q1:.3f}</p>"
        )


class RunChartPanel(_SingleColumnPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(data_handler, license_manager,
                         "Run Chart",
                         "Time series with runs tests and trend test.", parent)
        self.set_run_handler(self._run)

    def _run(self) -> None:
        arr = self._arr()
        if arr is None:
            return
        r = se.run_chart(arr)
        viz.draw_run_chart(self.figure, r, title=self.col.currentText())
        self.canvas.draw()
        self.results_text.setHtml(
            f"<p>Median = {r.median:.3f} · Runs observed = {r.runs_observed} · "
            f"Expected = {r.runs_expected:.2f} · p (randomness) = {r.runs_p:.4g}</p>"
            f"<p>Longest run = {r.longest_run} · Mann-Kendall trend p = {r.trend_p:.4g}</p>"
        )


# ---------------------------------------------------------------------------
# Analyze phase
# ---------------------------------------------------------------------------
class ANOVAPanel(ToolPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(
            "One-way ANOVA",
            "Compare means across groups. Requires a grouping column and a value column.",
            parent,
        )
        self.data_handler = data_handler
        self.group_col = QComboBox()
        self.value_col = QComboBox()
        refresh = QPushButton("Refresh columns")
        refresh.clicked.connect(self._refresh)
        self.add_control("Group column", self.group_col)
        self.add_control("Value column", self.value_col)
        self.add_control("", refresh)
        self._refresh()
        self.set_run_handler(self._run)

    def _refresh(self) -> None:
        df = self.data_handler.dataframe()
        if df is None:
            return
        self.group_col.clear(); self.group_col.addItems(df.columns.tolist())
        numeric = [c for c in df.columns if np.issubdtype(df[c].dtype, np.number)]
        self.value_col.clear(); self.value_col.addItems(numeric)

    def _run(self) -> None:
        df = self.data_handler.dataframe()
        if df is None:
            self.show_error("Load a dataset first."); return
        gc = self.group_col.currentText()
        vc = self.value_col.currentText()
        if not gc or not vc:
            self.show_error("Select both columns."); return
        groups = {str(name): grp[vc].dropna().values
                  for name, grp in df.groupby(gc)}
        a = se.one_way_anova(groups)
        html = f"<h3>ANOVA</h3><p>F = {a.f_statistic:.4f} · p = {a.p_value:.4g}</p>"
        html += "<table border='0'><tr><th>Source</th><th>SS</th><th>DF</th><th>MS</th></tr>"
        html += f"<tr><td>Between</td><td>{a.ss_between:.4f}</td><td>{a.df_between}</td><td>{a.ms_between:.4f}</td></tr>"
        html += f"<tr><td>Within</td><td>{a.ss_within:.4f}</td><td>{a.df_within}</td><td>{a.ms_within:.4f}</td></tr>"
        html += "</table>"
        if a.tukey_pairs:
            html += "<h3>Tukey HSD</h3>"
            html += df_to_html(pd.DataFrame(a.tukey_pairs))
        self.results_text.setHtml(html)

        self.figure.clear()
        ax = self.figure.add_subplot(1, 1, 1)
        names = list(groups.keys())
        data = [groups[n] for n in names]
        bp = ax.boxplot(data, labels=names, patch_artist=True,
                        boxprops=dict(facecolor="#dcad73", edgecolor="#6d132a"),
                        medianprops=dict(color="#6d132a", linewidth=2))
        ax.set_title(f"{vc} by {gc}")
        ax.tick_params(axis="x", rotation=30)
        self.figure.tight_layout()
        self.canvas.draw()


class CorrelationPanel(ToolPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__("Correlation",
                         "Pearson and Spearman correlation with scatter plot.", parent)
        self.data_handler = data_handler
        self.x = QComboBox(); self.y = QComboBox()
        self.add_control("X", self.x); self.add_control("Y", self.y)
        refresh = QPushButton("Refresh columns")
        refresh.clicked.connect(self._refresh)
        self.add_control("", refresh)
        self._refresh()
        self.set_run_handler(self._run)

    def _refresh(self) -> None:
        df = self.data_handler.dataframe()
        if df is None: return
        num = [c for c in df.columns if np.issubdtype(df[c].dtype, np.number)]
        self.x.clear(); self.x.addItems(num)
        self.y.clear(); self.y.addItems(num)

    def _run(self) -> None:
        df = self.data_handler.dataframe()
        if df is None: self.show_error("Load a dataset first."); return
        xname, yname = self.x.currentText(), self.y.currentText()
        r = se.correlation(df[xname], df[yname])
        viz.draw_scatter(self.figure, df[xname], df[yname], xname, yname,
                         title=f"{xname} vs {yname}")
        self.canvas.draw()
        self.results_text.setHtml(
            f"<p>n = {r.n}</p>"
            f"<p>Pearson r = {r.pearson_r:.4f} · p = {r.pearson_p:.4g}</p>"
            f"<p>Spearman ρ = {r.spearman_r:.4f} · p = {r.spearman_p:.4g}</p>"
        )


class ParetoPanel(ToolPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(
            "Pareto Chart",
            "Enter a grouping column and a count column (or leave count empty to tally).",
            parent,
        )
        self.data_handler = data_handler
        self.cat = QComboBox()
        self.cnt = QComboBox()
        self.add_control("Category", self.cat)
        self.add_control("Count column (optional)", self.cnt)
        refresh = QPushButton("Refresh columns")
        refresh.clicked.connect(self._refresh)
        self.add_control("", refresh)
        self._refresh()
        self.set_run_handler(self._run)

    def _refresh(self) -> None:
        df = self.data_handler.dataframe()
        if df is None: return
        self.cat.clear(); self.cat.addItems(df.columns.tolist())
        self.cnt.clear(); self.cnt.addItem(""); self.cnt.addItems(df.columns.tolist())

    def _run(self) -> None:
        df = self.data_handler.dataframe()
        if df is None: self.show_error("Load a dataset first."); return
        cat = self.cat.currentText()
        cnt = self.cnt.currentText()
        if cnt:
            table = se.pareto_table(df[cat], df[cnt])
        else:
            counts = df[cat].value_counts().reset_index()
            counts.columns = [cat, "count"]
            table = se.pareto_table(counts[cat], counts["count"])
        viz.draw_pareto(self.figure, table, title=f"Pareto — {cat}")
        self.canvas.draw()
        self.results_text.setHtml("<h3>Pareto Table</h3>" + df_to_html(table.round(2)))


class SwimLanePanel(ToolPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(
            "Swim Lane Diagram",
            "Enter lane names as the first column of each line, steps separated by '|'.",
            parent,
        )
        from PySide6.QtWidgets import QPlainTextEdit
        self.text = QPlainTextEdit()
        self.text.setPlaceholderText(
            "Intake | Receive filing | Review docket\n"
            "Clerk | Assign case | Notify counsel"
        )
        self.add_control("Lanes", self.text)
        self.set_run_handler(self._run)

    def _run(self) -> None:
        lanes: dict[str, list[str]] = {}
        for line in self.text.toPlainText().splitlines():
            if "|" not in line:
                continue
            parts = [p.strip() for p in line.split("|")]
            lanes[parts[0]] = parts[1:]
        if not lanes:
            self.show_error("Enter at least one lane."); return
        process_diagrams.draw_swim_lane(self.figure, lanes)
        self.canvas.draw()
        self.results_text.setHtml(f"<p>{len(lanes)} lanes rendered.</p>")


class VSMPanel(ToolPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(
            "Value Stream Map",
            "One step per line: 'Name, cycle_time, wait_time'.",
            parent,
        )
        from PySide6.QtWidgets import QPlainTextEdit
        self.text = QPlainTextEdit()
        self.text.setPlaceholderText("Intake, 2.0, 5.0\nReview, 3.5, 12.0\nDocketing, 1.5, 2.0")
        self.add_control("Steps", self.text)
        self.set_run_handler(self._run)

    def _run(self) -> None:
        steps = []
        for line in self.text.toPlainText().splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 3:
                try:
                    steps.append({
                        "name": parts[0],
                        "cycle_time": float(parts[1]),
                        "wait_time": float(parts[2]),
                    })
                except ValueError:
                    continue
        if not steps:
            self.show_error("Enter at least one step."); return
        process_diagrams.draw_vsm(self.figure, steps)
        self.canvas.draw()
        total_ct = sum(s["cycle_time"] for s in steps)
        total_wait = sum(s["wait_time"] for s in steps)
        total = total_ct + total_wait
        pce = 100 * total_ct / total if total else 0
        self.results_text.setHtml(
            f"<p>Total cycle: {total_ct:.2f} · Total wait: {total_wait:.2f} · "
            f"PCE: {pce:.2f}%</p>"
        )


class FishbonePanel(ToolPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(
            "Fishbone (Ishikawa)",
            "Enter categories. Sub-causes go after a colon, comma-separated.",
            parent,
        )
        from PySide6.QtWidgets import QPlainTextEdit
        self.effect = QLineEdit("Delayed case processing")
        self.text = QPlainTextEdit()
        self.text.setPlaceholderText(
            "People: staffing gaps, training\n"
            "Process: rework, handoff delay\n"
            "Systems: filing system latency\n"
            "Policy: ambiguous local rule"
        )
        self.add_control("Effect", self.effect)
        self.add_control("Categories", self.text)
        self.set_run_handler(self._run)

    def _run(self) -> None:
        causes: dict[str, list[str]] = {}
        for line in self.text.toPlainText().splitlines():
            if ":" in line:
                cat, subs = line.split(":", 1)
                causes[cat.strip()] = [s.strip() for s in subs.split(",") if s.strip()]
        if not causes:
            self.show_error("Enter at least one category."); return
        process_diagrams.draw_fishbone(self.figure, self.effect.text(), causes)
        self.canvas.draw()
        self.results_text.setHtml(f"<p>{len(causes)} categories rendered.</p>")


# ---------------------------------------------------------------------------
# Improve phase
# ---------------------------------------------------------------------------
class ROICalculatorPanel(ToolPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(
            "ROI Calculator",
            "Compute return on investment for process improvement initiatives.",
            parent,
        )
        self.benefit = make_double_spin(100000, 0, 1e12, 1000, 2)
        self.cost = make_double_spin(25000, 0, 1e12, 1000, 2)
        self.years = make_int_spin(3, 1, 30)
        self.add_control("Annual benefit ($)", self.benefit)
        self.add_control("Implementation cost ($)", self.cost)
        self.add_control("Time horizon (years)", self.years)
        self.set_run_handler(self._run)

    def _run(self) -> None:
        benefit = self.benefit.value()
        cost = self.cost.value()
        years = self.years.value()
        total_benefit = benefit * years
        net = total_benefit - cost
        roi = 100 * net / cost if cost else float("inf")
        payback = cost / benefit if benefit else float("inf")
        self.results_text.setHtml(
            f"<p>Total benefit: ${total_benefit:,.2f}</p>"
            f"<p>Implementation cost: ${cost:,.2f}</p>"
            f"<p>Net: ${net:,.2f}</p>"
            f"<p><b>ROI: {roi:.1f}%</b></p>"
            f"<p>Payback period: {payback:.2f} years</p>"
        )
        self.figure.clear()
        ax = self.figure.add_subplot(1, 1, 1)
        yr = np.arange(0, years + 1)
        cumulative = yr * benefit - cost
        ax.plot(yr, cumulative, marker="o", color="#6d132a", linewidth=2)
        ax.axhline(0, color="#b2b2b2")
        ax.set_xlabel("Year"); ax.set_ylabel("Cumulative Net Benefit ($)")
        ax.set_title("ROI — Cumulative Net Benefit")
        ax.grid(True, linestyle=":", alpha=0.6)
        self.figure.tight_layout()
        self.canvas.draw()


# ---------------------------------------------------------------------------
# Control phase
# ---------------------------------------------------------------------------
class ControlChartReviewPanel(_SingleColumnPanel):
    def __init__(self, data_handler, license_manager, parent=None):
        super().__init__(
            data_handler, license_manager,
            "Control Chart Review",
            "Post-control monitoring: apply Western Electric rules to recent data.",
            parent,
        )
        self.window = make_int_spin(30, 5, 10000)
        self.add_control("Recent observations", self.window)
        self.set_run_handler(self._run)

    def _run(self) -> None:
        arr = self._arr()
        if arr is None:
            return
        window = min(self.window.value(), arr.size)
        recent = arr[-window:]
        result = se.xmr_chart(recent)
        viz.draw_xmr(self.figure, result, label=self.col.currentText())
        self.canvas.draw()
        if result.signals:
            html = "<h3>Rule signals in recent window</h3><ul>"
            for s in result.signals:
                html += f"<li>Point {s['index']+1}: Rule {s['rule']} — {s['description']}</li>"
            html += "</ul>"
            html += "<p><b>Action:</b> investigate assignable causes before taking corrective action.</p>"
        else:
            html = "<p>No Western Electric rule signals in the recent window. Process appears stable.</p>"
        self.results_text.setHtml(html)
