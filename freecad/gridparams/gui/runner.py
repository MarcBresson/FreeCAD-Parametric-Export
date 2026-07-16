"""The seam where the pure core engine meets FreeCAD: apply each variation and export it."""

from pathlib import Path

from freecad.gridparams.core.config import GridConfig, expand_config
from freecad.gridparams.core.export_plan import build_export_jobs_for_variation
from freecad.gridparams.core.variation import find_duplicate_names

from .mesh_export import export_objects
from .selection import resolve_objects
from .varset_apply import apply_variation


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


def run_export(
    doc, config: GridConfig, output_folder: Path, progress_callback=None
) -> list[Path]:
    variations = expand_config(config)
    duplicates = find_duplicate_names(variations)
    if duplicates:
        raise DuplicateVariationNamesError(duplicates)

    written = []
    total = len(variations)
    for index, variation in enumerate(variations, start=1):
        try:
            apply_variation(doc, config.varset_object_name, variation)
            for job in build_export_jobs_for_variation(
                variation, config.export_settings
            ):
                objects = resolve_objects(doc, job.objects)
                path = output_folder / job.output_stem
                export_objects(objects, path)
                written.append(path.with_suffix(".3mf"))
        except Exception as exc:
            raise ExportAbortedError(
                f"Stopped at variation {index}/{total} ({variation.name!r}): {exc}",
                written=written,
            ) from exc
        if progress_callback is not None:
            progress_callback(index, total)
    return written
