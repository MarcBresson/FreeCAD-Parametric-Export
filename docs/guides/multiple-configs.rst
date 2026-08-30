Multiple configurations in one document
==========================================

A single document can hold more than one Grid Params Export configuration. For example, one
per body in a multi-body assembly, each with its own grid and its own export settings.
Clicking **"New Grid Export Config..."** again creates another one alongside any existing
configuration; it doesn't replace it.

Each configuration is a normal object in the tree (labeled "Grid Params Config", auto-suffixed
if that label is already taken), just hidden from the 3D view since it has no geometry of its
own.

.. _tree-context-menu:

The tree context menu
------------------------

Right-clicking a configuration object in the tree gives you:

.. figure:: ../_static/context-menu.png
   :alt: the right-click context menu on a Grid Params Config tree object
   :align: center
   :scale: 50 %

- **"Edit..."**: opens the dialog for that configuration.
- **"Export using config"**: runs an export directly, without opening the dialog.
- **"Export to..."**: the one-off, pick-a-folder-and-format export, also without opening the
  dialog.

Double-clicking the object in the tree also opens its dialog, same as "Edit...".

.. seealso::

   :doc:`/concepts/persistence-and-versioning` for where each configuration's data actually
   lives inside the document.
