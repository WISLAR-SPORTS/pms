from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Department, Branch, Program

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    #list_filter = ('department',)
from django.contrib import admin
from .models import Program, Department

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'department', 'duration_years')
    list_filter = ('department__branch', 'department')
    search_fields = ('name', 'code', 'department__name', 'department__branch__name')
    # raw_id_fields = ('department',)  # optional; comment out if you want a dropdown