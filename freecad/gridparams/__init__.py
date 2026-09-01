"""Entry point for the addon (headless mode).

This file is loaded once during FreeCAD initialization if the addon is not disabled. It
runs in headless mode, so no Gui imports or calls are allowed here.

Keep this file fast -- it runs on every FreeCAD startup.
"""
