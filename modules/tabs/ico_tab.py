# """
# modules/tabs/ico_tab.py

# Tab 2: ICO Generator
# - Pick a source image (ideally PNG with transparency)
# - Select sizes (defaults: 16,24,32,48,64,128,256)
# - Preview panel showing the icon at selected sizes
# - Non-blocking generation worker
# """

# from __future__ import annotations

# import os
# from pathlib import Path
# from typing import List, Optional

# from PyQt5 import QtCore, QtGui, QtWidgets

# from ..workers import IcoWorker
# from ..widgets import ImagePreviewLabel


# DEFAULT_SIZES = [16, 24, 32, 48, 64, 128, 256]


# class IcoTab(QtWidgets.QWidget):
#     def __init__(self) -> None:
#         super().__init__()
#         self.thread_pool = QtCore.QThreadPool.globalInstance()

#         self.src_path: Optional[Path] = None

#         self._build_ui()
#         self._wire()
#         self._apply_defaults()

#     def _build_ui(self) -> None:
#         root = QtWidgets.QHBoxLayout(self)
#         root.setContentsMargins(0, 0, 0, 0)
#         root.setSpacing(12)

#         # Left controls
#         left = QtWidgets.QVBoxLayout()
#         left.setSpacing(10)

#         pick = QtWidgets.QGroupBox("Input")
#         pg = QtWidgets.QGridLayout(pick)
#         pg.setHorizontalSpacing(10)
#         pg.setVerticalSpacing(10)

#         self.txt_in = QtWidgets.QLineEdit()
#         self.txt_in.setPlaceholderText("Pick an image (PNG recommended)...")
#         self.btn_in = QtWidgets.QPushButton("Browse")
#         self.btn_in.setObjectName("SecondaryButton")

#         self.chk_autorotate = QtWidgets.QCheckBox("Auto-rotate using EXIF orientation")
#         self.chk_autorotate.setChecked(True)

#         self.chk_strip = QtWidgets.QCheckBox("Strip metadata (EXIF)")
#         self.chk_strip.setChecked(False)

#         pg.addWidget(QtWidgets.QLabel("Input image"), 0, 0)
#         pg.addWidget(self.txt_in, 0, 1)
#         pg.addWidget(self.btn_in, 0, 2)
#         pg.addWidget(self.chk_autorotate, 1, 1, 1, 2)
#         pg.addWidget(self.chk_strip, 2, 1, 1, 2)

#         sizes_box = QtWidgets.QGroupBox("Icon Sizes")
#         sv = QtWidgets.QVBoxLayout(sizes_box)

#         self.size_checks: List[QtWidgets.QCheckBox] = []
#         wrap = QtWidgets.QGridLayout()
#         wrap.setHorizontalSpacing(10)
#         wrap.setVerticalSpacing(8)

#         for i, s in enumerate(DEFAULT_SIZES):
#             chk = QtWidgets.QCheckBox(f"{s}x{s}")
#             self.size_checks.append(chk)
#             wrap.addWidget(chk, i // 3, i % 3)

#         self.btn_default = QtWidgets.QPushButton("Select default sizes")
#         self.btn_default.setObjectName("SecondaryButton")
#         self.btn_all = QtWidgets.QPushButton("Select all")
#         self.btn_all.setObjectName("SecondaryButton")
#         self.btn_none = QtWidgets.QPushButton("Select none")
#         self.btn_none.setObjectName("SecondaryButton")

#         btns = QtWidgets.QHBoxLayout()
#         btns.addWidget(self.btn_default)
#         btns.addWidget(self.btn_all)
#         btns.addWidget(self.btn_none)

#         sv.addLayout(wrap)
#         sv.addLayout(btns)

#         out = QtWidgets.QGroupBox("Output")
#         og = QtWidgets.QGridLayout(out)
#         og.setHorizontalSpacing(10)
#         og.setVerticalSpacing(10)

