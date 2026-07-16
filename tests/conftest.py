"""Stub the real FreeCAD/FreeCADGui modules so gui/* code can be imported and unit-tested
without a full FreeCAD installation."""

import sys
import types

for _name in ("FreeCAD", "FreeCADGui"):
    sys.modules.setdefault(_name, types.ModuleType(_name))
