"""The seam where the pure core engine meets FreeCAD: apply each variation and export it."""

from pathlib import Path

from freecad.gridparams.core.config import GridConfig, expand_config
from freecad.gridparams.core.export_plan import build_export_jobs_for_variation
from freecad.gridparams.core.variation import find_duplicate_names

from . import preferences
from .format_registry import export_objects
from .selection import resolve_objects
from .varset_apply import apply_variation, capture_params, restore_params


class DuplicateVariationNamesError(Exception):
    def __init__(self, names):
        super().__init__(
            f"Duplicate variation name(s), would overwrite output files: {', '.join(names)}"
        )
        self.names = names


class ExportAbortedError(Exception):
    def __init__(self, message, written):
        super().__init__(message)
        self.written = written


def _export_variation(
    doc,
    config: GridConfig,
    variation,
    output_folder: Path,
    format_override: str | None,
    object_labels: dict,
) -> list[Path]:
    """Apply one variation and export every job it produces. Returns the paths written."""
    written = []
    apply_variation(doc, config.varset_object_name, variation)
    for job in build_export_jobs_for_variation(
        variation,
        config.export_settings,
        object_labels,
        body_name_template=preferences.get_body_name_template(),
    ):
        objects = resolve_objects(doc, job.objects)
        path = output_folder / job.output_stem
        formats = (
            [format_override]
            if format_override
            else preferences.resolve_effective_formats(job.formats)
        )
        for format_id in formats:
            written.append(export_objects(objects, path, format_id))
    return written


def run_export(
    doc,
    config: GridConfig,
    output_folder: Path,
    progress_callback=None,
    format_override: str | None = None,
) -> list[Path]:
    variations = expand_config(config, document_label=doc.Label)
    duplicates = find_duplicate_names(variations)
    if duplicates:
        raise DuplicateVariationNamesError(duplicates)

    object_labels = {
        name: obj.Label
        for name in config.export_settings.selected_object_names
        if (obj := doc.getObject(name)) is not None
    }

    param_names = {name for variation in variations for name in variation.params}
    original_values = capture_params(doc, config.varset_object_name, param_names)

    written = []
    total = len(variations)
    try:
        for index, variation in enumerate(variations, start=1):
            try:
                written.extend(
                    _export_variation(
                        doc,
                        config,
                        variation,
                        output_folder,
                        format_override,
                        object_labels,
                    )
                )
            except Exception as exc:
                raise ExportAbortedError(
                    f"Stopped at variation {index}/{total} ({variation.name!r}): {exc}",
                    written=written,
                ) from exc
            if progress_callback is not None:
                progress_callback(index, total)
    finally:
        restore_params(doc, config.varset_object_name, original_values)
    return written
