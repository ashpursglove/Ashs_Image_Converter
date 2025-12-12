# """
# modules/tabs/convert_tab.py

# Tab 1: Convert + Resize
# - Drag/drop files
# - Batch table
# - Preview (before/after)
# - Output format, naming, output dir
# - Resize options
# - Quality slider for JPEG/WEBP
# - Metadata stripping, EXIF autorotate
# - Transparency flatten warning + background color
# - Non-blocking conversions via worker
# """

# from __future__ import annotations

# import os
# from dataclasses import replace
# from pathlib import Path
# from typing import Dict, List, Optional, Tuple

# from PyQt5 import QtCore, QtGui, QtWidgets

# from ..image_ops import (
#     ConvertResult,
#     ConvertSettings,
#     ResizeMode,
#     SUPPORTED_INPUT,
#     SUPPORTED_OUTPUT,
#     estimate_output_path,
#     is_supported_input,
# )
# from ..workers import ConvertBatchWorker
# from ..widgets import DropTableWidget, ImagePreviewLabel


# def _rgb_from_qcolor(c: QtGui.QColor) -> Tuple[int, int, int]:
#     return (c.red(), c.green(), c.blue())


# class ConvertTab(QtWidgets.QWidget):
#     COLS = ["Status", "File", "Format", "WxH", "Output Path", "Message"]

#     def __init__(self) -> None:
#         super().__init__()
#         self.thread_pool = QtCore.QThreadPool.globalInstance()

#         self.files: List[Path] = []
#         self._row_for_path: Dict[Path, int] = {}
#         self._current_preview_path: Optional[Path] = None

#         self._build_ui()
#         self._wire()
#         self._refresh_controls()

#     # ---------- UI ----------

#     def _build_ui(self) -> None:
#         root = QtWidgets.QHBoxLayout(self)
#         root.setContentsMargins(0, 0, 0, 0)
#         root.setSpacing(12)

#         # Left: table + controls
#         left = QtWidgets.QVBoxLayout()
#         left.setSpacing(10)

#         self.table = DropTableWidget(self._on_files_dropped)
#         self.table.setColumnCount(len(self.COLS))
#         self.table.setHorizontalHeaderLabels(self.COLS)
#         self.table.horizontalHeader().setStretchLastSection(True)
#         self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
#         self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
#         self.table.setAlternatingRowColors(False)
#         self.table.setSortingEnabled(False)
#         self.table.verticalHeader().setVisible(False)
#         self.table.setObjectName("FileTable")
#         self.table.setToolTip("Drag & drop images here. Yes, like it’s 2007 but cooler.")

#         btn_row = QtWidgets.QHBoxLayout()
#         self.btn_add = QtWidgets.QPushButton("Add Files")
#         self.btn_add.setObjectName("SecondaryButton")
#         self.btn_remove = QtWidgets.QPushButton("Remove Selected")
#         self.btn_remove.setObjectName("SecondaryButton")
#         self.btn_clear = QtWidgets.QPushButton("Clear")
#         self.btn_clear.setObjectName("DangerButton")
#         btn_row.addWidget(self.btn_add)
#         btn_row.addWidget(self.btn_remove)
#         btn_row.addWidget(self.btn_clear)
#         btn_row.addStretch(1)

#         left.addWidget(self.table, 1)
#         left.addLayout(btn_row)

#         # Settings group
#         settings = QtWidgets.QGroupBox("Output Settings")
#         sgrid = QtWidgets.QGridLayout(settings)
#         sgrid.setHorizontalSpacing(10)
#         sgrid.setVerticalSpacing(10)

#         self.cmb_format = QtWidgets.QComboBox()
#         self.cmb_format.addItems(sorted(SUPPORTED_OUTPUT))
#         self.cmb_format.setCurrentText("PNG")

#         self.txt_outdir = QtWidgets.QLineEdit()
#         self.txt_outdir.setPlaceholderText("Choose output folder...")
#         self.btn_outdir = QtWidgets.QPushButton("Browse")
#         self.btn_outdir.setObjectName("SecondaryButton")

#         self.cmb_naming = QtWidgets.QComboBox()
#         self.cmb_naming.addItems(["Keep original name", "Add prefix", "Add suffix"])
#         self.txt_name = QtWidgets.QLineEdit()
#         self.txt_name.setPlaceholderText("prefix_or_suffix")
#         self.chk_autonum = QtWidgets.QCheckBox("Auto-number if collisions happen")
#         self.chk_autonum.setChecked(True)

#         sgrid.addWidget(QtWidgets.QLabel("Output format"), 0, 0)
#         sgrid.addWidget(self.cmb_format, 0, 1)

#         sgrid.addWidget(QtWidgets.QLabel("Output folder"), 1, 0)
#         sgrid.addWidget(self.txt_outdir, 1, 1)
#         sgrid.addWidget(self.btn_outdir, 1, 2)

#         sgrid.addWidget(QtWidgets.QLabel("Naming"), 2, 0)
#         sgrid.addWidget(self.cmb_naming, 2, 1)
#         sgrid.addWidget(self.txt_name, 2, 2)

#         sgrid.addWidget(self.chk_autonum, 3, 1, 1, 2)

#         left.addWidget(settings)

#         # Resize group
#         resize_g = QtWidgets.QGroupBox("Resize (Optional)")
#         rgrid = QtWidgets.QGridLayout(resize_g)
#         rgrid.setHorizontalSpacing(10)
#         rgrid.setVerticalSpacing(10)

#         self.chk_resize = QtWidgets.QCheckBox("Resize enabled")
#         self.chk_resize.setChecked(False)

#         self.spin_w = QtWidgets.QSpinBox()
#         self.spin_w.setRange(1, 20000)
#         self.spin_w.setValue(1600)

#         self.spin_h = QtWidgets.QSpinBox()
#         self.spin_h.setRange(1, 20000)
#         self.spin_h.setValue(1600)

#         self.chk_aspect = QtWidgets.QCheckBox("Keep aspect ratio")
#         self.chk_aspect.setChecked(True)

#         self.cmb_resize_mode = QtWidgets.QComboBox()
#         self.cmb_resize_mode.addItems([ResizeMode.CONTAIN, ResizeMode.COVER, ResizeMode.STRETCH])

