"""This provides logging functionality for MESA.

It is modeled on the default `logging approach that comes with Python <https://docs.python.org/library/logging.html>`_.


"""

import inspect
import logging
from functools import wraps
from logging import DEBUG, INFO

__all__ = [
    "get_rootlogger",
    "get_module_logger",
    "log_to_stderr",
    "DEBUG",
    "INFO",
    "DEFAULT_LEVEL",
    "LOGGER_NAME",
    "method_logger",
    "function_logger",
]
LOGGER_NAME = "MESA"
DEFAULT_LEVEL = DEBUG


def create_module_logger(name:str|None=None):
    """Helper function for creating a module logger.

    Args:
        name (str): The name to be given to the logger. If the name is None, the name defaults to the name of the module.

    """
    if name is None:
        frm = inspect.stack()[1]
        mod = inspect.getmodule(frm[0])
        name = mod.__name__
    logger = logging.getLogger(f"{LOGGER_NAME}.{name}")

    _module_loggers[name] = logger
    return logger


def get_module_logger(name:str):
    """Helper function for getting the module logger.

    Args:
        name (str): The name of the module in which the method being decorated is located

    """
    try:
        logger = _module_loggers[name]
    except KeyError:
        logger = create_module_logger(name)

    return logger


_rootlogger = None
_module_loggers = {}
_logger = get_module_logger(__name__)

LOG_FORMAT = "[%(processName)s/%(levelname)s] %(message)s"




def method_logger(name:str):
    """Decorator for adding logging to a method.

    Args:
        name (str): The name of the module in which the method being decorated is located

    """
    logger = get_module_logger(name)
    classname = inspect.getouterframes(inspect.currentframe())[1][3]

    def real_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # hack, because log is applied to methods, we can get
            # object instance as first arguments in args
            logger.debug(f"calling {func.__name__} on {classname}")
            res = func(*args, **kwargs)
            logger.debug(f"completed calling {func.__name__} on {classname}")
            return res

        return wrapper

    return real_decorator

def function_logger(name):
    """Decorator for adding logging to a Function.

    Args:
        name (str): The name of the module in which the function being decorated is located

    """
    logger = get_module_logger(name)

    def real_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # hack, because log is applied to methods, we can get
            # object instance as first arguments in args
            logger.debug(f"calling {func.__name__}")
            res = func(*args, **kwargs)
            logger.debug(f"completed calling {func.__name__}")
            return res

        return wrapper

    return real_decorator


def get_rootlogger():
    """Returns root logger used by MESA.

    Returns:
        the root logger of MESA

    """
    global _rootlogger  # noqa: PLW0603

    if not _rootlogger:
        _rootlogger = logging.getLogger(LOGGER_NAME)
        _rootlogger.handlers = []
        _rootlogger.addHandler(logging.NullHandler())
        _rootlogger.setLevel(DEBUG)

    return _rootlogger


def log_to_stderr(level: int | None = None, pass_root_logger_level: bool = False):
    """Turn on logging and add a handler which prints to stderr.

    Args:
        level: minimum level of the messages that will be logged
        pass_root_logger_level: bool, optional. Default False
                if True, all module loggers will be set to the same logging level as the root logger.

    """
    if not level:
        level = DEFAULT_LEVEL

    logger = get_rootlogger()

    # avoid creation of multiple stream handlers for logging to console
    for entry in logger.handlers:
        if (isinstance(entry, logging.StreamHandler)) and (entry.formatter._fmt == LOG_FORMAT):
            return logger

    formatter = logging.Formatter(LOG_FORMAT)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    if pass_root_logger_level:
        for _, mod_logger in _module_loggers.items():
            mod_logger.setLevel(level)

    return logger