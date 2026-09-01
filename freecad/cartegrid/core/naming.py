"""Name resolution for a variation: a single mechanism for both explicit names and templates.

A literal string with no ``{...}`` placeholders (e.g. "XS") resolves to itself unchanged, so
explicit per-item names and parameter-driven templates are the same code path.
"""


class NamingTemplateError(Exception):
    pass


def resolve_name(
    template: str, base_name: str, params: dict, document_label: str = ""
) -> str:
    try:
        return template.format(
            base_name=base_name, document_label=document_label, **params
        )
    except KeyError as exc:
        raise NamingTemplateError(
            f"Unknown placeholder {exc} in naming template {template!r} -- "
            f"available: base_name, document_label, {sorted(params)}"
        ) from exc
