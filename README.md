# Cookiecutter templates for python projects at singularIT

## Prerequisites

- [cookiecutter](https://cookiecutter.readthedocs.io/en/latest/installation.html) or [uv](https://docs.astral.sh/uv/getting-started/installation/) installed

## Django template

1. Go into the top-level directory where you want to create the project directory:

    ```
    cd /path/to/your/top-level-directory
    ```

2. Run the following command to create a new Django project using the newest template version:
    ```shell
    cookiecutter https://github.com/singularit-de/cc-python.git --directory django
    # or
    uvx cookiecutter https://github.com/singularit-de/cc-python.git --directory django
    ```

   1. If you want to use a specific version/branch you can use the `--checkout <tag/branch>` option:
   ```shell
   cookiecutter https://github.com/singularit-de/cc-python.git --directory django --checkout v1.1.0
   ```

## Why we are using templates

Cookiecutter templates ensure consistency, standardization, and best practices across all Python projects at singularIT. They:

- **Reduce setup time** by automating project initialization and boilerplate configuration
- **Enforce conventions** with a standardized directory structure, naming patterns, and tooling (ruff, pre-commit, etc.)
- **Ensure quality** by baking in linting, formatting, and testing configurations from the start
- **Simplify maintenance** by allowing template updates to benefit all projects using them
- **Enable team alignment** on development practices and technology choices

## Testing template updates locally

If you contribute to the template you mostly want to test your changes locally before pushing them to the remote repository to see that everything works as expected.


1. Go into the top-level directory where your "cc-python" repository lives:

    ```shell
    cd /path/to/the/cc-python/top-level-directory
    ```

2. Run the following command to create a new Django project using the local template version:

    ```shell
    cookiecutter cc-python --directory django
    # or
    uvx cookiecutter cc-python --directory django
    ```

### Tech stack of this repository

- Python 3.12
- uv
- ruff
- pre-commit
