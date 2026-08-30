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

from ..core.export_plan import DEFAULT_BODY_NAME_TEMPLATE

PARAM_GROUP = "User parameter:BaseApp/Preferences/Mod/GridParams"
EXPORT_RELATIVE_PATH_KEY = "ExportRelativePath"
PREFERRED_FORMATS_KEY = "PreferredFormats"
ALLOW_PER_ITEM_FORMATS_KEY = "AllowPerItemFormats"
BODY_NAME_TEMPLATE_KEY = "BodyNameTemplate"

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


def get_body_name_template() -> str:
    return App.ParamGet(PARAM_GROUP).GetString(
        BODY_NAME_TEMPLATE_KEY, DEFAULT_BODY_NAME_TEMPLATE
    )


def set_body_name_template(template: str) -> None:
    App.ParamGet(PARAM_GROUP).SetString(BODY_NAME_TEMPLATE_KEY, template)


def resolve_effective_formats(item_formats: list[str] | None) -> list[str]:
    """The formats a given grid item should actually export to.

    Uses `item_formats` if AllowPerItemFormats is on and an override is set -- otherwise
    callers must not assume a non-None `item_formats` is reflected in the result. Falls back
    to the preferred formats (or the built-in fallback, if none are configured).
    """
    preferred = get_preferred_formats() or _FALLBACK_FORMATS
    if get_allow_per_item_formats() and item_formats is not None:
        return item_formats
    return preferred
