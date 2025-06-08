from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "username", "role", "is_staff")
    readonly_fields = ("date_joined", "last_login")

    fieldsets = UserAdmin.fieldsets + (
        (None, {
            "fields": (
                "role",
                "birth_date",
                "gender",
                "bio",
                "profile_completed",
            )
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {
            "fields": (
                "role",
                "birth_date",
                "gender",
                "bio",
            )
        }),
    )



admin.site.register(CustomUser, CustomUserAdmin)
