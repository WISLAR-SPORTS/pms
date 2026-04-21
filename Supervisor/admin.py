from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import SupervisorProfile

@admin.register(SupervisorProfile)
class SupervisorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'office', 'phone')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')