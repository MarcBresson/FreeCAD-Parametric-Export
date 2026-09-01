from tests.fakes import FakeDocument, consume, group

from freecad.cartegrid.gui import object_tree


def test_is_intermediate_true_for_body_internal_feature():
    doc = FakeDocument()
    body = doc.addObject("PartDesign::Body", "Body")
    pad = doc.addObject("Part::Feature", "Pad")
    group(body, pad)

    assert object_tree.is_intermediate(pad)
    assert not object_tree.is_intermediate(body)


def test_is_intermediate_false_when_only_consumer_is_a_container():
    doc = FakeDocument()
    part_container = doc.addObject("App::Part", "Part")
    body = doc.addObject("PartDesign::Body", "Body")
    group(part_container, body)

    assert not object_tree.is_intermediate(body)


def test_is_intermediate_false_for_standalone_tip_object():
    doc = FakeDocument()
    box = doc.addObject("Part::Feature", "Box")
    cylinder = doc.addObject("Part::Feature", "Cylinder")
    cut = doc.addObject("Part::Feature", "Cut")
    consume(cut, box, cylinder)

    assert object_tree.is_intermediate(box)
    assert object_tree.is_intermediate(cylinder)
    assert not object_tree.is_intermediate(cut)


def test_build_object_tree_nests_body_features_and_hides_when_only_finished():
    doc = FakeDocument()
    body = doc.addObject("PartDesign::Body", "Body")
    pad = doc.addObject("Part::Feature", "Pad")
    group(body, pad)

    full = object_tree.build_object_tree(doc.Objects, only_finished=False)
    assert [node.obj.Name for node in full] == ["Body"]
    assert [child.obj.Name for child in full[0].children] == ["Pad"]

    finished_only = object_tree.build_object_tree(doc.Objects, only_finished=True)
    assert [node.obj.Name for node in finished_only] == ["Body"]
    assert finished_only[0].children == []


def test_build_object_tree_prunes_empty_container_branches():
    doc = FakeDocument()
    part_container = doc.addObject("App::Part", "Part")
    sketch = doc.addObject("Sketcher::SketchObject", "Sketch")
    group(part_container, sketch)

    roots = object_tree.build_object_tree(doc.Objects, only_finished=False)
    assert roots == []


def test_build_object_tree_excludes_names_in_excluded_set():
    doc = FakeDocument()
    box = doc.addObject("Part::Feature", "Box")
    doc.addObject("Part::Feature", "Cylinder")

    roots = object_tree.build_object_tree(doc.Objects, excluded_names={box.Name})
    assert [node.obj.Name for node in roots] == ["Cylinder"]


def test_build_object_tree_handles_objects_without_a_group_property():
    # Real Part::Feature objects (Box, Cylinder, booleans...) have no Group property
    # at all -- only container-like types (App::Part, PartDesign::Body, ...) do.
    doc = FakeDocument()
    box = doc.addObject("Part::Feature", "Box")
    del box.Group

    roots = object_tree.build_object_tree(doc.Objects)
    assert [node.obj.Name for node in roots] == ["Box"]


def test_build_object_tree_marks_already_selected_instead_of_hiding():
    doc = FakeDocument()
    box = doc.addObject("Part::Feature", "Box")
    doc.addObject("Part::Feature", "Cylinder")

    roots = object_tree.build_object_tree(
        doc.Objects, already_selected_names={box.Name}
    )
    by_name = {node.obj.Name: node for node in roots}
    assert by_name["Box"].already_selected
    assert not by_name["Box"].is_candidate
    assert by_name["Cylinder"].is_candidate
    assert not by_name["Cylinder"].already_selected


def test_build_object_tree_shows_already_selected_even_when_only_finished():
    doc = FakeDocument()
    body = doc.addObject("PartDesign::Body", "Body")
    pad = doc.addObject("Part::Feature", "Pad")
    group(body, pad)

    roots = object_tree.build_object_tree(
        doc.Objects, already_selected_names={pad.Name}, only_finished=True
    )
    assert [node.obj.Name for node in roots] == ["Body"]
    children = roots[0].children
    assert [child.obj.Name for child in children] == ["Pad"]
    assert children[0].already_selected
    assert not children[0].is_candidate
