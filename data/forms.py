import re
from django import forms
from .models import Course, Account
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'description', 'crn', 'credits', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
        error_messages = {
            'name': {
                'required': 'Course name is required.',
                'max_length': 'Course name cannot exceed 100 characters.',
            },
            'credits': {
                'required': 'Credits are required.',
                'invalid': 'Enter a valid number for credits.',
            },
            'start_date': {
                'required': 'Start date is required.',
                'invalid': 'Enter a valid date for start date.',
            },
            'crn': {
                'required': 'CRN is required.',
                'max_length': 'CRN cannot exceed 10 characters.',
            },
        }

    def clean_crn(self):
        crn = self.cleaned_data.get('crn', '')
        if len(crn) != 5:
            raise forms.ValidationError('CRN must be exactly 5 characters.')
        if not crn.isalnum():
            raise forms.ValidationError('CRN must contain only letters and numbers.')
        if not any(c.isalpha() for c in crn):
            raise forms.ValidationError('CRN must contain at least one letter.')
        if not any(c.isdigit() for c in crn):
            raise forms.ValidationError('CRN must contain at least one number.')
        return crn.upper()

    def clean_start_date(self):
        from datetime import date
        start_date = self.cleaned_data.get('start_date')
        if start_date and start_date <= date.today():
            raise forms.ValidationError('Start date must be after today.')
        return start_date

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and end_date <= start_date:
            raise forms.ValidationError('End date must be after the start date.')
        return cleaned_data

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label='Username', max_length=150)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

