"""
modules/widgets.py

Small reusable widgets:
- DropTableWidget: QTableWidget with drag & drop file support.
- ImagePreviewLabel: aspect-aware preview label.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Iterable, List, Optional

from PyQt5 import QtCore, QtGui, QtWidgets


def _extract_paths_from_mime(mime: QtCore.QMimeData) -> List[Path]:
    paths: List[Path] = []
    if mime.hasUrls():
        for url in mime.urls():
            try:
                p = Path(url.toLocalFile())
                if p.exists():
                    paths.append(p)
            except Exception:
                continue
    return paths


class DropTableWidget(QtWidgets.QTableWidget):
    """
    A QTableWidget that accepts file drops.
    Calls on_files_dropped(paths) when files are dropped.
    """
    def __init__(self, on_files_dropped: Callable[[List[Path]], None], parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self._on_files_dropped = on_files_dropped
        self.setAcceptDrops(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DropOnly)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        paths = _extract_paths_from_mime(event.mimeData())
        if paths:
            self._on_files_dropped(paths)
            event.acceptProposedAction()
        else:
            event.ignore()


class ImagePreviewLabel(QtWidgets.QLabel):
    """
    Displays a pixmap scaled to fit while keeping aspect ratio.
    """
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(260, 260)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setText("No preview")
        self.setObjectName("PreviewLabel")
        self._pix: Optional[QtGui.QPixmap] = None

    def set_pixmap(self, pix: Optional[QtGui.QPixmap]) -> None:
        self._pix = pix
        self._refresh()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        self._refresh()

    def _refresh(self) -> None:
        if not self._pix or self._pix.isNull():
            self.setPixmap(QtGui.QPixmap())
            self.setText("No preview")
            return
        scaled = self._pix.scaled(self.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.setText("")
        self.setPixmap(scaled)
