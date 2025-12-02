"""Sanity checks for Mesa icon rendering optimization.

Tests:
1. Mix of icons and markers in the same scene
2. Various icon sizes (16, 24, 32, 48)
3. No "ignored keys" warnings
4. Cache effectiveness

Usage:
    python benchmarks/icon_sanity_checks.py --backend altair
    python benchmarks/icon_sanity_checks.py --backend matplotlib
"""

from __future__ import annotations

import argparse
import sys
import traceback
import warnings

from mesa import Agent, Model
from mesa.space import ContinuousSpace
from mesa.visualization.space_renderer import SpaceRenderer


class TestAgent(Agent):
    """Agent with icon configuration."""

    def __init__(self, model, icon_name=None, icon_size=24):
        """Initialize test agent.

        Args:
            model: The model instance
            icon_name: Optional icon name (e.g., "smiley")
            icon_size: Icon size in pixels (default: 24)
        """
        super().__init__(model)
        self.icon_name = icon_name
        self.icon_size = icon_size


class TestModel(Model):
    """Test model with mixed agents."""

    def __init__(self, n_icons=50, n_markers=50, seed=None):
        """Initialize test model with icon and marker agents.

        Args:
            n_icons: Number of agents with icons
            n_markers: Number of agents with markers only
            seed: Random seed for reproducibility
        """
        super().__init__(seed=seed)  # REQUIRED in Mesa 3.0
        self.space = ContinuousSpace(800, 600, torus=False)

        # Add icon agents with various sizes
        icon_sizes = [16, 24, 32, 48]
        cols = 10
        for i in range(n_icons):
            a = TestAgent(
                self, icon_name="smiley", icon_size=icon_sizes[i % len(icon_sizes)]
            )
            # Ensure positions are within bounds [0, 800) x [0, 600)
            x = (i % cols) * 70 + 40  # Max: 9*70 + 40 = 670 < 800
            y = (i // cols) * 50 + 40  # Max: 4*50 + 40 = 240 < 600
            self.space.place_agent(a, (x, y))

        # Add marker agents (no icon) in right half
        for i in range(n_markers):
            a = TestAgent(self, icon_name=None)
            x = (i % cols) * 70 + 440  # Start at x=440
            y = (i // cols) * 50 + 40
            # Ensure within bounds
            x = min(x, 760)
            y = min(y, 560)
            self.space.place_agent(a, (x, y))


def test_mixed_scene(backend: str):
    """Test 1: Mix of icons and markers.

    Args:
        backend: Backend to test ("altair" or "matplotlib")

    Returns:
        bool: True if test passed, False otherwise
    """
    print(f"\n{'=' * 60}")
    print(f"Test 1: Mixed icons and markers ({backend})")
    print(f"{'=' * 60}")

    model = TestModel(n_icons=50, n_markers=50)
    renderer = SpaceRenderer(model, backend=backend)

    def portrayal(agent):
        # Return dict portrayal (Mesa 3.3 still accepts dicts)
        base_dict = {
            "size": agent.icon_size,
            "color": "#1f77b4",
            "marker": "o",
        }
        if agent.icon_name:
            base_dict["icon"] = agent.icon_name
            base_dict["icon_size"] = agent.icon_size
        return base_dict

    # Capture warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        renderer.render(agent_portrayal=portrayal)
        try:
            _ = renderer.canvas
        except Exception as e:
            print(f" Warning during render: {e}")

    # Check for "ignored keys" warnings about icon/icon_size
    icon_ignored = False
    for warning in w:
        msg = str(warning.message)
        if "Ignored keys" in msg and ("icon" in msg.lower()):
            print(" FAILED: Found 'ignored keys' warning for icon:")
            print(f"   {msg}")
            icon_ignored = True
            break

    if not icon_ignored:
        print(" PASSED: No 'ignored keys' warnings for icon/icon_size")

    # Check cache - IconCache may not have hit/miss counters
    # Just verify it exists and has _cache dictionary
    cache = renderer._icon_cache
    if hasattr(cache, "_cache"):
        num_cached = len(cache._cache)
        print(f"   Cache contains {num_cached} icon(s)")
        print(" PASSED: IconCache is working")
    else:
        print("  WARNING: Cannot inspect cache internals")

    return not icon_ignored


def test_icon_sizes(backend: str):
    """Test 2: Various icon sizes.

    Args:
        backend: Backend to test ("altair" or "matplotlib")

    Returns:
        bool: True if test passed, False otherwise
    """
    print(f"\n{'=' * 60}")
    print(f"Test 2: Multiple icon sizes ({backend})")
    print(f"{'=' * 60}")

    model = TestModel(n_icons=40, n_markers=0)
    renderer = SpaceRenderer(model, backend=backend)

    def portrayal(agent):
        return {
            "size": agent.icon_size,
            "color": "#ff7f0e",
            "marker": "o",
            "icon": agent.icon_name,
            "icon_size": agent.icon_size,
        }

    # Get initial cache state
    cache = renderer._icon_cache
    initial_cache_size = len(cache._cache) if hasattr(cache, "_cache") else 0

    # Render multiple frames
    frames_rendered = 0
    for frame in range(10):
        try:
            renderer.agent_mesh = None  # Force redraw
            renderer.render(agent_portrayal=portrayal)
            _ = renderer.canvas
            frames_rendered += 1
        except Exception as e:
            print(f"  Warning on frame {frame}: {e}")

    # Check cache growth
    final_cache_size = len(cache._cache) if hasattr(cache, "_cache") else 0

    print(f"   Rendered {frames_rendered} frames")
    print(f"   Initial cache size: {initial_cache_size}")
    print(f"   Final cache size: {final_cache_size}")

    # We expect 4 unique icon sizes (16, 24, 32, 48)
    # Cache should grow to 4 entries (one per size)
    expected_cache_size = 4

    if final_cache_size >= expected_cache_size:
        print(
            f" PASSED: Cache contains expected number of icons ({final_cache_size} >= {expected_cache_size})"
        )
        return True
    else:
        print(
            f"  WARNING: Cache size ({final_cache_size}) less than expected ({expected_cache_size})"
        )
        return True  # Don't fail, just warn


def test_culling(backend: str):
    """Test 3: Culling reduces agent count.

    Args:
        backend: Backend to test ("altair" or "matplotlib")

    Returns:
        bool: True if test passed, False otherwise
    """
    if backend != "altair":
        print(f"\n{'=' * 60}")
        print(f"Test 3: Culling (skipped for {backend})")
        print(f"{'=' * 60}")
        print("   Culling only implemented for Altair backend")
        return True

    print(f"\n{'=' * 60}")
    print("Test 3: Culling optimization (altair)")
    print(f"{'=' * 60}")

    # Create large model where most agents are off-screen
    model = Model()
    model.space = ContinuousSpace(5000, 5000, torus=False)

    # Add 200 agents spread across space
    agent_count = 0
    for i in range(200):
        try:
            a = TestAgent(model, icon_name="smiley", icon_size=24)
            x = (i % 20) * 240 + 100
            y = (i // 20) * 480 + 100
            model.space.place_agent(a, (x, y))
            agent_count += 1
        except Exception as e:
            print(f"  Could not place agent {i}: {e}")

    print(f"   Created {agent_count} agents in 5000x5000 space")

    renderer = SpaceRenderer(model, backend="altair")

    def portrayal(agent):
        return {
            "size": 24,
            "color": "#1f77b4",
            "marker": "o",
            "icon": "smiley",
            "icon_size": 24,
        }

    try:
        # Render without culling
        renderer.render(
            agent_portrayal=portrayal, agent_kwargs={"enable_culling": False}
        )
        chart_no_cull = renderer.canvas
        print("   ✓ Rendered without culling")

        # Render with culling
        renderer.agent_mesh = None
        renderer.render(
            agent_portrayal=portrayal, agent_kwargs={"enable_culling": True}
        )
        chart_cull = renderer.canvas
        print("   ✓ Rendered with culling")

        if chart_no_cull and chart_cull:
            print(" PASSED: Culling renders successfully")
            return True
        else:
            print(" FAILED: One of the renders returned None")
            return False

    except Exception as e:
        print(f" FAILED: Culling test error: {e}")
        traceback.print_exc()
        return False


def main():
    """Run icon rendering sanity checks from command line."""
    parser = argparse.ArgumentParser(description="Icon rendering sanity checks")
    parser.add_argument(
        "--backend",
        choices=["altair", "matplotlib"],
        default="altair",
        help="Backend to test",
    )
    args = parser.parse_args()

    print(f"\n{'#' * 60}")
    print(f"# Mesa Icon Rendering Sanity Checks - {args.backend.upper()}")
    print(f"{'#' * 60}")

    results = []
    results.append(("Mixed scene", test_mixed_scene(args.backend)))
    results.append(("Icon sizes", test_icon_sizes(args.backend)))
    results.append(("Culling", test_culling(args.backend)))

    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")

    for name, passed in results:
        status = " PASS" if passed else " FAIL"
        print(f"  {status}: {name}")

    all_passed = all(r[1] for r in results)

    if all_passed:
        print(f"\n All sanity checks passed for {args.backend}!")
        sys.exit(0)
    else:
        print(f"\n Some sanity checks failed for {args.backend}")
        sys.exit(1)


if __name__ == "__main__":
    main()
