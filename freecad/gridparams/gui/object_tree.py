"""Hierarchy and filtering helpers for the "Add Objects" picker.

Deliberately free of PySide/FreeCAD/FreeCADGui imports -- only touches duck-typed
attributes (isDerivedFrom, Name, Label, Group, InList) any document object exposes,
so it can be unit-tested with plain fakes.
"""

from dataclasses import dataclass, field
from typing import Collection

_EXPORTABLE_BASE_TYPES = ("PartDesign::Body", "Part::Feature")


def is_exportable_candidate(obj):
    return any(obj.isDerivedFrom(t) for t in _EXPORTABLE_BASE_TYPES)


def is_intermediate(obj):
    """True if `obj` is consumed by another exportable object -- a Body-internal
    feature (Pad/Pocket/Fillet...) or an earlier step of a boolean/transform chain --
    rather than a finished, independently-exportable result.

    Only a consumer that is itself an exportable candidate disqualifies `obj`, so this
    doesn't fire just because `obj` is also referenced by an organizational container
    (App::Part/App::DocumentObjectGroup) or an unrelated bystander (TechDraw view,
    Spreadsheet alias, ...).
    """
    return any(is_exportable_candidate(consumer) for consumer in obj.InList)


@dataclass
class TreeNode:
    obj: object
    is_candidate: bool
    already_selected: bool = False
    children: list = field(default_factory=list)


def _build_parent_map(doc_objects):
    parent_of = {}
    for obj in doc_objects:
        for child in getattr(obj, "Group", None) or []:
            parent_of[child.Name] = obj
    return parent_of


def _classify(obj, excluded_names, already_selected_names, only_finished):
    """Return (is_candidate, already_selected) for `obj`."""
    if obj.Name in excluded_names or not is_exportable_candidate(obj):
        return False, False
    if obj.Name in already_selected_names:
        return False, True
    if only_finished and is_intermediate(obj):
        return False, False
    return True, False


def _get_or_create_node(obj, nodes, parent_of, classify_kwargs):
    node = nodes.get(obj.Name)
    if node is not None:
        return node
    is_candidate, already_selected = _classify(obj, **classify_kwargs)
    node = TreeNode(
        obj=obj, is_candidate=is_candidate, already_selected=already_selected
    )
    nodes[obj.Name] = node
    parent = parent_of.get(obj.Name)
    if parent is not None:
        parent_node = _get_or_create_node(parent, nodes, parent_of, classify_kwargs)
        parent_node.children.append(node)
    return node


def _prune_empty_branches(node):
    node.children = [child for child in node.children if _prune_empty_branches(child)]
    return node.is_candidate or node.already_selected or bool(node.children)


def build_object_tree(
    doc_objects,
    excluded_names: Collection[str] = frozenset(),
    already_selected_names: Collection[str] = frozenset(),
    only_finished: bool = False,
):
    """Build the root TreeNodes for a filtered view mirroring the document's own
    Group-based nesting (PartDesign::Body -> its features, App::Part -> its children).

    Every object gets a node so ancestor chains through non-candidate containers are
    preserved; branches with no candidate, no already-selected object, and no
    surviving descendant are pruned. An already-selected object is always shown
    (regardless of `only_finished`) so the user can see it's already in their list,
    but is never a pickable candidate.
    """
    doc_objects = list(doc_objects)
    parent_of = _build_parent_map(doc_objects)
    classify_kwargs = {
        "excluded_names": excluded_names,
        "already_selected_names": already_selected_names,
        "only_finished": only_finished,
    }

    nodes = {}
    for obj in doc_objects:
        _get_or_create_node(obj, nodes, parent_of, classify_kwargs)

    roots = [node for name, node in nodes.items() if parent_of.get(name) is None]
    return [root for root in roots if _prune_empty_branches(root)]
