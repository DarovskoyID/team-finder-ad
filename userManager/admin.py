from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from userManager.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    ordering = ('-date_joined',)
    list_display = ('email', 'name', 'surname', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'name', 'surname')
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Личные данные', {'fields': ('name', 'surname', 'avatar', 'about', 'phone', 'github')}),
        ('Права', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'surname', 'password1', 'password2'),
        }),
    )