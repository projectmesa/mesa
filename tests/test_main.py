import os
import sys
import unittest
from unittest.mock import patch
from click.testing import CliRunner
import pytest
import tempfile
import contextlib

from mesa.main import cli, runserver


class TestCli(unittest.TestCase):
    '''
    Test CLI commands
    '''

    def setUp(self):
        self.old_sys_path = sys.path[:]
        self.runner = CliRunner()

    def tearDown(self):
        sys.path[:] = self.old_sys_path

    @pytest.mark.skip(reason="based on examples now in external repository")
    def test_run(self):
        # TODO transform in integration testing in external repository with examples.
        with patch('mesa.visualization.ModularVisualization.ModularServer') as ModularServer:
            example_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../examples/wolf_sheep'))
            with self.runner.isolated_filesystem():
                result = self.runner.invoke(cli, ['runserver', example_dir])
                assert result.exit_code == 0, result.output
                assert ModularServer().launch.call_count == 1

    def test_run_no_server_target(self):
        with patch('mesa.visualization.ModularVisualization.ModularServer') as ModularServer:
            with self.runner.isolated_filesystem():
                result = self.runner.invoke(cli, ['runserver', ''])
                assert result.exit_code == 2, result.output
                assert ModularServer().launch.call_count == 0

    @staticmethod
    @contextlib.contextmanager
    def mock_file_opener(file_path, content=''):
        with open(file_path, 'w') as f:
            f.write(content)
        yield file_path
        try:
            os.remove(file_path)
        except Exception:
            pass

    def test_runserver_mocked_file(self):
        mock_dir = tempfile.gettempdir()
        mock_file = os.path.join(mock_dir, "run.py")
        with self.mock_file_opener(mock_file):
            result = self.runner.invoke(cli, ['runserver', mock_dir])
            assert result.exit_code == 0, result.output
            self.assertEqual(sys.path[0], os.getcwd())

    def test_runserver_non_existing_run_file(self):
        mock_project_dir = tempfile.gettempdir()
        # TODO in run server raise a more specific error when run.py is not found.
        result = self.runner.invoke(cli, ['runserver', mock_project_dir])
        assert result.exit_code == 1, result.output


if __name__ == '__main__':
    unittest.main()
    tbc = TestCli()