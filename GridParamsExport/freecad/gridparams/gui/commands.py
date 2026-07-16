import os

import FreeCAD as App
import FreeCADGui as Gui

from freecad.gridparams import ICON_DIR

COMMAND_NAME = "GridParamsExport_NewConfig"


class CmdNewGridParamsConfig:
    def GetResources(self):
        return {
            "MenuText": "New Grid Export Config...",
            "ToolTip": "Create a new parameter grid over a VarSet and batch-export the resulting variations",
            "Pixmap": os.path.join(ICON_DIR, "gridparams.svg"),
        }

    def IsActive(self):
        return App.ActiveDocument is not None

    def Activated(self):
        from . import persistence
        from .dialog import GridParamsDialog

        doc = App.ActiveDocument
        obj = persistence.create_config_object(doc)
        doc.recompute()

        dialog = GridParamsDialog(doc, obj.Name, parent=Gui.getMainWindow())
        dialog.show()


def register():
    Gui.addCommand(COMMAND_NAME, CmdNewGridParamsConfig())