#         self.txt_outdir = QtWidgets.QLineEdit()
#         self.txt_outdir.setPlaceholderText("Choose output folder...")
#         self.btn_outdir = QtWidgets.QPushButton("Browse")
#         self.btn_outdir.setObjectName("SecondaryButton")

#         self.txt_name = QtWidgets.QLineEdit()
#         self.txt_name.setText("app_icon.ico")

#         og.addWidget(QtWidgets.QLabel("Output folder"), 0, 0)
#         og.addWidget(self.txt_outdir, 0, 1)
#         og.addWidget(self.btn_outdir, 0, 2)
#         og.addWidget(QtWidgets.QLabel("ICO filename"), 1, 0)
#         og.addWidget(self.txt_name, 1, 1, 1, 2)

#         run_row = QtWidgets.QHBoxLayout()
#         self.btn_make = QtWidgets.QPushButton("Generate ICO")
#         self.progress = QtWidgets.QProgressBar()
#         self.progress.setRange(0, 100)
#         self.progress.setValue(0)
#         run_row.addWidget(self.btn_make)
#         run_row.addWidget(self.progress, 1)

#         self.log = QtWidgets.QPlainTextEdit()
#         self.log.setReadOnly(True)
#         self.log.setPlaceholderText("Logs appear here. No judgement. Some judgement.")

#         left.addWidget(pick)
#         left.addWidget(sizes_box)
#         left.addWidget(out)
#         left.addLayout(run_row)
#         left.addWidget(self.log, 1)

#         # Right preview
#         right = QtWidgets.QVBoxLayout()
#         right.setSpacing(10)

#         prev = QtWidgets.QGroupBox("Multi-size Preview")
#         pv = QtWidgets.QVBoxLayout(prev)
#         pv.setSpacing(10)

#         self.preview_big = ImagePreviewLabel()
#         self.preview_big.setMinimumSize(320, 320)

#         # Row of small previews
#         self.preview_row = QtWidgets.QHBoxLayout()
#         self.preview_row.setSpacing(10)
#         self.small_previews: List[ImagePreviewLabel] = []
#         for _ in range(5):
#             lab = ImagePreviewLabel()
#             lab.setMinimumSize(90, 90)
#             self.small_previews.append(lab)
#             self.preview_row.addWidget(lab)

#         self.lbl_hint = QtWidgets.QLabel(
#             "Tip: Use a square PNG with transparency. ICO will embed multiple sizes for Windows.\n"
#             "Yes, this is the part where your icon stops looking like a sad postage stamp."
#         )
#         self.lbl_hint.setWordWrap(True)

#         pv.addWidget(self.preview_big, 1)
#         pv.addLayout(self.preview_row)
#         pv.addWidget(self.lbl_hint)

#         right.addWidget(prev, 1)

#         root.addLayout(left, 3)
#         root.addLayout(right, 2)

#     def _wire(self) -> None:
#         self.btn_in.clicked.connect(self._pick_input)
#         self.btn_outdir.clicked.connect(self._pick_outdir)

#         self.btn_default.clicked.connect(self._apply_defaults)
#         self.btn_all.clicked.connect(self._select_all)
#         self.btn_none.clicked.connect(self._select_none)

#         for chk in self.size_checks:
#             chk.toggled.connect(self._update_previews)

#         self.txt_in.textChanged.connect(self._on_input_text_changed)
#         self.chk_autorotate.toggled.connect(self._update_previews)
#         self.chk_strip.toggled.connect(self._update_previews)

#         self.btn_make.clicked.connect(self._start_ico)

#     def _apply_defaults(self) -> None:
#         for chk in self.size_checks:
#             chk.setChecked(True)
#         self._update_previews()

#     def _select_all(self) -> None:
#         for chk in self.size_checks:
#             chk.setChecked(True)

#     def _select_none(self) -> None:
#         for chk in self.size_checks:
#             chk.setChecked(False)

