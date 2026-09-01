Contributing
============

Development install
-----------------------

Same as a manual install (see :doc:`installation`): symlink this repository into FreeCAD's
``Mod/`` folder and restart FreeCAD after each change to ``freecad/gridparams/init_gui.py`` or
anything imported at startup. Most changes inside ``freecad/gridparams/gui/`` take effect after
just reopening the dialog.

Running the tests
---------------------

.. code-block:: bash

   python -m pytest tests/

The ``freecad.gridparams.core`` package has no dependency on ``FreeCAD``/``FreeCADGui`` at all
and is fully unit-tested standalone. The ``gui`` package is exercised through
``tests/conftest.py``'s stubbed ``FreeCAD``/``FreeCADGui`` modules and ``tests/fakes.py``'s
duck-typed doubles, rather than a real FreeCAD install. If you're adding new behavior, prefer
putting the logic in ``core`` and covering it there first; it's the easier package to test
thoroughly.

Pre-commit hooks
--------------------

.. code-block:: bash

   pre-commit install

This repository runs ``ruff``, ``ruff-format``, ``pyupgrade`` (targeting Python 3.11+),
``complexipy``, and ``mypy`` on every commit.

Architecture
---------------

The codebase is split into two packages with a clear boundary:

- ``freecad/gridparams/core/``: pure Python, no ``FreeCAD``/``FreeCADGui`` import anywhere.
  Grid expansion, naming, export planning, and persistence serialization all live here.
- ``freecad/gridparams/gui/``: the Qt/FreeCADGui integration layer: dialogs, commands, the
  preferences page, and the toolbar manipulator. ``gui/runner.py`` is the seam where the two
  meet; it's the only place that both calls into ``core`` and talks to a live FreeCAD
  document.

Building these docs locally
-------------------------------

.. code-block:: bash

   pip install -r docs/requirements.txt
   sphinx-build -b html docs docs/_build/html

Then open ``docs/_build/html/index.html``.
