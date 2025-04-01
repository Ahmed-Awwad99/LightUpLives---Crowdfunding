from django import forms
from .models import Profile, Users

class UserEditForm(forms.ModelForm):
    class Meta:
        model = Users  # Updated to use the custom Users model
        fields = {'first_name', 'last_name',  'phone_number', 'profile_picture'}


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = {'birthdate', 'facebook_profile', 'country'}
        widgets = {
            'birthdate': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),  # Add a date picker widget
            'country': forms.Select(attrs={'class': 'form-control'}),  # Add a widget for better styling
        }


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=254, label='Email')  # Use email instead of username
    password = forms.CharField(widget=forms.PasswordInput, label='Password')


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    class Meta:
        model = Users  # Updated to use the custom Users model
        fields = {'email', 'first_name', 'last_name', 'phone_number', 'profile_picture'}  # Removed 'username'

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2

