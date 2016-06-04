import unittest
import os
from click.testing import CliRunner

from mesa.scripts.mesa_init import main as mesa_init


class ScaffoldTest(unittest.TestCase):
    """
    Test mesa project scaffolding command
    """

    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()

    def test_scaffold_creates_project_dir(self):
        with self.runner.isolated_filesystem():
            assert not os.path.isdir("ExampleProject")
            self.runner.invoke(mesa_init, ['--no-input'])
            assert os.path.isdir("ExampleProject")
        self.runner.invoke(mesa_init, ['True'])
