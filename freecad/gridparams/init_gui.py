import FreeCADGui as Gui

from freecad.gridparams.gui import ICON_DIR, commands, preferences_page
from freecad.gridparams.gui.manipulator import GridParamsManipulator

commands.register()
Gui.addWorkbenchManipulator(GridParamsManipulator())
# FreeCAD looks up a preference group's icon as "preferences-<group, lowercased, spaces
# turned into underscores>.svg" -- see Resources/icons/preferences-grid_params_export.svg
# (src/Gui/DlgPreferencesImp.cpp, DlgPreferencesImp::setupPages).
Gui.addIconPath(ICON_DIR)
Gui.addPreferencePage(preferences_page.GridParamsPreferencesPage, "Grid Params Export")
