"""Unit tests for mesa_logging."""

import logging

import pytest

import ast

import os

from pathlib import Path

from mesa import mesa_logging


@pytest.fixture(autouse=True)
def tear_down():
    """Pytest fixture to ensure all logging state is reset after testing."""
    yield
    mesa_logging._logger = None
    mesa_logging._rootlogger = None
    mesa_logger = logging.getLogger(mesa_logging.LOGGER_NAME)
    mesa_logger.handlers = []
    mesa_logger.propagate = True


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


def test_log_to_stderr_propagation():
    """Test log_to_stderr with propagate parameter."""
    mesa_logging._rootlogger = None
    logger = mesa_logging.log_to_stderr(propagate=True)
    assert logger.propagate is True

    mesa_logging._rootlogger = None
    logger = mesa_logging.log_to_stderr(propagate=False)
    assert logger.propagate is False


def test_caplog_capture_after_teardown(caplog):
    """Verify that logger propagation allows caplog to capture records."""
    logger = mesa_logging.get_module_logger("test_propagation")
    logger.setLevel(logging.INFO)
    logger.info("testing caplog propagation")
    assert "testing caplog propagation" in caplog.text


def test_no_module_level_logging_in_examples():
    """
    Static AST scan to ensure no module-level logging configuration
    (like log_to_stderr or basicConfig) happens in the examples directory.
    """
    
    current_dir = Path(__file__).parent
    examples_dir = current_dir.parent / "mesa" / "examples"
    
    forbidden_calls = {"log_to_stderr", "log_to_file", "basicConfig"}
    
    for root, dirs, files in os.walk(examples_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        
                        tree = ast.parse(f.read(), filename=file_path)
                    except SyntaxError:
                        continue
                
                
                for node in tree.body:
                    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                        func = node.value.func
                        
                        
                        if isinstance(func, ast.Name) and func.id in forbidden_calls:
                            assert False, f"Forbidden module-level logging call '{func.id}' found in {file_path}"
                            
                        
                        elif isinstance(func, ast.Attribute) and func.attr in forbidden_calls:
                            assert False, f"Forbidden module-level logging call '{func.attr}' found in {file_path}"
