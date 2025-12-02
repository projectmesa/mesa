"""Icon cache for Mesa visualizations."""

from __future__ import annotations

import base64
import io
from io import BytesIO
from typing import TYPE_CHECKING, Literal

import numpy as np
from PIL import Image, ImageDraw

if TYPE_CHECKING:
    pass


class IconCache:
    """Cache for rasterized icon images.

    Stores pre-rendered icons as data URLs or numpy arrays to avoid
    redundant rendering operations.
    """

    def __init__(self, backend: Literal["matplotlib", "altair"] = "matplotlib"):
        """Initialize the icon cache.

        Args:
            backend: The visualization backend ("matplotlib" or "altair")
        """
        self.backend = backend
        self._cache = {}

    def get(self, icon_name: str | None, size: int) -> str | np.ndarray | None:
        """Get cached icon or return None if not cached.

        Args:
            icon_name: Name of the icon
            size: Size of the icon in pixels

        Returns:
            Cached icon data (data URL for altair, numpy array for matplotlib),
            or None if not cached
        """
        if icon_name is None:
            return None
        key = (icon_name, size)
        return self._cache.get(key)

    def get_or_create(self, icon_name: str, size: int) -> str | np.ndarray | None:
        """Get cached icon or create and cache it.

        Args:
            icon_name: Name of the icon to retrieve/create
            size: Size of the icon in pixels

        Returns:
            Icon data (data URL for altair, numpy array for matplotlib),
            or None if icon cannot be created
        """
        cached = self.get(icon_name, size)
        if cached is not None:
            return cached

        raster = self._rasterize_icon(icon_name, size)
        if raster is not None:
            key = (icon_name, size)
            self._cache[key] = raster
        return raster

    def _rasterize_icon(self, icon_name: str, size: int) -> str | np.ndarray | None:
        """Rasterize icon to appropriate format for backend.

        Args:
            icon_name: Name of the icon to rasterize
            size: Size of the icon in pixels

        Returns:
            Rasterized icon (data URL for altair, numpy array for matplotlib),
            or None if icon cannot be rasterized
        """
        # Placeholder implementation - draws a simple circle
        # In production, this would load actual icon files or use a library
        img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        # Draw a simple colored circle based on icon name
        color_map = {
            "smiley": (255, 200, 0, 255),  # Yellow
            "star": (255, 215, 0, 255),  # Gold
            "heart": (255, 0, 100, 255),  # Red-pink
            "default": (100, 150, 255, 255),  # Blue
        }
        color = color_map.get(icon_name, color_map["default"])

        # Draw circle
        margin = size // 8
        draw.ellipse(
            [margin, margin, size - margin, size - margin], fill=color, outline=None
        )

        # Convert to appropriate format for backend
        if self.backend == "altair":
            return self._to_data_url(img)
        elif self.backend == "matplotlib":
            return self._to_numpy(img)
        return None

    def _to_data_url(self, img: Image.Image) -> str:
        """Convert PIL Image to data URL for Altair.

        Args:
            img: PIL Image to convert

        Returns:
            Base64-encoded data URL string
        """
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        png_bytes = buffer.getvalue()
        b64 = base64.b64encode(png_bytes).decode("utf-8")
        return f"data:image/png;base64,{b64}"

    def _to_numpy(self, img: Image.Image) -> np.ndarray:
        """Convert PIL Image to numpy array for Matplotlib.

        Args:
            img: PIL Image to convert

        Returns:
            RGBA numpy array
        """
        return np.asarray(img.convert("RGBA"))

    @classmethod
    def from_png_bytes(cls, png_bytes: bytes, backend: str) -> str | np.ndarray:
        """Convert PNG bytes to appropriate format for backend.

        Args:
            png_bytes: Raw PNG image bytes
            backend: Target backend ("matplotlib" or "altair")

        Returns:
            Converted image (data URL for altair, numpy array for matplotlib)
        """
        if backend == "altair":
            b64 = base64.b64encode(png_bytes).decode("utf-8")
            return f"data:image/png;base64,{b64}"
        elif backend == "matplotlib":
            img = Image.open(BytesIO(png_bytes)).convert("RGBA")
            arr = np.asarray(img)
            return arr
        raise ValueError(f"Unsupported backend: {backend}")

    def clear(self):
        """Clear all cached icons."""
        self._cache.clear()

    def __len__(self):
        """Get number of cached icons.

        Returns:
            Number of cached icon entries
        """
        return len(self._cache)
