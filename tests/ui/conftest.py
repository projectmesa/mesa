"""Configuration for UI browser-based tests."""

import os

import pytest


@pytest.fixture
def solara_snapshots_directory():
    """Set the directory for storing and comparing snapshots."""
    return os.path.join(os.path.dirname(__file__), "snapshots")
