# """
# modules/gui.py

# PyQt5 GUI for "Ash's PDF Manipulator".

# Tabs:

# 1) Merge PDFs:
#    - Up to 6 input PDF file pickers
#    - Merge button
#    - User chooses:
#        * output file path (location + name)
#        * PDF "tab name" (document title metadata)

# 2) Split PDF:
#    - Single input PDF picker
#    - Split page selector
#    - Output folder picker
#    - Optional names for FIRST and SECOND PDFs
#      (defaults to "<original>_FIRST.pdf" and "<original>_SECOND.pdf")
# """

# from pathlib import Path
# from typing import List

# from PyQt5 import QtCore, QtWidgets

# from .pdf_utils import PdfError, merge_pdfs, split_pdf


# class PdfManipulatorWindow(QtWidgets.QMainWindow):
#     """
#     Main window containing a QTabWidget with:
#     - MergeTab
#     - SplitTab
#     """

#     def __init__(self, parent=None) -> None:  # type: ignore[override]
#         super().__init__(parent)

#         self.setWindowTitle("Ash's PDF Manipulator")
#         self.resize(900, 600)

#         central = QtWidgets.QWidget(self)
#         self.setCentralWidget(central)

#         layout = QtWidgets.QVBoxLayout(central)

#         self.tab_widget = QtWidgets.QTabWidget(self)
#         layout.addWidget(self.tab_widget)

#         # Create and add tabs
#         self.merge_tab = MergeTab(self)
#         self.split_tab = SplitTab(self)

#         self.tab_widget.addTab(self.merge_tab, "Merge PDFs")
#         self.tab_widget.addTab(self.split_tab, "Split PDF")


# class MergeTab(QtWidgets.QWidget):
#     """
#     Tab for merging up to 6 PDF files into one.
#     """

#     MAX_FILES = 6

#     def __init__(self, parent=None) -> None:  # type: ignore[override]
#         super().__init__(parent)

#         main_layout = QtWidgets.QVBoxLayout(self)
#         main_layout.setSpacing(12)

#         # Group box for input files
#         files_group = QtWidgets.QGroupBox("Input PDFs (in merge order):", self)
#         files_layout = QtWidgets.QVBoxLayout(files_group)

#         self.file_edits: List[QtWidgets.QLineEdit] = []
#         for i in range(self.MAX_FILES):
#             row = QtWidgets.QHBoxLayout()
#             label = QtWidgets.QLabel(f"PDF {i + 1}:", self)

#             edit = QtWidgets.QLineEdit(self)
#             edit.setReadOnly(True)

#             browse_btn = QtWidgets.QPushButton("Browse…", self)
#             browse_btn.clicked.connect(
#                 lambda _, idx=i: self._choose_input_pdf(idx)
#             )

#             row.addWidget(label)
#             row.addWidget(edit)
#             row.addWidget(browse_btn)

#             files_layout.addLayout(row)
#             self.file_edits.append(edit)

#         main_layout.addWidget(files_group)

#         # Output section: save path + tab title
#         output_group = QtWidgets.QGroupBox("Output settings:", self)
#         output_layout = QtWidgets.QFormLayout(output_group)

#         # Output file path (user chooses via save dialog)
#         self.output_path_edit = QtWidgets.QLineEdit(self)
#         self.output_path_edit.setReadOnly(True)
#         output_browse_btn = QtWidgets.QPushButton("Choose output file…", self)
#         output_browse_btn.clicked.connect(self._choose_output_file)

#         output_path_row = QtWidgets.QHBoxLayout()
#         output_path_row.addWidget(self.output_path_edit)
#         output_path_row.addWidget(output_browse_btn)

#         output_layout.addRow("Output merged PDF:", output_path_row)

#         # Tab title / document title metadata
#         self.title_edit = QtWidgets.QLineEdit(self)
#         self.title_edit.setPlaceholderText(
#             "Optional: Title used as tab name in PDF viewers (e.g. Chrome)."
#         )
#         output_layout.addRow("PDF tab name / title:", self.title_edit)

