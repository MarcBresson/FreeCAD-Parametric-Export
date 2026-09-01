"""Collect an App::VarSet's properties and let the user export them to a CSV file for
documentation purposes. Ported from a one-off macro that dumped name/value/unit/comment.
"""

from pathlib import Path

from PySide import QtWidgets

from freecad.cartegrid.core.varset_export import (
    PropertyInfo,
    VarSetCsvOptions,
    filter_properties,
    to_csv_text,
)

_SKIPPED_PROPERTIES = {"ExpressionEngine", "Label", "Label2"}


def _describe_unit(unit_):
    if unit_ == "":
        return ""
    if unit_.Type == "Length":
        return str(unit_).split(" ")[1]
    return unit_


def _describe_comment(varset, prop_name):
    try:
        doc = varset.getDocumentationOfProperty(prop_name)
    except AttributeError:
        return ""
    if not doc:
        return ""
    if isinstance(doc, (list, tuple)):
        return "; ".join(str(part) for part in doc if part)
    return str(doc)


def _describe_group(varset, prop_name):
    try:
        group = varset.getGroupOfProperty(prop_name)
    except AttributeError:
        return ""
    return group or ""


def collect_properties(varset) -> list[PropertyInfo]:
    properties = []
    for prop_name in varset.PropertiesList:
        if prop_name in _SKIPPED_PROPERTIES:
            continue
        prop = varset.getPropertyByName(prop_name)
        if hasattr(prop, "Value"):
            value = prop.Value
            freecad_unit = getattr(prop, "Unit", "")
            unit = _describe_unit(freecad_unit)
        else:
            value = prop
            freecad_unit = ""
            unit = ""
        properties.append(
            PropertyInfo(
                name=prop_name,
                value=value,
                unit=unit,
                freecad_unit=freecad_unit,
                group=_describe_group(varset, prop_name),
                comment=_describe_comment(varset, prop_name),
            )
        )
    return properties


class VarSetCsvExportDialog(QtWidgets.QDialog):
    """Checkboxes for which columns/variables to include, then a save-file prompt."""

    def __init__(self, varset, properties, options, default_folder="", parent=None):
        super().__init__(parent)
        self.varset = varset
        self.properties = properties
        self.options = options
        self._default_folder = default_folder
        self.setWindowTitle(f"Export VarSet to CSV — {varset.Label}")

        layout = QtWidgets.QVBoxLayout(self)

        self.value_check = QtWidgets.QCheckBox("Include Value column")
        self.value_check.setChecked(options.include_value)
        self.unit_check = QtWidgets.QCheckBox("Include Unit column")
        self.unit_check.setChecked(options.include_unit)
        self.freecad_unit_check = QtWidgets.QCheckBox(
            "Include FreeCAD Unit column (raw)"
        )
        self.freecad_unit_check.setChecked(options.include_freecad_unit)
        self.group_check = QtWidgets.QCheckBox("Include Group column")
        self.group_check.setChecked(options.include_group)
        self.comment_check = QtWidgets.QCheckBox("Include Comment column")
        self.comment_check.setChecked(options.include_comment)
        self.private_check = QtWidgets.QCheckBox(
            "Include private variables (name or group starting with _)"
        )
        self.private_check.setChecked(options.include_private)
        for check in (
            self.value_check,
            self.unit_check,
            self.freecad_unit_check,
            self.group_check,
            self.comment_check,
            self.private_check,
        ):
            layout.addWidget(check)

        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Cancel)
        export_btn = buttons.addButton(
            "Export...", QtWidgets.QDialogButtonBox.AcceptRole
        )
        export_btn.clicked.connect(self._on_export)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _current_options(self):
        return VarSetCsvOptions(
            include_value=self.value_check.isChecked(),
            include_unit=self.unit_check.isChecked(),
            include_freecad_unit=self.freecad_unit_check.isChecked(),
            include_group=self.group_check.isChecked(),
            include_comment=self.comment_check.isChecked(),
            include_private=self.private_check.isChecked(),
        )

    def _on_export(self):
        self.options = self._current_options()
        default_path = str(
            Path(self._default_folder or "") / f"{self.varset.Label}_parameters.csv"
        )
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export VarSet to CSV", default_path, "CSV Files (*.csv)"
        )
        if not path:
            return
        try:
            Path(path).write_text(
                to_csv_text(self.properties, self.options), encoding="utf-8"
            )
        except OSError as exc:
            QtWidgets.QMessageBox.critical(
                self, "CarteGrid", f"Could not write CSV file: {exc}"
            )
            return

        exported_count = len(filter_properties(self.properties, self.options))
        QtWidgets.QMessageBox.information(
            self, "CarteGrid", f"Exported {exported_count} parameter(s) to {path}"
        )
        self.accept()
