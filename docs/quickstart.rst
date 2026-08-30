Quickstart
==========

This walks through exporting a handful of parametrized variants of a model, end to end. It
assumes you already have Grid Params Export :doc:`installed <installation>`.

1. Prerequisites
-----------------

Open (or create) a FreeCAD document containing:

- at least one exportable object, a ``PartDesign::Body`` or a ``Part::Feature``;
- an ``App::VarSet`` with at least one numeric property that drives that object (for example,
  a length used by a Pad or a Sketch constraint).

2. Open the dialog
--------------------

Click **"New Grid Export Config..."** in the **Structure** toolbar.

.. figure:: _static/toolbar-icon.png
   :alt: the Structure toolbar with "New Grid Export Config..." visible next to "Create a variable set"
   :align: center
   :scale: 50 %

3. Pick your VarSet
----------------------

The dialog opens with a new, empty configuration. Pick your ``App::VarSet`` from the **VarSet**
combo in the header row.

4. Build a grid item
----------------------

With the first grid item selected on the left, add a parameter: pick one of your VarSet's
properties in the **Parameter** column, set **Kind** to ``LinSpace`` or ``Range``, and type a
value like ``10, 20, 5`` (for ``LinSpace``: start, stop, num) or ``10, 20, 2`` (for ``Range``:
start, stop, step). The status line below the table updates live to show how many variations
that produces.

See :doc:`guides/parameter-grids` for the full set of value kinds and how naming templates
work.

5. Choose what to export
--------------------------

In the export panel, click **"From Selection"** to use whatever is currently selected in the
3D view or tree, or click **"+"** to pick objects from a filtered tree view instead. See
:doc:`guides/selecting-objects` for details on that tree picker.

6. Choose a format (optional)
-------------------------------

By default, export uses your global "preferred formats" preference. You can leave this as-is
for now; see :doc:`guides/preferences` later if you want per-item control.

7. Export
---------

Click **Export**. This saves your configuration to the document and exports every resulting
variation to your export folder: one file (or one file per object) per variation, named from
your naming template.

8. Check the results
----------------------

Look in your export folder for one file per resolved variation name. Open your VarSet's
properties again: they're back to whatever they were before you clicked Export, Grid Params
Export always restores them, whether the export succeeded or failed partway through. See
:doc:`concepts/how-it-works` for why.

.. seealso::

   :doc:`dialog-overview` gives a full tour of every control you just used, including which
   ones only appear once you've selected more than one object. :doc:`guides/multiple-configs`
   covers adding a second, independent configuration to the same document.
