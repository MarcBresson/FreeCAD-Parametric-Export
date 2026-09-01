Installation
============

Requirements
------------

FreeCAD 1.1 or newer

Option 1: FreeCAD's Addon Manager
----------------------------------

Open **Tools ▸ Addon Manager** and search for "CarteGrid". If it doesn't show up in
the curated list yet, you can still install it by adding this repository as a custom source:
open the Addon Manager's configuration (the gear icon), add a **custom repository** pointing
at ``https://github.com/MarcBresson/cartegrid``, and it will appear in your
addon list like any other.

Option 2: manual install
-------------------------

Symlink or copy this repository into FreeCAD's user ``Mod/`` folder, then restart FreeCAD.

The most reliable way to find that folder (independent of your OS or FreeCAD version) is to
ask FreeCAD itself, from the **Python console** (View ▸ Panels ▸ Python console):

.. code-block:: python

   import FreeCAD
   print(FreeCAD.getUserAppDataDir())

``Mod/`` is a subfolder of whatever path that prints. Typically, that's:

- **macOS**: ``~/Library/Application Support/FreeCAD/Mod``
- **Linux**: ``~/.local/share/FreeCAD/Mod``; if you installed FreeCAD via Flatpak or Snap,
  your data directory is sandboxed instead (e.g. under
  ``~/.var/app/org.freecad.FreeCAD/...`` for Flatpak); use the Python console command above to
  be sure.
- **Windows**: ``%APPDATA%\FreeCAD\Mod``

On macOS, for example:

.. code-block:: bash

   ln -s "$(pwd)" "$HOME/Library/Application Support/FreeCAD/Mod/CarteGrid"

.. note::

   A manual install doesn't update itself. Pull the latest changes (or re-download and
   re-symlink) whenever you want a newer version; the Addon Manager path handles updates for
   you automatically.

Verifying the install
----------------------

Restart FreeCAD, open (or create) a document, and look for **"Batch Export from Varset..."** in
the **Structure** toolbar, next to "Create a variable set". It's available in any workbench
that exposes that toolbar (Part, PartDesign, Draft, Arch/BIM, ...).

.. seealso::

   :doc:`quickstart` walks through creating your first export end to end.
