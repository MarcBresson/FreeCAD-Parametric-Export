"""The GridParams dialog: build a parameter grid, preview resulting variations, and run export.

All expansion/naming/export-planning logic is delegated to freecad.gridparams.core -- this
module only translates between Qt widgets and that core's dataclasses.
"""

from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets

from freecad.gridparams.core.config import ConfigSchemaError, ExportSettings, GridConfig, GridItem, expand_config
from freecad.gridparams.core.values import Fixed, LinSpace, Range, ValueList
from freecad.gridparams.core.variation import find_duplicate_names

from . import persistence, runner, selection

_VALUE_PLACEHOLDERS = {
    "Fixed": "e.g. 12",
    "List": "e.g. 1000, 1500, 2000",
    "LinSpace": "start, stop, num",
    "Range": "start, stop, step",
}


def _parse_scalar(text):
    text = text.strip()
    if text.lower() == "true":
        return True
    if text.lower() == "false":
        return False
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        pass
    return text


def _build_param_value(kind, raw_text):
    if kind == "Fixed":
        return Fixed(_parse_scalar(raw_text))
    if kind == "List":
        parts = [part.strip() for part in raw_text.split(",") if part.strip() != ""]
        return ValueList([_parse_scalar(part) for part in parts])
    if kind == "LinSpace":
        start, stop, num = (part.strip() for part in raw_text.split(","))
        return LinSpace(float(start), float(stop), int(num))
    if kind == "Range":
        parts = [part.strip() for part in raw_text.split(",")]
        step = float(parts[2]) if len(parts) > 2 else 1
        return Range(float(parts[0]), float(parts[1]), step)
    raise ValueError(f"Unknown parameter kind: {kind!r}")


def _describe_param_value(value):
    if isinstance(value, Fixed):
        return "Fixed", str(value.value)
    if isinstance(value, ValueList):
        return "List", ", ".join(str(v) for v in value.values)
    if isinstance(value, LinSpace):
        return "LinSpace", f"{value.start}, {value.stop}, {value.num}"
    if isinstance(value, Range):
        return "Range", f"{value.start}, {value.stop}, {value.step}"
    if isinstance(value, list):
        return "List", ", ".join(str(v) for v in value)
    return "Fixed", str(value)


