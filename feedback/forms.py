# supervisor/forms.py
from django import forms
from feedback.models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter feedback here...'})
        }
from django import forms
from .models import TestFeedback

from django import forms
from .models import TestFeedback
import re
import bleach

class TestFeedbackForm(forms.ModelForm):
    class Meta:
        model = TestFeedback
        fields = ['email', 'message', 'screenshot']

    def clean_message(self):
        message = self.cleaned_data.get('message')

        if not message:
            raise forms.ValidationError("Message is required.")
        
        # 🧼 Remove any HTML / scripts safely
        message = bleach.clean(message, tags=[], strip=True)

        # 🧼 Reject scripts / HTML completely
        if "<" in message or ">" in message:
            raise forms.ValidationError("HTML or scripts are not allowed.")

        # 🔤 Only letters, spaces, and dots allowed
        if not re.match(r'^[A-Za-z\s.,!?]+$', message):
            raise forms.ValidationError(
                "Only letters, spaces, and full stops (.) are allowed."
            )

        return message