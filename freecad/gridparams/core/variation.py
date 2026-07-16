from collections import Counter
from dataclasses import dataclass
from typing import Any


@dataclass
class Variation:
    name: str
    params: dict[str, Any]


def find_duplicate_names(variations: list[Variation]) -> list[str]:
    """Names that resolve to more than one variation -- a real error since it means silent file overwrites."""
    counts = Counter(variation.name for variation in variations)
    return sorted(name for name, count in counts.items() if count > 1)
