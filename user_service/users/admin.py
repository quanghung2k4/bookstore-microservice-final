from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.infrastructure.models import UserModel


@admin.register(UserModel)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("role", "phone", "is_verified")}),)
    list_display = ("id", "username", "email", "role", "is_staff", "is_active", "is_verified")
