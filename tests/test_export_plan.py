import pytest

from freecad.cartegrid.core.config import ExportSettings
from freecad.cartegrid.core.export_plan import (
    apply_body_name_template,
    build_export_jobs_for_variation,
    sanitize_filename,
)
from freecad.cartegrid.core.naming import NamingTemplateError, resolve_name
from freecad.cartegrid.core.variation import Variation


def _templated_variation(template, base_name="Base", params=None):
    """Mimics what expand_config produces for a variation whose naming template references
    {body_label}/{body_name}: `name` is the "" placeholder identity resolution, and
    name_template/base_name are kept so build_export_jobs_for_variation can re-resolve with
    the real body at export time."""
    params = params or {}
    identity_params = {**params, "body_label": "", "body_name": ""}
    return Variation(
        name=resolve_name(template, base_name, identity_params),
        params=params,
        name_template=template,
        base_name=base_name,
    )


def test_sanitize_filename_strips_invalid_characters():
    result = sanitize_filename('Name: <bad>/chars*?"|\\')
    assert result.startswith("Name")
    assert not any(char in result for char in '<>:"/\\|?*')


def test_combine_true_produces_single_job_with_all_objects():
    variation = Variation(name="XS", params={})
    settings = ExportSettings(
        combine=True, selected_object_names=["Body001", "Body003"]
    )
    jobs = build_export_jobs_for_variation(variation, settings)
    assert len(jobs) == 1
    assert jobs[0].output_stem == "XS"
    assert jobs[0].objects == ["Body001", "Body003"]


def test_combine_false_produces_one_job_per_object_using_default_template():
    variation = Variation(name="XS", params={})
    settings = ExportSettings(
        combine=False, selected_object_names=["Body001", "Body003"]
    )
    jobs = build_export_jobs_for_variation(variation, settings)
    assert len(jobs) == 2
    assert jobs[0].output_stem == "XS - Body001"
    assert jobs[0].objects == ["Body001"]
    assert jobs[1].output_stem == "XS - Body003"
    assert jobs[1].objects == ["Body003"]


def test_single_selected_object_is_never_split_even_if_combine_is_false():
    variation = Variation(name="XS", params={})
    settings = ExportSettings(combine=False, selected_object_names=["Body001"])
    jobs = build_export_jobs_for_variation(variation, settings)
    assert len(jobs) == 1
    assert jobs[0].output_stem == "XS"


def test_body_name_template_controls_placement():
    variation = Variation(name="XS", params={})
    settings = ExportSettings(
        combine=False, selected_object_names=["Body001", "Body003"]
    )
    jobs = build_export_jobs_for_variation(
        variation, settings, body_name_template="{body_label} - {name}"
    )
    assert jobs[0].output_stem == "Body001 - XS"
    assert jobs[1].output_stem == "Body003 - XS"


def test_body_name_template_supports_arbitrary_literal_text():
    variation = Variation(name="XS", params={})
    settings = ExportSettings(
        combine=False, selected_object_names=["Body001", "Body003"]
    )
    jobs = build_export_jobs_for_variation(
        variation, settings, body_name_template="{name}_part-{body_label}"
    )
    assert jobs[0].output_stem == "XS_part-Body001"
    assert jobs[1].output_stem == "XS_part-Body003"


def test_body_name_template_has_no_effect_when_not_split():
    variation = Variation(name="XS", params={})
    settings = ExportSettings(combine=False, selected_object_names=["Body001"])
    jobs = build_export_jobs_for_variation(
        variation, settings, body_name_template="{body_label} - {name}"
    )
    assert len(jobs) == 1
    assert jobs[0].output_stem == "XS"


def test_body_label_is_used_instead_of_internal_name_when_provided():
    variation = Variation(name="XS", params={})
    settings = ExportSettings(
        combine=False, selected_object_names=["Body001", "Body003"]
    )
    jobs = build_export_jobs_for_variation(
        variation,
        settings,
        object_labels={"Body001": "Left Arm", "Body003": "Right Arm"},
    )
    assert jobs[0].output_stem == "XS - Left Arm"
    assert jobs[1].output_stem == "XS - Right Arm"


