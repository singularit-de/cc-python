from .base import *  # noqa

SECRET_KEY = env.str("DJANGO_SECRET_KEY")
DEBUG = False

FRONTEND_URL = "http://localhost:5173"  # TODO: Update this to your frontend URL in stagings

ALLOWED_HOSTS = [".v2.singular-it-test.de"]

CSRF_TRUSTED_ORIGINS = ["https://*.v2.singular-it-test.de"]
