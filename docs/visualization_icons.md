# Icon-Based Agent Visualization

Mesa supports rendering agents as icons (images) instead of simple markers. This feature allows for more expressive and visually distinctive agent representations.

## Overview

The icon system provides:
- **Bundled SVG icons** (smiley, sad_face, neutral_face)
- **Efficient caching** of rasterized icons
- **Altair backend support** for icon rendering
- **Minimal performance overhead** (~1% vs markers)

## Quick Start

### 1. Using Icons in Agent Portrayal

To display an agent as an icon, include the `icon` key in your portrayal function:

```python
def agent_portrayal(agent):
    return {
        "size": 24,
        "color": "#4CAF50",
        "marker": "o",
        "icon": "smiley",      # Icon name
        "icon_size": 32,       # Optional: icon size in pixels
    }
```

### 2. Available Icons

Mesa includes these bundled icons:

| Icon Name | Description |
|-----------|-------------|
| `smiley` | Happy face  |
| `sad_face` | Sad face  |
| `neutral_face` | Neutral face  |

### 3. Listing Available Icons

```python
from mesa.visualization.icons import list_icons, get_icon_svg

# Get all available icon names
icons = list_icons()
print(icons)  # ['neutral_face', 'sad_face', 'smiley']

# Get raw SVG text for an icon
svg_text = get_icon_svg("smiley")
```

## Configuration

### SpaceRenderer Icon Mode

When using `SpaceRenderer`, you can control icon behavior:

```python
from mesa.visualization.space_renderer import SpaceRenderer

renderer = SpaceRenderer(
    model,
    backend="altair",
    icon_mode="auto",           # "off", "auto", or "force"
    icon_auto_max_agents=1500,  # Max agents for auto mode
    icon_culling=True,          # Enable viewport culling
)
```

| Parameter | Values | Description |
|-----------|--------|-------------|
| `icon_mode` | `"off"` | Icons disabled (default) |
| | `"auto"` | Icons enabled if N ≤ `icon_auto_max_agents` |
| | `"force"` | Icons always enabled |
| `icon_auto_max_agents` | int | Threshold for auto mode (default: 1500) |
| `icon_culling` | bool | Skip off-screen agents (default: True) |

## Icon Cache

Icons are cached after first rasterization for performance:

```python
from mesa.visualization.icon_cache import IconCache

# Create cache for Altair backend
cache = IconCache(backend="altair")

# Get or create a rasterized icon
icon_url = cache.get_or_create("smiley", size=32)

# Clear cache if needed
cache.clear()
```

## Adding Custom Icons

### 1. Create an SVG File

Save your SVG in `mesa/visualization/icons/`:

```xml
<!-- mesa/visualization/icons/my_icon.svg -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <circle cx="16" cy="16" r="12" fill="currentColor"/>
</svg>
```

**Tips for custom icons:**
- Use `fill="currentColor"` for dynamic coloring
- Keep viewBox at `0 0 32 32` for consistency
- Minimize complexity for better performance

### 2. Use Your Icon

```python
def agent_portrayal(agent):
    return {
        "icon": "my_icon",  # Matches filename without .svg
        "icon_size": 24,
    }
```

## Performance

Icon rendering adds minimal overhead:

| Agents (N) | Marker (ms) | Icon (ms) | Overhead |
|------------|-------------|-----------|----------|
| 100 | 15.02 | 15.10 | +0.5% |
| 500 | 22.77 | 22.72 | -0.2% |
| 1000 | 31.49 | 31.97 | +1.5% |
| 2000 | 50.96 | 51.57 | +1.2% |

**Why so fast?**
- SVG→PNG conversion happens once per icon/size
- Cached data URLs are reused across frames
- Viewport culling skips off-screen agents

## Example: Grid with Icons

```python
from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.visualization import SolaraViz

class MyAgent(Agent):
    def __init__(self, model, mood):
        super().__init__(model)
        self.mood = mood  # "happy", "sad", or "neutral"

def agent_portrayal(agent):
    icon_map = {
        "happy": "smiley",
        "sad": "sad_face",
        "neutral": "neutral_face",
    }
    color_map = {
        "happy": "#4CAF50",
        "sad": "#8B4513",
        "neutral": "#FFC107",
    }
    return {
        "icon": icon_map.get(agent.mood, "smiley"),
        "icon_size": 24,
        "color": color_map.get(agent.mood, "#808080"),
    }

# Visualize with SolaraViz
page = SolaraViz(
    model,
    components=[make_space_component(agent_portrayal)],
)
```

## Running the Demo

Mesa includes an interactive demo:

```bash
cd mesa/visualization
solara run solara_viz_icon.py
```

This demo shows:
- Grid-based icon visualization
- Controls for grid size, agent density, icon size
- Statistics panel with agent counts
- Real-time render performance

## Optional Dependencies

For SVG rasterization with actual SVG icons:

```bash
pip install cairosvg
```

**System dependencies (macOS):**
```bash
brew install cairo pango gdk-pixbuf libffi
```

**Without cairosvg:** Icons fall back to colored circles.

## Troubleshooting

### Icons show as colored circles
- Install `cairosvg`: `pip install cairosvg`
- Check system dependencies (cairo, pango)

### Icons are black
- SVG uses `currentColor` which defaults to black
- The `IconCache` should replace this automatically

### Performance issues with many agents
- Enable culling: `icon_culling=True`
- Use `icon_mode="auto"` to fall back for large N
- Reduce icon size

## API Reference

### `mesa.visualization.icons`

```python
list_icons() -> list[str]
    """Return list of available icon names."""

get_icon_svg(name: str) -> str
    """Return raw SVG text for an icon."""
```

### `mesa.visualization.icon_cache.IconCache`

```python
IconCache(backend: Literal["matplotlib", "altair"])
    """Create icon cache for specified backend."""

get(icon_name: str, size: int) -> str | np.ndarray | None
    """Get cached icon or None."""

get_or_create(icon_name: str, size: int) -> str | np.ndarray | None
    """Get cached icon or create and cache it."""

clear()
    """Clear all cached icons."""
```

## See Also

- [Visualization Overview](./apis/visualization.md)
- [Basic Visualization Tutorial](./tutorials/4_visualization_basic.ipynb)
- [Custom Agent Visualization](./tutorials/6_visualization_custom.ipynb)