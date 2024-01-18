import timeit
import os
import sys
import gc
import random

from configurations import configurations

# Generic function to initialize and run a model
def run_model(model_class, seed, parameters):
    start_init = timeit.default_timer()
    model = model_class(seed, **parameters)

    end_init_start_run = timeit.default_timer()

    for _ in range(config['steps']):
        model.step()
    end_run = timeit.default_timer()

    return (end_init_start_run - start_init), (end_run - end_init_start_run)


# Function to run experiments and save the fastest replication for each seed
def run_experiments(model_class, config):
    gc.enable()
    sys.path.insert(0, os.path.abspath("."))

    init_times = []
    run_times = []
    for seed in range(1, config['seeds'] + 1):
        fastest_init = float('inf')
        fastest_run = float('inf')
        for replication in range(1, config['replications'] + 1):
            init_time, run_time = run_model(model_class, seed, config["parameters"])
            if init_time < fastest_init:
                fastest_init = init_time
            if run_time < fastest_run:
                fastest_run = run_time
        init_times.append(fastest_init)
        run_times.append(fastest_run)

    return init_times, run_times

for model, model_config in configurations.items():
    for size, config in model_config.items():
        results = run_experiments(model, config)
        print(results)
        # Save the results in a file
        # with open(f'./results/{model}_{size}.csv', 'w') as f:
        #     f.write('Seed,Initialization,Run\n')
        #     for seed, times in results.items():
        #         f.write(f'{seed},{times["Initialization"]},{times["Run"]}\n')

# Similarly, run experiments for other models (WolfSheep, Flocking) by passing the appropriate model class and configuration
