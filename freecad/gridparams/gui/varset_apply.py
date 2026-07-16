"""Apply a Variation's resolved params onto a document's App::VarSet. Ported from the macro's apply_params."""


class RecomputeError(Exception):
    pass


def apply_variation(doc, varset_name, variation):
    varset = doc.getObject(varset_name)
    if varset is None:
        raise LookupError(f"No object named {varset_name!r} in document {doc.Name!r}")

    for param_name, param_value in variation.params.items():
        if not hasattr(varset, param_name):
            available = ", ".join(varset.PropertiesList)
            raise AttributeError(
                f"VarSet {varset_name!r} has no property {param_name!r}. "
                f"Available properties: {available}"
            )
        prop = getattr(varset, param_name)
        if hasattr(prop, "Value"):
            prop.Value = param_value
        else:
            setattr(varset, param_name, param_value)

    doc.recompute()

    invalid = [obj for obj in doc.Objects if "Invalid" in obj.State]
    if invalid:
        details = "; ".join(f"{obj.Name}: {obj.getStatusString()}" for obj in invalid)
        raise RecomputeError(
            f"Recompute failed for variation {variation.name!r} -- {details}"
        )
