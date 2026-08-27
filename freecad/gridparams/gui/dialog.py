"""The GridParams dialog: build a parameter grid, preview resulting variations, and run export.

All expansion/naming/export-planning logic is delegated to gridparams.core -- this
module only translates between Qt widgets and that core's dataclasses.
"""

from PySide import QtCore, QtGui, QtWidgets

import FreeCAD as App
from freecad.gridparams.core.config import (
    ConfigSchemaError,
    ExportSettings,
    GridConfig,
    GridItem,
    expand_config,
)
from freecad.gridparams.core.values import Fixed, LinSpace, Range, ValueList
from freecad.gridparams.core.variation import find_duplicate_names
from freecad.gridparams.core.varset_export import VarSetCsvOptions

from . import export_helpers, persistence, selection, varset_export

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


_EXPORTABLE_BASE_TYPES = ("PartDesign::Body", "Part::Feature")


class VariationsDialog(QtWidgets.QDialog):
    """Read-only table of every expanded variation, with duplicate names highlighted."""

    def __init__(self, variations, duplicate_names, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Variations Preview")
        self.resize(600, 400)

        layout = QtWidgets.QVBoxLayout(self)
        param_keys = sorted(
            {key for variation in variations for key in variation.params}
        )
        table = QtWidgets.QTableWidget(len(variations), 1 + len(param_keys))
        table.setHorizontalHeaderLabels(["Name"] + param_keys)
        table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        for row, variation in enumerate(variations):
            name_item = QtWidgets.QTableWidgetItem(variation.name)
            if variation.name in duplicate_names:
                name_item.setBackground(QtGui.QColor("#c0392b"))
            table.setItem(row, 0, name_item)
            for col, key in enumerate(param_keys, start=1):
                table.setItem(
                    row,
                    col,
                    QtWidgets.QTableWidgetItem(str(variation.params.get(key, ""))),
                )
        layout.addWidget(table)

        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=QtCore.Qt.AlignRight)


class ObjectPickerDialog(QtWidgets.QDialog):
    """Pick bodies to add to the export list -- from a filtered list, or by typing any reference."""

    def __init__(self, doc, candidates, parent=None):
        super().__init__(parent)
        self.doc = doc
        self.setWindowTitle("Add Objects")
        self._resolved_manual_name = None

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("Solid/body objects in this document:"))

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        for obj in candidates:
            item = QtWidgets.QListWidgetItem(obj.Label)
            item.setData(QtCore.Qt.UserRole, obj.Name)
            self.list_widget.addItem(item)
        layout.addWidget(self.list_widget)

        manual_row = QtWidgets.QHBoxLayout()
        manual_row.addWidget(QtWidgets.QLabel("Or reference by name/label:"))
        self.manual_edit = QtWidgets.QLineEdit()
        self.manual_edit.setPlaceholderText(
            "e.g. Compound001 (bypasses the filter above)"
        )
        manual_row.addWidget(self.manual_edit, stretch=1)
        layout.addLayout(manual_row)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_accept(self):
        text = self.manual_edit.text().strip()
        if text:
            obj = self.doc.getObject(text) or next(
                iter(self.doc.getObjectsByLabel(text)), None
            )
            if obj is None:
                QtWidgets.QMessageBox.warning(
                    self, "GridParams", f"No object found named or labeled {text!r}."
                )
                return
            self._resolved_manual_name = obj.Name
        self.accept()

    def selected_names(self):
        names = [
            item.data(QtCore.Qt.UserRole) for item in self.list_widget.selectedItems()
        ]
        if self._resolved_manual_name and self._resolved_manual_name not in names:
            names.append(self._resolved_manual_name)
        return names


