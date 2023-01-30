import contextlib
import importlib
import os.path
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

    EXAMPLES = os.path.abspath(os.path.join(os.path.dirname(__file__), "../examples"))

    @contextlib.contextmanager
    def active_example_dir(self, example):
        "save and restore sys.path and sys.modules"
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
            added = [m for m in sys.modules if m not in old_sys_modules]
            for mod in added:
                del sys.modules[mod]
            sys.modules.update(old_sys_modules)
            sys.path[:] = old_sys_path

    def test_examples(self):
        for example in os.listdir(self.EXAMPLES):
            if not os.path.isdir(os.path.join(self.EXAMPLES, example)):
                continue
            if hasattr(self, f"test_{example.replace('-', '_')}"):
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
                    mod = importlib.import_module(f"{example.replace('-', '_')}.model")
                    server = importlib.import_module(
                        f"{example.replace('-', '_')}.server"
                    )
                    server.server.render_model()
                model_class = getattr(mod, classcase(example))
                model = model_class()
                for _ in range(10):
                    model.step()
