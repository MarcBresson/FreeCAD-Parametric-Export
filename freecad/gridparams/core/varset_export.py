"""Turn a VarSet's properties into CSV text. Pure Python -- no FreeCAD import -- so it is
unit-testable the same way as the rest of gridparams.core.
"""

import csv
import io
from dataclasses import dataclass
from typing import Any

_ALL_COLUMNS = ("Group", "Value", "Unit", "FreeCAD Unit", "Comment")


@dataclass
class PropertyInfo:
    name: str
    value: Any
    unit: Any = ""
    freecad_unit: Any = ""
    group: str = ""
    comment: str = ""

    @property
    def is_private(self) -> bool:
        return self.name.startswith("_") or self.group.startswith("_")


@dataclass
class VarSetCsvOptions:
    include_value: bool = True
    include_unit: bool = True
    include_freecad_unit: bool = True
    include_group: bool = True
    include_comment: bool = True
    include_private: bool = False


def filter_properties(
    properties: list[PropertyInfo], options: VarSetCsvOptions
) -> list[PropertyInfo]:
    if options.include_private:
        return list(properties)
    return [prop for prop in properties if not prop.is_private]


def to_csv_text(properties: list[PropertyInfo], options: VarSetCsvOptions) -> str:
    included = {
        "Group": options.include_group,
        "Value": options.include_value,
        "Unit": options.include_unit,
        "FreeCAD Unit": options.include_freecad_unit,
        "Comment": options.include_comment,
    }
    header = ["Name"] + [col for col in _ALL_COLUMNS if included[col]]

    field_getters = {
        "Name": lambda prop: prop.name,
        "Group": lambda prop: prop.group,
        "Value": lambda prop: prop.value,
        "Unit": lambda prop: prop.unit,
        "FreeCAD Unit": lambda prop: prop.freecad_unit,
        "Comment": lambda prop: prop.comment,
    }

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(header)
    for prop in filter_properties(properties, options):
        writer.writerow([field_getters[col](prop) for col in header])
    return buffer.getvalue()
