"""The single data model unifying every parameter-grid shape the addon supports.

A GridItem is one "sklearn grid dict" plus its own optional name template. Every scenario --
the macro's plain literal list, a single dict expanded via full Cartesian product, or a list of
independently-expanded dicts -- is just a list of GridItems; nothing downstream branches on
which shape produced it.
"""

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Literal

from .grid import ParameterGrid
from .naming import resolve_name
from .values import param_values_from_dict, param_values_to_dict
from .variation import Variation

CONFIG_SCHEMA_VERSION = 1


class ConfigSchemaError(Exception):
    pass


# Keyed by the version a migration migrates FROM; each function takes the raw dict at that
# version and returns the raw dict at version + 1 (with "schema_version" updated to match).
# To make a breaking change to the on-disk shape: bump CONFIG_SCHEMA_VERSION, write a
# `_migrate_v<N>_to_v<N+1>(data: dict) -> dict` that transforms the old keys/shape into the new
# one, and register it here under `<N>`. Old documents then migrate forward automatically the
# next time they're loaded; nothing else in this module needs to change.
_MIGRATIONS: dict[int, Callable[[dict], dict]] = {}


def apply_migrations(data: dict, migrations: dict[int, Callable[[dict], dict]], current_version: int) -> dict:
    """Walk `data` forward from its own schema_version to `current_version` via `migrations`.

    Pulled out of `config_from_json` as a pure function (no module-level state) so the walking
    logic -- version too new, no migration path registered, multi-step chains -- can be unit
    tested with a synthetic migrations table, without waiting for a real schema change to happen.
    """
    version = data.get("schema_version", 1)
    if version > current_version:
        raise ConfigSchemaError(
            f"Saved grid config is schema_version {version}, newer than this addon supports "
            f"(max {current_version}). Update the GridParamsExport addon to open it."
        )
    while version < current_version:
        migrate = migrations.get(version)
        if migrate is None:
            raise ConfigSchemaError(f"No migration registered from schema_version {version} to {current_version}.")
        data = migrate(data)
        version = data.get("schema_version", version + 1)
    return data


@dataclass
class GridItem:
    params: dict[str, Any] = field(default_factory=dict)
    name_template: str | None = None  # None => fall back to GridConfig.naming_template


@dataclass
class ExportSettings:
    combine: bool = False
    selected_object_names: list[str] = field(default_factory=list)
    last_export_folder: str = ""
    body_name_placement: Literal["append", "prepend"] = "append"  # only relevant when combine is False


@dataclass
class GridConfig:
    base_name: str = ""
    varset_object_name: str = "VarSet"
    naming_template: str = "{base_name}"
    items: list[GridItem] = field(default_factory=lambda: [GridItem()])
    export_settings: ExportSettings = field(default_factory=ExportSettings)


def expand_config(config: GridConfig) -> list[Variation]:
    variations = []
    for item in config.items:
        template = item.name_template if item.name_template is not None else config.naming_template
        for resolved_params in ParameterGrid(item.params):
            variations.append(Variation(
                name=resolve_name(template, config.base_name, resolved_params),
                params=resolved_params,
            ))
    return variations


def config_to_json(config: GridConfig) -> str:
    data = {
        "schema_version": CONFIG_SCHEMA_VERSION,
        "base_name": config.base_name,
        "varset_object_name": config.varset_object_name,
        "naming_template": config.naming_template,
        "items": [
            {
                "params": {key: param_values_to_dict(value) for key, value in item.params.items()},
                "name_template": item.name_template,
            }
            for item in config.items
        ],
        "export_settings": {
            "combine": config.export_settings.combine,
            "selected_object_names": list(config.export_settings.selected_object_names),
            "last_export_folder": config.export_settings.last_export_folder,
            "body_name_placement": config.export_settings.body_name_placement,
        },
    }
    return json.dumps(data, indent=2)


def config_from_json(raw: str) -> GridConfig:
    data = json.loads(raw)
    data = apply_migrations(data, _MIGRATIONS, CONFIG_SCHEMA_VERSION)
    items = [
        GridItem(
            params={key: param_values_from_dict(value) for key, value in item_data.get("params", {}).items()},
            name_template=item_data.get("name_template"),
        )
        for item_data in data.get("items", [])
    ]
    export_data = data.get("export_settings", {})
    export_settings = ExportSettings(
        combine=export_data.get("combine", False),
        selected_object_names=list(export_data.get("selected_object_names", [])),
        last_export_folder=export_data.get("last_export_folder", ""),
        body_name_placement=export_data.get("body_name_placement", "append"),
    )
    return GridConfig(
        base_name=data.get("base_name", ""),
        varset_object_name=data.get("varset_object_name", "VarSet"),
        naming_template=data.get("naming_template", "{base_name}"),
        items=items or [GridItem()],
        export_settings=export_settings,
    )