#     def _pick_input(self) -> None:
#         f, _ = QtWidgets.QFileDialog.getOpenFileName(
#             self,
#             "Select source image",
#             "",
#             "Images (*.png *.jpg *.jpeg *.webp *.bmp *.tif *.tiff *.gif)",
#         )
#         if f:
#             self.txt_in.setText(f)

#     def _pick_outdir(self) -> None:
#         d = QtWidgets.QFileDialog.getExistingDirectory(self, "Select output folder")
#         if d:
#             self.txt_outdir.setText(d)

#     def _on_input_text_changed(self, t: str) -> None:
#         p = Path(t) if t.strip() else None
#         if p and p.exists() and p.is_file():
#             self.src_path = p
#         else:
#             self.src_path = None
#         self._update_previews()

#     def _selected_sizes(self) -> List[int]:
#         out: List[int] = []
#         for chk in self.size_checks:
#             if chk.isChecked():
#                 # "16x16" -> 16
#                 s = int(chk.text().split("x")[0])
#                 out.append(s)
#         return sorted(set(out))

#     def _update_previews(self) -> None:
#         """
#         Builds quick previews for a few sizes.
#         Does not save anything, just shows how the icon will look.
#         """
#         if not self.src_path:
#             self.preview_big.set_pixmap(None)
#             for p in self.small_previews:
#                 p.set_pixmap(None)
#             return

#         try:
#             from PIL import Image, ImageOps

#             img = Image.open(str(self.src_path))
#             if self.chk_autorotate.isChecked():
#                 img = ImageOps.exif_transpose(img)

#             img = img.convert("RGBA")

#             # Big preview is 256 if possible, else nearest
#             sizes = self._selected_sizes() or DEFAULT_SIZES
#             big = 256 if 256 in sizes else max(sizes)

#             big_img = img.resize((big, big), Image.LANCZOS)
#             self.preview_big.set_pixmap(self._pil_to_pixmap(big_img))

#             # Small previews: show first 5 selected sizes (or defaults)
#             show_sizes = (sizes[:5] if sizes else DEFAULT_SIZES[:5])
#             for lab, s in zip(self.small_previews, show_sizes):
#                 small = img.resize((s, s), Image.LANCZOS)
#                 lab.set_pixmap(self._pil_to_pixmap(small))

#         except Exception:
#             self.preview_big.set_pixmap(None)
#             for p in self.small_previews:
#                 p.set_pixmap(None)

#     def _pil_to_pixmap(self, img: "Image.Image") -> QtGui.QPixmap:
#         data = img.tobytes("raw", "RGBA")
#         qimg = QtGui.QImage(data, img.size[0], img.size[1], QtGui.QImage.Format_RGBA8888)
#         return QtGui.QPixmap.fromImage(qimg)

#     def _start_ico(self) -> None:
#         if not self.src_path:
#             self._log("Pick an input image first.")
#             return

#         outdir_txt = self.txt_outdir.text().strip()
#         if not outdir_txt:
#             self._log("Pick an output folder first.")
#             return

#         sizes = self._selected_sizes()
#         if not sizes:
#             self._log("Select at least one size. A 0x0 icon is not a flex.")
#             return

#         name = self.txt_name.text().strip()
#         if not name.lower().endswith(".ico"):
#             name += ".ico"

#         dst = Path(outdir_txt) / name

#         self.progress.setValue(0)
#         self.btn_make.setEnabled(False)
#         self._log(f"Generating ICO -> {dst.name} (sizes: {sizes})")

#         worker = IcoWorker(
#             src=self.src_path,
#             dst=dst,
#             sizes=sizes,
#             autorotate_exif=self.chk_autorotate.isChecked(),
#             strip_metadata=self.chk_strip.isChecked(),
#         )
#         worker.signals.message.connect(self._log)
#         worker.signals.result.connect(self._on_done)
#         worker.signals.finished.connect(self._on_finished)
#         worker.signals.failed.connect(self._on_failed)

#         self.thread_pool.start(worker)

#         # Fake progress: ICO build is usually fast, but give UI feedback
#         self.progress.setValue(35)

