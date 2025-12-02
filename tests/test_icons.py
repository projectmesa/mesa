"""Tests for bundled SVG icon helpers (listing and retrieval)."""

import pytest

from mesa.visualization import icons


def test_list_icons_contains_smiley():
    """list_icons() includes 'smiley' (adjust if needed)."""
    names = icons.list_icons()
    assert "smiley" in names
    assert "sad_face" in names
    assert "neutral_face" in names


def test_get_icon_svg_returns_text():
    """get_icon_svg('smiley') returns SVG text containing '<svg'."""
    svg = icons.get_icon_svg("smiley")
    assert "<svg" in svg

    svg = icons.get_icon_svg("sad_face")
    assert "<svg" in svg

    svg = icons.get_icon_svg("neutral_face")
    assert "<svg" in svg


def test_get_icon_svg_not_found():
    """get_icon_svg() raises for missing icon."""
    with pytest.raises(FileNotFoundError):
        icons.get_icon_svg("this-does-not-exist")
