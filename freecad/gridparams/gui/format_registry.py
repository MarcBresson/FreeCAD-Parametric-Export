"""Dynamic export-format catalogue, built from whatever every loaded FreeCAD module has
registered via FreeCAD.addExportType -- the same mechanism FreeCAD's own built-in
"File > Export" command uses to resolve formats. No hardcoded format list.

FreeCAD.getExportType() returns {extension: module_name_or_[module_names]}, e.g.
{"step": "ImportGui", "dxf": ["importDXF", "TechDrawGui"]} -- keyed by bare extension, not by
the human-readable filter string originally passed to addExportType (that string isn't
exposed back to Python), so the extension doubles as both id and display label here.
"""

import importlib
from dataclasses import dataclass

_cache: list["FormatOption"] | None = None


@dataclass(frozen=True)
class FormatOption:
    id: str  # extension, lowercase, no dot -- e.g. "step"
    label: str  # display label -- e.g. "*.step"
    module_name: str


def list_available_formats() -> list[FormatOption]:
    """Every export format any loaded FreeCAD module has registered, keyed by its extension.
    Cached for the process lifetime -- registrations don't change after startup."""
    global _cache
    if _cache is None:
        import FreeCAD

        seen_ids: set[str] = set()
        options = []
        for extension, module_name in FreeCAD.getExportType().items():
            # A handful of formats are registered by more than one module; first wins.
            if isinstance(module_name, (list, tuple)):
                module_name = module_name[0] if module_name else None
            if not module_name:
                continue
            format_id = extension.lower()
            if format_id in seen_ids:
                continue
            seen_ids.add(format_id)
            options.append(
                FormatOption(
                    id=format_id, label=f"*.{format_id}", module_name=module_name
                )
            )
        _cache = sorted(options, key=lambda option: option.label)
    return _cache


def get_format(format_id: str) -> FormatOption | None:
    for option in list_available_formats():
        if option.id == format_id:
            return option
    return None


def export_objects(objects, export_path, format_id: str):
    """Export `objects` to `export_path` with `format_id`'s extension appended, dispatching
    to whichever FreeCAD module registered that format. Returns the full path written."""
    option = get_format(format_id)
    if option is None:
        raise ValueError(f"Unknown export format: {format_id!r}")

    export_path = export_path.with_name(f"{export_path.name}.{option.id}")
    module = importlib.import_module(option.module_name)

    if hasattr(module, "exportOptions"):
        options = module.exportOptions(str(export_path))
        module.export(objects, str(export_path), options)
    else:
        module.export(objects, str(export_path))
    return export_path