#         main_layout.addWidget(output_group)

#         # Merge button
#         self.merge_button = QtWidgets.QPushButton("Merge PDFs", self)
#         self.merge_button.clicked.connect(self._on_merge_clicked)
#         main_layout.addWidget(self.merge_button, alignment=QtCore.Qt.AlignRight)

#         # Status label (small, at bottom)
#         self.status_label = QtWidgets.QLabel(self)
#         self.status_label.setObjectName("statusLabel")
#         self.status_label.setText("Ready.")
#         main_layout.addWidget(self.status_label)

#         main_layout.addStretch(1)

#     # -----------------------
#     # Helpers / Slots
#     # -----------------------

#     def _choose_input_pdf(self, index: int) -> None:
#         """
#         Open a file dialog to select a PDF and put the path into the line edit.
#         """
#         path, _ = QtWidgets.QFileDialog.getOpenFileName(
#             self,
#             "Select PDF file",
#             "",
#             "PDF files (*.pdf);;All files (*.*)",
#         )
#         if path:
#             self.file_edits[index].setText(path)
#             self.status_label.setText(f"Selected PDF {index + 1}.")

#     def _choose_output_file(self) -> None:
#         """
#         Open a save dialog so the user can choose where and how to name the merged PDF.
#         """
#         path, _ = QtWidgets.QFileDialog.getSaveFileName(
#             self,
#             "Save merged PDF as",
#             "merged.pdf",
#             "PDF files (*.pdf);;All files (*.*)",
#         )
#         if path:
#             # Ensure it ends with .pdf
#             if not path.lower().endswith(".pdf"):
#                 path += ".pdf"
#             self.output_path_edit.setText(path)
#             self.status_label.setText("Output file selected.")

#     def _on_merge_clicked(self) -> None:
#         """
#         Collect selected PDFs and merge them into one.
#         """
#         input_paths = [
#             edit.text().strip() for edit in self.file_edits if edit.text().strip()
#         ]

#         if len(input_paths) < 2:
#             QtWidgets.QMessageBox.warning(
#                 self,
#                 "Not enough PDFs",
#                 "Please select at least two PDF files to merge.",
#             )
#             return

#         # Determine output path. If user hasn't chosen, default near first file.
#         output_path = self.output_path_edit.text().strip()
#         if not output_path:
#             first = Path(input_paths[0])
#             default_out = first.with_name(first.stem + "_merged.pdf")
#             self.output_path_edit.setText(str(default_out))
#             output_path = str(default_out)

#         title = self.title_edit.text().strip() or None

#         try:
#             merge_pdfs(input_paths, output_path, title=title)
#         except PdfError as exc:
#             QtWidgets.QMessageBox.critical(
#                 self,
#                 "Merge failed",
#                 str(exc),
#             )
#             self.status_label.setText("Merge failed.")
#             return

#         QtWidgets.QMessageBox.information(
#             self,
#             "Merge complete",
#             f"Merged PDF saved to:\n{output_path}",
#         )
#         self.status_label.setText("Merge complete.")


# class SplitTab(QtWidgets.QWidget):
#     """
#     Tab for splitting a single PDF into two PDFs at a given page.
#     """

#     def __init__(self, parent=None) -> None:  # type: ignore[override]
#         super().__init__(parent)

#         main_layout = QtWidgets.QVBoxLayout(self)
#         main_layout.setSpacing(12)

#         # Input PDF
#         input_group = QtWidgets.QGroupBox("Input PDF:", self)
#         input_layout = QtWidgets.QHBoxLayout(input_group)

#         self.input_edit = QtWidgets.QLineEdit(self)
#         self.input_edit.setReadOnly(True)

#         browse_btn = QtWidgets.QPushButton("Browse…", self)
#         browse_btn.clicked.connect(self._choose_input_pdf)

