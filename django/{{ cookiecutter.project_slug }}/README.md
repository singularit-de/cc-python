# {{ cookiecutter.project_name }} ({{ cookiecutter.customer }})


## Tech stack

- Python {{ cookiecutter.python_version }}
- uv
- PostgreSQL {{ cookiecutter.postgresql_version }}
- Django


**------------------- BEGIN DELETE SECTION --------------------**

## Get started after cookiecutter

1. Create a new remote git repository [here](https://singular-code.de/projects/new)
   1. Create the following CI/CD variables (under `Settings` > `CI/CD` > `Variables` > `Project variables` > `Add variable`):
       - `DJANGO_SECRET_KEY`
         - Type: `Variable (default)` 
         - Environments: `All (default)`
         - Visibility: `Masked`
         - Flags - Protect variable: `yes`
         - Flags - Expand variable reference: `no`
         - Key: `DJANGO_SECRET_KEY`
         - Value:
         ```shell
         python -c "import secrets; print(secrets.token_urlsafe(50))"
         ```
2. Initialize git in the project

   ```bash
   git init --initial-branch=main
   ```

3. Create a venv and install dependencies:

   ```bash
   uv venv --allow-existing
   # Windows
   .venv\Scripts\activate
   # Linux: source .venv/bin/activate
   uv sync
   ```
   
4. Enable pre-commit hooks:

   ```bash
   pre-commit install
   ```

5. **Delete this section, because its only for the initial setup**

6. Create an initial commit and push to the remote repository:

   ```bash
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push --set-upstream origin main
   ```

**------------------- END DELETE SECTION --------------------**

## Get started locally

1. Create a virtual environment using uv:

   ```bash
   uv venv --allow-existing
   # Windows
   .venv\Scripts\activate
   # Linux: source .venv/bin/activate
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
