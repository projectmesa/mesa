"""Unit tests for mesa_logging."""
import pytest

import logging

import unittest

from mesa import mesa_logging


@pytest.fixture
def tear_down():
    """Pytest fixture to ensure all logging is disabled after testing."""
    yield None
    mesa_logging._logger = None
    ema_logger = logging.getLogger(mesa_logging.LOGGER_NAME)
    ema_logger.handlers = []


def test_get_logger():
    """Test get_logger."""
    mesa_logging._rootlogger = None
    logger = mesa_logging.get_rootlogger()
    assert logger == logging.getLogger(mesa_logging.LOGGER_NAME)
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.NullHandler)

    logger = mesa_logging.get_rootlogger()
    assert logger, logging.getLogger(mesa_logging.LOGGER_NAME)
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.NullHandler)


def test_log_to_stderr():
    """Test log_to_stderr."""
    mesa_logging._rootlogger = None
    logger = mesa_logging.log_to_stderr(mesa_logging.DEBUG)
    assert len(logger.handlers) == 2
    assert logger.level == mesa_logging.DEBUG

    mesa_logging._rootlogger = None
    logger = mesa_logging.log_to_stderr()
    assert len(logger.handlers) == 2
    assert logger.level == mesa_logging.DEFAULT_LEVEL

    logger = mesa_logging.log_to_stderr()
    assert len(logger.handlers) == 2
    assert logger.level == mesa_logging.DEFAULT_LEVEL



