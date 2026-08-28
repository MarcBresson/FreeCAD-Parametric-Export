import FreeCADGui as Gui

from freecad.gridparams.gui import commands, preferences
from freecad.gridparams.gui.manipulator import GridParamsManipulator

commands.register()
Gui.addWorkbenchManipulator(GridParamsManipulator())
Gui.addPreferencePage(preferences.GridParamsPreferencesPage, "Grid Params Export")
