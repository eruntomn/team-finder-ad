from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Project, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'email',
        'name',
        'surname',
        'phone',
        'is_staff',
        'is_active',
    )
    ordering = ('email',)
    search_fields = ('email', 'name', 'surname', 'phone')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            'Личная информация',
            {
                'fields': (
                    'name',
                    'surname',
                    'avatar',
                    'phone',
                    'github_url',
                    'about',
                )
            },
        ),
        (
            'Права',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email',
                    'name',
                    'surname',
                    'phone',
                    'password1',
                    'password2',
                    'is_staff',
                    'is_active',
                ),
            },
        ),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'description', 'owner__email')
    filter_horizontal = ('participants', 'interested_users')
