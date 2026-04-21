from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action')
    list_filter = ('user',)
    search_fields = ('action', 'user__username')
    readonly_fields = ('timestamp', 'user', 'action')