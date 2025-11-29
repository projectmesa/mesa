from __future__ import annotations

import importlib.resources

ICONS_SUBDIR = "icons"
SVG_EXT = ".svg"


def _icons_package_root():
    """Returns a Traversable pointing at the icons subdirectory inside this package."""
    # this module's __package__ is "mesa.visualization"
    return importlib.resources.files(__package__).joinpath(ICONS_SUBDIR)


def list_icons() -> list[str]:
    """Return a sorted list of available bundled icon basenames (without .svg)."""
    root = _icons_package_root()
    names = []
    for item in root.iterdir():
        if item.is_file() and item.name.lower().endswith(SVG_EXT):
            names.append(item.name[: -len(SVG_EXT)])
    names.sort()
    return names


def get_icon_svg(name: str) -> str:
    """Return raw SVG text for a bundled icon.

    Accepts plain basenames (e.g. "person") or optional namespace form "mesa:person".
    Raises FileNotFoundError if icon not found.
    """
    if ":" in name:
        _, name = name.split(":", 1)

    root = _icons_package_root()
    svg_path = root.joinpath(f"{name}{SVG_EXT}")
    if not svg_path.exists():
        raise FileNotFoundError(f"Icon not found: {name}")
    return svg_path.read_text(encoding="utf-8")