#         self.chk_no_upscale = QtWidgets.QCheckBox("Do not upscale")
#         self.chk_no_upscale.setChecked(True)

#         self.slider_quality = QtWidgets.QSlider(QtCore.Qt.Horizontal)
#         self.slider_quality.setRange(1, 100)
#         self.slider_quality.setValue(90)
#         self.lbl_quality = QtWidgets.QLabel("Quality: 90")

#         self.chk_optimize = QtWidgets.QCheckBox("Optimize output size (may be slower)")
#         self.chk_optimize.setChecked(True)

#         rgrid.addWidget(self.chk_resize, 0, 0, 1, 3)
#         rgrid.addWidget(QtWidgets.QLabel("Width"), 1, 0)
#         rgrid.addWidget(self.spin_w, 1, 1)
#         rgrid.addWidget(QtWidgets.QLabel("Height"), 2, 0)
#         rgrid.addWidget(self.spin_h, 2, 1)
#         rgrid.addWidget(self.chk_aspect, 1, 2)
#         rgrid.addWidget(QtWidgets.QLabel("Mode"), 3, 0)
#         rgrid.addWidget(self.cmb_resize_mode, 3, 1, 1, 2)
#         rgrid.addWidget(self.chk_no_upscale, 4, 0, 1, 3)
#         rgrid.addWidget(self.lbl_quality, 5, 0)
#         rgrid.addWidget(self.slider_quality, 5, 1, 1, 2)
#         rgrid.addWidget(self.chk_optimize, 6, 0, 1, 3)

#         left.addWidget(resize_g)

#         # Extras group
#         extras = QtWidgets.QGroupBox("Extras")
#         egrid = QtWidgets.QGridLayout(extras)
#         egrid.setHorizontalSpacing(10)
#         egrid.setVerticalSpacing(10)

#         self.chk_strip = QtWidgets.QCheckBox("Strip metadata (EXIF) for privacy + smaller files")
#         self.chk_strip.setChecked(False)

#         self.chk_autorotate = QtWidgets.QCheckBox("Auto-rotate using EXIF orientation")
#         self.chk_autorotate.setChecked(True)

#         self.lbl_flatten = QtWidgets.QLabel("Transparency handling (PNG -> JPG):")
#         self.cmb_flatten = QtWidgets.QComboBox()
#         self.cmb_flatten.addItems(["Flatten on BLACK", "Flatten on WHITE", "Pick custom color..."])
#         self._custom_flatten_color = QtGui.QColor(0, 0, 0)

#         egrid.addWidget(self.chk_strip, 0, 0, 1, 2)
#         egrid.addWidget(self.chk_autorotate, 1, 0, 1, 2)
#         egrid.addWidget(self.lbl_flatten, 2, 0)
#         egrid.addWidget(self.cmb_flatten, 2, 1)

#         left.addWidget(extras)

#         # Run controls
#         run_row = QtWidgets.QHBoxLayout()
#         self.btn_convert = QtWidgets.QPushButton("Convert")
#         self.progress = QtWidgets.QProgressBar()
#         self.progress.setRange(0, 100)
#         self.progress.setValue(0)
#         run_row.addWidget(self.btn_convert)
#         run_row.addWidget(self.progress, 1)

#         left.addLayout(run_row)

#         self.log = QtWidgets.QPlainTextEdit()
#         self.log.setReadOnly(True)
#         self.log.setPlaceholderText("Logs appear here. If something explodes, it will at least be documented.")

#         left.addWidget(self.log, 0)

#         # Right: preview panel
#         right = QtWidgets.QVBoxLayout()
#         right.setSpacing(10)

#         prev_box = QtWidgets.QGroupBox("Preview")
#         pv = QtWidgets.QVBoxLayout(prev_box)
#         pv.setSpacing(10)

#         self.preview_before = ImagePreviewLabel()
#         self.preview_after = ImagePreviewLabel()

#         self.lbl_summary = QtWidgets.QLabel("Select a file to preview.")
#         self.lbl_summary.setWordWrap(True)
#         self.lbl_summary.setObjectName("PreviewSummary")

#         # Clipboard helpers
#         tools = QtWidgets.QHBoxLayout()
#         self.btn_copy_outpath = QtWidgets.QPushButton("Copy output path")
#         self.btn_copy_outpath.setObjectName("SecondaryButton")
#         self.btn_open_outdir = QtWidgets.QPushButton("Open output folder")
#         self.btn_open_outdir.setObjectName("SecondaryButton")
#         tools.addWidget(self.btn_copy_outpath)
#         tools.addWidget(self.btn_open_outdir)

#         pv.addWidget(QtWidgets.QLabel("Before"))
#         pv.addWidget(self.preview_before, 1)
#         pv.addWidget(QtWidgets.QLabel("After (resize preview)"))
#         pv.addWidget(self.preview_after, 1)
#         pv.addWidget(self.lbl_summary)
#         pv.addLayout(tools)

#         right.addWidget(prev_box, 1)

#         root.addLayout(left, 3)
#         root.addLayout(right, 2)

#     # ---------- Wiring ----------

#     def _wire(self) -> None:
#         self.btn_add.clicked.connect(self._pick_files)
#         self.btn_remove.clicked.connect(self._remove_selected)
#         self.btn_clear.clicked.connect(self._clear_all)
#         self.btn_outdir.clicked.connect(self._pick_outdir)

#         self.cmb_format.currentTextChanged.connect(self._refresh_controls)
#         self.cmb_naming.currentIndexChanged.connect(self._refresh_controls)
#         self.txt_name.textChanged.connect(self._update_estimates)
#         self.txt_outdir.textChanged.connect(self._update_estimates)
#         self.chk_resize.toggled.connect(self._refresh_controls)
#         self.spin_w.valueChanged.connect(self._update_preview_after)
#         self.spin_h.valueChanged.connect(self._update_preview_after)
#         self.chk_aspect.toggled.connect(self._update_preview_after)
#         self.cmb_resize_mode.currentTextChanged.connect(self._update_preview_after)
#         self.chk_no_upscale.toggled.connect(self._update_preview_after)

#         self.slider_quality.valueChanged.connect(self._on_quality_changed)
#         self.chk_optimize.toggled.connect(self._update_estimates)

