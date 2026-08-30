"""Shared progress-dialog/validation glue around runner.run_export.

Pulled out of the dialog so the tree context menu's "Export using config" action can run an
export straight from a saved GridConfig without duplicating the progress dialog and error
messaging that already lives on the "Export" button.
"""

from pathlib import Path

from PySide import QtCore, QtWidgets

from freecad.gridparams.core.config import expand_config
from freecad.gridparams.core.variation import find_duplicate_names

from . import format_registry, preferences, runner


def _report_error(parent, message):
    QtWidgets.QMessageBox.critical(parent, "GridParams", message)


def _validate_variations(config, parent, document_label):
    """Return the expanded variations, or None (after reporting) if validation fails."""
    variations = expand_config(config, document_label=document_label)
    duplicates = find_duplicate_names(variations)
    if duplicates:
        _report_error(parent, f"Duplicate variation name(s): {', '.join(duplicates)}")
        return None
    if not config.export_settings.selected_object_names:
        _report_error(parent, "Select at least one object to export first.")
        return None
    return variations


def compute_output_folder(doc):
    """Return the configured export folder as a Path (not guaranteed to exist), resolved
    relative to `doc`'s own folder, or None if the document has not been saved yet."""
    if not doc.FileName:
        return None
    doc_folder = Path(doc.FileName).parent
    relative_path = preferences.get_export_relative_path()
    return doc_folder / relative_path if relative_path else doc_folder


def _resolve_output_folder(doc, parent):
    """Return the export folder as an absolute Path, or None (after reporting) if it
    can't be resolved or doesn't exist."""
    output_folder = compute_output_folder(doc)
    if output_folder is None:
        _report_error(
            parent,
            "The document has not been saved yet. Save the document first so the "
            "export folder can be resolved relative to it.",
        )
        return None

    if not output_folder.is_dir():
        _report_error(parent, f"Export folder does not exist: {output_folder}")
        return None
    return output_folder


def _make_progress_dialog(parent, total, disable_widget):
    progress = QtWidgets.QProgressDialog(
        "Exporting variations...", "Cancel", 0, total, parent
    )
    progress.setWindowModality(QtCore.Qt.WindowModal)
    if disable_widget is not None:
        disable_widget.setEnabled(False)
        # Disabling `disable_widget` cascades to `progress` when it is one of its
        # ancestors (e.g. the "Export" button's own dialog), which would freeze
        # the progress bar. Explicitly re-enable it so it keeps updating/responding.
        progress.setEnabled(True)
    return progress


def _close_progress(progress, disable_widget):
    progress.close()
    if disable_widget is not None:
        disable_widget.setEnabled(True)


def _export_to_resolved_folder(
    doc, config, output_folder, total, parent, disable_widget, format_override=None
):
    """Run the export to an already-resolved, already-existing `output_folder`, behind a
    modal progress dialog, reporting the outcome via message boxes."""
    progress = _make_progress_dialog(parent, total, disable_widget)

    def on_progress(done, total):
        progress.setValue(done)
        QtWidgets.QApplication.processEvents()

    try:
        written = runner.run_export(
            doc,
            config,
            output_folder,
            progress_callback=on_progress,
            format_override=format_override,
        )
    except Exception as exc:
        _close_progress(progress, disable_widget)
        message = f"Export failed: {exc}"
        written_so_far = getattr(exc, "written", None)
        if written_so_far:
            message += f"\n\n{len(written_so_far)} file(s) were already written before the failure."
        _report_error(parent, message)
        return False

    _close_progress(progress, disable_widget)
    QtWidgets.QMessageBox.information(
        parent, "GridParams", f"Exported {len(written)} file(s) to {output_folder}"
    )
    return True


def run_export_with_progress(doc, config, parent, disable_widget=None):
    """Validate `config`, run the export behind a modal progress dialog, and report the
    outcome via message boxes. Returns True on success, False if validation failed or the
    export raised."""
    variations = _validate_variations(config, parent, doc.Label)
    if variations is None:
        return False

    output_folder = _resolve_output_folder(doc, parent)
    if output_folder is None:
        return False

    return _export_to_resolved_folder(
        doc, config, output_folder, len(variations), parent, disable_widget
    )


def _prompt_export_format(parent):
    """Ask the user to pick a single format for a one-off "Export to..." run, independent of
    the preferred/per-item format settings. Returns the chosen format id, or None if
    the user cancelled."""
    options = format_registry.list_available_formats()
    if not options:
        _report_error(parent, "No export formats are available.")
        return None

    labels = [option.label for option in options]
    label, ok = QtWidgets.QInputDialog.getItem(
        parent, "Export to...", "Format:", labels, editable=False
    )
    if not ok:
        return None
    return next((option.id for option in options if option.label == label), None)


def export_to_folder_with_progress(doc, config, parent, disable_widget=None):
    """Validate `config`, prompt for a single export format and a destination folder via
    native pickers, then run the export there behind a modal progress dialog. The chosen
    format is a one-off override for this run only -- it is never persisted, and ignores the
    preferred/per-item format settings. Mutates `config.export_settings` in place
    with the chosen folder (as `last_export_folder`) so the picker reopens there next time --
    the caller is responsible for persisting that if it wants it remembered. Returns True on
    success, False if validation failed, the user cancelled a picker, or the export raised."""
    variations = _validate_variations(config, parent, doc.Label)
    if variations is None:
        return False

    format_id = _prompt_export_format(parent)
    if format_id is None:
        return False

    folder = QtWidgets.QFileDialog.getExistingDirectory(
        parent, "Select export folder", config.export_settings.last_export_folder
    )
    if not folder:
        return False
    config.export_settings.last_export_folder = folder

    return _export_to_resolved_folder(
        doc,
        config,
        Path(folder),
        len(variations),
        parent,
        disable_widget,
        format_override=format_id,
    )
