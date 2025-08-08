from .base import *  # noqa

SECRET_KEY = env.str("DJANGO_SECRET_KEY")
DEBUG = False

FRONTEND_URL = "http://localhost:5173"  # TODO: Update this to your frontend URL in stagings

ALLOWED_HOSTS = [".v2.singular-it-test.de"]

CSRF_TRUSTED_ORIGINS = ["https://*.v2.singular-it-test.de"]

{% if cookiecutter.use_drf == "y" %}
# CORS
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.v2\.singular-it-test\.de$",
]
{% endif %}