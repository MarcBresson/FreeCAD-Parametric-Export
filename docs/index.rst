CarteGrid
===================

.. figure:: ../Resources/logos/cartegrid-logo.png
   :alt: CarteGrid logo
   :align: center
   :width: 200px

**CarteGrid** is a FreeCAD addon for batch-exporting parametrized variants of a
model. You define a parameter grid over an ``App::VarSet``'s properties, and the addon expands
it into named **variations**: for each one, it applies the parameter values, recomputes the
document, and exports a chosen set of objects to one or more files. Export formats are
whatever FreeCAD itself can produce (STEP, STL, IGES, OBJ, 3MF, and anything else a loaded
workbench registers); nothing is hardcoded to a single format.

.. figure:: _static/main-dialog.png
   :alt: the full dialog
   :align: center

   The full dialog, with all panels and controls visible.

Why CarteGrid?
------------------------

- **A familiar parameter-grid model.** Grid items expand the same way
  `scikit-learn's ParameterGrid <https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.ParameterGrid.html>`_
  does: one item's parameters are fully cross-produced, and multiple items are independent
  alternatives, never crossed with each other.
- **Flexible naming, with duplicate protection.** Name each variation with a template built
  from your parameters; export refuses to run if two variations would resolve to the same
  file name.
- **A tree-based object picker** that understands your model's structure, hiding
  Body-internal features by default so you only see finished, exportable parts.
- **Per-format export preferences**, resolved through a clear precedence rule between a
  global "preferred formats" setting and a per-grid-item override.
- **Your document is never left in a strange state.** Whatever your VarSet's values were
  before you clicked Export, they're restored afterward, even if the export fails partway
  through.
- **A VarSet-to-CSV export**, handy for generating parameter documentation alongside your
  exported files.

Get started with the :doc:`quickstart`, or jump straight to
:doc:`installation` if you already know the addon.

.. toctree::
   :maxdepth: 1
   :caption: Getting Started

   installation
   quickstart
   dialog-overview

.. toctree::
   :maxdepth: 2
   :caption: Guides

   guides/parameter-grids
   guides/selecting-objects
   guides/exporting
   guides/preferences
   guides/multiple-configs

.. toctree::
   :maxdepth: 2
   :caption: Concepts

   concepts/how-it-works
   concepts/persistence-and-versioning

.. toctree::
   :maxdepth: 1
   :caption: Reference

   reference
   troubleshooting
   changelog
   contributing

.. toctree::
   :maxdepth: 1
   :caption: Links

   GitHub <https://github.com/MarcBresson/cartegrid>
   Issues <https://github.com/MarcBresson/cartegrid/issues>