class GridParamsDialog(QtWidgets.QDialog):
    def __init__(self, doc, parent=None):
        super().__init__(parent)
        self.doc = doc
        self._selected_object_names = []
        self.setWindowTitle("Grid Params Export")
        self.resize(900, 650)

        try:
            config = persistence.load_config(doc) or GridConfig(base_name=doc.Name)
        except ConfigSchemaError as exc:
            QtWidgets.QMessageBox.warning(
                self,
                "GridParams",
                f"Could not load saved grid configuration: {exc}\n\n"
                "Starting from a blank configuration instead -- the previously saved one is "
                "left untouched in the document until you explicitly Save over it.",
            )
            config = GridConfig(base_name=doc.Name)
        self._items = list(config.items)

        self._build_ui()
        self._load_from_config(config)

    # -- UI construction -------------------------------------------------

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        header_form = QtWidgets.QFormLayout()
        self.base_name_edit = QtWidgets.QLineEdit()
        self.naming_template_edit = QtWidgets.QLineEdit()
        self.naming_template_edit.setPlaceholderText("{base_name} - {ParamName}")
        self.varset_combo = QtWidgets.QComboBox()
        self.varset_combo.addItems(
            [obj.Name for obj in self.doc.Objects if obj.TypeId == "App::VarSet"]
        )
        self.varset_combo.currentTextChanged.connect(self._refresh_param_name_choices)
        header_form.addRow("Base name", self.base_name_edit)
        header_form.addRow("Default naming template", self.naming_template_edit)
        header_form.addRow("VarSet", self.varset_combo)
        layout.addLayout(header_form)

        items_split = QtWidgets.QHBoxLayout()

        items_panel = QtWidgets.QVBoxLayout()
        items_panel.addWidget(QtWidgets.QLabel("Grid items (one per configuration/version)"))
        self.items_list = QtWidgets.QListWidget()
        self.items_list.currentItemChanged.connect(self._on_item_selection_changed)
        items_panel.addWidget(self.items_list)
        items_buttons = QtWidgets.QHBoxLayout()
        add_item_btn = QtWidgets.QPushButton("Add Item")
        add_item_btn.clicked.connect(self._add_item)
        duplicate_item_btn = QtWidgets.QPushButton("Duplicate Item")
        duplicate_item_btn.clicked.connect(self._duplicate_item)
        remove_item_btn = QtWidgets.QPushButton("Remove Item")
        remove_item_btn.clicked.connect(self._remove_item)
        for btn in (add_item_btn, duplicate_item_btn, remove_item_btn):
            items_buttons.addWidget(btn)
        items_panel.addLayout(items_buttons)
        items_split.addLayout(items_panel, stretch=1)

        detail_panel = QtWidgets.QVBoxLayout()
        detail_panel.addWidget(QtWidgets.QLabel("Item name (blank = use default template above)"))
        self.item_name_template_edit = QtWidgets.QLineEdit()
        self.item_name_template_edit.editingFinished.connect(self._refresh_preview)
        detail_panel.addWidget(self.item_name_template_edit)

        self.params_table = QtWidgets.QTableWidget(0, 3)
        self.params_table.setHorizontalHeaderLabels(["Parameter", "Kind", "Value"])
        self.params_table.horizontalHeader().setStretchLastSection(True)
        detail_panel.addWidget(self.params_table)

        param_buttons = QtWidgets.QHBoxLayout()
        add_param_btn = QtWidgets.QPushButton("Add Parameter")
        add_param_btn.clicked.connect(lambda: self._add_param_row())
        remove_param_btn = QtWidgets.QPushButton("Remove Parameter")
        remove_param_btn.clicked.connect(self._remove_selected_param_row)
        param_buttons.addWidget(add_param_btn)
        param_buttons.addWidget(remove_param_btn)
        detail_panel.addLayout(param_buttons)
        items_split.addLayout(detail_panel, stretch=2)

        layout.addLayout(items_split)

        preview_header = QtWidgets.QHBoxLayout()
        preview_header.addWidget(QtWidgets.QLabel("Preview"))
        refresh_btn = QtWidgets.QPushButton("Refresh Preview")
        refresh_btn.clicked.connect(self._refresh_preview)
        preview_header.addWidget(refresh_btn)
        preview_header.addStretch(1)
        layout.addLayout(preview_header)

        self.preview_table = QtWidgets.QTableWidget(0, 1)
        self.preview_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.preview_table)

        self.status_label = QtWidgets.QLabel("")
        layout.addWidget(self.status_label)

        export_group = QtWidgets.QGroupBox("Export")
        export_layout = QtWidgets.QVBoxLayout(export_group)

        selection_row = QtWidgets.QHBoxLayout()
        use_selection_btn = QtWidgets.QPushButton("Use Current Selection")
        use_selection_btn.clicked.connect(self._use_current_selection)
        selection_row.addWidget(use_selection_btn)
        self.selected_objects_label = QtWidgets.QLabel("(none selected)")
        selection_row.addWidget(self.selected_objects_label, stretch=1)
        export_layout.addLayout(selection_row)

        combine_row = QtWidgets.QHBoxLayout()
        self.combine_radio = QtWidgets.QRadioButton("Combine into one file")
        self.separate_radio = QtWidgets.QRadioButton("One file per object")
        self.separate_radio.setChecked(True)
        combine_row.addWidget(self.combine_radio)
        combine_row.addWidget(self.separate_radio)
        combine_row.addStretch(1)
        export_layout.addLayout(combine_row)

        folder_row = QtWidgets.QHBoxLayout()
        self.output_folder_edit = QtWidgets.QLineEdit()
        browse_btn = QtWidgets.QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_folder)
        folder_row.addWidget(QtWidgets.QLabel("Export folder"))
        folder_row.addWidget(self.output_folder_edit, stretch=1)
        folder_row.addWidget(browse_btn)
        export_layout.addLayout(folder_row)

        layout.addWidget(export_group)

        footer = QtWidgets.QHBoxLayout()
        save_btn = QtWidgets.QPushButton("Save")
        save_btn.clicked.connect(self._on_save)
        run_btn = QtWidgets.QPushButton("Run Export")
        run_btn.clicked.connect(self._on_run_export)
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(self.close)
        footer.addWidget(save_btn)
        footer.addWidget(run_btn)
        footer.addStretch(1)
        footer.addWidget(close_btn)
        layout.addLayout(footer)

    # -- Loading initial state --------------------------------------------

    def _load_from_config(self, config):
        self.base_name_edit.setText(config.base_name)
        self.naming_template_edit.setText(config.naming_template)
        index = self.varset_combo.findText(config.varset_object_name)
        if index >= 0:
            self.varset_combo.setCurrentIndex(index)

        self.items_list.clear()
        for item in self._items:
            self.items_list.addItem(self._item_label(item))
        if self._items:
            self.items_list.setCurrentRow(0)

        self._selected_object_names = list(config.export_settings.selected_object_names)
        self._update_selected_objects_label()
        self.combine_radio.setChecked(config.export_settings.combine)
        self.separate_radio.setChecked(not config.export_settings.combine)
        self.output_folder_edit.setText(config.export_settings.last_export_folder)

        self._refresh_preview()

    def _item_label(self, item):
        return item.name_template or "(uses default template)"

    # -- Item list management ---------------------------------------------

    def _on_item_selection_changed(self, current, previous):
        if previous is not None:
            previous_row = self.items_list.row(previous)
            if 0 <= previous_row < len(self._items):
                self._items[previous_row] = self._capture_item_from_widgets()
        if current is not None:
            row = self.items_list.row(current)
            self._apply_item_to_widgets(self._items[row])
        self._refresh_preview()

    def _add_item(self):
        new_item = GridItem(params={})
        self._items.append(new_item)
        self.items_list.addItem(self._item_label(new_item))
        self.items_list.setCurrentRow(len(self._items) - 1)

    def _duplicate_item(self):
        row = self.items_list.currentRow()
        if row < 0:
            return
        self._items[row] = self._capture_item_from_widgets()
        original = self._items[row]
        clone = GridItem(params=dict(original.params), name_template=original.name_template)
        self._items.insert(row + 1, clone)
        self.items_list.insertItem(row + 1, self._item_label(clone))
        self.items_list.setCurrentRow(row + 1)

    def _remove_item(self):
        row = self.items_list.currentRow()
        if row < 0:
            return
        if len(self._items) <= 1:
            QtWidgets.QMessageBox.warning(self, "GridParams", "At least one item is required.")
            return
        del self._items[row]
        self.items_list.takeItem(row)

    # -- Parameter table management ----------------------------------------

    def _apply_item_to_widgets(self, item):
        self.item_name_template_edit.setText(item.name_template or "")
        self.params_table.setRowCount(0)
        for name, value in item.params.items():
            kind, value_text = _describe_param_value(value)
            self._add_param_row(name, kind, value_text)

    def _capture_item_from_widgets(self):
        name_template = self.item_name_template_edit.text().strip() or None
        params = {}
        for row in range(self.params_table.rowCount()):
            name_widget = self.params_table.cellWidget(row, 0)
            param_name = name_widget.currentText().strip() if name_widget else ""
            if not param_name:
                continue
            kind_widget = self.params_table.cellWidget(row, 1)
            value_widget = self.params_table.cellWidget(row, 2)
            try:
                params[param_name] = _build_param_value(kind_widget.currentText(), value_widget.text())
            except ValueError:
                continue
        return GridItem(params=params, name_template=name_template)

    def _varset_property_names(self):
        varset = self.doc.getObject(self.varset_combo.currentText())
        return list(varset.PropertiesList) if varset is not None else []

    def _refresh_param_name_choices(self):
        choices = self._varset_property_names()
        for row in range(self.params_table.rowCount()):
            combo = self.params_table.cellWidget(row, 0)
            if combo is None:
                continue
            current = combo.currentText()
            combo.blockSignals(True)
            combo.clear()
            combo.addItems(choices)
            combo.setCurrentText(current)
            combo.blockSignals(False)

    def _add_param_row(self, name="", kind="Fixed", value_text=""):
        row = self.params_table.rowCount()
        self.params_table.insertRow(row)

        name_combo = QtWidgets.QComboBox()
        name_combo.setEditable(True)
        name_combo.addItems(self._varset_property_names())
        name_combo.setCurrentText(name)
        self.params_table.setCellWidget(row, 0, name_combo)

        kind_combo = QtWidgets.QComboBox()
        kind_combo.addItems(["Fixed", "List", "LinSpace", "Range"])
        kind_combo.setCurrentText(kind)
        self.params_table.setCellWidget(row, 1, kind_combo)

        value_edit = QtWidgets.QLineEdit(value_text)
        self.params_table.setCellWidget(row, 2, value_edit)

        def _update_placeholder(new_kind):
            value_edit.setPlaceholderText(_VALUE_PLACEHOLDERS.get(new_kind, ""))

        kind_combo.currentTextChanged.connect(_update_placeholder)
        _update_placeholder(kind)

    def _remove_selected_param_row(self):
        rows = sorted({index.row() for index in self.params_table.selectedIndexes()}, reverse=True)
        for row in rows:
            self.params_table.removeRow(row)
        self._refresh_preview()

    # -- Preview -------------------------------------------------------------

    def _build_config_from_widgets(self):
        current_row = self.items_list.currentRow()
        if 0 <= current_row < len(self._items):
            self._items[current_row] = self._capture_item_from_widgets()
        return GridConfig(
            base_name=self.base_name_edit.text(),
            varset_object_name=self.varset_combo.currentText(),
            naming_template=self.naming_template_edit.text() or "{base_name}",
            items=list(self._items),
            export_settings=ExportSettings(
                combine=self.combine_radio.isChecked(),
                selected_object_names=list(self._selected_object_names),
                last_export_folder=self.output_folder_edit.text(),
            ),
        )

    def _refresh_preview(self):
        try:
            config = self._build_config_from_widgets()
            variations = expand_config(config)
        except Exception as exc:
            self.preview_table.setRowCount(0)
            self.status_label.setText(f"Error: {exc}")
            return

        duplicates = set(find_duplicate_names(variations))
        param_keys = sorted({key for variation in variations for key in variation.params})

        self.preview_table.setColumnCount(1 + len(param_keys))
        self.preview_table.setHorizontalHeaderLabels(["Name"] + param_keys)
        self.preview_table.setRowCount(len(variations))
        for row, variation in enumerate(variations):
            name_item = QtWidgets.QTableWidgetItem(variation.name)
            if variation.name in duplicates:
                name_item.setBackground(QtGui.QColor("#c0392b"))
            self.preview_table.setItem(row, 0, name_item)
            for col, key in enumerate(param_keys, start=1):
                value_item = QtWidgets.QTableWidgetItem(str(variation.params.get(key, "")))
                self.preview_table.setItem(row, col, value_item)

        if duplicates:
            self.status_label.setText(
                f"{len(variations)} variation(s) -- DUPLICATE NAMES: {', '.join(sorted(duplicates))}"
            )
        else:
            self.status_label.setText(f"{len(variations)} variation(s)")

    # -- Export selection ------------------------------------------------

    def _use_current_selection(self):
        names = selection.get_selected_object_names()
        if not names:
            QtWidgets.QMessageBox.warning(self, "GridParams", "Nothing selected in the 3D view / tree.")
            return
        self._selected_object_names = names
        self._update_selected_objects_label()

    def _update_selected_objects_label(self):
        if not self._selected_object_names:
            self.selected_objects_label.setText("(none selected)")
            return
        labels = []
        for name in self._selected_object_names:
            obj = self.doc.getObject(name)
            labels.append(obj.Label if obj is not None else f"{name} (missing)")
        self.selected_objects_label.setText(", ".join(labels))

    def _browse_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select export folder", self.output_folder_edit.text()
        )
        if folder:
            self.output_folder_edit.setText(folder)

    # -- Save / Run --------------------------------------------------------

    def _on_save(self):
        config = self._build_config_from_widgets()
        persistence.save_config(self.doc, config)
        QtWidgets.QMessageBox.information(self, "GridParams", "Configuration saved to document.")

    def _on_run_export(self):
        config = self._build_config_from_widgets()
        variations = expand_config(config)
        duplicates = find_duplicate_names(variations)
        if duplicates:
            QtWidgets.QMessageBox.critical(
                self, "GridParams", f"Duplicate variation name(s): {', '.join(duplicates)}"
            )
            return
        if not config.export_settings.selected_object_names:
            QtWidgets.QMessageBox.critical(self, "GridParams", "Select at least one object to export first.")
            return
        output_folder = Path(self.output_folder_edit.text())
        if not output_folder.is_dir():
            QtWidgets.QMessageBox.critical(self, "GridParams", f"Export folder does not exist: {output_folder}")
            return

        persistence.save_config(self.doc, config)

        progress = QtWidgets.QProgressDialog(
            "Exporting variations...", "Cancel", 0, len(variations), self
        )
        progress.setWindowModality(QtCore.Qt.WindowModal)
        self.setEnabled(False)

        def on_progress(done, total):
            progress.setValue(done)
            QtWidgets.QApplication.processEvents()

        try:
            written = runner.run_export(self.doc, config, output_folder, progress_callback=on_progress)
        except Exception as exc:
            progress.close()
            self.setEnabled(True)
            message = f"Export failed: {exc}"
            written_so_far = getattr(exc, "written", None)
            if written_so_far:
                message += f"\n\n{len(written_so_far)} file(s) were already written before the failure."
            QtWidgets.QMessageBox.critical(self, "GridParams", message)
            return

        progress.close()
        self.setEnabled(True)
        QtWidgets.QMessageBox.information(
            self, "GridParams", f"Exported {len(written)} file(s) to {output_folder}"
        )
