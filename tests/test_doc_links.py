import re
from pathlib import Path

from freecad.gridparams.gui import doc_links

PREFERENCES_RST = Path(__file__).parent.parent / "docs" / "guides" / "preferences.rst"

_LABEL_RE = re.compile(r"^\.\. _([\w-]+):", re.MULTILINE)


def _rst_anchor_labels(text: str) -> set[str]:
    return set(_LABEL_RE.findall(text))


def test_doc_link_anchors_exist_in_preferences_rst():
    labels = _rst_anchor_labels(PREFERENCES_RST.read_text())

    for url in (
        doc_links.PER_PART_FILENAME_TEMPLATE_URL,
        doc_links.FORMAT_PRECEDENCE_URL,
    ):
        _, anchor = url.split("#", 1)
        assert anchor in labels, (
            f"{url} references a label not defined in {PREFERENCES_RST}"
        )


def test_preferences_guide_url_has_no_fragment():
    assert "#" not in doc_links.PREFERENCES_GUIDE_URL
