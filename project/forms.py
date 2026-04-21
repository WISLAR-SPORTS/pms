from django import forms
from project.models import Project
from django import forms
from .models import Project
from branchDepart.models import Department, Program
from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
import bleach

from .models import Project, Department, Program


class ProjectSubmissionForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'branch', 'department', 'program']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Bootstrap classes
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

        # Initial empty dropdowns
        self.fields['department'].queryset = Department.objects.none()
        self.fields['program'].queryset = Program.objects.none()

        # Branch filter
        if 'branch' in self.data:
            try:
                branch_id = int(self.data.get('branch'))
                self.fields['department'].queryset = Department.objects.filter(branch_id=branch_id)
            except (ValueError, TypeError):
                pass

        # Department filter
        if 'department' in self.data:
            try:
                dept_id = int(self.data.get('department'))
                self.fields['program'].queryset = Program.objects.filter(department_id=dept_id)
            except (ValueError, TypeError):
                pass

    # 🔐 TITLE SECURITY + FORMAT
    def clean_title(self):
        title = self.cleaned_data.get('title')

        if title:
            # 🧼 remove scripts/HTML
            title = bleach.clean(strip_tags(title), tags=[], strip=True)

            # 🧹 normalize spacing
            title = title.strip()

            # 🔠 auto-format title case
            title = title.title()

            # 🚫 basic safety check
            if len(title) < 5:
                raise ValidationError("Title is too short.")

        return title

    # 🔐 DESCRIPTION SECURITY + SANITIZATION
    def clean_description(self):
        description = self.cleaned_data.get('description')

        if description:
            # 🧼 remove HTML/scripts completely
            description = bleach.clean(strip_tags(description), tags=[], strip=True)

            # 🧹 normalize whitespace
            description = " ".join(description.split())

            # 🚫 length validation
            if len(description) < 20:
                raise ValidationError("Description must be at least 20 characters.")

        return description