import pytest

from tests.fakes import FakeDocument

from freecad.gridparams.core.config import GridConfig, GridItem
from freecad.gridparams.gui import runner


def _make_varset(doc, **params):
    varset = doc.addObject("App::FeaturePython", "VarSet")
    varset.State = []
    for name, value in params.items():
        setattr(varset, name, value)
    return varset


def _make_config(**params):
    return GridConfig(
        varset_object_name="VarSet",
        naming_template="{Width}",
        items=[GridItem(params=params)],
    )


def test_run_export_restores_varset_values_after_success(monkeypatch, tmp_path):
    doc = FakeDocument()
    doc.Label = doc.Name
    varset = _make_varset(doc, Width=10)
    config = _make_config(Width=[1, 2])

    monkeypatch.setattr(runner, "resolve_objects", lambda doc, names: [])
    monkeypatch.setattr(runner, "export_objects", lambda objects, path: None)

    runner.run_export(doc, config, tmp_path)

    assert varset.Width == 10


def test_run_export_restores_varset_values_after_failure(monkeypatch, tmp_path):
    doc = FakeDocument()
    doc.Label = doc.Name
    varset = _make_varset(doc, Width=10)
    config = _make_config(Width=[1, 2])

    monkeypatch.setattr(runner, "resolve_objects", lambda doc, names: [])

    def boom(objects, path):
        raise RuntimeError("disk full")

    monkeypatch.setattr(runner, "export_objects", boom)

    with pytest.raises(runner.ExportAbortedError):
        runner.run_export(doc, config, tmp_path)

    assert varset.Width == 10
