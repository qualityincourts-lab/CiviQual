#!/usr/bin/env python3
"""
CiviQual Stats - Statistical Process Control for Public-Sector Quality Management

Version 2.0.0 - DMAIC Edition

A statistical analysis tool for Lean Six Sigma practitioners in government.
Part of the CiviQual Suite family of quality management tools.

Copyright (c) 2026 A Step in the Right Direction LLC
All Rights Reserved.

Features:
- Section 508 accessibility compliance
- DMAIC phase-organized interface
- Yellow Belt and basic Green Belt statistical tools (Free tier)
- Advanced Green Belt and Black Belt tools (CiviQual Stats Pro)
- Project session save/resume (Pro)
"""

import sys
import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QFileDialog, QLabel, QComboBox,
    QTableWidget, QTableWidgetItem, QGroupBox, QFormLayout,
    QLineEdit, QSpinBox, QDoubleSpinBox, QMessageBox, QScrollArea,
    QSplitter, QTextEdit, QCheckBox, QStatusBar, QMenuBar, QMenu,
    QDialog, QDialogButtonBox, QGridLayout, QRadioButton, QButtonGroup,
    QTextBrowser, QFrame, QListWidget, QAbstractItemView, QStackedWidget,
    QToolBar, QSizePolicy, QProgressBar, QSlider, QInputDialog
)
from PySide6.QtCore import Qt, QSize, QStandardPaths, QTimer, Signal, QSettings
from PySide6.QtGui import (
    QAction, QFont, QIcon, QColor, QPixmap, QPainter, QPen, QBrush,
    QKeySequence, QShortcut, QActionGroup
)

import pandas as pd
import numpy as np

# Core modules
from statistics_engine import StatisticsEngine
from visualizations import VisualizationEngine
from report_generator import ReportGenerator
from data_handler import DataHandler
from process_diagrams import ProcessDiagramEngine
from license_manager import LicenseManager

# Pro modules (gated by license)
from msa import MSA
from doe import DOE
from hypothesis_tests import HypothesisTests
from sample_size import SampleSizeCalculator
from advanced_capability import AdvancedCapability
from multiple_regression import MultipleRegression
from advanced_control_charts import AdvancedControlCharts
from lean_calculators import LeanCalculators
from root_cause_tools import FishboneBuilder, FiveWhysBuilder
from solution_tools import PughMatrix, ImpactEffortMatrix
from planning_tools import FMEA, ControlPlan
from data_tools import OutlierDetection, MissingDataAnalysis
from chart_editor import ChartEditor


# =============================================================================
# Version Information
# =============================================================================
VERSION = "2.0.0"
VERSION_NAME = "DMAIC Edition"
VERSION_DATE = "April 2026"

# =============================================================================
# Application Constants
# =============================================================================
APP_NAME = "CiviQual Stats"
ORG_NAME = "A Step in the Right Direction LLC"
ORG_DOMAIN = "qualityincourts.com"

# Color scheme
COLOR_BURGUNDY = "#6d132a"
COLOR_GOLD = "#dcad73"
COLOR_BURGUNDY_DARK = "#4a0919"

# DMAIC Phase definitions
DMAIC_PHASES = {
    "Define": {
        "shortcut": "Alt+D",
        "description": "Define the problem and project scope",
        "free_tools": ["SIPOC Diagram", "Process Map", "RACI Matrix", "Data Sampling", "Split Worksheet"],
        "pro_tools": []
    },
    "Measure": {
        "shortcut": "Alt+M",
        "description": "Measure current performance",
        "free_tools": ["4-Up Chart", "Descriptive Statistics", "Control Charts", "Capability Analysis", 
                       "Probability Plot", "Histogram", "Box Plot", "Run Chart"],
        "pro_tools": ["★ MSA (Gage R&R)", "★ Sample Size Calculator", "★ Advanced Capability"]
    },
    "Analyze": {
        "shortcut": "Alt+A",
        "description": "Analyze root causes",
        "free_tools": ["ANOVA", "Correlation", "Pareto Analysis", "Swim Lane Diagram", 
                       "Value Stream Map", "Fishbone Diagram"],
        "pro_tools": ["★ Hypothesis Tests", "★ Design of Experiments", "★ Multiple Regression",
                      "★ Root Cause Tools", "★ Data Tools"]
    },
    "Improve": {
        "shortcut": "Alt+I",
        "description": "Improve the process",
        "free_tools": ["ROI Calculator"],
        "pro_tools": ["★ Solution Tools", "★ Lean Calculators"]
    },
    "Control": {
        "shortcut": "Alt+C",
        "description": "Control and sustain gains",
        "free_tools": ["Control Chart Review"],
        "pro_tools": ["★ CUSUM/EWMA Charts", "★ Planning Tools", "★ Chart Editor"]
    }
}

# Project file extension
PROJECT_EXTENSION = ".civiqual"
PROJECT_FILTER = f"CiviQual Project (*{PROJECT_EXTENSION})"

# Settings keys
SETTINGS_RECENT_FILES = "recent_files"
SETTINGS_RECENT_PROJECTS = "recent_projects"
SETTINGS_WINDOW_GEOMETRY = "window_geometry"
SETTINGS_WINDOW_STATE = "window_state"
SETTINGS_LICENSE_ACCEPTED = "license_accepted"
SETTINGS_AUTO_SAVE = "auto_save_enabled"
SETTINGS_AUTO_SAVE_INTERVAL = "auto_save_interval"

MAX_RECENT_FILES = 10
MAX_RECENT_PROJECTS = 5
AUTO_SAVE_INTERVAL_DEFAULT = 300000  # 5 minutes in milliseconds


# =============================================================================
# Configuration Management
# =============================================================================
def get_config_dir() -> Path:
    """Get the configuration directory path."""
    if sys.platform == "win32":
        config_dir = Path(os.environ.get("LOCALAPPDATA", "")) / "CiviQualStats"
    else:
        config_dir = Path.home() / ".civiqual"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_auto_save_dir() -> Path:
    """Get the auto-save directory path."""
    auto_save_dir = get_config_dir() / "AutoSave"
    auto_save_dir.mkdir(parents=True, exist_ok=True)
    return auto_save_dir


def load_config() -> dict:
    """Load application configuration."""
    config_file = get_config_dir() / "config.json"
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def save_config(config: dict):
    """Save application configuration."""
    config_file = get_config_dir() / "config.json"
    try:
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
    except IOError:
        pass


