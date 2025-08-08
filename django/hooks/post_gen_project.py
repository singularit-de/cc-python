import sys
from pathlib import Path

project_slug = "{{ cookiecutter.project_slug }}"
project_path = Path(project_slug)
common_path = Path("common")
use_drf = "{{ cookiecutter.use_drf }}" == "y"

def _remove_file(file_path: Path):
    """Remove a file if it exists."""
    file_path.unlink(missing_ok=True)

def _remove_dir(dir_path: Path):
    """Remove a directory if it exists."""
    if dir_path.is_dir():
        for item in dir_path.iterdir():
            if item.is_file():
                item.unlink(missing_ok=True)
            elif item.is_dir():
                _remove_dir(item)
        dir_path.rmdir()

def handle_drf():
    if use_drf:
        return

    _remove_file(project_path / "drf_exception_handler.py")
    _remove_dir(common_path / "drf")

def main():
    handle_drf()


if __name__ == "__main__":
    sys.exit(main())