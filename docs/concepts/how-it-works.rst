How an export actually runs
==============================

This is the full lifecycle behind the **Export** button, start to finish.

1. **Expand the grid into variations.** Every grid item is expanded (see the
   :ref:`exact cross-product rules <cross-product-rules>`), and each resulting
   parameter combination is resolved into a named variation via its naming template.
2. **Check for duplicate names.** If any two variations would resolve to the same name, the
   export is aborted here, before anything else happens; see the
   :ref:`warning about duplicate names <duplicate-variation-names-warning>`.
3. **Capture the VarSet's current values**, for every parameter that appears anywhere in the
   grid. This snapshot is what gets restored at the very end, no matter what happens in
   between.
4. **For each variation, in order:**

   a. Apply that variation's values to the VarSet.
   b. Recompute the document.
   c. Build one export job per output file for this variation (one job if combined or only one
      object is selected, one job per object otherwise; see the
      :ref:`combine/split rules <combine-split-export>`).
   d. Resolve the effective format list for each job (see the
      :ref:`format precedence rules <format-precedence-table>`).
   e. Export.

5. **Restore the VarSet**, unconditionally, this step runs whether every variation exported
   cleanly, or something raised partway through.

.. note::

   If a variation fails partway through a batch, the export stops there: later variations in
   the batch are **not** attempted. Files already written by earlier variations are kept;
   only the VarSet's values are guaranteed to end up back where they started.
