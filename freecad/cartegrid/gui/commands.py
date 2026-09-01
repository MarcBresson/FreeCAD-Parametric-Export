import os

import FreeCAD as App
import FreeCADGui as Gui

from . import ICON_DIR

COMMAND_NAME = "CarteGrid_NewConfig"


class CmdNewCarteGridConfig:
    def GetResources(self):
        return {
            "MenuText": "Batch Export from Varset...",
            "ToolTip": "Create a new parameter grid over a VarSet and batch-export the resulting variations",
            "Pixmap": os.path.join(ICON_DIR, "favicon.svg"),
        }

    def IsActive(self):
        return App.ActiveDocument is not None

    def Activated(self):
        from . import persistence
        from .dialog import open_or_focus

        doc = App.ActiveDocument
        obj = persistence.create_config_object(doc)
        doc.recompute()

        open_or_focus(doc, obj.Name, parent=Gui.getMainWindow())


def register():
    Gui.addCommand(COMMAND_NAME, CmdNewCarteGridConfig())
