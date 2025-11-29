import pytest
from mesa.visualization import icons


def test_list_icons_contains_smiley():
    names = icons.list_icons()
    assert "smiley" in names
    assert "sad_face" in names
    assert "neutral_face" in names

def test_get_icon_svg_returns_text():
    svg = icons.get_icon_svg("smiley")
    assert "<svg" in svg

    svg = icons.get_icon_svg("sad_face")
    assert "<svg" in svg

    svg = icons.get_icon_svg("neutral_face")
    assert "<svg" in svg



def test_get_icon_svg_not_found():
    with pytest.raises(FileNotFoundError):
        icons.get_icon_svg("this-does-not-exist")