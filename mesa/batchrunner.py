# -*- coding: utf-8 -*-
"""
Batchrunner
===========

A single class to manage a batch run or parameter sweep of a given model.

"""
from itertools import product
import pandas as pd
from tqdm import tqdm


class BatchRunner:
    """ This class is instantiated with a model class, and model parameters
    associated with one or more values. It is also instantiated with model and
    agent-level reporters, dictionaries mapping a variable name to a function
    which collects some data from the model or its agents at the end of the run
    and stores it.

    Note that by default, the reporters only collect data at the *end* of the
    run. To get step by step data, simply have a reporter store the model's
    entire DataCollector object.

    """
    def __init__(self, model_cls, parameter_values, iterations=1,
                 max_steps=1000, model_reporters=None, agent_reporters=None,
                 display_progress=True):
        """ Create a new BatchRunner for a given model with the given
        parameters.

        Args:
            model_cls: The class of model to batch-run.
            parameter_values: Dictionary of parameters to their values or
                ranges of values. For example:
                    {"param_1": range(5),
                     "param_2": [1, 5, 10],
                      "const_param": 100}
            iterations: The total number of times to run the model for each
                combination of parameters.
            max_steps: The upper limit of steps above which each run will be halted
                if it hasn't halted on its own.
            model_reporters: The dictionary of variables to collect on each run at
                the end, with variable names mapped to a function to collect
                them. For example:
                    {"agent_count": lambda m: m.schedule.get_agent_count()}
            agent_reporters: Like model_reporters, but each variable is now
                collected at the level of each agent present in the model at
                the end of the run.
            display_progress: Display progresss bar with time estimation?

        """
        self.model_cls = model_cls
        self.parameter_values = {param: self.make_iterable(vals)
                                 for param, vals in parameter_values.items()}
        self.iterations = iterations
        self.max_steps = max_steps

        self.model_reporters = model_reporters
        self.agent_reporters = agent_reporters

        if self.model_reporters:
            self.model_vars = {}

        if self.agent_reporters:
            self.agent_vars = {}

        self.display_progress = display_progress

    def run_all(self):
        """ Run the model at all parameter combinations and store results. """
        params = self.parameter_values.keys()
        param_ranges = self.parameter_values.values()
        run_count = 0

        if self.display_progress:
            pbar = tqdm(total=len(list(product(*param_ranges))) * self.iterations)

        for param_values in list(product(*param_ranges)):
            kwargs = dict(zip(params, param_values))
            for _ in range(self.iterations):
                model = self.model_cls(**kwargs)
                self.run_model(model)
                # Collect and store results:
                if self.model_reporters:
                    key = tuple(list(param_values) + [run_count])
                    self.model_vars[key] = self.collect_model_vars(model)
                if self.agent_reporters:
                    agent_vars = self.collect_agent_vars(model)
                    for agent_id, reports in agent_vars.items():
                        key = tuple(list(param_values) + [run_count, agent_id])
                        self.agent_vars[key] = reports
                if self.display_progress:
                    pbar.update()

                run_count += 1

        if self.display_progress:
            pbar.close()

    def run_model(self, model):
        """ Run a model object to completion, or until reaching max steps.

        If your model runs in a non-standard way, this is the method to modify
        in your subclass.

        """
        while model.running and model.schedule.steps < self.max_steps:
            model.step()

    def collect_model_vars(self, model):
        """ Run reporters and collect model-level variables. """
        model_vars = {}
        for var, reporter in self.model_reporters.items():
            model_vars[var] = reporter(model)
        return model_vars

    def collect_agent_vars(self, model):
        """ Run reporters and collect agent-level variables. """
        agent_vars = {}
        for agent in model.schedule.agents:
            agent_record = {}
            for var, reporter in self.agent_reporters.items():
                agent_record[var] = reporter(agent)
            agent_vars[agent.unique_id] = agent_record
        return agent_vars

    def get_model_vars_dataframe(self):
        """ Generate a pandas DataFrame from the model-level variables collected.

        """
        index_col_names = list(self.parameter_values.keys())
        index_col_names.append("Run")
        records = []
        for key, val in self.model_vars.items():
            record = dict(zip(index_col_names, key))
            for k, v in val.items():
                record[k] = v
            records.append(record)
        return pd.DataFrame(records)

    def get_agent_vars_dataframe(self):
        """ Generate a pandas DataFrame from the agent-level variables
        collected.

        """
        index_col_names = list(self.parameter_values.keys())
        index_col_names += ["Run", "AgentID"]
        records = []
        for key, val in self.agent_vars.items():
            record = dict(zip(index_col_names, key))
            for k, v in val.items():
                record[k] = v
            records.append(record)
        return pd.DataFrame(records)

    @staticmethod
    def make_iterable(val):
        """ Helper method to ensure a value is a non-string iterable. """
        if hasattr(val, "__iter__") and not isinstance(val, str):
            return val
        else:
            return [val]