class GridParamsDialog(QtWidgets.QDialog):
    def __init__(self, doc, config_object_name, parent=None):
        super().__init__(parent)
        self.doc = doc
        self.config_object_name = config_object_name
        self._selected_object_names = []
        self._last_export_folder = ""
        self._csv_options = VarSetCsvOptions()
        self.resize(900, 650)

        config_obj = self._require_config_object()
        try:
            config = persistence.load_config(config_obj) or GridConfig(
                base_name=doc.Label
            )
        except ConfigSchemaError as exc:
            QtWidgets.QMessageBox.warning(
                self,
                "GridParams",
                f"Could not load saved grid configuration: {exc}\n\n"
                "Starting from a blank configuration instead -- the previously saved one is "
                "left untouched in the document until you explicitly Save over it.",
            )
            config = GridConfig(base_name=doc.Label)
        self._items = list(config.items)

        self.setWindowTitle(f"Grid Params Export — {config_obj.Label}")
        self._build_ui()
        self._load_from_config(config)

    def _require_config_object(self):
        obj = persistence.get_config_object(self.doc, self.config_object_name)
        if obj is None:
            raise RuntimeError(
                f"GridParams config object {self.config_object_name!r} no longer exists."
            )
        return obj

    # -- UI construction -------------------------------------------------

    def _make_separator(self):
        frame = QtWidgets.QFrame()
        frame.setFrameShape(QtWidgets.QFrame.HLine)
        frame.setFixedHeight(2)
        frame.setStyleSheet("QFrame { border: none; background-color: palette(mid); }")
        return frame

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
        self.varset_combo.currentTextChanged.connect(self._refresh_preview)
        self.base_name_edit.textChanged.connect(self._refresh_preview)
        self.naming_template_edit.textChanged.connect(self._refresh_preview)
        header_form.addRow("Base name", self.base_name_edit)
        header_form.addRow("Default naming template", self.naming_template_edit)
        varset_row = QtWidgets.QHBoxLayout()
        varset_row.addWidget(self.varset_combo, stretch=1)
        export_csv_btn = QtWidgets.QPushButton("Export VarSet to CSV...")
        export_csv_btn.clicked.connect(self._on_export_varset_csv)
        varset_row.addWidget(export_csv_btn)
        header_form.addRow("VarSet", varset_row)
        layout.addLayout(header_form)

        layout.addWidget(self._make_separator())

        items_split = QtWidgets.QHBoxLayout()

        items_panel = QtWidgets.QVBoxLayout()
        items_panel.addWidget(
            QtWidgets.QLabel("Grid items (one per configuration/version)")
        )
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
        detail_panel.addWidget(
            QtWidgets.QLabel(
                "Item naming template (blank = use default template above)"
            )
        )
        self.item_name_template_edit = QtWidgets.QLineEdit()
        self.item_name_template_edit.setPlaceholderText("{base_name} - {ParamName}")
        self.item_name_template_edit.textChanged.connect(self._refresh_preview)
        self.item_name_template_edit.textChanged.connect(
            self._on_item_name_template_changed
        )
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

        status_row = QtWidgets.QHBoxLayout()
        self.status_label = QtWidgets.QLabel("")
        status_row.addWidget(self.status_label)
        show_variations_btn = QtWidgets.QPushButton("Show Variations")
        show_variations_btn.clicked.connect(self._show_variations_dialog)
        status_row.addWidget(show_variations_btn)
        status_row.addStretch(1)
        layout.addLayout(status_row)

        layout.addWidget(self._make_separator())

        export_group = QtWidgets.QGroupBox("Export")
        export_layout = QtWidgets.QVBoxLayout(export_group)

        self.objects_table = QtWidgets.QTableWidget(0, 1)
        self.objects_table.setHorizontalHeaderLabels(["Object"])
        self.objects_table.horizontalHeader().setStretchLastSection(True)
        self.objects_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.objects_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        export_layout.addWidget(self.objects_table)

        objects_buttons = QtWidgets.QHBoxLayout()
        add_objects_btn = QtWidgets.QPushButton("+")
        add_objects_btn.clicked.connect(self._add_objects)
        remove_objects_btn = QtWidgets.QPushButton("-")
        remove_objects_btn.clicked.connect(self._remove_selected_objects)
        from_selection_btn = QtWidgets.QPushButton("From Selection")
        from_selection_btn.clicked.connect(self._use_current_selection)
        objects_buttons.addWidget(add_objects_btn)
        objects_buttons.addWidget(remove_objects_btn)
        objects_buttons.addWidget(from_selection_btn)
        objects_buttons.addStretch(1)
        export_layout.addLayout(objects_buttons)

        multi_part_tooltip = (
            "Controls how a variation is exported when it includes more than one part.\n"
            '"Combine parts into one file" merges all of the variation\'s parts into a '
            "single output file.\n"
            '"One file per part" exports each part as its own file, using the part\'s '
            "body label (see below) to keep the filenames unique."
        )

        self.multi_part_row_widget = QtWidgets.QWidget()
        multi_part_row = QtWidgets.QHBoxLayout(self.multi_part_row_widget)
        multi_part_row.setContentsMargins(0, 0, 0, 0)

        multi_part_label = QtWidgets.QLabel("Multi part export per variation:")
        multi_part_label.setToolTip(multi_part_tooltip)
        multi_part_info_btn = QtWidgets.QToolButton()
        multi_part_info_btn.setIcon(
            self.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxInformation)
        )
        multi_part_info_btn.setAutoRaise(True)
        multi_part_info_btn.setToolTip(multi_part_tooltip)

        self.multi_part_combo = QtWidgets.QComboBox()
        self.multi_part_combo.addItems(
            ["Combine parts into one file", "One file per part"]
        )
        self.multi_part_combo.setCurrentIndex(1)

        multi_part_row.addWidget(multi_part_label)
        multi_part_row.addWidget(multi_part_info_btn)
        multi_part_row.addWidget(self.multi_part_combo)
        multi_part_row.addStretch(1)
        export_layout.addWidget(self.multi_part_row_widget)

        self.body_name_row_widget = QtWidgets.QWidget()
        body_name_row = QtWidgets.QHBoxLayout(self.body_name_row_widget)
        body_name_row.setContentsMargins(0, 0, 0, 0)
        body_name_row.addSpacing(20)
        self.prepend_body_radio = QtWidgets.QRadioButton(
            "Prepend body label to exported variation names"
        )
        self.append_body_radio = QtWidgets.QRadioButton(
            "Append body label to exported variation names"
        )
        self.append_body_radio.setChecked(True)
        self.body_name_group = QtWidgets.QButtonGroup(self)
        self.body_name_group.addButton(self.prepend_body_radio)
        self.body_name_group.addButton(self.append_body_radio)
        body_name_row.addWidget(self.prepend_body_radio)
        body_name_row.addWidget(self.append_body_radio)
        body_name_row.addStretch(1)
        export_layout.addWidget(self.body_name_row_widget)

        self.multi_part_combo.currentIndexChanged.connect(
            self._update_body_name_radios_enabled
        )
        self._update_body_name_radios_enabled()

        layout.addWidget(export_group)

        footer = QtWidgets.QHBoxLayout()
        save_btn = QtWidgets.QPushButton("Save")
        save_btn.clicked.connect(self._on_save)
        save_close_btn = QtWidgets.QPushButton("Save and Close")
        save_close_btn.clicked.connect(self._on_save_and_close)
        run_btn = QtWidgets.QPushButton("Export")
        run_btn.clicked.connect(self._on_run_export)
        export_to_btn = QtWidgets.QPushButton("Export to...")
        export_to_btn.setToolTip(
            "Pick a folder and export all variations there directly."
        )
        export_to_btn.clicked.connect(self._on_export_to_folder)
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(self.close)
        footer.addWidget(save_btn)
        footer.addWidget(save_close_btn)
        footer.addWidget(run_btn)
        footer.addWidget(export_to_btn)
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
        for index, item in enumerate(self._items):
            self.items_list.addItem(self._item_label(index, item))
        if self._items:
            self.items_list.setCurrentRow(0)

        self._selected_object_names = list(config.export_settings.selected_object_names)
        self._last_export_folder = config.export_settings.last_export_folder
        self._refresh_objects_table()
        self.multi_part_combo.setCurrentIndex(
            0 if config.export_settings.combine else 1
        )
        if config.export_settings.body_name_placement == "prepend":
            self.prepend_body_radio.setChecked(True)
        else:
            self.append_body_radio.setChecked(True)
        self._update_body_name_radios_enabled()

        self._csv_options = VarSetCsvOptions(
            include_value=config.export_settings.csv_include_value,
            include_unit=config.export_settings.csv_include_unit,
            include_freecad_unit=config.export_settings.csv_include_freecad_unit,
            include_group=config.export_settings.csv_include_group,
            include_comment=config.export_settings.csv_include_comment,
            include_private=config.export_settings.csv_include_private,
        )

        self._refresh_preview()

    def _item_label(self, index, item):
        return self._format_item_label(index, item.name_template)

    def _format_item_label(self, index, name_template):
        return f"{index + 1}. {name_template or '(uses default template)'}"

    def _on_item_name_template_changed(self, text):
        row = self.items_list.currentRow()
        if 0 <= row < self.items_list.count():
            self.items_list.item(row).setText(
                self._format_item_label(row, text.strip() or None)
            )

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

    def _renumber_items(self):
        for index in range(self.items_list.count()):
            self.items_list.item(index).setText(
                self._item_label(index, self._items[index])
            )

    def _add_item(self):
        new_item = GridItem(params={})
        self._items.append(new_item)
        self.items_list.addItem(self._item_label(len(self._items) - 1, new_item))
        self.items_list.setCurrentRow(len(self._items) - 1)
        self._refresh_preview()

    def _duplicate_item(self):
        row = self.items_list.currentRow()
        if row < 0:
            return
        self._items[row] = self._capture_item_from_widgets()
        original = self._items[row]
        clone = GridItem(
            params=dict(original.params), name_template=original.name_template
        )
        self._items.insert(row + 1, clone)
        self.items_list.insertItem(row + 1, self._item_label(row + 1, clone))
        self._renumber_items()
        self.items_list.setCurrentRow(row + 1)
        self._refresh_preview()

    def _remove_item(self):
        row = self.items_list.currentRow()
        if row < 0:
            return
        if len(self._items) <= 1:
            QtWidgets.QMessageBox.warning(
                self, "GridParams", "At least one item is required."
            )
            return
        del self._items[row]
        self.items_list.takeItem(row)
        self._renumber_items()
        self._refresh_preview()

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
                params[param_name] = _build_param_value(
                    kind_widget.currentText(), value_widget.text()
                )
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
        name_combo.currentTextChanged.connect(self._refresh_preview)
        self.params_table.setCellWidget(row, 0, name_combo)

        kind_combo = QtWidgets.QComboBox()
        kind_combo.addItems(["Fixed", "List", "LinSpace", "Range"])
        kind_combo.setCurrentText(kind)
        kind_combo.currentTextChanged.connect(self._refresh_preview)
        self.params_table.setCellWidget(row, 1, kind_combo)

        value_edit = QtWidgets.QLineEdit(value_text)
        value_edit.textChanged.connect(self._refresh_preview)
        self.params_table.setCellWidget(row, 2, value_edit)

        def _update_placeholder(new_kind):
            value_edit.setPlaceholderText(_VALUE_PLACEHOLDERS.get(new_kind, ""))

        kind_combo.currentTextChanged.connect(_update_placeholder)
        _update_placeholder(kind)
        self._refresh_preview()

    def _remove_selected_param_row(self):
        rows = sorted(
            {index.row() for index in self.params_table.selectedIndexes()}, reverse=True
        )
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
                combine=self.multi_part_combo.currentIndex() == 0,
                selected_object_names=list(self._selected_object_names),
                last_export_folder=self._last_export_folder,
                body_name_placement="prepend"
                if self.prepend_body_radio.isChecked()
                else "append",
                csv_include_value=self._csv_options.include_value,
                csv_include_unit=self._csv_options.include_unit,
                csv_include_freecad_unit=self._csv_options.include_freecad_unit,
                csv_include_group=self._csv_options.include_group,
                csv_include_comment=self._csv_options.include_comment,
                csv_include_private=self._csv_options.include_private,
            ),
        )

    def _refresh_preview(self):
        try:
            config = self._build_config_from_widgets()
            variations = expand_config(config, document_label=self.doc.Label)
        except Exception as exc:
            self.status_label.setText(f"Error: {exc}")
            return

        if find_duplicate_names(variations):
            self.status_label.setText("Duplicated names for some variations")
        else:
            self.status_label.setText(f"{len(variations)} variation(s)")

    def _show_variations_dialog(self):
        try:
            config = self._build_config_from_widgets()
            variations = expand_config(config, document_label=self.doc.Label)
        except Exception as exc:
            QtWidgets.QMessageBox.critical(self, "GridParams", f"Error: {exc}")
            return
        duplicates = set(find_duplicate_names(variations))
        VariationsDialog(variations, duplicates, self).exec()

    # -- Export selection ------------------------------------------------

    def _use_current_selection(self):
        names = selection.get_selected_object_names()
        if not names:
            QtWidgets.QMessageBox.warning(
                self, "GridParams", "Nothing selected in the 3D view / tree."
            )
            return
        self._selected_object_names = names
        self._refresh_objects_table()

    def _refresh_objects_table(self):
        self.objects_table.setRowCount(len(self._selected_object_names))
        for row, name in enumerate(self._selected_object_names):
            obj = self.doc.getObject(name)
            label = obj.Label if obj is not None else f"{name} (missing)"
            self.objects_table.setItem(row, 0, QtWidgets.QTableWidgetItem(label))
        self._update_multi_part_visibility()

    def _update_multi_part_visibility(self):
        self.multi_part_row_widget.setVisible(len(self._selected_object_names) > 1)
        self._update_body_name_radios_enabled()

    def _add_objects(self):
        existing = set(self._selected_object_names)
        candidates = [
            obj
            for obj in self.doc.Objects
            if obj.Name not in existing
            and not persistence.is_config_object(obj)
            and any(obj.isDerivedFrom(t) for t in _EXPORTABLE_BASE_TYPES)
        ]
        picker = ObjectPickerDialog(self.doc, candidates, self)
        if picker.exec() == QtWidgets.QDialog.Accepted:
            for name in picker.selected_names():
                if name not in self._selected_object_names:
                    self._selected_object_names.append(name)
            self._refresh_objects_table()

    def _remove_selected_objects(self):
        rows = sorted(
            {index.row() for index in self.objects_table.selectedIndexes()},
            reverse=True,
        )
        for row in rows:
            del self._selected_object_names[row]
        self._refresh_objects_table()

    def _update_body_name_radios_enabled(self):
        show = (
            len(self._selected_object_names) > 1
            and self.multi_part_combo.currentIndex() == 1
        )
        self.body_name_row_widget.setVisible(show)
        self.prepend_body_radio.setEnabled(show)
        self.append_body_radio.setEnabled(show)

    def _on_export_varset_csv(self):
        varset = self.doc.getObject(self.varset_combo.currentText())
        if varset is None:
            QtWidgets.QMessageBox.warning(
                self, "GridParams", "Select a VarSet to export first."
            )
            return
        properties = varset_export.collect_properties(varset)
        default_folder = export_helpers.compute_output_folder(self.doc)
        csv_dialog = varset_export.VarSetCsvExportDialog(
            varset,
            properties,
            self._csv_options,
            default_folder=str(default_folder) if default_folder else "",
            parent=self,
        )
        if csv_dialog.exec() == QtWidgets.QDialog.Accepted:
            self._csv_options = csv_dialog.options

    # -- Save / Run --------------------------------------------------------

    def _save_config(self):
        config = self._build_config_from_widgets()
        persistence.save_config(self._require_config_object(), config)

    def _on_save(self):
        self._save_config()
        QtWidgets.QMessageBox.information(
            self, "GridParams", "Configuration saved to document."
        )

    def _on_save_and_close(self):
        self._save_config()
        self.close()

    def closeEvent(self, event):
        _open_dialogs.pop((self.doc.Name, self.config_object_name), None)
        super().closeEvent(event)

    def _multi_part_choice_is_valid(self):
        if self.multi_part_combo.currentIndex() == 1 and not (
            self.prepend_body_radio.isChecked() or self.append_body_radio.isChecked()
        ):
            QtWidgets.QMessageBox.critical(
                self,
                "GridParams",
                "Choose whether to prepend or append the body label when exporting one file per object.",
            )
            return False
        return True

    def _on_run_export(self):
        config = self._build_config_from_widgets()
        if not self._multi_part_choice_is_valid():
            return

        persistence.save_config(self._require_config_object(), config)
        export_helpers.run_export_with_progress(
            self.doc, config, parent=self, disable_widget=self
        )

    def _on_export_to_folder(self):
        config = self._build_config_from_widgets()
        if not self._multi_part_choice_is_valid():
            return

        export_helpers.export_to_folder_with_progress(
            self.doc, config, parent=self, disable_widget=self
        )
        self._last_export_folder = config.export_settings.last_export_folder
        persistence.save_config(self._require_config_object(), config)


