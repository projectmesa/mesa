"""
Mesa Agent-Based Modeling Framework
Core Objects: Model, and Agent.
"""

import datetime

from mesa import space, time
from mesa.agent import Agent
from mesa.batchrunner import batch_run  # Add this line to import batch_run
from mesa.datacollection import DataCollector
from mesa.model import Model

__all__ = [
    "Model",
    "Agent",
    "time",
    "space",
    "DataCollector",
    "batch_run",  # Add this line to include batch_run in __all__
    "experimental",
]

__title__ = "mesa"
__version__ = "3.0.0a0"
__license__ = "Apache 2.0"
_this_year = datetime.datetime.now(tz=datetime.timezone.utc).date().year
__copyright__ = f"Copyright {_this_year} Project Mesa Team"

def get_batch_run():
    from mesa.batchrunner import batch_run
    return batch_run

def get_Model():
    from mesa import Model
    return Model
