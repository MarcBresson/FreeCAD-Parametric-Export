"""Embed the grid configuration inside the document via a dedicated hidden data-only object.

A dedicated object (rather than a property bolted onto the VarSet) is used because a document
may have zero, one, or several VarSets, and the tool's saved state shouldn't depend on that
object's name, existence, or survive it being renamed/deleted.
"""

from freecad.gridparams.core.config import config_from_json, config_to_json

CONFIG_OBJECT_NAME = "GridParamsConfig"
CONFIG_PROP = "ConfigJSON"


class ConfigContainerProxy:
    """No geometry -- this object exists only to hold the ConfigJSON property."""

    def execute(self, obj):
        pass


def get_or_create_config_object(doc):
    obj = doc.getObject(CONFIG_OBJECT_NAME)
    if obj is None:
        obj = doc.addObject("App::FeaturePython", CONFIG_OBJECT_NAME)
        obj.Proxy = ConfigContainerProxy()
        obj.addProperty(
            "App::PropertyString", CONFIG_PROP, "GridParams", "Serialized GridParams configuration (JSON)"
        )
        if obj.ViewObject is not None:
            obj.ViewObject.Visibility = False
    return obj


def save_config(doc, config):
    obj = get_or_create_config_object(doc)
    setattr(obj, CONFIG_PROP, config_to_json(config))
    doc.recompute()


def load_config(doc):
    obj = doc.getObject(CONFIG_OBJECT_NAME)
    if obj is None or not getattr(obj, CONFIG_PROP, ""):
        return None
    return config_from_json(getattr(obj, CONFIG_PROP))
