"""Pytest configuration and shared fixtures for Mesa tests."""

import random

import pytest


@pytest.fixture
def rng():
    """Deterministic RNG for tests that require randomness."""
    return random.Random(42)
