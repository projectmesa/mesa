"""
Mesa Agent-Based Modeling Framework
Core Objects: Model, and Agent.
"""
import datetime
from mesa import space, time
from mesa.agent import Agent
from mesa.datacollection import DataCollector
from mesa.model import Model

def batch_run(*args, **kwargs):
    from mesa.batchrunner import batch_run as _batch_run
    return _batch_run(*args, **kwargs)

__all__ = [
    "Model",
    "Agent",
    "time",
    "space",
    "DataCollector",
    "batch_run",
    "experimental",
]

__title__ = "mesa"
__version__ = "3.0.0a0"
__license__ = "Apache 2.0"
_this_year = datetime.datetime.now(tz=datetime.timezone.utc).date().year
__copyright__ = f"Copyright {_this_year} Project Mesa Team"

# If 'experimental' is defined elsewhere, you might need to import it here
# or define it if it's missing
