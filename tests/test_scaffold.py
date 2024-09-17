# noqa: D100
import os
import unittest

from click.testing import CliRunner

from mesa.main import cli


class ScaffoldTest(unittest.TestCase):
    """Test mesa project scaffolding command."""

    @classmethod
    def setUpClass(cls):  # noqa: D102
        cls.runner = CliRunner()

    def test_scaffold_creates_project_dir(self):  # noqa: D102
        with self.runner.isolated_filesystem():
            assert not os.path.isdir("example_project")
            self.runner.invoke(cli, ["startproject", "--no-input"])
            assert os.path.isdir("example_project")
