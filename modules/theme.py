"""
modules/theme.py

Dark blue + orange theme (Ash standard).
Applied app-wide via QApplication.setStyleSheet.
"""

from __future__ import annotations

from PyQt5 import QtWidgets

VIBRANT_ORANGE = "#FF7A00"
DARK_BG = "#050B1A"
DARK_PANEL = "#0B1020"
DARK_PANEL_2 = "#0E1630"
TEXT = "#F5F5F5"
MUTED = "#AAB3C5"
BORDER = "#1C2A55"
DANGER = "#FF4D4D"
OK = "#39D98A"


QSS = f"""
/* ---------- Base ---------- */
QWidget {{
    background-color: {DARK_BG};
    color: {TEXT};
    font-size: 13px;
}}

QMainWindow {{
    background-color: {DARK_BG};
}}

QLabel#AppTitle {{
    font-size: 22px;
    font-weight: 700;
    color: {TEXT};
}}
QLabel#AppSubtitle {{
    color: {MUTED};
    padding-bottom: 6px;
}}
QLabel#Footer {{
    color: {MUTED};
    font-size: 11px;
}}

/* ---------- Tabs ---------- */
/* ---------- Tabs ---------- */
QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 6px;
    background: {DARK_PANEL};
}}

/* Make tabs wider + stop text truncation */
QTabBar::tab {{
    background: {DARK_PANEL_2};
    color: {TEXT};
    padding: 12px 22px;              /* wider */
    min-width: 220px;                /* force wide tabs */
    border: 1px solid {BORDER};
    border-bottom: none;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    margin-right: 6px;
}}
QTabBar::tab:selected {{
    background: {DARK_PANEL};
    color: {VIBRANT_ORANGE};
    font-weight: 700;
}}
QTabBar::tab:hover {{
    border-color: {VIBRANT_ORANGE};
}}


/* ---------- GroupBoxes ---------- */
QGroupBox {{
    border: 1px solid {BORDER};
    border-radius: 10px;
    margin-top: 12px;
    padding: 10px;
    background: {DARK_PANEL};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    color: {VIBRANT_ORANGE};
    font-weight: 700;
}}

/* ---------- Inputs ---------- */
QLineEdit, QPlainTextEdit, QTextEdit {{
    background: {DARK_PANEL_2};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 8px;
    selection-background-color: {VIBRANT_ORANGE};
    selection-color: {DARK_BG};
}}
QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus {{
    border-color: {VIBRANT_ORANGE};
}}

QComboBox {{
    background: {DARK_PANEL_2};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 8px;
}}
QComboBox:focus {{
    border-color: {VIBRANT_ORANGE};
}}
QComboBox QAbstractItemView {{
    background: {DARK_PANEL};
    border: 1px solid {BORDER};
    selection-background-color: {VIBRANT_ORANGE};
    selection-color: {DARK_BG};
}}

QSpinBox, QDoubleSpinBox {{
    background: {DARK_PANEL_2};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 6px;
}}
QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {VIBRANT_ORANGE};
}}

QCheckBox {{
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid {BORDER};
    background: {DARK_PANEL_2};
}}
QCheckBox::indicator:checked {{
    background: {VIBRANT_ORANGE};
    border-color: {VIBRANT_ORANGE};
}}

QSlider::groove:horizontal {{
    background: {DARK_PANEL_2};
    border: 1px solid {BORDER};
    height: 8px;
    border-radius: 4px;
}}
QSlider::handle:horizontal {{
    background: {VIBRANT_ORANGE};
    width: 18px;
    margin: -6px 0;
    border-radius: 9px;
}}

/* ---------- Buttons ---------- */
QPushButton {{
    background: {VIBRANT_ORANGE};
    color: {DARK_BG};
    border: none;
    border-radius: 10px;
    padding: 10px 14px;
    font-weight: 700;
}}
QPushButton:hover {{
    background: #FF8A1A;
}}
QPushButton:pressed {{
    background: #E86E00;
}}
QPushButton:disabled {{
    background: #6A3B14;
    color: #2A1607;
}}

QPushButton#SecondaryButton {{
    background: {DARK_PANEL_2};
    color: {TEXT};
    border: 1px solid {BORDER};
}}
QPushButton#SecondaryButton:hover {{
    border-color: {VIBRANT_ORANGE};
    color: {VIBRANT_ORANGE};
}}
QPushButton#DangerButton {{
    background: {DANGER};
    color: {DARK_BG};
}}

/* ---------- Tables/Lists ---------- */
QTableWidget {{
    background: {DARK_PANEL};
    border: 1px solid {BORDER};
    border-radius: 10px;
    gridline-color: {BORDER};
}}
QHeaderView::section {{
    background: {DARK_PANEL_2};
    color: {TEXT};
    padding: 8px;
    border: 1px solid {BORDER};
    font-weight: 700;
}}
QTableWidget::item:selected {{
    background: {VIBRANT_ORANGE};
    color: {DARK_BG};
}}

QListWidget {{
    background: {DARK_PANEL};
    border: 1px solid {BORDER};
    border-radius: 10px;
}}
QListWidget::item:selected {{
    background: {VIBRANT_ORANGE};
    color: {DARK_BG};
}}

/* ---------- Progress ---------- */
QProgressBar {{
    border: 1px solid {BORDER};
    border-radius: 10px;
    background: {DARK_PANEL_2};
    text-align: center;
}}
QProgressBar::chunk {{
    background: {VIBRANT_ORANGE};
    border-radius: 10px;
}}

/* ---------- Scrollbars ---------- */
QScrollBar:vertical {{
    background: {DARK_PANEL};
    width: 12px;
    margin: 0px;
    border-radius: 6px;
}}
QScrollBar::handle:vertical {{
    background: {VIBRANT_ORANGE};
    min-height: 20px;
    border-radius: 6px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QLabel#TaglineMain {{
    font-size: 14px;
    font-weight: 600;
    color: #E6E6E6;
    padding-top: 2px;
}}

QLabel#TaglineSub {{
    font-size: 11px;
    color: #AAB3C5;
    padding-bottom: 8px;
}}
"""




def apply_dark_blue_orange_theme(app: QtWidgets.QApplication) -> None:
    app.setStyleSheet(QSS)
