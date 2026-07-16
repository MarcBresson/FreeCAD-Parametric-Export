"""Shared progress-dialog/validation glue around runner.run_export.

Pulled out of the dialog so the tree context menu's "Export using config" action can run an
export straight from a saved GridConfig without duplicating the progress dialog and error
messaging that already lives on the "Run Export" button.
"""

from pathlib import Path

from PySide import QtCore, QtWidgets

from freecad.gridparams.core.config import expand_config
from freecad.gridparams.core.variation import find_duplicate_names

from . import runner


def run_export_with_progress(doc, config, parent, disable_widget=None):
    """Validate `config`, run the export behind a modal progress dialog, and report the
    outcome via message boxes. Returns True on success, False if validation failed or the
    export raised."""
    variations = expand_config(config)
    duplicates = find_duplicate_names(variations)
    if duplicates:
        QtWidgets.QMessageBox.critical(
            parent,
            "GridParams",
            f"Duplicate variation name(s): {', '.join(duplicates)}",
        )
        return False
    if not config.export_settings.selected_object_names:
        QtWidgets.QMessageBox.critical(
            parent, "GridParams", "Select at least one object to export first."
        )
        return False
    output_folder = Path(config.export_settings.last_export_folder)
    if not output_folder.is_dir():
        QtWidgets.QMessageBox.critical(
            parent, "GridParams", f"Export folder does not exist: {output_folder}"
        )
        return False

    progress = QtWidgets.QProgressDialog(
        "Exporting variations...", "Cancel", 0, len(variations), parent
    )
    progress.setWindowModality(QtCore.Qt.WindowModal)
    if disable_widget is not None:
        disable_widget.setEnabled(False)

    def on_progress(done, total):
        progress.setValue(done)
        QtWidgets.QApplication.processEvents()

    try:
        written = runner.run_export(
            doc, config, output_folder, progress_callback=on_progress
        )
    except Exception as exc:
        progress.close()
        if disable_widget is not None:
            disable_widget.setEnabled(True)
        message = f"Export failed: {exc}"
        written_so_far = getattr(exc, "written", None)
        if written_so_far:
            message += f"\n\n{len(written_so_far)} file(s) were already written before the failure."
        QtWidgets.QMessageBox.critical(parent, "GridParams", message)
        return False

    progress.close()
    if disable_widget is not None:
        disable_widget.setEnabled(True)
    QtWidgets.QMessageBox.information(
        parent, "GridParams", f"Exported {len(written)} file(s) to {output_folder}"
    )
    return True
