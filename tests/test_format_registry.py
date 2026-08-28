import types

import pytest

from freecad.gridparams.gui import format_registry


@pytest.fixture(autouse=True)
def _reset_cache(monkeypatch):
    monkeypatch.setattr(format_registry, "_cache", None)


def _fake_get_export_type(monkeypatch, mapping):
    import FreeCAD

    monkeypatch.setattr(FreeCAD, "getExportType", lambda: dict(mapping), raising=False)


def test_list_available_formats_reads_extension_keyed_dict(monkeypatch):
    # FreeCAD.getExportType() is keyed by bare extension, not by a filter string.
    _fake_get_export_type(monkeypatch, {"step": "ImportGui", "stl": "Mesh"})
    options = {option.id: option for option in format_registry.list_available_formats()}
    assert options["step"].module_name == "ImportGui"
    assert options["step"].label == "*.step"
    assert options["stl"].module_name == "Mesh"


def test_list_available_formats_uses_first_module_when_registered_as_a_list(
    monkeypatch,
):
    _fake_get_export_type(monkeypatch, {"dxf": ["importDXF", "TechDrawGui"]})
    options = format_registry.list_available_formats()
    assert options[0].module_name == "importDXF"


def test_list_available_formats_lowercases_and_dedupes_extensions(monkeypatch):
    # FreeCAD registers some extensions inconsistently-cased (e.g. "stpZ" vs "stpz").
    _fake_get_export_type(monkeypatch, {"stpZ": "Import", "stpz": "Import"})
    ids = [option.id for option in format_registry.list_available_formats()]
    assert ids == ["stpz"]


def test_list_available_formats_skips_entries_with_no_module(monkeypatch):
    _fake_get_export_type(monkeypatch, {"stl": "Mesh", "empty": []})
    ids = {option.id for option in format_registry.list_available_formats()}
    assert ids == {"stl"}


def test_export_objects_dispatches_to_registered_module(monkeypatch, tmp_path):
    _fake_get_export_type(monkeypatch, {"stl": "FakeMesh"})

    calls = []
    fake_module = types.ModuleType("FakeMesh")
    fake_module.export = lambda objects, filename: calls.append((objects, filename))
    monkeypatch.setattr(
        format_registry.importlib, "import_module", lambda name: fake_module
    )

    result = format_registry.export_objects(["Body001"], tmp_path / "out", "stl")

    assert calls == [(["Body001"], str(tmp_path / "out.stl"))]
    assert result == tmp_path / "out.stl"


def test_export_objects_uses_export_options_when_available(monkeypatch, tmp_path):
    _fake_get_export_type(monkeypatch, {"stl": "FakeMesh"})

    calls = []
    fake_module = types.ModuleType("FakeMesh")
    fake_module.exportOptions = lambda filename: {"sentinel": filename}
    fake_module.export = lambda objects, filename, options: calls.append(
        (objects, filename, options)
    )
    monkeypatch.setattr(
        format_registry.importlib, "import_module", lambda name: fake_module
    )

    format_registry.export_objects(["Body001"], tmp_path / "out", "stl")

    assert calls == [
        (
            ["Body001"],
            str(tmp_path / "out.stl"),
            {"sentinel": str(tmp_path / "out.stl")},
        )
    ]


def test_export_objects_raises_for_unknown_format(monkeypatch, tmp_path):
    _fake_get_export_type(monkeypatch, {"stl": "FakeMesh"})
    with pytest.raises(ValueError):
        format_registry.export_objects(["Body001"], tmp_path / "out", "unknown")
