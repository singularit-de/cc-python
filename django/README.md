# Cookiecutter Django

## Features

- Django 6
- Python 3.14, 3.13, 3.12
- PostgreSQL 18, 17, 16
- Package and Project management with uv
- Pre-commit hooks for code quality and formatting
    - ruff
- Optional DRF (Django Rest Framework) setup
- GitLab CI/CD
    - pre-commit checks
    - django tests
    - deployment checks
    - automated deployment to our staging environment
- Dependency Tracking
- Custom `User` model
- ``common`` directory with utility functions and classes

## `cookiecutter.json` questions

1. `project_name` - Human-readable project name
    - Used in the README and API documentation.

2. `project_slug` - Project identifier / Python package name (slugified)
    - Used throughout the codebase, e.g. in `import` statements, as the Django project/module name, and in the GitLab
      CI/CD configuration.
    - Use a valid Python module name (typically lowercase letters, numbers, and underscores; must not start with a
      number).

3. `customer` - Customer/client name (optional)
    - Used in the README.

4. `python_version` - Python version for the project
    - Prefer the latest stable Python version that is supported by Django and your dependencies.

5. `postgresql_version` - PostgreSQL version for the project
    - Prefer the latest stable PostgreSQL version.

6. `username_type` - Identifier used to log in (for the Django user model)
    - Commonly set to `email` for customer projects. (This affects the custom user model and should be chosen early.)

7. `use_drf` - Include Django REST Framework (DRF)
    - If set to `yes`, DRF, drf-spectacular, django-filter, and django-cors-headers will be installed and preconfigured.

## ``common`` directory

The ``common`` directory contains basic utility functions for models, Django management commands, tests. If DRF is
enabled, it also contains filters, a BinaryRenderer and a MultipleSerializersMixin for ViewSets.