#         input_layout.addWidget(self.input_edit)
#         input_layout.addWidget(browse_btn)

#         main_layout.addWidget(input_group)

#         # Split settings
#         split_group = QtWidgets.QGroupBox("Split settings:", self)
#         split_form = QtWidgets.QFormLayout(split_group)

#         # Split page spinbox (will be updated once PDF is chosen)
#         self.split_spin = QtWidgets.QSpinBox(self)
#         self.split_spin.setMinimum(2)
#         self.split_spin.setMaximum(2)
#         self.split_spin.setValue(2)
#         self.split_spin.setEnabled(False)
#         self.split_spin.setToolTip(
#             "Split page is the first page of the SECOND PDF.\n"
#             "Example: split page = 4, PDF = 10 pages ->\n"
#             "FIRST = pages 1-3, SECOND = pages 4-10."
#         )
#         split_form.addRow("Split at page:", self.split_spin)

#         main_layout.addWidget(split_group)

#         # Output folder + names
#         output_group = QtWidgets.QGroupBox("Output settings:", self)
#         output_form = QtWidgets.QFormLayout(output_group)

#         # Folder chooser
#         self.output_folder_edit = QtWidgets.QLineEdit(self)
#         self.output_folder_edit.setReadOnly(True)

#         folder_btn = QtWidgets.QPushButton("Choose folder…", self)
#         folder_btn.clicked.connect(self._choose_output_folder)

#         folder_row = QtWidgets.QHBoxLayout()
#         folder_row.addWidget(self.output_folder_edit)
#         folder_row.addWidget(folder_btn)

#         output_form.addRow("Output folder:", folder_row)

#         # Optional custom names
#         self.first_name_edit = QtWidgets.QLineEdit(self)
#         self.first_name_edit.setPlaceholderText(
#             "Optional: name for FIRST PDF (without .pdf)."
#         )
#         output_form.addRow("FIRST PDF name:", self.first_name_edit)

#         self.second_name_edit = QtWidgets.QLineEdit(self)
#         self.second_name_edit.setPlaceholderText(
#             "Optional: name for SECOND PDF (without .pdf)."
#         )
#         output_form.addRow("SECOND PDF name:", self.second_name_edit)

#         main_layout.addWidget(output_group)

#         # Split button
#         self.split_button = QtWidgets.QPushButton("Split PDF", self)
#         self.split_button.clicked.connect(self._on_split_clicked)
#         self.split_button.setEnabled(False)
#         main_layout.addWidget(self.split_button, alignment=QtCore.Qt.AlignRight)

#         # Status label at bottom
#         self.status_label = QtWidgets.QLabel(self)
#         self.status_label.setObjectName("statusLabel")
#         self.status_label.setText("Ready.")
#         main_layout.addWidget(self.status_label)

#         main_layout.addStretch(1)

#         # Cache total pages once input selected
#         self._total_pages: int | None = None

#     # -----------------------
#     # Helpers / Slots
#     # -----------------------

#     def _choose_input_pdf(self) -> None:
#         """
#         Let the user select an input PDF, then determine page count
#         and configure the split spinbox accordingly.
#         """
#         path, _ = QtWidgets.QFileDialog.getOpenFileName(
#             self,
#             "Select PDF file to split",
#             "",
#             "PDF files (*.pdf);;All files (*.*)",
#         )
#         if not path:
#             return

#         self.input_edit.setText(path)
#         self.status_label.setText("Selected input PDF. Reading page count…")

#         # Determine page count using PdfReader
#         from pypdf import PdfReader  # local import to avoid circulars

#         try:
#             reader = PdfReader(path)
#             total_pages = len(reader.pages)
#         except Exception as exc:  # noqa: BLE001
#             QtWidgets.QMessageBox.critical(
#                 self,
#                 "Error reading PDF",
#                 f"Failed to read PDF: {exc}",
#             )
#             self.status_label.setText("Failed to read PDF.")
#             self.split_spin.setEnabled(False)
#             self.split_button.setEnabled(False)
#             self._total_pages = None
#             return

