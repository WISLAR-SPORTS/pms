from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email','first_name', 'last_name',  'role', 'get_branch', 'department', 'is_active')
    def get_branch(self, obj):
        # Safely handle missing department or branch
        if obj.department and obj.department.branch:
            return obj.department.branch.name
        return "N/A"
    get_branch.short_description = 'Branch'
    list_filter = ('role', 'department', 'is_active')
    search_fields = ('username', 'email', 'enrollment_number')
    fieldsets = (
    (None, {'fields': ('username', 'password')}),

    ('Personal info', {
        'fields': ('first_name', 'last_name', 'email')
    }),

    ('Permissions', {
        'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
    }),

    ('Important dates', {
        'fields': ('last_login', 'date_joined')
    }),

    # ✅ YOUR CUSTOM FIELDS (now guaranteed to show)
    ('Additional Info', {
        'fields': ('role', 'department', 'enrollment_number'),
    }),
)