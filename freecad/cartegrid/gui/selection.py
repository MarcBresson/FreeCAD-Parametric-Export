"""Bridge between the FreeCAD tree/3D-view selection and object names stored in ExportSettings."""

import FreeCADGui as Gui


def get_selected_object_names():
    return [obj.Name for obj in Gui.Selection.getSelection()]


def resolve_objects(doc, names):
    objects = []
    missing = []
    for name in names:
        obj = doc.getObject(name)
        if obj is None:
            missing.append(name)
        else:
            objects.append(obj)
    if missing:
        raise LookupError(
            f"Object(s) not found in document {doc.Name!r}: {', '.join(missing)}"
        )
    return objects
