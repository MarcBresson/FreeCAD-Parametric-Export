import FreeCADGui as Gui

from freecad.gridparams.gui import commands, preferences_page
from freecad.gridparams.gui.manipulator import GridParamsManipulator

commands.register()
Gui.addWorkbenchManipulator(GridParamsManipulator())
Gui.addPreferencePage(preferences_page.GridParamsPreferencesPage, "Grid Params Export")
