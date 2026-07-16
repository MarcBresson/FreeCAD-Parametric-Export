from freecad.gridparams.core.grid import ParameterGrid
from freecad.gridparams.core.values import Fixed, ValueList


def test_single_dict_cartesian_product():
    grid = ParameterGrid({"a": [1, 2], "b": [3, 4]})
    assert list(grid) == [
        {"a": 1, "b": 3},
        {"a": 1, "b": 4},
        {"a": 2, "b": 3},
        {"a": 2, "b": 4},
    ]
    assert len(grid) == 4


def test_list_of_dicts_concatenates_independently():
    grid = ParameterGrid([{"a": [1]}, {"b": [2, 3]}])
    assert list(grid) == [{"a": 1}, {"b": 2}, {"b": 3}]
    assert len(grid) == 3


def test_empty_dict_yields_one_empty_combination():
    grid = ParameterGrid({})
    assert list(grid) == [{}]
    assert len(grid) == 1


def test_bare_scalar_and_sampler_values():
    grid = ParameterGrid({"a": 5, "b": ValueList([1, 2])})
    assert list(grid) == [{"a": 5, "b": 1}, {"a": 5, "b": 2}]


def test_fixed_wrapped_scalar_degenerates_to_one_combination():
    grid = ParameterGrid({"a": Fixed(1), "b": Fixed(2)})
    assert list(grid) == [{"a": 1, "b": 2}]
    assert len(grid) == 1


def test_macro_style_literal_dicts_no_expansion():
    grid = ParameterGrid(
        [
            {"Base_CableLength": 1000, "Base_CableThickness": 3},
            {"Base_CableLength": 1500, "Base_CableThickness": 4},
        ]
    )
    assert list(grid) == [
        {"Base_CableLength": 1000, "Base_CableThickness": 3},
        {"Base_CableLength": 1500, "Base_CableThickness": 4},
    ]
    assert len(grid) == 2