#         if total_pages < 2:
#             QtWidgets.QMessageBox.warning(
#                 self,
#                 "Too few pages",
#                 "This PDF has fewer than 2 pages and cannot be split.",
#             )
#             self.status_label.setText("PDF too short to split.")
#             self.split_spin.setEnabled(False)
#             self.split_button.setEnabled(False)
#             self._total_pages = None
#             return

#         self._total_pages = total_pages
#         # Valid split page range: [2, total_pages]
#         self.split_spin.setMinimum(2)
#         self.split_spin.setMaximum(total_pages)
#         self.split_spin.setValue(2)
#         self.split_spin.setEnabled(True)
#         self.split_button.setEnabled(True)

#         self.status_label.setText(
#             f"Loaded PDF with {total_pages} pages. Choose split page."
#         )

#     def _choose_output_folder(self) -> None:
#         """
#         Let the user choose an output folder for the two PDFs.
#         """
#         folder = QtWidgets.QFileDialog.getExistingDirectory(
#             self,
#             "Select output folder",
#             "",
#         )
#         if folder:
#             self.output_folder_edit.setText(folder)
#             self.status_label.setText("Output folder selected.")

#     def _on_split_clicked(self) -> None:
#         """
#         Perform the split operation using the entered settings.
#         """
#         input_path = self.input_edit.text().strip()
#         if not input_path:
#             QtWidgets.QMessageBox.warning(
#                 self,
#                 "No input PDF",
#                 "Please choose an input PDF.",
#             )
#             return

#         if self._total_pages is None:
#             QtWidgets.QMessageBox.warning(
#                 self,
#                 "Unknown page count",
#                 "Please re-select the input PDF.",
#             )
#             return

#         split_page = self.split_spin.value()
#         if split_page <= 1 or split_page > self._total_pages:
#             QtWidgets.QMessageBox.warning(
#                 self,
#                 "Invalid split page",
#                 f"Split page must be between 2 and {self._total_pages}.",
#             )
#             return

#         output_folder = self.output_folder_edit.text().strip()
#         if not output_folder:
#             QtWidgets.QMessageBox.warning(
#                 self,
#                 "No output folder",
#                 "Please choose an output folder.",
#             )
#             return

#         in_path = Path(input_path)
#         base_name = in_path.stem

#         # Determine output file names
#         first_base = self.first_name_edit.text().strip() or f"{base_name}_FIRST"
#         second_base = self.second_name_edit.text().strip() or f"{base_name}_SECOND"

#         if not first_base.lower().endswith(".pdf"):
#             first_base += ".pdf"
#         if not second_base.lower().endswith(".pdf"):
#             second_base += ".pdf"

#         out_first = str(Path(output_folder) / first_base)
#         out_second = str(Path(output_folder) / second_base)

#         try:
#             path_first, path_second = split_pdf(
#                 input_path=input_path,
#                 split_page=split_page,
#                 output_path_first=out_first,
#                 output_path_second=out_second,
#             )
#         except PdfError as exc:
#             QtWidgets.QMessageBox.critical(
#                 self,
#                 "Split failed",
#                 str(exc),
#             )
#             self.status_label.setText("Split failed.")
#             return

#         QtWidgets.QMessageBox.information(
#             self,
#             "Split complete",
#             f"FIRST PDF:\n{path_first}\n\nSECOND PDF:\n{path_second}",
#         )
#         self.status_label.setText("Split complete.")

















