"""Cartesian-product expansion over a parameter grid, mirroring sklearn.model_selection.ParameterGrid.

Given a dict, every value is expanded to a list (via ``normalize_param_values``) and the full
Cartesian product is taken. Given a list of dicts, each dict is expanded independently and the
results are concatenated -- a list of dicts means "independent alternatives", never a cross
product between dicts. This module never inspects Fixed/ValueList/LinSpace/Range directly; it
only ever sees concrete lists, keeping it decoupled from `values.py`.
"""

from collections.abc import Iterator, Mapping
from itertools import product
from typing import Any

from .values import normalize_param_values


class ParameterGrid:
    def __init__(self, param_grid: Mapping[str, Any] | list[Mapping[str, Any]]) -> None:
        if isinstance(param_grid, Mapping):
            param_grid = [param_grid]
        self.param_grid = [
            {key: normalize_param_values(value) for key, value in grid_dict.items()}
            for grid_dict in param_grid
        ]

    def __iter__(self) -> Iterator[dict[str, Any]]:
        for grid_dict in self.param_grid:
            items = sorted(grid_dict.items())
            if not items:
                yield {}
                continue
            keys, value_lists = zip(*items)
            for combination in product(*value_lists):
                yield dict(zip(keys, combination))

    def __len__(self) -> int:
        total = 0
        for grid_dict in self.param_grid:
            product_size = 1
            for values in grid_dict.values():
                product_size *= len(values)
            total += product_size
        return total
