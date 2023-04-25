import contextlib
import importlib
import os
from pathlib import Path
import sys
import unittest


def classcase(name):
    return "".join(x.capitalize() for x in name.replace("-", "_").split("_"))


@unittest.skip(
    "Skipping TextExamples, because examples folder was moved. More discussion needed."
)
class TestExamples(unittest.TestCase):
    """
    Test examples' models.  This creates a model object and iterates it through
    some steps.  The idea is to get code coverage, rather than to test the
    details of each example's model.
    """

    EXAMPLES = (Path(__file__) / "../examples").resolve()

    @contextlib.contextmanager
    def active_example_dir(self, example):
        "save and restore sys.path and sys.modules"
        old_sys_path = sys.path[:]
        old_sys_modules = sys.modules.copy()
        old_cwd = Path.cwd()
        example_path = (Path(self.EXAMPLES) / example).resolve()
        try:
            sys.path.insert(0, str(example_path))
            os.chdir(example_path)
            yield
        finally:
            os.chdir(old_cwd)
            added = [m for m in sys.modules if m not in old_sys_modules]
            for mod in added:
                del sys.modules[mod]
            sys.modules.update(old_sys_modules)
            sys.path[:] = old_sys_path

    def test_examples(self):
        for example in os.listdir(self.EXAMPLES):
            if not (self.EXAMPLES / example).isdir():
                continue
            example_snaked = f"test_{example.replace('-', '_')}"
            if hasattr(self, example_snaked):
                # non-standard example; tested below
                continue

            print(f"testing example {example!r}")
            with self.active_example_dir(example):
                try:
                    # model.py at the top level
                    mod = importlib.import_module("model")
                    server = importlib.import_module("server")
                    server.server.render_model()
                except ImportError:
                    # <example>/model.py
                    mod = importlib.import_module(f"{example_snaked}.model")
                    server = importlib.import_module(f"{example_snaked}.server")
                    server.server.render_model()
                model_class = getattr(mod, classcase(example))
                model = model_class()
                for _ in range(10):
                    model.step()
