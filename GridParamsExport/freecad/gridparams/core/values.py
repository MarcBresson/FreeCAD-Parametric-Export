"""Parameter value kinds: a fixed scalar, an explicit list, or a deterministic range sampler.

Each kind exposes ``to_list()`` so callers (namely :mod:`grid`) never need to know which
kind they're holding -- they only rely on the ``to_list`` duck-type contract.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Fixed:
    """A single, unvarying value. Degenerate case of a list with one element."""

    value: Any

    def to_list(self) -> list:
        return [self.value]


@dataclass(frozen=True)
class ValueList:
    """An explicit, unordered set of values to enumerate."""

    values: list

    def to_list(self) -> list:
        return list(self.values)


@dataclass(frozen=True)
class LinSpace:
    """``num`` evenly spaced floats between ``start`` and ``stop`` (inclusive), like numpy.linspace."""

    start: float
    stop: float
    num: int

    def to_list(self) -> list:
        if self.num <= 1:
            return [self.start]
        step = (self.stop - self.start) / (self.num - 1)
        return [self.start + i * step for i in range(self.num)]


@dataclass(frozen=True)
class Range:
    """Arithmetic sequence from ``start`` to ``stop`` (inclusive) by ``step``. Works for int or float step."""

    start: float
    stop: float
    step: float = 1

    def to_list(self) -> list:
        if self.step == 0:
            raise ValueError("Range.step must be non-zero")
        values = []
        count = 0
        while True:
            value = self.start + count * self.step
            if (self.step > 0 and value > self.stop) or (self.step < 0 and value < self.stop):
                break
            values.append(value)
            count += 1
        return values


def normalize_param_values(value: Any) -> list:
    """Turn a Fixed/ValueList/LinSpace/Range/plain-list/bare-scalar into a concrete list of values.

    A bare scalar becomes a single-element list -- this is what makes "fixed value" a
    degenerate case of "list of values" rather than a separate code path anywhere downstream.
    """
    if hasattr(value, "to_list"):
        return value.to_list()
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


_KIND_TO_CLASS = {
    "fixed": Fixed,
    "list": ValueList,
    "linspace": LinSpace,
    "range": Range,
}
_CLASS_TO_KIND = {cls: kind for kind, cls in _KIND_TO_CLASS.items()}


def param_values_to_dict(value: Any) -> Any:
    """Serialize a Fixed/ValueList/LinSpace/Range to a JSON-friendly dict; pass through anything else."""
    kind = _CLASS_TO_KIND.get(type(value))
    if kind is None:
        return value
    payload = dict(value.__dict__)
    payload["kind"] = kind
    return payload


def param_values_from_dict(data: Any) -> Any:
    """Inverse of :func:`param_values_to_dict`; passes through anything that isn't a tagged dict."""
    if not isinstance(data, dict) or "kind" not in data:
        return data
    kind = data["kind"]
    cls = _KIND_TO_CLASS.get(kind)
    if cls is None:
        raise ValueError(f"Unknown parameter value kind: {kind!r}")
    fields = {k: v for k, v in data.items() if k != "kind"}
    return cls(**fields)
