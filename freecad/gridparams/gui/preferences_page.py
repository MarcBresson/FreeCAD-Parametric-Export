"""The Qt preferences page (Edit > Preferences > Grid Params Export), registered with
FreeCADGui.addPreferencePage. Split from `preferences.py` so the getters/setters/format
resolution there can be imported and tested without a Qt installation."""

from PySide import QtCore, QtWidgets

from . import format_registry, preferences


class GridParamsPreferencesPage(QtWidgets.QWidget):
    """Registered with FreeCADGui.addPreferencePage; must implement loadSettings/saveSettings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QFormLayout(self)

        self.relative_path_edit = QtWidgets.QLineEdit()
        tooltip = (
            "Grid exports are written here, resolved relative to each FreeCAD document's "
            "own folder.\n"
            "Leave empty to export next to the document.\n"
            "This applies to every document -- no export path is stored inside .FCStd files."
        )
        self.relative_path_edit.setToolTip(tooltip)
        self.relative_path_edit.setPlaceholderText(
            "Same folder as the FreeCAD document"
        )
        label = QtWidgets.QLabel("Grid export relative path")
        label.setToolTip(tooltip)
        layout.addRow(label, self.relative_path_edit)

        self.preferred_formats_list = QtWidgets.QListWidget()
        self.preferred_formats_list.setToolTip(
            "Formats used whenever a grid item doesn't specify its own. Select one or more --"
            " every checked format is exported."
        )
        self.preferred_formats_list.setFixedHeight(140)
        for option in format_registry.list_available_formats():
            item = QtWidgets.QListWidgetItem(option.label)
            item.setData(QtCore.Qt.UserRole, option.id)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.preferred_formats_list.addItem(item)
        layout.addRow(
            QtWidgets.QLabel("Preferred formats"), self.preferred_formats_list
        )

        self.allow_per_item_checkbox = QtWidgets.QCheckBox(
            "Allow choosing export formats per grid item"
        )
        self.allow_per_item_checkbox.setToolTip(
            "When checked, the Grid Params dialog shows a per-item format picker that "
            "overrides the preferred formats above for that item."
        )
        layout.addRow(self.allow_per_item_checkbox)

        self.enforce_preferred_checkbox = QtWidgets.QCheckBox(
            "Enforce preferred formats for every export"
        )
        self.enforce_preferred_checkbox.setToolTip(
            "When checked, the preferred formats above are always used, ignoring any "
            "per-item override."
        )
        layout.addRow(self.enforce_preferred_checkbox)

    def loadSettings(self):
        self.relative_path_edit.setText(preferences.get_export_relative_path())

        preferred = set(preferences.get_preferred_formats())
        for row in range(self.preferred_formats_list.count()):
            item = self.preferred_formats_list.item(row)
            checked = item.data(QtCore.Qt.UserRole) in preferred
            item.setCheckState(QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked)

        self.allow_per_item_checkbox.setChecked(
            preferences.get_allow_per_item_formats()
        )
        self.enforce_preferred_checkbox.setChecked(
            preferences.get_enforce_preferred_formats()
        )

    def saveSettings(self):
        preferences.set_export_relative_path(self.relative_path_edit.text())

        formats = [
            self.preferred_formats_list.item(row).data(QtCore.Qt.UserRole)
            for row in range(self.preferred_formats_list.count())
            if self.preferred_formats_list.item(row).checkState() == QtCore.Qt.Checked
        ]
        preferences.set_preferred_formats(formats)
        preferences.set_allow_per_item_formats(self.allow_per_item_checkbox.isChecked())
        preferences.set_enforce_preferred_formats(
            self.enforce_preferred_checkbox.isChecked()
        )
