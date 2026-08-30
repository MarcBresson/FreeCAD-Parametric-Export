Exporting variations
=====================

.. _combine-split-export:

One file, or one file per part
---------------------------------

Once two or more objects are selected for export, a **"Multi part export per variation:"**
combo appears with two options:

- **"Combine parts into one file"**: every selected object goes into a single output file per
  variation.
- **"One file per part"** (the default): each object gets its own output file, with its body
  label placed into the variation name (see below) so the files don't collide.

.. note::

   With one object selected, both options produce exactly the same output: a single
   file, with no body-label suffix at all. The split only has a visible effect once you have 2
   or more objects selected. (This row is hidden from the dialog entirely until you have 2+
   objects selected; see the :ref:`exact visibility rules <objects-panel-visibility-rules>` in
   :doc:`/dialog-overview`; this page focuses on the filenames that result.)

Where the body label goes
----------------------------

When exporting one file per part, where the body label lands in the filename is controlled by
the global **"Per-part filename template"** preference -- see
:ref:`per-part-filename-template` in :doc:`preferences` for the placeholders and examples.

This uses the object's **Label** (the human-readable name you see in the tree), not its
internal Name. Either way, characters that aren't valid in filenames
(``< > : " / \ | ? *``) are replaced with ``_``.

Choosing export formats
-------------------------

The Formats button next to the export panel controls which format(s) this specific grid item
exports to, but what it shows and whether it's even clickable depends on your global
preferences. The :ref:`full precedence table <format-precedence-table>` in :doc:`preferences`
has worked examples; this page assumes you're using whatever your preferences already resolve
to.

Once you've saved a per-item override on a grid item, a small red **✖** button appears next to
the Formats button. Click it to remove that item's override in one step, instead of reopening
the format picker and deselecting everything -- the item then falls back to the preferred
formats.

Running the export
---------------------

Five buttons in the footer:

- **Save**: persists your configuration to the document and shows a confirmation popup.
  Doesn't export anything.
- **Save and Close**: persists silently, then closes the dialog.
- **Export**: persists your configuration, then runs the export using your resolved
  preferences and export folder, disabling the dialog while it runs.
- **Export to...** (tooltip: "Pick a folder and export all variations there directly"): a
  one-off export to a folder you pick on the spot, using a single format you choose right
  then. This bypasses every format preference entirely; it's meant for a quick one-time
  export, not your regular workflow.
- **Close**: closes the dialog.

.. warning::

   **Close** does not save. Any edits made since your last **Save**, **Save and Close**, or
   **Export** are discarded.

Where files are written
--------------------------

The regular **Export** button writes to a folder resolved from the global "Export
relative path" preference (:doc:`preferences`), always **relative to the document's own
folder**. As the preference page's own tooltip puts it:

    "This applies to every document; no export path is stored inside .FCStd files"

This is deliberate: an absolute path never gets baked into a document you might share with
someone else, whose files live somewhere completely different on disk.

Your VarSet is always restored
---------------------------------

Whatever your VarSet's values were right before you clicked Export, they're back to that
afterward, even if the export fails partway through a large batch. See
:doc:`/concepts/how-it-works` for exactly when this capture and restore happen.

.. _csv-export-section:

Exporting VarSet parameters to CSV
-------------------------------------

The **"Export VarSet to CSV..."** button lives in the header row, next to the VarSet combo.
It dumps every property of the selected VarSet (name, property group, value, unit, comment,
...) to a CSV file, which is handy for generating parameter documentation to go alongside
your exported models.

.. todo::

   Screenshot: the VarSet CSV export dialog, showing the column checkboxes.

Checkboxes let you choose which columns to include, and whether to include "private"
variables: a variable is considered private if its name **or** its property group starts with
an underscore (``_``), and these are excluded by default.

For instance, the following CSV was generated from `this file <https://www.printables.com/model/542792-parametric-travel-soap-box>`_ with the export parameters used in the screenshot here-above:

.. csv-table:: Example output
   :header: "Name", "Group", "Value", "Unit", "FreeCAD Unit", "Comment"
   :widths: 20, 12, 8, 8, 25, 30

   "Model_BorderAdditionalHeight", "Model", "1.0", "mm", "Unit: mm (1,0,0,0,0,0,0,0) [Length]", "Controls the height of the border that surrounds the model. It can prevent the soap from running away."
   "Model_BorderThickness", "Model", "2.0", "mm", "Unit: mm (1,0,0,0,0,0,0,0) [Length]", "Controls the thickness of the border that surrounds the model. It has an effect iven if Model_BorderAdditionalHeight is set to 0."
   "Soap_Length", "Soap", "100.0", "mm", "Unit: mm (1,0,0,0,0,0,0,0) [Length]", ""
   "Soap_Width", "Soap", "100.0", "mm", "Unit: mm (1,0,0,0,0,0,0,0) [Length]", ""
   "WaterEvacuation_Enable", "WaterEvacuation", "True", "", "", ""
   "WaterEvacuation_LengthPercentOfSoap", "WaterEvacuation", "0.9", "", "", ""
   "WaterEvacuation_Width", "WaterEvacuation", "2.0", "mm", "Unit: mm (1,0,0,0,0,0,0,0) [Length]", ""
