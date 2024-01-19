import pickle
import pandas as pd
from scipy import stats
import numpy as np

filename1 = 'timings_1'
filename2 = 'timings_2'

with open(f"{filename1}.pickle", 'rb') as handle:
    timings_1 = pickle.load(handle)

with open(f"{filename2}.pickle", 'rb') as handle:
    timings_2 = pickle.load(handle)


# Function to calculate the percentage change and perform bootstrap to estimate the confidence interval
def bootstrap_percentage_change_confidence_interval(data1, data2, n=1000):
    change_samples = []
    for _ in range(n):
        sampled_indices = np.random.choice(range(len(data1)), size=len(data1), replace=True)
        sampled_data1 = np.array(data1)[sampled_indices]
        sampled_data2 = np.array(data2)[sampled_indices]
        change = 100 * (sampled_data2 - sampled_data1) / sampled_data1
        change_samples.append(np.mean(change))
    lower, upper = np.percentile(change_samples, [2.5, 97.5])
    return np.mean(change_samples), lower, upper

# DataFrame to store the results
results_df = pd.DataFrame()

# Iterate over the models and sizes, perform analysis, and populate the DataFrame
for (model, size) in timings_1.keys():
    model_name = model.__name__

    # Calculate percentage change and confidence interval for init times
    init_change, init_lower, init_upper = bootstrap_percentage_change_confidence_interval(timings_1[(model, size)][0], timings_2[(model, size)][0])
    init_summary = f"{init_change:+.1f}% [{init_lower:+.1f}%, {init_upper:+.1f}%]"

    # Calculate percentage change and confidence interval for run times
    run_change, run_lower, run_upper = bootstrap_percentage_change_confidence_interval(timings_1[(model, size)][1], timings_2[(model, size)][1])
    run_summary = f"{run_change:+.1f}% [{run_lower:+.1f}%, {run_upper:+.1f}%]"

    # Append results to DataFrame
    row = pd.DataFrame({
        'Model': [model_name],
        'Size': [size],
        'Init time [95% CI]': [init_summary],
        'Run time [95% CI]': [run_summary]
    })

    results_df = pd.concat([results_df, row], ignore_index=True)

# Display the DataFrame
print(results_df.to_markdown(index=False))

