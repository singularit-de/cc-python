import sys
from pathlib import Path

project_slug = "{{ cookiecutter.project_slug }}"
project_path = Path(project_slug)
use_drf = "{{ cookiecutter.use_drf }}" == "y"

def _remove_file(file_path: Path) -> None:
    """Remove a file if it exists."""
    file_path.unlink(missing_ok=True)


def handle_drf():
    if use_drf:
        return

    _remove_file(project_path / "drf_exception_handler.py")

def main():
    handle_drf()


if __name__ == "__main__":
    sys.exit(main())