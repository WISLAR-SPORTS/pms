from django import forms
from django.contrib.auth.forms import UserCreationForm
from Auth.models import CustomUser
from branchDepart.models import Department, Branch, Program
from django import forms
from django.contrib.auth.forms import UserCreationForm
from Auth.models import CustomUser
from branchDepart.models import Department, Branch
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import bleach
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
import bleach

from .models import CustomUser



class StudentRegistrationForm(UserCreationForm):
    branch = forms.ModelChoiceField(queryset=Branch.objects.all())
    department = forms.ModelChoiceField(queryset=Department.objects.none())

    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)

    class Meta:
        model = CustomUser
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'branch',
            'department',
            'password1',
            'password2'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['branch'].queryset = Branch.objects.all()
        self.fields['department'].queryset = Department.objects.none()

        if 'branch' in self.data:
            try:
                branch_id = int(self.data.get('branch'))
                self.fields['department'].queryset = Department.objects.filter(branch_id=branch_id)
            except (ValueError, TypeError):
                pass

    # 🔒 AUTO FORMAT + SECURITY: FIRST NAME
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')

        if first_name:
            # 🧼 remove scripts/HTML
            first_name = bleach.clean(strip_tags(first_name), tags=[], strip=True)

            # 🧹 normalize
            first_name = first_name.strip().lower().capitalize()

            # 🔐 strict safety check (letters only)
            if not first_name.replace(" ", "").isalpha():
                raise ValidationError("First name must contain only letters.")

        return first_name

    # 🔒 AUTO FORMAT + SECURITY: LAST NAME
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')

        if last_name:
            last_name = bleach.clean(strip_tags(last_name), tags=[], strip=True)

            last_name = last_name.strip()

            # supports multi-word names (e.g. "van dyke")
            last_name = " ".join(word.lower().capitalize() for word in last_name.split())

            # safety check
            if not last_name.replace(" ", "").isalpha():
                raise ValidationError("Last name must contain only letters.")

        return last_name

    # 🔐 EMAIL CLEANING (safe normalization)
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email:
            email = bleach.clean(strip_tags(email), tags=[], strip=True)
            email = email.strip().lower()  # important for consistency

        return email

    # 🔐 USERNAME HARDENING (recommended)
    def clean_username(self):
        username = self.cleaned_data.get('username')

        if username:
            username = bleach.clean(strip_tags(username), tags=[], strip=True)
            username = username.strip().lower()

            if len(username) < 3:
                raise ValidationError("Username must be at least 3 characters.")

        return username
# Auth/forms.py
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from Auth.models import CustomUser

class StudentPasswordChangeForm(PasswordChangeForm):
    # Optional: you can customize field labels here
    old_password = forms.CharField(label="Current Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(label="New Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(label="Confirm New Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
# Auth/forms.py
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import CustomUser
from django import forms
from django.utils.html import strip_tags
import bleach
from .models import CustomUser


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'department']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
        }

    # 🔤 AUTO FORMAT first name
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')

        if first_name:
            # 🧼 remove HTML/scripts
            first_name = bleach.clean(strip_tags(first_name), tags=[], strip=True)

            # 🧹 normalize spaces
            first_name = first_name.strip()

            # 🔠 auto-format (capitalize properly)
            first_name = first_name.lower().capitalize()

        return first_name

    # 🔤 AUTO FORMAT last name
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')

        if last_name:
            last_name = bleach.clean(strip_tags(last_name), tags=[], strip=True)

            last_name = last_name.strip()

            # supports multi-word last names (e.g. "van dyke")
            last_name = " ".join(word.capitalize() for word in last_name.split())

        return last_name

    # 🔒 email safety (unchanged logic, just cleaned)
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email:
            email = bleach.clean(strip_tags(email), tags=[], strip=True)

        return email
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.utils.html import strip_tags
import bleach


class EditProfileWithPasswordForm(EditProfileForm):
    old_password = forms.CharField(
        label="Current Password",
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password1 = forms.CharField(
        label="New Password",
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    def clean(self):
        cleaned_data = super().clean()

        old = cleaned_data.get('old_password')
        new1 = cleaned_data.get('new_password1')
        new2 = cleaned_data.get('new_password2')

        # 🔒 Sanitize inputs (prevent hidden injection / weird chars)
        if new1:
            new1 = bleach.clean(strip_tags(new1), tags=[], strip=True)
            cleaned_data['new_password1'] = new1

        if new2:
            new2 = bleach.clean(strip_tags(new2), tags=[], strip=True)
            cleaned_data['new_password2'] = new2

        # 🔐 Your original logic (kept intact)
        if old or new1 or new2:
            if not old or not new1 or not new2:
                self.add_error(None, "To change password, fill all password fields.")

        if new1 and new2 and new1 != new2:
            self.add_error('new_password2', "Passwords do not match.")

        # 🔥 Password strength validation (unchanged logic, hardened)
        if new1:
            try:
                validate_password(new1, self.instance)
            except ValidationError as e:
                for error in e.messages:
                    self.add_error('new_password1', error)

        return cleaned_data