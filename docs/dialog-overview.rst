The main dialog, piece by piece
================================

This page is a full tour of the Grid Params Export dialog: what every control is, and,
critically, which ones only appear or become enabled under specific conditions. It exists so
that when the dialog looks different from one moment to the next, you know why. For
task-oriented instructions ("how do I get this filename pattern"), see the :doc:`guides
<guides/parameter-grids>` instead; this page sticks to describing the UI itself.

.. todo::

   Screenshot: the full dialog

Header row
----------

- **Base name**: a free-text field, available to naming templates as ``{base_name}``.
- **Default naming template**: the template used by any grid item that doesn't set its own.
- **VarSet**: a combo listing every ``App::VarSet`` in the document, plus an
  **"Export VarSet to CSV"** button next to it (not in the footer, see the
  :ref:`CSV section <csv-export-section>` in :doc:`guides/exporting`).

Grid items panel (left)
------------------------

Always visible. The items list shows one row per grid item, labeled live as
``"<N>. <its own template>"`` or ``"<N>. (uses default template)"`` if it has none, updating
as you type. **Add Item**, **Duplicate Item**, and **Remove Item** sit below it.

.. note::

   **Remove Item** is refused ("At least one item is required.") when only one item remains.
   A grid always needs at least one.

Item detail panel (right)
---------------------------

Always visible, and reflects whichever item is currently selected on the left:

- **Item naming template**: blank means "inherit the default template above."
- **Parameters table**, three columns:

  - **Parameter**: an *editable* combo box pre-filled with the selected VarSet's own
    property names, but it accepts any text you type.

    .. warning::

       Nothing validates that a typed parameter name matches a real property on the VarSet;
       double-check spelling against the VarSet's property list.

  - **Kind**: ``Fixed`` / ``List`` / ``LinSpace`` / ``Range``.
  - **Value**: free text. Its *placeholder* changes with the selected Kind, to remind you of
    the expected format: ``Fixed`` → "e.g. 12", ``List`` → "e.g. 1000, 1500, 2000",
    ``LinSpace`` → "start, stop, num", ``Range`` → "start, stop, step".

  **Add Parameter** / **Remove Parameter** sit below the table.

.. note::

   Switching the VarSet combo refreshes every row's Parameter dropdown to the newly selected
   VarSet's properties, without clearing whatever text you'd already typed.

Status row
----------

Always visible; the text recomputes live as you edit anything above. It's one of three
states:

- ``Error: <message>``, for example, a malformed ``LinSpace``/``Range``, or a naming template
  using a placeholder that doesn't exist for that item.
- ``Duplicated names for some variations``
- ``<N> variation(s)``: the healthy state.

A **"Show Variations"** button next to it opens a read-only preview table of every resolved
variation name, with duplicates highlighted in red.

.. _objects-panel-section:

Objects panel
-------------

The objects table, plus three controls: **"+"** opens the "Add Objects" tree picker (see
:doc:`guides/selecting-objects`), **"-"** removes the selected row(s), and
**"From Selection"** reads the current 3D-view/tree selection directly with no dialog at all.

.. _objects-panel-visibility-rules:

One control below the table is **conditionally visible**:

- **"Multi part export per variation"** row (the combine/split combo and its info button) is
  **completely hidden** if 1 object is selected, and appears only once 2 or more
  objects are in the list.

  .. todo::

     Screenshot pair: the objects panel with 1 objects selected, and with 2+
     objects selected, a before/after comparison

Where the body label lands in the filename (when splitting into one file per part) is a global
preference, not a per-config control here -- see :ref:`per-part-filename-template` in
:doc:`guides/preferences`.

See the :ref:`combine/split rules <combine-split-export>` in :doc:`guides/exporting` for what
these settings actually do to your output filenames.

.. _formats-button-section:

Formats button
--------------

Always visible, never hidden, but its text and whether it's clickable depend on two global
preferences crossed with whether this specific grid item has a saved format override. You'll
see one of these on-screen states:

- ``Formats (enforced): ...``, disabled; the global "enforce" preference always wins.
- ``Formats (preferred): ...``, enabled or disabled depending on context.
- ``Formats (this grid instance): ...``, enabled; this item has its own override in effect.

the :ref:`full precedence table <format-precedence-table>` in :doc:`guides/preferences`
explains each state exactly; this page just tells you the button won't always say (or do) the
same thing.

A small red **✖** button appears immediately to the right of the Formats button whenever this
grid item has a saved per-item override (i.e. whenever the button reads
``Formats (this grid instance): ...`` or the override is inactive but still saved, see
:ref:`the precedence table <format-precedence-table>`). Click it to drop the item's override and
fall back to the preferred formats; it disappears again once there's nothing left to remove.

Footer
------

**Save** / **Save and Close** / **Export** / **Export to...** / **Close**: see
:doc:`guides/exporting` for what each one does in full.

.. warning::

   **Close** does not save. Any edits made since your last **Save**, **Save and Close**, or
   **Export** are discarded when you close the dialog this way.

One dialog per configuration
------------------------------

Only one dialog can be open per configuration object at a time. Reopening the same one,
double-clicking it in the tree, or using its
:ref:`context menu <tree-context-menu>` (:doc:`guides/multiple-configs`),
brings the existing window to the front instead of opening a duplicate. Closing the document
closes any dialogs still open for it.
