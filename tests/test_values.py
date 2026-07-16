from freecad.gridparams.core.values import (
    Fixed,
    LinSpace,
    Range,
    ValueList,
    normalize_param_values,
    param_values_from_dict,
    param_values_to_dict,
)


def test_fixed_to_list():
    assert Fixed(5).to_list() == [5]


def test_value_list_to_list():
    assert ValueList([1, 2, 3]).to_list() == [1, 2, 3]


def test_linspace_endpoints_and_count():
    assert LinSpace(0, 10, 5).to_list() == [0.0, 2.5, 5.0, 7.5, 10.0]


def test_linspace_single_point():
    assert LinSpace(3, 7, 1).to_list() == [3]


def test_range_inclusive():
    assert Range(0, 10, 5).to_list() == [0, 5, 10]


def test_range_float_step():
    assert Range(0, 1, 0.5).to_list() == [0, 0.5, 1.0]


def test_range_negative_step():
    assert Range(10, 0, -5).to_list() == [10, 5, 0]


def test_range_zero_step_raises():
    import pytest

    with pytest.raises(ValueError):
        Range(0, 10, 0).to_list()


def test_normalize_bare_scalar():
    assert normalize_param_values(4) == [4]


def test_normalize_plain_list():
    assert normalize_param_values([1, 2]) == [1, 2]


def test_normalize_plain_tuple():
    assert normalize_param_values((1, 2)) == [1, 2]


def test_normalize_sampler():
    assert normalize_param_values(Range(0, 4, 2)) == [0, 2, 4]


def test_param_values_roundtrip_fixed():
    original = Fixed(3.5)
    restored = param_values_from_dict(param_values_to_dict(original))
    assert restored == original


def test_param_values_roundtrip_linspace():
    original = LinSpace(0, 1, 3)
    restored = param_values_from_dict(param_values_to_dict(original))
    assert restored == original


def test_param_values_passthrough_plain_scalar():
    assert param_values_to_dict(42) == 42
    assert param_values_from_dict(42) == 42
