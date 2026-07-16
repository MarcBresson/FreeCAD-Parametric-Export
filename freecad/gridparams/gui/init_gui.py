import os

import FreeCADGui as Gui

from freecad.gridparams import ICON_DIR


class GridParamsWorkbench(Gui.Workbench):
    MenuText = "Grid Params Export"
    ToolTip = (
        "Batch-export parametric model variations driven by a VarSet parameter grid"
    )
    Icon = os.path.join(ICON_DIR, "gridparams.svg")

    def Initialize(self):
        from . import commands

        commands.register()
        self.appendToolbar("Grid Params Export", [commands.COMMAND_NAME])
        self.appendMenu("Grid Params Export", [commands.COMMAND_NAME])

    def GetClassName(self):
        return "Gui::PythonWorkbench"
