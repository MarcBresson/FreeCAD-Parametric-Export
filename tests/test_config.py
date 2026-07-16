import json

import pytest

from freecad.gridparams.core.config import (
    CONFIG_SCHEMA_VERSION,
    ConfigSchemaError,
    ExportSettings,
    GridConfig,
    GridItem,
    apply_migrations,
    config_from_json,
    config_to_json,
    expand_config,
)
from freecad.gridparams.core.values import Fixed, LinSpace, ValueList
from freecad.gridparams.core.variation import find_duplicate_names


def test_macro_style_basic_list_no_sampler():
    """Each literal item expands to exactly one variation, named directly -- the macro's exact behavior."""
    config = GridConfig(
        base_name="Cable winder organizer",
        items=[
            GridItem(
                params={"Base_CableLength": 1000, "Base_CableThickness": 3},
                name_template="XS",
            ),
            GridItem(
                params={"Base_CableLength": 1500, "Base_CableThickness": 4},
                name_template="S",
            ),
        ],
    )
    variations = expand_config(config)
    assert [v.name for v in variations] == ["XS", "S"]
    assert variations[0].params == {"Base_CableLength": 1000, "Base_CableThickness": 3}


def test_single_dict_grid_expands_via_cartesian_product_with_template_naming():
    config = GridConfig(
        base_name="Base",
        naming_template="{base_name} - L{Length}",
        items=[GridItem(params={"Length": ValueList([1, 2]), "Thickness": Fixed(3)})],
    )
    variations = expand_config(config)
    assert [v.name for v in variations] == ["Base - L1", "Base - L2"]


def test_list_of_dicts_grid_expands_independently():
    config = GridConfig(
        base_name="Base",
        naming_template="{base_name} - {Length}",
        items=[
            GridItem(params={"Length": Fixed(1)}),
            GridItem(
                params={"Width": ValueList([2, 3])},
                name_template="{base_name} - W{Width}",
            ),
        ],
    )
    variations = expand_config(config)
    assert [v.name for v in variations] == ["Base - 1", "Base - W2", "Base - W3"]


def test_item_without_placeholder_but_multiple_combinations_creates_duplicates():
    config = GridConfig(
        base_name="Base",
        items=[GridItem(params={"Length": ValueList([1, 2])}, name_template="Fixed")],
    )
    variations = expand_config(config)
    assert find_duplicate_names(variations) == ["Fixed"]


def test_config_json_roundtrip_preserves_samplers_and_settings():
    config = GridConfig(
        base_name="Cable winder",
        varset_object_name="VarSet",
        naming_template="{base_name} - {Length}",
        items=[
            GridItem(
                params={"Length": LinSpace(0, 10, 3), "Label": "fixed-str"},
                name_template=None,
            ),
            GridItem(params={"Length": 5}, name_template="Explicit"),
        ],
        export_settings=ExportSettings(
            combine=True,
            selected_object_names=["Body001", "Body003"],
            last_export_folder="/tmp/export",
            body_name_placement="prepend",
        ),
    )
    restored = config_from_json(config_to_json(config))

    assert restored.base_name == config.base_name
    assert restored.naming_template == config.naming_template
    assert restored.export_settings == config.export_settings
    assert restored.items[0].params["Length"] == LinSpace(0, 10, 3)
    assert restored.items[1].name_template == "Explicit"
    assert expand_config(restored) == expand_config(config)


def test_config_to_json_stamps_current_schema_version():
    data = json.loads(config_to_json(GridConfig()))
    assert data["schema_version"] == CONFIG_SCHEMA_VERSION


def test_apply_migrations_is_a_no_op_at_current_version():
    data = {"schema_version": 3, "value": "unchanged"}
    assert apply_migrations(data, migrations={}, current_version=3) == data


def test_apply_migrations_defaults_missing_version_to_one():
    data = {"value": "no version key"}
    assert apply_migrations(data, migrations={}, current_version=1) == data


def test_apply_migrations_walks_a_multi_step_chain():
    def v1_to_v2(data):
        remaining = {
            k: v for k, v in data.items() if k not in ("old_name", "schema_version")
        }
        return {**remaining, "schema_version": 2, "renamed": data["old_name"]}

    def v2_to_v3(data):
        return {**data, "schema_version": 3, "renamed": data["renamed"].upper()}

    data = {"schema_version": 1, "old_name": "hello"}
    migrations = {1: v1_to_v2, 2: v2_to_v3}

    result = apply_migrations(data, migrations, current_version=3)

    assert result == {"schema_version": 3, "renamed": "HELLO"}


def test_apply_migrations_raises_when_version_is_newer_than_supported():
    data = {"schema_version": 99}
    with pytest.raises(ConfigSchemaError):
        apply_migrations(data, migrations={}, current_version=1)


def test_apply_migrations_raises_when_no_migration_path_exists():
    data = {"schema_version": 1}
    with pytest.raises(ConfigSchemaError):
        apply_migrations(data, migrations={}, current_version=2)


def test_config_from_json_raises_config_schema_error_for_unsupported_future_version():
    raw = config_to_json(GridConfig())
    data = json.loads(raw)
    data["schema_version"] = CONFIG_SCHEMA_VERSION + 1
    with pytest.raises(ConfigSchemaError):
        config_from_json(json.dumps(data))
