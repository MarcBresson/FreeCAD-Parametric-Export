"""Embed grid configurations inside the document via dedicated hidden data-only objects.

A document may hold any number of these config containers -- one per body/VarSet
combination a user wants to manage independently. Each is identified by its own FreeCAD
object (looked up by internal Name, a stable technical handle), while its user-facing
identity is just its Label -- renamable inline in the tree like any other FreeCAD object,
with no separate name property to keep in sync.
"""

from freecad.gridparams.core.config import config_from_json, config_to_json

CONFIG_OBJECT_BASE_NAME = "GridParamsConfig"
CONFIG_PROP = "ConfigJSON"
CONFIG_MARKER_PROP = "IsGridParamsConfig"
DEFAULT_CONFIG_LABEL = "Grid Params Config"


class ConfigContainerProxy:
    """No geometry -- this object exists only to hold the ConfigJSON property."""

    def execute(self, obj):
        pass


def is_config_object(obj):
    return (
        obj is not None
        and getattr(obj, "TypeId", "") == "App::FeaturePython"
        and hasattr(obj, CONFIG_PROP)
        and hasattr(obj, CONFIG_MARKER_PROP)
    )


def list_config_objects(doc):
    return [obj for obj in doc.Objects if is_config_object(obj)]


def _suggest_label(doc, base=DEFAULT_CONFIG_LABEL):
    existing = {obj.Label for obj in list_config_objects(doc)}
    if base not in existing:
        return base
    suffix = 2
    while f"{base} {suffix}" in existing:
        suffix += 1
    return f"{base} {suffix}"


def create_config_object(doc, label=None):
    obj = doc.addObject("App::FeaturePython", CONFIG_OBJECT_BASE_NAME)
    obj.Proxy = ConfigContainerProxy()
    obj.addProperty(
        "App::PropertyString", CONFIG_PROP, "GridParams", "Serialized GridParams configuration (JSON)"
    )
    obj.addProperty(
        "App::PropertyBool", CONFIG_MARKER_PROP, "GridParams", "Internal marker; do not edit", 8
    )
    setattr(obj, CONFIG_MARKER_PROP, True)
    obj.Label = label or _suggest_label(doc)
    if obj.ViewObject is not None:
        from .view_provider import ConfigContainerViewProxy

        obj.ViewObject.Proxy = ConfigContainerViewProxy()
    return obj


def get_config_object(doc, internal_name):
    obj = doc.getObject(internal_name)
    return obj if is_config_object(obj) else None


def save_config(obj, config):
    setattr(obj, CONFIG_PROP, config_to_json(config))
    if obj.Document is not None:
        obj.Document.recompute()


def load_config(obj):
    if obj is None or not getattr(obj, CONFIG_PROP, ""):
        return None
    return config_from_json(getattr(obj, CONFIG_PROP))
