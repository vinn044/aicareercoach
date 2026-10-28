from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Resume, User

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Unable to use this email. Try signing in or use another address.')
        return email

class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        # Never accept owner, machine-generated output, or permissions from a browser.
        fields = ['title', 'text', 'major', 'minor']
        widgets = {'text': forms.Textarea(attrs={'rows': 14})}
        help_texts = {'text': 'Paste your resume text. PDF upload is not connected yet.',
                      'minor': 'Optional. Confirm this from your resume or academic record.'}
