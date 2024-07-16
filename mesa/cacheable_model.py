import os
import contextlib
import itertools
import types
from copy import deepcopy
from functools import partial
from typing import Any, Callable

import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path
from enum import Enum
from mesa import Model

with contextlib.suppress(ImportError):
    import pandas as pd


class CacheState(Enum):
    """When using 'RECORD', with every simulation step the actual simulation will be performed and the model state
    written to the cache (also called simulation mode).
    When using 'REPLAY', with every step the model state will be read from the cache (also called replay mode)."""

    RECORD = (1,)
    REPLAY = 2


class CacheableModel:
    """Class that takes a model and writes its steps to a cache file or reads them from a cache file."""

    def __init__(
        self,
        model: Model,
        cache_file_path: str | Path,
        # cache_state: CacheState,
        total_steps: int,
        # cache_step_rate: int = 1,
        condition_function=None,
    ) -> None:
        """Create a new caching wrapper around an existing mesa model instance.

        Attributes:
            model: mesa model
            cache_file_path: cache file to write to or read from
            cache_state: whether to replay by reading from the cache or simulate and write to the cache
            cache_step_rate: only every n-th step is cached. If it is 1, every step is cached. If it is 2,
            only every second step is cached and so on. Increasing 'cache_step_rate' will reduce cache size and
            increase replay performance by skipping the steps inbetween every n-th step.
        """

        self.model = model
        self.cache_file_path = Path(cache_file_path)
        # self._cache_state = cache_state
        # self._cache_step_rate = cache_step_rate
        self._total_steps = total_steps
        # self.cache: list[Any] = []
        self.step_count: int = 0
        self.run_finished = False

        # temporary dicts to be flushed
        self.model_vars_cache = {}


        self._agent_records = {}

        self._cache_interval = 100
        # self.output_dir = 'output_dir'

        self._last_cached_step = 0 # inclusive since it is the bottom bound of slicing
        self.condition_function = condition_function
    def get_agent_vars_dataframe(self):
        """Create a pandas DataFrame from the agent variables.

        The DataFrame has one column for each variable, with two additional
        columns for tick and agent_id.
        """
        # Check if self.agent_reporters dictionary is empty, if so raise warning
        if not self.model.datacollector.agent_reporters:
            raise UserWarning(
                "No agent reporters have been defined in the DataCollector, returning empty DataFrame."
            )

        all_records = itertools.chain.from_iterable(self._agent_records.values())
        rep_names = list(self.model.datacollector.agent_reporters)

        df = pd.DataFrame.from_records(
            data=all_records,
            columns=["Step", "AgentID", *rep_names],
            index=["Step", "AgentID"],
        )
        return df

    def get_model_vars_dataframe(self):
        """Create a pandas DataFrame from the model variables.

        The DataFrame has one column for each model variable, and the index is
        (implicitly) the model tick.
        """
        # Check if self.model_reporters dictionary is empty, if so raise warning
        if not self.model.datacollector.model_reporters:
            raise UserWarning(
                "No model reporters have been defined in the DataCollector, returning empty DataFrame."
            )

        print(f" TEST {self.model._steps=}")
        print(f" TEST {self._cache_interval=}")
        print(pd.DataFrame(self.model.datacollector.model_vars)[self._last_cached_step:self.model._steps])
        return pd.DataFrame(self.model.datacollector.model_vars)[self._last_cached_step:self.model._steps]

    # def get_table_dataframe(self, table_name):
    #     """Create a pandas DataFrame from a particular table.
    #
    #     Args:
    #         table_name: The name of the table to convert.
    #     """
    #     if table_name not in self.tables:
    #         raise Exception("No such table.")
    #     return pd.DataFrame(self.tables[table_name])

    def _save_to_parquet(self, model):
        """Save the current cache of data to a Parquet file and clear the cache."""
        model_df = self.get_model_vars_dataframe()
        agent_df = self.get_agent_vars_dataframe()
        padding = len(str(self._total_steps)) - 1
        print(padding)

        # ceiling function
        model_file = f"{self.cache_file_path}/model_data_{-(self.model._steps // -self._cache_interval):0{padding}}.parquet"
        agent_file = f"{self.cache_file_path}/agent_data_{-(self.model._steps // -self._cache_interval):0{padding}}.parquet"

        self.cache_file_path.mkdir(parents=True, exist_ok=True)

        print(f"{model_file=}")
        absolute_path = os.path.abspath(model_file)
        print(f"{absolute_path=}")
        if os.path.exists(absolute_path):
            raise FileExistsError(f"A directory with the name {model_file} already exists.")
        if os.path.exists(model_file):
            raise FileExistsError(f"A directory with the name {model_file} already exists.")
        if os.path.exists(agent_file):
            raise FileExistsError(f"A directory with the name {agent_file} already exists.")

        if not model_df.empty:
            print(f"Saving model to {model_file}")
            model_table = pa.Table.from_pandas(model_df)
            pq.write_table(model_table, model_file)

        if not agent_df.empty:
            print(f"Saving agent to {agent_file}")
            agent_table = pa.Table.from_pandas(agent_df)
            pq.write_table(agent_table, agent_file)

        # Clear the cache


    def cache(self):
        """Custom collect method to extend the original collect behavior."""
        # Implement your custom logic here
        # For example, let's say we want to write collected data to a cache file every `cache_step_rate` steps
        if self.model._steps % self._cache_interval == 0:
            print("CALLED")
            print(f"{self.model._steps=}")
            self._save_to_parquet(self.model)
            self._last_cached_step = self.model._steps
        elif self.model._steps == self._total_steps:
            print("FINAL CALLED")
            print(f"{self.model._steps=}")
            self._save_to_parquet(self.model)
            self._last_cached_step = self.model._steps

        if self.condition_function and self.save_special_results(self.condition_function):
            # print("CHECK SPECIAL RESULTS CONDITION")
            pass

    def save_special_results(self, condition_function: Callable[[dict], bool]):

        model_vars = self.model.datacollector.model_vars
        # print(f"{model_vars=}")
        print(f"{model_vars.get('Gini', 0)[-1]=}")
        self.cache_file_path.mkdir(parents=True, exist_ok=True)
        # if condition_function(model_vars):
        #     special_results_df = pd.DataFrame(model_vars)
        #     special_results_file = f"{self.cache_file_path}/special_results.parquet"
        #
        #
        #     if not special_results_df.empty:
        #         print(f"Condition met. Saving special results to {special_results_file}")
        #         special_results_table = pa.Table.from_pandas(special_results_df)
        #         pq.write_table(special_results_table, special_results_file)
        #     else:
        #         print("Condition met but no data to save.")

        current_step = self.model._steps
        special_results_file = f"{self.cache_file_path}/special_results.parquet"
        if condition_function(model_vars):
            step_data = {key: [value[-1]] for key, value in model_vars.items()}
            step_data['Step'] = current_step
            special_results_df = pd.DataFrame(step_data)

            # Append the current step data to the Parquet file
            if os.path.exists(special_results_file):
                existing_data = pq.read_table(special_results_file).to_pandas()
                combined_data = pd.concat([existing_data, special_results_df], ignore_index=True)
                special_results_table = pa.Table.from_pandas(combined_data)
            else:
                special_results_table = pa.Table.from_pandas(special_results_df)

            pq.write_table(special_results_table, special_results_file)

            print(f"Condition met. Appended special results for step {current_step} to {special_results_file}")
        else:
            print(f"Condition not met at step {current_step}. No data to save.")
