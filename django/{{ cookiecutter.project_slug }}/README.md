# {{ cookiecutter.project_name }}

## Tech stack

- Python {{ cookiecutter.python_version }}
- uv
- PostgreSQL {{ cookiecutter.postgresql_version }}
- Django

## Get started after cookiecutter

1. Adjust the code as you need
2. Resolve the remaining TODOs in the code
3. Create a remote git repository
4. Initialize git in the project

   ```bash
   git init -b main
   ```
5. Enable pre-commit hooks:

   ```bash
   pre-commit install
   ```

6. Add and commit the initial code:

   ```bash
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push origin main
   ```

5. Go to the remote git repository and create a CI/CD variable (under Settings > CI/CD > Variables > Project variables):

    - `DJANGO_SECRET_KEY`
      - Visibility: `Masked`
      - Protect variable: `yes`
      - Expand variable reference: `no`
      - Key: `DJANGO_SECRET_KEY`
      - Value: generate it using `python -c "import secrets; print(secrets.token_urlsafe(50))"`
6. Delete this section and make a second commit

## Get started locally

1. Create a virtual environment using uv:

   ```bash
   uv venv
   source .venv/bin/activate
   uv sync
   ```

2. Create a database in your PostgreSQL instance
3. Create a `.env` file according to the `.env.example` file
4. Run the development server:

   ```bash
   python manage.py runserver
   # or
   uv run manage.py runserver
   ```
5. Install pre-commit hooks:

   ```bash
   pre-commit install
   ```
