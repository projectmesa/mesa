"""Benchmark matrix generator for Mesa icon rendering optimization.

Runs a grid of benchmarks (backend x mode x N) and outputs a Markdown table.

Usage:
    python benchmarks/backend_space_benchmark_matrix.py --backend altair --frames 120
    python benchmarks/backend_space_benchmark_matrix.py --backend matplotlib --frames 60 --ns "100,500,1000"
"""

from __future__ import annotations

import argparse
import sys

from backend_space_benchmark import BenchConfig, run_benchmark


def run_matrix(
    backend: str,
    frames: int,
    ns: list[int],
    modes: tuple[str, ...] = ("marker", "icon"),
) -> list[dict]:
    """Run benchmark matrix for given backend, N values, and modes.

    Args:
        backend: "matplotlib" or "altair"
        frames: Number of frames to render per benchmark
        ns: List of agent counts to test
        modes: Tuple of modes ("marker", "icon")

    Returns:
        List of result dictionaries
    """
    results = []
    total = len(ns) * len(modes)
    current = 0

    for n in ns:
        for mode in modes:
            current += 1
            print(f"\n[{current}/{total}] Running: {backend} {mode} N={n}")
            print("=" * 60)

            cfg = BenchConfig(backend=backend, mode=mode, n=n, frames=frames)
            res = run_benchmark(cfg)

            if res is not None:
                results.append(res)
            else:
                print(f"  Benchmark failed for {backend} {mode} N={n}")

    return results


def print_markdown_table(results: list[dict]):
    """Print results as a Markdown table.

    Args:
        results: List of benchmark result dictionaries
    """
    if not results:
        print("No results to display!")
        return

    print("\n" + "=" * 80)
    print("BENCHMARK RESULTS (Markdown Table)")
    print("=" * 80)
    print()
    print("| Backend     | Mode   | N    | Frames | Avg (ms) | P95 (ms) | Speedup |")
    print("|-------------|--------|------|--------|----------|----------|---------|")

    # Group by backend and N to calculate speedup
    grouped = {}
    for r in results:
        key = (r["backend"], r["n"])
        grouped.setdefault(key, {})[r["mode"]] = r

    for r in results:
        key = (r["backend"], r["n"])
        baseline = grouped[key].get("marker")

        if baseline and r["mode"] == "icon":
            speedup = f"{baseline['avg_frame_ms'] / r['avg_frame_ms']:.2f}x"
        elif baseline and r["mode"] == "marker":
            speedup = "1.00x (baseline)"
        else:
            speedup = "N/A"

        print(
            f"| {r['backend']:<11} | {r['mode']:<6} | {r['n']:<4} | {r['frames']:<6} | "
            f"{r['avg_frame_ms']:>8.3f} | {r['p95_frame_ms']:>8.3f} | {speedup:<7} |"
        )
    print()


def print_summary_stats(results: list[dict]):
    """Print summary statistics.

    Args:
        results: List of benchmark result dictionaries
    """
    if not results:
        return

    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)

    # Group by mode
    by_mode = {}
    for r in results:
        by_mode.setdefault(r["mode"], []).append(r["avg_frame_ms"])

    for mode, times in by_mode.items():
        avg = sum(times) / len(times)
        print(
            f"  {mode.capitalize():>6} mode: avg={avg:.3f}ms across {len(times)} tests"
        )

    # Icon vs marker comparison
    marker_times = by_mode.get("marker", [])
    icon_times = by_mode.get("icon", [])

    if marker_times and icon_times and len(marker_times) == len(icon_times):
        avg_marker = sum(marker_times) / len(marker_times)
        avg_icon = sum(icon_times) / len(icon_times)
        overhead = ((avg_icon - avg_marker) / avg_marker) * 100
        print(f"\n  Icon overhead: {overhead:+.1f}% (avg across all N)")
        print("  Target: <50% overhead for N≤1000")

    print()


def main():
    """Run benchmark matrix from command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run benchmark matrix for Mesa icon rendering"
    )
    parser.add_argument(
        "--backend",
        choices=["altair", "matplotlib"],
        required=True,
        help="Backend to benchmark",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=120,
        help="Number of frames per benchmark (default: 120)",
    )
    parser.add_argument(
        "--ns",
        type=str,
        default="100,500,1000,2000",
        help="Comma-separated agent counts (default: 100,500,1000,2000)",
    )
    parser.add_argument(
        "--modes",
        type=str,
        default="marker,icon",
        help="Comma-separated modes (default: marker,icon)",
    )
    args = parser.parse_args()

    # Parse N values
    try:
        ns = [int(x.strip()) for x in args.ns.split(",") if x.strip()]
    except ValueError:
        print(f"Error: Invalid --ns argument: {args.ns}")
        sys.exit(1)

    # Parse modes
    modes = tuple(x.strip() for x in args.modes.split(",") if x.strip())
    valid_modes = {"marker", "icon"}
    if not all(m in valid_modes for m in modes):
        print(f"Error: Invalid mode. Must be one of: {valid_modes}")
        sys.exit(1)

    print("\nRunning benchmark matrix:")
    print(f"  Backend: {args.backend}")
    print(f"  Frames:  {args.frames}")
    print(f"  N:       {ns}")
    print(f"  Modes:   {modes}")

    results = run_matrix(args.backend, args.frames, ns, modes)

    if not results:
        print("\n All benchmarks failed!")
        sys.exit(1)

    print_markdown_table(results)
    print_summary_stats(results)

    print("\n Benchmark matrix complete!")


if __name__ == "__main__":
    main()
