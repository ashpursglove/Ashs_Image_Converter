"""
modules/workers.py

Threading utilities for non-blocking UI.

Uses:
- QThreadPool + QRunnable (simple, scalable for batch jobs)
- WorkerSignals for progress and results
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional

from PyQt5 import QtCore

from .image_ops import ConvertResult, ConvertSettings, convert_one, build_multisize_ico


class WorkerSignals(QtCore.QObject):
    progress = QtCore.pyqtSignal(int, int)  # done, total
    message = QtCore.pyqtSignal(str)
    result = QtCore.pyqtSignal(object)  # ConvertResult or Path
    finished = QtCore.pyqtSignal()
    failed = QtCore.pyqtSignal(str)


class ConvertBatchWorker(QtCore.QRunnable):
    """
    Converts a list of images using ConvertSettings, emits results per file.
    """
    def __init__(self, files: List[Path], settings: ConvertSettings) -> None:
        super().__init__()
        self.files = files
        self.settings = settings
        self.signals = WorkerSignals()
        self.setAutoDelete(True)

    @QtCore.pyqtSlot()
    def run(self) -> None:
        try:
            total = len(self.files)
            done = 0
            for p in self.files:
                res = convert_one(p, self.settings)
                self.signals.result.emit(res)
                done += 1
                self.signals.progress.emit(done, total)
            self.signals.finished.emit()
        except Exception as e:
            self.signals.failed.emit(str(e))


class IcoWorker(QtCore.QRunnable):
    """
    Builds a single multi-size ICO.
    """
    def __init__(self, src: Path, dst: Path, sizes: List[int], autorotate_exif: bool, strip_metadata: bool) -> None:
        super().__init__()
        self.src = src
        self.dst = dst
        self.sizes = sizes
        self.autorotate_exif = autorotate_exif
        self.strip_metadata = strip_metadata
        self.signals = WorkerSignals()
        self.setAutoDelete(True)

    @QtCore.pyqtSlot()
    def run(self) -> None:
        try:
            self.signals.message.emit("Building ICO...")
            build_multisize_ico(self.src, self.dst, self.sizes, self.autorotate_exif, self.strip_metadata)
            self.signals.result.emit(self.dst)
            self.signals.finished.emit()
        except Exception as e:
            self.signals.failed.emit(str(e))
