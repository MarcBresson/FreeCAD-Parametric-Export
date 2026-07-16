from freecad.gridparams.core.config import ExportSettings
from freecad.gridparams.core.export_plan import build_export_jobs_for_variation, sanitize_filename
from freecad.gridparams.core.variation import Variation


def test_sanitize_filename_strips_invalid_characters():
    result = sanitize_filename('Name: <bad>/chars*?"|\\')
    assert result.startswith("Name")
    assert not any(char in result for char in '<>:"/\\|?*')


def test_combine_true_produces_single_job_with_all_objects():
    variation = Variation(name="XS", params={})
    settings = ExportSettings(combine=True, selected_object_names=["Body001", "Body003"])
    jobs = build_export_jobs_for_variation(variation, settings)
    assert len(jobs) == 1
    assert jobs[0].output_stem == "XS"
    assert jobs[0].objects == ["Body001", "Body003"]


def test_combine_false_produces_one_job_per_object():
    variation = Variation(name="XS", params={})
    settings = ExportSettings(combine=False, selected_object_names=["Body001", "Body003"])
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


def test_prepend_body_name_puts_body_before_variation_name():
    variation = Variation(name="XS", params={})
    settings = ExportSettings(
        combine=False, selected_object_names=["Body001", "Body003"], body_name_placement="prepend"
    )
    jobs = build_export_jobs_for_variation(variation, settings)
    assert jobs[0].output_stem == "Body001 - XS"
    assert jobs[1].output_stem == "Body003 - XS"


def test_prepend_body_name_has_no_effect_when_not_split():
    variation = Variation(name="XS", params={})
    settings = ExportSettings(
        combine=False, selected_object_names=["Body001"], body_name_placement="prepend"
    )
    jobs = build_export_jobs_for_variation(variation, settings)
    assert len(jobs) == 1
    assert jobs[0].output_stem == "XS"
