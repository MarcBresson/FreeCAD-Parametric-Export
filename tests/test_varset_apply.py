from tests.fakes import FakeDocument

from freecad.gridparams.core.variation import Variation
from freecad.gridparams.gui.varset_apply import (
    apply_variation,
    capture_params,
    restore_params,
)


def _make_varset(doc, **params):
    varset = doc.addObject("App::FeaturePython", "VarSet")
    varset.State = []
    for name, value in params.items():
        setattr(varset, name, value)
    return varset


def test_capture_then_restore_params_roundtrips_original_values():
    doc = FakeDocument()
    varset = _make_varset(doc, Width=10, Height=20)

    original = capture_params(doc, "VarSet", {"Width", "Height"})
    varset.Width = 99
    varset.Height = 55

    restore_params(doc, "VarSet", original)

    assert varset.Width == 10
    assert varset.Height == 20


def test_restore_params_undoes_apply_variation():
    doc = FakeDocument()
    varset = _make_varset(doc, Width=10)

    original = capture_params(doc, "VarSet", {"Width"})
    apply_variation(doc, "VarSet", Variation(name="v1", params={"Width": 42}))
    assert varset.Width == 42

    restore_params(doc, "VarSet", original)

    assert varset.Width == 10
