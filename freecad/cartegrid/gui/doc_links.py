"""URLs to the published documentation, referenced from the preferences page. Kept in a
plain-Python module (no PySide/FreeCAD import) so `tests/test_doc_links.py` can check the
fragments against `docs/guides/preferences.rst` without a Qt installation."""

BASE_URL = "https://cartegrid.readthedocs.io/en/latest"
PREFERENCES_GUIDE_URL = f"{BASE_URL}/guides/preferences.html"
PER_PART_FILENAME_TEMPLATE_URL = f"{PREFERENCES_GUIDE_URL}#per-part-filename-template"
FORMAT_PRECEDENCE_URL = f"{PREFERENCES_GUIDE_URL}#format-precedence-table"
