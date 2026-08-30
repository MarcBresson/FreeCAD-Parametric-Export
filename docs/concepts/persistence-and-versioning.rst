Where your configuration lives
=================================

Every Grid Params Export configuration is saved as JSON inside a hidden data object in the
``.FCStd`` file itself; there are no sidecar files to lose track of, and copying or sharing
the document takes your grid configuration with it automatically.

Opening the document again, and reopening the dialog, restores exactly what you last saved.

.. _schema-versioning-section:

Schema versioning
---------------------

The saved JSON is stamped with a schema version, so the addon can evolve the shape of what it
saves without breaking documents created by older versions:

- **Opening an older document** silently upgrades its configuration in memory (and re-saves it
  in the new shape the next time you hit Save). You never need to edit anything by hand.
- **Opening a document saved by a newer addon version than the one you have installed** shows
  a warning and falls back to a blank configuration for that dialog session, but it does
  **not** touch or overwrite the still-good saved JSON already in the document.

.. tip::

   Because the newer-version case never overwrites your saved data, updating the addon and
   reopening an old document is always safe: worst case, you see a warning and the dialog
   starts blank until you update.
