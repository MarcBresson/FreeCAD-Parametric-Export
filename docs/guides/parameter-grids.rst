Building a parameter grid
==========================

A grid is a list of **items**. Each item is one dict of ``{parameter_name: value}``, and how
items combine follows `scikit-learn's ParameterGrid
<https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.ParameterGrid.html>`_
semantics exactly.

.. _cross-product-rules:

One item, cross-produced; many items, concatenated
-----------------------------------------------------

Within a single item, every parameter is fully cross-produced against every other parameter in
that same item. Across items, the results are independent alternatives that get concatenated,
**never** crossed with each other.

For example, with two items:

.. code-block:: text

   Item 1: Length = LinSpace(10, 20, num=2)   ->  10, 20
           Width  = List(5, 8)                ->  5, 8

   Item 2: Length = Fixed(100)                ->  100

This produces **5** variations, not 6:

.. code-block:: text

   Length=10, Width=5      \
   Length=10, Width=8       |  from item 1 (2 x 2 = 4 variations)
   Length=20, Width=5       |
   Length=20, Width=8      /
   Length=100               -- from item 2 (1 variation), independent of item 1's Width

If you wanted ``Length=100`` combined with every ``Width``, it would need to be a third value
in item 1's own ``Length`` list, not a second item: a second item is a fork, not an extra
dimension of the same cross product.

Value kinds
-----------

The **Kind** column in the dialog offers four options:

``Fixed``
   A single, unvarying value.

``List``
   An explicit, unordered set of values you enumerate directly (e.g. ``1000, 1500, 2000``).

``LinSpace(start, stop, num)``
   ``num`` evenly spaced values between ``start`` and ``stop``, **inclusive of both ends**, following
   the same convention as ``numpy.linspace``. If ``num`` is ``1`` or less, you just get
   ``[start]``.

``Range(start, stop, step=1)``
   An arithmetic sequence from ``start`` to ``stop``, inclusive of ``stop`` if the steps land
   on it exactly. ``step`` can be negative to count down.

   .. warning::

      A ``step`` of ``0`` raises an error rather than looping forever or silently doing
      nothing.

See the :ref:`exact syntax table <value-kind-syntax-table>` in :doc:`/reference`.

.. _naming-templates-section:

Naming templates
-----------------

Each item has an optional naming template; if left blank, it falls back to the configuration's
default template (``{base_name}`` out of the box). Templates use Python's ``str.format``
syntax, with these placeholders available:

- ``{base_name}``: the Base Name field.
- ``{document_label}``: the current document's label.
- one placeholder per parameter name used in *that* grid item (e.g. ``{Length}``).

If you reference a placeholder that isn't available (a typo, or a parameter that only exists
in a different item) the status line shows an error message that lists exactly which
placeholders *are* available for that item, so you don't have to guess.

.. _duplicate-variation-names-warning:

.. warning::

   **Duplicate variation names are a hard block, not just a warning.** Two variations that
   resolve to the identical name would silently overwrite each other's output files, so export
   refuses to run until every name is unique. The status line flags this early
   ("Duplicated names for some variations"), but that's only a heads-up: the **Export**
   button itself stays clickable, and the actual block only fires when you try to export. See
   :doc:`/troubleshooting` if this happens to you.

.. seealso::

   :doc:`/reference` for the naming-placeholder and value-kind syntax tables side by side.
