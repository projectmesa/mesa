"""Python-only benchmark for bundled SVG icons.

Measures:
- cold SVG read time (icon mode)
- SVG -> raster conversion time (icon mode, via cairosvg)
- per-frame composition time for N icons/markers drawn onto a Pillow canvas
"""

from __future__ import annotations

import argparse
import statistics
import time
from io import BytesIO
from typing import Literal

try:
    import cairosvg
    from PIL import Image, ImageDraw
except Exception as e:  # pragma: no cover
    raise SystemExit(
        "Requires 'cairosvg' and 'Pillow'. Install with: pip install cairosvg pillow"
    ) from e

from mesa.visualization import icons as icons_module


def svg_to_pil_image(svg_text: str, scale: float = 1.0) -> Image.Image:
    """Convert an SVG string to a Pillow RGBA image using cairosvg."""
    png_bytes = cairosvg.svg2png(bytestring=svg_text.encode("utf-8"), scale=scale)
    return Image.open(BytesIO(png_bytes)).convert("RGBA")


def run_benchmark(
    icon_name: str = "smiley",
    n: int = 100,
    frames: int = 60,
    canvas_size: tuple[int, int] = (800, 600),
    icon_size: tuple[int, int] = (32, 32),
    scale: float = 1.0,
    mode: Literal["icon", "marker"] = "icon",
    marker_color: tuple[int, int, int, int] = (0, 0, 0, 255),  # black
) -> dict[str, float | str | int]:
    """Run benchmark: compare rasterized SVG icon composition vs default marker drawing.

    - mode="icon": pre-rasterize the SVG once, then alpha-composite per agent.
    - mode="marker": draw a filled circle per agent with ImageDraw (default marker proxy).
    """
    svg_read_sec = 0.0
    convert_sec = 0.0
    pil_icon: Image.Image | None = None

    if mode == "icon":
        t_read0 = time.perf_counter()
        svg_text = icons_module.get_icon_svg(icon_name)
        t_read1 = time.perf_counter()
        svg_read_sec = t_read1 - t_read0

        t_conv0 = time.perf_counter()
        pil_icon = svg_to_pil_image(svg_text, scale=scale)
        t_conv1 = time.perf_counter()
        convert_sec = t_conv1 - t_conv0

        if pil_icon.size != icon_size:
            pil_icon = pil_icon.resize(icon_size, resample=Image.LANCZOS)

    # lay out positions on a grid
    cols = int(max(1, n**0.5))
    spacing_x = canvas_size[0] / cols
    rows = (n + cols - 1) // cols
    spacing_y = canvas_size[1] / max(1, rows)
    positions: list[tuple[int, int]] = []
    for i in range(n):
        x = int((i % cols) * spacing_x + spacing_x / 2 - icon_size[0] / 2)
        y = int((i // cols) * spacing_y + spacing_y / 2 - icon_size[1] / 2)
        positions.append((x, y))

    # warm-up
    for _ in range(2):
        canvas = Image.new("RGBA", canvas_size, (255, 255, 255, 0))
        if mode == "icon":
            assert pil_icon is not None
            for x, y in positions:
                canvas.alpha_composite(pil_icon, dest=(x, y))
        else:
            draw = ImageDraw.Draw(canvas)
            r_w, r_h = icon_size
            for x, y in positions:
                draw.ellipse((x, y, x + r_w, y + r_h), fill=marker_color)

    # timed frames
    frame_times_ms: list[float] = []
    for _ in range(frames):
        canvas = Image.new("RGBA", canvas_size, (255, 255, 255, 0))
        t0 = time.perf_counter()
        if mode == "icon":
            assert pil_icon is not None
            for x, y in positions:
                canvas.alpha_composite(pil_icon, dest=(x, y))
        else:
            draw = ImageDraw.Draw(canvas)
            r_w, r_h = icon_size
            for x, y in positions:
                draw.ellipse((x, y, x + r_w, y + r_h), fill=marker_color)
        t1 = time.perf_counter()
        frame_times_ms.append((t1 - t0) * 1000.0)

    avg_ms = statistics.mean(frame_times_ms)
    p95_ms = (
        statistics.quantiles(frame_times_ms, n=100)[94]
        if len(frame_times_ms) >= 20
        else max(frame_times_ms)
    )

    return {
        "mode": mode,
        "icon": icon_name if mode == "icon" else "",
        "n": n,
        "frames": frames,
        "svg_read_sec": svg_read_sec,
        "svg_convert_sec": convert_sec,
        "avg_frame_ms": avg_ms,
        "p95_frame_ms": p95_ms,
    }


def main() -> None:
    """CLI entry point for the icon vs marker benchmark."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["icon", "marker"], default="icon")
    ap.add_argument("--icon", default="smiley")
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--frames", type=int, default=60)
    ap.add_argument("--width", type=int, default=800)
    ap.add_argument("--height", type=int, default=600)
    ap.add_argument("--icon-w", type=int, default=32)
    ap.add_argument("--icon-h", type=int, default=32)
    ap.add_argument("--scale", type=float, default=1.0)
    args = ap.parse_args()

    result = run_benchmark(
        mode=args.mode,
        icon_name=args.icon,
        n=args.n,
        frames=args.frames,
        canvas_size=(args.width, args.height),
        icon_size=(args.icon_w, args.icon_h),
        scale=args.scale,
    )
    print("Benchmark:")
    for k, v in result.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.3f}")
        else:
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