def test_job_formats_are_carried_from_variation():
    variation = Variation(name="XS", params={}, formats=["step", "stl"])
    settings = ExportSettings(combine=True, selected_object_names=["Body001"])
    jobs = build_export_jobs_for_variation(variation, settings)
    assert jobs[0].formats == ["step", "stl"]


def test_job_formats_default_to_none():
    variation = Variation(name="XS", params={})
    settings = ExportSettings(combine=True, selected_object_names=["Body001"])
    jobs = build_export_jobs_for_variation(variation, settings)
    assert jobs[0].formats is None


def test_body_label_falls_back_to_internal_name_when_missing():
    variation = Variation(name="XS", params={})
    settings = ExportSettings(
        combine=False, selected_object_names=["Body001", "Body003"]
    )
    jobs = build_export_jobs_for_variation(
        variation, settings, object_labels={"Body001": "Left Arm"}
    )
    assert jobs[0].output_stem == "XS - Left Arm"
    assert jobs[1].output_stem == "XS - Body003"


def test_apply_body_name_template_raises_on_unknown_placeholder():
    with pytest.raises(NamingTemplateError):
        apply_body_name_template(
            "{unknown}", name="XS", body_label="Body001", body_name="Body001"
        )


def test_apply_body_name_template_supports_body_name_placeholder():
    result = apply_body_name_template(
        "{name} - {body_name}", name="XS", body_label="Left Arm", body_name="Body001"
    )
    assert result == "XS - Body001"


def test_naming_template_can_reference_body_label_and_body_name():
    """A naming template (item or default) can reference {body_label}/{body_name} directly,
    not just the separate body-name-template preference -- build_export_jobs_for_variation
    re-resolves the template with the real body at export time (see naming.py/config.py)."""
    variation = _templated_variation("{base_name} ({body_label}-{body_name})")
    settings = ExportSettings(
        combine=False, selected_object_names=["Body001", "Body003"]
    )
    jobs = build_export_jobs_for_variation(
        variation,
        settings,
        object_labels={"Body001": "Left Arm"},
        body_name_template="{name}",
    )
    assert jobs[0].output_stem == "Base (Left Arm-Body001)"
    assert jobs[1].output_stem == "Base (Body003-Body003)"


def test_naming_template_body_placeholders_resolve_for_a_single_selected_object():
    """A single selected object is a well-defined body even though there's nothing to
    disambiguate it from (no suffix gets appended) -- {body_label}/{body_name} should still
    resolve to it, not blank out."""
    variation = _templated_variation("{base_name} - {body_label}")
    settings = ExportSettings(combine=False, selected_object_names=["Body001"])
    jobs = build_export_jobs_for_variation(
        variation, settings, object_labels={"Body001": "Left Arm"}
    )
    assert len(jobs) == 1
    assert jobs[0].output_stem == "Base - Left Arm"


def test_naming_template_body_placeholders_use_first_object_when_combined():
    """When 2+ objects are combined into one file, there's no single body to point to --
    {body_label}/{body_name} deterministically resolve to the first selected object rather
    than leaving the placeholder blank."""
    variation = _templated_variation("{base_name} ({body_label})")
    settings = ExportSettings(
        combine=True, selected_object_names=["Body001", "Body003"]
    )
    jobs = build_export_jobs_for_variation(
        variation, settings, object_labels={"Body001": "Left Arm"}
    )
    assert jobs[0].output_stem == "Base (Left Arm)"


def test_naming_template_body_placeholders_are_blank_when_nothing_is_selected():
    variation = _templated_variation("{base_name} ({body_label})")
    settings = ExportSettings(combine=True, selected_object_names=[])
    jobs = build_export_jobs_for_variation(variation, settings)
    assert jobs[0].output_stem == "Base ()"
