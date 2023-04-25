from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from click.testing import CliRunner

from mesa.main import cli


class TestCli(unittest.TestCase):
    """
    Test CLI commands
    """

    def setUp(self):
        self.old_sys_path = sys.path[:]
        self.runner = CliRunner()

    def tearDown(self):
        sys.path[:] = self.old_sys_path

    @unittest.skip(
        "Skipping test_run, because examples folder was moved. More discussion needed."
    )
    def test_run(self):
        with patch("mesa.visualization.ModularServer") as ModularServer:  # noqa: N806
            example_dir = (Path(__file__).parent / "../examples/wolf_sheep").resolve()
            with self.runner.isolated_filesystem():
                result = self.runner.invoke(cli, ["runserver", str(example_dir)])
                assert result.exit_code == 0, result.output
                assert ModularServer().launch.call_count == 1
