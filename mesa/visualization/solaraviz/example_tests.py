"""
Example test execution script that can be used to manually run the tests.
This is separate from the test files themselves and serves as a way
to run and view test results programmatically.
"""

import sys
import os
import logging
import argparse
import subprocess
import json
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define test categories
TEST_CATEGORIES = {
    "basic": "tests/test_solara_viz.py",
    "integration": "tests/test_viz_integration.py",
    "performance": "tests/test_viz_performance.py",
    "regression": "tests/test_viz_regression.py"
}

def run_test(category: str, verbose: bool = True, benchmark: bool = False) -> Dict[str, Any]:
    """
    Run a specific test category and return the results
    
    Args:
        category: Test category to run (basic, integration, performance, regression)
        verbose: Whether to show verbose output
        benchmark: Whether to generate benchmark output (for performance tests)
        
    Returns:
        Dictionary with test results
    """
    if category not in TEST_CATEGORIES:
        logger.error(f"Unknown test category: {category}")
        return {"error": f"Unknown test category: {category}"}
    
    test_path = TEST_CATEGORIES[category]
    benchmark_file = None
    
    # Build command
    cmd = ["python", "-m", "pytest", test_path]
    
    if verbose:
        cmd.append("-v")
    
    if benchmark and category == "performance":
        benchmark_file = f"{category}_benchmark.json"
        cmd.extend(["--benchmark-json", benchmark_file])
    
    # Run the tests
    logger.info(f"Running {category} tests: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Process the output
        if result.returncode == 0:
            logger.info(f"{category} tests completed successfully")
            status = "success"
        else:
            logger.warning(f"{category} tests completed with failures")
            status = "failure"
        
        # Parse benchmark results if available
        benchmark_results = None
        if benchmark_file and benchmark and category == "performance" and os.path.exists(benchmark_file):
            try:
                with open(benchmark_file, 'r') as f:
                    benchmark_results = json.load(f)
            except Exception as e:
                logger.error(f"Error parsing benchmark results: {e}")
        
        return {
            "status": status,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "benchmark_results": benchmark_results
        }
    
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        return {"error": str(e)}

def run_all_tests(verbose: bool = True, benchmark: bool = False) -> Dict[str, Dict[str, Any]]:
    """
    Run all test categories
    
    Args:
        verbose: Whether to show verbose output
        benchmark: Whether to generate benchmark output
        
    Returns:
        Dictionary mapping test categories to their results
    """
    results = {}
    
    for category in TEST_CATEGORIES:
        results[category] = run_test(category, verbose, benchmark)
    
    return results

def parse_test_output(output: str) -> List[Dict[str, Any]]:
    """
    Parse pytest output to extract test results
    
    Args:
        output: Pytest output string
        
    Returns:
        List of dictionaries with test information
    """
    import re
    tests = []
    
    # Extract test result lines with regex
    # Pattern matches lines like: tests/test_solara_viz.py::test_solara_imports PASSED [0.12s]
    test_pattern = r'(tests/[\w/]+\.py::[\w\[\]]+(?:\[[\w\d-]+\])?) (PASSED|FAILED|SKIPPED|XFAILED|XPASSED|ERROR)(?:\s+\[(.+)s\])?'
    test_matches = re.findall(test_pattern, output)
    
    for match in test_matches:
        test_name = match[0]
        status = match[1].lower()
        duration_str = match[2] if len(match) > 2 and match[2] else None
        
        # Convert duration to float if available
        duration = float(duration_str) if duration_str else None
        
        # Extract error message for failed tests
        message = None
        if status == 'failed':
            # Look for the error message after the test name
            error_pattern = f"{re.escape(test_name)}.*?FAILED.*?\n(.*?)(?:=+ |$)"
            error_match = re.search(error_pattern, output, re.DOTALL)
            if error_match:
                message = error_match.group(1).strip()
        
        tests.append({
            "name": test_name,
            "status": status,
            "duration": duration,
            "message": message
        })
    
    return tests

def main():
    """Main function to run tests from command line"""
    parser = argparse.ArgumentParser(description="Run Mesa SolaraViz tests")
    parser.add_argument("--category", choices=list(TEST_CATEGORIES.keys()) + ["all"], default="all",
                       help="Test category to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show verbose output")
    parser.add_argument("--benchmark", "-b", action="store_true", help="Generate benchmark output")
    parser.add_argument("--output", "-o", help="Output file for results")
    
    args = parser.parse_args()
    
    # Run tests
    if args.category == "all":
        results = run_all_tests(args.verbose, args.benchmark)
    else:
        results = {args.category: run_test(args.category, args.verbose, args.benchmark)}
    
    # Process results
    processed_results = {}
    for category, result in results.items():
        if "error" in result:
            processed_results[category] = {"error": result["error"]}
        else:
            processed_results[category] = {
                "status": result["status"],
                "tests": parse_test_output(result["stdout"])
            }
            if result.get("benchmark_results"):
                processed_results[category]["benchmark"] = result["benchmark_results"]
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(processed_results, f, indent=2)
    else:
        # Print summary
        for category, result in processed_results.items():
            print(f"\n=== {category.upper()} TESTS ===")
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                tests = result["tests"]
                passed = sum(1 for t in tests if t["status"] == "passed")
                failed = sum(1 for t in tests if t["status"] == "failed")
                skipped = sum(1 for t in tests if t["status"] == "skipped")
                print(f"Status: {result['status']}")
                print(f"Tests: {len(tests)} total, {passed} passed, {failed} failed, {skipped} skipped")
                
                if failed > 0:
                    print("\nFailed tests:")
                    for test in tests:
                        if test["status"] == "failed":
                            duration_str = f"{test['duration']:.3f}s" if test['duration'] is not None else "N/A"
                            print(f"  - {test['name']} ({duration_str})")

if __name__ == "__main__":
    main()