#         self.chk_strip.toggled.connect(self._update_preview_after)
#         self.chk_autorotate.toggled.connect(self._update_preview_after)

#         self.cmb_flatten.currentIndexChanged.connect(self._on_flatten_choice)

#         self.table.itemSelectionChanged.connect(self._on_selection_changed)

#         self.btn_convert.clicked.connect(self._start_convert)

#         self.btn_copy_outpath.clicked.connect(self._copy_selected_output_path)
#         self.btn_open_outdir.clicked.connect(self._open_output_folder)

#     # ---------- File ingest ----------

#     def _on_files_dropped(self, paths: List[Path]) -> None:
#         self._add_files(paths)

#     def _pick_files(self) -> None:
#         files, _ = QtWidgets.QFileDialog.getOpenFileNames(
#             self,
#             "Select images",
#             "",
#             "Images (*.png *.jpg *.jpeg *.webp *.bmp *.tif *.tiff *.gif)",
#         )
#         self._add_files([Path(f) for f in files])

#     def _add_files(self, paths: List[Path]) -> None:
#         # Expand folders into contained files
#         expanded: List[Path] = []
#         for p in paths:
#             if p.is_dir():
#                 for child in p.rglob("*"):
#                     if child.is_file() and is_supported_input(child):
#                         expanded.append(child)
#             else:
#                 expanded.append(p)

#         # Filter supported files only
#         new_files: List[Path] = []
#         for p in expanded:
#             if p.exists() and p.is_file() and is_supported_input(p):
#                 if p not in self.files:
#                     new_files.append(p)

#         if not new_files:
#             self._log("No valid images found in that drop/pick.")
#             return

#         for p in new_files:
#             self.files.append(p)
#             self._append_row(p)

#         self._log(f"Added {len(new_files)} file(s).")
#         self._update_estimates()

#         # Auto-select first added if nothing selected
#         if self.table.currentRow() < 0 and self.table.rowCount() > 0:
#             self.table.selectRow(0)

#     def _append_row(self, p: Path) -> None:
#         row = self.table.rowCount()
#         self.table.insertRow(row)
#         self._row_for_path[p] = row

#         # Status
#         self._set_item(row, 0, "Queued")
#         self._set_item(row, 1, p.name)
#         self._set_item(row, 2, p.suffix.lower().lstrip("."))
#         self._set_item(row, 3, self._read_dimensions_str(p))
#         self._set_item(row, 4, "")
#         self._set_item(row, 5, "")

#     def _read_dimensions_str(self, p: Path) -> str:
#         try:
#             from PIL import Image
#             img = Image.open(str(p))
#             w, h = img.size
#             return f"{w}x{h}"
#         except Exception:
#             return "?"

#     def _set_item(self, row: int, col: int, text: str) -> None:
#         item = QtWidgets.QTableWidgetItem(text)
#         self.table.setItem(row, col, item)

#     def _remove_selected(self) -> None:
#         rows = sorted({idx.row() for idx in self.table.selectionModel().selectedRows()}, reverse=True)
#         if not rows:
#             return

#         # Map rows back to paths
#         paths_by_row: Dict[int, Path] = {r: p for p, r in self._row_for_path.items()}
#         for r in rows:
#             p = paths_by_row.get(r)
#             if p and p in self.files:
#                 self.files.remove(p)
#                 self._row_for_path.pop(p, None)
#             self.table.removeRow(r)

#         # Rebuild row mapping
#         self._row_for_path = {}
#         for r in range(self.table.rowCount()):
#             name = self.table.item(r, 1).text()
#             # Find matching path by name (may collide, but good enough for UI rebuild)
#             for p in self.files:
#                 if p.name == name and p not in self._row_for_path:
#                     self._row_for_path[p] = r
#                     break

#         self._log(f"Removed {len(rows)} row(s).")
#         self._update_estimates()
#         self._clear_preview()

#     def _clear_all(self) -> None:
#         self.files.clear()
#         self._row_for_path.clear()
#         self.table.setRowCount(0)
#         self._log("Cleared everything. Fresh slate. No regrets.")
#         self._update_estimates()
#         self._clear_preview()

#     # ---------- Settings -> ConvertSettings ----------

#     def _get_flatten_color(self) -> Tuple[int, int, int]:
#         choice = self.cmb_flatten.currentText()
#         if "BLACK" in choice:
#             return (0, 0, 0)
#         if "WHITE" in choice:
#             return (255, 255, 255)
#         return _rgb_from_qcolor(self._custom_flatten_color)

#     def _build_settings(self) -> Optional[ConvertSettings]:
#         outdir = Path(self.txt_outdir.text().strip()) if self.txt_outdir.text().strip() else None
#         if not outdir:
#             return None

#         naming_index = self.cmb_naming.currentIndex()
#         name_mode = "keep"
#         if naming_index == 1:
#             name_mode = "prefix"
#         elif naming_index == 2:
#             name_mode = "suffix"

#         return ConvertSettings(
#             output_format=self.cmb_format.currentText(),
#             output_dir=outdir,
#             name_mode=name_mode,
#             name_text=self.txt_name.text(),
#             auto_number_collisions=self.chk_autonum.isChecked(),
#             resize_enabled=self.chk_resize.isChecked(),
#             width=int(self.spin_w.value()),
#             height=int(self.spin_h.value()),
#             keep_aspect=self.chk_aspect.isChecked(),
#             resize_mode=self.cmb_resize_mode.currentText(),
#             do_not_upscale=self.chk_no_upscale.isChecked(),
#             quality=int(self.slider_quality.value()),
#             optimize=self.chk_optimize.isChecked(),
#             strip_metadata=self.chk_strip.isChecked(),
#             autorotate_exif=self.chk_autorotate.isChecked(),
#             flatten_bg_rgb=self._get_flatten_color(),
#         )

#     # ---------- Preview ----------

#     def _on_selection_changed(self) -> None:
#         row = self.table.currentRow()
#         if row < 0:
#             return

#         # Find path for row
#         p = None
#         for path, r in self._row_for_path.items():
#             if r == row:
#                 p = path
#                 break
#         if not p:
#             return

#         self._current_preview_path = p
#         self._update_preview_before()
#         self._update_preview_after()
#         self._update_summary()

