Preferences and format precedence
====================================

This addon ads new preferences to the FreeCAD interface. They can be found all under the
**Edit ▸ Preferences** menu. The **Edit ▸ Preferences ▸ Grid Params Export** has five settings:

.. todo::

   Screenshot: the Grid Params Export preferences page, all four fields visible.

- **"Grid export relative path"**: where **Export** writes files, relative to the current
  document's own folder. Empty means the same folder as the document.
- **"Preferred formats"**: a checkable list of export formats, built dynamically from
  whatever format any currently loaded FreeCAD module has registered (the same source FreeCAD's
  own **File ▸ Export** uses). If you leave this empty, the addon falls back to 3MF.
- **"Allow choosing export formats per grid item"**: whether the per-item Formats button in
  the dialog is allowed to override the preferred formats at all.
- **"Enforce preferred formats for every export"**: when on, the preferred formats always
  win, no matter what any grid item has saved.
- **"Per-part filename template"**: how each part's output filename is built when exporting
  one file per part (see :ref:`per-part-filename-template` below).

.. note::

   The preferred-formats list is built once per FreeCAD session. A format registered by a
   workbench you load *after* first opening this dialog won't appear in the list until you
   restart FreeCAD.

.. _per-part-filename-template:

Per-part filename template
-------------------------------

When exporting one file per part (see :ref:`combine-split-export` in :doc:`exporting`), this
template controls how each part's filename is built. It has three placeholders, ``{name}``
(the already-resolved variation name), ``{body_label}`` (the part's Label), and ``{body_name}``
(the part's internal Name), combined however you like:

- ``{name} - {body_label}`` (the default) → ``<variation name> - <body label>``
- ``{body_label} - {name}`` → ``<body label> - <variation name>``

Because it's a preference rather than a per-grid-config setting, it applies the same way to
every grid config in every document -- it mainly affects the alphabetical order your exports
land in, so it's set once to match how you like your output folder organized, not tuned per
export.

``{body_label}``/``{body_name}`` are also accepted directly in the Default/Item naming
template itself (see :ref:`naming-templates-section` in :doc:`parameter-grids`), if you'd
rather place the body somewhere other than what this preference appends. If your naming
template already embeds one of them, set this preference to just ``{name}`` to avoid getting
the body label twice.

.. _format-precedence-table:

How the Formats button resolves
-----------------------------------

This is the single most-asked-about mechanic in the addon, so here's exactly what you'll see
on the per-item Formats button for every combination of the two toggles above, crossed with
whether that particular grid item has a saved override:

.. list-table::
   :header-rows: 1

   * - Enforce?
     - Allow per-item?
     - Item has a saved override?
     - Button text
     - Clickable?
   * - On
     - (ignored)
     - (ignored)
     - ``Formats (enforced): <preferred formats>``
     - No
   * - Off
     - On
     - No
     - ``Formats (preferred): <preferred formats>``
     - Yes
   * - Off
     - On
     - Yes
     - ``Formats (this grid instance): <its override>``
     - Yes
   * - Off
     - Off
     - Yes
     - ``Formats (preferred): <preferred formats>``
     - Yes, but inactive
   * - Off
     - Off
     - No
     - ``Formats (preferred): <preferred formats>``
     - No

.. warning::

   Row four is easy to misread. The button stays clickable (so you can inspect or
   change the saved value) but the selected formats are inactive. Turning "Allow
   choosing export formats per grid item" back on reactivates the existing override
   immediately, with nothing to re-pick.

.. seealso::

   the :ref:`Formats button <formats-button-section>` section of :doc:`/dialog-overview` for
   where it sits in the dialog, and the
   :ref:`troubleshooting steps <format-not-taking-effect>` in :doc:`/troubleshooting` if a
   format choice doesn't seem to be taking effect.
