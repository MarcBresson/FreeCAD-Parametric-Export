"""Tree behavior for a GridParams config container: double-click to edit, right-click to
edit or run its saved export directly."""

import os

import FreeCADGui as Gui

from freecad.gridparams import ICON_DIR
from freecad.gridparams.core.config import ConfigSchemaError

from . import persistence


class ConfigContainerViewProxy:
    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def getIcon(self):
        return os.path.join(ICON_DIR, "gridparams.svg")

    def doubleClicked(self, vobj):
        _edit_config(vobj.Object)
        return True

    def setupContextMenu(self, vobj, menu):
        edit_action = menu.addAction("Edit...")
        edit_action.triggered.connect(lambda: _edit_config(vobj.Object))
        export_action = menu.addAction("Export using config")
        export_action.triggered.connect(lambda: _export_using_config(vobj.Object))

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


def _edit_config(obj):
    from .dialog import GridParamsDialog

    dialog = GridParamsDialog(obj.Document, obj.Name, parent=Gui.getMainWindow())
    dialog.show()


def _export_using_config(obj):
    from PySide6 import QtWidgets

    from . import export_helpers

    try:
        config = persistence.load_config(obj)
    except ConfigSchemaError as exc:
        QtWidgets.QMessageBox.critical(Gui.getMainWindow(), "GridParams", f"Could not load config: {exc}")
        return
    if config is None:
        QtWidgets.QMessageBox.warning(
            Gui.getMainWindow(), "GridParams", "Nothing saved yet -- open Edit and Save first."
        )
        return
    export_helpers.run_export_with_progress(obj.Document, config, parent=Gui.getMainWindow())
