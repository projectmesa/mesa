import contextlib
import glob
import itertools
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from mesa import Model

with contextlib.suppress(ImportError):
    import pandas as pd


class CacheableModel:
    """Class that takes a model and writes its steps to a cache file or reads them from a cache file."""

    def __init__(
        self,
        model: Model,
        cache_file_path: str | Path,
        total_steps: int,
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
        self._total_steps = total_steps
        self.step_count: int = 0
        self.run_finished = False

        # temporary dicts to be flushed
        self.model_vars_cache = {}
        self._agent_records = {}

        self._cache_interval = 100

        self._last_cached_step = 0  # inclusive since it is the bottom bound of slicing
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

        all_records = itertools.chain.from_iterable(
            self.model.datacollector._agent_records.values()
        )
        rep_names = list(self.model.datacollector.agent_reporters)
        print(f"{all_records=}")
        print(f"{rep_names=}")

        df = pd.DataFrame.from_records(
            data=all_records,
            columns=["Step", "AgentID", *rep_names],
            index=["Step", "AgentID"],
        )

        sliced_df = df.loc[self._last_cached_step : self.model._steps]

        return sliced_df

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

        return pd.DataFrame(self.model.datacollector.model_vars)[
            self._last_cached_step : self.model._steps
        ]

    def _save_to_parquet(self, model):
        """Save the current cache of data to a Parquet file and clear the cache."""
        model_df = self.get_model_vars_dataframe()
        agent_df = self.get_agent_vars_dataframe()
        padding = len(str(self._total_steps)) - 1

        # ceiling function
        model_file = f"{self.cache_file_path}/model_data_{-(self.model._steps // -self._cache_interval):0{padding}}.parquet"
        agent_file = f"{self.cache_file_path}/agent_data_{-(self.model._steps // -self._cache_interval):0{padding}}.parquet"

        self.cache_file_path.mkdir(parents=True, exist_ok=True)

        absolute_path = os.path.abspath(model_file)
        if os.path.exists(absolute_path):
            raise FileExistsError(
                f"A directory with the name {model_file} already exists."
            )
        if os.path.exists(model_file):
            raise FileExistsError(
                f"A directory with the name {model_file} already exists."
            )
        if os.path.exists(agent_file):
            raise FileExistsError(
                f"A directory with the name {agent_file} already exists."
            )

        if not model_df.empty:
            model_table = pa.Table.from_pandas(model_df)
            pq.write_table(model_table, model_file)

        if not agent_df.empty:
            agent_table = pa.Table.from_pandas(agent_df)
            pq.write_table(agent_table, agent_file)

    def cache(self):
        """Custom collect method to extend the original collect behavior."""
        # Implement your custom logic here
        # For example, let's say we want to write collected data to a cache file every `cache_step_rate` steps
        if (
            self.model._steps % self._cache_interval == 0
            or self.model._steps == self._total_steps
        ):
            self._save_to_parquet(self.model)
            self._last_cached_step = self.model._steps

        if self.condition_function and self.save_special_results(
            self.condition_function
        ):
            pass

    def save_special_results(self, condition_function: Callable[[dict], bool]):
        model_vars = self.model.datacollector.model_vars
        self.cache_file_path.mkdir(parents=True, exist_ok=True)

        current_step = self.model._steps
        special_results_file = f"{self.cache_file_path}/special_results.parquet"
        if condition_function(model_vars):
            step_data = {key: [value[-1]] for key, value in model_vars.items()}
            step_data["Step"] = current_step
            special_results_df = pd.DataFrame(step_data)

            # Append the current step data to the Parquet file
            if os.path.exists(special_results_file):
                existing_data = pq.read_table(special_results_file).to_pandas()
                combined_data = pd.concat(
                    [existing_data, special_results_df], ignore_index=True
                )
                special_results_table = pa.Table.from_pandas(combined_data)
            else:
                special_results_table = pa.Table.from_pandas(special_results_df)

            pq.write_table(special_results_table, special_results_file)

            print(
                f"Condition met. Appended special results for step {current_step} to {special_results_file}"
            )
        else:
            print(f"Condition not met at step {current_step}. No data to save.")

    def read_model_data(self):
        """Read and combine all model data Parquet files into a single DataFrame."""
        model_files = glob.glob(f"{self.cache_file_path}/model_data_*.parquet")
        model_dfs = []

        for model_file in model_files:
            table = pq.read_table(model_file)
            df = table.to_pandas()
            model_dfs.append(df)

        if model_dfs:
            model_df = pd.concat(model_dfs, ignore_index=True)
            return model_df
        else:
            raise FileNotFoundError("No model data files found.")

    def read_agent_data(self):
        """Read and combine all agent data Parquet files into a single DataFrame."""
        agent_files = glob.glob(f"{self.cache_file_path}/agent_data_*.parquet")
        agent_dfs = []

        for agent_file in agent_files:
            table = pq.read_table(agent_file)
            df = table.to_pandas()
            agent_dfs.append(df)

        if agent_dfs:
            agent_df = pd.concat(agent_dfs)
            return agent_df
        else:
            raise FileNotFoundError("No agent data files found.")

    def combine_dataframes(self):
        """Combine and return the model and agent DataFrames."""
        try:
            model_df = self.read_model_data()
            agent_df = self.read_agent_data()

            # Sort agent DataFrame by the multi-index (Step, AgentID) to ensure order
            agent_df = agent_df.sort_index()

            return model_df, agent_df
        except FileNotFoundError as e:
            print(e)
            return None, None


# FOR GRID KIV IGNORE NOW
from mesa.agent import Agent


class AgentSerializer:
    @staticmethod
    def agent_to_dict(agent: Agent) -> dict[str, Any]:
        """Convert an Agent instance to a dictionary."""
        return {
            "unique_id": agent.unique_id,
            "model": str(agent.model),  # Convert model to a string or identifier
            "pos": str(agent.pos)
            if agent.pos
            else None,  # Convert position to a string or identifier
        }

    @staticmethod
    def dict_to_agent(agent_dict: dict[str, Any], model: Any) -> Agent:
        """Convert a dictionary to an Agent instance."""
        unique_id = agent_dict["unique_id"]
        pos = agent_dict["pos"] if agent_dict["pos"] != "None" else None
        agent = Agent(unique_id=unique_id, model=model)
        agent.pos = pos
        return agent

    @staticmethod
    def save_agents_to_parquet(agents: list[Agent], filename: str) -> None:
        """Save a list of agents to a Parquet file."""
        agent_dicts = [AgentSerializer.agent_to_dict(agent) for agent in agents]
        df = pd.DataFrame(agent_dicts)
        df.to_parquet(filename)

    @staticmethod
    def load_agents_from_parquet(filename: str, model: Any) -> list[Agent]:
        """Load agents from a Parquet file."""
        df = pd.read_parquet(filename)
        agents = [
            AgentSerializer.dict_to_agent(row.to_dict(), model)
            for _, row in df.iterrows()
        ]
        return agents