# -- Open-dialog tracking --------------------------------------------------
#
# Keeps at most one GridParamsDialog per (document, config object) so that
# double-clicking/re-invoking the same config brings the existing dialog to
# front instead of opening a conflicting duplicate, and so that closing a
# document can close whichever of its dialogs are still open.

_open_dialogs: dict[tuple[str, str], GridParamsDialog] = {}
_document_observer_registered = False


class _DocumentCloseObserver:
    def slotDeletedDocument(self, doc):
        _close_dialogs_for_document(doc.Name)


def _close_dialogs_for_document(doc_name):
    for key in [key for key in _open_dialogs if key[0] == doc_name]:
        dialog = _open_dialogs.pop(key, None)
        if dialog is not None:
            try:
                dialog.close()
            except RuntimeError:
                pass  # underlying Qt widget was already destroyed


def _ensure_document_observer_registered():
    global _document_observer_registered
    if not _document_observer_registered:
        App.addDocumentObserver(_DocumentCloseObserver())
        _document_observer_registered = True


def open_or_focus(doc, config_object_name, parent=None):
    """Show the GridParamsDialog for (doc, config_object_name).

    Reuses and raises an already-open dialog for the same config object instead of
    opening a second, conflicting one.
    """
    _ensure_document_observer_registered()
    key = (doc.Name, config_object_name)
    existing = _open_dialogs.get(key)
    if existing is not None:
        try:
            existing.setWindowState(existing.windowState() & ~QtCore.Qt.WindowMinimized)
            existing.show()
            existing.raise_()
            existing.activateWindow()
            return existing
        except RuntimeError:
            _open_dialogs.pop(key, None)  # underlying Qt widget was already destroyed

    dialog = GridParamsDialog(doc, config_object_name, parent=parent)
    _open_dialogs[key] = dialog
    dialog.show()
    return dialog
