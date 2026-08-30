Troubleshooting
===============

A format I just enabled doesn't show up in the Formats list
----------------------------------------------------------------

The list of available export formats is built once per FreeCAD session, from whatever formats
are registered at that moment. If you loaded a new workbench (or add-on) that registers a
format *after* first opening the Grid Params Export dialog, it won't appear until you restart
FreeCAD.

.. _format-not-taking-effect:

My per-item format choice doesn't seem to take effect
-----------------------------------------------------------

Check the two global preferences in **Edit ▸ Preferences ▸ Grid Params Export**: "Enforce
preferred formats" always overrides a per-item choice, and "Allow choosing export formats per
grid item" must be on for a per-item override to apply at all. See the
:ref:`full precedence table <format-precedence-table>` in :doc:`guides/preferences`.

.. _duplicate-names-troubleshooting:

Export refuses to run because of duplicate variation names
------------------------------------------------------------

Your naming template doesn't distinguish every combination your grid produces. The status line
warns you early ("Duplicated names for some variations"), but that's only a heads-up; the
**Export** button itself stays clickable, and the block only happens when you actually try to
export. See the :ref:`naming templates <naming-templates-section>` section of
:doc:`guides/parameter-grids` for how naming templates and placeholders work.

"One file per part" gave me a single file with no body name in it
----------------------------------------------------------------------

This is expected with one object selected: combine and split produce identical output in
that case, since there's nothing to disambiguate. Select 2 or more objects to see the split
take effect. See the :ref:`combine/split rules <combine-split-export>` in
:doc:`guides/exporting`.

I get a warning that my saved configuration is newer than this addon supports
------------------------------------------------------------------------------------

This happens if a document was last saved by a newer version of Grid Params Export than the
one you currently have installed. The dialog falls back to a blank configuration for that
session, but your actual saved data is left untouched; update the addon and reopen the
document to get it back. See the :ref:`schema versioning <schema-versioning-section>` section
of :doc:`concepts/persistence-and-versioning`.
