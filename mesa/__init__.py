"""Mesa Agent-Based Modeling Framework.

Core Objects: Model, and Agent.
"""

import datetime

import mesa.experimental as experimental
import mesa.space as space
from mesa.agent import Agent
from mesa.batchrunner import batch_run
from mesa.datacollection import DataCollector
from mesa.model import Model

__all__ = [
    "Agent",
    "DataCollector",
    "Model",
    "batch_run",
    "experimental",
    "space",
]

__title__ = "mesa"
__version__ = "3.1.1"
__license__ = "Apache 2.0"
_this_year = datetime.datetime.now(tz=datetime.UTC).date().year
__copyright__ = f"Copyright {_this_year} Project Mesa Team"
