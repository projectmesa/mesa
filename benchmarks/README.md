# Mesa Performance Benchmarks

This directory contains tools for benchmarking Mesa model performance. These benchmarks help track performance improvements and regressions across different versions of Mesa.

## Available Files

- `configurations.py`: Contains model configurations for benchmarking
- `global_benchmark.py`: Main script for running benchmarks
- `compare_timings.py`: Tool to compare results between benchmark runs

## How to Use

### 1. Running Benchmarks

To run the benchmarks:

```bash
python global_benchmark.py
```

This will:
- Run all models defined in `configurations.py` with their respective configurations
- Measure initialization time and run time for each model
- Save results to a pickle file named `timings_X.pickle` (where X is an incremental number)
- Display a summary of results in the terminal

#### What's being measured:

- **Initialization time**: How long it takes to create model instances
- **Run time**: How long it takes to run the model for the specified number of steps

### 2. Benchmark Configuration

The `configurations.py` file defines which models to benchmark and their parameters. Each model has:

- `small` and `large` configurations for testing different scales
- Parameters for:
  - `seeds`: Number of different random seeds to use
  - `replications`: Number of times to repeat the benchmark for each seed
  - `steps`: Number of model steps to run
  - `parameters`: Model-specific parameters

Example of adding a new model to benchmark:

```python
MyNewModel: {
    "small": {
        "seeds": 20,
        "replications": 3,
        "steps": 50,
        "parameters": {
            "width": 50,
            "height": 50,
            # other model parameters
        },
    },
    "large": {
        # large configuration
    }
}
```

### 3. Comparing Results

After running benchmarks at different times (e.g., before and after code changes), you can compare the results:

1. Rename your benchmark files to distinguish them (e.g., `timings_before.pickle` and `timings_after.pickle`)
2. Edit `compare_timings.py` to use your file names:
   ```python
   filename1 = "timings_before"
   filename2 = "timings_after"
   ```
3. Run the comparison:
   ```bash
   python compare_timings.py
   ```

The output will show:
- Percentage changes in initialization and run times
- 95% confidence intervals for the changes
- Emojis indicating performance changes:
  - 🟢 Faster performance (>3% improvement)
  - 🔴 Slower performance (>3% regression)
  - 🔵 Insignificant change (within ±3%)

## Tips for Effective Benchmarking

1. **Run on an idle system** for more consistent results
2. **Run multiple times** to account for system variability
3. **Compare only within the same environment** (same hardware, OS, Python version)
4. **Increase replications** for more precise measurements of small changes
5. **Add custom models** to `configurations.py` to benchmark specific components

## Example Workflow

1. Run benchmarks on your current Mesa version:
   ```bash
   python global_benchmark.py
   # Results saved as timings_1.pickle
   ```

2. Make code changes (e.g., optimize AgentSet methods)

3. Run benchmarks again:
   ```bash
   python global_benchmark.py
   # Results saved as timings_2.pickle
   ```

4. Compare results:
   ```bash
   python compare_timings.py
   # Shows performance change table
   ```

5. Use the results to validate your optimizations or identify regressions