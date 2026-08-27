"""Global add-on preferences (Edit > Preferences > Grid Params Export).

The export folder used to be a per-document setting typed into the export dialog and saved
inside the .FCStd file, which meant an absolute (or even relative) filesystem path could leak
into a shared document. It's now a single add-on-wide preference: a path always resolved
relative to the FreeCAD document's own folder, and never written to any document.
"""

from PySide import QtWidgets

import FreeCAD as App

PARAM_GROUP = "User parameter:BaseApp/Preferences/Mod/GridParams"
EXPORT_RELATIVE_PATH_KEY = "ExportRelativePath"


def get_export_relative_path() -> str:
    return App.ParamGet(PARAM_GROUP).GetString(EXPORT_RELATIVE_PATH_KEY, "")


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

    def loadSettings(self):
        self.relative_path_edit.setText(get_export_relative_path())

    def saveSettings(self):
        App.ParamGet(PARAM_GROUP).SetString(
            EXPORT_RELATIVE_PATH_KEY, self.relative_path_edit.text()
        )
