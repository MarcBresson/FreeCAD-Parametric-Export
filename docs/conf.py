from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

DOCS_DIR = Path(__file__).parent
PROJECT_ROOT = DOCS_DIR.parent

_PACKAGE_XML_NS = {"pm": "https://wiki.freecad.org/Package_Metadata"}


def _read_version() -> str:
    root = ET.parse(PROJECT_ROOT / "package.xml").getroot()
    version_element = root.find("pm:version", _PACKAGE_XML_NS)
    assert version_element is not None, "package.xml is missing a <version> element"
    text = version_element.text
    assert text, "package.xml <version> element is empty"
    return text.strip()


html_title = "CarteGrid"
project = "CarteGrid"
author = "Marc Bresson"
copyright = f"{date.today().year}, {author}"
release = _read_version()
version = release

extensions = [
    "sphinx.ext.todo",
    "sphinx_copybutton",
    "sphinx_github_changelog",
]

todo_include_todos = True

sphinx_github_changelog_root_repo = "MarcBresson/cartegrid"

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_static_path = ["_static"]

html_theme = "furo"
html_logo = "../Resources/icons/cartegrid.svg"
html_favicon = "../Resources/icons/favicon.svg"
html_theme_options = {
    "source_repository": "https://github.com/MarcBresson/cartegrid/",
    "source_branch": "main",
    "source_directory": "docs/",
}
html_copy_source = False
html_show_sourcelink = False