def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA-256 hash of a file."""
    try:
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except IOError:
        return ""
# =============================================================================
# Splash Screen
# =============================================================================
class SplashScreen(QDialog):
    """Splash screen showing CiviQual Stats branding."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CiviQual Stats")
        self.setFixedSize(500, 400)
        self.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(f"""
            QDialog {{ background-color: white; border: 3px solid {COLOR_BURGUNDY}; }}
            QLabel {{ border: none; background: transparent; }}
        """)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(30, 25, 30, 25)
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = self._create_logo()
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)
        
        # Title
        title = QLabel("CiviQual Stats")
        title.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLOR_BURGUNDY};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Statistical Process Control")
        subtitle.setFont(QFont("Arial", 14))
        subtitle.setStyleSheet(f"color: {COLOR_BURGUNDY};")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        # Tagline
        tagline = QLabel("for Public-Sector Quality Management")
        tagline.setFont(QFont("Arial", 10))
        tagline.setStyleSheet("color: #666;")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tagline)
        
        layout.addSpacing(15)
        layout.addStretch()
        
        # Version
        version = QLabel(f"Version {VERSION} — {VERSION_NAME}")
        version.setStyleSheet("color: #666; font-size: 10px;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)
        
        # Copyright
        copyright_label = QLabel(f"© 2026 {ORG_NAME}")
        copyright_label.setStyleSheet("color: #999; font-size: 8px;")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(copyright_label)
    
    def _create_logo(self):
        """Create CiviQual Stats logo with burgundy/gold color scheme."""
        pixmap = QPixmap(80, 80)
        pixmap.fill(QColor(COLOR_BURGUNDY))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # White inner area
        painter.setBrush(QBrush(QColor("white")))
        painter.setPen(QPen(QColor("white")))
        painter.drawRoundedRect(5, 5, 70, 70, 6, 6)
        
        # Burgundy dividing lines (4-Up grid)
        pen = QPen(QColor(COLOR_BURGUNDY))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(40, 8, 40, 72)
        painter.drawLine(8, 40, 72, 40)
        
        # Bar chart in upper-left quadrant
        painter.setBrush(QBrush(QColor(COLOR_BURGUNDY)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(12, 28, 6, 10)
        painter.drawRect(20, 20, 6, 18)
        painter.drawRect(28, 14, 6, 24)
        
        # Bell curve hint in upper-right (gold accent)
        painter.setPen(QPen(QColor(COLOR_GOLD), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(46, 12, 20, 24, 0, 180 * 16)
        
        # Control chart hint in lower-left
        painter.setPen(QPen(QColor(COLOR_BURGUNDY), 2))
        points = [(12, 58), (20, 52), (28, 56), (36, 50)]
        for i in range(len(points) - 1):
            painter.drawLine(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
        
        # Scatter plot hint in lower-right (gold accent)
        painter.setBrush(QBrush(QColor(COLOR_GOLD)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(50, 48, 5, 5)
        painter.drawEllipse(58, 54, 5, 5)
        painter.drawEllipse(54, 62, 5, 5)
        painter.drawEllipse(66, 58, 5, 5)
        
        painter.end()
        return pixmap


# =============================================================================
# License Dialog
# =============================================================================
class LicenseDialog(QDialog):
    """License acceptance dialog shown on first run."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CiviQual Stats License Agreement")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        self.accepted_license = False
        self.dont_show_again = False
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("CiviQual Stats Software License Agreement")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setAccessibleName("License Agreement Title")
        layout.addWidget(title)
        
        # License text
        license_text = QTextBrowser()
        license_text.setAccessibleName("License agreement text")
        license_text.setAccessibleDescription("Please read the license agreement carefully before accepting")
        license_text.setHtml(self._get_license_html())
        layout.addWidget(license_text)
        
        # Don't show again checkbox
        self.dont_show_checkbox = QCheckBox("Do not show this dialog again")
        self.dont_show_checkbox.setAccessibleName("Do not show license dialog again")
        self.dont_show_checkbox.setAccessibleDescription("Check this box to skip this dialog on future launches")
        self.dont_show_checkbox.setToolTip("Check to skip this dialog on future launches")
        layout.addWidget(self.dont_show_checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        decline_btn = QPushButton("Decline")
        decline_btn.setAccessibleName("Decline license agreement")
        decline_btn.setAccessibleDescription("Click to decline the license and exit the application")
        decline_btn.clicked.connect(self._decline)
        button_layout.addWidget(decline_btn)
        
        accept_btn = QPushButton("I Accept")
        accept_btn.setAccessibleName("Accept license agreement")
        accept_btn.setAccessibleDescription("Click to accept the license agreement and continue")
        accept_btn.setDefault(True)
        accept_btn.clicked.connect(self._accept)
        button_layout.addWidget(accept_btn)
        
        layout.addLayout(button_layout)
    
    def _get_license_html(self):
        """Get dual license text as HTML."""
        return f"""
        <style>
            body {{ font-family: Arial, sans-serif; }}
            h3 {{ color: {COLOR_BURGUNDY}; }}
            h4 {{ color: {COLOR_BURGUNDY_DARK}; margin-top: 16px; }}
            .tier {{ background: #f5f5f5; padding: 12px; margin: 8px 0; border-left: 3px solid {COLOR_BURGUNDY}; }}
            .pro {{ border-left-color: {COLOR_GOLD}; }}
        </style>
        
        <h3>CiviQual Stats Dual License</h3>
        <p>Copyright © 2026 {ORG_NAME}. All Rights Reserved.</p>
        
        <h4>License Tiers</h4>
        
        <div class="tier">
            <strong>FREE TIER — Yellow Belt and Basic Green Belt Tools</strong><br>
            Free for government agencies, courts, nonprofits, and educational use.<br>
            Includes: 4-Up Chart, Control Charts, Capability (Cp/Cpk), ANOVA, 
            Pareto, Process Diagrams, and more.
        </div>
        
        <div class="tier pro">
            <strong>PRO TIER — Advanced Green Belt and Black Belt Tools</strong><br>
            Requires paid license. Contact www.{ORG_DOMAIN} for pricing.<br>
            Includes: MSA (Gage R&R), DOE, Hypothesis Tests, Advanced Capability,
            CUSUM/EWMA, Regression, FMEA, and more.
        </div>
        
        <h4>Permitted Use (Free Tier)</h4>
        <ul>
            <li>Government agencies (federal, state, local, tribal)</li>
            <li>Courts and judicial organizations</li>
            <li>Public educational institutions</li>
            <li>501(c)(3) nonprofit organizations</li>
        </ul>
        
        <h4>Restrictions</h4>
        <ul>
            <li>Commercial use of Free tier requires Pro license</li>
            <li>You may not redistribute this software</li>
            <li>You may not reverse engineer or modify this software</li>
        </ul>
        
        <h4>Warranty Disclaimer</h4>
        <p>THE SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND. 
        {ORG_NAME.upper()} SHALL NOT BE LIABLE FOR ANY DAMAGES ARISING 
        FROM THE USE OF THIS SOFTWARE.</p>
        
        <p><strong>By clicking "I Accept" you agree to these license terms.</strong></p>
        """
    
    def _accept(self):
        self.accepted_license = True
        self.dont_show_again = self.dont_show_checkbox.isChecked()
        self.accept()
    
    def _decline(self):
        self.accepted_license = False
        self.reject()
    
    def closeEvent(self, event):
        if not self.accepted_license:
            self.reject()
        event.accept()


# =============================================================================
# Pro License Dialog
# =============================================================================
class ProLicenseDialog(QDialog):
    """Dialog for entering CiviQual Stats Pro license key."""
    
    def __init__(self, license_manager: LicenseManager, parent=None):
        super().__init__(parent)
        self.license_manager = license_manager
        self.setWindowTitle("CiviQual Stats Pro License")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("CiviQual Stats Pro License")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {COLOR_BURGUNDY};")
        header.setAccessibleName("Pro License Key Entry")
        layout.addWidget(header)
        
        # Description
        desc = QLabel(
            "CiviQual Stats Pro unlocks advanced Green Belt and Black Belt "
            "statistical tools for comprehensive quality management analysis."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666; margin-bottom: 12px;")
        layout.addWidget(desc)
        
        # Current status
        status_group = QGroupBox("License Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel()
        self._update_status_label()
        status_layout.addWidget(self.status_label)
        layout.addWidget(status_group)
        
        # License key entry
        key_group = QGroupBox("Enter License Key")
        key_layout = QFormLayout(key_group)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("your.email@organization.gov")
        self.email_input.setAccessibleName("License email address")
        key_layout.addRow("Email:", self.email_input)
        
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("XXXX-XXXX-XXXX-XXXX")
        self.key_input.setAccessibleName("License key")
        key_layout.addRow("License Key:", self.key_input)
        
        layout.addWidget(key_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        purchase_btn = QPushButton("Purchase License")
        purchase_btn.setAccessibleName("Purchase a Pro license")
        purchase_btn.clicked.connect(self._open_purchase_page)
        button_layout.addWidget(purchase_btn)
        
        button_layout.addStretch()
        
        if self.license_manager.is_pro:
            deactivate_btn = QPushButton("Deactivate")
            deactivate_btn.clicked.connect(self._deactivate)
            button_layout.addWidget(deactivate_btn)
        
        activate_btn = QPushButton("Activate")
        activate_btn.setDefault(True)
        activate_btn.clicked.connect(self._activate)
        button_layout.addWidget(activate_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _update_status_label(self):
        if self.license_manager.is_pro:
            status_text = f"✓ Licensed to: {self.license_manager.licensee}"
            if self.license_manager.days_remaining is not None:
                if self.license_manager.days_remaining <= 30:
                    status_text += f"\n⚠ Expires in {self.license_manager.days_remaining} days"
                else:
                    status_text += f"\nExpires in {self.license_manager.days_remaining} days"
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            status_text = "✗ No valid Pro license"
            self.status_label.setStyleSheet("color: #666;")
        self.status_label.setText(status_text)
    
    def _activate(self):
        key = self.key_input.text().strip()
        email = self.email_input.text().strip()
        
        if not key:
            QMessageBox.warning(self, "Missing Key", "Please enter a license key.")
            return
        
        success, message = self.license_manager.activate_license(key, email)
        if success:
            QMessageBox.information(self, "License Activated", message)
            self._update_status_label()
            self.accept()
        else:
            QMessageBox.warning(self, "Activation Failed", message)
    
    def _deactivate(self):
        reply = QMessageBox.question(
            self, "Deactivate License",
            "Are you sure you want to deactivate your Pro license?\n\n"
            "You will need to re-enter your license key to use Pro features again.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.license_manager.deactivate_license()
            QMessageBox.information(self, "License Deactivated", "Your Pro license has been deactivated.")
            self._update_status_label()
    
    def _open_purchase_page(self):
        import webbrowser
        webbrowser.open(f"https://{ORG_DOMAIN}/pro")


# =============================================================================
# Pro Feature Prompt Dialog
# =============================================================================
class ProFeaturePromptDialog(QDialog):
    """Dialog shown when user clicks a Pro feature without license."""
    
    def __init__(self, feature_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CiviQual Stats Pro Feature")
        self.setFixedSize(450, 300)
        self.setModal(True)
        self.feature_name = feature_name
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Header with star icon
        header = QLabel(f"★ {self.feature_name}")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {COLOR_GOLD};")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Description
        desc = QLabel(
            f"{self.feature_name} is a CiviQual Stats Pro feature.\n\n"
            "Upgrade to Pro to unlock advanced Green Belt and Black Belt tools:"
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        # Feature list
        features = QLabel(
            "• Measurement System Analysis (Gage R&R)\n"
            "• Design of Experiments (DOE)\n"
            "• Hypothesis Testing Suite\n"
            "• Advanced Control Charts (CUSUM/EWMA)\n"
            "• Multiple Regression Analysis\n"
            "• FMEA & Control Plan Tools\n"
            "• Project Session Save/Resume\n"
            "• And more..."
        )
        features.setStyleSheet("color: #555; margin-left: 20px;")
        layout.addWidget(features)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        enter_key_btn = QPushButton("Enter License Key")
        enter_key_btn.setDefault(True)
        enter_key_btn.clicked.connect(lambda: self.done(1))  # Return 1 for "enter key"
        button_layout.addWidget(enter_key_btn)
        
        learn_more_btn = QPushButton("Learn More")
        learn_more_btn.clicked.connect(self._open_learn_more)
        button_layout.addWidget(learn_more_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _open_learn_more(self):
        import webbrowser
        webbrowser.open(f"https://{ORG_DOMAIN}/pro")


# =============================================================================
# About Dialog
# =============================================================================
class AboutDialog(QDialog):
    """About dialog with application information."""
    
    def __init__(self, license_manager: LicenseManager, parent=None):
        super().__init__(parent)
        self.license_manager = license_manager
        self.setWindowTitle("About CiviQual Stats")
        self.setFixedSize(500, 620)
        self.setModal(True)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = SplashScreen()._create_logo()
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setAccessibleName("CiviQual Stats logo")
        layout.addWidget(logo_label)
        
        # Title
        title = QLabel("CiviQual Stats")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLOR_BURGUNDY};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("for Lean Six Sigma")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setStyleSheet(f"color: {COLOR_BURGUNDY};")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        # Version
        version = QLabel(f"Version {VERSION} — {VERSION_NAME}")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet("font-weight: bold;")
        layout.addWidget(version)
        
        # Tagline
        tagline = QLabel('"Quality in Every Process"')
        tagline.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        tagline.setStyleSheet(f"color: {COLOR_BURGUNDY_DARK};")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tagline)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background-color: {COLOR_BURGUNDY};")
        layout.addWidget(line)
        
        # License status
        if self.license_manager.is_pro:
            license_status = QLabel(f"★ Pro Licensed to: {self.license_manager.licensee}")
            license_status.setStyleSheet(f"color: {COLOR_GOLD}; font-weight: bold;")
        else:
            license_status = QLabel("Free Tier — Yellow Belt and Basic Green Belt Tools")
            license_status.setStyleSheet("color: #666;")
        license_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(license_status)
        
        # Description
        desc = QLabel(
            "A statistical analysis tool for Lean Six Sigma practitioners\n"
            "in government and public service organizations.\n\n"
            "Organized by DMAIC phases for intuitive workflow."
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 10px;")
        layout.addWidget(desc)
        
        # Copyright
        copyright_label = QLabel(
            f"© 2026 {ORG_NAME}\n"
            f"www.{ORG_DOMAIN}"
        )
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(copyright_label)
        
        layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setAccessibleName("Close about dialog")
        close_btn.clicked.connect(self.accept)
        close_btn.setDefault(True)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
# =============================================================================
# Project Session Manager (Pro Feature)
# =============================================================================
class ProjectSession:
    """Manages project session save/load functionality (Pro only)."""
    
    def __init__(self):
        self.project_path: Optional[str] = None
        self.project_name: str = "Untitled Project"
        self.project_description: str = ""
        self.project_notes: str = ""
        self.data_file_path: Optional[str] = None
        self.data_file_hash: Optional[str] = None
        self.column_selections: Dict[str, str] = {}
        self.spec_limits: Dict[str, float] = {}
        self.control_chart_settings: Dict[str, Any] = {}
        self.western_electric_rules: List[int] = [1, 2, 3, 4]
        self.analysis_history: List[Dict[str, Any]] = []
        self.window_geometry: Optional[bytes] = None
        self.active_phase: str = "Measure"
        self.active_tool: str = "4-Up Chart"
        self.created_at: Optional[str] = None
        self.modified_at: Optional[str] = None
        self.is_modified: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for JSON serialization."""
        return {
            "version": VERSION,
            "project_name": self.project_name,
            "project_description": self.project_description,
            "project_notes": self.project_notes,
            "data_file_path": self.data_file_path,
            "data_file_hash": self.data_file_hash,
            "column_selections": self.column_selections,
            "spec_limits": self.spec_limits,
            "control_chart_settings": self.control_chart_settings,
            "western_electric_rules": self.western_electric_rules,
            "analysis_history": self.analysis_history,
            "active_phase": self.active_phase,
            "active_tool": self.active_tool,
            "created_at": self.created_at or datetime.now().isoformat(),
            "modified_at": datetime.now().isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectSession":
        """Create session from dictionary."""
        session = cls()
        session.project_name = data.get("project_name", "Untitled Project")
        session.project_description = data.get("project_description", "")
        session.project_notes = data.get("project_notes", "")
        session.data_file_path = data.get("data_file_path")
        session.data_file_hash = data.get("data_file_hash")
        session.column_selections = data.get("column_selections", {})
        session.spec_limits = data.get("spec_limits", {})
        session.control_chart_settings = data.get("control_chart_settings", {})
        session.western_electric_rules = data.get("western_electric_rules", [1, 2, 3, 4])
        session.analysis_history = data.get("analysis_history", [])
        session.active_phase = data.get("active_phase", "Measure")
        session.active_tool = data.get("active_tool", "4-Up Chart")
        session.created_at = data.get("created_at")
        session.modified_at = data.get("modified_at")
        return session
    
    def save(self, file_path: str) -> bool:
        """Save session to file."""
        try:
            self.project_path = file_path
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2)
            self.is_modified = False
            return True
        except IOError as e:
            print(f"Error saving project: {e}")
            return False
    
    @classmethod
    def load(cls, file_path: str) -> Optional["ProjectSession"]:
        """Load session from file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            session = cls.from_dict(data)
            session.project_path = file_path
            session.is_modified = False
            return session
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading project: {e}")
            return None
    
    def add_analysis_entry(self, analysis_type: str, parameters: Dict[str, Any], summary: str):
        """Add an entry to analysis history."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "analysis_type": analysis_type,
            "parameters": parameters,
            "summary": summary
        }
        self.analysis_history.append(entry)
        self.is_modified = True
    
    def verify_data_file(self) -> tuple:
        """
        Verify data file integrity.
        Returns (status, message) where status is 'ok', 'changed', 'missing'.
        """
        if not self.data_file_path:
            return ("ok", "No data file associated")
        
        if not os.path.exists(self.data_file_path):
            return ("missing", f"Data file not found: {self.data_file_path}")
        
        current_hash = calculate_file_hash(self.data_file_path)
        if self.data_file_hash and current_hash != self.data_file_hash:
            return ("changed", "Data file has been modified since last save")
        
        return ("ok", "Data file verified")


class SaveProjectDialog(QDialog):
    """Dialog for saving a project with metadata."""
    
    def __init__(self, session: ProjectSession, parent=None):
        super().__init__(parent)
        self.session = session
        self.setWindowTitle("Save Project")
        self.setMinimumSize(450, 350)
        self.setModal(True)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Project info
        form = QFormLayout()
        
        self.name_input = QLineEdit(self.session.project_name)
        self.name_input.setAccessibleName("Project name")
        form.addRow("Project Name:", self.name_input)
        
        self.desc_input = QLineEdit(self.session.project_description)
        self.desc_input.setAccessibleName("Project description")
        form.addRow("Description:", self.desc_input)
        
        self.notes_input = QTextEdit()
        self.notes_input.setPlainText(self.session.project_notes)
        self.notes_input.setMaximumHeight(100)
        self.notes_input.setAccessibleName("Project notes")
        form.addRow("Notes:", self.notes_input)
        
        layout.addLayout(form)
        
        # Data file info
        if self.session.data_file_path:
            data_info = QGroupBox("Data File")
            data_layout = QVBoxLayout(data_info)
            data_label = QLabel(f"File: {os.path.basename(self.session.data_file_path)}")
            data_label.setStyleSheet("color: #666;")
            data_layout.addWidget(data_label)
            note_label = QLabel("Note: Only the file path is saved, not the data itself.")
            note_label.setStyleSheet("color: #999; font-size: 10px;")
            data_layout.addWidget(note_label)
            layout.addWidget(data_info)
        
        layout.addStretch()
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._save)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _save(self):
        self.session.project_name = self.name_input.text().strip() or "Untitled Project"
        self.session.project_description = self.desc_input.text().strip()
        self.session.project_notes = self.notes_input.toPlainText().strip()
        self.accept()


class OpenProjectDialog(QDialog):
    """Dialog for handling data file issues when opening a project."""
    
    def __init__(self, session: ProjectSession, status: str, message: str, parent=None):
        super().__init__(parent)
        self.session = session
        self.status = status
        self.message = message
        self.result_action = None  # "browse", "open_without", "cancel"
        self.new_data_path = None
        self.setWindowTitle("Open Project")
        self.setMinimumSize(450, 250)
        self.setModal(True)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Project info
        title = QLabel(f"Project: {self.session.project_name}")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        if self.session.project_description:
            desc = QLabel(self.session.project_description)
            desc.setStyleSheet("color: #666;")
            layout.addWidget(desc)
        
        layout.addSpacing(12)
        
        # Warning
        if self.status == "missing":
            icon = "⚠"
            color = "#c9302c"
        else:  # changed
            icon = "ℹ"
            color = "#f0ad4e"
        
        warning = QLabel(f"{icon} {self.message}")
        warning.setStyleSheet(f"color: {color}; font-weight: bold;")
        warning.setWordWrap(True)
        layout.addWidget(warning)
        
        if self.session.data_file_path:
            path_label = QLabel(f"Expected: {self.session.data_file_path}")
            path_label.setStyleSheet("color: #666; font-size: 10px;")
            path_label.setWordWrap(True)
            layout.addWidget(path_label)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        browse_btn = QPushButton("Browse for File...")
        browse_btn.clicked.connect(self._browse)
        button_layout.addWidget(browse_btn)
        
        open_without_btn = QPushButton("Open Without Data")
        open_without_btn.clicked.connect(self._open_without)
        button_layout.addWidget(open_without_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _browse(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Data File",
            os.path.dirname(self.session.data_file_path) if self.session.data_file_path else "",
            "CSV Files (*.csv);;Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        if file_path:
            self.new_data_path = file_path
            self.result_action = "browse"
            self.accept()
    
    def _open_without(self):
        self.result_action = "open_without"
        self.accept()


# =============================================================================
# Sample Data Loader
# =============================================================================
class SampleDataDialog(QDialog):
    """Dialog for loading sample data files."""
    
    def __init__(self, is_pro_licensed: bool, parent=None):
        super().__init__(parent)
        self.is_pro_licensed = is_pro_licensed
        self.selected_file = None
        self.setWindowTitle("Load Sample Data")
        self.setMinimumSize(550, 450)
        self.setModal(True)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Sample Data Files")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        desc = QLabel(
            "Select a sample data file to load. These files demonstrate "
            "public-sector quality management scenarios."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666; margin-bottom: 8px;")
        layout.addWidget(desc)
        
        # Sample list
        self.sample_list = QListWidget()
        self.sample_list.setAccessibleName("Sample data files")
        self.sample_list.itemDoubleClicked.connect(self._load_selected)
        
        # Populate list
        self._populate_samples()
        
        layout.addWidget(self.sample_list)
        
        # Description area
        self.desc_text = QTextEdit()
        self.desc_text.setReadOnly(True)
        self.desc_text.setMaximumHeight(100)
        self.desc_text.setAccessibleName("Sample file description")
        layout.addWidget(self.desc_text)
        
        self.sample_list.currentItemChanged.connect(self._show_description)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        load_btn = QPushButton("Load Sample")
        load_btn.setDefault(True)
        load_btn.clicked.connect(self._load_selected)
        button_layout.addWidget(load_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _get_samples_dir(self) -> Optional[Path]:
        """Get the samples directory path."""
        # Check relative to executable/script
        possible_paths = [
            Path(__file__).parent / "samples",
            Path(sys.executable).parent / "samples",
            Path.cwd() / "samples"
        ]
        for path in possible_paths:
            if path.exists():
                return path
        return None
    
    def _populate_samples(self):
        """Populate the sample list."""
        samples_dir = self._get_samples_dir()
        if not samples_dir:
            self.sample_list.addItem("Sample files not found")
            return
        
        # Free tier samples
        free_samples = [
            ("sample_control_chart.csv", "Court case processing times with control chart signals"),
            ("sample_capability.csv", "Document processing cycle time for Cp/Cpk analysis"),
            ("sample_anova.csv", "Processing times by court division for ANOVA"),
            ("sample_correlation.csv", "Case complexity factors correlation study"),
            ("sample_pareto.csv", "Filing defect categories for Pareto analysis"),
            ("sample_court_operations.csv", "Comprehensive court operations data (50 cases)"),
        ]
        
        for filename, description in free_samples:
            file_path = samples_dir / filename
            if file_path.exists():
                item = self.sample_list.addItem(filename)
                self.sample_list.item(self.sample_list.count() - 1).setData(
                    Qt.ItemDataRole.UserRole, 
                    {"path": str(file_path), "description": description, "pro": False}
                )
        
        # Pro tier samples
        pro_samples = [
            ("pro/sample_msa_gage_rr.csv", "Case file quality review by supervisors (Gage R&R)"),
            ("pro/sample_doe_factorial.csv", "Court process optimization 2³ factorial design"),
            ("pro/sample_hypothesis_tests.csv", "Workflow comparison study (3 methods)"),
            ("pro/sample_regression.csv", "Processing time prediction (5 factors)"),
            ("pro/sample_cusum_ewma.csv", "Weekly court metrics with process drift"),
            ("pro/sample_lean_metrics.csv", "12-step court process lean metrics"),
            ("pro/sample_fmea.csv", "Court process failure modes and effects"),
        ]
        
        for filename, description in pro_samples:
            file_path = samples_dir / filename
            if file_path.exists():
                display_name = f"★ {os.path.basename(filename)}"
                self.sample_list.addItem(display_name)
                item = self.sample_list.item(self.sample_list.count() - 1)
                item.setData(
                    Qt.ItemDataRole.UserRole,
                    {"path": str(file_path), "description": description, "pro": True}
                )
                if not self.is_pro_licensed:
                    item.setForeground(QColor("#999"))
    
    def _show_description(self, current, previous):
        """Show description for selected sample."""
        if current:
            data = current.data(Qt.ItemDataRole.UserRole)
            if data:
                desc = data.get("description", "")
                if data.get("pro") and not self.is_pro_licensed:
                    desc += "\n\n★ Pro license required to load this sample."
                self.desc_text.setPlainText(desc)
    
    def _load_selected(self):
        """Load the selected sample file."""
        current = self.sample_list.currentItem()
        if not current:
            return
        
        data = current.data(Qt.ItemDataRole.UserRole)
        if not data:
            return
        
        if data.get("pro") and not self.is_pro_licensed:
            QMessageBox.information(
                self, "Pro Feature",
                "This sample file is designed for Pro features.\n\n"
                "You can still load it, but the recommended analysis tools require a Pro license."
            )
        
        self.selected_file = data.get("path")
        self.accept()


# =============================================================================
# Accessibility Statement Dialog
# =============================================================================
class AccessibilityDialog(QDialog):
    """Accessibility statement and settings dialog."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Accessibility")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Accessibility Statement")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header.setAccessibleName("Accessibility Statement Heading")
        layout.addWidget(header)
        
        # Statement
        statement = QTextBrowser()
        statement.setAccessibleName("Accessibility statement content")
        statement.setHtml(f"""
        <h3>CiviQual Stats {VERSION} Accessibility</h3>
        
        <p>CiviQual Stats is designed to comply with Section 508 of the 
        Rehabilitation Act and WCAG 2.1 Level AA guidelines.</p>
        
        <h4>Accessibility Features</h4>
        <ul>
            <li>Full keyboard navigation support</li>
            <li>Screen reader compatibility (NVDA, JAWS, VoiceOver)</li>
            <li>High contrast color scheme option</li>
            <li>Resizable interface elements</li>
            <li>Accessible names and descriptions for all controls</li>
            <li>Focus indicators on interactive elements</li>
            <li>Alternative text for charts and visualizations</li>
        </ul>
        
        <h4>Keyboard Shortcuts</h4>
        <table border="0" cellpadding="4">
            <tr><td><b>Alt+D</b></td><td>Define phase</td></tr>
            <tr><td><b>Alt+M</b></td><td>Measure phase</td></tr>
            <tr><td><b>Alt+A</b></td><td>Analyze phase</td></tr>
            <tr><td><b>Alt+I</b></td><td>Improve phase</td></tr>
            <tr><td><b>Alt+C</b></td><td>Control phase</td></tr>
            <tr><td><b>Ctrl+O</b></td><td>Open data file</td></tr>
            <tr><td><b>Ctrl+S</b></td><td>Save project (Pro)</td></tr>
            <tr><td><b>Ctrl+E</b></td><td>Export chart</td></tr>
            <tr><td><b>F1</b></td><td>Help</td></tr>
        </table>
        
        <h4>Feedback</h4>
        <p>If you encounter accessibility barriers or have suggestions for 
        improvement, please contact us at:</p>
        <p><b>support@{ORG_DOMAIN}</b></p>
        """)
        layout.addWidget(statement)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setAccessibleName("Close accessibility dialog")
        close_btn.clicked.connect(self.accept)
        close_btn.setDefault(True)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
# =============================================================================
# DMAIC Phase Tab Widget
# =============================================================================
class DMaicPhaseWidget(QWidget):
    """Widget containing tools for a single DMAIC phase."""
    
    tool_selected = Signal(str, bool)  # tool_name, is_pro
    
    def __init__(self, phase_name: str, phase_config: dict, license_manager: LicenseManager, parent=None):
        super().__init__(parent)
        self.phase_name = phase_name
        self.phase_config = phase_config
        self.license_manager = license_manager
        self.tool_tabs = QTabWidget()
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tool tabs
        self.tool_tabs.setAccessibleName(f"{self.phase_name} phase tools")
        self.tool_tabs.setDocumentMode(True)
        self.tool_tabs.currentChanged.connect(self._on_tool_changed)
        
        layout.addWidget(self.tool_tabs)
    
    def add_tool_tab(self, name: str, widget: QWidget, is_pro: bool = False):
        """Add a tool tab to this phase."""
        if is_pro:
            display_name = f"★ {name}"
            widget.setAccessibleDescription(f"Pro feature: {name}")
        else:
            display_name = name
        
        index = self.tool_tabs.addTab(widget, display_name)
        
        # Store metadata
        self.tool_tabs.setTabToolTip(index, f"{name} - {'Pro' if is_pro else 'Free'}")
        widget.setProperty("tool_name", name)
        widget.setProperty("is_pro", is_pro)
    
    def _on_tool_changed(self, index: int):
        """Handle tool tab change."""
        if index >= 0:
            widget = self.tool_tabs.widget(index)
            if widget:
                tool_name = widget.property("tool_name") or ""
                is_pro = widget.property("is_pro") or False
                self.tool_selected.emit(tool_name, is_pro)
    
    def get_current_tool(self) -> tuple:
        """Get current tool name and pro status."""
        widget = self.tool_tabs.currentWidget()
        if widget:
            return (widget.property("tool_name") or "", widget.property("is_pro") or False)
        return ("", False)
    
    def select_tool(self, tool_name: str):
        """Select a tool by name."""
        for i in range(self.tool_tabs.count()):
            widget = self.tool_tabs.widget(i)
            if widget and widget.property("tool_name") == tool_name:
                self.tool_tabs.setCurrentIndex(i)
                break


# =============================================================================
# Pro Feature Gated Widget
# =============================================================================
class ProGatedWidget(QWidget):
    """Widget wrapper that shows Pro upgrade prompt if not licensed."""
    
    request_license = Signal()
    
    def __init__(self, tool_name: str, actual_widget: QWidget, license_manager: LicenseManager, parent=None):
        super().__init__(parent)
        self.tool_name = tool_name
        self.actual_widget = actual_widget
        self.license_manager = license_manager
        self._setup_ui()
    
    def _setup_ui(self):
        self.stack = QStackedWidget()
        
        # Locked view
        locked_widget = QWidget()
        locked_layout = QVBoxLayout(locked_widget)
        locked_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_label = QLabel("★")
        icon_label.setFont(QFont("Arial", 48))
        icon_label.setStyleSheet(f"color: {COLOR_GOLD};")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        locked_layout.addWidget(icon_label)
        
        title_label = QLabel(self.tool_name)
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        locked_layout.addWidget(title_label)
        
        desc_label = QLabel("This is a CiviQual Stats Pro feature.")
        desc_label.setStyleSheet("color: #666;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        locked_layout.addWidget(desc_label)
        
        locked_layout.addSpacing(20)
        
        unlock_btn = QPushButton("Unlock with Pro License")
        unlock_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_GOLD};
                color: white;
                font-weight: bold;
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: #c9a066;
            }}
        """)
        unlock_btn.clicked.connect(self._request_license)
        unlock_btn.setAccessibleName(f"Unlock {self.tool_name} with Pro license")
        locked_layout.addWidget(unlock_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.stack.addWidget(locked_widget)
        self.stack.addWidget(self.actual_widget)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)
        
        self._update_view()
    
    def _update_view(self):
        """Update view based on license status."""
        if self.license_manager.is_pro:
            self.stack.setCurrentIndex(1)  # Show actual widget
        else:
            self.stack.setCurrentIndex(0)  # Show locked view
    
    def _request_license(self):
        """Request license entry."""
        self.request_license.emit()
    
    def refresh_license_status(self):
        """Refresh the view based on current license status."""
        self._update_view()


# =============================================================================
# Main Window
# =============================================================================
class CiviQualStatsMainWindow(QMainWindow):
    """Main application window with DMAIC phase organization."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize managers
        self.license_manager = LicenseManager()
        self.stats_engine = StatisticsEngine()
        self.viz_engine = VisualizationEngine()
        self.report_generator = ReportGenerator()
        self.data_handler = DataHandler()
        self.diagram_engine = ProcessDiagramEngine()
        
        # Initialize Pro modules
        self._init_pro_modules()
        
        # Session management
        self.session = ProjectSession()
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self._auto_save)
        
        # Data state
        self.current_data: Optional[pd.DataFrame] = None
        self.current_file_path: Optional[str] = None
        
        # Settings
        self.settings = QSettings(ORG_NAME, APP_NAME)
        
        # UI references
        self.phase_widgets: Dict[str, DMaicPhaseWidget] = {}
        self.pro_gated_widgets: List[ProGatedWidget] = []
        
        # Setup
        self._setup_window()
        self._setup_menus()
        self._setup_toolbar()
        self._setup_statusbar()
        self._setup_central_widget()
        self._setup_shortcuts()
        self._restore_settings()
        self._check_auto_save_recovery()
        self._start_auto_save()
    
    def _init_pro_modules(self):
        """Initialize Pro module references.
        
        Note: Some Pro modules are dataclasses with required arguments.
        We store class references here and instantiate on demand.
        """
        # Analysis engines (can be instantiated without arguments)
        self.msa = MSA()
        self.doe = DOE()
        self.hypothesis_tests = HypothesisTests()
        self.sample_size_calc = SampleSizeCalculator()
        self.advanced_capability = AdvancedCapability()
        self.multiple_regression = MultipleRegression()
        self.advanced_control_charts = AdvancedControlCharts()
        self.lean_calculators = LeanCalculators()
        self.outlier_detection = OutlierDetection()
        self.missing_data_analysis = MissingDataAnalysis()
        
        # Builder/factory classes (store references, instantiate on demand)
        self.FishboneBuilder = FishboneBuilder
        self.FiveWhysBuilder = FiveWhysBuilder
        
        # Dataclasses with required arguments (store references, instantiate on demand)
        self.PughMatrix = PughMatrix
        self.ImpactEffortMatrix = ImpactEffortMatrix
        self.FMEA = FMEA
        self.ControlPlan = ControlPlan
        
        # Widget (requires parent, instantiate when needed)
        self.ChartEditor = ChartEditor
    
    def _setup_window(self):
        """Setup main window properties."""
        self.setWindowTitle(f"{APP_NAME} {VERSION}")
        self.setMinimumSize(1200, 800)
        self.setAccessibleName(f"{APP_NAME} main window")
        
        # Window icon
        icon_pixmap = SplashScreen()._create_logo()
        self.setWindowIcon(QIcon(icon_pixmap))
    
    def _setup_menus(self):
        """Setup menu bar with all menus."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        open_action = QAction("&Open Data File...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)
        
        # Recent files submenu
        self.recent_files_menu = file_menu.addMenu("Open &Recent")
        self._update_recent_files_menu()
        
        file_menu.addSeparator()
        
        # Pro: Save/Open Project
        save_project_action = QAction("&Save Project...", self)
        save_project_action.setShortcut(QKeySequence("Ctrl+S"))
        save_project_action.triggered.connect(self._save_project)
        file_menu.addAction(save_project_action)
        
        open_project_action = QAction("Open Pro&ject...", self)
        open_project_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        open_project_action.triggered.connect(self._open_project)
        file_menu.addAction(open_project_action)
        
        # Recent projects submenu
        self.recent_projects_menu = file_menu.addMenu("Recent Pro&jects")
        self._update_recent_projects_menu()
        
        file_menu.addSeparator()
        
        # Export submenu
        export_menu = file_menu.addMenu("E&xport")
        
        export_chart_action = QAction("Export &Chart...", self)
        export_chart_action.setShortcut(QKeySequence("Ctrl+E"))
        export_chart_action.triggered.connect(self._export_chart)
        export_menu.addAction(export_chart_action)
        
        export_report_action = QAction("Export &Report (Word)...", self)
        export_report_action.triggered.connect(self._export_report)
        export_menu.addAction(export_report_action)
        
        export_data_action = QAction("Export &Data...", self)
        export_data_action.triggered.connect(self._export_data)
        export_menu.addAction(export_data_action)
        
        file_menu.addSeparator()
        
        print_action = QAction("&Print...", self)
        print_action.setShortcut(QKeySequence.StandardKey.Print)
        print_action.triggered.connect(self._print)
        file_menu.addAction(print_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Alt+F4"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.setEnabled(False)  # Placeholder
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.setEnabled(False)  # Placeholder
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self._copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self._paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction("&Find in Data...", self)
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        find_action.triggered.connect(self._find_in_data)
        edit_menu.addAction(find_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        # Phase shortcuts
        view_menu.addAction(self._create_phase_action("&Define", "Alt+D", "Define"))
        view_menu.addAction(self._create_phase_action("&Measure", "Alt+M", "Measure"))
        view_menu.addAction(self._create_phase_action("&Analyze", "Alt+A", "Analyze"))
        view_menu.addAction(self._create_phase_action("&Improve", "Alt+I", "Improve"))
        view_menu.addAction(self._create_phase_action("&Control", "Alt+C", "Control"))
        
        view_menu.addSeparator()
        
        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut(QKeySequence("Ctrl++"))
        zoom_in_action.triggered.connect(self._zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut(QKeySequence("Ctrl+-"))
        zoom_out_action.triggered.connect(self._zoom_out)
        view_menu.addAction(zoom_out_action)
        
        reset_zoom_action = QAction("&Reset Zoom", self)
        reset_zoom_action.setShortcut(QKeySequence("Ctrl+0"))
        reset_zoom_action.triggered.connect(self._reset_zoom)
        view_menu.addAction(reset_zoom_action)
        
        view_menu.addSeparator()
        
        self.high_contrast_action = QAction("&High Contrast Mode", self)
        self.high_contrast_action.setCheckable(True)
        self.high_contrast_action.triggered.connect(self._toggle_high_contrast)
        view_menu.addAction(self.high_contrast_action)
        
        fullscreen_action = QAction("&Full Screen", self)
        fullscreen_action.setShortcut(QKeySequence("F11"))
        fullscreen_action.triggered.connect(self._toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # Analysis menu
        analysis_menu = menubar.addMenu("&Analysis")
        
        run_analysis_action = QAction("&Run Current Analysis", self)
        run_analysis_action.setShortcut(QKeySequence("F5"))
        run_analysis_action.triggered.connect(self._run_analysis)
        analysis_menu.addAction(run_analysis_action)
        
        analysis_menu.addSeparator()
        
        clear_results_action = QAction("&Clear Results", self)
        clear_results_action.triggered.connect(self._clear_results)
        analysis_menu.addAction(clear_results_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        data_sampling_action = QAction("Data &Sampling...", self)
        data_sampling_action.triggered.connect(lambda: self._goto_tool("Define", "Data Sampling"))
        tools_menu.addAction(data_sampling_action)
        
        split_worksheet_action = QAction("Split &Worksheet...", self)
        split_worksheet_action.triggered.connect(lambda: self._goto_tool("Define", "Split Worksheet"))
        tools_menu.addAction(split_worksheet_action)
        
        roi_calc_action = QAction("&ROI Calculator...", self)
        roi_calc_action.triggered.connect(lambda: self._goto_tool("Improve", "ROI Calculator"))
        tools_menu.addAction(roi_calc_action)
        
        tools_menu.addSeparator()
        
        # Process diagrams submenu
        diagrams_menu = tools_menu.addMenu("Process &Diagrams")
        diagrams_menu.addAction(self._create_tool_action("SIPOC Diagram", "Define", "SIPOC Diagram"))
        diagrams_menu.addAction(self._create_tool_action("Process Map", "Define", "Process Map"))
        diagrams_menu.addAction(self._create_tool_action("RACI Matrix", "Define", "RACI Matrix"))
        diagrams_menu.addAction(self._create_tool_action("Swim Lane Diagram", "Analyze", "Swim Lane Diagram"))
        diagrams_menu.addAction(self._create_tool_action("Value Stream Map", "Analyze", "Value Stream Map"))
        diagrams_menu.addAction(self._create_tool_action("Fishbone Diagram", "Analyze", "Fishbone Diagram"))
        
        tools_menu.addSeparator()
        
        # Pro features submenu
        pro_menu = tools_menu.addMenu("★ &Pro Features")
        
        pro_tools = [
            ("MSA (Gage R&R)", "Measure"),
            ("Sample Size Calculator", "Measure"),
            ("Advanced Capability", "Measure"),
            ("Hypothesis Tests", "Analyze"),
            ("Design of Experiments", "Analyze"),
            ("Multiple Regression", "Analyze"),
            ("Root Cause Tools", "Analyze"),
            ("Data Tools", "Analyze"),
            ("Solution Tools", "Improve"),
            ("Lean Calculators", "Improve"),
            ("CUSUM/EWMA Charts", "Control"),
            ("Planning Tools", "Control"),
            ("Chart Editor", "Control"),
        ]
        
        for tool_name, phase in pro_tools:
            action = QAction(f"★ {tool_name}", self)
            action.triggered.connect(lambda checked, t=tool_name, p=phase: self._goto_pro_tool(p, t))
            pro_menu.addAction(action)
        
        tools_menu.addSeparator()
        
        options_action = QAction("&Options...", self)
        options_action.triggered.connect(self._show_options)
        tools_menu.addAction(options_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        user_guide_action = QAction("&User Guide", self)
        user_guide_action.setShortcut(QKeySequence("F1"))
        user_guide_action.triggered.connect(self._show_user_guide)
        help_menu.addAction(user_guide_action)
        
        # Sample data submenu
        sample_menu = help_menu.addMenu("&Sample Data")
        
        load_sample_action = QAction("&Load Sample Data...", self)
        load_sample_action.triggered.connect(self._load_sample_data)
        sample_menu.addAction(load_sample_action)
        
        open_samples_folder_action = QAction("&Open Samples Folder...", self)
        open_samples_folder_action.triggered.connect(self._open_samples_folder)
        sample_menu.addAction(open_samples_folder_action)
        
        help_menu.addSeparator()
        
        accessibility_action = QAction("&Accessibility...", self)
        accessibility_action.triggered.connect(self._show_accessibility)
        help_menu.addAction(accessibility_action)
        
        help_menu.addSeparator()
        
        license_action = QAction("&Pro License...", self)
        license_action.triggered.connect(self._show_pro_license)
        help_menu.addAction(license_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("&About CiviQual Stats", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_phase_action(self, text: str, shortcut: str, phase: str) -> QAction:
        """Create an action for switching to a DMAIC phase."""
        action = QAction(text, self)
        action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(lambda: self._goto_phase(phase))
        return action
    
    def _create_tool_action(self, text: str, phase: str, tool: str) -> QAction:
        """Create an action for navigating to a tool."""
        action = QAction(text, self)
        action.triggered.connect(lambda: self._goto_tool(phase, tool))
        return action
    
    def _setup_toolbar(self):
        """Setup main toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Open button
        open_btn = QPushButton("Open Data")
        open_btn.clicked.connect(self._open_file)
        toolbar.addWidget(open_btn)
        
        toolbar.addSeparator()
        
        # Column selector
        toolbar.addWidget(QLabel("Column:"))
        self.column_combo = QComboBox()
        self.column_combo.setMinimumWidth(150)
        self.column_combo.setAccessibleName("Select analysis column")
        self.column_combo.currentTextChanged.connect(self._on_column_changed)
        toolbar.addWidget(self.column_combo)
        
        toolbar.addSeparator()
        
        # Run analysis button
        run_btn = QPushButton("Run Analysis")
        run_btn.setAccessibleName("Run current analysis")
        run_btn.setShortcut(QKeySequence("F5"))
        run_btn.clicked.connect(self._run_analysis)
        toolbar.addWidget(run_btn)
        
        # Export button
        export_btn = QPushButton("Export")
        export_btn.setAccessibleName("Export results")
        export_btn.clicked.connect(self._export_chart)
        toolbar.addWidget(export_btn)
        
        toolbar.addSeparator()
        
        # Chart editor button (Pro)
        chart_editor_btn = QPushButton("★ Edit Chart")
        chart_editor_btn.setAccessibleName("Open chart editor (Pro feature)")
        chart_editor_btn.setStyleSheet(f"color: {COLOR_GOLD};")
        chart_editor_btn.clicked.connect(self._open_chart_editor_overlay)
        toolbar.addWidget(chart_editor_btn)
        
        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
        
        # License status
        self.license_status_label = QLabel()
        self._update_license_status_label()
        toolbar.addWidget(self.license_status_label)
    
    def _update_license_status_label(self):
        """Update the license status label in toolbar."""
        if self.license_manager.is_pro:
            self.license_status_label.setText("★ Pro")
            self.license_status_label.setStyleSheet(f"color: {COLOR_GOLD}; font-weight: bold;")
            self.license_status_label.setToolTip(f"Licensed to: {self.license_manager.licensee}")
        else:
            self.license_status_label.setText("Free Tier")
            self.license_status_label.setStyleSheet("color: #666;")
            self.license_status_label.setToolTip("Click Help > Pro License to upgrade")
    
    def _setup_central_widget(self):
        """Setup central widget with DMAIC phase tabs."""
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # DMAIC phase tabs
        self.phase_tabs = QTabWidget()
        self.phase_tabs.setAccessibleName("DMAIC phase tabs")
        self.phase_tabs.setDocumentMode(True)
        self.phase_tabs.setStyleSheet(f"""
            QTabBar::tab {{
                padding: 10px 20px;
                font-weight: bold;
            }}
            QTabBar::tab:selected {{
                color: {COLOR_BURGUNDY};
                border-bottom: 3px solid {COLOR_BURGUNDY};
            }}
        """)
        
        # Create phase widgets
        for phase_name, phase_config in DMAIC_PHASES.items():
            phase_widget = DMaicPhaseWidget(phase_name, phase_config, self.license_manager)
            phase_widget.tool_selected.connect(self._on_tool_selected)
            self.phase_widgets[phase_name] = phase_widget
            
            # Add tools to phase
            self._populate_phase_tools(phase_name, phase_widget)
            
            self.phase_tabs.addTab(phase_widget, phase_name)
        
        layout.addWidget(self.phase_tabs)
        self.setCentralWidget(central)
    
    def _populate_phase_tools(self, phase_name: str, phase_widget: DMaicPhaseWidget):
        """Populate a phase widget with its tools."""
        config = DMAIC_PHASES[phase_name]
        
        # Add free tools
        for tool_name in config["free_tools"]:
            widget = self._create_tool_widget(tool_name, False)
            phase_widget.add_tool_tab(tool_name, widget, is_pro=False)
        
        # Add pro tools (gated)
        for tool_name in config["pro_tools"]:
            # Remove ★ prefix for internal name
            clean_name = tool_name.replace("★ ", "")
            actual_widget = self._create_tool_widget(clean_name, True)
            gated_widget = ProGatedWidget(clean_name, actual_widget, self.license_manager)
            gated_widget.request_license.connect(self._show_pro_license)
            self.pro_gated_widgets.append(gated_widget)
            phase_widget.add_tool_tab(clean_name, gated_widget, is_pro=True)
    
    def _create_tool_widget(self, tool_name: str, is_pro: bool) -> QWidget:
        """Create the actual widget for a tool."""
        # This is a factory method - returns appropriate widget for each tool
        # For brevity, returning placeholder widgets here
        # In full implementation, each would be a complete analysis interface
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Tool header
        header = QLabel(tool_name)
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        if is_pro:
            header.setStyleSheet(f"color: {COLOR_GOLD};")
        else:
            header.setStyleSheet(f"color: {COLOR_BURGUNDY};")
        layout.addWidget(header)
        
        desc = QLabel(self._get_tool_description(tool_name))
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666;")
        layout.addWidget(desc)
        
        layout.addSpacing(16)
        
        # Tool-specific content area
        content = self._create_tool_content(tool_name, is_pro)
        layout.addWidget(content)
        
        layout.addStretch()
        
        return widget
    
    def _get_tool_description(self, tool_name: str) -> str:
        """Get description for a tool."""
        descriptions = {
            # Define
            "SIPOC Diagram": "Suppliers, Inputs, Process, Outputs, Customers diagram for scoping.",
            "Process Map": "Visual flowchart of process steps and decision points.",
            "RACI Matrix": "Responsibility assignment matrix: Responsible, Accountable, Consulted, Informed.",
            "Data Sampling": "Extract random or stratified samples from your data.",
            "Split Worksheet": "Split data into separate files based on column values.",
            
            # Measure
            "4-Up Chart": "Combined view: histogram, run chart, control chart, and capability.",
            "Descriptive Statistics": "Mean, median, standard deviation, and distribution analysis.",
            "Control Charts": "I-Chart, MR-Chart, I-MR Chart with Western Electric rules.",
            "Capability Analysis": "Process capability indices Cp, Cpk, Pp, Ppk.",
            "Probability Plot": "Anderson-Darling normality test with probability plot.",
            "Histogram": "Frequency distribution with optional normal curve overlay.",
            "Box Plot": "Box-and-whisker plot for comparing distributions.",
            "Run Chart": "Time-series plot with median and runs analysis.",
            
            # Measure Pro
            "MSA (Gage R&R)": "Measurement System Analysis: Gage R&R study.",
            "Sample Size Calculator": "Calculate required sample size for various study designs.",
            "Advanced Capability": "Ppk, non-normal capability, confidence intervals.",
            
            # Analyze
            "ANOVA": "One-way and two-way Analysis of Variance.",
            "Correlation": "Pearson and Spearman correlation analysis.",
            "Pareto Analysis": "Pareto chart with cumulative percentage line.",
            "Swim Lane Diagram": "Cross-functional process map by role or department.",
            "Value Stream Map": "Current and future state value stream mapping.",
            "Fishbone Diagram": "Ishikawa cause-and-effect diagram.",
            
            # Analyze Pro
            "Hypothesis Tests": "t-tests, Mann-Whitney, Kruskal-Wallis, Chi-Square.",
            "Design of Experiments": "Full and fractional factorial experiment design.",
            "Multiple Regression": "Multi-factor regression with model diagnostics.",
            "Root Cause Tools": "5 Whys, Fault Tree Analysis, Cause Mapping.",
            "Data Tools": "Data transformation, outlier detection, missing value handling.",
            
            # Improve
            "ROI Calculator": "Return on Investment calculator for improvement projects.",
            
            # Control
            "Control Chart Review": "Review control charts with annotations for ongoing process monitoring.",
            
            # Improve Pro
            "Solution Tools": "Pugh Matrix, Impact-Effort Matrix, solution evaluation.",
            "Lean Calculators": "DPMO, RTY, OEE, Takt Time, cycle time analysis.",
            
            # Control Pro
            "CUSUM/EWMA Charts": "Cumulative sum and exponentially weighted moving average charts.",
            "Planning Tools": "FMEA worksheet, Control Plan, audit checklists.",
            "Chart Editor": "Customize chart colors, labels, and formatting.",
        }
        return descriptions.get(tool_name, "Statistical analysis tool.")
    
    def _create_tool_content(self, tool_name: str, is_pro: bool) -> QWidget:
        """Create tool-specific content widget."""
        # This would contain the actual analysis interface
        # Simplified for this implementation
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Placeholder for data display / analysis controls
        placeholder = QLabel(f"[{tool_name} analysis interface]")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("color: #999; border: 1px dashed #ccc; padding: 40px;")
        layout.addWidget(placeholder)
        
        return content
    
    def _setup_statusbar(self):
        """Setup status bar."""
        self.statusbar = QStatusBar()
        self.statusbar.setAccessibleName("Status bar")
        self.setStatusBar(self.statusbar)
        
        # Data status
        self.data_status_label = QLabel("No data loaded")
        self.statusbar.addWidget(self.data_status_label)
        
        # Spacer
        self.statusbar.addWidget(QLabel(""), 1)
        
        # Modified indicator
        self.modified_label = QLabel("")
        self.statusbar.addPermanentWidget(self.modified_label)
        
        # Version
        version_label = QLabel(f"v{VERSION}")
        version_label.setStyleSheet("color: #999;")
        self.statusbar.addPermanentWidget(version_label)
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Phase shortcuts are handled by menu actions
        
        # Tool number shortcuts (1-9 for tools within phase)
        for i in range(1, 10):
            shortcut = QShortcut(QKeySequence(str(i)), self)
            shortcut.activated.connect(lambda idx=i-1: self._select_tool_by_index(idx))
    
    def _restore_settings(self):
        """Restore window settings from previous session."""
        geometry = self.settings.value(SETTINGS_WINDOW_GEOMETRY)
        if geometry:
            self.restoreGeometry(geometry)
        
        state = self.settings.value(SETTINGS_WINDOW_STATE)
        if state:
            self.restoreState(state)
    
    def _save_settings(self):
        """Save window settings."""
        self.settings.setValue(SETTINGS_WINDOW_GEOMETRY, self.saveGeometry())
        self.settings.setValue(SETTINGS_WINDOW_STATE, self.saveState())
    # =========================================================================
    # File Operations
    # =========================================================================
    
    def _open_file(self):
        """Open a data file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Data File", "",
            "CSV Files (*.csv);;Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        if file_path:
            self._load_data_file(file_path)
    
    def _load_data_file(self, file_path: str, confirm_replace: bool = True):
        """Load data from file."""
        if confirm_replace and self.current_data is not None:
            reply = QMessageBox.question(
                self, "Replace Data",
                "Loading new data will replace current data.\n\nContinue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        try:
            if file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path)
            
            self.current_data = df
            self.current_file_path = file_path
            
            # Update session
            self.session.data_file_path = file_path
            self.session.data_file_hash = calculate_file_hash(file_path)
            self.session.is_modified = True
            
            # Update column selector
            self.column_combo.clear()
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            self.column_combo.addItems(numeric_cols)
            
            # Update status
            self.data_status_label.setText(
                f"{os.path.basename(file_path)} | {len(df)} rows × {len(df.columns)} cols"
            )
            
            # Add to recent files
            self._add_recent_file(file_path)
            
            self.statusbar.showMessage(f"Loaded: {file_path}", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load file:\n{e}")
    
    def _add_recent_file(self, file_path: str):
        """Add file to recent files list."""
        recent = self.settings.value(SETTINGS_RECENT_FILES, []) or []
        if file_path in recent:
            recent.remove(file_path)
        recent.insert(0, file_path)
        recent = recent[:MAX_RECENT_FILES]
        self.settings.setValue(SETTINGS_RECENT_FILES, recent)
        self._update_recent_files_menu()
    
    def _update_recent_files_menu(self):
        """Update recent files menu."""
        self.recent_files_menu.clear()
        recent = self.settings.value(SETTINGS_RECENT_FILES, []) or []
        
        if not recent:
            action = QAction("(No recent files)", self)
            action.setEnabled(False)
            self.recent_files_menu.addAction(action)
            return
        
        for file_path in recent:
            action = QAction(os.path.basename(file_path), self)
            action.setToolTip(file_path)
            action.triggered.connect(lambda checked, fp=file_path: self._load_data_file(fp))
            self.recent_files_menu.addAction(action)
        
        self.recent_files_menu.addSeparator()
        clear_action = QAction("Clear Recent Files", self)
        clear_action.triggered.connect(self._clear_recent_files)
        self.recent_files_menu.addAction(clear_action)
    
    def _clear_recent_files(self):
        """Clear recent files list."""
        self.settings.setValue(SETTINGS_RECENT_FILES, [])
        self._update_recent_files_menu()
    
    # =========================================================================
    # Project Operations (Pro)
    # =========================================================================
    
    def _save_project(self):
        """Save project (Pro feature)."""
        if not self.license_manager.is_pro:
            dialog = ProFeaturePromptDialog("Project Save", self)
            result = dialog.exec()
            if result == 1:  # Enter license key
                self._show_pro_license()
            return
        
        # Show save dialog
        dialog = SaveProjectDialog(self.session, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        # Get save path
        if self.session.project_path:
            file_path = self.session.project_path
        else:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Project",
                f"{self.session.project_name}{PROJECT_EXTENSION}",
                PROJECT_FILTER
            )
            if not file_path:
                return
            if not file_path.endswith(PROJECT_EXTENSION):
                file_path += PROJECT_EXTENSION
        
        # Update session state
        current_phase = list(DMAIC_PHASES.keys())[self.phase_tabs.currentIndex()]
        self.session.active_phase = current_phase
        phase_widget = self.phase_widgets.get(current_phase)
        if phase_widget:
            tool_name, _ = phase_widget.get_current_tool()
            self.session.active_tool = tool_name
        
        # Save
        if self.session.save(file_path):
            self._add_recent_project(file_path)
            self._update_modified_indicator()
            self.statusbar.showMessage(f"Project saved: {file_path}", 3000)
        else:
            QMessageBox.critical(self, "Error", "Could not save project.")
    
    def _open_project(self):
        """Open project (Pro feature)."""
        if not self.license_manager.is_pro:
            dialog = ProFeaturePromptDialog("Project Open", self)
            result = dialog.exec()
            if result == 1:
                self._show_pro_license()
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", PROJECT_FILTER
        )
        if file_path:
            self._load_project(file_path)
    
    def _load_project(self, file_path: str):
        """Load a project file."""
        session = ProjectSession.load(file_path)
        if not session:
            QMessageBox.critical(self, "Error", "Could not load project file.")
            return
        
        # Check data file
        status, message = session.verify_data_file()
        if status != "ok":
            dialog = OpenProjectDialog(session, status, message, self)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return
            
            if dialog.result_action == "browse":
                session.data_file_path = dialog.new_data_path
                session.data_file_hash = calculate_file_hash(dialog.new_data_path)
            elif dialog.result_action == "open_without":
                session.data_file_path = None
        
        # Apply session
        self.session = session
        
        # Load data file
        if session.data_file_path:
            self._load_data_file(session.data_file_path, confirm_replace=False)
        
        # Restore UI state
        phase_index = list(DMAIC_PHASES.keys()).index(session.active_phase) if session.active_phase in DMAIC_PHASES else 1
        self.phase_tabs.setCurrentIndex(phase_index)
        
        if session.active_tool:
            phase_widget = self.phase_widgets.get(session.active_phase)
            if phase_widget:
                phase_widget.select_tool(session.active_tool)
        
        self._add_recent_project(file_path)
        self._update_modified_indicator()
        self.statusbar.showMessage(f"Project loaded: {session.project_name}", 3000)
    
    def _add_recent_project(self, file_path: str):
        """Add project to recent projects list."""
        recent = self.settings.value(SETTINGS_RECENT_PROJECTS, []) or []
        if file_path in recent:
            recent.remove(file_path)
        recent.insert(0, file_path)
        recent = recent[:MAX_RECENT_PROJECTS]
        self.settings.setValue(SETTINGS_RECENT_PROJECTS, recent)
        self._update_recent_projects_menu()
    
    def _update_recent_projects_menu(self):
        """Update recent projects menu."""
        self.recent_projects_menu.clear()
        recent = self.settings.value(SETTINGS_RECENT_PROJECTS, []) or []
        
        if not recent:
            action = QAction("(No recent projects)", self)
            action.setEnabled(False)
            self.recent_projects_menu.addAction(action)
            return
        
        for file_path in recent:
            name = os.path.basename(file_path).replace(PROJECT_EXTENSION, "")
            action = QAction(name, self)
            action.setToolTip(file_path)
            action.triggered.connect(lambda checked, fp=file_path: self._load_project(fp))
            self.recent_projects_menu.addAction(action)
    
    def _update_modified_indicator(self):
        """Update the modified indicator in status bar."""
        if self.session.is_modified:
            self.modified_label.setText("● Modified")
            self.modified_label.setStyleSheet("color: #f0ad4e;")
        else:
            self.modified_label.setText("")
    
    # =========================================================================
    # Auto-Save
    # =========================================================================
    
    def _check_auto_save_recovery(self):
        """Check for auto-save recovery on startup."""
        auto_save_dir = get_auto_save_dir()
        recovery_files = list(auto_save_dir.glob(f"*{PROJECT_EXTENSION}"))
        
        if recovery_files:
            reply = QMessageBox.question(
                self, "Recover Session",
                "An auto-saved session was found from a previous crash.\n\n"
                "Would you like to recover it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                # Load the most recent recovery file
                recovery_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                self._load_project(str(recovery_files[0]))
            
            # Clean up recovery files
            for f in recovery_files:
                try:
                    f.unlink()
                except OSError:
                    pass
    
    def _start_auto_save(self):
        """Start auto-save timer."""
        if self.settings.value(SETTINGS_AUTO_SAVE, True):
            interval = self.settings.value(SETTINGS_AUTO_SAVE_INTERVAL, AUTO_SAVE_INTERVAL_DEFAULT)
            self.auto_save_timer.start(interval)
    
    def _auto_save(self):
        """Perform auto-save."""
        if not self.license_manager.is_pro:
            return
        
        if not self.session.is_modified:
            return
        
        auto_save_path = get_auto_save_dir() / f"recovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}{PROJECT_EXTENSION}"
        self.session.save(str(auto_save_path))
    
    # =========================================================================
    # Export Operations
    # =========================================================================
    
    def _export_chart(self):
        """Export current chart."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Chart", "",
            "PNG Image (*.png);;PDF Document (*.pdf);;SVG Vector (*.svg)"
        )
        if file_path:
            # TODO: Implement actual chart export
            self.statusbar.showMessage(f"Chart exported: {file_path}", 3000)
    
    def _export_report(self):
        """Export analysis report to Word."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Report", "",
            "Word Document (*.docx)"
        )
        if file_path:
            # TODO: Implement report generation
            self.statusbar.showMessage(f"Report exported: {file_path}", 3000)
    
    def _export_data(self):
        """Export data to file."""
        if self.current_data is None:
            QMessageBox.warning(self, "No Data", "No data loaded to export.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "",
            "CSV File (*.csv);;Excel File (*.xlsx)"
        )
        if file_path:
            try:
                if file_path.endswith('.xlsx'):
                    self.current_data.to_excel(file_path, index=False)
                else:
                    self.current_data.to_csv(file_path, index=False)
                self.statusbar.showMessage(f"Data exported: {file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not export data:\n{e}")
    
    def _print(self):
        """Print current view."""
        # TODO: Implement print functionality
        QMessageBox.information(self, "Print", "Print functionality coming soon.")
    
    # =========================================================================
    # Edit Operations
    # =========================================================================
    
    def _copy(self):
        """Copy to clipboard."""
        # Context-dependent copy
        pass
    
    def _paste(self):
        """Paste from clipboard."""
        # Context-dependent paste
        pass
    
    def _find_in_data(self):
        """Find in data."""
        if self.current_data is None:
            QMessageBox.warning(self, "No Data", "No data loaded to search.")
            return
        
        text, ok = QInputDialog.getText(self, "Find in Data", "Search for:")
        if ok and text:
            # TODO: Implement data search
            pass
    
    # =========================================================================
    # View Operations
    # =========================================================================
    
    def _goto_phase(self, phase_name: str):
        """Navigate to a DMAIC phase."""
        if phase_name in DMAIC_PHASES:
            index = list(DMAIC_PHASES.keys()).index(phase_name)
            self.phase_tabs.setCurrentIndex(index)
    
    def _goto_tool(self, phase_name: str, tool_name: str):
        """Navigate to a specific tool."""
        self._goto_phase(phase_name)
        phase_widget = self.phase_widgets.get(phase_name)
        if phase_widget:
            phase_widget.select_tool(tool_name)
    
    def _goto_pro_tool(self, phase_name: str, tool_name: str):
        """Navigate to a Pro tool (with license check)."""
        if not self.license_manager.is_pro:
            dialog = ProFeaturePromptDialog(tool_name, self)
            result = dialog.exec()
            if result == 1:
                self._show_pro_license()
                return
            return
        
        self._goto_tool(phase_name, tool_name)
    
    def _select_tool_by_index(self, index: int):
        """Select tool by number key (1-9)."""
        current_phase = list(DMAIC_PHASES.keys())[self.phase_tabs.currentIndex()]
        phase_widget = self.phase_widgets.get(current_phase)
        if phase_widget and index < phase_widget.tool_tabs.count():
            phase_widget.tool_tabs.setCurrentIndex(index)
    
    def _zoom_in(self):
        """Zoom in."""
        # TODO: Implement zoom
        pass
    
    def _zoom_out(self):
        """Zoom out."""
        # TODO: Implement zoom
        pass
    
    def _reset_zoom(self):
        """Reset zoom."""
        # TODO: Implement zoom
        pass
    
    def _toggle_high_contrast(self, checked: bool):
        """Toggle high contrast mode."""
        if checked:
            self.setStyleSheet("""
                QWidget { background-color: white; color: black; }
                QLabel { color: black; }
            """)
        else:
            self.setStyleSheet("")
    
    def _toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    # =========================================================================
    # Analysis Operations
    # =========================================================================
    
    def _on_column_changed(self, column_name: str):
        """Handle column selection change."""
        self.session.column_selections["primary"] = column_name
        self.session.is_modified = True
        self._update_modified_indicator()
    
    def _on_tool_selected(self, tool_name: str, is_pro: bool):
        """Handle tool selection."""
        if is_pro and not self.license_manager.is_pro:
            # Pro tool selected without license - gated widget will handle display
            pass
        
        self.statusbar.showMessage(f"Tool: {tool_name}", 2000)
    
    def _run_analysis(self):
        """Run current analysis."""
        if self.current_data is None:
            QMessageBox.warning(self, "No Data", "Please load data before running analysis.")
            return
        
        column = self.column_combo.currentText()
        if not column:
            QMessageBox.warning(self, "No Column", "Please select a column for analysis.")
            return
        
        # TODO: Run actual analysis based on current tool
        self.statusbar.showMessage("Analysis complete", 3000)
    
    def _clear_results(self):
        """Clear analysis results."""
        # TODO: Implement clear results
        self.statusbar.showMessage("Results cleared", 2000)
    
    # =========================================================================
    # Chart Editor (Pro)
    # =========================================================================
    
    def _open_chart_editor_overlay(self):
        """Open chart editor as overlay."""
        if not self.license_manager.is_pro:
            dialog = ProFeaturePromptDialog("Chart Editor", self)
            result = dialog.exec()
            if result == 1:
                self._show_pro_license()
            return
        
        # TODO: Implement chart editor overlay
        QMessageBox.information(self, "Chart Editor", "Chart Editor overlay coming in full implementation.")
    
    # =========================================================================
    # Sample Data
    # =========================================================================
    
    def _load_sample_data(self):
        """Load sample data dialog."""
        dialog = SampleDataDialog(self.license_manager.is_pro, self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.selected_file:
            self._load_data_file(dialog.selected_file)
    
    def _open_samples_folder(self):
        """Open samples folder in file browser."""
        samples_dir = None
        possible_paths = [
            Path(__file__).parent / "samples",
            Path(sys.executable).parent / "samples",
            Path.cwd() / "samples"
        ]
        for path in possible_paths:
            if path.exists():
                samples_dir = path
                break
        
        if samples_dir:
            import subprocess
            if sys.platform == "win32":
                subprocess.run(["explorer", str(samples_dir)])
            elif sys.platform == "darwin":
                subprocess.run(["open", str(samples_dir)])
            else:
                subprocess.run(["xdg-open", str(samples_dir)])
        else:
            QMessageBox.warning(self, "Not Found", "Sample data folder not found.")
    
    # =========================================================================
    # Help and Dialogs
    # =========================================================================
    
    def _show_user_guide(self):
        """Show user guide."""
        guide_path = Path(__file__).parent / "docs" / "user_guide.html"
        if guide_path.exists():
            import webbrowser
            webbrowser.open(f"file://{guide_path}")
        else:
            QMessageBox.information(
                self, "User Guide",
                f"User guide not found.\n\nVisit https://{ORG_DOMAIN}/docs for documentation."
            )
    
    def _show_accessibility(self):
        """Show accessibility dialog."""
        dialog = AccessibilityDialog(self)
        dialog.exec()
    
    def _show_pro_license(self):
        """Show Pro license dialog."""
        dialog = ProLicenseDialog(self.license_manager, self)
        dialog.exec()
        
        # Refresh Pro widgets
        for widget in self.pro_gated_widgets:
            widget.refresh_license_status()
        
        self._update_license_status_label()
    
    def _show_about(self):
        """Show about dialog."""
        dialog = AboutDialog(self.license_manager, self)
        dialog.exec()
    
    def _show_options(self):
        """Show options dialog."""
        # TODO: Implement options dialog
        QMessageBox.information(self, "Options", "Options dialog coming soon.")
    
    # =========================================================================
    # Window Events
    # =========================================================================
    
    def closeEvent(self, event):
        """Handle window close."""
        if self.session.is_modified and self.license_manager.is_pro:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes.\n\nSave project before closing?",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self._save_project()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        
        self._save_settings()
        self.auto_save_timer.stop()
        event.accept()
# =============================================================================
# Main Entry Point
# =============================================================================
def main():
    """Application entry point."""
    # Enable high DPI scaling (must be before QApplication)
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORG_NAME)
    app.setOrganizationDomain(ORG_DOMAIN)
    app.setApplicationVersion(VERSION)
    
    # Application style
    app.setStyle("Fusion")
    
    # Set palette for burgundy/gold theme
    from PySide6.QtGui import QPalette
    palette = app.palette()
    palette.setColor(QPalette.ColorRole.Highlight, QColor(COLOR_BURGUNDY))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("white"))
    app.setPalette(palette)
    
    # Settings
    settings = QSettings(ORG_NAME, APP_NAME)
    
    # Show splash screen
    splash = SplashScreen()
    splash.show()
    app.processEvents()
    
    # Check license acceptance
    if not settings.value(SETTINGS_LICENSE_ACCEPTED, False):
        splash.close()
        license_dialog = LicenseDialog()
        if license_dialog.exec() != QDialog.DialogCode.Accepted or not license_dialog.accepted_license:
            sys.exit(0)
        
        if license_dialog.dont_show_again:
            settings.setValue(SETTINGS_LICENSE_ACCEPTED, True)
        
        splash.show()
        app.processEvents()
    
    # Create main window
    window = CiviQualStatsMainWindow()
    
    # Close splash and show window
    import time
    time.sleep(0.5)  # Brief pause to show splash
    splash.close()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