#     def _clear_preview(self) -> None:
#         self._current_preview_path = None
#         self.preview_before.set_pixmap(None)
#         self.preview_after.set_pixmap(None)
#         self.lbl_summary.setText("Select a file to preview.")

#     def _update_preview_before(self) -> None:
#         p = self._current_preview_path
#         if not p:
#             return
#         pix = QtGui.QPixmap(str(p))
#         self.preview_before.set_pixmap(pix if not pix.isNull() else None)

#     def _update_preview_after(self) -> None:
#         """
#         For "after" preview we do a lightweight PIL resize preview into a pixmap.
#         Not a full conversion save, just a visual sanity check.
#         """
#         p = self._current_preview_path
#         if not p:
#             return

#         try:
#             from PIL import Image, ImageOps
#             img = Image.open(str(p))
#             if self.chk_autorotate.isChecked():
#                 img = ImageOps.exif_transpose(img)

#             if self.chk_resize.isChecked():
#                 # Mirror the resize behavior at preview time
#                 w = int(self.spin_w.value())
#                 h = int(self.spin_h.value())
#                 keep = self.chk_aspect.isChecked()
#                 mode = self.cmb_resize_mode.currentText()
#                 no_up = self.chk_no_upscale.isChecked()

#                 src_w, src_h = img.size
#                 if not (no_up and src_w <= w and src_h <= h):
#                     if (not keep) or (mode == ResizeMode.STRETCH):
#                         img = img.resize((w, h), Image.LANCZOS)
#                     elif mode == ResizeMode.CONTAIN:
#                         img = ImageOps.contain(img, (w, h), method=Image.LANCZOS)
#                     elif mode == ResizeMode.COVER:
#                         img = ImageOps.fit(img, (w, h), method=Image.LANCZOS, centering=(0.5, 0.5))

#             # Render to Qt pixmap
#             img = img.convert("RGBA")
#             data = img.tobytes("raw", "RGBA")
#             qimg = QtGui.QImage(data, img.size[0], img.size[1], QtGui.QImage.Format_RGBA8888)
#             self.preview_after.set_pixmap(QtGui.QPixmap.fromImage(qimg))
#         except Exception:
#             self.preview_after.set_pixmap(None)

#         self._update_summary()

#     def _update_summary(self) -> None:
#         p = self._current_preview_path
#         if not p:
#             return
#         settings = self._build_settings()
#         if not settings:
#             self.lbl_summary.setText("Pick an output folder to see output summary.")
#             return

#         dst = estimate_output_path(p, settings)
#         parts = [
#             f"Input: {p.name}",
#             f"Output: {settings.output_format} -> {dst.name}",
#             f"Folder: {dst.parent}",
#         ]
#         if settings.resize_enabled:
#             parts.append(f"Resize: {settings.width}x{settings.height} | {settings.resize_mode}")
#             if settings.keep_aspect:
#                 parts.append("Aspect: locked")
#             else:
#                 parts.append("Aspect: unlocked")
#             if settings.do_not_upscale:
#                 parts.append("Upscale: blocked")

#         if settings.output_format in ("JPEG", "WEBP"):
#             parts.append(f"Quality: {settings.quality}")

#         # Transparency warning when output is JPEG
#         if settings.output_format == "JPEG":
#             parts.append("Note: JPEG cannot store transparency. It will be flattened.")

#         self.lbl_summary.setText(" | ".join(parts))

#     # ---------- Output folder helpers ----------

#     def _pick_outdir(self) -> None:
#         d = QtWidgets.QFileDialog.getExistingDirectory(self, "Select output folder")
#         if d:
#             self.txt_outdir.setText(d)

#     def _copy_selected_output_path(self) -> None:
#         p = self._current_preview_path
#         settings = self._build_settings()
#         if not p or not settings:
#             return
#         dst = estimate_output_path(p, settings)
#         QtWidgets.QApplication.clipboard().setText(str(dst))
#         self._log(f"Copied output path: {dst}")

#     def _open_output_folder(self) -> None:
#         settings = self._build_settings()
#         if not settings:
#             return
#         outdir = settings.output_dir
#         try:
#             if os.name == "nt":
#                 os.startfile(str(outdir))  # type: ignore[attr-defined]
#             else:
#                 QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(outdir)))
#         except Exception as e:
#             self._log(f"Failed to open folder: {e}")

#     # ---------- Controls + estimates ----------

#     def _refresh_controls(self) -> None:
#         fmt = self.cmb_format.currentText()
#         is_lossy = fmt in ("JPEG", "WEBP")
#         self.slider_quality.setEnabled(is_lossy)
#         self.lbl_quality.setEnabled(is_lossy)

#         naming_index = self.cmb_naming.currentIndex()
#         self.txt_name.setEnabled(naming_index in (1, 2))

#         resize_on = self.chk_resize.isChecked()
#         for w in (self.spin_w, self.spin_h, self.chk_aspect, self.cmb_resize_mode, self.chk_no_upscale):
#             w.setEnabled(resize_on)

#         # Transparency options only matter when output is JPEG/BMP, but keep visible
#         self._update_estimates()
#         self._update_preview_after()

#     def _update_estimates(self) -> None:
#         settings = self._build_settings()
#         for p, row in self._row_for_path.items():
#             if not settings:
#                 self._set_item(row, 4, "")
#                 continue
#             dst = estimate_output_path(p, settings)
#             self._set_item(row, 4, str(dst))

#     def _on_quality_changed(self, v: int) -> None:
#         self.lbl_quality.setText(f"Quality: {v}")
#         self._update_estimates()

#     def _on_flatten_choice(self) -> None:
#         text = self.cmb_flatten.currentText()
#         if "Pick custom" in text:
#             c = QtWidgets.QColorDialog.getColor(self._custom_flatten_color, self, "Pick background color")
#             if c.isValid():
#                 self._custom_flatten_color = c
#                 self._log(f"Flatten background set to RGB({c.red()},{c.green()},{c.blue()}).")
#         self._update_preview_after()

#     # ---------- Conversion worker ----------

#     def _start_convert(self) -> None:
#         if not self.files:
#             self._log("No files queued. Feed me pixels.")
#             return

#         settings = self._build_settings()
#         if not settings:
#             self._log("Pick an output folder first. Even I can’t save to ‘vibes’.")
#             return

