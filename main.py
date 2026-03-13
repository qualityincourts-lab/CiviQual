#!/usr/bin/env python3
"""
CiviQual - Quality Analytics for Public Service

Version 1.0.0 - Initial Public Release

A statistical analysis tool for Lean Six Sigma practitioners in government
and public service organizations.

The 4-Up Chart methodology is based on the exploratory data analysis
approach developed by Dr. Gregory H. Watson.

Copyright (c) 2026 A Step in the Right Direction LLC
All Rights Reserved.

This version includes:
- Full Windows dark mode support
- Section 508 accessibility compliance
- CPI Process Diagram tools
- Colorblind-friendly visualizations
- Enhanced I-Chart with Western Electric rule filtering
- Improved capability analysis with normality checking
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QFileDialog, QLabel, QComboBox,
    QTableWidget, QTableWidgetItem, QGroupBox, QFormLayout,
    QLineEdit, QSpinBox, QDoubleSpinBox, QMessageBox, QScrollArea,
    QSplitter, QTextEdit, QCheckBox, QStatusBar, QMenuBar, QMenu,
    QDialog, QDialogButtonBox, QGridLayout, QRadioButton, QButtonGroup,
    QTextBrowser, QFrame, QListWidget, QAbstractItemView
)
from PySide6.QtCore import Qt, QSize, QStandardPaths, QTimer
from PySide6.QtGui import (
    QAction, QFont, QIcon, QColor, QPixmap, QPainter, QPen, QBrush,
    QKeySequence, QShortcut, QPalette
)

import pandas as pd
import numpy as np

from statistics_engine import StatisticsEngine
from visualizations import VisualizationEngine
from report_generator import ReportGenerator
from data_handler import DataHandler
from process_diagrams import ProcessDiagramEngine


# =============================================================================
# Version Information
# =============================================================================
VERSION = "1.0.0"
VERSION_NAME = "Initial Public Release"


# =============================================================================
# Theme and Dark Mode Support
# =============================================================================
def is_dark_mode():
    """Detect if the system is using dark mode."""
    # Try to detect Windows dark mode via registry
    if sys.platform == 'win32':
        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return value == 0  # 0 = dark mode, 1 = light mode
        except Exception:
            pass
    
    # Fallback: check Qt palette
    app = QApplication.instance()
    if app:
        palette = app.palette()
        bg_color = palette.color(QPalette.ColorRole.Window)
        # If background luminance is low, assume dark mode
        luminance = (0.299 * bg_color.red() + 0.587 * bg_color.green() + 0.114 * bg_color.blue()) / 255
        return luminance < 0.5
    
    return False


def create_dark_palette():
    """Create a dark color palette for the application."""
    palette = QPalette()
    
    # Dark mode colors
    dark_bg = QColor(30, 30, 30)
    dark_alt = QColor(45, 45, 45)
    dark_text = QColor(220, 220, 220)
    dark_highlight = QColor(109, 19, 42)  # Brand burgundy
    dark_highlight_text = QColor(255, 255, 255)
    dark_link = QColor(86, 180, 233)  # Sky blue
    dark_disabled = QColor(128, 128, 128)
    dark_mid = QColor(60, 60, 60)
    
    # Set colors for different roles
    palette.setColor(QPalette.ColorRole.Window, dark_bg)
    palette.setColor(QPalette.ColorRole.WindowText, dark_text)
    palette.setColor(QPalette.ColorRole.Base, dark_alt)
    palette.setColor(QPalette.ColorRole.AlternateBase, dark_bg)
    palette.setColor(QPalette.ColorRole.ToolTipBase, dark_alt)
    palette.setColor(QPalette.ColorRole.ToolTipText, dark_text)
    palette.setColor(QPalette.ColorRole.Text, dark_text)
    palette.setColor(QPalette.ColorRole.Button, dark_alt)
    palette.setColor(QPalette.ColorRole.ButtonText, dark_text)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, dark_link)
    palette.setColor(QPalette.ColorRole.Highlight, dark_highlight)
    palette.setColor(QPalette.ColorRole.HighlightedText, dark_highlight_text)
    palette.setColor(QPalette.ColorRole.Mid, dark_mid)
    
    # Disabled colors
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, dark_disabled)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, dark_disabled)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, dark_disabled)
    
    return palette


def create_light_palette():
    """Create a light color palette for the application."""
    palette = QPalette()
    
    # Light mode colors
    light_bg = QColor(255, 255, 255)
    light_alt = QColor(245, 245, 245)
    light_text = QColor(0, 0, 0)
    light_highlight = QColor(109, 19, 42)  # Brand burgundy
    light_highlight_text = QColor(255, 255, 255)
    light_link = QColor(0, 114, 178)  # Blue
    light_disabled = QColor(160, 160, 160)
    light_mid = QColor(200, 200, 200)
    
    # Set colors for different roles
    palette.setColor(QPalette.ColorRole.Window, light_bg)
    palette.setColor(QPalette.ColorRole.WindowText, light_text)
    palette.setColor(QPalette.ColorRole.Base, light_bg)
    palette.setColor(QPalette.ColorRole.AlternateBase, light_alt)
    palette.setColor(QPalette.ColorRole.ToolTipBase, light_alt)
    palette.setColor(QPalette.ColorRole.ToolTipText, light_text)
    palette.setColor(QPalette.ColorRole.Text, light_text)
    palette.setColor(QPalette.ColorRole.Button, light_alt)
    palette.setColor(QPalette.ColorRole.ButtonText, light_text)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, light_link)
    palette.setColor(QPalette.ColorRole.Highlight, light_highlight)
    palette.setColor(QPalette.ColorRole.HighlightedText, light_highlight_text)
    palette.setColor(QPalette.ColorRole.Mid, light_mid)
    
    # Disabled colors
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, light_disabled)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, light_disabled)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, light_disabled)
    
    return palette


# Global flag for dark mode (set at startup)
DARK_MODE = False


def get_chart_display_style():
    """Get stylesheet for chart display areas based on current theme."""
    if DARK_MODE:
        return "background-color: #1e1e1e; border: 1px solid #555;"
    else:
        return "background-color: white; border: 1px solid #ccc;"


def get_text_edit_style():
    """Get stylesheet for text edit areas based on current theme."""
    if DARK_MODE:
        return "background-color: #2d2d2d; color: #dcdcdc; border: 1px solid #555; font-family: 'Consolas', monospace;"
    else:
        return "background-color: #f8f9fa; color: #333; border: 1px solid #ccc; font-family: 'Consolas', monospace;"


# =============================================================================
# Splash Screen
# =============================================================================
class SplashScreen(QDialog):
    """Splash screen showing CiviQual branding and attribution."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CiviQual")
        self.setFixedSize(500, 400)
        self.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("""
            QDialog { background-color: white; border: 3px solid #6d132a; }
            QLabel { border: none; background: transparent; }
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
        title = QLabel("CiviQual")
        title.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title.setStyleSheet("color: #6d132a;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Tagline
        tagline = QLabel("Quality Analytics for Public Service")
        tagline.setFont(QFont("Arial", 12))
        tagline.setStyleSheet("color: #6d132a;")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tagline)
        
        # Subtitle
        subtitle = QLabel("Statistical Analysis for Lean Six Sigma")
        subtitle.setFont(QFont("Arial", 10))
        subtitle.setStyleSheet("color: #666;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(15)
        
        layout.addStretch()
        
        # Version
        version = QLabel(f"Version {VERSION}")
        version.setStyleSheet("color: #666; font-size: 10px;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)
        
        # Disclaimer
        disclaimer = QLabel(
            "Free for government, courts, and nonprofit organizations."
        )
        disclaimer.setFont(QFont("Arial", 8))
        disclaimer.setStyleSheet("color: #888;")
        disclaimer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(disclaimer)
        
        # Copyright
        copyright_label = QLabel("© 2026 A Step in the Right Direction LLC")
        copyright_label.setStyleSheet("color: #999; font-size: 8px;")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(copyright_label)
    
    def _create_logo(self):
        """Create CiviQual logo with burgundy/gold color scheme."""
        pixmap = QPixmap(80, 80)
        pixmap.fill(QColor("#6d132a"))  # Burgundy background
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # White inner area
        painter.setBrush(QBrush(QColor("white")))
        painter.setPen(QPen(QColor("white")))
        painter.drawRoundedRect(5, 5, 70, 70, 6, 6)
        
        # Burgundy dividing lines (4-Up grid)
        pen = QPen(QColor("#6d132a"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(40, 8, 40, 72)
        painter.drawLine(8, 40, 72, 40)
        
        # Bar chart in upper-left quadrant
        painter.setBrush(QBrush(QColor("#6d132a")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(12, 28, 6, 10)
        painter.drawRect(20, 20, 6, 18)
        painter.drawRect(28, 14, 6, 24)
        
        # Bell curve hint in upper-right (gold accent)
        painter.setPen(QPen(QColor("#dcad73"), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(46, 12, 20, 24, 0, 180 * 16)
        
        # Control chart hint in lower-left
        painter.setPen(QPen(QColor("#6d132a"), 2))
        points = [(12, 58), (20, 52), (28, 56), (36, 50)]
        for i in range(len(points) - 1):
            painter.drawLine(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
        
        # Scatter plot hint in lower-right (gold accent)
        painter.setBrush(QBrush(QColor("#dcad73")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(50, 48, 5, 5)
        painter.drawEllipse(58, 54, 5, 5)
        painter.drawEllipse(66, 60, 5, 5)
        
        painter.end()
        return pixmap


# =============================================================================
# Configuration Management
# =============================================================================
def get_config_path():
    """Get the path to the configuration file."""
    if sys.platform == 'win32':
        config_dir = Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CiviQual'
    else:
        config_dir = Path.home() / '.civiqual'
    
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / 'config.json'


def load_config():
    """Load configuration from file."""
    config_path = get_config_path()
    default_config = {
        'license_accepted': False,
        'show_license_dialog': True,
        'recent_files': [],
        'window_geometry': None,
        'last_directory': str(Path.home()),
        'accessibility_high_contrast': False,
        'accessibility_large_text': False
    }
    
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                saved_config = json.load(f)
                default_config.update(saved_config)
        except (json.JSONDecodeError, IOError):
            pass
    
    return default_config


def save_config(config):
    """Save configuration to file."""
    config_path = get_config_path()
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
    except IOError:
        pass


# =============================================================================
# Keyboard Shortcuts Dialog
# =============================================================================
class KeyboardShortcutsDialog(QDialog):
    """Dialog showing all keyboard shortcuts for accessibility."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Keyboard Shortcuts")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Keyboard Shortcuts")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAccessibleName("Keyboard Shortcuts Dialog Title")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("CiviQual supports full keyboard navigation. "
                     "Use Tab to move between controls, Enter to activate buttons, "
                     "and the shortcuts below for quick access to features.")
        desc.setWordWrap(True)
        desc.setAccessibleName("Keyboard navigation description")
        layout.addWidget(desc)
        
        # Shortcuts browser
        shortcuts_text = QTextBrowser()
        shortcuts_text.setAccessibleName("Keyboard shortcuts list")
        shortcuts_text.setAccessibleDescription("A comprehensive list of all keyboard shortcuts organized by category")
        shortcuts_text.setOpenExternalLinks(False)
        shortcuts_text.setHtml(self._get_shortcuts_html())
        layout.addWidget(shortcuts_text)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setAccessibleName("Close keyboard shortcuts dialog")
        close_btn.setAccessibleDescription("Press Enter or click to close this dialog")
        close_btn.clicked.connect(self.accept)
        close_btn.setDefault(True)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _get_shortcuts_html(self):
        """Generate HTML content for keyboard shortcuts."""
        return """
        <style>
            body { font-family: Arial, Arial, sans-serif; }
            h3 { color: #6d132a; margin-top: 15px; margin-bottom: 8px; border-bottom: 1px solid #dcad73; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 10px; }
            td { padding: 5px 10px; border-bottom: 1px solid #e0e0e0; }
            td:first-child { font-weight: bold; width: 40%; color: #333; }
            .key { background-color: #f0f0f0; padding: 2px 6px; border-radius: 3px; 
                   font-family: monospace; border: 1px solid #ccc; }
        </style>
        
        <h3>File Operations</h3>
        <table>
            <tr><td><span class="key">Ctrl+O</span></td><td>Open data file (CSV or Excel)</td></tr>
            <tr><td><span class="key">Ctrl+S</span></td><td>Save current report</td></tr>
            <tr><td><span class="key">Ctrl+Shift+S</span></td><td>Save report as...</td></tr>
            <tr><td><span class="key">Ctrl+E</span></td><td>Export chart as image</td></tr>
            <tr><td><span class="key">Ctrl+Q</span></td><td>Quit application</td></tr>
        </table>
        
        <h3>Navigation</h3>
        <table>
            <tr><td><span class="key">Tab</span></td><td>Move to next control</td></tr>
            <tr><td><span class="key">Shift+Tab</span></td><td>Move to previous control</td></tr>
            <tr><td><span class="key">Ctrl+Tab</span></td><td>Switch to next tab</td></tr>
            <tr><td><span class="key">Ctrl+Shift+Tab</span></td><td>Switch to previous tab</td></tr>
            <tr><td><span class="key">Alt+1</span> through <span class="key">Alt+9</span></td><td>Jump to tab 1-9</td></tr>
            <tr><td><span class="key">F6</span></td><td>Move between panes</td></tr>
        </table>
        
        <h3>Analysis Actions</h3>
        <table>
            <tr><td><span class="key">Ctrl+G</span></td><td>Generate CiviQual 4-Up Chart</td></tr>
            <tr><td><span class="key">Ctrl+D</span></td><td>Run descriptive statistics</td></tr>
            <tr><td><span class="key">Ctrl+I</span></td><td>Generate I-Chart</td></tr>
            <tr><td><span class="key">Ctrl+A</span></td><td>Run ANOVA analysis</td></tr>
            <tr><td><span class="key">Ctrl+P</span></td><td>Generate Pareto chart</td></tr>
            <tr><td><span class="key">Ctrl+R</span></td><td>Generate report</td></tr>
        </table>
        
        <h3>Data Operations</h3>
        <table>
            <tr><td><span class="key">Ctrl+F</span></td><td>Find in data table</td></tr>
            <tr><td><span class="key">Ctrl+C</span></td><td>Copy selected data</td></tr>
            <tr><td><span class="key">Ctrl+Home</span></td><td>Go to first row</td></tr>
            <tr><td><span class="key">Ctrl+End</span></td><td>Go to last row</td></tr>
        </table>
        
        <h3>Help &amp; Accessibility</h3>
        <table>
            <tr><td><span class="key">F1</span></td><td>Open Quick Reference guide</td></tr>
            <tr><td><span class="key">Ctrl+?</span></td><td>Show keyboard shortcuts (this dialog)</td></tr>
            <tr><td><span class="key">Ctrl+Shift+A</span></td><td>Accessibility information</td></tr>
            <tr><td><span class="key">Escape</span></td><td>Close current dialog</td></tr>
        </table>
        
        <h3>Screen Reader Tips</h3>
        <table>
            <tr><td><span class="key">Arrow Keys</span></td><td>Navigate within lists and tables</td></tr>
            <tr><td><span class="key">Space</span></td><td>Toggle checkboxes, activate buttons</td></tr>
            <tr><td><span class="key">Enter</span></td><td>Activate focused button or link</td></tr>
            <tr><td><span class="key">Alt+Down</span></td><td>Open dropdown menu</td></tr>
        </table>
        """


