import os

import FreeCAD as App
import FreeCADGui as Gui

from freecad.gridparams import ICON_DIR

COMMAND_NAME = "GridParamsExport_OpenDialog"


class CmdOpenGridParamsDialog:
    def GetResources(self):
        return {
            "MenuText": "Grid Export...",
            "ToolTip": "Define a parameter grid over a VarSet and batch-export the resulting variations",
            "Pixmap": os.path.join(ICON_DIR, "gridparams.svg"),
        }

    def IsActive(self):
        return App.ActiveDocument is not None

    def Activated(self):
        from .dialog import GridParamsDialog

        dialog = GridParamsDialog(App.ActiveDocument, parent=Gui.getMainWindow())
        dialog.show()


def register():
    Gui.addCommand(COMMAND_NAME, CmdOpenGridParamsDialog())
