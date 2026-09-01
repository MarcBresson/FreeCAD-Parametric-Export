"""The Qt preferences page (Edit > Preferences > CarteGrid), registered with
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


def _make_card() -> tuple[QtWidgets.QFrame, QtWidgets.QFormLayout]:
    """A light-gray rounded card grouping one setting and its hint text, matching the
    section styling used by FreeCAD's other preference pages. Uses a translucent gray
    fill rather than a hardcoded color so it reads correctly in both light and dark themes."""
    card = QtWidgets.QFrame()
    card.setObjectName("SettingsCard")
    card.setStyleSheet(
        "QFrame#SettingsCard {"
        " background-color: rgba(127, 127, 127, 30);"
        " border-radius: 8px;"
        "}"
    )
    card_layout = QtWidgets.QVBoxLayout(card)
    card_layout.setContentsMargins(12, 10, 12, 10)
    form = QtWidgets.QFormLayout()
    form.setVerticalSpacing(6)
    card_layout.addLayout(form)
    return card, form


class CarteGridPreferencesPage(QtWidgets.QWidget):
    """Registered with FreeCADGui.addPreferencePage; must implement loadSettings/saveSettings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("General")
        outer_layout = QtWidgets.QVBoxLayout(self)
        outer_layout.setSpacing(12)

        path_card, path_form = _make_card()
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
        path_form.addRow(label, self.relative_path_edit)
        path_form.addRow(
            _hint_label(
                "Where Export writes files, relative to the document's own folder.",
                doc_links.PREFERENCES_GUIDE_URL,
            )
        )
        outer_layout.addWidget(path_card)

        formats_card, formats_form = _make_card()
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
        formats_form.addRow(
            QtWidgets.QLabel("Preferred formats"), self.preferred_formats_list
        )
        formats_form.addRow(
            _hint_label(
                "Formats exported when a grid item doesn't choose its own.",
                doc_links.FORMAT_PRECEDENCE_URL,
            )
        )
        outer_layout.addWidget(formats_card)

        allow_card, allow_form = _make_card()
        self.allow_per_item_checkbox = QtWidgets.QCheckBox(
            "Allow choosing export formats per grid item"
        )
        self.allow_per_item_checkbox.setToolTip(
            "When checked, the CarteGrid dialog shows a per-item format picker that "
            "overrides the preferred formats above for that item."
        )
        allow_form.addRow(self.allow_per_item_checkbox)
        allow_form.addRow(
            _hint_label(
                "Lets each grid item override the preferred formats above.",
                doc_links.FORMAT_PRECEDENCE_URL,
            )
        )
        outer_layout.addWidget(allow_card)

        template_card, template_form = _make_card()
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
        template_form.addRow(
            per_part_filename_template_label, self.per_part_filename_template_edit
        )
        template_form.addRow(
            _hint_label(
                "How each part's filename is built when exporting one file per part.",
                doc_links.PER_PART_FILENAME_TEMPLATE_URL,
            )
        )
        outer_layout.addWidget(template_card)

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
