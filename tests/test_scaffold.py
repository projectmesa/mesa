import os
from pathlib import Path
import unittest

from click.testing import CliRunner

from mesa.main import cli


class ScaffoldTest(unittest.TestCase):
    """
    Test mesa project scaffolding command
    """

    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()

    def test_scaffold_creates_project_dir(self):
        with self.runner.isolated_filesystem():
            assert not Path("example_project").is_dir()
            self.runner.invoke(cli, ["startproject", "--no-input"])
            assert Path("example_project").is_dir()
