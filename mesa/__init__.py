# -*- coding: utf-8 -*-
"""
Mesa Agent-Based Modeling Framework

Core Objects: Model, and Agent.

"""
import datetime

from .model import Model
from .agent import Agent


__all__ = ["Model", "Agent"]

__title__ = "mesa"
__version__ = "0.8.7"
__license__ = "Apache 2.0"
__copyright__ = "Copyright %s Project Mesa Team" % datetime.date.today().year
