from freecad.cartegrid.core.varset_export import (
    PropertyInfo,
    VarSetCsvOptions,
    filter_properties,
    to_csv_text,
)


def _properties():
    return [
        PropertyInfo(
            name="Length",
            value=10,
            unit="mm",
            freecad_unit="1 mm",
            group="Dimensions",
            comment="overall length",
        ),
        PropertyInfo(
            name="Width",
            value=5,
            unit="mm",
            freecad_unit="1 mm",
            group="Dimensions",
            comment="",
        ),
        PropertyInfo(
            name="_Internal",
            value=True,
            unit="",
            freecad_unit="",
            group="Dimensions",
            comment="not for docs",
        ),
        PropertyInfo(
            name="Ratio",
            value=0.5,
            unit="",
            freecad_unit="",
            group="_Internal",
            comment="private via its group",
        ),
    ]


def test_filter_properties_excludes_private_by_default():
    result = filter_properties(_properties(), VarSetCsvOptions())
    assert [p.name for p in result] == ["Length", "Width"]


def test_filter_properties_includes_private_when_requested():
    result = filter_properties(_properties(), VarSetCsvOptions(include_private=True))
    assert [p.name for p in result] == ["Length", "Width", "_Internal", "Ratio"]


def test_is_private_when_group_starts_with_underscore():
    prop = PropertyInfo(name="Ratio", value=0.5, group="_Internal")
    assert prop.is_private is True


def test_to_csv_text_includes_all_columns_by_default():
    text = to_csv_text(_properties(), VarSetCsvOptions())
    lines = text.splitlines()
    assert lines[0] == "Name,Group,Value,Unit,FreeCAD Unit,Comment"
    assert lines[1] == "Length,Dimensions,10,mm,1 mm,overall length"
    assert lines[2] == "Width,Dimensions,5,mm,1 mm,"
    assert len(lines) == 3  # private properties excluded


def test_to_csv_text_omits_disabled_columns():
    options = VarSetCsvOptions(
        include_unit=False,
        include_freecad_unit=False,
        include_group=False,
        include_comment=False,
    )
    text = to_csv_text(_properties(), options)
    lines = text.splitlines()
    assert lines[0] == "Name,Value"
    assert lines[1] == "Length,10"


def test_to_csv_text_quotes_values_containing_commas():
    properties = [PropertyInfo(name="Note", value="1, 2, 3", comment="a, b")]
    text = to_csv_text(properties, VarSetCsvOptions())
    lines = text.splitlines()
    assert lines[1] == 'Note,,"1, 2, 3",,,"a, b"'
