# GridParamsExport

A FreeCAD Addon for generating and batch-exporting multiple versions of a parametric model
driven by an `App::VarSet`. Everything is managed with an interactive dialog: define a
parameter grid, preview the resulting variations and their names, then export a selected set
of objects per variation to files.

## Parameter grid model

A grid is a list of **items**. Each item is one "sklearn `ParameterGrid`-style" dict of
`{parameter_name: value}`, where a value can be:

- a fixed scalar (`Fixed`, or just type a plain value in the dialog)
- an explicit list of values (`ValueList` / the "List" kind)
- a deterministic range sampler (`LinSpace(start, stop, num)` or `Range(start, stop, step)`)

Every item is expanded independently via a full Cartesian product over its own parameters, and
results across items are concatenated -- this mirrors `sklearn.model_selection.ParameterGrid`
exactly (a dict expands to a cross-product; a list of dicts is independent alternatives, never
crossed with each other).

## Naming

Each item has an optional name template; if left blank it falls back to the global default
template. Template can be filled-in using parameters like `"{base_name} - CableLength{Base_CableLength}"`.
If a template lacks a placeholder needed to distinguish multiple resulting combinations, the
preview highlights the resulting duplicate names and "Run Export" refuses to run until it's
fixed.

## Export

Pick objects via "Use Current Selection" (reads the current 3D view / tree selection), and
choose "Combine into one file" or "One file per object".

## Persistence

The grid configuration is stored inside the document itself, in a hidden `GridParamsConfig`
object's `ConfigJSON` property -- reopening the `.FCStd` file and reopening the dialog
restores the last-used setup with no extra files to manage.

The JSON is stamped with a `schema_version`. If a future release changes the saved shape, a
migration function gets registered in `core/config.py`'s `_MIGRATIONS` table (keyed by the
version it migrates *from*) and old documents upgrade automatically the next time they're
opened -- no manual file editing. Opening a document saved by a *newer* addon version than the
one currently installed shows a clear warning and falls back to a blank configuration rather
than silently misreading it or crashing (the old saved config is left untouched in the document
until you explicitly overwrite it with Save).

## Installing (development)

Symlink or copy this folder into your FreeCAD user `Mod/` directory, e.g. on macOS:

```
ln -s "$(pwd)" "$HOME/Library/Application Support/FreeCAD/Mod/GridParamsExport"
```

Restart FreeCAD; "Grid Params Export" appears in the workbench selector.

## Running the core tests

The `gridparams.core` package has no dependency on `FreeCAD`/`FreeCADGui` and can be
tested standalone:

```
python -m pytest tests/
```
