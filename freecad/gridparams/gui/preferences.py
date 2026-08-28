"""Global add-on preferences (Edit > Preferences > Grid Params Export).

The export folder used to be a per-document setting typed into the export dialog and saved
inside the .FCStd file, which meant an absolute (or even relative) filesystem path could leak
into a shared document. It's now a single add-on-wide preference: a path always resolved
relative to the FreeCAD document's own folder, and never written to any document.

This module holds only the FreeCAD.ParamGet-backed getters/setters and the format-resolution
logic -- no PySide import, so it can be imported (and its logic exercised) without a Qt
installation. The Qt preferences page itself lives in `preferences_page.py`.
"""

import FreeCAD as App

PARAM_GROUP = "User parameter:BaseApp/Preferences/Mod/GridParams"
EXPORT_RELATIVE_PATH_KEY = "ExportRelativePath"
PREFERRED_FORMATS_KEY = "PreferredFormats"
ALLOW_PER_ITEM_FORMATS_KEY = "AllowPerItemFormats"
ENFORCE_PREFERRED_FORMATS_KEY = "EnforcePreferredFormats"

_FALLBACK_FORMATS = ["3mf"]


def get_export_relative_path() -> str:
    return App.ParamGet(PARAM_GROUP).GetString(EXPORT_RELATIVE_PATH_KEY, "")


def set_export_relative_path(relative_path: str) -> None:
    App.ParamGet(PARAM_GROUP).SetString(EXPORT_RELATIVE_PATH_KEY, relative_path)


def get_preferred_formats() -> list[str]:
    raw = App.ParamGet(PARAM_GROUP).GetString(PREFERRED_FORMATS_KEY, "")
    return [format_id for format_id in raw.split(",") if format_id]


def set_preferred_formats(formats: list[str]) -> None:
    App.ParamGet(PARAM_GROUP).SetString(PREFERRED_FORMATS_KEY, ",".join(formats))


def get_allow_per_item_formats() -> bool:
    return App.ParamGet(PARAM_GROUP).GetBool(ALLOW_PER_ITEM_FORMATS_KEY, False)


def set_allow_per_item_formats(allowed: bool) -> None:
    App.ParamGet(PARAM_GROUP).SetBool(ALLOW_PER_ITEM_FORMATS_KEY, allowed)


def get_enforce_preferred_formats() -> bool:
    return App.ParamGet(PARAM_GROUP).GetBool(ENFORCE_PREFERRED_FORMATS_KEY, False)


def set_enforce_preferred_formats(enforced: bool) -> None:
    App.ParamGet(PARAM_GROUP).SetBool(ENFORCE_PREFERRED_FORMATS_KEY, enforced)


def resolve_effective_formats(item_formats: list[str] | None) -> list[str]:
    """The formats a given grid item should actually export to, given the global preferences:
    enforced preferred formats always win; otherwise a per-item override is used if the global
    toggle allows it; otherwise the preferred formats apply."""
    preferred = get_preferred_formats() or _FALLBACK_FORMATS
    if get_enforce_preferred_formats():
        return preferred
    if get_allow_per_item_formats() and item_formats is not None:
        return item_formats
    return preferred
