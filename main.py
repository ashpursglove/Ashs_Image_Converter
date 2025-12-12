"""
main.py

Ash’s Image Converter
- Batch convert images between formats
- Optional resize with multiple modes
- Multi-size ICO generator (PyInstaller friendly)
- Drag & drop
- Preview
- Non-blocking UI (worker threads)

Run:
    pip install -r requirements.txt
    python main.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets

from modules.theme import apply_dark_blue_orange_theme
from modules.tabs.convert_tab import ConvertTab
from modules.tabs.ico_tab import IcoTab


APP_NAME = "Ash’s Image Converter"


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1200, 760)

        # Central layout
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        root = QtWidgets.QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        title = QtWidgets.QLabel(APP_NAME)
        title.setObjectName("AppTitle")
        # subtitle = QtWidgets.QLabel("Convert. Resize. ICO. Done. No wizard robes required.")
        # subtitle.setObjectName("AppSubtitle")

        tagline_main = QtWidgets.QLabel(
            '<span style="color:#FF7A00; font-weight:600;">No </span> subscriptions. <span style="color:#FF7A00; font-weight:600;">No </span>  logins. <span style="color:#FF7A00; font-weight:600;">No </span>  cloud. <span style="color:#FF7A00; font-weight:600;">No </span>  account.'
        )
        tagline_main.setObjectName("TaglineMain")

        # tagline_sub = QtWidgets.QLabel(
        #     "Because 4GB installers for resizing a PNG are unhinged... Fuck you Adobe."
        # )


        tagline_sub = QtWidgets.QLabel(
            'Because 4GB installers for resizing a PNG are unhinged... '
            '<span style="color:#FF7A00; font-weight:600;">Fuck you, Adobe.</span>'
        )
        tagline_sub.setObjectName("TaglineSub")



        # root.addWidget(title)
        # root.addWidget(subtitle)

        root.addWidget(title)
        root.addWidget(tagline_main)
        root.addWidget(tagline_sub)


        tabs = QtWidgets.QTabWidget()
        tabs.setObjectName("MainTabs")
        tabs.addTab(ConvertTab(), "Convert + Resize")
        tabs.addTab(IcoTab(), "ICO Generator")

        root.addWidget(tabs, 1)

        footer = QtWidgets.QLabel("Local-only tool. No cloud. No spying. No nonsense.")
        footer.setObjectName("Footer")
        footer.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        root.addWidget(footer)


def _set_windows_app_id() -> None:
    """
    Sets a stable Windows AppUserModelID so taskbar grouping works nicely.
    Safe no-op on non-Windows.
    """
    try:
        import ctypes  # type: ignore
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Ash.ImageConverter")
    except Exception:
        pass


def main() -> None:
    _set_windows_app_id()
    app = QtWidgets.QApplication(sys.argv)
    apply_dark_blue_orange_theme(app)

    # Slightly nicer font default
    font = QtGui.QFont("Segoe UI", 10)
    app.setFont(font)

    win = MainWindow()
    win.showMaximized()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
