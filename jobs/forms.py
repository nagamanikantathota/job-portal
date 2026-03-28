from django import forms
from django.contrib.auth.models import User
from .models import Profile, Job, Application, Category, Company

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    user_type = forms.ChoiceField(choices=Profile.USER_TYPES)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            Profile.objects.create(user=user, user_type=self.cleaned_data['user_type'])
        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['resume', 'bio', 'experience', 'skills', 'phone', 'location', 'preferred_category']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'logo', 'description', 'website', 'location']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'category', 'job_type', 'location', 'salary_min', 'salary_max', 'description', 'requirements', 'is_featured']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Describe the role and responsibilities...'}),
            'requirements': forms.Textarea(attrs={'rows': 4, 'placeholder': 'List the key requirements and qualifications...'}),
            'salary_min': forms.NumberInput(attrs={'placeholder': 'Min salary (e.g. 50000)'}),
            'salary_max': forms.NumberInput(attrs={'placeholder': 'Max salary (e.g. 80000)'}),
        }

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['resume', 'cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 4}),
        }

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=200)
    message = forms.CharField(widget=forms.Textarea)
