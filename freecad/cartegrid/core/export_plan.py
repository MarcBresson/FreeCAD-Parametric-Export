"""Pure planning of which objects go into which output file for a variation -- no I/O, no Mesh."""

import re
from dataclasses import dataclass

from .config import ExportSettings
from .naming import NamingTemplateError, resolve_name
from .variation import Variation

_INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*]')

DEFAULT_BODY_NAME_TEMPLATE = "{name} - {body_label}"


def sanitize_filename(name: str) -> str:
    return _INVALID_FILENAME_CHARS.sub("_", name).strip()


def apply_body_name_template(
    template: str, name: str, body_label: str, body_name: str
) -> str:
    try:
        return template.format(name=name, body_label=body_label, body_name=body_name)
    except KeyError as exc:
        raise NamingTemplateError(
            f"Unknown placeholder {exc} in body name template {template!r} -- "
            f"available: name, body_label, body_name"
        ) from exc


@dataclass
class ExportJob:
    variation_name: str
    output_stem: str  # sanitized filename stem, no extension
    objects: list[str]  # object names for this one output file
    formats: list[str] | None = (
        None  # None => fall back to the global preferred formats
    )


def build_export_jobs_for_variation(
    variation: Variation,
    settings: ExportSettings,
    object_labels: dict[str, str] | None = None,
    body_name_template: str = DEFAULT_BODY_NAME_TEMPLATE,
) -> list[ExportJob]:
    object_labels = object_labels or {}
    names = settings.selected_object_names
    groups = (
        [names] if settings.combine or len(names) <= 1 else [[name] for name in names]
    )
    jobs = []
    for group in groups:
        # This job's first object -- the only one, unless several are combined into one file,
        # in which case it's still a deterministic choice for {body_label}/{body_name} rather
        # than leaving them blank. `group` is only ever empty if no object is selected at all.
        body_name = sanitize_filename(group[0]) if group else ""
        label = (
            sanitize_filename(object_labels.get(group[0], group[0])) if group else ""
        )
        if variation.name_template is not None:
            # Re-resolve with the real body now that one is known, so a naming template that
            # itself references {body_label}/{body_name} gets a per-body name here instead of
            # the "" placeholder used in expand_config.
            body_params = {
                **variation.params,
                "body_label": label,
                "body_name": body_name,
            }
            name = resolve_name(
                variation.name_template,
                variation.base_name,
                body_params,
                variation.document_label,
            )
        else:
            name = variation.name
        stem = sanitize_filename(name)
        if len(groups) > 1:
            stem = sanitize_filename(
                apply_body_name_template(body_name_template, stem, label, body_name)
            )
        jobs.append(
            ExportJob(
                variation_name=variation.name,
                output_stem=stem,
                objects=group,
                formats=variation.formats,
            )
        )
    return jobs