#         self._log(f"Starting conversion of {len(self.files)} file(s) -> {settings.output_format} ...")
#         self.progress.setValue(0)
#         self.btn_convert.setEnabled(False)

#         # Reset table statuses
#         for p, row in self._row_for_path.items():
#             self._set_item(row, 0, "Queued")
#             self._set_item(row, 5, "")

#         worker = ConvertBatchWorker(self.files[:], settings)

#         worker.signals.progress.connect(self._on_progress)
#         worker.signals.result.connect(self._on_convert_result)
#         worker.signals.finished.connect(self._on_finished)
#         worker.signals.failed.connect(self._on_failed)

#         self.thread_pool.start(worker)

#     def _on_progress(self, done: int, total: int) -> None:
#         pct = int((done / max(total, 1)) * 100)
#         self.progress.setValue(pct)

#     def _on_convert_result(self, obj: object) -> None:
#         res = obj  # ConvertResult
#         if not isinstance(res, ConvertResult):
#             return

#         row = self._row_for_path.get(res.src)
#         if row is None:
#             return

#         if res.ok:
#             self._set_item(row, 0, "OK")
#             self._set_item(row, 5, "Converted")
#         else:
#             self._set_item(row, 0, "FAIL")
#             self._set_item(row, 5, res.message)

#         # Update output path in case autonumbering changed it
#         if res.dst:
#             self._set_item(row, 4, str(res.dst))

#     def _on_finished(self) -> None:
#         self.btn_convert.setEnabled(True)
#         self.progress.setValue(100)
#         self._log("Done. Your images have been reshaped into obedience.")

#     def _on_failed(self, msg: str) -> None:
#         self.btn_convert.setEnabled(True)
#         self._log(f"Worker failed: {msg}")

#     # ---------- Logging ----------

#     def _log(self, s: str) -> None:
#         self.log.appendPlainText(s)






















