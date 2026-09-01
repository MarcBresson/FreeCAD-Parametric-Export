import pytest

from tests.fakes import FakeDocument

from freecad.cartegrid.core.config import GridConfig, GridItem
from freecad.cartegrid.gui import runner


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
    monkeypatch.setattr(
        runner.preferences, "get_body_name_template", lambda: "{name} - {body_label}"
    )
    monkeypatch.setattr(runner, "export_objects", lambda objects, path, format_id: path)
    monkeypatch.setattr(
        runner.preferences, "resolve_effective_formats", lambda item_formats: ["3mf"]
    )

    runner.run_export(doc, config, tmp_path)

    assert varset.Width == 10


def test_run_export_restores_varset_values_after_failure(monkeypatch, tmp_path):
    doc = FakeDocument()
    doc.Label = doc.Name
    varset = _make_varset(doc, Width=10)
    config = _make_config(Width=[1, 2])

    monkeypatch.setattr(runner, "resolve_objects", lambda doc, names: [])
    monkeypatch.setattr(
        runner.preferences, "get_body_name_template", lambda: "{name} - {body_label}"
    )
    monkeypatch.setattr(
        runner.preferences, "resolve_effective_formats", lambda item_formats: ["3mf"]
    )

    def boom(objects, path, format_id):
        raise RuntimeError("disk full")

    monkeypatch.setattr(runner, "export_objects", boom)

    with pytest.raises(runner.ExportAbortedError):
        runner.run_export(doc, config, tmp_path)

    assert varset.Width == 10


def test_run_export_uses_format_override_regardless_of_preferences(
    monkeypatch, tmp_path
):
    doc = FakeDocument()
    doc.Label = doc.Name
    _make_varset(doc, Width=10)
    config = _make_config(Width=[1])

    monkeypatch.setattr(runner, "resolve_objects", lambda doc, names: [])
    monkeypatch.setattr(
        runner.preferences, "get_body_name_template", lambda: "{name} - {body_label}"
    )
    seen_formats = []

    def fake_export(objects, path, format_id):
        seen_formats.append(format_id)
        return path

    monkeypatch.setattr(runner, "export_objects", fake_export)

    def boom(item_formats):
        raise AssertionError(
            "resolve_effective_formats should not be used with an override"
        )

    monkeypatch.setattr(runner.preferences, "resolve_effective_formats", boom)

    runner.run_export(doc, config, tmp_path, format_override="step")

    assert seen_formats == ["step"]