"""
modules/gui.py

PyQt5 GUI for "Ash's PDF Manipulator".

Tabs:

1) Merge PDFs:
   - Up to 6 input PDF file pickers
   - Merge button
   - User chooses:
       * output file path (location + name)
       * PDF "tab name" (document title metadata)

2) Split PDF:
   - Single input PDF picker
   - Split page selector
   - Output folder picker
   - Optional names for FIRST and SECOND PDFs
     (defaults to "<original>_FIRST.pdf" and "<original>_SECOND.pdf")
   - Optional browser tab / document titles for FIRST and SECOND PDFs
"""

from pathlib import Path
from typing import List

from PyQt5 import QtCore, QtWidgets

from .pdf_utils import PdfError, merge_pdfs, split_pdf


class PdfManipulatorWindow(QtWidgets.QMainWindow):
    """
    Main window containing a QTabWidget with:
    - MergeTab
    - SplitTab
    """

    def __init__(self, parent=None) -> None:  # type: ignore[override]
        super().__init__(parent)

        self.setWindowTitle("Ash's PDF Manipulator")
        self.resize(900, 600)

        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)

        layout = QtWidgets.QVBoxLayout(central)

        self.tab_widget = QtWidgets.QTabWidget(self)
        layout.addWidget(self.tab_widget)

        # Create and add tabs
        self.merge_tab = MergeTab(self)
        self.split_tab = SplitTab(self)

        self.tab_widget.addTab(self.merge_tab, "Merge PDFs")
        self.tab_widget.addTab(self.split_tab, "Split PDF")


class MergeTab(QtWidgets.QWidget):
    """
    Tab for merging up to 6 PDF files into one.
    """

    MAX_FILES = 6

    def __init__(self, parent=None) -> None:  # type: ignore[override]
        super().__init__(parent)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(12)

        # Group box for input files
        files_group = QtWidgets.QGroupBox("Input PDFs (in merge order):", self)
        files_layout = QtWidgets.QVBoxLayout(files_group)

        self.file_edits: List[QtWidgets.QLineEdit] = []
        for i in range(self.MAX_FILES):
            row = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(f"PDF {i + 1}:", self)

            edit = QtWidgets.QLineEdit(self)
            edit.setReadOnly(True)

            browse_btn = QtWidgets.QPushButton("Browse…", self)
            browse_btn.clicked.connect(
                lambda _, idx=i: self._choose_input_pdf(idx)
            )

            row.addWidget(label)
            row.addWidget(edit)
            row.addWidget(browse_btn)

            files_layout.addLayout(row)
            self.file_edits.append(edit)

        main_layout.addWidget(files_group)

        # Output section: save path + tab title
        output_group = QtWidgets.QGroupBox("Output settings:", self)
        output_layout = QtWidgets.QFormLayout(output_group)

        # Output file path (user chooses via save dialog)
        self.output_path_edit = QtWidgets.QLineEdit(self)
        self.output_path_edit.setReadOnly(True)
        output_browse_btn = QtWidgets.QPushButton("Choose output file…", self)
        output_browse_btn.clicked.connect(self._choose_output_file)

        output_path_row = QtWidgets.QHBoxLayout()
        output_path_row.addWidget(self.output_path_edit)
        output_path_row.addWidget(output_browse_btn)

        output_layout.addRow("Output merged PDF:", output_path_row)

        # Tab title / document title metadata
        self.title_edit = QtWidgets.QLineEdit(self)
        self.title_edit.setPlaceholderText(
            "Optional: Title used as tab name in PDF viewers (e.g. Chrome)."
        )
        output_layout.addRow("PDF tab name / title:", self.title_edit)

        main_layout.addWidget(output_group)

        # Merge button
        self.merge_button = QtWidgets.QPushButton("Merge PDFs", self)
        self.merge_button.clicked.connect(self._on_merge_clicked)
        main_layout.addWidget(self.merge_button, alignment=QtCore.Qt.AlignRight)

        # Status label (small, at bottom)
        self.status_label = QtWidgets.QLabel(self)
        self.status_label.setObjectName("statusLabel")
        self.status_label.setText("Ready.")
        main_layout.addWidget(self.status_label)

        main_layout.addStretch(1)

    # -----------------------
    # Helpers / Slots
    # -----------------------

    def _choose_input_pdf(self, index: int) -> None:
        """
        Open a file dialog to select a PDF and put the path into the line edit.
        """
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select PDF file",
            "",
            "PDF files (*.pdf);;All files (*.*)",
        )
        if path:
            self.file_edits[index].setText(path)
            self.status_label.setText(f"Selected PDF {index + 1}.")

    def _choose_output_file(self) -> None:
        """
        Open a save dialog so the user can choose where and how to name the merged PDF.
        """
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save merged PDF as",
            "merged.pdf",
            "PDF files (*.pdf);;All files (*.*)",
        )
        if path:
            # Ensure it ends with .pdf
            if not path.lower().endswith(".pdf"):
                path += ".pdf"
            self.output_path_edit.setText(path)
            self.status_label.setText("Output file selected.")

    def _on_merge_clicked(self) -> None:
        """
        Collect selected PDFs and merge them into one.
        """
        input_paths = [
            edit.text().strip() for edit in self.file_edits if edit.text().strip()
        ]

        if len(input_paths) < 2:
            QtWidgets.QMessageBox.warning(
                self,
                "Not enough PDFs",
                "Please select at least two PDF files to merge.",
            )
            return

        # Determine output path. If user hasn't chosen, default near first file.
        output_path = self.output_path_edit.text().strip()
        if not output_path:
            first = Path(input_paths[0])
            default_out = first.with_name(first.stem + "_merged.pdf")
            self.output_path_edit.setText(str(default_out))
            output_path = str(default_out)

        title = self.title_edit.text().strip() or None

        try:
            merge_pdfs(input_paths, output_path, title=title)
        except PdfError as exc:
            QtWidgets.QMessageBox.critical(
                self,
                "Merge failed",
                str(exc),
            )
            self.status_label.setText("Merge failed.")
            return

        QtWidgets.QMessageBox.information(
            self,
            "Merge complete",
            f"Merged PDF saved to:\n{output_path}",
        )
        self.status_label.setText("Merge complete.")


