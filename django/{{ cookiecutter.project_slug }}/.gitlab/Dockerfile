FROM python:{{ cookiecutter.python_version }}-slim-bookworm as base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD pyproject.toml uv.lock /app/

WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive

RUN uv sync

COPY . .

FROM base as app

RUN uv run manage.py collectstatic --no-input
