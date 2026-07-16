"""Pure planning of which objects go into which output file for a variation -- no I/O, no Mesh."""

import re
from dataclasses import dataclass

from .config import ExportSettings
from .variation import Variation

_INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*]')


def sanitize_filename(name: str) -> str:
    return _INVALID_FILENAME_CHARS.sub("_", name).strip()


@dataclass
class ExportJob:
    variation_name: str
    output_stem: str  # sanitized filename stem, no extension
    objects: list[str]  # object names for this one output file


def build_export_jobs_for_variation(
    variation: Variation, settings: ExportSettings
) -> list[ExportJob]:
    names = settings.selected_object_names
    groups = (
        [names] if settings.combine or len(names) <= 1 else [[name] for name in names]
    )
    jobs = []
    for group in groups:
        stem = sanitize_filename(variation.name)
        if len(groups) > 1:
            stem = (
                f"{group[0]} - {stem}"
                if settings.body_name_placement == "prepend"
                else f"{stem} - {group[0]}"
            )
        jobs.append(
            ExportJob(variation_name=variation.name, output_stem=stem, objects=group)
        )
    return jobs
