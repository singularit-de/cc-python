# Third Party Packages
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext as _

from users.models import User

admin.site.site_url = settings.FRONTEND_URL

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {"fields": ("{{ cookiecutter.username_type }}", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    {% if cookiecutter.username_type == "username" %} "email" {% endif %}
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("{{ cookiecutter.username_type }}", "password1", "password2"),
            },
        ),
    )
    list_display = (
        "{{ cookiecutter.username_type }}",
        {% if cookiecutter.username_type == "username" %}"email", {% endif %}
        "first_name",
        "last_name",
        "is_staff",
        "is_superuser",
        "date_joined",
        "is_active",
        "last_login",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("first_name", "last_name", "{{ cookiecutter.username_type }}")
    ordering = ("{{ cookiecutter.username_type }}",)
