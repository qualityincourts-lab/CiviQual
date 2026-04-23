"""
CiviQual Stats Chart Editor

Provides interactive chart customization including:
- Horizontal and vertical reference lines
- Text annotations
- Specification limits
- Shaded regions
- Color customization
- Export options (PNG, SVG, PDF)

Copyright (c) 2026 A Step in the Right Direction LLC
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QDialog, QDialogButtonBox,
    QPushButton, QLabel, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QCheckBox, QColorDialog, QFileDialog, QListWidget, QListWidgetItem,
    QTabWidget, QFormLayout, QGroupBox, QScrollArea, QMessageBox,
    QSplitter, QTextEdit, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QIcon


class LineStyle(Enum):
    """Line style options."""
    SOLID = '-'
    DASHED = '--'
    DOTTED = ':'
    DASHDOT = '-.'


class LineType(Enum):
    """Types of reference lines."""
    HORIZONTAL = 'horizontal'
    VERTICAL = 'vertical'


@dataclass
class ReferenceLine:
    """A reference line on the chart."""
    line_type: LineType
    value: float
    label: str = ''
    color: str = '#8B1538'  # Brand burgundy
    line_style: LineStyle = LineStyle.DASHED
    line_width: float = 1.5
    show_label: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'line_type': self.line_type.value,
            'value': self.value,
            'label': self.label,
            'color': self.color,
            'line_style': self.line_style.value,
            'line_width': self.line_width,
            'show_label': self.show_label
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReferenceLine':
        return cls(
            line_type=LineType(data['line_type']),
            value=data['value'],
            label=data.get('label', ''),
            color=data.get('color', '#8B1538'),
            line_style=LineStyle(data.get('line_style', '-')),
            line_width=data.get('line_width', 1.5),
            show_label=data.get('show_label', True)
        )


@dataclass
class Annotation:
    """A text annotation on the chart."""
    x: float
    y: float
    text: str
    color: str = '#333333'
    font_size: int = 10
    background: bool = True
    arrow: bool = False
    arrow_target_x: float = 0.0
    arrow_target_y: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'x': self.x,
            'y': self.y,
            'text': self.text,
            'color': self.color,
            'font_size': self.font_size,
            'background': self.background,
            'arrow': self.arrow,
            'arrow_target_x': self.arrow_target_x,
            'arrow_target_y': self.arrow_target_y
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Annotation':
        return cls(**data)


@dataclass
class ShadedRegion:
    """A shaded region on the chart."""
    orientation: str = 'vertical'  # 'vertical' or 'horizontal'
    start: float = 0.0
    end: float = 0.0
    color: str = '#FFE4E9'  # Light pink
    alpha: float = 0.3
    label: str = ''
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'orientation': self.orientation,
            'start': self.start,
            'end': self.end,
            'color': self.color,
            'alpha': self.alpha,
            'label': self.label
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ShadedRegion':
        return cls(**data)


@dataclass 
class ChartCustomization:
    """All customizations for a chart."""
    title: str = ''
    subtitle: str = ''
    x_label: str = ''
    y_label: str = ''
    reference_lines: List[ReferenceLine] = field(default_factory=list)
    annotations: List[Annotation] = field(default_factory=list)
    shaded_regions: List[ShadedRegion] = field(default_factory=list)
    show_legend: bool = True
    legend_position: str = 'best'
    grid: bool = True
    grid_alpha: float = 0.3
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'subtitle': self.subtitle,
            'x_label': self.x_label,
            'y_label': self.y_label,
            'reference_lines': [line.to_dict() for line in self.reference_lines],
            'annotations': [ann.to_dict() for ann in self.annotations],
            'shaded_regions': [region.to_dict() for region in self.shaded_regions],
            'show_legend': self.show_legend,
            'legend_position': self.legend_position,
            'grid': self.grid,
            'grid_alpha': self.grid_alpha
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChartCustomization':
        return cls(
            title=data.get('title', ''),
            subtitle=data.get('subtitle', ''),
            x_label=data.get('x_label', ''),
            y_label=data.get('y_label', ''),
            reference_lines=[ReferenceLine.from_dict(d) for d in data.get('reference_lines', [])],
            annotations=[Annotation.from_dict(d) for d in data.get('annotations', [])],
            shaded_regions=[ShadedRegion.from_dict(d) for d in data.get('shaded_regions', [])],
            show_legend=data.get('show_legend', True),
            legend_position=data.get('legend_position', 'best'),
            grid=data.get('grid', True),
            grid_alpha=data.get('grid_alpha', 0.3)
        )
    
    def clear(self) -> None:
        """Clear all customizations."""
        self.reference_lines.clear()
        self.annotations.clear()
        self.shaded_regions.clear()


class ChartEditor(QWidget):
    """
    Widget for editing chart customizations.
    
    Provides UI for adding/removing reference lines, annotations,
    shaded regions, and other chart customizations.
    """
    
    customization_changed = Signal()
    
    # Brand colors
    BRAND_BURGUNDY = '#8B1538'
    BRAND_GOLD = '#C5A572'
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.customization = ChartCustomization()
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the editor UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Tab widget for different customization types
        tabs = QTabWidget()
        tabs.setAccessibleName("Chart customization tabs")
        
        # Reference Lines tab
        ref_lines_tab = self._create_reference_lines_tab()
        tabs.addTab(ref_lines_tab, "Reference Lines")
        
        # Annotations tab
        annotations_tab = self._create_annotations_tab()
        tabs.addTab(annotations_tab, "Annotations")
        
        # Regions tab
        regions_tab = self._create_regions_tab()
        tabs.addTab(regions_tab, "Shaded Regions")
        
        # Labels tab
        labels_tab = self._create_labels_tab()
        tabs.addTab(labels_tab, "Labels")
        
        layout.addWidget(tabs)
        
        # Apply button
        apply_btn = QPushButton("Apply Changes")
        apply_btn.clicked.connect(self._apply_changes)
        apply_btn.setStyleSheet(f"background-color: {self.BRAND_BURGUNDY}; color: white; padding: 8px;")
        layout.addWidget(apply_btn)
    
    def _create_reference_lines_tab(self) -> QWidget:
        """Create the reference lines tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Add line controls
        add_group = QGroupBox("Add Reference Line")
        add_layout = QFormLayout(add_group)
        
        self.ref_type_combo = QComboBox()
        self.ref_type_combo.addItems(["Horizontal", "Vertical"])
        add_layout.addRow("Type:", self.ref_type_combo)
        
        self.ref_value_spin = QDoubleSpinBox()
        self.ref_value_spin.setRange(-1e9, 1e9)
        self.ref_value_spin.setDecimals(4)
        add_layout.addRow("Value:", self.ref_value_spin)
        
        self.ref_label_edit = QLineEdit()
        self.ref_label_edit.setPlaceholderText("e.g., Target, LSL, UCL")
        add_layout.addRow("Label:", self.ref_label_edit)
        
        self.ref_color_btn = QPushButton("Select Color")
        self.ref_color_btn.setStyleSheet(f"background-color: {self.BRAND_BURGUNDY};")
        self.ref_color_btn.clicked.connect(self._select_ref_line_color)
        self._ref_line_color = self.BRAND_BURGUNDY
        add_layout.addRow("Color:", self.ref_color_btn)
        
        self.ref_style_combo = QComboBox()
        self.ref_style_combo.addItems(["Dashed", "Solid", "Dotted", "Dash-Dot"])
        add_layout.addRow("Style:", self.ref_style_combo)
        
        add_btn = QPushButton("Add Line")
        add_btn.clicked.connect(self._add_reference_line)
        add_layout.addRow("", add_btn)
        
        layout.addWidget(add_group)
        
        # List of existing lines
        list_group = QGroupBox("Current Lines")
        list_layout = QVBoxLayout(list_group)
        
        self.ref_lines_list = QListWidget()
        self.ref_lines_list.setAccessibleName("Reference lines list")
        list_layout.addWidget(self.ref_lines_list)
        
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self._remove_reference_line)
        list_layout.addWidget(remove_btn)
        
        layout.addWidget(list_group)
        
        return widget
    
    def _create_annotations_tab(self) -> QWidget:
        """Create the annotations tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Add annotation controls
        add_group = QGroupBox("Add Annotation")
        add_layout = QFormLayout(add_group)
        
        self.ann_x_spin = QDoubleSpinBox()
        self.ann_x_spin.setRange(-1e9, 1e9)
        self.ann_x_spin.setDecimals(4)
        add_layout.addRow("X Position:", self.ann_x_spin)
        
        self.ann_y_spin = QDoubleSpinBox()
        self.ann_y_spin.setRange(-1e9, 1e9)
        self.ann_y_spin.setDecimals(4)
        add_layout.addRow("Y Position:", self.ann_y_spin)
        
        self.ann_text_edit = QLineEdit()
        self.ann_text_edit.setPlaceholderText("Annotation text")
        add_layout.addRow("Text:", self.ann_text_edit)
        
        self.ann_fontsize_spin = QSpinBox()
        self.ann_fontsize_spin.setRange(6, 24)
        self.ann_fontsize_spin.setValue(10)
        add_layout.addRow("Font Size:", self.ann_fontsize_spin)
        
        self.ann_background_check = QCheckBox("Show Background")
        self.ann_background_check.setChecked(True)
        add_layout.addRow("", self.ann_background_check)
        
        add_btn = QPushButton("Add Annotation")
        add_btn.clicked.connect(self._add_annotation)
        add_layout.addRow("", add_btn)
        
        layout.addWidget(add_group)
        
        # List of existing annotations
        list_group = QGroupBox("Current Annotations")
        list_layout = QVBoxLayout(list_group)
        
        self.annotations_list = QListWidget()
        self.annotations_list.setAccessibleName("Annotations list")
        list_layout.addWidget(self.annotations_list)
        
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self._remove_annotation)
        list_layout.addWidget(remove_btn)
        
        layout.addWidget(list_group)
        
        return widget
    
    def _create_regions_tab(self) -> QWidget:
        """Create the shaded regions tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Add region controls
        add_group = QGroupBox("Add Shaded Region")
        add_layout = QFormLayout(add_group)
        
        self.region_orient_combo = QComboBox()
        self.region_orient_combo.addItems(["Vertical (X range)", "Horizontal (Y range)"])
        add_layout.addRow("Orientation:", self.region_orient_combo)
        
        self.region_start_spin = QDoubleSpinBox()
        self.region_start_spin.setRange(-1e9, 1e9)
        self.region_start_spin.setDecimals(4)
        add_layout.addRow("Start:", self.region_start_spin)
        
        self.region_end_spin = QDoubleSpinBox()
        self.region_end_spin.setRange(-1e9, 1e9)
        self.region_end_spin.setDecimals(4)
        add_layout.addRow("End:", self.region_end_spin)
        
        self.region_color_btn = QPushButton("Select Color")
        self.region_color_btn.setStyleSheet("background-color: #FFE4E9;")
        self.region_color_btn.clicked.connect(self._select_region_color)
        self._region_color = '#FFE4E9'
        add_layout.addRow("Color:", self.region_color_btn)
        
        self.region_alpha_spin = QDoubleSpinBox()
        self.region_alpha_spin.setRange(0.0, 1.0)
        self.region_alpha_spin.setDecimals(2)
        self.region_alpha_spin.setValue(0.3)
        self.region_alpha_spin.setSingleStep(0.1)
        add_layout.addRow("Opacity:", self.region_alpha_spin)
        
        self.region_label_edit = QLineEdit()
        self.region_label_edit.setPlaceholderText("e.g., Out of Spec")
        add_layout.addRow("Label:", self.region_label_edit)
        
        add_btn = QPushButton("Add Region")
        add_btn.clicked.connect(self._add_region)
        add_layout.addRow("", add_btn)
        
        layout.addWidget(add_group)
        
        # List of existing regions
        list_group = QGroupBox("Current Regions")
        list_layout = QVBoxLayout(list_group)
        
        self.regions_list = QListWidget()
        self.regions_list.setAccessibleName("Shaded regions list")
        list_layout.addWidget(self.regions_list)
        
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self._remove_region)
        list_layout.addWidget(remove_btn)
        
        layout.addWidget(list_group)
        
        return widget
    
    def _create_labels_tab(self) -> QWidget:
        """Create the labels/titles tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        form_layout = QFormLayout()
        
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Chart title")
        form_layout.addRow("Title:", self.title_edit)
        
        self.subtitle_edit = QLineEdit()
        self.subtitle_edit.setPlaceholderText("Subtitle (optional)")
        form_layout.addRow("Subtitle:", self.subtitle_edit)
        
        self.x_label_edit = QLineEdit()
        self.x_label_edit.setPlaceholderText("X-axis label")
        form_layout.addRow("X Label:", self.x_label_edit)
        
        self.y_label_edit = QLineEdit()
        self.y_label_edit.setPlaceholderText("Y-axis label")
        form_layout.addRow("Y Label:", self.y_label_edit)
        
        layout.addLayout(form_layout)
        
        # Legend options
        legend_group = QGroupBox("Legend")
        legend_layout = QFormLayout(legend_group)
        
        self.show_legend_check = QCheckBox("Show Legend")
        self.show_legend_check.setChecked(True)
        legend_layout.addRow("", self.show_legend_check)
        
        self.legend_pos_combo = QComboBox()
        self.legend_pos_combo.addItems([
            "Best", "Upper Right", "Upper Left", "Lower Right", 
            "Lower Left", "Right", "Center Left", "Center Right",
            "Lower Center", "Upper Center", "Center"
        ])
        legend_layout.addRow("Position:", self.legend_pos_combo)
        
        layout.addWidget(legend_group)
        
        # Grid options
        grid_group = QGroupBox("Grid")
        grid_layout = QFormLayout(grid_group)
        
        self.show_grid_check = QCheckBox("Show Grid")
        self.show_grid_check.setChecked(True)
        grid_layout.addRow("", self.show_grid_check)
        
        self.grid_alpha_spin = QDoubleSpinBox()
        self.grid_alpha_spin.setRange(0.0, 1.0)
        self.grid_alpha_spin.setDecimals(2)
        self.grid_alpha_spin.setValue(0.3)
        self.grid_alpha_spin.setSingleStep(0.1)
        grid_layout.addRow("Grid Opacity:", self.grid_alpha_spin)
        
        layout.addWidget(grid_group)
        
        layout.addStretch()
        
        return widget
    
    def _select_ref_line_color(self):
        """Open color dialog for reference line."""
        color = QColorDialog.getColor(QColor(self._ref_line_color), self, "Select Line Color")
        if color.isValid():
            self._ref_line_color = color.name()
            self.ref_color_btn.setStyleSheet(f"background-color: {self._ref_line_color};")
    
    def _select_region_color(self):
        """Open color dialog for shaded region."""
        color = QColorDialog.getColor(QColor(self._region_color), self, "Select Region Color")
        if color.isValid():
            self._region_color = color.name()
            self.region_color_btn.setStyleSheet(f"background-color: {self._region_color};")
    
    def _add_reference_line(self):
        """Add a new reference line."""
        line_type = LineType.HORIZONTAL if self.ref_type_combo.currentIndex() == 0 else LineType.VERTICAL
        
        style_map = {0: LineStyle.DASHED, 1: LineStyle.SOLID, 2: LineStyle.DOTTED, 3: LineStyle.DASHDOT}
        line_style = style_map.get(self.ref_style_combo.currentIndex(), LineStyle.DASHED)
        
        line = ReferenceLine(
            line_type=line_type,
            value=self.ref_value_spin.value(),
            label=self.ref_label_edit.text(),
            color=self._ref_line_color,
            line_style=line_style
        )
        
        self.customization.reference_lines.append(line)
        self._update_ref_lines_list()
        self.ref_label_edit.clear()
    
    def _remove_reference_line(self):
        """Remove selected reference line."""
        row = self.ref_lines_list.currentRow()
        if row >= 0 and row < len(self.customization.reference_lines):
            self.customization.reference_lines.pop(row)
            self._update_ref_lines_list()
    
    def _update_ref_lines_list(self):
        """Update the reference lines list widget."""
        self.ref_lines_list.clear()
        for line in self.customization.reference_lines:
            type_str = "H" if line.line_type == LineType.HORIZONTAL else "V"
            label = f" ({line.label})" if line.label else ""
            self.ref_lines_list.addItem(f"{type_str}: {line.value:.4f}{label}")
    
    def _add_annotation(self):
        """Add a new annotation."""
        ann = Annotation(
            x=self.ann_x_spin.value(),
            y=self.ann_y_spin.value(),
            text=self.ann_text_edit.text(),
            font_size=self.ann_fontsize_spin.value(),
            background=self.ann_background_check.isChecked()
        )
        
        self.customization.annotations.append(ann)
        self._update_annotations_list()
        self.ann_text_edit.clear()
    
    def _remove_annotation(self):
        """Remove selected annotation."""
        row = self.annotations_list.currentRow()
        if row >= 0 and row < len(self.customization.annotations):
            self.customization.annotations.pop(row)
            self._update_annotations_list()
    
    def _update_annotations_list(self):
        """Update the annotations list widget."""
        self.annotations_list.clear()
        for ann in self.customization.annotations:
            text_preview = ann.text[:20] + "..." if len(ann.text) > 20 else ann.text
            self.annotations_list.addItem(f"({ann.x:.2f}, {ann.y:.2f}): {text_preview}")
    
    def _add_region(self):
        """Add a new shaded region."""
        orientation = 'vertical' if self.region_orient_combo.currentIndex() == 0 else 'horizontal'
        
        region = ShadedRegion(
            orientation=orientation,
            start=self.region_start_spin.value(),
            end=self.region_end_spin.value(),
            color=self._region_color,
            alpha=self.region_alpha_spin.value(),
            label=self.region_label_edit.text()
        )
        
        self.customization.shaded_regions.append(region)
        self._update_regions_list()
        self.region_label_edit.clear()
    
    def _remove_region(self):
        """Remove selected region."""
        row = self.regions_list.currentRow()
        if row >= 0 and row < len(self.customization.shaded_regions):
            self.customization.shaded_regions.pop(row)
            self._update_regions_list()
    
    def _update_regions_list(self):
        """Update the regions list widget."""
        self.regions_list.clear()
        for region in self.customization.shaded_regions:
            orient = "V" if region.orientation == 'vertical' else "H"
            label = f" ({region.label})" if region.label else ""
            self.regions_list.addItem(f"{orient}: {region.start:.2f} to {region.end:.2f}{label}")
    
    def _apply_changes(self):
        """Apply label changes and emit signal."""
        self.customization.title = self.title_edit.text()
        self.customization.subtitle = self.subtitle_edit.text()
        self.customization.x_label = self.x_label_edit.text()
        self.customization.y_label = self.y_label_edit.text()
        self.customization.show_legend = self.show_legend_check.isChecked()
        
        pos_map = {
            0: 'best', 1: 'upper right', 2: 'upper left', 3: 'lower right',
            4: 'lower left', 5: 'right', 6: 'center left', 7: 'center right',
            8: 'lower center', 9: 'upper center', 10: 'center'
        }
        self.customization.legend_position = pos_map.get(self.legend_pos_combo.currentIndex(), 'best')
        
        self.customization.grid = self.show_grid_check.isChecked()
        self.customization.grid_alpha = self.grid_alpha_spin.value()
        
        self.customization_changed.emit()
    
    def get_customization(self) -> ChartCustomization:
        """Get the current customization settings."""
        return self.customization
    
    def set_customization(self, customization: ChartCustomization):
        """Set customization settings."""
        self.customization = customization
        self._update_ui_from_customization()
    
    def _update_ui_from_customization(self):
        """Update UI controls from customization object."""
        self.title_edit.setText(self.customization.title)
        self.subtitle_edit.setText(self.customization.subtitle)
        self.x_label_edit.setText(self.customization.x_label)
        self.y_label_edit.setText(self.customization.y_label)
        self.show_legend_check.setChecked(self.customization.show_legend)
        self.show_grid_check.setChecked(self.customization.grid)
        self.grid_alpha_spin.setValue(self.customization.grid_alpha)
        
        self._update_ref_lines_list()
        self._update_annotations_list()
        self._update_regions_list()
    
    def clear(self):
        """Clear all customizations."""
        self.customization.clear()
        self.title_edit.clear()
        self.subtitle_edit.clear()
        self.x_label_edit.clear()
        self.y_label_edit.clear()
        self._update_ref_lines_list()
        self._update_annotations_list()
        self._update_regions_list()


def apply_customization_to_axes(ax, customization: ChartCustomization):
    """
    Apply customization settings to a matplotlib axes object.
    
    Args:
        ax: Matplotlib axes object
        customization: ChartCustomization settings to apply
    """
    # Apply title and labels
    if customization.title:
        ax.set_title(customization.title, fontsize=14, fontweight='bold', color='#8B1538')
    if customization.x_label:
        ax.set_xlabel(customization.x_label)
    if customization.y_label:
        ax.set_ylabel(customization.y_label)
    
    # Apply reference lines
    for line in customization.reference_lines:
        if line.line_type == LineType.HORIZONTAL:
            ax.axhline(line.value, color=line.color, linestyle=line.line_style.value,
                      linewidth=line.line_width, label=line.label if line.show_label else None)
        else:
            ax.axvline(line.value, color=line.color, linestyle=line.line_style.value,
                      linewidth=line.line_width, label=line.label if line.show_label else None)
    
    # Apply shaded regions
    for region in customization.shaded_regions:
        if region.orientation == 'vertical':
            ax.axvspan(region.start, region.end, color=region.color, alpha=region.alpha,
                      label=region.label if region.label else None)
        else:
            ax.axhspan(region.start, region.end, color=region.color, alpha=region.alpha,
                      label=region.label if region.label else None)
    
    # Apply annotations
    for ann in customization.annotations:
        bbox_props = dict(boxstyle='round,pad=0.3', facecolor='white', 
                         edgecolor='gray', alpha=0.8) if ann.background else None
        ax.annotate(ann.text, xy=(ann.x, ann.y), fontsize=ann.font_size,
                   color=ann.color, bbox=bbox_props)
    
    # Apply grid settings
    ax.grid(customization.grid, alpha=customization.grid_alpha)
    
    # Apply legend
    if customization.show_legend:
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(loc=customization.legend_position)


class ChartExporter:
    """Handles exporting charts to various formats."""
    
    @staticmethod
    def export_png(fig: Figure, filepath: str, dpi: int = 300):
        """Export chart to PNG format."""
        fig.savefig(filepath, format='png', dpi=dpi, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
    
    @staticmethod
    def export_svg(fig: Figure, filepath: str):
        """Export chart to SVG format."""
        fig.savefig(filepath, format='svg', bbox_inches='tight')
    
    @staticmethod
    def export_pdf(fig: Figure, filepath: str):
        """Export chart to PDF format."""
        fig.savefig(filepath, format='pdf', bbox_inches='tight')
    
    @staticmethod
    def show_export_dialog(parent, fig: Figure, default_name: str = 'chart'):
        """Show export dialog and save chart."""
        filepath, filter_used = QFileDialog.getSaveFileName(
            parent,
            "Export Chart",
            f"{default_name}.png",
            "PNG Image (*.png);;SVG Vector (*.svg);;PDF Document (*.pdf);;All Files (*)"
        )
        
        if not filepath:
            return False
        
        try:
            ext = Path(filepath).suffix.lower()
            if ext == '.svg':
                ChartExporter.export_svg(fig, filepath)
            elif ext == '.pdf':
                ChartExporter.export_pdf(fig, filepath)
            else:
                ChartExporter.export_png(fig, filepath)
            
            QMessageBox.information(parent, "Export Complete",
                                   f"Chart exported successfully to:\n{filepath}")
            return True
            
        except Exception as e:
            QMessageBox.critical(parent, "Export Error",
                               f"Could not export chart:\n{str(e)}")
            return False