# =============================================================================
# Accessibility Information Dialog
# =============================================================================
class AccessibilityInfoDialog(QDialog):
    """Dialog providing accessibility information and features."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Accessibility Information")
        self.setMinimumSize(650, 550)
        self.setModal(True)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Accessibility Information")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAccessibleName("Accessibility Information Dialog Title")
        layout.addWidget(title)
        
        # Content browser
        content = QTextBrowser()
        content.setAccessibleName("Accessibility features and information")
        content.setAccessibleDescription("Detailed information about CiviQual's accessibility features and compliance")
        content.setOpenExternalLinks(True)
        content.setHtml(self._get_accessibility_html())
        layout.addWidget(content)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setAccessibleName("Close accessibility information dialog")
        close_btn.setAccessibleDescription("Press Enter or click to close this dialog")
        close_btn.clicked.connect(self.accept)
        close_btn.setDefault(True)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _get_accessibility_html(self):
        """Generate HTML content for accessibility information."""
        return """
        <style>
            body { font-family: Arial, Arial, sans-serif; line-height: 1.5; }
            h3 { color: #6d132a; margin-top: 15px; margin-bottom: 8px; border-bottom: 1px solid #dcad73; }
            h4 { color: #333; margin-top: 12px; margin-bottom: 5px; }
            ul { margin-left: 20px; }
            li { margin-bottom: 5px; }
            .highlight { background-color: #f0f8ff; padding: 10px; border-left: 3px solid #dcad73; margin: 10px 0; }
            a { color: #6d132a; }
        </style>
        
        <h3>Section 508 Compliance</h3>
        <p>CiviQual version 1.3 has been designed to meet <strong>Section 508 of the Rehabilitation Act</strong> 
        and <strong>WCAG 2.0 Level AA</strong> accessibility standards. These standards ensure that people 
        with disabilities can effectively use the software.</p>
        
        <h3>Accessibility Features</h3>
        
        <h4>Keyboard Navigation</h4>
        <ul>
            <li>All features accessible via keyboard without requiring a mouse</li>
            <li>Logical tab order follows visual layout</li>
            <li>Keyboard shortcuts for common actions (press <strong>Ctrl+?</strong> for full list)</li>
            <li>Focus indicators clearly visible on all interactive elements</li>
        </ul>
        
        <h4>Screen Reader Support</h4>
        <ul>
            <li>All controls have accessible names and descriptions</li>
            <li>Form labels properly associated with input fields</li>
            <li>Charts include text descriptions of statistical results</li>
            <li>Status messages announced to assistive technology</li>
            <li>Compatible with NVDA, JAWS, and Windows Narrator</li>
        </ul>
        
        <h4>Visual Accessibility</h4>
        <ul>
            <li>Color contrast meets WCAG AA requirements (4.5:1 minimum)</li>
            <li>Focus indicators use blue outline (#dcad73) for high visibility</li>
            <li>Text remains readable when resized up to 200%</li>
            <li>Information not conveyed by color alone</li>
            <li>Compatible with Windows High Contrast mode</li>
        </ul>
        
        <h4>Motor Accessibility</h4>
        <ul>
            <li>Large click targets (minimum 44x44 pixels)</li>
            <li>No time limits on user actions</li>
            <li>Drag-and-drop operations have keyboard alternatives</li>
        </ul>
        
        <div class="highlight">
            <strong>Tip:</strong> Press <strong>F1</strong> at any time to open the Quick Reference guide, 
            or <strong>Ctrl+?</strong> to see all keyboard shortcuts.
        </div>
        
        <h3>Assistive Technology Compatibility</h3>
        <p>CiviQual has been tested with:</p>
        <ul>
            <li>NVDA (NonVisual Desktop Access) - Free screen reader</li>
            <li>Windows Narrator - Built into Windows</li>
            <li>Windows Magnifier - Built into Windows</li>
            <li>Windows High Contrast themes</li>
        </ul>
        
        <h3>Accessibility Feedback</h3>
        <p>We are committed to making CiviQual accessible to all users. If you encounter any 
        accessibility barriers or have suggestions for improvement, please contact us:</p>
        <ul>
            <li><strong>Website:</strong> <a href="https://www.qualityincourts.com">www.qualityincourts.com</a></li>
            <li><strong>Email:</strong> accessibility@qualityincourts.com</li>
        </ul>
        
        <h3>External Resources</h3>
        <ul>
            <li><a href="https://www.section508.gov">Section 508 Standards</a></li>
            <li><a href="https://www.w3.org/WAI/WCAG21/quickref/">WCAG 2.1 Quick Reference</a></li>
            <li><a href="https://www.nvaccess.org">NVDA Screen Reader (Free)</a></li>
            <li><a href="https://accessibilityinsights.io">Accessibility Insights (Testing Tool)</a></li>
        </ul>
        """


# =============================================================================
# License Dialog
# =============================================================================
class LicenseDialog(QDialog):
    """License acceptance dialog shown on first run."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CiviQual License Agreement")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        self.accepted_license = False
        self.dont_show_again = False
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("CiviQual Software License Agreement")
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
        """Get license text as HTML."""
        return """
        <style>
            body { font-family: Arial, Arial, sans-serif; }
            h3 { color: #6d132a; }
        </style>
        
        <h3>CiviQual Software License</h3>
        <h4>Public Sector and Nonprofit License</h4>
        
        <p>Copyright © 2025 A Step in the Right Direction LLC. All Rights Reserved.</p>
        
        <p><strong>FREE USE PERMITTED FOR:</strong></p>
        <ul>
            <li>Government agencies (federal, state, local, tribal)</li>
            <li>Courts and judicial organizations</li>
            <li>Public educational institutions</li>
            <li>501(c)(3) nonprofit organizations</li>
            <li>Charitable, educational, and religious organizations</li>
        </ul>
        
        <p><strong>COMMERCIAL USE:</strong> For-profit commercial use requires a separate 
        commercial license. Contact www.qualityincourts.com for licensing information.</p>
        
        <p><strong>RESTRICTIONS:</strong></p>
        <ul>
            <li>You may not redistribute this software</li>
            <li>You may not modify or create derivative works</li>
            <li>You may not reverse engineer, decompile, or disassemble this software</li>
            <li>You may not remove any copyright notices or proprietary labels</li>
        </ul>
        
        <p><strong>WARRANTY DISCLAIMER:</strong> THE SOFTWARE IS PROVIDED "AS IS" WITHOUT 
        WARRANTY OF ANY KIND, EXPRESS OR IMPLIED. A STEP IN THE RIGHT DIRECTION LLC SHALL 
        NOT BE LIABLE FOR ANY DAMAGES ARISING FROM THE USE OF THIS SOFTWARE.</p>
        
        <p><strong>By clicking "I Accept" you agree to these license terms.</strong></p>
        """
    
    def _accept(self):
        """Handle license acceptance."""
        self.accepted_license = True
        self.dont_show_again = self.dont_show_checkbox.isChecked()
        self.accept()
    
    def _decline(self):
        """Handle license decline."""
        self.accepted_license = False
        self.reject()
    
    def closeEvent(self, event):
        """Handle dialog close - treat as decline."""
        if not self.accepted_license:
            self.reject()
        event.accept()


# =============================================================================
# About Dialog
# =============================================================================
class AboutDialog(QDialog):
    """About dialog with application information."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About CiviQual")
        self.setFixedSize(500, 580)
        self.setModal(True)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = self._create_logo()
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setAccessibleName("CiviQual logo")
        layout.addWidget(logo_label)
        
        # Title
        title = QLabel("CiviQual")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #6d132a;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setAccessibleName("CiviQual application title")
        layout.addWidget(title)
        
        # Product subtitle
        product_subtitle = QLabel("Quality Analytics for Public Service")
        product_subtitle.setFont(QFont("Arial", 12))
        product_subtitle.setStyleSheet("color: #6d132a; ")
        product_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(product_subtitle)
        
        # Tagline
        subtitle = QLabel("Statistical Analysis for Lean Six Sigma\nin Government and Courts")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 10px; color: #666;")
        subtitle.setAccessibleName("CiviQual tagline")
        layout.addWidget(subtitle)
        
        # Version
        version = QLabel(f"Version {VERSION}")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet("font-weight: bold;")
        version.setAccessibleName(f"Version {VERSION}")
        layout.addWidget(version)
        
        # Tagline
        tagline = QLabel('"Quality in Every Process"')
        tagline.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        tagline.setStyleSheet("color: #4a0919; ")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tagline)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #6d132a;")
        layout.addWidget(line)
        
        # Description
        desc = QLabel(
            "A statistical analysis tool for Lean Six Sigma practitioners\n"
            "in government and public service organizations.\n\n"
            "The 4-Up Chart methodology is based on the exploratory\n"
            "data analysis approach developed by Dr. Gregory H. Watson."
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 10px;")
        layout.addWidget(desc)
        
        # Copyright
        copyright_label = QLabel(
            "© 2026 A Step in the Right Direction LLC\n"
            "www.qualityincourts.com"
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
    
    def _create_logo(self):
        """Create CiviQual logo programmatically."""
        pixmap = QPixmap(80, 80)
        pixmap.fill(QColor("#6d132a"))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # White inner area
        painter.setBrush(QBrush(QColor("white")))
        painter.setPen(QPen(QColor("white")))
        painter.drawRoundedRect(5, 5, 70, 70, 6, 6)
        
        # Burgundy dividing lines (4-Up grid)
        pen = QPen(QColor("#6d132a"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(40, 8, 40, 72)
        painter.drawLine(8, 40, 72, 40)
        
        # Bar chart in upper-left quadrant
        painter.setBrush(QBrush(QColor("#6d132a")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(12, 28, 6, 10)
        painter.drawRect(20, 20, 6, 18)
        painter.drawRect(28, 14, 6, 24)
        
        # Bell curve hint in upper-right (gold accent)
        painter.setPen(QPen(QColor("#dcad73"), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(46, 12, 20, 24, 0, 180 * 16)
        
        # Control chart hint in lower-left
        painter.setPen(QPen(QColor("#6d132a"), 2))
        points = [(12, 58), (20, 52), (28, 56), (36, 50)]
        for i in range(len(points) - 1):
            painter.drawLine(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
        
        # Scatter plot hint in lower-right (gold accent)
        painter.setBrush(QBrush(QColor("#dcad73")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(50, 48, 5, 5)
        painter.drawEllipse(58, 54, 5, 5)
        painter.drawEllipse(54, 62, 5, 5)
        painter.drawEllipse(66, 58, 5, 5)
        
        painter.end()
        return pixmap


# =============================================================================
# Main Window
# =============================================================================
class MainWindow(QMainWindow):
    """Main application window for CiviQual with Section 508 accessibility."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CiviQual")
        self.setMinimumSize(1200, 800)
        
        # Set window icon
        self._create_window_icon()
        
        # Initialize data storage
        self.data = None
        self.data_handler = DataHandler()
        self.stats_engine = StatisticsEngine()
        self.viz_engine = VisualizationEngine()
        self.report_gen = ReportGenerator()
        
        # Load configuration
        self.config = load_config()
        
        # Setup UI
        self._create_menu_bar()
        self._create_main_layout()
        self._create_status_bar()
        self._setup_keyboard_shortcuts()
        
        # Apply styling
        self._apply_styles()
        
        # Set initial focus
        self.load_btn.setFocus()
    
    def _create_window_icon(self):
        """Create a default icon for the window."""
        try:
            icon_path = Path(__file__).parent / "civiqual_icon.png"
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
            else:
                self._create_default_icon()
        except Exception:
            pass
    
    def _create_default_icon(self):
        """Create a programmatic icon if file not found."""
        try:
            pixmap = QPixmap(64, 64)
            pixmap.fill(QColor("#6d132a"))
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # White inner square
            painter.setBrush(QBrush(QColor("white")))
            painter.setPen(QPen(QColor("white")))
            painter.drawRoundedRect(4, 4, 56, 56, 4, 4)
            
            # Burgundy dividing lines
            pen = QPen(QColor("#6d132a"))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawLine(32, 6, 32, 58)
            painter.drawLine(6, 32, 58, 32)
            
            # Gold accent elements
            painter.setBrush(QBrush(QColor("#dcad73")))
            painter.setPen(QPen(QColor("#dcad73")))
            painter.drawRect(10, 20, 4, 8)
            painter.drawRect(16, 14, 4, 14)
            painter.drawRect(22, 10, 4, 18)
            
            painter.end()
            self.setWindowIcon(QIcon(pixmap))
        except Exception:
            pass
    
    def _create_menu_bar(self):
        """Create the application menu bar with accessibility support."""
        menubar = self.menuBar()
        menubar.setAccessibleName("Main menu bar")
        
        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.setAccessibleName("File menu")
        
        open_action = QAction("&Open Data File...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.setStatusTip("Open a CSV or Excel data file")
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_report_action = QAction("&Save Report...", self)
        save_report_action.setShortcut(QKeySequence.StandardKey.Save)
        save_report_action.setStatusTip("Save the current analysis report")
        save_report_action.triggered.connect(self._save_report)
        file_menu.addAction(save_report_action)
        
        export_chart_action = QAction("&Export Chart...", self)
        export_chart_action.setShortcut("Ctrl+E")
        export_chart_action.setStatusTip("Export the current chart as an image")
        export_chart_action.triggered.connect(self._export_chart)
        file_menu.addAction(export_chart_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Analysis menu
        analysis_menu = menubar.addMenu("&Analysis")
        analysis_menu.setAccessibleName("Analysis menu")
        
        four_up_action = QAction("CiviQual &4-Up Chart", self)
        four_up_action.setShortcut("Ctrl+G")
        four_up_action.setStatusTip("Generate CiviQual 4-Up exploratory data analysis chart")
        four_up_action.triggered.connect(self._generate_four_up)
        analysis_menu.addAction(four_up_action)
        
        descriptive_action = QAction("&Descriptive Statistics", self)
        descriptive_action.setShortcut("Ctrl+D")
        descriptive_action.setStatusTip("Calculate descriptive statistics")
        descriptive_action.triggered.connect(self._run_descriptive)
        analysis_menu.addAction(descriptive_action)
        
        analysis_menu.addSeparator()
        
        ichart_action = QAction("&I-Chart", self)
        ichart_action.setShortcut("Ctrl+I")
        ichart_action.setStatusTip("Generate individuals control chart")
        ichart_action.triggered.connect(self._generate_ichart)
        analysis_menu.addAction(ichart_action)
        
        anova_action = QAction("&ANOVA", self)
        anova_action.setShortcut("Ctrl+Shift+A")
        anova_action.setStatusTip("Run analysis of variance")
        anova_action.triggered.connect(self._run_anova)
        analysis_menu.addAction(anova_action)
        
        pareto_action = QAction("&Pareto Chart", self)
        pareto_action.setShortcut("Ctrl+P")
        pareto_action.setStatusTip("Generate Pareto chart")
        pareto_action.triggered.connect(self._generate_pareto)
        analysis_menu.addAction(pareto_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        help_menu.setAccessibleName("Help menu")
        
        guide_action = QAction("&Quick Reference", self)
        guide_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        guide_action.setStatusTip("Show quick reference guide")
        guide_action.triggered.connect(self._show_guide)
        help_menu.addAction(guide_action)
        
        shortcuts_action = QAction("&Keyboard Shortcuts...", self)
        shortcuts_action.setShortcut("Ctrl+?")
        shortcuts_action.setStatusTip("Show all keyboard shortcuts")
        shortcuts_action.triggered.connect(self._show_keyboard_shortcuts)
        help_menu.addAction(shortcuts_action)
        
        accessibility_action = QAction("&Accessibility Information...", self)
        accessibility_action.setShortcut("Ctrl+Shift+F1")
        accessibility_action.setStatusTip("Show accessibility features and information")
        accessibility_action.triggered.connect(self._show_accessibility_info)
        help_menu.addAction(accessibility_action)
        
        help_menu.addSeparator()
        
        user_guide_action = QAction("&User Guide", self)
        user_guide_action.setShortcut("F1")
        user_guide_action.setStatusTip("View the user guide")
        user_guide_action.triggered.connect(self._show_user_guide)
        help_menu.addAction(user_guide_action)
        
        license_action = QAction("View &License...", self)
        license_action.setStatusTip("View the software license")
        license_action.triggered.connect(self._show_license)
        help_menu.addAction(license_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("&About CiviQual", self)
        about_action.setStatusTip("About this application")
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_main_layout(self):
        """Create the main application layout with accessibility support."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Data loading section with accessibility
        data_group = QGroupBox("Data")
        data_group.setAccessibleName("Data loading section")
        data_layout = QHBoxLayout(data_group)
        
        self.load_btn = QPushButton("Load Data File")
        self.load_btn.clicked.connect(self._open_file)
        self.load_btn.setAccessibleName("Load Data File")
        self.load_btn.setAccessibleDescription(
            "Open a CSV or Excel file containing data for analysis. Keyboard shortcut: Ctrl+O"
        )
        self.load_btn.setToolTip("Open a data file (CSV or Excel) - Ctrl+O")
        data_layout.addWidget(self.load_btn)
        
        self.file_label = QLabel("No file loaded")
        self.file_label.setAccessibleName("Current file status")
        self.file_label.setAccessibleDescription("Shows the name of the currently loaded data file")
        data_layout.addWidget(self.file_label)
        
        data_layout.addStretch()
        
        # Column selection with label buddy
        self.column_label = QLabel("Analysis Column:")
        data_layout.addWidget(self.column_label)
        
        self.column_combo = QComboBox()
        self.column_combo.setMinimumWidth(200)
        self.column_combo.currentTextChanged.connect(self._on_column_changed)
        self.column_combo.setAccessibleName("Analysis Column")
        self.column_combo.setAccessibleDescription(
            "Select the numeric column containing data to analyze. Use arrow keys to navigate options."
        )
        self.column_combo.setToolTip("Select the column containing numeric data to analyze")
        self.column_label.setBuddy(self.column_combo)  # Associate label with combo
        data_layout.addWidget(self.column_combo)
        
        # Subgroup column selection
        self.subgroup_label = QLabel("Subgroup Column:")
        data_layout.addWidget(self.subgroup_label)
        
        self.subgroup_combo = QComboBox()
        self.subgroup_combo.setMinimumWidth(150)
        self.subgroup_combo.setAccessibleName("Subgroup Column")
        self.subgroup_combo.setAccessibleDescription(
            "Optional: Select a column for grouping data in analysis. Leave as None for no grouping."
        )
        self.subgroup_combo.setToolTip("Optional: Select a column for rational subgroup analysis")
        self.subgroup_combo.addItem("(None)")
        self.subgroup_label.setBuddy(self.subgroup_combo)
        data_layout.addWidget(self.subgroup_combo)
        
        main_layout.addWidget(data_group)
        
        # Create splitter for data table and analysis
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setAccessibleName("Main content area")
        
        # Data table
        self.data_table = QTableWidget()
        self.data_table.setAccessibleName("Data table")
        self.data_table.setAccessibleDescription(
            "Table showing loaded data. Use arrow keys to navigate cells."
        )
        self.data_table.setToolTip("Data from loaded file")
        splitter.addWidget(self.data_table)
        
        # Analysis tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setAccessibleName("Analysis tabs")
        self.tab_widget.setAccessibleDescription(
            "Switch between different analysis views using Ctrl+Tab or click on tab names"
        )
        self._create_analysis_tabs()
        splitter.addWidget(self.tab_widget)
        
        splitter.setSizes([400, 800])
        main_layout.addWidget(splitter)
    
    def _create_analysis_tabs(self):
        """Create analysis tab widgets with accessibility support."""
        # CiviQual 4-Up Chart tab
        four_up_tab = QWidget()
        four_up_tab.setAccessibleName("CiviQual 4-Up Chart analysis tab")
        four_up_layout = QVBoxLayout(four_up_tab)
        
        four_up_controls = QHBoxLayout()
        
        self.four_up_btn = QPushButton("Generate 4-Up Chart")
        self.four_up_btn.clicked.connect(self._generate_four_up)
        self.four_up_btn.setAccessibleName("Generate CiviQual 4-Up Chart")
        self.four_up_btn.setAccessibleDescription(
            "Generate a CiviQual 4-Up exploratory data analysis chart showing statistical summary, "
            "probability plot, I-Chart, and capability analysis. Keyboard shortcut: Ctrl+G"
        )
        self.four_up_btn.setToolTip("Generate CiviQual 4-Up Chart - Ctrl+G")
        four_up_controls.addWidget(self.four_up_btn)
        
        four_up_controls.addStretch()
        
        # Percentile input with label buddy
        percentile_label = QLabel("Percentile Line:")
        four_up_controls.addWidget(percentile_label)
        
        self.percentile_spin = QSpinBox()
        self.percentile_spin.setRange(1, 99)
        self.percentile_spin.setValue(80)
        self.percentile_spin.setSuffix("%")
        self.percentile_spin.setAccessibleName("Percentile Line Value")
        self.percentile_spin.setAccessibleDescription(
            "Set the percentile line to display on the probability plot. Default is 80 percent."
        )
        self.percentile_spin.setToolTip("Percentile line for probability plot (default: 80%)")
        percentile_label.setBuddy(self.percentile_spin)
        four_up_controls.addWidget(self.percentile_spin)
        
        four_up_layout.addLayout(four_up_controls)
        
        # Chart display area
        self.four_up_display = QLabel("Load data and click 'Generate 4-Up Chart' to begin")
        self.four_up_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.four_up_display.setMinimumHeight(500)
        self.four_up_display.setStyleSheet(get_chart_display_style())
        self.four_up_display.setAccessibleName("CiviQual 4-Up Chart display area")
        self.four_up_display.setAccessibleDescription(
            "Displays the generated CiviQual 4-Up Chart with four analysis views"
        )
        four_up_layout.addWidget(self.four_up_display)
        
        self.tab_widget.addTab(four_up_tab, "CiviQual 4-Up Chart")
        
        # Descriptive Statistics tab
        desc_tab = QWidget()
        desc_tab.setAccessibleName("Descriptive Statistics analysis tab")
        desc_layout = QVBoxLayout(desc_tab)
        
        desc_btn = QPushButton("Calculate Statistics")
        desc_btn.clicked.connect(self._run_descriptive)
        desc_btn.setAccessibleName("Calculate Descriptive Statistics")
        desc_btn.setAccessibleDescription(
            "Calculate mean, median, standard deviation, and other descriptive statistics "
            "for the selected column. Keyboard shortcut: Ctrl+D"
        )
        desc_btn.setToolTip("Calculate descriptive statistics - Ctrl+D")
        desc_layout.addWidget(desc_btn)
        
        self.desc_output = QTextEdit()
        self.desc_output.setReadOnly(True)
        self.desc_output.setAccessibleName("Descriptive statistics results")
        self.desc_output.setAccessibleDescription(
            "Displays calculated statistics including mean, median, standard deviation, "
            "quartiles, and normality test results"
        )
        desc_layout.addWidget(self.desc_output)
        
        self.tab_widget.addTab(desc_tab, "Descriptive Statistics")
        
        # Control Charts tab
        control_tab = QWidget()
        control_tab.setAccessibleName("Control Charts analysis tab")
        control_layout = QVBoxLayout(control_tab)
        
        control_controls = QHBoxLayout()
        
        ichart_btn = QPushButton("Generate I-Chart")
        ichart_btn.clicked.connect(self._generate_ichart)
        ichart_btn.setAccessibleName("Generate I-Chart")
        ichart_btn.setAccessibleDescription(
            "Generate an Individuals control chart to assess process stability. "
            "Keyboard shortcut: Ctrl+I"
        )
        ichart_btn.setToolTip("Generate I-Chart - Ctrl+I")
        control_controls.addWidget(ichart_btn)
        
        mr_btn = QPushButton("Generate MR Chart")
        mr_btn.clicked.connect(self._generate_mr)
        mr_btn.setAccessibleName("Generate MR Chart")
        mr_btn.setAccessibleDescription(
            "Generate a Moving Range control chart to assess process variability"
        )
        mr_btn.setToolTip("Generate Moving Range Chart")
        control_controls.addWidget(mr_btn)
        
        imr_btn = QPushButton("Generate I-MR Chart")
        imr_btn.clicked.connect(self._generate_imr)
        imr_btn.setAccessibleName("Generate I-MR Chart")
        imr_btn.setAccessibleDescription(
            "Generate combined Individuals and Moving Range control charts"
        )
        imr_btn.setToolTip("Generate I-MR Chart")
        control_controls.addWidget(imr_btn)
        
        control_controls.addStretch()
        
        # Western Electric rules checkboxes
        rules_label = QLabel("Apply Rules:")
        control_controls.addWidget(rules_label)
        
        self.rule1_check = QCheckBox("Test 1 (3σ)")
        self.rule1_check.setChecked(True)
        self.rule1_check.setAccessibleName("Test 1: Point beyond 3 sigma")
        self.rule1_check.setAccessibleDescription(
            "Apply Western Electric Test 1: Flag points beyond 3 standard deviations from center"
        )
        self.rule1_check.setToolTip("Point beyond 3σ from center line")
        control_controls.addWidget(self.rule1_check)
        
        self.rule2_check = QCheckBox("Test 2")
        self.rule2_check.setChecked(True)
        self.rule2_check.setAccessibleName("Test 2: 2 of 3 beyond 2 sigma")
        self.rule2_check.setAccessibleDescription(
            "Apply Western Electric Test 2: Flag when 2 of 3 points are beyond 2 sigma"
        )
        self.rule2_check.setToolTip("2 of 3 points beyond 2σ (same side)")
        control_controls.addWidget(self.rule2_check)
        
        self.rule3_check = QCheckBox("Test 3")
        self.rule3_check.setChecked(True)
        self.rule3_check.setAccessibleName("Test 3: 4 of 5 beyond 1 sigma")
        self.rule3_check.setAccessibleDescription(
            "Apply Western Electric Test 3: Flag when 4 of 5 points are beyond 1 sigma"
        )
        self.rule3_check.setToolTip("4 of 5 points beyond 1σ (same side)")
        control_controls.addWidget(self.rule3_check)
        
        self.rule4_check = QCheckBox("Test 4")
        self.rule4_check.setChecked(True)
        self.rule4_check.setAccessibleName("Test 4: 8 consecutive same side")
        self.rule4_check.setAccessibleDescription(
            "Apply Western Electric Test 4: Flag 8 consecutive points on same side of center"
        )
        self.rule4_check.setToolTip("8 consecutive points same side of center")
        control_controls.addWidget(self.rule4_check)
        
        control_layout.addLayout(control_controls)
        
        # Split layout for chart and analysis
        control_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.control_display = QLabel("Load data and select chart type")
        self.control_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.control_display.setMinimumHeight(400)
        self.control_display.setMinimumWidth(500)
        self.control_display.setStyleSheet(get_chart_display_style())
        self.control_display.setAccessibleName("Control chart display area")
        control_splitter.addWidget(self.control_display)
        
        # Analysis output panel
        self.control_analysis = QTextEdit()
        self.control_analysis.setReadOnly(True)
        self.control_analysis.setMinimumWidth(350)
        self.control_analysis.setAccessibleName("Control chart analysis output")
        self.control_analysis.setPlaceholderText("Analysis results will appear here after generating a chart.")
        self.control_analysis.setStyleSheet(
            "font-family: Arial; font-size: 10pt; padding: 10px;"
        )
        control_splitter.addWidget(self.control_analysis)
        
        control_splitter.setSizes([550, 350])
        control_layout.addWidget(control_splitter)
        
        self.tab_widget.addTab(control_tab, "Control Charts")
        
        # Capability Analysis tab
        capability_tab = QWidget()
        capability_tab.setAccessibleName("Capability Analysis tab")
        cap_layout = QVBoxLayout(capability_tab)
        
        cap_controls = QHBoxLayout()
        
        cap_btn = QPushButton("Calculate Capability")
        cap_btn.clicked.connect(self._run_capability)
        cap_btn.setAccessibleName("Calculate Process Capability")
        cap_btn.setAccessibleDescription(
            "Calculate Cp, Cpk, Cpu, and Cpl capability indices"
        )
        cap_btn.setToolTip("Calculate capability indices")
        cap_controls.addWidget(cap_btn)
        
        cap_controls.addStretch()
        
        # Specification limits with label buddies
        lsl_label = QLabel("LSL:")
        cap_controls.addWidget(lsl_label)
        
        self.lsl_input = QDoubleSpinBox()
        self.lsl_input.setRange(-1000000, 1000000)
        self.lsl_input.setDecimals(2)
        self.lsl_input.setSpecialValueText("Not Set")
        self.lsl_input.setValue(self.lsl_input.minimum())
        self.lsl_input.setAccessibleName("Lower Specification Limit")
        self.lsl_input.setAccessibleDescription(
            "Enter the lower specification limit for capability analysis. Leave at minimum for no LSL."
        )
        self.lsl_input.setToolTip("Lower Specification Limit")
        lsl_label.setBuddy(self.lsl_input)
        cap_controls.addWidget(self.lsl_input)
        
        usl_label = QLabel("USL:")
        cap_controls.addWidget(usl_label)
        
        self.usl_input = QDoubleSpinBox()
        self.usl_input.setRange(-1000000, 1000000)
        self.usl_input.setDecimals(2)
        self.usl_input.setSpecialValueText("Not Set")
        self.usl_input.setValue(self.usl_input.minimum())
        self.usl_input.setAccessibleName("Upper Specification Limit")
        self.usl_input.setAccessibleDescription(
            "Enter the upper specification limit for capability analysis. Leave at minimum for no USL."
        )
        self.usl_input.setToolTip("Upper Specification Limit")
        usl_label.setBuddy(self.usl_input)
        cap_controls.addWidget(self.usl_input)
        
        target_label = QLabel("Target:")
        cap_controls.addWidget(target_label)
        
        self.target_input = QDoubleSpinBox()
        self.target_input.setRange(-1000000, 1000000)
        self.target_input.setDecimals(2)
        self.target_input.setSpecialValueText("Not Set")
        self.target_input.setValue(self.target_input.minimum())
        self.target_input.setAccessibleName("Target Value")
        self.target_input.setToolTip("Target Value (optional)")
        target_label.setBuddy(self.target_input)
        cap_controls.addWidget(self.target_input)
        
        cap_layout.addLayout(cap_controls)
        
        # Second row: Cp=1.0 option
        cap_options = QHBoxLayout()
        
        self.cp_one_checkbox = QCheckBox("Show Cp=1.0 Natural Tolerance Limits")
        self.cp_one_checkbox.setAccessibleName("Show Cp equals 1.0 limits")
        self.cp_one_checkbox.setAccessibleDescription(
            "Calculate and display specification limits that would result in Cp=1.0 based on current process variation"
        )
        self.cp_one_checkbox.setToolTip(
            "Shows what USL/LSL would need to be for Cp=1.0 (process just capable)"
        )
        cap_options.addWidget(self.cp_one_checkbox)
        
        cap_options.addStretch()
        cap_layout.addLayout(cap_options)
        
        # Splitter for chart and results
        cap_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Capability chart display
        self.capability_chart_display = QLabel("Select column and spec limits, then click Calculate")
        self.capability_chart_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.capability_chart_display.setMinimumHeight(300)
        self.capability_chart_display.setStyleSheet(get_chart_display_style())
        self.capability_chart_display.setAccessibleName("Capability analysis chart")
        cap_splitter.addWidget(self.capability_chart_display)
        
        self.capability_output = QTextEdit()
        self.capability_output.setReadOnly(True)
        self.capability_output.setMinimumHeight(200)
        self.capability_output.setAccessibleName("Capability analysis results")
        self.capability_output.setAccessibleDescription(
            "Displays calculated capability indices and interpretation"
        )
        cap_splitter.addWidget(self.capability_output)
        
        cap_splitter.setSizes([350, 200])
        cap_layout.addWidget(cap_splitter)
        
        self.tab_widget.addTab(capability_tab, "Capability Analysis")
        
        # =================================================================
        # Probability Plot tab (with multiple series support)
        # =================================================================
        prob_plot_tab = QWidget()
        prob_plot_tab.setAccessibleName("Probability Plot tab - Measure Phase")
        prob_plot_layout = QVBoxLayout(prob_plot_tab)
        
        prob_header = QLabel("<b>Probability Plot</b> - Compare distributions of multiple data series")
        prob_header.setAccessibleName("Probability plot description")
        prob_plot_layout.addWidget(prob_header)
        
        prob_controls = QHBoxLayout()
        
        prob_btn = QPushButton("Generate Probability Plot")
        prob_btn.clicked.connect(self._generate_probability_plot)
        prob_btn.setAccessibleName("Generate Probability Plot")
        prob_btn.setToolTip("Generate probability plot for selected columns")
        prob_controls.addWidget(prob_btn)
        
        prob_controls.addStretch()
        
        prob_controls.addWidget(QLabel("Select columns to compare:"))
        
        prob_plot_layout.addLayout(prob_controls)
        
        # List widget for selecting multiple columns
        self.prob_plot_columns = QListWidget()
        self.prob_plot_columns.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.prob_plot_columns.setMaximumHeight(120)
        self.prob_plot_columns.setAccessibleName("Column selection for probability plot")
        self.prob_plot_columns.setAccessibleDescription(
            "Select one or more numeric columns to display on probability plot. "
            "Hold Ctrl to select multiple columns."
        )
        prob_plot_layout.addWidget(self.prob_plot_columns)
        
        self.prob_plot_display = QLabel("Select columns and click Generate")
        self.prob_plot_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prob_plot_display.setMinimumHeight(400)
        self.prob_plot_display.setStyleSheet(get_chart_display_style())
        self.prob_plot_display.setAccessibleName("Probability plot display area")
        prob_plot_layout.addWidget(self.prob_plot_display)
        
        self.prob_plot_output = QTextEdit()
        self.prob_plot_output.setReadOnly(True)
        self.prob_plot_output.setMaximumHeight(100)
        self.prob_plot_output.setAccessibleName("Probability plot statistics")
        prob_plot_layout.addWidget(self.prob_plot_output)
        
        self.tab_widget.addTab(prob_plot_tab, "Probability Plot")
        
        # ANOVA tab
        anova_tab = QWidget()
        anova_tab.setAccessibleName("ANOVA analysis tab")
        anova_layout = QVBoxLayout(anova_tab)
        
        anova_btn = QPushButton("Run ANOVA")
        anova_btn.clicked.connect(self._run_anova)
        anova_btn.setAccessibleName("Run ANOVA Analysis")
        anova_btn.setAccessibleDescription(
            "Run Analysis of Variance using the selected subgroup column. "
            "Displays box plots and statistical results. Keyboard shortcut: Ctrl+Shift+A"
        )
        anova_btn.setToolTip("Run ANOVA - Ctrl+Shift+A")
        anova_layout.addWidget(anova_btn)
        
        # Splitter for box plot and results
        anova_splitter = QSplitter(Qt.Orientation.Vertical)
        anova_splitter.setAccessibleName("ANOVA results splitter")
        
        # Box plot display area
        self.anova_chart_display = QLabel("Run ANOVA to display box plots by group")
        self.anova_chart_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.anova_chart_display.setMinimumHeight(350)
        self.anova_chart_display.setStyleSheet(get_chart_display_style())
        self.anova_chart_display.setAccessibleName("ANOVA box plot display")
        self.anova_chart_display.setAccessibleDescription(
            "Displays box plots showing the distribution of data for each group in the factor"
        )
        anova_splitter.addWidget(self.anova_chart_display)
        
        # Text output for ANOVA results
        self.anova_output = QTextEdit()
        self.anova_output.setReadOnly(True)
        self.anova_output.setMaximumHeight(200)
        self.anova_output.setAccessibleName("ANOVA results")
        self.anova_output.setAccessibleDescription(
            "Displays ANOVA table with F-statistic, p-value, and interpretation"
        )
        anova_splitter.addWidget(self.anova_output)
        
        anova_splitter.setSizes([400, 150])
        anova_layout.addWidget(anova_splitter)
        
        self.tab_widget.addTab(anova_tab, "ANOVA")
        
        # =================================================================
        # Correlation Analysis tab
        # =================================================================
        correlation_tab = QWidget()
        correlation_tab.setAccessibleName("Correlation Analysis tab - Analyze Phase")
        correlation_layout = QVBoxLayout(correlation_tab)
        
        correlation_header = QLabel("<b>Correlation Analysis</b> - Examine relationship between two variables")
        correlation_header.setAccessibleName("Correlation analysis description")
        correlation_layout.addWidget(correlation_header)
        
        correlation_controls = QHBoxLayout()
        
        # X variable selection
        x_label = QLabel("X Variable:")
        correlation_controls.addWidget(x_label)
        
        self.corr_x_combo = QComboBox()
        self.corr_x_combo.setMinimumWidth(150)
        self.corr_x_combo.setAccessibleName("X Variable for correlation")
        self.corr_x_combo.setToolTip("Select the independent (X) variable")
        x_label.setBuddy(self.corr_x_combo)
        correlation_controls.addWidget(self.corr_x_combo)
        
        # Y variable selection
        y_label = QLabel("Y Variable:")
        correlation_controls.addWidget(y_label)
        
        self.corr_y_combo = QComboBox()
        self.corr_y_combo.setMinimumWidth(150)
        self.corr_y_combo.setAccessibleName("Y Variable for correlation")
        self.corr_y_combo.setToolTip("Select the dependent (Y) variable")
        y_label.setBuddy(self.corr_y_combo)
        correlation_controls.addWidget(self.corr_y_combo)
        
        correlation_controls.addStretch()
        
        self.show_regression_check = QCheckBox("Show Regression Line")
        self.show_regression_check.setChecked(True)
        self.show_regression_check.setAccessibleName("Show regression line checkbox")
        correlation_controls.addWidget(self.show_regression_check)
        
        correlation_layout.addLayout(correlation_controls)
        
        corr_btn = QPushButton("Generate Correlation Analysis")
        corr_btn.clicked.connect(self._generate_correlation)
        corr_btn.setAccessibleName("Generate Correlation Analysis button")
        corr_btn.setAccessibleDescription(
            "Generate scatter plot with correlation coefficient, R-squared, and significance test"
        )
        corr_btn.setToolTip("Analyze correlation between selected variables")
        correlation_layout.addWidget(corr_btn)
        
        self.correlation_display = QLabel("Select X and Y variables, then click Generate")
        self.correlation_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.correlation_display.setMinimumHeight(400)
        self.correlation_display.setStyleSheet(get_chart_display_style())
        self.correlation_display.setAccessibleName("Correlation scatter plot display")
        correlation_layout.addWidget(self.correlation_display)
        
        self.correlation_output = QTextEdit()
        self.correlation_output.setReadOnly(True)
        self.correlation_output.setMaximumHeight(120)
        self.correlation_output.setAccessibleName("Correlation analysis results")
        correlation_layout.addWidget(self.correlation_output)
        
        self.tab_widget.addTab(correlation_tab, "Correlation")
        
        # =================================================================
        # Run Chart tab
        # =================================================================
        run_chart_tab = QWidget()
        run_chart_tab.setAccessibleName("Run Chart tab - Measure/Analyze Phase")
        run_chart_layout = QVBoxLayout(run_chart_tab)
        
        run_chart_header = QLabel("<b>Run Chart</b> - Sequential plot with median line (no control limits)")
        run_chart_header.setAccessibleName("Run chart description")
        run_chart_layout.addWidget(run_chart_header)
        
        run_chart_btn = QPushButton("Generate Run Chart")
        run_chart_btn.clicked.connect(self._generate_run_chart)
        run_chart_btn.setAccessibleName("Generate Run Chart button")
        run_chart_btn.setAccessibleDescription(
            "Generate a run chart showing data sequence with median line and runs analysis"
        )
        run_chart_btn.setToolTip("Generate run chart for selected column")
        run_chart_layout.addWidget(run_chart_btn)
        
        self.run_chart_display = QLabel("Select a column and click Generate")
        self.run_chart_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.run_chart_display.setMinimumHeight(400)
        self.run_chart_display.setStyleSheet(get_chart_display_style())
        self.run_chart_display.setAccessibleName("Run chart display area")
        run_chart_layout.addWidget(self.run_chart_display)
        
        self.run_chart_output = QTextEdit()
        self.run_chart_output.setReadOnly(True)
        self.run_chart_output.setMaximumHeight(100)
        self.run_chart_output.setAccessibleName("Run chart analysis results")
        run_chart_layout.addWidget(self.run_chart_output)
        
        self.tab_widget.addTab(run_chart_tab, "Run Chart")
        
        # =================================================================
        # Histogram tab
        # =================================================================
        histogram_tab = QWidget()
        histogram_tab.setAccessibleName("Histogram tab - Measure Phase")
        histogram_layout = QVBoxLayout(histogram_tab)
        
        histogram_header = QLabel("<b>Histogram</b> - Distribution visualization with statistics")
        histogram_header.setAccessibleName("Histogram description")
        histogram_layout.addWidget(histogram_header)
        
        histogram_controls = QHBoxLayout()
        
        histogram_btn = QPushButton("Generate Histogram")
        histogram_btn.clicked.connect(self._generate_histogram)
        histogram_btn.setAccessibleName("Generate Histogram button")
        histogram_btn.setAccessibleDescription(
            "Generate a histogram showing data distribution with mean, median, and normal curve"
        )
        histogram_btn.setToolTip("Generate histogram for selected column")
        histogram_controls.addWidget(histogram_btn)
        
        histogram_controls.addStretch()
        
        self.show_normal_check = QCheckBox("Show Normal Curve")
        self.show_normal_check.setChecked(True)
        self.show_normal_check.setAccessibleName("Show normal distribution curve")
        histogram_controls.addWidget(self.show_normal_check)
        
        bins_label = QLabel("Bins:")
        histogram_controls.addWidget(bins_label)
        
        self.histogram_bins = QSpinBox()
        self.histogram_bins.setRange(5, 50)
        self.histogram_bins.setValue(0)  # 0 means auto
        self.histogram_bins.setSpecialValueText("Auto")
        self.histogram_bins.setAccessibleName("Number of histogram bins")
        self.histogram_bins.setToolTip("Number of bins (0 = automatic)")
        histogram_controls.addWidget(self.histogram_bins)
        
        histogram_layout.addLayout(histogram_controls)
        
        self.histogram_display = QLabel("Select a column and click Generate")
        self.histogram_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.histogram_display.setMinimumHeight(500)
        self.histogram_display.setStyleSheet(get_chart_display_style())
        self.histogram_display.setAccessibleName("Histogram display area")
        histogram_layout.addWidget(self.histogram_display)
        
        self.tab_widget.addTab(histogram_tab, "Histogram")
        
        # =================================================================
        # Box Plot tab
        # =================================================================
        boxplot_tab = QWidget()
        boxplot_tab.setAccessibleName("Box Plot tab - Measure Phase")
        boxplot_layout = QVBoxLayout(boxplot_tab)
        
        boxplot_header = QLabel("<b>Box Plot</b> - Quartile visualization with outlier detection")
        boxplot_header.setAccessibleName("Box plot description")
        boxplot_layout.addWidget(boxplot_header)
        
        boxplot_controls = QHBoxLayout()
        
        boxplot_btn = QPushButton("Generate Box Plot")
        boxplot_btn.clicked.connect(self._generate_boxplot)
        boxplot_btn.setAccessibleName("Generate Box Plot button")
        boxplot_btn.setAccessibleDescription(
            "Generate a box plot showing quartiles, median, mean, and outliers"
        )
        boxplot_btn.setToolTip("Generate box plot for selected column")
        boxplot_controls.addWidget(boxplot_btn)
        
        boxplot_controls.addStretch()
        
        self.show_points_check = QCheckBox("Show Data Points")
        self.show_points_check.setChecked(True)
        self.show_points_check.setAccessibleName("Show individual data points")
        boxplot_controls.addWidget(self.show_points_check)
        
        boxplot_layout.addLayout(boxplot_controls)
        
        self.boxplot_display = QLabel("Select a column and click Generate")
        self.boxplot_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.boxplot_display.setMinimumHeight(500)
        self.boxplot_display.setStyleSheet(get_chart_display_style())
        self.boxplot_display.setAccessibleName("Box plot display area")
        boxplot_layout.addWidget(self.boxplot_display)
        
        self.tab_widget.addTab(boxplot_tab, "Box Plot")
        
        # Pareto tab
        pareto_tab = QWidget()
        pareto_tab.setAccessibleName("Pareto Analysis tab")
        pareto_layout = QVBoxLayout(pareto_tab)
        
        pareto_controls = QHBoxLayout()
        
        pareto_btn = QPushButton("Generate Pareto Chart")
        pareto_btn.clicked.connect(self._generate_pareto)
        pareto_btn.setAccessibleName("Generate Pareto Chart")
        pareto_btn.setAccessibleDescription(
            "Generate a Pareto chart showing the vital few categories. "
            "Keyboard shortcut: Ctrl+P"
        )
        pareto_btn.setToolTip("Generate Pareto Chart - Ctrl+P")
        pareto_controls.addWidget(pareto_btn)
        
        pareto_controls.addStretch()
        
        category_label = QLabel("Category Column:")
        pareto_controls.addWidget(category_label)
        
        self.pareto_column = QComboBox()
        self.pareto_column.setMinimumWidth(150)
        self.pareto_column.setAccessibleName("Pareto Category Column")
        self.pareto_column.setAccessibleDescription(
            "Select the column containing categories for Pareto analysis"
        )
        self.pareto_column.setToolTip("Select category column for Pareto analysis")
        category_label.setBuddy(self.pareto_column)
        pareto_controls.addWidget(self.pareto_column)
        
        pareto_layout.addLayout(pareto_controls)
        
        self.pareto_display = QLabel("Select category column and click Generate")
        self.pareto_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pareto_display.setMinimumHeight(500)
        self.pareto_display.setStyleSheet(get_chart_display_style())
        self.pareto_display.setAccessibleName("Pareto chart display area")
        pareto_layout.addWidget(self.pareto_display)
        
        self.tab_widget.addTab(pareto_tab, "Pareto Analysis")
        
        # ROI Calculator tab
        roi_tab = QWidget()
        roi_tab.setAccessibleName("ROI Calculator tab")
        roi_layout = QVBoxLayout(roi_tab)
        
        roi_form = QFormLayout()
        
        self.hours_saved = QDoubleSpinBox()
        self.hours_saved.setRange(0, 100000)
        self.hours_saved.setDecimals(1)
        self.hours_saved.setAccessibleName("Annual Hours Saved")
        self.hours_saved.setAccessibleDescription(
            "Enter the estimated annual hours saved by the improvement"
        )
        self.hours_saved.setToolTip("Estimated annual hours saved")
        roi_form.addRow("Annual Hours Saved:", self.hours_saved)
        
        self.hourly_rate = QDoubleSpinBox()
        self.hourly_rate.setRange(0, 1000)
        self.hourly_rate.setDecimals(2)
        self.hourly_rate.setValue(32.00)
        self.hourly_rate.setPrefix("$")
        self.hourly_rate.setAccessibleName("Hourly Rate")
        self.hourly_rate.setAccessibleDescription(
            "Enter the average hourly rate for calculating labor savings"
        )
        self.hourly_rate.setToolTip("Average hourly labor rate")
        roi_form.addRow("Hourly Rate:", self.hourly_rate)
        
        self.project_cost = QDoubleSpinBox()
        self.project_cost.setRange(0, 10000000)
        self.project_cost.setDecimals(2)
        self.project_cost.setPrefix("$")
        self.project_cost.setAccessibleName("Project Investment")
        self.project_cost.setAccessibleDescription(
            "Enter the total investment cost for the improvement project"
        )
        self.project_cost.setToolTip("Total project investment cost")
        roi_form.addRow("Project Investment:", self.project_cost)
        
        roi_layout.addLayout(roi_form)
        
        calc_roi_btn = QPushButton("Calculate ROI")
        calc_roi_btn.clicked.connect(self._calculate_roi)
        calc_roi_btn.setAccessibleName("Calculate Return on Investment")
        calc_roi_btn.setAccessibleDescription(
            "Calculate the return on investment based on entered values"
        )
        calc_roi_btn.setToolTip("Calculate ROI")
        roi_layout.addWidget(calc_roi_btn)
        
        self.roi_output = QTextEdit()
        self.roi_output.setReadOnly(True)
        self.roi_output.setAccessibleName("ROI calculation results")
        self.roi_output.setAccessibleDescription(
            "Displays calculated ROI, payback period, and multi-year projections"
        )
        roi_layout.addWidget(self.roi_output)
        
        self.tab_widget.addTab(roi_tab, "ROI Calculator")
        
        # =================================================================
        # Data Sampling Tab
        # =================================================================
        sampling_tab = QWidget()
        sampling_tab.setAccessibleName("Data Sampling tab")
        sampling_layout = QVBoxLayout(sampling_tab)
        
        sampling_header = QLabel("<b>Data Sampling</b> - Select random samples from your data")
        sampling_header.setAccessibleName("Data sampling description")
        sampling_layout.addWidget(sampling_header)
        
        sampling_form = QFormLayout()
        
        self.sampling_column = QComboBox()
        self.sampling_column.setAccessibleName("Column to sample from")
        self.sampling_column.setToolTip("Select the column to sample from")
        sampling_form.addRow("Sample Column:", self.sampling_column)
        
        self.sample_size = QSpinBox()
        self.sample_size.setRange(1, 10000)
        self.sample_size.setValue(30)
        self.sample_size.setAccessibleName("Sample size")
        self.sample_size.setAccessibleDescription("Number of random data points to select, default is 30")
        self.sample_size.setToolTip("Number of random data points to select (default: 30)")
        sampling_form.addRow("Sample Size:", self.sample_size)
        
        self.sampling_seed = QSpinBox()
        self.sampling_seed.setRange(0, 999999)
        self.sampling_seed.setValue(0)
        self.sampling_seed.setSpecialValueText("Random")
        self.sampling_seed.setAccessibleName("Random seed")
        self.sampling_seed.setAccessibleDescription("Set a seed for reproducible sampling, or 0 for random")
        self.sampling_seed.setToolTip("Set seed for reproducible results (0 = random)")
        sampling_form.addRow("Random Seed:", self.sampling_seed)
        
        sampling_layout.addLayout(sampling_form)
        
        sample_btn = QPushButton("Generate Sample")
        sample_btn.clicked.connect(self._generate_sample)
        sample_btn.setAccessibleName("Generate random sample")
        sample_btn.setAccessibleDescription("Generate a random sample from the selected column")
        sample_btn.setToolTip("Generate a random sample from the data")
        sampling_layout.addWidget(sample_btn)
        
        export_sample_btn = QPushButton("Export Sample to CSV")
        export_sample_btn.clicked.connect(self._export_sample)
        export_sample_btn.setAccessibleName("Export sample to CSV file")
        export_sample_btn.setToolTip("Export the generated sample to a CSV file")
        sampling_layout.addWidget(export_sample_btn)
        
        self.sampling_output = QTextEdit()
        self.sampling_output.setReadOnly(True)
        self.sampling_output.setAccessibleName("Sample results")
        self.sampling_output.setAccessibleDescription("Displays the randomly selected sample data")
        sampling_layout.addWidget(self.sampling_output)
        
        self.tab_widget.addTab(sampling_tab, "Data Sampling")
        
        # =================================================================
        # Split Worksheet Tab
        # =================================================================
        split_tab = QWidget()
        split_tab.setAccessibleName("Split Worksheet tab")
        split_layout = QVBoxLayout(split_tab)
        
        split_header = QLabel("<b>Split Worksheet</b> - Split data by categorical factor or rational subgroup")
        split_header.setAccessibleName("Split worksheet description")
        split_layout.addWidget(split_header)
        
        split_form = QFormLayout()
        
        self.split_by_column = QComboBox()
        self.split_by_column.setAccessibleName("Column to split by")
        self.split_by_column.setToolTip("Select the categorical column to split by")
        split_form.addRow("Split By:", self.split_by_column)
        
        self.split_data_column = QComboBox()
        self.split_data_column.setAccessibleName("Data column to include")
        self.split_data_column.setToolTip("Select the data column to include in split files")
        split_form.addRow("Data Column:", self.split_data_column)
        
        split_layout.addLayout(split_form)
        
        split_preview_btn = QPushButton("Preview Split")
        split_preview_btn.clicked.connect(self._preview_split)
        split_preview_btn.setAccessibleName("Preview worksheet split")
        split_preview_btn.setAccessibleDescription("Preview how the data will be split by category")
        split_preview_btn.setToolTip("Preview the split without exporting")
        split_layout.addWidget(split_preview_btn)
        
        split_export_btn = QPushButton("Export Split Files")
        split_export_btn.clicked.connect(self._export_split)
        split_export_btn.setAccessibleName("Export split worksheets")
        split_export_btn.setAccessibleDescription("Export each category to a separate CSV file")
        split_export_btn.setToolTip("Export each category to a separate CSV file")
        split_layout.addWidget(split_export_btn)
        
        self.split_output = QTextEdit()
        self.split_output.setReadOnly(True)
        self.split_output.setAccessibleName("Split preview results")
        self.split_output.setAccessibleDescription("Displays preview of data split by category")
        split_layout.addWidget(self.split_output)
        
        self.tab_widget.addTab(split_tab, "Split Worksheet")
        
        # =================================================================
        # CPI Process Diagram Tabs
        # =================================================================
        
        # Initialize diagram engine
        self.diagram_engine = ProcessDiagramEngine()
        
        # SIPOC Diagram tab (Define Phase)
        sipoc_tab = QWidget()
        sipoc_tab.setAccessibleName("SIPOC Diagram tab - Define Phase")
        sipoc_layout = QVBoxLayout(sipoc_tab)
        
        sipoc_header = QLabel("<b>SIPOC Diagram</b> - Suppliers → Inputs → Process → Outputs → Customers")
        sipoc_header.setAccessibleName("SIPOC diagram description")
        sipoc_layout.addWidget(sipoc_header)
        
        sipoc_form = QFormLayout()
        
        self.sipoc_title = QLineEdit()
        self.sipoc_title.setPlaceholderText("Enter diagram title")
        self.sipoc_title.setText("SIPOC Diagram")
        self.sipoc_title.setAccessibleName("SIPOC diagram title")
        self.sipoc_title.setToolTip("Enter the title for your SIPOC diagram")
        sipoc_form.addRow("Title:", self.sipoc_title)
        
        self.sipoc_suppliers = QTextEdit()
        self.sipoc_suppliers.setPlaceholderText("Enter suppliers (one per line)")
        self.sipoc_suppliers.setMaximumHeight(80)
        self.sipoc_suppliers.setAccessibleName("Suppliers list")
        self.sipoc_suppliers.setToolTip("List the suppliers who provide inputs to the process")
        sipoc_form.addRow("Suppliers:", self.sipoc_suppliers)
        
        self.sipoc_inputs = QTextEdit()
        self.sipoc_inputs.setPlaceholderText("Enter inputs (one per line)")
        self.sipoc_inputs.setMaximumHeight(80)
        self.sipoc_inputs.setAccessibleName("Inputs list")
        self.sipoc_inputs.setToolTip("List the inputs required by the process")
        sipoc_form.addRow("Inputs:", self.sipoc_inputs)
        
        self.sipoc_process = QTextEdit()
        self.sipoc_process.setPlaceholderText("Enter 3-5 high-level process steps (one per line)")
        self.sipoc_process.setMaximumHeight(80)
        self.sipoc_process.setAccessibleName("Process steps")
        self.sipoc_process.setToolTip("List 3-5 high-level process steps")
        sipoc_form.addRow("Process:", self.sipoc_process)
        
        self.sipoc_outputs = QTextEdit()
        self.sipoc_outputs.setPlaceholderText("Enter outputs (one per line)")
        self.sipoc_outputs.setMaximumHeight(80)
        self.sipoc_outputs.setAccessibleName("Outputs list")
        self.sipoc_outputs.setToolTip("List the outputs produced by the process")
        sipoc_form.addRow("Outputs:", self.sipoc_outputs)
        
        self.sipoc_requirements = QTextEdit()
        self.sipoc_requirements.setPlaceholderText("Enter output requirements - CTQ/CTS (one per line)\nExample: Accuracy > 99%, Response time < 24 hours")
        self.sipoc_requirements.setMaximumHeight(80)
        self.sipoc_requirements.setAccessibleName("Output requirements CTQ CTS")
        self.sipoc_requirements.setToolTip("Critical to Quality (CTQ) and Critical to Satisfaction (CTS) requirements for outputs")
        sipoc_form.addRow("Requirements (CTQ/CTS):", self.sipoc_requirements)
        
        self.sipoc_customers = QTextEdit()
        self.sipoc_customers.setPlaceholderText("Enter customers (one per line)")
        self.sipoc_customers.setMaximumHeight(80)
        self.sipoc_customers.setAccessibleName("Customers list")
        self.sipoc_customers.setToolTip("List the customers who receive the outputs")
        sipoc_form.addRow("Customers:", self.sipoc_customers)
        
        sipoc_layout.addLayout(sipoc_form)
        
        sipoc_btn = QPushButton("Generate SIPOC Diagram")
        sipoc_btn.clicked.connect(self._generate_sipoc)
        sipoc_btn.setAccessibleName("Generate SIPOC Diagram button")
        sipoc_btn.setToolTip("Create the SIPOC diagram from entered data")
        sipoc_layout.addWidget(sipoc_btn)
        
        self.sipoc_display = QLabel("Enter data above and click Generate")
        self.sipoc_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sipoc_display.setMinimumHeight(400)
        self.sipoc_display.setStyleSheet(get_chart_display_style())
        self.sipoc_display.setAccessibleName("SIPOC diagram display area")
        sipoc_layout.addWidget(self.sipoc_display)
        
        self.tab_widget.addTab(sipoc_tab, "SIPOC Diagram")
        
        # Process Map tab (Define Phase)
        process_map_tab = QWidget()
        process_map_tab.setAccessibleName("Process Map tab - Define Phase")
        process_map_layout = QVBoxLayout(process_map_tab)
        
        process_map_header = QLabel("<b>Process Map</b> - Use [S] for Start/End, [D] for Decision")
        process_map_header.setAccessibleName("Process Map description")
        process_map_layout.addWidget(process_map_header)
        
        # Help text for branching
        branching_help = QLabel(
            "Decision branching: [D] steps show Yes (continues down) and No (returns/loops left)"
        )
        branching_help.setStyleSheet("color: #666; font-size: 9pt;")
        process_map_layout.addWidget(branching_help)
        
        process_map_form = QFormLayout()
        
        self.process_map_title = QLineEdit()
        self.process_map_title.setPlaceholderText("Enter diagram title")
        self.process_map_title.setText("Process Map")
        self.process_map_title.setAccessibleName("Process map title")
        process_map_form.addRow("Title:", self.process_map_title)
        
        process_map_layout.addLayout(process_map_form)
        
        steps_label = QLabel("Process Steps (one per line):")
        steps_label.setAccessibleName("Process steps label")
        process_map_layout.addWidget(steps_label)
        
        self.process_map_steps = QTextEdit()
        self.process_map_steps.setPlaceholderText(
            "[S] Start\n"
            "Receive Document\n"
            "[D] Complete?\n"
            "Process Document\n"
            "[S] End"
        )
        self.process_map_steps.setMaximumHeight(200)
        self.process_map_steps.setAccessibleName("Process steps input")
        self.process_map_steps.setToolTip(
            "Enter process steps, one per line.\n"
            "[S] prefix = Start/End (oval shape)\n"
            "[D] prefix = Decision (diamond shape)\n"
            "No prefix = Process step (rectangle)\n\n"
            "Decision branching:\n"
            "- Yes path continues downward to next step\n"
            "- No path indicates return/rework (shown left)"
        )
        process_map_layout.addWidget(self.process_map_steps)
        
        process_map_btn = QPushButton("Generate Process Map")
        process_map_btn.clicked.connect(self._generate_process_map)
        process_map_btn.setAccessibleName("Generate Process Map button")
        process_map_layout.addWidget(process_map_btn)
        
        self.process_map_display = QLabel("Enter steps above and click Generate")
        self.process_map_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.process_map_display.setMinimumHeight(400)
        self.process_map_display.setStyleSheet(get_chart_display_style())
        self.process_map_display.setAccessibleName("Process map display area")
        process_map_layout.addWidget(self.process_map_display)
        
        self.tab_widget.addTab(process_map_tab, "Process Map")
        
        # RACI Matrix tab (Define/Improve Phase)
        raci_tab = QWidget()
        raci_tab.setAccessibleName("RACI Matrix tab - Define and Improve Phases")
        raci_layout = QVBoxLayout(raci_tab)
        
        raci_header = QLabel("<b>RACI Matrix</b> - R=Responsible, A=Accountable, C=Consulted, I=Informed")
        raci_header.setAccessibleName("RACI matrix description")
        raci_layout.addWidget(raci_header)
        
        raci_form = QFormLayout()
        
        self.raci_title = QLineEdit()
        self.raci_title.setPlaceholderText("Enter matrix title")
        self.raci_title.setText("RACI Matrix")
        self.raci_title.setAccessibleName("RACI matrix title")
        raci_form.addRow("Title:", self.raci_title)
        
        self.raci_roles = QLineEdit()
        self.raci_roles.setPlaceholderText("Enter roles separated by commas (e.g., Lead, Staff, Supervisor)")
        self.raci_roles.setAccessibleName("Roles input")
        self.raci_roles.setToolTip("Enter role names separated by commas")
        raci_form.addRow("Roles:", self.raci_roles)
        
        raci_layout.addLayout(raci_form)
        
        tasks_label = QLabel("Tasks with RACI assignments (format: Task | R,A,C,I for each role):")
        tasks_label.setAccessibleName("Tasks instructions")
        raci_layout.addWidget(tasks_label)
        
        self.raci_tasks = QTextEdit()
        self.raci_tasks.setPlaceholderText(
            "Define Problem | R,A,C\n"
            "Collect Data | C,R,A\n"
            "Analyze Results | R,R,I\n"
            "Implement Solution | A,R,C"
        )
        self.raci_tasks.setMaximumHeight(150)
        self.raci_tasks.setAccessibleName("Tasks input")
        self.raci_tasks.setToolTip("Format: Task Name | assignments (R, A, C, I, or blank for each role)")
        raci_layout.addWidget(self.raci_tasks)
        
        raci_btn = QPushButton("Generate RACI Matrix")
        raci_btn.clicked.connect(self._generate_raci)
        raci_btn.setAccessibleName("Generate RACI Matrix button")
        raci_layout.addWidget(raci_btn)
        
        self.raci_display = QLabel("Enter data above and click Generate")
        self.raci_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.raci_display.setMinimumHeight(400)
        self.raci_display.setStyleSheet(get_chart_display_style())
        self.raci_display.setAccessibleName("RACI matrix display area")
        raci_layout.addWidget(self.raci_display)
        
        self.tab_widget.addTab(raci_tab, "RACI Matrix")
        
        # Swim Lane Diagram tab (Define/Analyze Phase)
        swimlane_tab = QWidget()
        swimlane_tab.setAccessibleName("Swim Lane Diagram tab - Define and Analyze Phases")
        swimlane_layout = QVBoxLayout(swimlane_tab)
        
        swimlane_header = QLabel("<b>Swim Lane Diagram</b> - Shows process flow across roles/departments")
        swimlane_header.setAccessibleName("Swim Lane diagram description")
        swimlane_layout.addWidget(swimlane_header)
        
        swimlane_form = QFormLayout()
        
        self.swimlane_title = QLineEdit()
        self.swimlane_title.setPlaceholderText("Enter diagram title")
        self.swimlane_title.setText("Swim Lane Diagram")
        self.swimlane_title.setAccessibleName("Swim lane diagram title")
        swimlane_form.addRow("Title:", self.swimlane_title)
        
        swimlane_layout.addLayout(swimlane_form)
        
        swimlane_steps_label = QLabel("Steps (format: Lane Name | Step Description):")
        swimlane_steps_label.setAccessibleName("Swim lane steps instructions")
        swimlane_layout.addWidget(swimlane_steps_label)
        
        self.swimlane_steps = QTextEdit()
        self.swimlane_steps.setPlaceholderText(
            "Customer | [S] Submit Request\n"
            "Front Desk | Receive Request\n"
            "Front Desk | [D] Complete?\n"
            "Processing | Process Request\n"
            "Supervisor | Review & Approve\n"
            "Front Desk | Notify Customer\n"
            "Customer | [S] Receive Result"
        )
        self.swimlane_steps.setMaximumHeight(200)
        self.swimlane_steps.setAccessibleName("Swim lane steps input")
        self.swimlane_steps.setToolTip("Format: Lane | Step. Use [S] for Start/End, [D] for Decision")
        swimlane_layout.addWidget(self.swimlane_steps)
        
        swimlane_btn = QPushButton("Generate Swim Lane Diagram")
        swimlane_btn.clicked.connect(self._generate_swimlane)
        swimlane_btn.setAccessibleName("Generate Swim Lane Diagram button")
        swimlane_layout.addWidget(swimlane_btn)
        
        self.swimlane_display = QLabel("Enter data above and click Generate")
        self.swimlane_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.swimlane_display.setMinimumHeight(400)
        self.swimlane_display.setStyleSheet(get_chart_display_style())
        self.swimlane_display.setAccessibleName("Swim lane diagram display area")
        swimlane_layout.addWidget(self.swimlane_display)
        
        self.tab_widget.addTab(swimlane_tab, "Swim Lane")
        
        # Value Stream Map tab (Analyze Phase)
        vsm_tab = QWidget()
        vsm_tab.setAccessibleName("Value Stream Map tab - Analyze Phase")
        vsm_layout = QVBoxLayout(vsm_tab)
        
        vsm_header = QLabel("<b>Value Stream Map</b> - Process flow with cycle time and wait time")
        vsm_header.setAccessibleName("Value Stream Map description")
        vsm_layout.addWidget(vsm_header)
        
        vsm_form = QFormLayout()
        
        self.vsm_title = QLineEdit()
        self.vsm_title.setPlaceholderText("Enter diagram title")
        self.vsm_title.setText("Value Stream Map")
        self.vsm_title.setAccessibleName("Value Stream Map title")
        vsm_form.addRow("Title:", self.vsm_title)
        
        vsm_layout.addLayout(vsm_form)
        
        vsm_steps_label = QLabel("Steps (format: Step Name, Cycle Time (min), Wait Time (min)):")
        vsm_steps_label.setAccessibleName("VSM steps instructions")
        vsm_layout.addWidget(vsm_steps_label)
        
        self.vsm_steps = QTextEdit()
        self.vsm_steps.setPlaceholderText(
            "Receive, 5, 60\n"
            "Review, 15, 120\n"
            "Process, 30, 240\n"
            "Approve, 10, 60\n"
            "Complete, 5, 0"
        )
        self.vsm_steps.setMaximumHeight(150)
        self.vsm_steps.setAccessibleName("VSM steps input")
        self.vsm_steps.setToolTip("Format: Step Name, Cycle Time, Wait Time (all times in minutes)")
        vsm_layout.addWidget(self.vsm_steps)
        
        vsm_btn = QPushButton("Generate Value Stream Map")
        vsm_btn.clicked.connect(self._generate_vsm)
        vsm_btn.setAccessibleName("Generate Value Stream Map button")
        vsm_layout.addWidget(vsm_btn)
        
        self.vsm_display = QLabel("Enter data above and click Generate")
        self.vsm_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vsm_display.setMinimumHeight(350)
        self.vsm_display.setStyleSheet(get_chart_display_style())
        self.vsm_display.setAccessibleName("Value Stream Map display area")
        vsm_layout.addWidget(self.vsm_display)
        
        self.vsm_metrics = QTextEdit()
        self.vsm_metrics.setReadOnly(True)
        self.vsm_metrics.setMaximumHeight(80)
        self.vsm_metrics.setAccessibleName("VSM metrics output")
        vsm_layout.addWidget(self.vsm_metrics)
        
        self.tab_widget.addTab(vsm_tab, "Value Stream Map")
        
        # Fishbone Diagram tab (Analyze Phase)
        fishbone_tab = QWidget()
        fishbone_tab.setAccessibleName("Fishbone Diagram tab - Analyze Phase")
        fishbone_layout = QVBoxLayout(fishbone_tab)
        
        fishbone_header = QLabel("<b>Fishbone Diagram</b> - Cause and Effect Analysis")
        fishbone_header.setAccessibleName("Fishbone diagram description")
        fishbone_layout.addWidget(fishbone_header)
        
        fishbone_form = QFormLayout()
        
        self.fishbone_title = QLineEdit()
        self.fishbone_title.setPlaceholderText("Enter diagram title")
        self.fishbone_title.setText("Fishbone Diagram")
        self.fishbone_title.setAccessibleName("Fishbone diagram title")
        fishbone_form.addRow("Title:", self.fishbone_title)
        
        self.fishbone_effect = QLineEdit()
        self.fishbone_effect.setPlaceholderText("Enter the problem/effect to analyze")
        self.fishbone_effect.setAccessibleName("Effect/problem input")
        self.fishbone_effect.setToolTip("The problem or effect shown in the fish head")
        fishbone_form.addRow("Effect/Problem:", self.fishbone_effect)
        
        fishbone_layout.addLayout(fishbone_form)
        
        categories_label = QLabel("Categories and Causes (one cause per line in each box):")
        categories_label.setAccessibleName("Categories instructions")
        fishbone_layout.addWidget(categories_label)
        
        # Create grid for 6 categories
        fishbone_grid = QGridLayout()
        
        self.fishbone_causes = {}
        categories = [
            ('Policy/Standards', 0, 0),
            ('Materials', 0, 1),
            ('Process/Procedures', 0, 2),
            ('Physical Environment', 1, 0),
            ('People', 1, 1),
            ('IT Systems/Equipment', 1, 2)
        ]
        
        for cat_name, row, col in categories:
            group = QGroupBox(cat_name)
            group.setAccessibleName(f"{cat_name} causes")
            group_layout = QVBoxLayout(group)
            
            text_edit = QTextEdit()
            text_edit.setPlaceholderText(f"Enter {cat_name} causes\n(one per line)")
            text_edit.setMaximumHeight(80)
            text_edit.setAccessibleName(f"{cat_name} causes input")
            group_layout.addWidget(text_edit)
            
            self.fishbone_causes[cat_name] = text_edit
            fishbone_grid.addWidget(group, row, col)
        
        fishbone_layout.addLayout(fishbone_grid)
        
        fishbone_btn = QPushButton("Generate Fishbone Diagram")
        fishbone_btn.clicked.connect(self._generate_fishbone)
        fishbone_btn.setAccessibleName("Generate Fishbone Diagram button")
        fishbone_layout.addWidget(fishbone_btn)
        
        self.fishbone_display = QLabel("Enter data above and click Generate")
        self.fishbone_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fishbone_display.setMinimumHeight(350)
        self.fishbone_display.setStyleSheet(get_chart_display_style())
        self.fishbone_display.setAccessibleName("Fishbone diagram display area")
        fishbone_layout.addWidget(self.fishbone_display)
        
        self.tab_widget.addTab(fishbone_tab, "Fishbone Diagram")
    
    def _create_status_bar(self):
        """Create the status bar with accessibility support."""
        self.status_bar = QStatusBar()
        self.status_bar.setAccessibleName("Status bar")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Load a data file to begin analysis")
    
    def _setup_keyboard_shortcuts(self):
        """Setup additional keyboard shortcuts."""
        # Tab navigation shortcuts
        for i in range(9):
            shortcut = QShortcut(QKeySequence(f"Alt+{i+1}"), self)
            shortcut.activated.connect(lambda idx=i: self._switch_to_tab(idx))
    
    def _switch_to_tab(self, index):
        """Switch to specified tab if it exists."""
        if index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(index)
    
    def _apply_styles(self):
        """Apply CiviQual brand styling with Section 508 accessibility compliance and dark mode support."""
        # CiviQual Brand Colors:
        # Burgundy (Primary): #6d132a
        # Gold (Accent): #dcad73
        # Gray (Secondary): #b2b2b2
        # Black: #000000
        
        if DARK_MODE:
            # Dark mode colors
            bg_main = "#1e1e1e"
            bg_widget = "#2d2d2d"
            bg_alt = "#3d3d3d"
            text_color = "#dcdcdc"
            text_secondary = "#a0a0a0"
            border_color = "#555555"
            tab_inactive = "#3d3d3d"
            tab_hover = "#4d4d4d"
        else:
            # Light mode colors
            bg_main = "#f5f5f5"
            bg_widget = "white"
            bg_alt = "#e8e8e8"
            text_color = "#333333"
            text_secondary = "#666666"
            border_color = "#b2b2b2"
            tab_inactive = "#e8e8e8"
            tab_hover = "#e0e0e0"
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {bg_main};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {border_color};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: {text_color};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #6d132a;
            }}
            
            /* Buttons with enhanced focus indicators */
            QPushButton {{
                background-color: #6d132a;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 30px;
            }}
            QPushButton:hover {{
                background-color: #4a0919;
            }}
            QPushButton:pressed {{
                background-color: #004166;
            }}
            QPushButton:focus {{
                outline: none;
            }}
            /* Improved disabled button contrast - Section 508 requirement */
            QPushButton:disabled {{
                background-color: #888888;
                color: #e0e0e0;
            }}
            
            /* Tables */
            QTableWidget {{
                gridline-color: {border_color};
                background-color: {bg_widget};
                color: {text_color};
            }}
            QTableWidget::item {{
                padding: 5px;
            }}
            QTableWidget::item:selected {{
                background-color: #6d132a;
                color: white;
            }}
            QHeaderView::section {{
                background-color: {bg_alt};
                color: {text_color};
                padding: 5px;
                border: 1px solid {border_color};
            }}
            
            /* Tabs */
            QTabWidget::pane {{
                border: 1px solid {border_color};
                background-color: {bg_widget};
            }}
            QTabBar::tab {{
                background-color: {tab_inactive};
                padding: 8px 16px;
                margin-right: 2px;
                color: {text_color};
            }}
            QTabBar::tab:selected {{
                background-color: {bg_widget};
                border-bottom: 3px solid #6d132a;
                color: #6d132a;
                font-weight: bold;
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {tab_hover};
                color: {text_color};
            }}
            QTabBar::tab:focus {{
                outline: none;
            }}
            
            /* Input fields */
            QComboBox {{
                border: 1px solid {border_color};
                border-radius: 3px;
                padding: 4px 8px;
                min-height: 24px;
                background-color: {bg_widget};
                color: {text_color};
            }}
            QComboBox:focus {{
                border: 1px solid #6d132a;
            }}
            QComboBox QAbstractItemView {{
                background-color: {bg_widget};
                color: {text_color};
                selection-background-color: #6d132a;
                selection-color: white;
            }}
            
            QLineEdit, QSpinBox, QDoubleSpinBox {{
                border: 1px solid {border_color};
                border-radius: 3px;
                padding: 4px 8px;
                min-height: 24px;
                background-color: {bg_widget};
                color: {text_color};
            }}
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
                border: 1px solid #6d132a;
            }}
            
            QTextEdit {{
                border: 1px solid {border_color};
                border-radius: 3px;
                background-color: {bg_widget};
                color: {text_color};
            }}
            QTextEdit:focus {{
                border: 1px solid #6d132a;
            }}
            
            /* Labels */
            QLabel {{
                color: {text_color};
            }}
            
            /* Checkboxes */
            QCheckBox {{
                spacing: 8px;
                color: {text_color};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
            QCheckBox::indicator:checked {{
                background-color: #6d132a;
                border: 1px solid #6d132a;
            }}
            QCheckBox::indicator:unchecked {{
                background-color: {bg_widget};
                border: 1px solid {border_color};
            }}
            
            /* Scrollbars */
            QScrollBar:vertical {{
                background-color: {bg_alt};
                width: 14px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {border_color};
                border-radius: 7px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: #6d132a;
            }}
            QScrollBar:horizontal {{
                background-color: {bg_alt};
                height: 14px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {border_color};
                border-radius: 7px;
                min-width: 30px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: #6d132a;
            }}
            
            /* Menu bar */
            QMenuBar {{
                background-color: #6d132a;
                color: white;
            }}
            QMenuBar::item {{
                padding: 6px 12px;
            }}
            QMenuBar::item:selected {{
                background-color: #4a0919;
                color: white;
            }}
            
            /* Menus */
            QMenu {{
                background-color: {bg_widget};
                border: 1px solid {border_color};
                color: {text_color};
            }}
            QMenu::item {{
                padding: 6px 30px 6px 20px;
            }}
            QMenu::item:selected {{
                background-color: #6d132a;
                color: white;
            }}
            
            /* Status bar */
            QStatusBar {{
                background-color: #6d132a;
                color: white;
            }}
            
            /* Text browser (for dialogs) */
            QTextBrowser {{
                border: 1px solid {border_color};
                background-color: {bg_widget};
                color: {text_color};
            }}
            
            /* Splitters */
            QSplitter::handle {{
                background-color: {border_color};
            }}
            QSplitter::handle:hover {{
                background-color: #6d132a;
            }}
            
            /* List widgets */
            QListWidget {{
                background-color: {bg_widget};
                color: {text_color};
                border: 1px solid {border_color};
            }}
            QListWidget::item:selected {{
                background-color: #6d132a;
                color: white;
            }}
        """)
    
    # =========================================================================
    # File Operations
    # =========================================================================
    def _open_file(self):
        """Open a data file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Data File",
            self.config.get('last_directory', str(Path.home())),
            "Data Files (*.csv *.xlsx *.xls);;CSV Files (*.csv);;Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        
        if file_path:
            self._load_file(file_path)
    
    def _load_file(self, file_path):
        """Load data from file."""
        try:
            self.data = self.data_handler.load_file(file_path)
            
            # Update config
            self.config['last_directory'] = str(Path(file_path).parent)
            save_config(self.config)
            
            # Update UI
            self.file_label.setText(Path(file_path).name)
            self._populate_columns()
            self._populate_data_table()
            
            self.status_bar.showMessage(f"Loaded {len(self.data)} rows from {Path(file_path).name}")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Loading File",
                f"Could not load file:\n{str(e)}"
            )
    
    def _populate_columns(self):
        """Populate column combo boxes."""
        if self.data is None:
            return
        
        # Get numeric columns
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()
        all_cols = self.data.columns.tolist()
        
        # Update analysis column combo
        self.column_combo.clear()
        self.column_combo.addItems(numeric_cols)
        
        # Update subgroup combo
        self.subgroup_combo.clear()
        self.subgroup_combo.addItem("(None)")
        self.subgroup_combo.addItems(all_cols)
        
        # Update Pareto column combo
        self.pareto_column.clear()
        self.pareto_column.addItems(all_cols)
        
        # Update correlation X and Y combo boxes
        self.corr_x_combo.clear()
        self.corr_x_combo.addItems(numeric_cols)
        
        self.corr_y_combo.clear()
        self.corr_y_combo.addItems(numeric_cols)
        
        # Set Y to second column if available (different from X)
        if len(numeric_cols) > 1:
            self.corr_y_combo.setCurrentIndex(1)
        
        # Update probability plot column list
        self.prob_plot_columns.clear()
        self.prob_plot_columns.addItems(numeric_cols)
        
        # Update data sampling column combo
        self.sampling_column.clear()
        self.sampling_column.addItems(all_cols)
        
        # Update split worksheet column combos
        self.split_by_column.clear()
        self.split_by_column.addItems(all_cols)
        
        self.split_data_column.clear()
        self.split_data_column.addItem("(All Columns)")
        self.split_data_column.addItems(numeric_cols)
    
    def _populate_data_table(self):
        """Populate the data table widget."""
        if self.data is None:
            return
        
        self.data_table.setRowCount(len(self.data))
        self.data_table.setColumnCount(len(self.data.columns))
        self.data_table.setHorizontalHeaderLabels(self.data.columns.tolist())
        
        for row in range(len(self.data)):
            for col in range(len(self.data.columns)):
                value = self.data.iloc[row, col]
                item = QTableWidgetItem(str(value) if pd.notna(value) else "")
                self.data_table.setItem(row, col, item)
    
    def _on_column_changed(self, column_name):
        """Handle column selection change."""
        if column_name:
            self.status_bar.showMessage(f"Selected column: {column_name}")
    
    # =========================================================================
    # Analysis Methods (Stubs - Implementation in separate modules)
    # =========================================================================
    def _generate_four_up(self):
        """Generate CiviQual 4-Up Chart."""
        if self.data is None:
            QMessageBox.warning(self, "No Data", "Please load a data file first.")
            return
        
        column = self.column_combo.currentText()
        if not column:
            QMessageBox.warning(self, "No Column", "Please select an analysis column.")
            return
        
        try:
            data = self.data[column].dropna()
            percentile = self.percentile_spin.value()
            
            # Get spec limits if set (for capability quadrant)
            lsl = None if self.lsl_input.value() == self.lsl_input.minimum() else self.lsl_input.value()
            usl = None if self.usl_input.value() == self.usl_input.minimum() else self.usl_input.value()
            target = None if self.target_input.value() == self.target_input.minimum() else self.target_input.value()
            
            # Generate chart using visualization engine
            chart_path = self.viz_engine.generate_four_up(
                data, column, lsl=lsl, usl=usl, target=target, percentile=percentile
            )
            
            if chart_path and Path(chart_path).exists():
                pixmap = QPixmap(chart_path)
                scaled = pixmap.scaled(
                    self.four_up_display.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.four_up_display.setPixmap(scaled)
                
                # Update accessible description with results
                stats = self.stats_engine.descriptive_stats(data)
                self.four_up_display.setAccessibleDescription(
                    f"CiviQual 4-Up Chart for {column}. "
                    f"Mean: {stats['mean']:.2f}, "
                    f"Standard Deviation: {stats['std']:.2f}, "
                    f"Sample Size: {stats['n']}"
                )
            
            self.status_bar.showMessage(f"Generated 4-Up Chart for {column}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not generate chart:\n{str(e)}")
    
    def _run_descriptive(self):
        """Run descriptive statistics."""
        if self.data is None:
            QMessageBox.warning(self, "No Data", "Please load a data file first.")
            return
        
        column = self.column_combo.currentText()
        if not column:
            QMessageBox.warning(self, "No Column", "Please select an analysis column.")
            return
        
        try:
            data = self.data[column].dropna()
            stats = self.stats_engine.descriptive_stats(data)
            
            output = f"Descriptive Statistics for: {column}\n"
            output += "=" * 50 + "\n\n"
            output += f"Sample Size (n):     {stats['n']}\n"
            output += f"Mean:                {stats['mean']:.4f}\n"
            output += f"Median:              {stats['median']:.4f}\n"
            output += f"Mode:                {stats['mode']:.4f}\n"
            output += f"Standard Deviation:  {stats['std']:.4f}\n"
            output += f"Variance:            {stats['variance']:.4f}\n"
            output += f"Minimum:             {stats['min']:.4f}\n"
            output += f"Maximum:             {stats['max']:.4f}\n"
            output += f"Range:               {stats['range']:.4f}\n"
            output += f"Q1 (25th percentile):{stats['q1']:.4f}\n"
            output += f"Q3 (75th percentile):{stats['q3']:.4f}\n"
            output += f"IQR:                 {stats['iqr']:.4f}\n"
            output += f"Skewness:            {stats['skewness']:.4f}\n"
            output += f"Kurtosis:            {stats['kurtosis']:.4f}\n"
            
            self.desc_output.setPlainText(output)
            self.tab_widget.setCurrentIndex(1)  # Switch to descriptive tab
            self.status_bar.showMessage(f"Calculated statistics for {column}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not calculate statistics:\n{str(e)}")
    
    def _generate_ichart(self):
        """Generate I-Chart with analytical interpretation."""
        if self.data is None:
            QMessageBox.warning(self, "No Data", "Please load a data file first.")
            return
        
        column = self.column_combo.currentText()
        if not column:
            return
        
        try:
            data = self.data[column].dropna().values
            rules = {
                'rule1': self.rule1_check.isChecked(),
                'rule2': self.rule2_check.isChecked(),
                'rule3': self.rule3_check.isChecked(),
                'rule4': self.rule4_check.isChecked()
            }
            
            chart_path = self.viz_engine.generate_ichart(data, column, rules)
            
            if chart_path and Path(chart_path).exists():
                pixmap = QPixmap(chart_path)
                scaled = pixmap.scaled(
                    self.control_display.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.control_display.setPixmap(scaled)
            
            # Generate analytical interpretation
            analysis = self._generate_control_chart_analysis(data, column, 'I-Chart', rules)
            self.control_analysis.setPlainText(analysis)
            
            self.tab_widget.setCurrentIndex(2)
            self.status_bar.showMessage(f"Generated I-Chart for {column}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not generate I-Chart:\n{str(e)}")
    
    def _generate_imr(self):
        """Generate I-MR Chart (Individuals and Moving Range) with analytical interpretation."""
        if self.data is None:
            QMessageBox.warning(self, "No Data", "Please load a data file first.")
            return
        
        column = self.column_combo.currentText()
        if not column:
            return
        
        try:
            data = self.data[column].dropna().values
            rules = {
                'rule1': self.rule1_check.isChecked(),
                'rule2': self.rule2_check.isChecked(),
                'rule3': self.rule3_check.isChecked(),
                'rule4': self.rule4_check.isChecked()
            }
            
            chart_path = self.viz_engine.generate_imr_chart(data, column, rules)
            
            if chart_path and Path(chart_path).exists():
                pixmap = QPixmap(chart_path)
                scaled = pixmap.scaled(
                    self.control_display.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.control_display.setPixmap(scaled)
            
            # Generate analytical interpretation
            analysis = self._generate_control_chart_analysis(data, column, 'I-MR Chart', rules)
            self.control_analysis.setPlainText(analysis)
            
            self.tab_widget.setCurrentIndex(2)
            self.status_bar.showMessage(f"Generated I-MR Chart for {column}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not generate I-MR Chart:\n{str(e)}")
    
    def _generate_mr(self):
        """Generate standalone Moving Range Chart with analytical interpretation."""
        if self.data is None:
            QMessageBox.warning(self, "No Data", "Please load a data file first.")
            return
        
        column = self.column_combo.currentText()
        if not column:
            return
        
        try:
            data = self.data[column].dropna().values
            
            chart_path = self.viz_engine.generate_mr_chart(data, column)
            
            if chart_path and Path(chart_path).exists():
                pixmap = QPixmap(chart_path)
                scaled = pixmap.scaled(
                    self.control_display.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.control_display.setPixmap(scaled)
            
            # Generate analytical interpretation
            analysis = self._generate_control_chart_analysis(data, column, 'MR Chart', {})
            self.control_analysis.setPlainText(analysis)
            
            self.tab_widget.setCurrentIndex(2)
            self.status_bar.showMessage(f"Generated MR Chart for {column}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not generate MR Chart:\n{str(e)}")
    
    def _generate_control_chart_analysis(self, data, column_name, chart_type, rules):
        """Generate analytical interpretation for control charts."""
        import numpy as np
        
        n = len(data)
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        
        # Calculate moving range for I-Chart limits
        mr = np.abs(np.diff(data))
        mr_bar = np.mean(mr) if len(mr) > 0 else 0
        
        # Control limits (d2 = 1.128 for n=2)
        d2 = 1.128
        sigma_est = mr_bar / d2 if mr_bar > 0 else std
        ucl = mean + 3 * sigma_est
        lcl = mean - 3 * sigma_est
        
        # MR Chart limits
        d4 = 3.267
        mr_ucl = d4 * mr_bar
        
        # Get detailed flagged points using statistics engine
        flagged = self.stats_engine.detect_special_causes(data, rules)
        
        # Count out-of-control points
        ooc_high = np.sum(data > ucl)
        ooc_low = np.sum(data < lcl)
        ooc_total = ooc_high + ooc_low
        
        # MR out-of-control
        mr_ooc = np.sum(mr > mr_ucl) if len(mr) > 0 else 0
        
        # Detect runs and trends
        above_mean = data > mean
        runs = 1
        for i in range(1, len(above_mean)):
            if above_mean[i] != above_mean[i-1]:
                runs += 1
        
        # Expected runs for random data
        expected_runs = (2 * np.sum(above_mean) * np.sum(~above_mean)) / n + 1
        
        # Build analysis text
        lines = []
        lines.append(f"CONTROL CHART ANALYSIS: {column_name}")
        lines.append(f"Chart Type: {chart_type}")
        lines.append("=" * 45)
        lines.append("")
        
        # Summary statistics
        lines.append("SUMMARY STATISTICS")
        lines.append("-" * 30)
        lines.append(f"Sample Size (n):        {n}")
        lines.append(f"Mean (X-bar):           {mean:.4f}")
        lines.append(f"Std Dev (s):            {std:.4f}")
        lines.append(f"Avg Moving Range:       {mr_bar:.4f}")
        lines.append(f"Sigma Estimate:         {sigma_est:.4f}")
        lines.append("")
        
        # Control limits
        lines.append("CONTROL LIMITS")
        lines.append("-" * 30)
        lines.append(f"Upper Control Limit:    {ucl:.4f}")
        lines.append(f"Center Line (Mean):     {mean:.4f}")
        lines.append(f"Lower Control Limit:    {lcl:.4f}")
        if chart_type in ['MR Chart', 'I-MR Chart']:
            lines.append(f"MR Upper Limit:         {mr_ucl:.4f}")
            lines.append(f"MR Center Line:         {mr_bar:.4f}")
        lines.append("")
        
        # Stability assessment
        lines.append("STABILITY ASSESSMENT")
        lines.append("-" * 30)
        
        stability_issues = []
        total_flagged = len(flagged.get('all', []))
        
        if total_flagged > 0:
            lines.append(f"Flagged Points:         {total_flagged}")
            
            # Count by test
            test_counts = {}
            for rule_num in [1, 2, 3, 4]:
                rule_key = f'rule{rule_num}'
                if rule_key in flagged and len(flagged[rule_key]) > 0:
                    test_counts[rule_num] = len(flagged[rule_key])
            
            for test_num, count in sorted(test_counts.items()):
                lines.append(f"  - Test {test_num}:            {count} point(s)")
            
            stability_issues.append(f"{total_flagged} point(s) flagged by Western Electric rules")
        else:
            lines.append("Flagged Points:         0")
        
        if chart_type in ['MR Chart', 'I-MR Chart'] and mr_ooc > 0:
            lines.append(f"MR Out-of-Control:      {mr_ooc}")
            stability_issues.append(f"{mr_ooc} MR point(s) above limit")
        
        lines.append(f"Number of Runs:         {runs}")
        lines.append(f"Expected Runs:          {expected_runs:.1f}")
        lines.append("")
        
        # Detailed flagged points by test
        if total_flagged > 0:
            lines.append("FLAGGED POINTS DETAIL")
            lines.append("-" * 30)
            
            # Build mapping of point to tests
            point_tests = {}
            for rule_num in [1, 2, 3, 4]:
                rule_key = f'rule{rule_num}'
                if rule_key in flagged:
                    for idx in flagged[rule_key]:
                        if idx not in point_tests:
                            point_tests[idx] = []
                        point_tests[idx].append(rule_num)
            
            # Sort by observation number
            for idx in sorted(point_tests.keys()):
                obs_num = idx + 1  # 1-based observation number
                value = data[idx]
                tests = point_tests[idx]
                test_str = ', '.join(f'T{t}' for t in sorted(tests))
                lines.append(f"  Obs {obs_num:3d}: {value:10.4f} → {test_str}")
            
            lines.append("")
        
        # Interpretation
        lines.append("INTERPRETATION")
        lines.append("-" * 30)
        
        if len(stability_issues) == 0:
            lines.append("PROCESS STATUS: IN CONTROL")
            lines.append("")
            lines.append("The process appears stable with only common")
            lines.append("cause variation present. All points fall within")
            lines.append("the control limits and no unusual patterns")
            lines.append("are detected.")
            lines.append("")
            lines.append("RECOMMENDED ACTIONS:")
            lines.append("- Process is predictable; proceed with")
            lines.append("  capability analysis if needed")
            lines.append("- Continue monitoring to maintain stability")
            lines.append("- Document current process settings")
        else:
            lines.append("PROCESS STATUS: OUT OF CONTROL")
            lines.append("")
            lines.append("Special cause variation detected:")
            for issue in stability_issues:
                lines.append(f"  - {issue}")
            lines.append("")
            lines.append("RECOMMENDED ACTIONS:")
            lines.append("- Investigate assignable causes for")
            lines.append("  out-of-control points")
            lines.append("- Do NOT calculate capability indices")
            lines.append("  until process is stable")
            lines.append("- Use root cause analysis tools")
            lines.append("  (Fishbone, 5 Whys) to identify causes")
            lines.append("- Implement corrective actions and")
            lines.append("  verify stability before proceeding")
        
        lines.append("")
        lines.append("=" * 45)
        
        # Add rules explanation if rules were applied
        if rules and any(rules.values()):
            lines.append("")
            lines.append("WESTERN ELECTRIC RULES APPLIED")
            lines.append("-" * 30)
            if rules.get('rule1'):
                lines.append("Test 1: Point beyond 3 sigma")
            if rules.get('rule2'):
                lines.append("Test 2: 2 of 3 beyond 2 sigma (same side)")
            if rules.get('rule3'):
                lines.append("Test 3: 4 of 5 beyond 1 sigma (same side)")
            if rules.get('rule4'):
                lines.append("Test 4: 8 consecutive same side of center")
        
        return "\n".join(lines)
    
    def _run_capability(self):
        """Run capability analysis with chart and enhanced interpretation."""
        if self.data is None:
            QMessageBox.warning(self, "No Data", "Please load a data file first.")
            return
        
        column = self.column_combo.currentText()
        if not column:
            return
        
        try:
            data = self.data[column].dropna().values
            
            lsl = None if self.lsl_input.value() == self.lsl_input.minimum() else self.lsl_input.value()
            usl = None if self.usl_input.value() == self.usl_input.minimum() else self.usl_input.value()
            target = None if self.target_input.value() == self.target_input.minimum() else self.target_input.value()
            show_cp_one = self.cp_one_checkbox.isChecked()
            
            results = self.stats_engine.capability_analysis(data, lsl, usl)
            
            # Calculate Cp=1.0 natural tolerance limits
            mean = results['mean']
            std = results['std_within']
            cp_one_lsl = mean - 3 * std  # Natural lower limit for Cp=1.0
            cp_one_usl = mean + 3 * std  # Natural upper limit for Cp=1.0
            
            # Generate capability chart
            chart_path = self.viz_engine.generate_capability_chart(
                data, column, lsl=lsl, usl=usl, target=target,
                show_cp_one=show_cp_one, cp_one_lsl=cp_one_lsl, cp_one_usl=cp_one_usl
            )
            
            if chart_path and Path(chart_path).exists():
                pixmap = QPixmap(chart_path)
                scaled = pixmap.scaled(
                    self.capability_chart_display.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.capability_chart_display.setPixmap(scaled)
            
            # Build comprehensive output with interpretation
            output = f"CAPABILITY ANALYSIS: {column}\n"
            output += "=" * 60 + "\n\n"
            
            output += "PROCESS STATISTICS\n"
            output += "-" * 40 + "\n"
            output += f"  Sample Size (N):     {results['n']}\n"
            output += f"  Process Mean:        {mean:.4f}\n"
            output += f"  Process StDev:       {std:.4f}\n"
            output += f"  Process Variation:   {6 * std:.4f} (6σ)\n\n"
            
            if lsl is not None or usl is not None:
                output += "SPECIFICATION LIMITS\n"
                output += "-" * 40 + "\n"
                if lsl is not None:
                    output += f"  Lower Spec (LSL):    {lsl:.4f}\n"
                if usl is not None:
                    output += f"  Upper Spec (USL):    {usl:.4f}\n"
                if lsl is not None and usl is not None:
                    output += f"  Spec Tolerance:      {usl - lsl:.4f}\n"
                if target is not None:
                    output += f"  Target:              {target:.4f}\n"
                output += "\n"
            
            if results.get('cp') is not None:
                output += "CAPABILITY INDICES\n"
                output += "-" * 40 + "\n"
                output += f"  Cp:   {results['cp']:.4f}    (Potential capability)\n"
                output += f"  Cpk:  {results['cpk']:.4f}    (Actual capability)\n"
                if results.get('cpu') is not None:
                    output += f"  Cpu:  {results['cpu']:.4f}    (Upper capability)\n"
                if results.get('cpl') is not None:
                    output += f"  Cpl:  {results['cpl']:.4f}    (Lower capability)\n"
                output += "\n"
                
                # Interpretation
                output += "INTERPRETATION\n"
                output += "-" * 40 + "\n"
                
                cp = results['cp']
                cpk = results['cpk']
                
                # Cp interpretation
                if cp >= 2.0:
                    output += "  Cp ≥ 2.0: EXCELLENT potential capability\n"
                    output += "            Process spread is ≤50% of spec tolerance\n"
                elif cp >= 1.33:
                    output += "  Cp ≥ 1.33: GOOD potential capability\n"
                    output += "             Process spread is ≤75% of spec tolerance\n"
                elif cp >= 1.0:
                    output += "  Cp ≥ 1.0: MARGINAL potential capability\n"
                    output += "            Process spread equals spec tolerance\n"
                else:
                    output += "  Cp < 1.0: INADEQUATE potential capability\n"
                    output += "            Process spread exceeds spec tolerance\n"
                
                output += "\n"
                
                # Cpk interpretation
                if cpk >= 1.33:
                    output += "  Cpk ≥ 1.33: CAPABLE - Process meets requirements\n"
                elif cpk >= 1.0:
                    output += "  Cpk ≥ 1.0: MARGINAL - Some defects expected\n"
                else:
                    output += "  Cpk < 1.0: NOT CAPABLE - Significant defects\n"
                
                # Centering analysis
                if abs(cp - cpk) > 0.1:
                    output += "\n  NOTE: Cp ≠ Cpk indicates process is not centered\n"
                    if results.get('cpu', 0) < results.get('cpl', 0):
                        output += "        Process is shifted toward UPPER spec limit\n"
                    else:
                        output += "        Process is shifted toward LOWER spec limit\n"
                
                output += "\n"
            
            # Cp=1.0 Natural Tolerance
            output += "NATURAL TOLERANCE (Cp=1.0)\n"
            output += "-" * 40 + "\n"
            
            # Check if all data is positive and natural LSL would be negative
            all_positive = np.min(data) >= 0
            display_nat_lsl = cp_one_lsl
            if all_positive and cp_one_lsl < 0:
                display_nat_lsl = 0
                output += f"  Natural LSL (Mean - 3σ): 0.0000 (clamped)\n"
                output += f"    (Calculated: {cp_one_lsl:.4f}, but data is all positive)\n"
            else:
                output += f"  Natural LSL (Mean - 3σ): {cp_one_lsl:.4f}\n"
            output += f"  Natural USL (Mean + 3σ): {cp_one_usl:.4f}\n"
            output += f"  Natural Tolerance (6σ):  {6 * std:.4f}\n"
            output += "\n"
            output += "  These limits represent Cp=1.0 based on current\n"
            output += "  process performance. If your specs must be tighter,\n"
            output += "  process variation must be reduced.\n"
            
            if lsl is not None and usl is not None:
                needed_std = (usl - lsl) / 6
                if std > needed_std:
                    reduction_pct = (1 - needed_std / std) * 100
                    output += f"\n  To achieve Cp=1.0 with current specs:\n"
                    output += f"    Required StDev: {needed_std:.4f}\n"
                    output += f"    Reduction needed: {reduction_pct:.1f}%\n"
            
            self.capability_output.setPlainText(output)
            self.status_bar.showMessage(f"Completed capability analysis for {column}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not run capability analysis:\n{str(e)}")
    
    def _generate_probability_plot(self):
        """Generate probability plot with multiple data series."""
        if self.data is None:
            QMessageBox.warning(self, "No Data", "Please load a data file first.")
            return
        
        # Get selected columns
        selected_items = self.prob_plot_columns.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select at least one column.")
            return
        
        selected_columns = [item.text() for item in selected_items]
        
        try:
            # Gather data for each selected column
            datasets = []
            labels = []
            stats_output = "Probability Plot Statistics\n"
            stats_output += "=" * 50 + "\n\n"
            
            for col in selected_columns:
                col_data = self.data[col].dropna().values
                if len(col_data) >= 2:
                    datasets.append(col_data)
                    labels.append(col)
                    
                    # Calculate normality statistics
                    mean = np.mean(col_data)
                    std = np.std(col_data, ddof=1)
                    
                    # Anderson-Darling test
                    ad_stat, ad_crit, ad_sig = self.stats_engine.anderson_darling_test(col_data)
                    
                    stats_output += f"{col}:\n"
                    stats_output += f"  N={len(col_data)}, Mean={mean:.4f}, StDev={std:.4f}\n"
                    stats_output += f"  Anderson-Darling: {ad_stat:.4f}"
                    if ad_stat < ad_crit[2]:  # 5% significance level
                        stats_output += " (Normal)\n"
                    else:
                        stats_output += " (Non-Normal)\n"
                    stats_output += "\n"
            
            if not datasets:
                QMessageBox.warning(self, "Insufficient Data", 
                                   "Selected columns do not have enough data points.")
                return
            
            # Generate multi-series probability plot
            title = "Probability Plot Comparison" if len(datasets) > 1 else f"Probability Plot: {labels[0]}"
            chart_path = self.viz_engine.generate_multi_probability_plot(datasets, labels, title)
            
            if chart_path and Path(chart_path).exists():
                pixmap = QPixmap(chart_path)
                scaled = pixmap.scaled(
                    self.prob_plot_display.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.prob_plot_display.setPixmap(scaled)
            
            self.prob_plot_output.setPlainText(stats_output)
            self.status_bar.showMessage(f"Generated probability plot for {len(datasets)} series")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not generate probability plot:\n{str(e)}")
    
    def _run_anova(self):
        """Run ANOVA analysis with box plot visualization."""
        if self.data is None:
            QMessageBox.warning(self, "No Data", "Please load a data file first.")
            return
        
        column = self.column_combo.currentText()
        subgroup = self.subgroup_combo.currentText()
        
        if not column:
            return
        
        if subgroup == "(None)":
            QMessageBox.warning(self, "No Subgroup", "Please select a subgroup column for ANOVA.")
            return
        
        try:
            # Run ANOVA analysis
            results = self.stats_engine.run_anova(self.data, column, subgroup)
            
            # Generate box plot
            chart_path = self.viz_engine.generate_anova_boxplot(
                self.data, column, subgroup,
                title=f"ANOVA: {column} by {subgroup}"
            )
            
            # Display box plot
            pixmap = QPixmap(str(chart_path))
            scaled = pixmap.scaled(
                self.anova_chart_display.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.anova_chart_display.setPixmap(scaled)
            
            # Build output text
            output = f"ANOVA Analysis\n"
            output += f"Response Variable: {column}\n"
            output += f"Factor: {subgroup}\n"
            output += "=" * 50 + "\n\n"
            
            # ANOVA table
            output += "ANOVA Table:\n"
            output += "-" * 50 + "\n"
            output += f"{'Source':<15} {'DF':<8} {'SS':<12} {'MS':<12} {'F':<10} {'P-value':<10}\n"
            output += "-" * 50 + "\n"
            
            # Between groups
            df_between = results.get('df_between', 'N/A')
            ss_between = results.get('ss_between', 'N/A')
            ms_between = results.get('ms_between', 'N/A')
            f_stat = results['f_stat']
            p_value = results['p_value']
            
            if isinstance(ss_between, (int, float)):
                output += f"{'Factor':<15} {df_between:<8} {ss_between:<12.4f} {ms_between:<12.4f} {f_stat:<10.4f} {p_value:<10.6f}\n"
            else:
                output += f"{'Factor':<15} {'--':<8} {'--':<12} {'--':<12} {f_stat:<10.4f} {p_value:<10.6f}\n"
            
            # Within groups (error)
            df_within = results.get('df_within', 'N/A')
            ss_within = results.get('ss_within', 'N/A')
            ms_within = results.get('ms_within', 'N/A')
            
            if isinstance(ss_within, (int, float)):
                output += f"{'Error':<15} {df_within:<8} {ss_within:<12.4f} {ms_within:<12.4f}\n"
            
            output += "-" * 50 + "\n\n"
            
            # Interpretation
            output += f"F-statistic: {f_stat:.4f}\n"
            output += f"P-value: {p_value:.6f}\n\n"
            
            if p_value < 0.05:
                output += "★ Result: SIGNIFICANT (p < 0.05)\n"
                output += "The factor shows statistically significant variation between groups.\n"
                output += "At least one group mean differs significantly from the others."
            else:
                output += "Result: NOT SIGNIFICANT (p ≥ 0.05)\n"
                output += "No statistically significant variation detected between groups.\n"
                output += "The observed differences may be due to random variation."
            
            # Effect size if available
            if 'eta_squared' in results:
                eta_sq = results['eta_squared']
                output += f"\n\nEffect Size (η²): {eta_sq:.4f}\n"
                if eta_sq < 0.01:
                    output += "Interpretation: Very small effect"
                elif eta_sq < 0.06:
                    output += "Interpretation: Small effect"
                elif eta_sq < 0.14:
                    output += "Interpretation: Medium effect"
                else:
                    output += "Interpretation: Large effect"
            
            self.anova_output.setPlainText(output)
            self.tab_widget.setCurrentIndex(4)
            self.status_bar.showMessage(f"Completed ANOVA analysis: {column} by {subgroup}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not run ANOVA:\n{str(e)}")
    
    def _generate_pareto(self):
        """Generate Pareto chart."""
        if self.data is None:
            QMessageBox.warning(self, "No Data", "Please load a data file first.")
            return
        
        category_col = self.pareto_column.currentText()
        if not category_col:
            return
        
        try:
            chart_path = self.viz_engine.generate_pareto(self.data, category_col)
            
            if chart_path and Path(chart_path).exists():
                pixmap = QPixmap(chart_path)
                scaled = pixmap.scaled(
                    self.pareto_display.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.pareto_display.setPixmap(scaled)
            
            self.status_bar.showMessage(f"Generated Pareto chart for {category_col}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not generate Pareto chart:\n{str(e)}")
    
    def _calculate_roi(self):
        """Calculate ROI."""
        hours = self.hours_saved.value()
        rate = self.hourly_rate.value()
        investment = self.project_cost.value()
        
        annual_savings = hours * rate
        
        output = "ROI Calculation Results\n"
        output += "=" * 50 + "\n\n"
        output += f"Annual Hours Saved: {hours:.1f}\n"
        output += f"Hourly Rate: ${rate:.2f}\n"
        output += f"Annual Savings: ${annual_savings:,.2f}\n"
        output += f"Project Investment: ${investment:,.2f}\n\n"
        
        if investment > 0:
            roi = ((annual_savings - investment) / investment) * 100
            payback_months = (investment / annual_savings) * 12 if annual_savings > 0 else float('inf')
            
            output += f"First Year ROI: {roi:.1f}%\n"
            output += f"Payback Period: {payback_months:.1f} months\n\n"
            
            output += "Multi-Year Projection:\n"
            for year in range(1, 6):
                cumulative = (annual_savings * year) - investment
                output += f"Year {year}: ${cumulative:,.2f}\n"
        else:
            output += "Enter project investment to calculate ROI.\n"
        
        self.roi_output.setPlainText(output)
        self.tab_widget.setCurrentIndex(11)
        self.status_bar.showMessage("ROI calculation complete")
    
    # =================================================================
    # Data Sampling Methods
    # =================================================================
    
    def _generate_sample(self):
        """Generate a random sample from the data."""
        if self.data is None:
            QMessageBox.warning(self, "No Data", "Please load data first.")
            return
        
        column = self.sampling_column.currentText()
        if not column:
            QMessageBox.warning(self, "No Column", "Please select a column to sample from.")
            return
        
        try:
            sample_size = self.sample_size.value()
            seed = self.sampling_seed.value() if self.sampling_seed.value() > 0 else None
            
            # Get valid data (non-null)
            valid_data = self.data[column].dropna()
            
            if len(valid_data) == 0:
                QMessageBox.warning(self, "No Data", "Selected column has no valid data.")
                return
            
            # Adjust sample size if larger than available data
            actual_sample_size = min(sample_size, len(valid_data))
            
            # Generate sample
            if seed is not None:
                np.random.seed(seed)
            
            sample_indices = np.random.choice(len(valid_data), size=actual_sample_size, replace=False)
            sample_data = valid_data.iloc[sample_indices]
            
            # Store for export
            self._last_sample = sample_data
            self._last_sample_column = column
            
            # Generate output
            output = f"Random Sample Results\n"
            output += "=" * 50 + "\n\n"
            output += f"Column: {column}\n"
            output += f"Total Records: {len(valid_data)}\n"
            output += f"Sample Size: {actual_sample_size}\n"
            if seed is not None:
                output += f"Random Seed: {seed}\n"
            output += "\n"
            
            # Summary statistics of sample
            if pd.api.types.is_numeric_dtype(sample_data):
                output += "Sample Statistics:\n"
                output += "-" * 30 + "\n"
                output += f"Mean: {sample_data.mean():.4f}\n"
                output += f"Median: {sample_data.median():.4f}\n"
                output += f"Std Dev: {sample_data.std():.4f}\n"
                output += f"Min: {sample_data.min():.4f}\n"
                output += f"Max: {sample_data.max():.4f}\n"
                output += "\n"
            
            output += "Sample Values:\n"
            output += "-" * 30 + "\n"
            for i, (idx, value) in enumerate(sample_data.items(), 1):
                output += f"{i:3d}. Row {idx}: {value}\n"
            
            self.sampling_output.setPlainText(output)
            self.status_bar.showMessage(f"Generated sample of {actual_sample_size} records")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Sampling failed: {str(e)}")
    
    def _export_sample(self):
        """Export the generated sample to CSV."""
        if not hasattr(self, '_last_sample') or self._last_sample is None:
            QMessageBox.warning(self, "No Sample", "Please generate a sample first.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Sample", f"sample_{self._last_sample_column}.csv",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                # Create DataFrame with original index
                export_df = pd.DataFrame({
                    'Original_Row': self._last_sample.index,
                    self._last_sample_column: self._last_sample.values
                })
                export_df.to_csv(file_path, index=False)
                self.status_bar.showMessage(f"Sample exported to {file_path}")
                QMessageBox.information(self, "Export Complete", 
                    f"Sample exported successfully to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")
    
    # =================================================================
    # Split Worksheet Methods
    # =================================================================
    
    def _preview_split(self):
        """Preview how data will be split by category."""
        if self.data is None:
            QMessageBox.warning(self, "No Data", "Please load data first.")
            return
        
        split_col = self.split_by_column.currentText()
        data_col = self.split_data_column.currentText()
        
        if not split_col:
            QMessageBox.warning(self, "No Column", "Please select a column to split by.")
            return
        
        try:
            # Get unique categories
            categories = self.data[split_col].dropna().unique()
            
            output = f"Split Worksheet Preview\n"
            output += "=" * 50 + "\n\n"
            output += f"Split By: {split_col}\n"
            output += f"Data Column: {data_col}\n"
            output += f"Number of Categories: {len(categories)}\n\n"
            
            output += "Category Summary:\n"
            output += "-" * 50 + "\n"
            
            for cat in sorted(categories, key=str):
                subset = self.data[self.data[split_col] == cat]
                count = len(subset)
                
                output += f"\n{cat}:\n"
                output += f"  Records: {count}\n"
                
                if data_col and data_col in subset.columns:
                    col_data = subset[data_col].dropna()
                    if pd.api.types.is_numeric_dtype(col_data) and len(col_data) > 0:
                        output += f"  {data_col} Mean: {col_data.mean():.4f}\n"
                        output += f"  {data_col} Std Dev: {col_data.std():.4f}\n"
            
            self.split_output.setPlainText(output)
            self.status_bar.showMessage(f"Preview: {len(categories)} categories found")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Preview failed: {str(e)}")
    
    def _export_split(self):
        """Export data split into separate files by category."""
        if self.data is None:
            QMessageBox.warning(self, "No Data", "Please load data first.")
            return
        
        split_col = self.split_by_column.currentText()
        
        if not split_col:
            QMessageBox.warning(self, "No Column", "Please select a column to split by.")
            return
        
        # Ask for output directory
        output_dir = QFileDialog.getExistingDirectory(
            self, "Select Output Directory for Split Files"
        )
        
        if not output_dir:
            return
        
        try:
            categories = self.data[split_col].dropna().unique()
            exported_files = []
            
            for cat in categories:
                subset = self.data[self.data[split_col] == cat]
                
                # Create safe filename
                safe_name = str(cat).replace('/', '_').replace('\\', '_').replace(' ', '_')
                file_path = Path(output_dir) / f"split_{safe_name}.csv"
                
                subset.to_csv(file_path, index=False)
                exported_files.append(f"{cat}: {len(subset)} records")
            
            output = f"Split Export Complete\n"
            output += "=" * 50 + "\n\n"
            output += f"Output Directory: {output_dir}\n"
            output += f"Files Created: {len(categories)}\n\n"
            output += "Exported Files:\n"
            output += "-" * 30 + "\n"
            for f in exported_files:
                output += f"  {f}\n"
            
            self.split_output.setPlainText(output)
            self.status_bar.showMessage(f"Exported {len(categories)} split files")
            
            QMessageBox.information(self, "Export Complete",
                f"Successfully exported {len(categories)} files to:\n{output_dir}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")
    
    # =================================================================
    # Process Diagram Handler Methods
    # =================================================================
    
    def _generate_sipoc(self):
        """Generate SIPOC diagram."""
        try:
            suppliers = [s.strip() for s in self.sipoc_suppliers.toPlainText().strip().split('\n') if s.strip()]
            inputs = [i.strip() for i in self.sipoc_inputs.toPlainText().strip().split('\n') if i.strip()]
            process = [p.strip() for p in self.sipoc_process.toPlainText().strip().split('\n') if p.strip()]
            outputs = [o.strip() for o in self.sipoc_outputs.toPlainText().strip().split('\n') if o.strip()]
            requirements = [r.strip() for r in self.sipoc_requirements.toPlainText().strip().split('\n') if r.strip()]
            customers = [c.strip() for c in self.sipoc_customers.toPlainText().strip().split('\n') if c.strip()]
            title = self.sipoc_title.text() or "SIPOC Diagram"
            
            if not any([suppliers, inputs, process, outputs, customers]):
                QMessageBox.warning(self, "Missing Data", "Please enter data in at least one field.")
                return
            
            chart_path = self.diagram_engine.generate_sipoc(
                suppliers=suppliers or ['(None)'],
                inputs=inputs or ['(None)'],
                process_steps=process or ['Process Step'],
                outputs=outputs or ['(None)'],
                customers=customers or ['(None)'],
                requirements=requirements,
                title=title
            )
            
            pixmap = QPixmap(str(chart_path))
            scaled = pixmap.scaled(
                self.sipoc_display.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.sipoc_display.setPixmap(scaled)
            self.sipoc_display.setAccessibleDescription(f"SIPOC Diagram: {title}")
            self.status_bar.showMessage("SIPOC diagram generated")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not generate SIPOC diagram:\n{str(e)}")
    
    def _generate_process_map(self):
        """Generate process map flowchart."""
        try:
            steps = [s.strip() for s in self.process_map_steps.toPlainText().strip().split('\n') if s.strip()]
            title = self.process_map_title.text() or "Process Map"
            
            if not steps:
                QMessageBox.warning(self, "Missing Data", "Please enter process steps.")
                return
            
            chart_path = self.diagram_engine.generate_process_map(steps=steps, title=title)
            
            pixmap = QPixmap(str(chart_path))
            scaled = pixmap.scaled(
                self.process_map_display.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.process_map_display.setPixmap(scaled)
            self.process_map_display.setAccessibleDescription(f"Process Map: {title}")
            self.status_bar.showMessage("Process map generated")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not generate process map:\n{str(e)}")
    
    def _generate_raci(self):
        """Generate RACI matrix."""
        try:
            roles_text = self.raci_roles.text().strip()
            tasks_text = self.raci_tasks.toPlainText().strip()
            title = self.raci_title.text() or "RACI Matrix"
            
            if not roles_text or not tasks_text:
                QMessageBox.warning(self, "Missing Data", "Please enter roles and tasks.")
                return
            
            roles = [r.strip() for r in roles_text.split(',') if r.strip()]
            
            tasks = []
            matrix = []
            for line in tasks_text.split('\n'):
                if '|' in line:
                    parts = line.split('|')
                    task_name = parts[0].strip()
                    assignments = [a.strip().upper() for a in parts[1].split(',')]
                    # Pad or trim to match number of roles
                    while len(assignments) < len(roles):
                        assignments.append('')
                    assignments = assignments[:len(roles)]
                    tasks.append(task_name)
                    matrix.append(assignments)
            
            if not tasks:
                QMessageBox.warning(self, "Invalid Format", "Use format: Task Name | R,A,C,I")
                return
            
            chart_path = self.diagram_engine.generate_raci(
                tasks=tasks,
                roles=roles,
                matrix=matrix,
                title=title
            )
            
            pixmap = QPixmap(str(chart_path))
            scaled = pixmap.scaled(
                self.raci_display.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.raci_display.setPixmap(scaled)
            self.raci_display.setAccessibleDescription(f"RACI Matrix: {title}")
            self.status_bar.showMessage("RACI matrix generated")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not generate RACI matrix:\n{str(e)}")
    
    def _generate_swimlane(self):
        """Generate swim lane diagram."""
        try:
            steps_text = self.swimlane_steps.toPlainText().strip()
            title = self.swimlane_title.text() or "Swim Lane Diagram"
            
            if not steps_text:
                QMessageBox.warning(self, "Missing Data", "Please enter swim lane steps.")
                return
            
            steps = []
            for line in steps_text.split('\n'):
                if '|' in line:
                    parts = line.split('|')
                    lane = parts[0].strip()
                    step = parts[1].strip()
                    steps.append(f"{lane} | {step}")
            
            if not steps:
                QMessageBox.warning(self, "Invalid Format", "Use format: Lane Name | Step Description")
                return
            
            chart_path = self.diagram_engine.generate_swimlane(steps=steps, title=title)
            
            pixmap = QPixmap(str(chart_path))
            scaled = pixmap.scaled(
                self.swimlane_display.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.swimlane_display.setPixmap(scaled)
            self.swimlane_display.setAccessibleDescription(f"Swim Lane Diagram: {title}")
            self.status_bar.showMessage("Swim lane diagram generated")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not generate swim lane diagram:\n{str(e)}")
    
    def _generate_vsm(self):
        """Generate value stream map."""
        try:
            steps_text = self.vsm_steps.toPlainText().strip()
            title = self.vsm_title.text() or "Value Stream Map"
            
            if not steps_text:
                QMessageBox.warning(self, "Missing Data", "Please enter VSM steps.")
                return
            
            steps = []
            for line in steps_text.split('\n'):
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 3:
                    try:
                        name = parts[0]
                        cycle_time = float(parts[1])
                        wait_time = float(parts[2])
                        steps.append((name, cycle_time, wait_time))
                    except ValueError:
                        continue
            
            if not steps:
                QMessageBox.warning(self, "Invalid Format", "Use format: Step Name, Cycle Time, Wait Time")
                return
            
            chart_path = self.diagram_engine.generate_vsm(steps=steps, title=title)
            
            pixmap = QPixmap(str(chart_path))
            scaled = pixmap.scaled(
                self.vsm_display.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.vsm_display.setPixmap(scaled)
            
            # Calculate and display metrics
            total_cycle = sum(s[1] for s in steps)
            total_wait = sum(s[2] for s in steps)
            lead_time = total_cycle + total_wait
            efficiency = (total_cycle / lead_time * 100) if lead_time > 0 else 0
            
            metrics_text = f"Lead Time: {lead_time:.0f} min | "
            metrics_text += f"Cycle Time (VA): {total_cycle:.0f} min | "
            metrics_text += f"Wait Time (NVA): {total_wait:.0f} min | "
            metrics_text += f"Process Efficiency: {efficiency:.1f}%"
            self.vsm_metrics.setPlainText(metrics_text)
            
            self.vsm_display.setAccessibleDescription(f"Value Stream Map: {title}. {metrics_text}")
            self.status_bar.showMessage("Value stream map generated")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not generate value stream map:\n{str(e)}")
    
    def _generate_fishbone(self):
        """Generate fishbone (Ishikawa) diagram."""
        try:
            effect = self.fishbone_effect.text().strip()
            title = self.fishbone_title.text() or "Fishbone Diagram"
            
            if not effect:
                QMessageBox.warning(self, "Missing Data", "Please enter the effect/problem.")
                return
            
            causes = {}
            for cat_name, text_edit in self.fishbone_causes.items():
                cat_causes = [c.strip() for c in text_edit.toPlainText().strip().split('\n') if c.strip()]
                if cat_causes:
                    causes[cat_name] = cat_causes
            
            chart_path = self.diagram_engine.generate_fishbone(
                effect=effect,
                causes=causes,
                title=title
            )
            
            pixmap = QPixmap(str(chart_path))
            scaled = pixmap.scaled(
                self.fishbone_display.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.fishbone_display.setPixmap(scaled)
            self.fishbone_display.setAccessibleDescription(f"Fishbone Diagram: {title}. Effect: {effect}")
            self.status_bar.showMessage("Fishbone diagram generated")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not generate fishbone diagram:\n{str(e)}")
    
    # =================================================================
    # New Statistical Analysis Methods
    # =================================================================
    
    def _generate_correlation(self):
        """Generate correlation analysis with scatter plot."""
        if self.data is None:
            QMessageBox.warning(self, "No Data", "Please load a data file first.")
            return
        
        x_col = self.corr_x_combo.currentText()
        y_col = self.corr_y_combo.currentText()
        
        if not x_col or not y_col:
            QMessageBox.warning(self, "Missing Selection", "Please select both X and Y variables.")
            return
        
        if x_col == y_col:
            QMessageBox.warning(self, "Same Variable", "Please select different variables for X and Y.")
            return
        
        try:
            x_data = self.data[x_col].dropna().values
            y_data = self.data[y_col].dropna().values
            
            # Align data (both must have values)
            df_temp = self.data[[x_col, y_col]].dropna()
            x_data = df_temp[x_col].values
            y_data = df_temp[y_col].values
            
            if len(x_data) < 3:
                QMessageBox.warning(self, "Insufficient Data", 
                                   "Need at least 3 paired observations for correlation analysis.")
                return
            
            # Run correlation analysis
            results = self.stats_engine.correlation_analysis(x_data, y_data)
            
            # Generate scatter plot
            show_regression = self.show_regression_check.isChecked()
            chart_path = self.viz_engine.generate_correlation_scatter(
                x_data, y_data, x_col, y_col,
                correlation_results=results,
                show_regression=show_regression
            )
            
            # Display chart
            pixmap = QPixmap(str(chart_path))
            scaled = pixmap.scaled(
                self.correlation_display.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.correlation_display.setPixmap(scaled)
            
            # Build output text
            output = "Correlation Analysis Results\n"
            output += "=" * 50 + "\n\n"
            output += f"Variables: {y_col} vs {x_col}\n"
            output += f"Sample Size (n): {results['n']}\n\n"
            output += f"Pearson Correlation (r): {results['r']:.4f}\n"
            output += f"R-Squared (R²): {results['r_squared']:.4f}\n"
            output += f"P-Value: {results['p_value']:.6f}\n\n"
            output += f"Interpretation: {results['interpretation']}\n\n"
            
            if show_regression:
                output += f"Regression: y = {results['slope']:.4f}x + {results['intercept']:.4f}\n"
                output += f"Standard Error: {results['std_err']:.4f}\n"
            
            output += "\n⚠ Note: Correlation does not prove causation."
            
            self.correlation_output.setPlainText(output)
            self.status_bar.showMessage(f"Correlation analysis complete: r = {results['r']:.4f}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not generate correlation analysis:\n{str(e)}")
    
    def _generate_run_chart(self):
        """Generate run chart with runs analysis."""
        if self.data is None:
            QMessageBox.warning(self, "No Data", "Please load a data file first.")
            return
        
        column = self.column_combo.currentText()
        if not column:
            QMessageBox.warning(self, "No Column", "Please select a column to analyze.")
            return
        
        try:
            data = self.data[column].dropna().values
            
            if len(data) < 10:
                QMessageBox.warning(self, "Insufficient Data", 
                                   "Need at least 10 data points for run chart analysis.")
                return
            
            # Run analysis
            results = self.stats_engine.run_chart_analysis(data)
            
            # Generate chart
            chart_path = self.viz_engine.generate_run_chart(data, column, run_results=results)
            
            # Display chart
            pixmap = QPixmap(str(chart_path))
            scaled = pixmap.scaled(
                self.run_chart_display.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.run_chart_display.setPixmap(scaled)
            
            # Build output text
            output = "Run Chart Analysis\n"
            output += "=" * 40 + "\n"
            output += f"n = {results['n']} | "
            output += f"Median = {results['median']:.2f} | "
            output += f"Mean = {results['mean']:.2f}\n"
            output += f"Runs = {results['n_runs']} (Expected: {results['expected_runs']:.1f}) | "
            output += f"p-value = {results['p_value']:.4f}\n\n"
            output += results['interpretation']
            
            self.run_chart_output.setPlainText(output)
            self.status_bar.showMessage(f"Run chart generated: {results['n_runs']} runs detected")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not generate run chart:\n{str(e)}")
    
    def _generate_histogram(self):
        """Generate standalone histogram."""
        if self.data is None:
            QMessageBox.warning(self, "No Data", "Please load a data file first.")
            return
        
        column = self.column_combo.currentText()
        if not column:
            QMessageBox.warning(self, "No Column", "Please select a column to analyze.")
            return
        
        try:
            data = self.data[column].dropna().values
            
            if len(data) < 5:
                QMessageBox.warning(self, "Insufficient Data", 
                                   "Need at least 5 data points for histogram.")
                return
            
            # Get settings
            show_normal = self.show_normal_check.isChecked()
            bins_value = self.histogram_bins.value()
            bins = 'auto' if bins_value == 0 else bins_value
            
            # Generate chart
            chart_path = self.viz_engine.generate_standalone_histogram(
                data, column, bins=bins, show_normal=show_normal
            )
            
            # Display chart
            pixmap = QPixmap(str(chart_path))
            scaled = pixmap.scaled(
                self.histogram_display.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.histogram_display.setPixmap(scaled)
            self.histogram_display.setAccessibleDescription(f"Histogram of {column}")
            self.status_bar.showMessage(f"Histogram generated for {column}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not generate histogram:\n{str(e)}")
    
    def _generate_boxplot(self):
        """Generate standalone box plot."""
        if self.data is None:
            QMessageBox.warning(self, "No Data", "Please load a data file first.")
            return
        
        column = self.column_combo.currentText()
        if not column:
            QMessageBox.warning(self, "No Column", "Please select a column to analyze.")
            return
        
        try:
            data = self.data[column].dropna().values
            
            if len(data) < 5:
                QMessageBox.warning(self, "Insufficient Data", 
                                   "Need at least 5 data points for box plot.")
                return
            
            # Get settings
            show_points = self.show_points_check.isChecked()
            
            # Generate chart
            chart_path = self.viz_engine.generate_standalone_boxplot(
                data, column, show_points=show_points
            )
            
            # Display chart
            pixmap = QPixmap(str(chart_path))
            scaled = pixmap.scaled(
                self.boxplot_display.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.boxplot_display.setPixmap(scaled)
            self.boxplot_display.setAccessibleDescription(f"Box plot of {column}")
            self.status_bar.showMessage(f"Box plot generated for {column}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not generate box plot:\n{str(e)}")
    
    def _save_report(self):
        """Save analysis report."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Report",
            str(Path.home() / "CiviQual_Report.docx"),
            "Word Document (*.docx);;HTML (*.html);;All Files (*)"
        )
        
        if file_path:
            try:
                self.report_gen.generate_report(file_path, self.data, self.stats_engine)
                self.status_bar.showMessage(f"Report saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save report:\n{str(e)}")
    
    def _export_chart(self):
        """Export current chart as image."""
        # Map tab indices to their chart display widgets
        chart_displays = {
            0: self.four_up_display,           # CiviQual 4-Up Chart
            2: self.control_display,           # Control Charts
            3: self.capability_chart_display,  # Capability Analysis
            4: self.prob_plot_display,         # Probability Plot
            5: self.anova_chart_display,       # ANOVA
            6: self.correlation_display,       # Correlation
            7: self.run_chart_display,         # Run Chart
            8: self.histogram_display,         # Histogram
            9: self.boxplot_display,           # Box Plot
            10: self.pareto_display,           # Pareto Analysis
            14: self.sipoc_display,            # SIPOC Diagram
            15: self.process_map_display,      # Process Map
            16: self.raci_display,             # RACI Matrix
            17: self.swimlane_display,         # Swim Lane
            18: self.vsm_display,              # Value Stream Map
            19: self.fishbone_display,         # Fishbone Diagram
        }
        
        current_tab = self.tab_widget.currentIndex()
        
        if current_tab not in chart_displays:
            QMessageBox.warning(
                self, "No Chart", 
                "The current tab does not contain an exportable chart.\n"
                "Please switch to a tab with a chart and try again."
            )
            return
        
        display_widget = chart_displays[current_tab]
        pixmap = display_widget.pixmap()
        
        if pixmap is None or pixmap.isNull():
            QMessageBox.warning(
                self, "No Chart",
                "No chart has been generated yet.\n"
                "Please generate a chart first, then export."
            )
            return
        
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Chart",
            str(Path.home() / "CiviQual_Chart.png"),
            "PNG Image (*.png);;JPEG Image (*.jpg);;All Files (*)"
        )
        
        if file_path:
            # Determine format from extension or filter
            if file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
                img_format = 'JPEG'
                quality = 95
            else:
                img_format = 'PNG'
                quality = -1  # Default PNG compression
                if not file_path.lower().endswith('.png'):
                    file_path += '.png'
            
            if pixmap.save(file_path, img_format, quality):
                self.status_bar.showMessage(f"Chart exported to {file_path}")
                QMessageBox.information(
                    self, "Export Successful",
                    f"Chart exported successfully to:\n{file_path}"
                )
            else:
                QMessageBox.critical(
                    self, "Export Failed",
                    f"Could not save chart to:\n{file_path}\n\n"
                    "Please check that you have write permissions to this location."
                )
    
    # =========================================================================
    # Help Methods
    # =========================================================================
    def _show_guide(self):
        """Show quick reference guide."""
        QMessageBox.information(
            self,
            "Quick Reference",
            "CiviQual Quick Reference\n\n"
            "1. Load Data: Click 'Load Data File' or press Ctrl+O\n"
            "2. Select Column: Choose the numeric column to analyze\n"
            "3. Generate Charts: Use the tabs to access different analyses\n"
            "4. Save Results: Export charts and reports from File menu\n\n"
            "Press Ctrl+? for keyboard shortcuts\n"
            "Press Ctrl+Shift+F1 for accessibility information"
        )
    
    def _show_keyboard_shortcuts(self):
        """Show keyboard shortcuts dialog."""
        dialog = KeyboardShortcutsDialog(self)
        dialog.exec()
    
    def _show_accessibility_info(self):
        """Show accessibility information dialog."""
        dialog = AccessibilityInfoDialog(self)
        dialog.exec()
    
    def _show_user_guide(self):
        """Display user guide in a dialog."""
        dialog = QDialog(self)
        dialog.setWindowTitle("CiviQual User Guide")
        dialog.setMinimumSize(850, 700)
        dialog.resize(900, 750)
        
        layout = QVBoxLayout(dialog)
        
        # Create text browser for guide content
        guide_text = QTextBrowser()
        guide_text.setOpenExternalLinks(True)
        guide_text.setHtml(self._get_user_guide_content())
        layout.addWidget(guide_text)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        dialog.exec()
    
    def _get_user_guide_content(self):
        """Return HTML content for user guide."""
        return """
        <html>
        <head>
        <style>
            body { font-family: Arial, Arial, sans-serif; margin: 20px; line-height: 1.5; }
            h1 { color: #6d132a; border-bottom: 2px solid #6d132a; padding-bottom: 10px; }
            h2 { color: #6d132a; margin-top: 30px; border-bottom: 1px solid #ccc; padding-bottom: 5px; }
            h3 { color: #4a0919; margin-top: 20px; }
            h4 { color: #333; margin-top: 15px; }
            table { border-collapse: collapse; width: 100%; margin: 10px 0; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #6d132a; color: white; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            .tip { background-color: #e8f4f8; padding: 10px; border-left: 4px solid #6d132a; margin: 10px 0; }
            .warning { background-color: #fff3e0; padding: 10px; border-left: 4px solid #dcad73; margin: 10px 0; }
            code { background-color: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: Consolas, monospace; }
            pre { background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }
            .phase { display: inline-block; padding: 2px 8px; border-radius: 3px; font-size: 0.85em; margin-left: 10px; }
            .define { background-color: #e3f2fd; color: #1565c0; }
            .measure { background-color: #e8f5e9; color: #2e7d32; }
            .analyze { background-color: #fff3e0; color: #ef6c00; }
            .improve { background-color: #fce4ec; color: #c2185b; }
            .control { background-color: #f3e5f5; color: #7b1fa2; }
        </style>
        </head>
        <body>
        
        <h1>CiviQual User Guide</h1>
        <p><strong>Version 1.3</strong> — for Lean Six Sigma</p>
        <p><strong>W</strong>orkbench for <strong>A</strong>nalysis, <strong>T</strong>esting, <strong>S</strong>tatistics, <strong>O</strong>ptimization &amp; <strong>N</strong>avigation</p>
        <p>A statistical analysis tool for Lean Six Sigma practitioners in government and public service organizations.</p>
        
        <h2>Getting Started</h2>
        <ol>
            <li><strong>Load Data:</strong> Click "Load Data File" or press <code>Ctrl+O</code> to open a CSV or Excel file</li>
            <li><strong>View Data:</strong> The data table shows your loaded data with row/column counts in the status bar</li>
            <li><strong>Select Column:</strong> Choose a numeric column from the dropdown for analysis</li>
            <li><strong>Select Subgroup:</strong> Optionally select a categorical column for grouped analysis</li>
            <li><strong>Navigate Tabs:</strong> Use the 18 analysis tabs organized by DMAIC phase</li>
            <li><strong>Generate Charts:</strong> Click Generate buttons to create visualizations</li>
            <li><strong>Export Results:</strong> Use File menu to export reports and charts</li>
        </ol>
        
        <h2>Statistical Analysis Tools</h2>
        
        <h3>CiviQual 4-Up Chart <span class="phase measure">Measure</span></h3>
        <p>The signature CiviQual analysis providing four complementary views of your data in a single chart. Based on the exploratory data analysis methodology developed by Dr. Gregory H. Watson.</p>
        <table>
            <tr><th>Quadrant</th><th>Chart Type</th><th>Purpose</th></tr>
            <tr><td>Upper Left</td><td>Statistical Summary</td><td>Histogram with normal curve overlay and descriptive statistics</td></tr>
            <tr><td>Upper Right</td><td>Probability Plot</td><td>Normality assessment with 95% confidence band</td></tr>
            <tr><td>Lower Left</td><td>I-Chart</td><td>Individuals control chart for stability assessment</td></tr>
            <tr><td>Lower Right</td><td>Capability (Cp=1.0)</td><td>Natural tolerance limits based on process variation (±3σ)</td></tr>
        </table>
        <div class="tip"><strong>Tip:</strong> The 4-Up Chart is ideal for initial data exploration. It answers: Is the data normal? Is the process stable? What is the natural process spread?</div>
        
        <h3>Descriptive Statistics <span class="phase measure">Measure</span></h3>
        <p>Calculates comprehensive statistics for the selected column:</p>
        <ul>
            <li><strong>Central Tendency:</strong> Mean, Median, Mode</li>
            <li><strong>Dispersion:</strong> Standard Deviation, Variance, Range, IQR</li>
            <li><strong>Shape:</strong> Skewness, Kurtosis</li>
            <li><strong>Position:</strong> Min, Max, Quartiles (Q1, Q3)</li>
            <li><strong>Inference:</strong> Standard Error, 95% Confidence Interval for Mean</li>
            <li><strong>Normality:</strong> Anderson-Darling test statistic and result</li>
        </ul>
        
        <h3>Control Charts <span class="phase control">Control</span></h3>
        <p>Generate I-Chart (Individuals) or I-MR Chart (Individuals and Moving Range) for process monitoring.</p>
        <h4>Western Electric Rules for Special Cause Detection:</h4>
        <table>
            <tr><th>Rule</th><th>Description</th><th>Indication</th></tr>
            <tr><td>Rule 1</td><td>1 point beyond 3σ</td><td>Extreme value - investigate immediately</td></tr>
            <tr><td>Rule 2</td><td>9 consecutive points on same side of center</td><td>Process shift</td></tr>
            <tr><td>Rule 3</td><td>6 consecutive points trending up or down</td><td>Process drift/trend</td></tr>
            <tr><td>Rule 4</td><td>14 points alternating up and down</td><td>Over-adjustment or two processes</td></tr>
        </table>
        <div class="tip"><strong>Interpretation:</strong> Flagged points appear in red. A stable process shows only common cause variation (random scatter within limits).</div>
        
        <h3>Capability Analysis <span class="phase measure">Measure</span></h3>
        <p>Compares process performance to customer specifications.</p>
        <h4>Required Inputs:</h4>
        <ul>
            <li><strong>LSL:</strong> Lower Specification Limit</li>
            <li><strong>USL:</strong> Upper Specification Limit</li>
            <li><strong>Target:</strong> Target value (optional)</li>
        </ul>
        <h4>Capability Indices:</h4>
        <table>
            <tr><th>Index</th><th>Formula</th><th>Interpretation</th></tr>
            <tr><td>Cp</td><td>(USL - LSL) / 6σ</td><td>Potential capability (spread vs. tolerance)</td></tr>
            <tr><td>Cpk</td><td>min(Cpu, Cpl)</td><td>Actual capability (accounts for centering)</td></tr>
            <tr><td>Cpu</td><td>(USL - Mean) / 3σ</td><td>Upper capability</td></tr>
            <tr><td>Cpl</td><td>(Mean - LSL) / 3σ</td><td>Lower capability</td></tr>
        </table>
        <h4>Capability Ratings:</h4>
        <table>
            <tr><th>Cpk Value</th><th>Rating</th><th>PPM Defects (approx)</th></tr>
            <tr><td>≥ 2.0</td><td>Excellent (Six Sigma)</td><td>&lt; 3.4</td></tr>
            <tr><td>≥ 1.33</td><td>Capable</td><td>&lt; 66</td></tr>
            <tr><td>≥ 1.0</td><td>Marginal</td><td>&lt; 2,700</td></tr>
            <tr><td>&lt; 1.0</td><td>Not Capable</td><td>&gt; 2,700</td></tr>
        </table>
        <div class="tip"><strong>Cp=1.0 Option:</strong> Check this box to display natural tolerance limits (Mean ± 3σ) on the chart. This shows what specifications would need to be for Cp=1.0.</div>
        
        <h3>Probability Plot <span class="phase measure">Measure</span></h3>
        <p>Assesses whether data follows a normal distribution using a graphical method.</p>
        <h4>Features:</h4>
        <ul>
            <li><strong>Probability Scale:</strong> Y-axis uses probability scaling (0.1, 1, 5, 10... 90, 95, 99, 99.9%)</li>
            <li><strong>95% Confidence Band:</strong> Blue shaded region shows expected range for normal data</li>
            <li><strong>Fit Line:</strong> Orange line represents the fitted normal distribution</li>
            <li><strong>Anderson-Darling Test:</strong> Statistical test for normality with p-value</li>
        </ul>
        <h4>Interpretation:</h4>
        <ul>
            <li>Points falling <strong>within the confidence band</strong> → Data fits normal distribution</li>
            <li>Points falling <strong>outside the band</strong> → Deviation from normality</li>
            <li><strong>p &gt; 0.05</strong> → Fail to reject normality (data is likely normal)</li>
            <li><strong>p &lt; 0.05</strong> → Reject normality (data may not be normal)</li>
        </ul>
        <div class="tip"><strong>Multi-Series:</strong> Select multiple columns to compare distributions on the same plot.</div>
        
        <h3>ANOVA <span class="phase analyze">Analyze</span></h3>
        <p>Analysis of Variance compares means across groups defined by a subgroup column.</p>
        <ul>
            <li>Generates box plots showing group distributions</li>
            <li>Calculates F-statistic and p-value</li>
            <li>Shows group means and standard deviations</li>
        </ul>
        <div class="tip"><strong>p &lt; 0.05</strong> indicates statistically significant differences between groups.</div>
        
        <h3>Correlation <span class="phase analyze">Analyze</span></h3>
        <p>Analyzes the relationship between two numeric variables.</p>
        <ul>
            <li><strong>Scatter Plot:</strong> Visual display of relationship</li>
            <li><strong>Regression Line:</strong> Best-fit linear trend</li>
            <li><strong>Pearson r:</strong> Correlation coefficient (-1 to +1)</li>
            <li><strong>R²:</strong> Coefficient of determination (variance explained)</li>
            <li><strong>p-value:</strong> Statistical significance of correlation</li>
        </ul>
        
        <h3>Run Chart <span class="phase measure">Measure</span></h3>
        <p>Time-series plot showing data in sequence order with median line.</p>
        <ul>
            <li>Useful for detecting trends and patterns over time</li>
            <li>Simpler than control charts (no control limits)</li>
            <li>Shows median as reference line</li>
        </ul>
        
        <h3>Histogram <span class="phase measure">Measure</span></h3>
        <p>Frequency distribution chart showing data shape.</p>
        <ul>
            <li>Adjustable number of bins</li>
            <li>Normal curve overlay option</li>
            <li>Shows mean and standard deviation lines</li>
        </ul>
        
        <h3>Box Plot <span class="phase measure">Measure</span></h3>
        <p>Five-number summary visualization (Min, Q1, Median, Q3, Max).</p>
        <ul>
            <li>Shows data spread and central tendency</li>
            <li>Identifies outliers (points beyond 1.5×IQR)</li>
            <li>Can be grouped by subgroup column</li>
        </ul>
        
        <h3>Pareto Analysis <span class="phase analyze">Analyze</span></h3>
        <p>Identifies the "vital few" causes using the 80/20 principle.</p>
        <ul>
            <li>Bar chart sorted by frequency (descending)</li>
            <li>Cumulative percentage line</li>
            <li>80% reference line to identify vital few</li>
        </ul>
        <div class="tip"><strong>Use for:</strong> Defect analysis, complaint categories, error types, delay causes</div>
        
        <h3>ROI Calculator <span class="phase improve">Improve</span></h3>
        <p>Calculates return on investment for process improvement projects.</p>
        <h4>Inputs:</h4>
        <ul>
            <li><strong>Project Cost:</strong> Total investment in the improvement</li>
            <li><strong>Annual Savings:</strong> Expected yearly cost reduction</li>
            <li><strong>Time Period:</strong> Analysis horizon (years)</li>
        </ul>
        <h4>Outputs:</h4>
        <ul>
            <li>Net Present Value (NPV)</li>
            <li>ROI Percentage</li>
            <li>Payback Period</li>
            <li>Break-even chart</li>
        </ul>
        
        <h2>Process Diagram Tools</h2>
        
        <h3>SIPOC Diagram <span class="phase define">Define</span></h3>
        <p>High-level process overview mapping:</p>
        <ul>
            <li><strong>S</strong>uppliers - Who provides inputs</li>
            <li><strong>I</strong>nputs - What is needed</li>
            <li><strong>P</strong>rocess - High-level steps (3-7 steps)</li>
            <li><strong>O</strong>utputs - What is produced</li>
            <li><strong>C</strong>ustomers - Who receives outputs</li>
        </ul>
        
        <h3>Process Map <span class="phase define">Define</span></h3>
        <p>Flowchart showing process steps with decision points.</p>
        <h4>Step Prefixes:</h4>
        <table>
            <tr><th>Prefix</th><th>Shape</th><th>Use For</th></tr>
            <tr><td><code>[S]</code></td><td>Oval</td><td>Start or End points</td></tr>
            <tr><td><code>[D]</code></td><td>Diamond</td><td>Decision points (Yes/No)</td></tr>
            <tr><td>(none)</td><td>Rectangle</td><td>Process steps</td></tr>
        </table>
        <h4>Decision Branching:</h4>
        <ul>
            <li><strong>Yes →</strong> Flow continues downward to next step</li>
            <li><strong>No →</strong> Indicates return/rework (labeled to the left)</li>
        </ul>
        <pre>[S] Start
Receive Application
Review for Completeness
[D] Complete?
Process Application
[S] End</pre>
        
        <h3>RACI Matrix <span class="phase define">Define</span></h3>
        <p>Responsibility assignment matrix:</p>
        <ul>
            <li><strong>R</strong>esponsible - Does the work</li>
            <li><strong>A</strong>ccountable - Ultimately answerable (one per task)</li>
            <li><strong>C</strong>onsulted - Provides input</li>
            <li><strong>I</strong>nformed - Kept updated</li>
        </ul>
        
        <h3>Swim Lane Diagram <span class="phase define">Define</span></h3>
        <p>Process flow organized by role/department.</p>
        <p>Format: <code>Role: Step description</code></p>
        <pre>Clerk: Receive application
Supervisor: Review application
Clerk: Enter into system
Manager: Approve request</pre>
        
        <h3>Value Stream Map <span class="phase analyze">Analyze</span></h3>
        <p>Visualizes material and information flow with timing data.</p>
        <ul>
            <li>Cycle Time (CT) - Processing time</li>
            <li>Wait Time (WT) - Queue/delay time</li>
            <li>Process Efficiency = CT / (CT + WT)</li>
        </ul>
        
        <h3>Fishbone Diagram <span class="phase analyze">Analyze</span></h3>
        <p>Cause-and-effect (Ishikawa) diagram for root cause analysis.</p>
        <h4>Default Categories (6 P's for Service):</h4>
        <ul>
            <li><strong>People</strong> - Staff-related causes</li>
            <li><strong>Process</strong> - Procedure-related causes</li>
            <li><strong>Policy</strong> - Rule/regulation causes</li>
            <li><strong>Place</strong> - Environment/location causes</li>
            <li><strong>Technology</strong> - System/equipment causes</li>
            <li><strong>Measurement</strong> - Data/metrics causes</li>
        </ul>
        
        <h2>Keyboard Shortcuts</h2>
        <table>
            <tr><th>Shortcut</th><th>Action</th></tr>
            <tr><td><code>Ctrl+O</code></td><td>Open data file</td></tr>
            <tr><td><code>Ctrl+S</code></td><td>Export report</td></tr>
            <tr><td><code>Ctrl+D</code></td><td>Calculate descriptive statistics</td></tr>
            <tr><td><code>F1</code></td><td>Open User Guide</td></tr>
            <tr><td><code>Ctrl+?</code></td><td>Keyboard shortcuts dialog</td></tr>
            <tr><td><code>Ctrl+Shift+F1</code></td><td>Accessibility information</td></tr>
            <tr><td><code>Ctrl+C</code></td><td>Copy selected data</td></tr>
            <tr><td><code>Tab</code></td><td>Navigate between controls</td></tr>
            <tr><td><code>Enter</code></td><td>Activate focused button</td></tr>
        </table>
        
        <h2>Sample Data Files</h2>
        <p>Sample datasets are included in the <code>samples/</code> folder for practice:</p>
        <table>
            <tr><th>File</th><th>Domain</th><th>Key Metrics</th></tr>
            <tr><td>sample_data.csv</td><td>Generic Government</td><td>Processing days, request types, volume</td></tr>
            <tr><td>sample_court_cases.csv</td><td>Court Administration</td><td>Filing to disposition time, hearings count</td></tr>
            <tr><td>sample_court_clerk.csv</td><td>Clerk Operations</td><td>Processing time, queue time, accuracy</td></tr>
            <tr><td>sample_permits.csv</td><td>Permit Processing</td><td>Processing days, review cycles</td></tr>
            <tr><td>sample_311_services.csv</td><td>Municipal Services</td><td>Response hours, resolution days</td></tr>
            <tr><td>sample_public_records.csv</td><td>FOIA Requests</td><td>Response days, pages produced</td></tr>
            <tr><td>sample_benefits.csv</td><td>Benefits Processing</td><td>Processing days, review time</td></tr>
            <tr><td>sample_citizen_services.csv</td><td>Citizen Services</td><td>Wait time, service time, satisfaction</td></tr>
            <tr><td>sample_inspections.csv</td><td>Regulatory</td><td>Scheduling days, inspection time</td></tr>
            <tr><td>sample_public_health.csv</td><td>Public Health</td><td>Wait time, service time by clinic type</td></tr>
            <tr><td>sample_mail_processing.csv</td><td>Mail Operations</td><td>Processing time, items count, errors</td></tr>
        </table>
        
        <h2>About DMAIC Phases</h2>
        <p>CiviQual tools are organized by Lean Six Sigma DMAIC phases:</p>
        <table>
            <tr><th>Phase</th><th>Purpose</th><th>CiviQual Tools</th></tr>
            <tr><td><span class="phase define">Define</span></td><td>Define the problem and scope</td><td>SIPOC, Process Map, RACI, Swim Lane</td></tr>
            <tr><td><span class="phase measure">Measure</span></td><td>Measure current performance</td><td>4-Up Chart, Descriptive Stats, I-Chart, Run Chart, Histogram, Box Plot, Probability Plot, Capability</td></tr>
            <tr><td><span class="phase analyze">Analyze</span></td><td>Analyze root causes</td><td>Pareto, ANOVA, Correlation, Fishbone, Value Stream Map, Swim Lane</td></tr>
            <tr><td><span class="phase improve">Improve</span></td><td>Implement solutions</td><td>ROI Calculator, RACI</td></tr>
            <tr><td><span class="phase control">Control</span></td><td>Sustain improvements</td><td>Control Charts (I-Chart, I-MR)</td></tr>
        </table>
        
        <h2>Tips for Effective Analysis</h2>
        <div class="tip">
        <strong>1. Start with the 4-Up Chart</strong> — It provides a comprehensive initial view of your data's distribution, normality, stability, and natural spread.
        </div>
        <div class="tip">
        <strong>2. Check stability before capability</strong> — A process must be stable (in control) before capability indices are meaningful.
        </div>
        <div class="tip">
        <strong>3. Verify normality assumptions</strong> — Many statistical tests assume normal data. Use the Probability Plot to verify.
        </div>
        <div class="tip">
        <strong>4. Use appropriate sample sizes</strong> — For control charts, aim for 20+ data points. For capability, 30+ is recommended.
        </div>
        
        <hr>
        <p style="text-align: center; color: #666;">
        <strong>CiviQual v1.0.0</strong><br>
        © 2026 A Step in the Right Direction LLC<br>
        www.qualityincourts.com
        </p>
        
        </body>
        </html>
        """
    
    def _show_license(self):
        """Show license dialog."""
        dialog = LicenseDialog(self)
        dialog.dont_show_checkbox.hide()  # Hide checkbox when viewing
        dialog.exec()
    
    def _show_about(self):
        """Show about dialog."""
        dialog = AboutDialog(self)
        dialog.exec()


# =============================================================================
# Main Entry Point
# =============================================================================
def main():
    """Main entry point."""
    global DARK_MODE
    
    app = QApplication(sys.argv)
    app.setApplicationName("CiviQual")
    app.setOrganizationName("A Step in the Right Direction LLC")
    app.setApplicationVersion(VERSION)
    
    # Detect and apply system theme
    DARK_MODE = is_dark_mode()
    if DARK_MODE:
        app.setPalette(create_dark_palette())
        # Set fusion style for better dark mode support
        app.setStyle("Fusion")
    else:
        app.setPalette(create_light_palette())
    
    # Set application font
    font = QFont("Arial", 10)
    app.setFont(font)
    
    # Check license acceptance
    config = load_config()
    
    if config.get("show_license_dialog", True):
        license_dialog = LicenseDialog()
        result = license_dialog.exec()
        
        if not license_dialog.accepted_license:
            sys.exit(0)
        
        config["license_accepted"] = True
        if license_dialog.dont_show_again:
            config["show_license_dialog"] = False
        save_config(config)
    
    # Show splash screen
    splash = SplashScreen()
    splash.show()
    app.processEvents()
    
    # Create main window while splash is showing
    window = MainWindow()
    
    # Close splash and show main window after delay
    def show_main():
        splash.close()
        window.show()
    
    QTimer.singleShot(2500, show_main)  # 2.5 second splash
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
