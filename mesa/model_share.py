"""This module contains functions to generate a shareable py.cafe link containing Python code and dependencies."""

import base64
import gzip
import json
import os
from pathlib import Path
from urllib.parse import quote


def get_pycafe_link(
    files: dict[str, str] | None = None,
    requirements: str | None = None,
    autodetect_files: bool = False,
) -> str:
    r"""Generate a shareable py.cafe link containing Python code and dependencies.

    Args:
        files(dict[str, str] | None): Map of file names to paths, if files are not in the current directory.

        requirements(str | None): Package dependencies, one per line other than the essential ones.

        autodetect_files(bool): If True, scans directory for Python files instead of using `files`. Mutually exclusive with `files`.

    Example:
            >>> files = {
            >>>     "model.py": "wolf_sheep\\model.py",
            >>>     "agents.py": "wolf_sheep\\agents.py",
            >>>     "app.py": "wolf_sheep\\app.py"
            >>> }
            >>> get_pycafe_link(files=files)

    Returns:
        str: URL with encoded application code and dependencies.

    """
    requirements = (
        requirements or "mesa\nmatplotlib\nnumpy\nnetworkx\nsolara\naltair\npandas"
    )

    app = ""
    file_list = []

    if autodetect_files:
        all_files = _scan_python_files()
        for file in all_files:
            with open(file) as f:
                if file.endswith("app.py"):
                    app += f.read()
                else:
                    file_dict = {}
                    file_dict["name"] = os.path.basename(file)
                    file_dict["content"] = f.read()
                    file_list.append(file_dict)
    else:
        for file in files:
            with open(files[file]) as f:
                file_content = f.read()
                if file == "app.py":
                    app += file_content
                else:
                    file_dict = {"name": file, "content": file_content}
                    file_list.append(file_dict)

    json_object = {"code": app, "requirements": requirements, "files": file_list}
    json_text = json.dumps(json_object)
    # Compress using gzip to make the url shorter
    compressed_json_text = gzip.compress(json_text.encode("utf8"))
    # Encode in base64
    base64_text = base64.b64encode(compressed_json_text).decode("utf8")
    c = quote(base64_text)
    url = f"https://py.cafe/snippet/solara/v1#c={c}"

    return url


def _scan_python_files(directory_path: str = ".") -> list[str]:
    """Scan a directory for specific Python files (model.py, app.py, agents.py)."""
    path = Path(directory_path)
    python_files = [
        str(file)
        for file in path.glob("*.py")
        if file.name in ["model.py", "app.py", "agents.py"]
    ]

    return python_files
