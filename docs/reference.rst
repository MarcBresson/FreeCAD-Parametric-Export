Reference
=========

Quick, precise tables for everything covered narratively in the guides. See
:doc:`guides/parameter-grids`, :doc:`guides/exporting`, and :doc:`guides/preferences` for the
full explanations behind each of these.

Naming template placeholders
-------------------------------

.. list-table::
   :header-rows: 1

   * - Placeholder
     - Resolves to
   * - ``{base_name}``
     - The configuration's Base Name field.
   * - ``{document_label}``
     - The current document's label.
   * - ``{<parameter name>}``
     - One placeholder per parameter used in that grid item, e.g. ``{Length}``.
   * - ``{body_label}`` / ``{body_name}``
     - The Label / internal Name of the object being exported for this file. If objects
       are combined into a single file, the first object is used. See
       :ref:`per-part-filename-template` in :doc:`guides/preferences`.

Referencing a placeholder that isn't available raises an error listing exactly which
placeholders are valid for that item.

.. _value-kind-syntax-table:

Value-kind syntax
--------------------

.. list-table::
   :header-rows: 1

   * - Kind
     - Syntax
     - Produces
   * - ``Fixed``
     - a single value
     - that one value, always.
   * - ``List``
     - comma-separated values
     - each value, in the order given.
   * - ``LinSpace``
     - ``start, stop, num``
     - ``num`` evenly spaced values from ``start`` to ``stop``, inclusive of both ends
       (``numpy.linspace`` semantics). ``num <= 1`` yields just ``[start]``.
   * - ``Range``
     - ``start, stop, step`` (``step`` defaults to ``1``)
     - an arithmetic sequence from ``start`` to ``stop``, inclusive of ``stop`` if landed on
       exactly; ``step`` may be negative. A ``step`` of ``0`` raises an error.

Filename sanitization
------------------------

Every resolved variation name is sanitized before becoming a filename:

- The characters ``< > : " / \ | ? *`` are each replaced with ``_``.
- The result is then trimmed of leading/trailing whitespace.

Combine/split filename pattern
----------------------------------

.. list-table::
   :header-rows: 1

   * - Situation
     - Resulting file stem
   * - Combined, or 0–1 objects selected
     - ``<variation name>``
   * - Split, default "Per-part filename template" (``{name} - {body_label}``)
     - ``<variation name> - <body label>``
   * - Split, "Per-part filename template" set to ``{body_label} - {name}``
     - ``<body label> - <variation name>``

"Split" only applies with 2 or more objects selected; see the
:ref:`combine/split rules <combine-split-export>` in :doc:`guides/exporting`. The template
itself is a global preference, not a per-config setting -- see below.

Preferences quick reference
-------------------------------

All four settings live under the FreeCAD parameter group
``User parameter:BaseApp/Preferences/Mod/GridParams``.

.. list-table::
   :header-rows: 1

   * - Setting
     - Default
     - Effect
   * - Grid export relative path
     - *(empty)*
     - Where **Export** writes files, relative to the document's own folder. Empty = same
       folder as the document.
   * - Preferred formats
     - *(empty, falls back to 3MF)*
     - The format(s) used unless a per-item override applies.
   * - Allow choosing export formats per grid item
     - Off
     - Whether a saved per-item override is actually used.
   * - Per-part filename template
     - ``{name} - {body_label}``
     - How each part's filename is built when exporting one file per part. Placeholders:
       ``{name}`` (variation name), ``{body_label}`` (the part's Label), and ``{body_name}``
       (the part's internal Name).

See the :ref:`full precedence table <format-precedence-table>` in :doc:`guides/preferences`
for worked examples.
