import pytest

from freecad.gridparams.core.naming import NamingTemplateError, resolve_name


def test_literal_name_resolves_unchanged():
    assert resolve_name("XS", base_name="Cable winder", params={}) == "XS"


def test_template_substitutes_base_name_and_params():
    result = resolve_name(
        "{base_name} - CableLength{Base_CableLength}",
        base_name="Cable winder",
        params={"Base_CableLength": 1000},
    )
    assert result == "Cable winder - CableLength1000"


def test_unknown_placeholder_raises():
    with pytest.raises(NamingTemplateError):
        resolve_name("{unknown_param}", base_name="Base", params={"a": 1})
