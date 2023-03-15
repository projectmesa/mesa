"""
Mesa Agent-Based Modeling Framework

Core Objects: Model, and Agent.
"""
import datetime

import mesa.flat.visualization as visualization
import mesa.space as space
import mesa.time as time
from mesa.agent import Agent
from mesa.batchrunner import batch_run
from mesa.datacollection import DataCollector
from mesa.model import Model

__all__ = [
    "Model",
    "Agent",
    "time",
    "space",
    "visualization",
    "DataCollector",
    "batch_run",
]

__title__ = "mesa"
__version__ = "1.2.1"
__license__ = "Apache 2.0"
_this_year = datetime.datetime.now(tz=datetime.timezone.utc).date().year
__copyright__ = f"Copyright {_this_year} Project Mesa Team"
