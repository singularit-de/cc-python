from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _



class UserManager(BaseUserManager):
    def create_user(self, email, **extra_fields) -> "User":
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(extra_fields["password"])
        user.save()
        return user

    def create_superuser(self, email, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, **extra_fields)


class User(AbstractUser):
    {% if cookiecutter.username_type == "email" %}
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    username = None
    email = models.EmailField(
        _("email address"),
        unique=True,
    )
    {% else %}
    email = models.EmailField(
        _("email address"),
        unique=True,
    )
    {% endif %}

    objects = UserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
{% if cookiecutter.username_type == "email" %}
        ordering = ["email"]

    def __repr__(self):
        return f"User({self.email})"

    def __str__(self):
        return self.email
{% else %}

    def __repr__(self):
        return f"User({self.username})"


    def __str__(self):
        return self.username
{% endif %}
