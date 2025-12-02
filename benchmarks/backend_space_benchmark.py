"""Improved backend micro-benchmark for Mesa SpaceRenderer icon optimization.

Measures per-frame render time (avg, p95) for:
  - Matplotlib backend (forces canvas draw)
  - Altair backend (forces chart serialization)

Modes:
  - marker: default primitive
  - icon: uses cached rasterized icons

Scenarios:
  - N = 100, 500, 1000, 2000 agents
  - frames = 60 and/or 120

Run examples:
  python benchmarks/backend_space_benchmark.py --backend matplotlib --mode marker --n 1000 --frames 120
  python benchmarks/backend_space_benchmark.py --backend altair --mode icon --n 1000 --frames 60
"""

from __future__ import annotations

import argparse
import contextlib
import math
import statistics
import sys
import time
import traceback
from dataclasses import dataclass

import numpy as np

try:
    from mesa import Agent, Model
    from mesa.space import ContinuousSpace
    from mesa.visualization.space_renderer import SpaceRenderer
except ImportError as e:
    print(f"Missing Mesa dependencies: {e}")
    sys.exit(1)


@dataclass
class BenchConfig:
    """Configuration for benchmark runs."""

    backend: str  # "matplotlib" | "altair"
    mode: str  # "marker" | "icon"
    n: int  # number of agents
    frames: int  # number of frames
    width: int = 800
    height: int = 600
    icon_name: str = "smiley"
    icon_size: int = 24
    redraw_structure: bool = False  # set True if you want to include structure cost


class DummyAgent(Agent):
    """Minimal agent for benchmark - no unique_id needed in __init__."""

    def __init__(self, model):
        """Initialize agent.

        Args:
            model: The model instance this agent belongs to.
        """
        super().__init__(model)  # Only pass model, unique_id is auto-assigned

    def step(self):
        """Perform agent step (no-op for benchmark)."""


class DummyModel(Model):
    """Minimal model with ContinuousSpace for rendering benchmark."""

    def __init__(self, width: int, height: int, n: int, seed=None):
        """Initialize model with agents in grid layout.

        Args:
            width: Space width
            height: Space height
            n: Number of agents to create
            seed: Random seed for reproducibility
        """
        super().__init__(seed=seed)  # REQUIRED in Mesa 3.0
        self.space = ContinuousSpace(width, height, torus=False)
        # Don't use self.agents - it's reserved by Mesa
        self._agent_list = []  # Use custom attribute name

        cols = int(max(1, math.sqrt(n)))
        rows = math.ceil(n / cols)
        x_spacing = width / (cols + 1)
        y_spacing = height / (rows + 1)

        idx = 0
        for r in range(rows):
            for c in range(cols):
                if idx >= n:
                    break
                x = (c + 1) * x_spacing
                y = (r + 1) * y_spacing
                # Don't pass unique_id - it's auto-assigned now
                a = DummyAgent(model=self)
                self.space.place_agent(a, (x, y))
                self._agent_list.append(a)
                idx += 1

        self.steps = 0
        self.running = True

    def step(self):
        """Advance model by one step."""
        self.steps += 1
        self.running = True


def make_portrayal(mode: str, icon_name: str, icon_size: int):
    """Return portrayal function.

    Note: Do NOT include x, y in portrayal - SpaceRenderer extracts position from agent.pos

    Args:
        mode: "marker" or "icon"
        icon_name: Name of icon to use
        icon_size: Size of icon in pixels

    Returns:
        Callable that returns portrayal dict for an agent
    """

    def portrayal(agent):
        base = {
            "size": icon_size,
            "color": "#1f77b4",
            "marker": "o",
            "alpha": 1.0,
        }
        if mode == "icon":
            base["icon"] = icon_name
            base["icon_size"] = icon_size
        return base

    return portrayal


def run_benchmark(cfg: BenchConfig):
    """Run benchmark and return timing results.

    Args:
        cfg: Benchmark configuration
    Returns:
        Dictionary with timing results, or None if benchmark failed
    """
    try:
        model = DummyModel(cfg.width, cfg.height, cfg.n)
        renderer = SpaceRenderer(model=model, backend=cfg.backend)
    except Exception as e:
        print(f"Error initializing benchmark: {e}")
        traceback.print_exc()
        return None

    agent_portrayal = make_portrayal(cfg.mode, cfg.icon_name, cfg.icon_size)

    # Warm-up: build initial meshes/caches
    print(f"Warming up ({cfg.backend}, {cfg.mode}, n={cfg.n})...")
    for _ in range(10):
        renderer.render(agent_portrayal=agent_portrayal)
        with contextlib.suppress(Exception):
            _ = renderer.canvas  # force initial build

    print(f"Measuring {cfg.frames} frames...")
    frame_ms = []
    for frame in range(cfg.frames):
        t0 = time.perf_counter()

        # Advance model (static layout; but we mimic progression)
        model.step()

        # Invalidate meshes to force redraw (otherwise render() may reuse)
        renderer.agent_mesh = None
        if cfg.redraw_structure:
            renderer.space_mesh = None

        # Redraw
        renderer.render(agent_portrayal=agent_portrayal)

        # Force actual backend work
        try:
            if cfg.backend == "matplotlib":
                # Ensure figure draws
                fig = (
                    renderer.canvas.get_figure()
                    if hasattr(renderer.canvas, "get_figure")
                    else renderer.canvas.figure
                )
                fig.canvas.draw()
            elif cfg.backend == "altair":
                # Serialize chart; triggers build pipeline
                _ = renderer.canvas.to_json()
        except Exception:
            # Fallback: just access canvas
            _ = renderer.canvas

        t1 = time.perf_counter()
        frame_ms.append((t1 - t0) * 1000.0)

        if (frame + 1) % 20 == 0:
            print(f"  {frame + 1}/{cfg.frames} frames completed")

    avg_ms = statistics.mean(frame_ms)
    p95_ms = float(np.percentile(frame_ms, 95))
    return {
        "backend": cfg.backend,
        "mode": cfg.mode,
        "n": cfg.n,
        "frames": cfg.frames,
        "avg_frame_ms": avg_ms,
        "p95_frame_ms": p95_ms,
    }


def main():
    """Run benchmark from command line arguments."""
    parser = argparse.ArgumentParser(description="Improved SpaceRenderer benchmark")
    parser.add_argument("--backend", choices=["matplotlib", "altair"], required=True)
    parser.add_argument("--mode", choices=["marker", "icon"], required=True)
    parser.add_argument("--n", type=int, default=1000)
    parser.add_argument("--frames", type=int, default=60)
    parser.add_argument("--icon", type=str, default="smiley")
    parser.add_argument("--icon-size", type=int, default=24)
    parser.add_argument("--width", type=int, default=800)
    parser.add_argument("--height", type=int, default=600)
    parser.add_argument(
        "--redraw-structure",
        action="store_true",
        help="Include structure redraw cost each frame",
    )
    args = parser.parse_args()

    cfg = BenchConfig(
        backend=args.backend,
        mode=args.mode,
        n=args.n,
        frames=args.frames,
        width=args.width,
        height=args.height,
        icon_name=args.icon,
        icon_size=args.icon_size,
        redraw_structure=args.redraw_structure,
    )

    res = run_benchmark(cfg)

    if res is None:
        print("Benchmark failed!")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("Backend Benchmark Results:")
    print("=" * 60)
    for k, v in res.items():
        if k.endswith("_ms"):
            print(f"  {k}: {v:.3f}")
        else:
            print(f"  {k}: {v}")
    print("=" * 60)


if __name__ == "__main__":
    main()
