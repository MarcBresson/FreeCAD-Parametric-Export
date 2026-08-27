"""Apply a Variation's resolved params onto a document's App::VarSet. Ported from the macro's apply_params."""


class RecomputeError(Exception):
    pass


def _get_varset(doc, varset_name):
    varset = doc.getObject(varset_name)
    if varset is None:
        raise LookupError(f"No object named {varset_name!r} in document {doc.Name!r}")
    return varset


def _set_params(varset, varset_name, params):
    for param_name, param_value in params.items():
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


def capture_params(doc, varset_name, param_names):
    """Snapshot the current values of `param_names` on the VarSet, to be handed to
    restore_params() later."""
    varset = _get_varset(doc, varset_name)
    values = {}
    for param_name in param_names:
        prop = getattr(varset, param_name)
        values[param_name] = prop.Value if hasattr(prop, "Value") else prop
    return values


def restore_params(doc, varset_name, values):
    """Put back values previously captured with capture_params()."""
    varset = _get_varset(doc, varset_name)
    _set_params(varset, varset_name, values)
    doc.recompute()


def apply_variation(doc, varset_name, variation):
    varset = _get_varset(doc, varset_name)
    _set_params(varset, varset_name, variation.params)

    doc.recompute()

    invalid = [obj for obj in doc.Objects if "Invalid" in obj.State]
    if invalid:
        details = "; ".join(f"{obj.Name}: {obj.getStatusString()}" for obj in invalid)
        raise RecomputeError(
            f"Recompute failed for variation {variation.name!r} -- {details}"
        )
