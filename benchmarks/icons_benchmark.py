"""benchmark for bundled SVG icons (Python-only, dev use).

Measures:
- cold SVG read time
- SVG -> raster conversion time (via cairosvg)
- per-frame composition time for N icons drawn onto a Pillow canvas

Usage:
  pip install cairosvg pillow
  python benchmarks/icon_benchmark.py --icon person --n 500 --frames 120

Environment info (record this in PR):
  python -V
  uname -a (Linux/macOS) or systeminfo (Windows)
  CPU, RAM
"""

import argparse
import statistics
import time
from io import BytesIO

try:
    import cairosvg
    from PIL import Image
except Exception as e:
    raise SystemExit(
        "Requires 'cairosvg' and 'Pillow'. Install with: pip install cairosvg pillow"
    ) from e

from mesa.visualization import icons as icons_module  # your icons.py


def svg_to_pil_image(svg_text, scale=1.0):
    png_bytes = cairosvg.svg2png(bytestring=svg_text.encode("utf-8"), scale=scale)
    return Image.open(BytesIO(png_bytes)).convert("RGBA")


def run_benchmark(
    icon_name="person",
    n=100,
    frames=60,
    canvas_size=(800, 600),
    icon_size=(32, 32),
    scale=1.0,
):
    # load SVG
    t_read0 = time.perf_counter()
    svg_text = icons_module.get_icon_svg(icon_name)
    t_read1 = time.perf_counter()
    svg_read_sec = t_read1 - t_read0

    # convert to raster
    t_conv0 = time.perf_counter()
    pil_icon = svg_to_pil_image(svg_text, scale=scale)
    t_conv1 = time.perf_counter()
    convert_sec = t_conv1 - t_conv0

    # resize if needed
    if pil_icon.size != icon_size:
        pil_icon = pil_icon.resize(icon_size, resample=Image.LANCZOS)

    # grid positions
    cols = int(max(1, (n**0.5)))
    spacing_x = canvas_size[0] / cols
    rows = (n + cols - 1) // cols
    spacing_y = canvas_size[1] / max(1, rows)
    positions = []
    for i in range(n):
        x = int((i % cols) * spacing_x + spacing_x / 2 - icon_size[0] / 2)
        y = int((i // cols) * spacing_y + spacing_y / 2 - icon_size[1] / 2)
        positions.append((x, y))

    # warm-up
    for _ in range(2):
        canvas = Image.new("RGBA", canvas_size, (255, 255, 255, 0))
        for x, y in positions:
            canvas.alpha_composite(pil_icon, dest=(x, y))

    # timed frames
    frame_times_ms = []
    for _ in range(frames):
        canvas = Image.new("RGBA", canvas_size, (255, 255, 255, 0))
        t0 = time.perf_counter()
        for x, y in positions:
            canvas.alpha_composite(pil_icon, dest=(x, y))
        t1 = time.perf_counter()
        frame_times_ms.append((t1 - t0) * 1000.0)

    avg_ms = statistics.mean(frame_times_ms)
    p95_ms = (
        statistics.quantiles(frame_times_ms, n=100)[94]
        if len(frame_times_ms) >= 20
        else max(frame_times_ms)
    )

    return {
        "icon": icon_name,
        "n": n,
        "frames": frames,
        "svg_read_sec": svg_read_sec,
        "svg_convert_sec": convert_sec,
        "avg_frame_ms": avg_ms,
        "p95_frame_ms": p95_ms,
    }


def main():
    ap = argparse.ArgumentParser()
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
