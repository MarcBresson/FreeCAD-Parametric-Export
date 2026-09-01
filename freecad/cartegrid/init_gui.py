import FreeCADGui as Gui

from freecad.cartegrid.gui import ICON_DIR, commands, preferences_page
from freecad.cartegrid.gui.manipulator import CarteGridManipulator

commands.register()
Gui.addWorkbenchManipulator(CarteGridManipulator())
# FreeCAD looks up a preference group's icon as "preferences-<group, lowercased, spaces
# turned into underscores>.svg" -- see Resources/icons/preferences-cartegrid.svg
# (src/Gui/DlgPreferencesImp.cpp, DlgPreferencesImp::setupPages).
Gui.addIconPath(ICON_DIR)
Gui.addPreferencePage(preferences_page.CarteGridPreferencesPage, "CarteGrid")
