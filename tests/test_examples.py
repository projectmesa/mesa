# -*- coding: utf-8 -*-
import sys
import os.path
import unittest
import contextlib
import importlib


def classcase(name):
    return ''.join(x.capitalize() for x in name.replace('-', '_').split('_'))


class TestExamples(unittest.TestCase):
    '''
    Test examples' models.  This creates a model object and iterates it through
    some steps.  The idea is to get code coverage, rather than to test the
    details of each example's model.
    '''

    EXAMPLES = os.path.abspath(os.path.join(os.path.dirname(__file__), '../examples'))

    @contextlib.contextmanager
    def active_example_dir(self, example):
        'save and restore sys.path and sys.modules'
        old_sys_path = sys.path[:]
        old_sys_modules = sys.modules.copy()
        old_cwd = os.getcwd()
        example_path = os.path.abspath(os.path.join(self.EXAMPLES, example))
        try:
            sys.path.insert(0, example_path)
            os.chdir(example_path)
            yield
        finally:
            os.chdir(old_cwd)
            added = [m for m in sys.modules.keys() if m not in old_sys_modules]
            for mod in added:
                del sys.modules[mod]
            sys.modules.update(old_sys_modules)
            sys.path[:] = old_sys_path

    def test_examples(self):
        for example in os.listdir(self.EXAMPLES):
            if not os.path.isdir(os.path.join(self.EXAMPLES, example)):
                continue
            if hasattr(self, 'test_{}'.format(example.replace('-', '_'))):
                # non-standard example; tested below
                continue

            print("testing example {!r}".format(example))
            with self.active_example_dir(example):
                try:
                    # model.py at the top level
                    mod = importlib.import_module('model'.format(example))
                except ImportError:
                    # <example>/model.py
                    mod = importlib.import_module('{}.model'.format(example.replace('-', '_')))
                Model = getattr(mod, classcase(example))
                model = Model()
                (model.step() for _ in range(100))

    def test_hex_snowflake(self):
        with self.active_example_dir('hex_snowflake'):
            from hex_snowflake.model import HexSnowflake
            model = HexSnowflake(100, 100)
            (model.step() for _ in range(100))

    def test_pd_grid(self):
        with self.active_example_dir('pd_grid'):
            from pd_grid.model import PDModel
            model = PDModel(100, 100, "Random")
            (model.step() for _ in range(100))

    def test_shape_example(self):
        with self.active_example_dir('shape_example'):
            from shape_model.model import ShapesModel
            model = ShapesModel(100, 100, 100)
            (model.step() for _ in range(100))

    def test_sugarscape_cg(self):
        with self.active_example_dir('sugarscape_cg'):
            from sugarscape.model import Sugarscape2ConstantGrowback
            model = Sugarscape2ConstantGrowback()
            (model.step() for _ in range(100))

    def test_virus_on_network(self):
        with self.active_example_dir('virus_on_network'):
            from virus_on_network.model import VirusModel
            model = VirusModel(
                num_nodes=10,
                avg_node_degree=3,
                initial_outbreak_size=1,
                virus_spread_chance=0.4,
                virus_check_frequency=0.4,
                recovery_chance=0.3,
                gain_resistance_chance=0.5)
            (model.step() for _ in range(100))

    def test_wolf_sheep(self):
        with self.active_example_dir('wolf_sheep'):
            from wolf_sheep.model import WolfSheepPredation
            model = WolfSheepPredation()
            (model.step() for _ in range(100))
