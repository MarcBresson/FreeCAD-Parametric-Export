from fakes import FakeDocument

from freecad.gridparams.core.config import GridConfig
from freecad.gridparams.gui import persistence


def test_create_config_object_adds_marker_and_json_property():
    doc = FakeDocument()
    obj = persistence.create_config_object(doc)
    assert persistence.is_config_object(obj)
    assert getattr(obj, persistence.CONFIG_MARKER_PROP) is True
    assert hasattr(obj, persistence.CONFIG_PROP)


def test_create_config_object_uses_default_label_and_avoids_collisions():
    doc = FakeDocument()
    first = persistence.create_config_object(doc)
    second = persistence.create_config_object(doc)
    assert first.Label == persistence.DEFAULT_CONFIG_LABEL
    assert second.Label == f"{persistence.DEFAULT_CONFIG_LABEL} 2"


def test_create_config_object_accepts_explicit_label():
    doc = FakeDocument()
    obj = persistence.create_config_object(doc, label="Body A grid")
    assert obj.Label == "Body A grid"


def test_list_config_objects_excludes_unrelated_objects():
    doc = FakeDocument()
    config_obj = persistence.create_config_object(doc)
    doc.addObject("Part::Feature", "Body")
    doc.addObject("App::FeaturePython", "SomeOtherFeaturePython")

    assert persistence.list_config_objects(doc) == [config_obj]


def test_save_and_load_config_roundtrip():
    doc = FakeDocument()
    obj = persistence.create_config_object(doc)
    config = GridConfig(base_name="Cable winder")

    persistence.save_config(obj, config)
    restored = persistence.load_config(obj)

    assert restored.base_name == "Cable winder"


def test_load_config_returns_none_when_never_saved():
    doc = FakeDocument()
    obj = persistence.create_config_object(doc)
    assert persistence.load_config(obj) is None


def test_get_config_object_returns_none_for_non_config_object():
    doc = FakeDocument()
    other = doc.addObject("App::FeaturePython", "SomeOtherFeaturePython")
    assert persistence.get_config_object(doc, other.Name) is None


def test_get_config_object_returns_the_config_object_by_internal_name():
    doc = FakeDocument()
    obj = persistence.create_config_object(doc)
    assert persistence.get_config_object(doc, obj.Name) is obj


def test_is_config_object_false_for_unrelated_type_id():
    doc = FakeDocument()
    body = doc.addObject("Part::Feature", "Body")
    assert persistence.is_config_object(body) is False