"""
modules/tabs/convert_tab.py

Scrollable Convert + Resize tab.
Wrapped in QScrollArea so the UI never overlaps on smaller screens.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PyQt5 import QtCore, QtGui, QtWidgets

from ..image_ops import (
    ConvertResult,
    ConvertSettings,
    ResizeMode,
    SUPPORTED_OUTPUT,
    estimate_output_path,
    is_supported_input,
)
from ..workers import ConvertBatchWorker
from ..widgets import DropTableWidget, ImagePreviewLabel


def _rgb_from_qcolor(c: QtGui.QColor) -> Tuple[int, int, int]:
    return (c.red(), c.green(), c.blue())


class ConvertTab(QtWidgets.QWidget):
    """
    This widget contains a QScrollArea that wraps the actual content widget.
    That way the tab is always usable, even if the window is smaller.
    """
    COLS = ["Status", "File", "Format", "WxH", "Output Path", "Message"]

    def __init__(self) -> None:
        super().__init__()
        self.thread_pool = QtCore.QThreadPool.globalInstance()

        self.files: List[Path] = []
        self._row_for_path: Dict[Path, int] = {}
        self._current_preview_path: Optional[Path] = None
        self._custom_flatten_color = QtGui.QColor(0, 0, 0)

        # Root layout holds only the scroll area
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
        self._refresh_controls()

    # ---------- UI ----------

    def _build_ui(self, parent: QtWidgets.QWidget) -> None:
        root = QtWidgets.QHBoxLayout(parent)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        # Left: table + controls
        left = QtWidgets.QVBoxLayout()
        left.setSpacing(10)

        self.table = DropTableWidget(self._on_files_dropped)
        self.table.setColumnCount(len(self.COLS))
        self.table.setHorizontalHeaderLabels(self.COLS)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setToolTip("Drag & drop images here.")

        btn_row = QtWidgets.QHBoxLayout()
        self.btn_add = QtWidgets.QPushButton("Add Files")
        self.btn_add.setObjectName("SecondaryButton")
        self.btn_remove = QtWidgets.QPushButton("Remove Selected")
        self.btn_remove.setObjectName("SecondaryButton")
        self.btn_clear = QtWidgets.QPushButton("Clear")
        self.btn_clear.setObjectName("DangerButton")
        btn_row.addWidget(self.btn_add)
        btn_row.addWidget(self.btn_remove)
        btn_row.addWidget(self.btn_clear)
        btn_row.addStretch(1)

        left.addWidget(self.table, 1)
        left.addLayout(btn_row)

        # Output settings
        settings = QtWidgets.QGroupBox("Output Settings")
        sgrid = QtWidgets.QGridLayout(settings)
        sgrid.setHorizontalSpacing(10)
        sgrid.setVerticalSpacing(10)

        self.cmb_format = QtWidgets.QComboBox()
        self.cmb_format.addItems(sorted(SUPPORTED_OUTPUT))
        self.cmb_format.setCurrentText("PNG")

        self.txt_outdir = QtWidgets.QLineEdit()
        self.txt_outdir.setPlaceholderText("Choose output folder...")
        self.btn_outdir = QtWidgets.QPushButton("Browse")
        self.btn_outdir.setObjectName("SecondaryButton")

        self.cmb_naming = QtWidgets.QComboBox()
        self.cmb_naming.addItems(["Keep original name", "Add prefix", "Add suffix"])
        self.txt_name = QtWidgets.QLineEdit()
        self.txt_name.setPlaceholderText("prefix_or_suffix")
        self.chk_autonum = QtWidgets.QCheckBox("Auto-number if collisions happen")
        self.chk_autonum.setChecked(True)

        sgrid.addWidget(QtWidgets.QLabel("Output format"), 0, 0)
        sgrid.addWidget(self.cmb_format, 0, 1)

        sgrid.addWidget(QtWidgets.QLabel("Output folder"), 1, 0)
        sgrid.addWidget(self.txt_outdir, 1, 1)
        sgrid.addWidget(self.btn_outdir, 1, 2)

        sgrid.addWidget(QtWidgets.QLabel("Naming"), 2, 0)
        sgrid.addWidget(self.cmb_naming, 2, 1)
        sgrid.addWidget(self.txt_name, 2, 2)

        sgrid.addWidget(self.chk_autonum, 3, 1, 1, 2)

        left.addWidget(settings)

        # Resize group
        resize_g = QtWidgets.QGroupBox("Resize (Optional)")
        rgrid = QtWidgets.QGridLayout(resize_g)
        rgrid.setHorizontalSpacing(10)
        rgrid.setVerticalSpacing(10)

        self.chk_resize = QtWidgets.QCheckBox("Resize enabled")
        self.chk_resize.setChecked(False)

        self.spin_w = QtWidgets.QSpinBox()
        self.spin_w.setRange(1, 20000)
        self.spin_w.setValue(1600)

        self.spin_h = QtWidgets.QSpinBox()
        self.spin_h.setRange(1, 20000)
        self.spin_h.setValue(1600)

        self.chk_aspect = QtWidgets.QCheckBox("Keep aspect ratio")
        self.chk_aspect.setChecked(True)

        self.cmb_resize_mode = QtWidgets.QComboBox()
        self.cmb_resize_mode.addItems([ResizeMode.CONTAIN, ResizeMode.COVER, ResizeMode.STRETCH])

        self.chk_no_upscale = QtWidgets.QCheckBox("Do not upscale")
        self.chk_no_upscale.setChecked(True)

        self.slider_quality = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_quality.setRange(1, 100)
        self.slider_quality.setValue(90)
        self.lbl_quality = QtWidgets.QLabel("Quality: 90")

        self.chk_optimize = QtWidgets.QCheckBox("Optimize output size (may be slower)")
        self.chk_optimize.setChecked(True)

        rgrid.addWidget(self.chk_resize, 0, 0, 1, 3)
        rgrid.addWidget(QtWidgets.QLabel("Width"), 1, 0)
        rgrid.addWidget(self.spin_w, 1, 1)
        rgrid.addWidget(self.chk_aspect, 1, 2)
        rgrid.addWidget(QtWidgets.QLabel("Height"), 2, 0)
        rgrid.addWidget(self.spin_h, 2, 1)
        rgrid.addWidget(QtWidgets.QLabel("Mode"), 3, 0)
        rgrid.addWidget(self.cmb_resize_mode, 3, 1, 1, 2)
        rgrid.addWidget(self.chk_no_upscale, 4, 0, 1, 3)
        rgrid.addWidget(self.lbl_quality, 5, 0)
        rgrid.addWidget(self.slider_quality, 5, 1, 1, 2)
        rgrid.addWidget(self.chk_optimize, 6, 0, 1, 3)

        left.addWidget(resize_g)

        # Extras group
        extras = QtWidgets.QGroupBox("Extras")
        egrid = QtWidgets.QGridLayout(extras)
        egrid.setHorizontalSpacing(10)
        egrid.setVerticalSpacing(10)

        self.chk_strip = QtWidgets.QCheckBox("Strip metadata (EXIF)")
        self.chk_strip.setChecked(False)

        self.chk_autorotate = QtWidgets.QCheckBox("Auto-rotate using EXIF orientation")
        self.chk_autorotate.setChecked(True)

        self.cmb_flatten = QtWidgets.QComboBox()
        self.cmb_flatten.addItems(["Flatten on BLACK", "Flatten on WHITE", "Pick custom color..."])

        egrid.addWidget(self.chk_strip, 0, 0, 1, 2)
        egrid.addWidget(self.chk_autorotate, 1, 0, 1, 2)
        egrid.addWidget(QtWidgets.QLabel("Transparency (PNG → JPG/BMP):"), 2, 0)
        egrid.addWidget(self.cmb_flatten, 2, 1)

        left.addWidget(extras)

        # Run controls
        run_row = QtWidgets.QHBoxLayout()
        self.btn_convert = QtWidgets.QPushButton("Convert")
        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        run_row.addWidget(self.btn_convert)
        run_row.addWidget(self.progress, 1)

        left.addLayout(run_row)

        self.log = QtWidgets.QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Logs appear here.")

        left.addWidget(self.log, 0)

        # Right: preview
        right = QtWidgets.QVBoxLayout()
        right.setSpacing(10)

        prev_box = QtWidgets.QGroupBox("Preview")
        pv = QtWidgets.QVBoxLayout(prev_box)
        pv.setSpacing(10)

        self.preview_before = ImagePreviewLabel()
        self.preview_after = ImagePreviewLabel()

        self.lbl_summary = QtWidgets.QLabel("Select a file to preview.")
        self.lbl_summary.setWordWrap(True)

        tools = QtWidgets.QHBoxLayout()
        self.btn_copy_outpath = QtWidgets.QPushButton("Copy output path")
        self.btn_copy_outpath.setObjectName("SecondaryButton")
        self.btn_open_outdir = QtWidgets.QPushButton("Open output folder")
        self.btn_open_outdir.setObjectName("SecondaryButton")
        tools.addWidget(self.btn_copy_outpath)
        tools.addWidget(self.btn_open_outdir)

        pv.addWidget(QtWidgets.QLabel("Before"))
        pv.addWidget(self.preview_before, 1)
        pv.addWidget(QtWidgets.QLabel("After (resize preview)"))
        pv.addWidget(self.preview_after, 1)
        pv.addWidget(self.lbl_summary)
        pv.addLayout(tools)

        right.addWidget(prev_box, 1)

        root.addLayout(left, 3)
        root.addLayout(right, 2)

    # ---------- Wiring ----------

    def _wire(self) -> None:
        self.btn_add.clicked.connect(self._pick_files)
        self.btn_remove.clicked.connect(self._remove_selected)
        self.btn_clear.clicked.connect(self._clear_all)
        self.btn_outdir.clicked.connect(self._pick_outdir)

        self.cmb_format.currentTextChanged.connect(self._refresh_controls)
        self.cmb_naming.currentIndexChanged.connect(self._refresh_controls)
        self.txt_name.textChanged.connect(self._update_estimates)
        self.txt_outdir.textChanged.connect(self._update_estimates)
        self.chk_resize.toggled.connect(self._refresh_controls)

        self.spin_w.valueChanged.connect(self._update_preview_after)
        self.spin_h.valueChanged.connect(self._update_preview_after)
        self.chk_aspect.toggled.connect(self._update_preview_after)
        self.cmb_resize_mode.currentTextChanged.connect(self._update_preview_after)
        self.chk_no_upscale.toggled.connect(self._update_preview_after)

        self.slider_quality.valueChanged.connect(self._on_quality_changed)
        self.chk_optimize.toggled.connect(self._update_estimates)

        self.chk_strip.toggled.connect(self._update_preview_after)
        self.chk_autorotate.toggled.connect(self._update_preview_after)

        self.cmb_flatten.currentIndexChanged.connect(self._on_flatten_choice)

        self.table.itemSelectionChanged.connect(self._on_selection_changed)

        self.btn_convert.clicked.connect(self._start_convert)

        self.btn_copy_outpath.clicked.connect(self._copy_selected_output_path)
        self.btn_open_outdir.clicked.connect(self._open_output_folder)

    # ---------- File ingest ----------

    def _on_files_dropped(self, paths: List[Path]) -> None:
        self._add_files(paths)

    def _pick_files(self) -> None:
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            "Select images",
            "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp *.tif *.tiff *.gif)",
        )
        self._add_files([Path(f) for f in files])

    def _add_files(self, paths: List[Path]) -> None:
        expanded: List[Path] = []
        for p in paths:
            if p.is_dir():
                for child in p.rglob("*"):
                    if child.is_file() and is_supported_input(child):
                        expanded.append(child)
            else:
                expanded.append(p)

        new_files: List[Path] = []
        for p in expanded:
            if p.exists() and p.is_file() and is_supported_input(p) and p not in self.files:
                new_files.append(p)

        if not new_files:
            self._log("No valid images found.")
            return

        for p in new_files:
            self.files.append(p)
            self._append_row(p)

        self._log(f"Added {len(new_files)} file(s).")
        self._update_estimates()

        if self.table.currentRow() < 0 and self.table.rowCount() > 0:
            self.table.selectRow(0)

    def _append_row(self, p: Path) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        self._row_for_path[p] = row

        self._set_item(row, 0, "Queued")
        self._set_item(row, 1, p.name)
        self._set_item(row, 2, p.suffix.lower().lstrip("."))
        self._set_item(row, 3, self._read_dimensions_str(p))
        self._set_item(row, 4, "")
        self._set_item(row, 5, "")

    def _read_dimensions_str(self, p: Path) -> str:
        try:
            from PIL import Image
            img = Image.open(str(p))
            w, h = img.size
            return f"{w}x{h}"
        except Exception:
            return "?"

    def _set_item(self, row: int, col: int, text: str) -> None:
        self.table.setItem(row, col, QtWidgets.QTableWidgetItem(text))

    def _remove_selected(self) -> None:
        rows = sorted({idx.row() for idx in self.table.selectionModel().selectedRows()}, reverse=True)
        if not rows:
            return

        paths_by_row: Dict[int, Path] = {r: p for p, r in self._row_for_path.items()}
        for r in rows:
            p = paths_by_row.get(r)
            if p and p in self.files:
                self.files.remove(p)
                self._row_for_path.pop(p, None)
            self.table.removeRow(r)

        self._row_for_path = {}
        for r in range(self.table.rowCount()):
            name = self.table.item(r, 1).text()
            for p in self.files:
                if p.name == name and p not in self._row_for_path:
                    self._row_for_path[p] = r
                    break

        self._log(f"Removed {len(rows)} row(s).")
        self._update_estimates()
        self._clear_preview()

    def _clear_all(self) -> None:
        self.files.clear()
        self._row_for_path.clear()
        self.table.setRowCount(0)
        self._log("Cleared everything.")
        self._update_estimates()
        self._clear_preview()

    # ---------- Settings ----------

    def _get_flatten_color(self) -> Tuple[int, int, int]:
        t = self.cmb_flatten.currentText()
        if "BLACK" in t:
            return (0, 0, 0)
        if "WHITE" in t:
            return (255, 255, 255)
        return _rgb_from_qcolor(self._custom_flatten_color)

    def _build_settings(self) -> Optional[ConvertSettings]:
        outdir_txt = self.txt_outdir.text().strip()
        if not outdir_txt:
            return None
        outdir = Path(outdir_txt)

        naming_index = self.cmb_naming.currentIndex()
        name_mode = "keep"
        if naming_index == 1:
            name_mode = "prefix"
        elif naming_index == 2:
            name_mode = "suffix"

        return ConvertSettings(
            output_format=self.cmb_format.currentText(),
            output_dir=outdir,
            name_mode=name_mode,
            name_text=self.txt_name.text(),
            auto_number_collisions=self.chk_autonum.isChecked(),
            resize_enabled=self.chk_resize.isChecked(),
            width=int(self.spin_w.value()),
            height=int(self.spin_h.value()),
            keep_aspect=self.chk_aspect.isChecked(),
            resize_mode=self.cmb_resize_mode.currentText(),
            do_not_upscale=self.chk_no_upscale.isChecked(),
            quality=int(self.slider_quality.value()),
            optimize=self.chk_optimize.isChecked(),
            strip_metadata=self.chk_strip.isChecked(),
            autorotate_exif=self.chk_autorotate.isChecked(),
            flatten_bg_rgb=self._get_flatten_color(),
        )

    # ---------- Preview ----------

    def _on_selection_changed(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            return

        p = None
        for path, r in self._row_for_path.items():
            if r == row:
                p = path
                break
        if not p:
            return

        self._current_preview_path = p
        self._update_preview_before()
        self._update_preview_after()
        self._update_summary()

    def _clear_preview(self) -> None:
        self._current_preview_path = None
        self.preview_before.set_pixmap(None)
        self.preview_after.set_pixmap(None)
        self.lbl_summary.setText("Select a file to preview.")

    def _update_preview_before(self) -> None:
        p = self._current_preview_path
        if not p:
            return
        pix = QtGui.QPixmap(str(p))
        self.preview_before.set_pixmap(pix if not pix.isNull() else None)

    def _update_preview_after(self) -> None:
        p = self._current_preview_path
        if not p:
            return
        try:
            from PIL import Image, ImageOps
            img = Image.open(str(p))
            if self.chk_autorotate.isChecked():
                img = ImageOps.exif_transpose(img)

            if self.chk_resize.isChecked():
                w = int(self.spin_w.value())
                h = int(self.spin_h.value())
                keep = self.chk_aspect.isChecked()
                mode = self.cmb_resize_mode.currentText()
                no_up = self.chk_no_upscale.isChecked()

                src_w, src_h = img.size
                if not (no_up and src_w <= w and src_h <= h):
                    if (not keep) or (mode == ResizeMode.STRETCH):
                        img = img.resize((w, h), Image.LANCZOS)
                    elif mode == ResizeMode.CONTAIN:
                        img = ImageOps.contain(img, (w, h), method=Image.LANCZOS)
                    elif mode == ResizeMode.COVER:
                        img = ImageOps.fit(img, (w, h), method=Image.LANCZOS, centering=(0.5, 0.5))

            img = img.convert("RGBA")
            data = img.tobytes("raw", "RGBA")
            qimg = QtGui.QImage(data, img.size[0], img.size[1], QtGui.QImage.Format_RGBA8888)
            self.preview_after.set_pixmap(QtGui.QPixmap.fromImage(qimg))
        except Exception:
            self.preview_after.set_pixmap(None)

        self._update_summary()

    def _update_summary(self) -> None:
        p = self._current_preview_path
        if not p:
            return
        settings = self._build_settings()
        if not settings:
            self.lbl_summary.setText("Pick an output folder to see output summary.")
            return

        dst = estimate_output_path(p, settings)
        parts = [
            f"Input: {p.name}",
            f"Output: {settings.output_format} -> {dst.name}",
            f"Folder: {dst.parent}",
        ]
        if settings.resize_enabled:
            parts.append(f"Resize: {settings.width}x{settings.height} | {settings.resize_mode}")
            parts.append("Aspect: locked" if settings.keep_aspect else "Aspect: unlocked")
            if settings.do_not_upscale:
                parts.append("Upscale: blocked")
        if settings.output_format in ("JPEG", "WEBP"):
            parts.append(f"Quality: {settings.quality}")
        if settings.output_format == "JPEG":
            parts.append("Note: JPEG cannot store transparency (it will be flattened).")
        self.lbl_summary.setText(" | ".join(parts))

    # ---------- Output folder helpers ----------

    def _pick_outdir(self) -> None:
        d = QtWidgets.QFileDialog.getExistingDirectory(self, "Select output folder")
        if d:
            self.txt_outdir.setText(d)

    def _copy_selected_output_path(self) -> None:
        p = self._current_preview_path
        settings = self._build_settings()
        if not p or not settings:
            return
        dst = estimate_output_path(p, settings)
        QtWidgets.QApplication.clipboard().setText(str(dst))
        self._log(f"Copied: {dst}")

    def _open_output_folder(self) -> None:
        settings = self._build_settings()
        if not settings:
            return
        outdir = settings.output_dir
        try:
            if os.name == "nt":
                os.startfile(str(outdir))  # type: ignore[attr-defined]
            else:
                QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(outdir)))
        except Exception as e:
            self._log(f"Open folder failed: {e}")

    # ---------- Controls ----------

    def _refresh_controls(self) -> None:
        fmt = self.cmb_format.currentText()
        is_lossy = fmt in ("JPEG", "WEBP")
        self.slider_quality.setEnabled(is_lossy)
        self.lbl_quality.setEnabled(is_lossy)

        naming_index = self.cmb_naming.currentIndex()
        self.txt_name.setEnabled(naming_index in (1, 2))

        resize_on = self.chk_resize.isChecked()
        for w in (self.spin_w, self.spin_h, self.chk_aspect, self.cmb_resize_mode, self.chk_no_upscale):
            w.setEnabled(resize_on)

        self._update_estimates()
        self._update_preview_after()

    def _update_estimates(self) -> None:
        settings = self._build_settings()
        for p, row in self._row_for_path.items():
            if not settings:
                self._set_item(row, 4, "")
                continue
            dst = estimate_output_path(p, settings)
            self._set_item(row, 4, str(dst))

    def _on_quality_changed(self, v: int) -> None:
        self.lbl_quality.setText(f"Quality: {v}")
        self._update_estimates()

    def _on_flatten_choice(self) -> None:
        text = self.cmb_flatten.currentText()
        if "Pick custom" in text:
            c = QtWidgets.QColorDialog.getColor(self._custom_flatten_color, self, "Pick background color")
            if c.isValid():
                self._custom_flatten_color = c
                self._log(f"Flatten background set to RGB({c.red()},{c.green()},{c.blue()}).")
        self._update_preview_after()

    # ---------- Worker ----------

    def _start_convert(self) -> None:
        if not self.files:
            self._log("No files queued.")
            return

        settings = self._build_settings()
        if not settings:
            self._log("Pick an output folder first.")
            return

        self._log(f"Converting {len(self.files)} file(s) -> {settings.output_format} ...")
        self.progress.setValue(0)
        self.btn_convert.setEnabled(False)

        for p, row in self._row_for_path.items():
            self._set_item(row, 0, "Queued")
            self._set_item(row, 5, "")

        worker = ConvertBatchWorker(self.files[:], settings)
        worker.signals.progress.connect(self._on_progress)
        worker.signals.result.connect(self._on_convert_result)
        worker.signals.finished.connect(self._on_finished)
        worker.signals.failed.connect(self._on_failed)
        self.thread_pool.start(worker)

    def _on_progress(self, done: int, total: int) -> None:
        pct = int((done / max(total, 1)) * 100)
        self.progress.setValue(pct)

    def _on_convert_result(self, obj: object) -> None:
        if not isinstance(obj, ConvertResult):
            return
        res: ConvertResult = obj

        row = self._row_for_path.get(res.src)
        if row is None:
            return

        if res.ok:
            self._set_item(row, 0, "OK")
            self._set_item(row, 5, "Converted")
        else:
            self._set_item(row, 0, "FAIL")
            self._set_item(row, 5, res.message)

        if res.dst:
            self._set_item(row, 4, str(res.dst))

    def _on_finished(self) -> None:
        self.btn_convert.setEnabled(True)
        self.progress.setValue(100)
        self._log("Done.")

    def _on_failed(self, msg: str) -> None:
        self.btn_convert.setEnabled(True)
        self._log(f"Worker failed: {msg}")

    # ---------- Logging ----------

    def _log(self, s: str) -> None:
        self.log.appendPlainText(s)

