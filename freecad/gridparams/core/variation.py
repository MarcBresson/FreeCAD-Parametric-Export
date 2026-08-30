from collections import Counter
from dataclasses import dataclass
from typing import Any


@dataclass
class Variation:
    name: str
    params: dict[str, Any]
    # Set by expand_config so build_export_jobs_for_variation can re-resolve `name` at export
    # time with the real body_label/body_name once a specific object is known, instead of the
    # "" placeholder used here. None for a Variation built with an already-final name (e.g. in
    # tests) -- it then always exports using `name` as-is.
    name_template: str | None = None
    base_name: str = ""
    document_label: str = ""
    formats: list[str] | None = (
        None  # None => fall back to the global preferred formats
    )


def find_duplicate_names(variations: list[Variation]) -> list[str]:
    """Names that resolve to more than one variation -- a real error since it means silent file overwrites."""
    counts = Counter(variation.name for variation in variations)
    return sorted(name for name, count in counts.items() if count > 1)
