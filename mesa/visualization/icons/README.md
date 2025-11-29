# Mesa Agent Icon Library

A collection of minimal, performance-optimized SVG icons for agent-based model visualization.

## Overview

This directory contains bundled SVG icons that can be used to represent agents in Mesa visualizations. The icons are designed to be lightweight, customizable, and easy to integrate with Python visualization backends.

## Usage

### Python

```python
from mesa.visualization import icons

# List all available icons
icons = icons.list_icons()
print(icons)  # ['smiley', 'sad_face', 'neutral_face', ...]

# Get SVG content as string
svg_content = icons.get_icon_svg("smiley")

# Use with namespace prefix (optional)
svg_content = icons.get_icon_svg("mesa:smiley")
```

### Integration with Visualization

The SVG strings returned by `get_icon_svg()` can be:
- Converted to raster images using libraries like `cairosvg`
- Embedded in HTML-based visualizations (Solara, Matplotlib, etc.)
- Styled dynamically by replacing `currentColor` in the SVG string

## Design Guidelines

### File Naming
- **Lowercase with underscores**: `person.svg`, `happy_face.svg`
- **Icon name = filename without extension**: `person.svg` → `"person"`
- **Descriptive and concise**: Prefer `arrow_up` over `arr_u`

### SVG Standards
- **ViewBox**: Use `0 0 32 32` for consistency
- **Dynamic coloring**: Use `fill="currentColor"` to enable programmatic color control
- **Minimal paths**: Keep SVG markup simple for performance
- **No embedded styles**: Avoid `<style>` tags or inline CSS

### Example Icon

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <circle cx="16" cy="16" r="14" fill="currentColor"/>
</svg>
```

## Performance Considerations

- Icons are loaded via `importlib.resources` for efficient bundling
- SVG files are read from the package without filesystem access
- Small file sizes (<2KB recommended) ensure fast loading
- See `benchmarks/icons_benchmark.py` for performance testing

## Adding New Icons

1. Create an SVG file following the guidelines above
2. Place it in this directory
3. Icon automatically becomes available via `icons.get_icon_svg()`
4. No code changes required - icons are discovered at runtime

## License

Icons in this directory are part of the Mesa project and follow the same Apache 2.0 license.
