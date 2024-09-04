import glob

import pytest

# Locate all notebooks in docs and subdirectories
notebooks = glob.glob("docs/**/*.ipynb", recursive=True)


# Parameterize the test with all found notebooks
@pytest.mark.parametrize("notebook", notebooks)
def test_notebook_execution(notebook):
    # This runs each notebook using nbval and ensures there are no errors
    pytest.main(
        [
            "--nbval",
            "--nbval-current-env",  # Use the current environment
            "--nbval-sanitize-with",
            ".sanitize_config.yaml",  # Optional: If you want to handle variable output, use this
            notebook,
        ]
    )
