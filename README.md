# Cookiecutter templates for python projects at singularIT

## Prerequisites

- [cookiecutter](https://cookiecutter.readthedocs.io/en/latest/installation.html) installed

## Django template

1. Go into the top-level directory where you want to create the project directory:

    ```
    cd /path/to/your/top-level-directory
    ```

2. Run the following command to create a new Django project using the newest template version:
    ```shell
    cookiecutter https://github.com/singularit-de/cc-python.git --directory django
    ```

   1. If you want to use a specific version/branch you can use the `--checkout <tag/branch>` option:
   ```shell
   cookiecutter https://github.com/singularit-de/cc-python.git --directory django --checkout v1.1.0
   ```

## Why we are using templates

## Contribute to this repository

### Tech stack of this repository

- Python 3.12
- uv
- ruff
- pre-commit