#     def _on_done(self, obj: object) -> None:
#         try:
#             p = obj
#             if isinstance(p, Path):
#                 self._log(f"ICO created: {p}")
#         except Exception:
#             pass

#     def _on_finished(self) -> None:
#         self.btn_make.setEnabled(True)
#         self.progress.setValue(100)
#         self._log("Done. Your icon is now a proper Windows multi-size creature.")

#         # Auto-open output folder on Windows for convenience (non-blocking)
#         outdir_txt = self.txt_outdir.text().strip()
#         if outdir_txt:
#             try:
#                 if os.name == "nt":
#                     os.startfile(outdir_txt)  # type: ignore[attr-defined]
#             except Exception:
#                 pass

#     def _on_failed(self, msg: str) -> None:
#         self.btn_make.setEnabled(True)
#         self.progress.setValue(0)
#         self._log(f"Failed: {msg}")

#     def _log(self, s: str) -> None:
#         self.log.appendPlainText(s)


























"""
modules/tabs/ico_tab.py

Scrollable ICO Generator tab.
Wrapped in QScrollArea so it never bunches/overlaps.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

from PyQt5 import QtCore, QtGui, QtWidgets

from ..workers import IcoWorker
from ..widgets import ImagePreviewLabel

DEFAULT_SIZES = [16, 24, 32, 48, 64, 128, 256]


class IcoTab(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.thread_pool = QtCore.QThreadPool.globalInstance()
        self.src_path: Optional[Path] = None

        # Root: scroll area wrapper
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.content = QtWidgets.QWidget()
        self.scroll.setWidget(self.content)

        outer.addWidget(self.scroll)

        self._build_ui(self.content)
        self._wire()
        self._apply_defaults()

    def _build_ui(self, parent: QtWidgets.QWidget) -> None:
        root = QtWidgets.QHBoxLayout(parent)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        left = QtWidgets.QVBoxLayout()
        left.setSpacing(10)

        pick = QtWidgets.QGroupBox("Input")
        pg = QtWidgets.QGridLayout(pick)
        pg.setHorizontalSpacing(10)
        pg.setVerticalSpacing(10)

        self.txt_in = QtWidgets.QLineEdit()
        self.txt_in.setPlaceholderText("Pick an image (PNG recommended)...")
        self.btn_in = QtWidgets.QPushButton("Browse")
        self.btn_in.setObjectName("SecondaryButton")

        self.chk_autorotate = QtWidgets.QCheckBox("Auto-rotate using EXIF orientation")
        self.chk_autorotate.setChecked(True)

        self.chk_strip = QtWidgets.QCheckBox("Strip metadata (EXIF)")
        self.chk_strip.setChecked(False)

        pg.addWidget(QtWidgets.QLabel("Input image"), 0, 0)
        pg.addWidget(self.txt_in, 0, 1)
        pg.addWidget(self.btn_in, 0, 2)
        pg.addWidget(self.chk_autorotate, 1, 1, 1, 2)
        pg.addWidget(self.chk_strip, 2, 1, 1, 2)

        sizes_box = QtWidgets.QGroupBox("Icon Sizes")
        sv = QtWidgets.QVBoxLayout(sizes_box)

        self.size_checks: List[QtWidgets.QCheckBox] = []
        wrap = QtWidgets.QGridLayout()
        wrap.setHorizontalSpacing(10)
        wrap.setVerticalSpacing(8)

        for i, s in enumerate(DEFAULT_SIZES):
            chk = QtWidgets.QCheckBox(f"{s}x{s}")
            self.size_checks.append(chk)
            wrap.addWidget(chk, i // 3, i % 3)

        self.btn_default = QtWidgets.QPushButton("Select default sizes")
        self.btn_default.setObjectName("SecondaryButton")
        self.btn_all = QtWidgets.QPushButton("Select all")
        self.btn_all.setObjectName("SecondaryButton")
        self.btn_none = QtWidgets.QPushButton("Select none")
        self.btn_none.setObjectName("SecondaryButton")

        btns = QtWidgets.QHBoxLayout()
        btns.addWidget(self.btn_default)
        btns.addWidget(self.btn_all)
        btns.addWidget(self.btn_none)

        sv.addLayout(wrap)
        sv.addLayout(btns)

        out = QtWidgets.QGroupBox("Output")
        og = QtWidgets.QGridLayout(out)
        og.setHorizontalSpacing(10)
        og.setVerticalSpacing(10)

        self.txt_outdir = QtWidgets.QLineEdit()
        self.txt_outdir.setPlaceholderText("Choose output folder...")
        self.btn_outdir = QtWidgets.QPushButton("Browse")
        self.btn_outdir.setObjectName("SecondaryButton")

        self.txt_name = QtWidgets.QLineEdit()
        self.txt_name.setText("app_icon.ico")

        og.addWidget(QtWidgets.QLabel("Output folder"), 0, 0)
        og.addWidget(self.txt_outdir, 0, 1)
        og.addWidget(self.btn_outdir, 0, 2)
        og.addWidget(QtWidgets.QLabel("ICO filename"), 1, 0)
        og.addWidget(self.txt_name, 1, 1, 1, 2)

        run_row = QtWidgets.QHBoxLayout()
        self.btn_make = QtWidgets.QPushButton("Generate ICO")
        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        run_row.addWidget(self.btn_make)
        run_row.addWidget(self.progress, 1)

        self.log = QtWidgets.QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Logs appear here.")

        left.addWidget(pick)
        left.addWidget(sizes_box)
        left.addWidget(out)
        left.addLayout(run_row)
        left.addWidget(self.log, 1)

        # Right preview
        right = QtWidgets.QVBoxLayout()
        right.setSpacing(10)

        prev = QtWidgets.QGroupBox("Multi-size Preview")
        pv = QtWidgets.QVBoxLayout(prev)
        pv.setSpacing(10)

        self.preview_big = ImagePreviewLabel()
        self.preview_big.setMinimumSize(320, 320)

        self.preview_row = QtWidgets.QHBoxLayout()
        self.preview_row.setSpacing(10)
        self.small_previews: List[ImagePreviewLabel] = []
        for _ in range(5):
            lab = ImagePreviewLabel()
            lab.setMinimumSize(90, 90)
            self.small_previews.append(lab)
            self.preview_row.addWidget(lab)

        self.lbl_hint = QtWidgets.QLabel(
            "Tip: Use a square PNG with transparency.\n"
            "Windows gets a proper multi-size ICO. Your taskbar icon stops crying."
        )
        self.lbl_hint.setWordWrap(True)

        pv.addWidget(self.preview_big, 1)
        pv.addLayout(self.preview_row)
        pv.addWidget(self.lbl_hint)

        right.addWidget(prev, 1)

        root.addLayout(left, 3)
        root.addLayout(right, 2)

    def _wire(self) -> None:
        self.btn_in.clicked.connect(self._pick_input)
        self.btn_outdir.clicked.connect(self._pick_outdir)

        self.btn_default.clicked.connect(self._apply_defaults)
        self.btn_all.clicked.connect(self._select_all)
        self.btn_none.clicked.connect(self._select_none)

        for chk in self.size_checks:
            chk.toggled.connect(self._update_previews)

        self.txt_in.textChanged.connect(self._on_input_text_changed)
        self.chk_autorotate.toggled.connect(self._update_previews)
        self.chk_strip.toggled.connect(self._update_previews)

        self.btn_make.clicked.connect(self._start_ico)

    def _apply_defaults(self) -> None:
        for chk in self.size_checks:
            chk.setChecked(True)
        self._update_previews()

    def _select_all(self) -> None:
        for chk in self.size_checks:
            chk.setChecked(True)

    def _select_none(self) -> None:
        for chk in self.size_checks:
            chk.setChecked(False)

    def _pick_input(self) -> None:
        f, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select source image",
            "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp *.tif *.tiff *.gif)",
        )
        if f:
            self.txt_in.setText(f)

    def _pick_outdir(self) -> None:
        d = QtWidgets.QFileDialog.getExistingDirectory(self, "Select output folder")
        if d:
            self.txt_outdir.setText(d)

    def _on_input_text_changed(self, t: str) -> None:
        p = Path(t) if t.strip() else None
        self.src_path = p if p and p.exists() and p.is_file() else None
        self._update_previews()

    def _selected_sizes(self) -> List[int]:
        out: List[int] = []
        for chk in self.size_checks:
            if chk.isChecked():
                out.append(int(chk.text().split("x")[0]))
        return sorted(set(out))

    def _update_previews(self) -> None:
        if not self.src_path:
            self.preview_big.set_pixmap(None)
            for p in self.small_previews:
                p.set_pixmap(None)
            return

        try:
            from PIL import Image, ImageOps
            img = Image.open(str(self.src_path))
            if self.chk_autorotate.isChecked():
                img = ImageOps.exif_transpose(img)
            img = img.convert("RGBA")

            sizes = self._selected_sizes() or DEFAULT_SIZES
            big = 256 if 256 in sizes else max(sizes)

            big_img = img.resize((big, big), Image.LANCZOS)
            self.preview_big.set_pixmap(self._pil_to_pixmap(big_img))

            show_sizes = sizes[:5] if sizes else DEFAULT_SIZES[:5]
            for lab, s in zip(self.small_previews, show_sizes):
                small = img.resize((s, s), Image.LANCZOS)
                lab.set_pixmap(self._pil_to_pixmap(small))
        except Exception:
            self.preview_big.set_pixmap(None)
            for p in self.small_previews:
                p.set_pixmap(None)

    def _pil_to_pixmap(self, img: "Image.Image") -> QtGui.QPixmap:
        data = img.tobytes("raw", "RGBA")
        qimg = QtGui.QImage(data, img.size[0], img.size[1], QtGui.QImage.Format_RGBA8888)
        return QtGui.QPixmap.fromImage(qimg)

    def _start_ico(self) -> None:
        if not self.src_path:
            self._log("Pick an input image first.")
            return

        outdir_txt = self.txt_outdir.text().strip()
        if not outdir_txt:
            self._log("Pick an output folder first.")
            return

        sizes = self._selected_sizes()
        if not sizes:
            self._log("Select at least one size.")
            return

        name = self.txt_name.text().strip()
        if not name.lower().endswith(".ico"):
            name += ".ico"

        dst = Path(outdir_txt) / name

        self.progress.setValue(0)
        self.btn_make.setEnabled(False)
        self._log(f"Generating ICO -> {dst.name} (sizes: {sizes})")

        worker = IcoWorker(
            src=self.src_path,
            dst=dst,
            sizes=sizes,
            autorotate_exif=self.chk_autorotate.isChecked(),
            strip_metadata=self.chk_strip.isChecked(),
        )
        worker.signals.message.connect(self._log)
        worker.signals.result.connect(self._on_done)
        worker.signals.finished.connect(self._on_finished)
        worker.signals.failed.connect(self._on_failed)

        self.thread_pool.start(worker)
        self.progress.setValue(35)

    def _on_done(self, obj: object) -> None:
        if isinstance(obj, Path):
            self._log(f"ICO created: {obj}")

    def _on_finished(self) -> None:
        self.btn_make.setEnabled(True)
        self.progress.setValue(100)
        self._log("Done.")

        outdir_txt = self.txt_outdir.text().strip()
        if outdir_txt:
            try:
                if os.name == "nt":
                    os.startfile(outdir_txt)  # type: ignore[attr-defined]
            except Exception:
                pass

    def _on_failed(self, msg: str) -> None:
        self.btn_make.setEnabled(True)
        self.progress.setValue(0)
        self._log(f"Failed: {msg}")

    def _log(self, s: str) -> None:
        self.log.appendPlainText(s)
