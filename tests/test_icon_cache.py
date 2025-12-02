"""Tests for icon cache functionality."""

from mesa.visualization.icon_cache import IconCache


def test_icon_cache_matplotlib():
    """Test icon cache with matplotlib backend."""
    cache = IconCache(backend="matplotlib")
    arr = cache.get("smiley", size=32)
    if arr is not None:  # Only test if deps available
        assert arr.shape == (32, 32, 4)
