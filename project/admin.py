from django.contrib import admin

from django.contrib import admin
from .models import Project
from django import forms
from branchDepart.models import Department

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'branch' in self.data:
            try:
                branch_id = int(self.data.get('branch'))
                self.fields['department'].queryset = Department.objects.filter(branch_id=branch_id)
            except (ValueError, TypeError):
                pass  # fallback to all departments
        else:
            self.fields['department'].queryset = Department.objects.all()
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'get_students',
        'status',
        'program',
        'department',
        'branch',
        'start_date',
        'end_date'
    )

    list_filter = ('branch', 'students')
    search_fields = ('title', 'description')
    filter_horizontal = ('supervisors', 'students')  # optional improvement

    def get_students(self, obj):
        return ", ".join(str(s) for s in obj.students.all())

    get_students.short_description = "Students"