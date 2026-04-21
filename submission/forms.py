from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
import bleach

from .models import Submission


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['project', 'title', 'file']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  # current student
        super().__init__(*args, **kwargs)

        # 🔐 Only show student's projects (your logic kept)
        self.fields['project'].queryset = user.projects.all()

        # 🎨 Optional: Bootstrap styling (safe UX improvement)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    # 🔐 CLEAN TITLE (remove scripts + format)


def clean_title(self):
    title = self.cleaned_data.get('title')

    if title:
        # 🧼 remove HTML/scripts once
        title = strip_tags(title)

        # 🧹 normalize spacing
        title = title.strip()

        # 🔠 auto format
        title = title.title()

        # 🚫 validation
        if len(title) < 3:
            raise ValidationError("Title is too short.")

    return title
    # 🔐 FILE SECURITY CHECK
    def clean_file(self):
        file = self.cleaned_data.get('file')

        if file:
            # 🚫 limit file size (5MB example)
            if file.size > 5 * 1024 * 1024:
                raise ValidationError("File size must be under 5MB.")

            # 🚫 block dangerous extensions
            allowed_extensions = ['pdf', 'doc', 'docx', 'zip']
            ext = file.name.split('.')[-1].lower()

            if ext not in allowed_extensions:
                raise ValidationError("Invalid file type.")

            # 🧼 clean filename (remove scripts or weird chars)
            file.name = bleach.clean(strip_tags(file.name), tags=[], strip=True)

        return file