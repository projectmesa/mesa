import glob

import nbformat
import pytest
from nbconvert.preprocessors import ExecutePreprocessor

notebooks = glob.glob("docs/**/*.ipynb", recursive=True)


@pytest.mark.parametrize("notebook_path", notebooks)
def test_notebook_execution(notebook_path):
    # Load the notebook
    with open(notebook_path) as f:
        nb = nbformat.read(f, as_version=4)

    # Set up the notebook execution
    ep = ExecutePreprocessor(timeout=600, kernel_name="python3")

    try:
        # Execute the notebook and catch any errors
        ep.preprocess(nb, {"metadata": {"path": "./"}})
    except Exception as e:
        pytest.fail(f"Notebook {notebook_path} failed: {e!s}")