class SplitTab(QtWidgets.QWidget):
    """
    Tab for splitting a single PDF into two PDFs at a given page.
    """

    def __init__(self, parent=None) -> None:  # type: ignore[override]
        super().__init__(parent)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(12)

        # Input PDF
        input_group = QtWidgets.QGroupBox("Input PDF:", self)
        input_layout = QtWidgets.QHBoxLayout(input_group)

        self.input_edit = QtWidgets.QLineEdit(self)
        self.input_edit.setReadOnly(True)

        browse_btn = QtWidgets.QPushButton("Browse…", self)
        browse_btn.clicked.connect(self._choose_input_pdf)

        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(browse_btn)

        main_layout.addWidget(input_group)

        # Split settings
        split_group = QtWidgets.QGroupBox("Split settings:", self)
        split_form = QtWidgets.QFormLayout(split_group)

        # Split page spinbox (will be updated once PDF is chosen)
        self.split_spin = QtWidgets.QSpinBox(self)
        self.split_spin.setMinimum(2)
        self.split_spin.setMaximum(2)
        self.split_spin.setValue(2)
        self.split_spin.setEnabled(False)
        self.split_spin.setToolTip(
            "Split page is the first page of the SECOND PDF.\n"
            "Example: split page = 4, PDF = 10 pages ->\n"
            "FIRST = pages 1-3, SECOND = pages 4-10."
        )
        self.split_spin.valueChanged.connect(self._update_split_help_label)

        split_form.addRow("Split at page:", self.split_spin)

        # Helper label explaining how the split works
        self.split_help_label = QtWidgets.QLabel(self)
        self.split_help_label.setWordWrap(True)
        self.split_help_label.setStyleSheet("font-size: 11px; color: #C0C4D0;")
        self.split_help_label.setText(
            "Select a PDF and choose a split page.\n"
            "If the PDF has 10 pages and you choose split page 4, "
            "the result will be:\n"
            "pages 1–3, pages 4–10."
        )
        split_form.addRow("", self.split_help_label)

        main_layout.addWidget(split_group)

        # Output folder + names + titles
        output_group = QtWidgets.QGroupBox("Output settings:", self)
        output_form = QtWidgets.QFormLayout(output_group)

        # Folder chooser
        self.output_folder_edit = QtWidgets.QLineEdit(self)
        self.output_folder_edit.setReadOnly(True)

        folder_btn = QtWidgets.QPushButton("Choose folder…", self)
        folder_btn.clicked.connect(self._choose_output_folder)

        folder_row = QtWidgets.QHBoxLayout()
        folder_row.addWidget(self.output_folder_edit)
        folder_row.addWidget(folder_btn)

        output_form.addRow("Output folder:", folder_row)

        # Optional custom file names
        self.first_name_edit = QtWidgets.QLineEdit(self)
        self.first_name_edit.setPlaceholderText(
            "Optional: name for first PDF (without .pdf)."
        )
        output_form.addRow("First PDF file name:", self.first_name_edit)

        self.second_name_edit = QtWidgets.QLineEdit(self)
        self.second_name_edit.setPlaceholderText(
            "Optional: name for second PDF (without .pdf)."
        )
        output_form.addRow("Second PDF file name:", self.second_name_edit)

        # Optional browser tab / document titles
        self.first_title_edit = QtWidgets.QLineEdit(self)
        self.first_title_edit.setPlaceholderText(
            "Optional: browser tab / PDF title for first PDF."
        )
        output_form.addRow("First PDF tab/title:", self.first_title_edit)

        self.second_title_edit = QtWidgets.QLineEdit(self)
        self.second_title_edit.setPlaceholderText(
            "Optional: browser tab / PDF title for second PDF."
        )
        output_form.addRow("Second PDF tab/title:", self.second_title_edit)

        main_layout.addWidget(output_group)

        # Split button
        self.split_button = QtWidgets.QPushButton("Split PDF", self)
        self.split_button.clicked.connect(self._on_split_clicked)
        self.split_button.setEnabled(False)
        main_layout.addWidget(self.split_button, alignment=QtCore.Qt.AlignRight)

        # Status label at bottom
        self.status_label = QtWidgets.QLabel(self)
        self.status_label.setObjectName("statusLabel")
        self.status_label.setText("Ready.")
        main_layout.addWidget(self.status_label)

        main_layout.addStretch(1)

        # Cache total pages once input selected
        self._total_pages: int | None = None

    # -----------------------
    # Helpers / Slots
    # -----------------------

    def _update_split_help_label(self) -> None:
        """
        Update the helper text to show exactly how the split will behave
        for the current split page and total number of pages.
        """
        if self._total_pages is None:
            self.split_help_label.setText(
                "Select a PDF and choose a split page.\n"
                "Example: if the PDF has 10 pages and you choose split page 4, "
                "the result will be:\n"
                "FIRST PDF = pages 1–3, SECOND PDF = pages 4–10."
            )
            return

        split_page = self.split_spin.value()
        first_end = split_page - 1
        second_start = split_page
        total = self._total_pages

        self.split_help_label.setText(
            f"When you split at page {split_page} in a {total}-page PDF:\n"
            f"FIRST PDF  = pages 1–{first_end}\n"
            f"SECOND PDF = pages {second_start}–{total}"
        )

    def _choose_input_pdf(self) -> None:
        """
        Let the user select an input PDF, then determine page count
        and configure the split spinbox accordingly.
        """
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select PDF file to split",
            "",
            "PDF files (*.pdf);;All files (*.*)",
        )
        if not path:
            return

        self.input_edit.setText(path)
        self.status_label.setText("Selected input PDF. Reading page count…")

        # Determine page count using PdfReader
        from pypdf import PdfReader  # local import to avoid circulars

        try:
            reader = PdfReader(path)
            total_pages = len(reader.pages)
        except Exception as exc:  # noqa: BLE001
            QtWidgets.QMessageBox.critical(
                self,
                "Error reading PDF",
                f"Failed to read PDF: {exc}",
            )
            self.status_label.setText("Failed to read PDF.")
            self.split_spin.setEnabled(False)
            self.split_button.setEnabled(False)
            self._total_pages = None
            self._update_split_help_label()
            return

        if total_pages < 2:
            QtWidgets.QMessageBox.warning(
                self,
                "Too few pages",
                "This PDF has fewer than 2 pages and cannot be split.",
            )
            self.status_label.setText("PDF too short to split.")
            self.split_spin.setEnabled(False)
            self.split_button.setEnabled(False)
            self._total_pages = None
            self._update_split_help_label()
            return

        self._total_pages = total_pages
        # Valid split page range: [2, total_pages]
        self.split_spin.setMinimum(2)
        self.split_spin.setMaximum(total_pages)
        self.split_spin.setValue(2)
        self.split_spin.setEnabled(True)
        self.split_button.setEnabled(True)

        self.status_label.setText(
            f"Loaded PDF with {total_pages} pages. Choose split page."
        )
        self._update_split_help_label()

    def _choose_output_folder(self) -> None:
        """
        Let the user choose an output folder for the two PDFs.
        """
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select output folder",
            "",
        )
        if folder:
            self.output_folder_edit.setText(folder)
            self.status_label.setText("Output folder selected.")

    def _on_split_clicked(self) -> None:
        """
        Perform the split operation using the entered settings.
        """
        input_path = self.input_edit.text().strip()
        if not input_path:
            QtWidgets.QMessageBox.warning(
                self,
                "No input PDF",
                "Please choose an input PDF.",
            )
            return

        if self._total_pages is None:
            QtWidgets.QMessageBox.warning(
                self,
                "Unknown page count",
                "Please re-select the input PDF.",
            )
            return

        split_page = self.split_spin.value()
        if split_page <= 1 or split_page > self._total_pages:
            QtWidgets.QMessageBox.warning(
                self,
                "Invalid split page",
                f"Split page must be between 2 and {self._total_pages}.",
            )
            return

        output_folder = self.output_folder_edit.text().strip()
        if not output_folder:
            QtWidgets.QMessageBox.warning(
                self,
                "No output folder",
                "Please choose an output folder.",
            )
            return

        in_path = Path(input_path)
        base_name = in_path.stem

        # Determine output file names
        first_base = self.first_name_edit.text().strip() or f"{base_name}_FIRST"
        second_base = self.second_name_edit.text().strip() or f"{base_name}_SECOND"

        if not first_base.lower().endswith(".pdf"):
            first_base += ".pdf"
        if not second_base.lower().endswith(".pdf"):
            second_base += ".pdf"

        out_first = str(Path(output_folder) / first_base)
        out_second = str(Path(output_folder) / second_base)

        # Optional tab / document titles
        first_title = self.first_title_edit.text().strip() or None
        second_title = self.second_title_edit.text().strip() or None

        try:
            path_first, path_second = split_pdf(
                input_path=input_path,
                split_page=split_page,
                output_path_first=out_first,
                output_path_second=out_second,
                first_title=first_title,
                second_title=second_title,
            )
        except PdfError as exc:
            QtWidgets.QMessageBox.critical(
                self,
                "Split failed",
                str(exc),
            )
            self.status_label.setText("Split failed.")
            return

        QtWidgets.QMessageBox.information(
            self,
            "Split complete",
            f"FIRST PDF:\n{path_first}\n\nSECOND PDF:\n{path_second}",
        )
        self.status_label.setText("Split complete.")
