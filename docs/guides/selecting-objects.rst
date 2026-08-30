Selecting objects to export
============================

What counts as exportable
---------------------------

Only objects deriving from ``PartDesign::Body`` or ``Part::Feature`` are ever offered as
candidates.

Two ways to add objects
-------------------------

**"From Selection"** reads whatever is currently selected in the 3D view or the tree, with no
dialog at all: the fastest path if you already have the right objects selected.

**"+"** opens a dedicated **"Add Objects"** picker: a filterable tree view of the whole
document.

.. figure:: ../_static/add-objects-tree.png
   :alt: the "Add Objects" tree picker, showing the "Show only finished parts" checkbox, a grayed-out already-selected item, and the "Or reference by name/label" field
   :align: center
   :scale: 50 %

The tree picker
-----------------

The tree mirrors your document's own group-based nesting. A checkbox, **"Show only finished
parts (hide intermediate features)"**, is checked by default and hides objects that are
referenced by another exportable candidate. In practice, this means Body-internal features
(Pad, Pocket, Fillet, ...) and intermediate steps of a boolean or transform chain are hidden,
so you see only the finished results.

.. note::

   Being referenced by an *organizational* container (an ``App::Part`` or an
   ``App::DocumentObjectGroup``) does **not** count as "intermediate." Grouping your bodies
   for tidiness doesn't hide them from this picker.

Objects already in your export list show up grayed out rather than disappearing entirely, so
you can always see what's already selected without losing your place in the tree.

The escape hatch
-------------------

The **"Or reference by name/label:"** field at the bottom bypasses every filter above. Type
an object's internal name or its label directly. Use this for anything the tree's filtering
rules don't fit, such as intentionally exporting an intermediate feature.

.. seealso::

   the :ref:`objects panel <objects-panel-section>` in :doc:`/dialog-overview` for where these
   controls sit relative to the rest of the dialog, and the
   :ref:`combine/split rules <combine-split-export>` in :doc:`exporting` for what happens once
   you have more than one object selected.
