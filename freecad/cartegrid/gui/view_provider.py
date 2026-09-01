"""Tree behavior for a CarteGrid config container: double-click to edit, right-click to
edit or run its saved export directly."""

import os

import FreeCADGui as Gui

from freecad.cartegrid.core.config import ConfigSchemaError

from . import ICON_DIR, persistence


class ConfigContainerViewProxy:
    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def getIcon(self):
        return os.path.join(ICON_DIR, "favicon.svg")

    def doubleClicked(self, vobj):
        _edit_config(vobj.Object)
        return True

    def setupContextMenu(self, vobj, menu):
        edit_action = menu.addAction("Edit...")
        edit_action.triggered.connect(lambda: _edit_config(vobj.Object))
        export_action = menu.addAction("Export using config")
        export_action.triggered.connect(lambda: _export_using_config(vobj.Object))
        export_to_action = menu.addAction("Export to...")
        export_to_action.triggered.connect(lambda: _export_to_folder(vobj.Object))

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


def _edit_config(obj):
    from .dialog import open_or_focus

    open_or_focus(obj.Document, obj.Name, parent=Gui.getMainWindow())


def _export_using_config(obj):
    from PySide import QtWidgets

    from . import export_helpers

    try:
        config = persistence.load_config(obj)
    except ConfigSchemaError as exc:
        QtWidgets.QMessageBox.critical(
            Gui.getMainWindow(), "CarteGrid", f"Could not load config: {exc}"
        )
        return
    if config is None:
        QtWidgets.QMessageBox.warning(
            Gui.getMainWindow(),
            "CarteGrid",
            "Nothing saved yet -- open Edit and Save first.",
        )
        return
    export_helpers.run_export_with_progress(
        obj.Document, config, parent=Gui.getMainWindow()
    )


def _export_to_folder(obj):
    from PySide import QtWidgets

    from . import export_helpers

    try:
        config = persistence.load_config(obj)
    except ConfigSchemaError as exc:
        QtWidgets.QMessageBox.critical(
            Gui.getMainWindow(), "CarteGrid", f"Could not load config: {exc}"
        )
        return
    if config is None:
        QtWidgets.QMessageBox.warning(
            Gui.getMainWindow(),
            "CarteGrid",
            "Nothing saved yet -- open Edit and Save first.",
        )
        return
    export_helpers.export_to_folder_with_progress(
        obj.Document, config, parent=Gui.getMainWindow()
    )
    persistence.save_config(obj, config)
