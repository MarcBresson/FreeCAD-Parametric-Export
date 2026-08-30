"""The Qt preferences page (Edit > Preferences > Grid Params Export), registered with
FreeCADGui.addPreferencePage. Split from `preferences.py` so the getters/setters/format
resolution there can be imported and tested without a Qt installation."""

from PySide import QtCore, QtWidgets

from . import doc_links, format_registry, preferences


def _hint_label(
    text: str, url: str | None = None, link_text: str = "Learn more"
) -> QtWidgets.QLabel:
    """A small word-wrapped explanatory label, optionally with a link to the docs."""
    html = text
    if url:
        html += f' <a href="{url}">{link_text} ↗</a>'
    label = QtWidgets.QLabel(html)
    label.setWordWrap(True)
    label.setOpenExternalLinks(True)
    font = label.font()
    font.setPointSizeF(font.pointSizeF() * 0.9)
    label.setFont(font)
    return label


def _group_spacer(height: int = 18) -> QtWidgets.QWidget:
    """An invisible full-width row used to widen the gap between option groups, while
    `layout`'s own vertical spacing stays tight for each field/hint pair."""
    spacer = QtWidgets.QWidget()
    spacer.setFixedHeight(height)
    return spacer


class GridParamsPreferencesPage(QtWidgets.QWidget):
    """Registered with FreeCADGui.addPreferencePage; must implement loadSettings/saveSettings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        outer_layout = QtWidgets.QVBoxLayout(self)
        layout = QtWidgets.QFormLayout()
        layout.setVerticalSpacing(6)
        outer_layout.addLayout(layout)

        self.relative_path_edit = QtWidgets.QLineEdit()
        tooltip = (
            "Exports are written here, resolved relative to each FreeCAD document's "
            "own folder.\n"
            "Leave empty to export next to the document.\n"
            "This applies to every document -- no export path is stored inside .FCStd files."
        )
        self.relative_path_edit.setToolTip(tooltip)
        self.relative_path_edit.setPlaceholderText(
            "Same folder as the FreeCAD document"
        )
        label = QtWidgets.QLabel("Export relative path")
        label.setToolTip(tooltip)
        layout.addRow(label, self.relative_path_edit)
        layout.addRow(
            _hint_label(
                "Where Export writes files, relative to the document's own folder.",
                doc_links.PREFERENCES_GUIDE_URL,
            )
        )
        layout.addRow(_group_spacer())

        self.preferred_formats_list = QtWidgets.QListWidget()
        self.preferred_formats_list.setToolTip(
            "Formats used whenever a grid item doesn't specify its own. Select one or more --"
            " every checked format is exported."
        )
        self.preferred_formats_list.setFixedHeight(140)
        for option in format_registry.list_available_formats():
            item = QtWidgets.QListWidgetItem(option.label)
            item.setData(QtCore.Qt.UserRole, option.id)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.preferred_formats_list.addItem(item)
        layout.addRow(
            QtWidgets.QLabel("Preferred formats"), self.preferred_formats_list
        )
        layout.addRow(
            _hint_label(
                "Formats exported when a grid item doesn't choose its own.",
                doc_links.FORMAT_PRECEDENCE_URL,
            )
        )
        layout.addRow(_group_spacer())

        self.allow_per_item_checkbox = QtWidgets.QCheckBox(
            "Allow choosing export formats per grid item"
        )
        self.allow_per_item_checkbox.setToolTip(
            "When checked, the Grid Params dialog shows a per-item format picker that "
            "overrides the preferred formats above for that item."
        )
        layout.addRow(self.allow_per_item_checkbox)
        layout.addRow(
            _hint_label(
                "Lets each grid item override the preferred formats above.",
                doc_links.FORMAT_PRECEDENCE_URL,
            )
        )
        layout.addRow(_group_spacer())

        self.per_part_filename_template_edit = QtWidgets.QLineEdit()
        per_part_filename_template_tooltip = (
            "How each part's output filename is built when exporting one file per part.\n"
            "Placeholders: {name} (the variation name), {body_label} (the part's Label), and "
            "{body_name} (the part's internal Name).\n"
            "These two placeholders are also available directly in the Default/Item naming "
            "template, if you'd rather place the body there instead.\n"
        )
        self.per_part_filename_template_edit.setToolTip(
            per_part_filename_template_tooltip
        )
        self.per_part_filename_template_edit.setPlaceholderText(
            preferences.DEFAULT_BODY_NAME_TEMPLATE
        )
        per_part_filename_template_label = QtWidgets.QLabel(
            "Per-part filename template"
        )
        per_part_filename_template_label.setToolTip(per_part_filename_template_tooltip)
        layout.addRow(
            per_part_filename_template_label, self.per_part_filename_template_edit
        )
        layout.addRow(
            _hint_label(
                "How each part's filename is built when exporting one file per part.",
                doc_links.PER_PART_FILENAME_TEMPLATE_URL,
            )
        )

        outer_layout.addStretch(1)

    def loadSettings(self):
        self.relative_path_edit.setText(preferences.get_export_relative_path())

        preferred = set(preferences.get_preferred_formats())
        for row in range(self.preferred_formats_list.count()):
            item = self.preferred_formats_list.item(row)
            checked = item.data(QtCore.Qt.UserRole) in preferred
            item.setCheckState(QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked)

        self.allow_per_item_checkbox.setChecked(
            preferences.get_allow_per_item_formats()
        )

        self.per_part_filename_template_edit.setText(
            preferences.get_body_name_template()
        )

    def saveSettings(self):
        preferences.set_export_relative_path(self.relative_path_edit.text())

        formats = [
            self.preferred_formats_list.item(row).data(QtCore.Qt.UserRole)
            for row in range(self.preferred_formats_list.count())
            if self.preferred_formats_list.item(row).checkState() == QtCore.Qt.Checked
        ]
        preferences.set_preferred_formats(formats)
        preferences.set_allow_per_item_formats(self.allow_per_item_checkbox.isChecked())

        preferences.set_body_name_template(
            self.per_part_filename_template_edit.text()
            or preferences.DEFAULT_BODY_NAME_TEMPLATE
        )
