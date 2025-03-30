
"""
Performance report generator for Mesa's SolaraViz visualization components.
"""
import json
import datetime
from pathlib import Path
from typing import Dict, Any, List

def generate_performance_report(benchmark_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a detailed performance report from benchmark data"""
    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "summary": {
            "total_tests": len(benchmark_data["benchmarks"]),
            "total_time": sum(b["stats"]["mean"] for b in benchmark_data["benchmarks"]),
            "slowest_test": max(benchmark_data["benchmarks"], key=lambda x: x["stats"]["mean"]),
            "fastest_test": min(benchmark_data["benchmarks"], key=lambda x: x["stats"]["mean"])
        },
        "detailed_results": []
    }
    
    for benchmark in benchmark_data["benchmarks"]:
        report["detailed_results"].append({
            "name": benchmark["name"],
            "mean_time": benchmark["stats"]["mean"],
            "std_dev": benchmark["stats"]["stddev"],
            "rounds": benchmark["stats"]["rounds"],
            "median": benchmark["stats"]["median"],
            "iterations": benchmark["stats"]["iterations"]
        })
    
    return report

def save_report(report: Dict[str, Any], output_dir: str = "performance_reports") -> str:
    """Save the performance report to a file"""
    Path(output_dir).mkdir(exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/performance_report_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump(report, f, indent=2)
    
    return filename

def analyze_trends(reports_dir: str = "performance_reports") -> Dict[str, Any]:
    """Analyze performance trends across multiple reports"""
    reports = []
    for report_file in Path(reports_dir).glob("performance_report_*.json"):
        with open(report_file) as f:
            reports.append(json.load(f))
    
    if not reports:
        return {"error": "No reports found"}
    
    trends = {
        "test_count": len(reports),
        "time_range": {
            "start": reports[0]["timestamp"],
            "end": reports[-1]["timestamp"]
        },
        "performance_trends": {}
    }
    
    # Analyze trends for each test
    for test in reports[0]["detailed_results"]:
        test_name = test["name"]
        trends["performance_trends"][test_name] = {
            "mean_times": [test["mean_time"] for report in reports 
                         for t in report["detailed_results"] if t["name"] == test_name],
            "trend": "stable"  # Will be updated based on analysis
        }
    
    return trends
