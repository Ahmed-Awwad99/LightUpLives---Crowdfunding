from django import forms
from .models import Profile, Users
from django.core.validators import MinLengthValidator, RegexValidator, URLValidator
from django.utils.translation import gettext_lazy as _
import re

class UserEditForm(forms.ModelForm):
    first_name = forms.CharField(
        validators=[MinLengthValidator(5, 'First name must be at least 5 characters')],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name', 'required': True, 'minlength': '5'})
    )
    last_name = forms.CharField(
        validators=[MinLengthValidator(5, 'Last name must be at least 5 characters')],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name', 'required': True, 'minlength': '5'})
    )
    
    # Enhanced phone number validation
    phone_number = forms.CharField(
        required=False,
        validators=[
            RegexValidator(
                regex=r'^01[0-2,5]{1}[0-9]{8}$',
                message='Phone number must be a valid Egyptian number starting with 010, 011, 012, or 015'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': '01XXXXXXXXX',
            'pattern': '01[0-2,5][0-9]{8}',
            'title': 'Enter a valid Egyptian mobile number'
        })
    )
    
    # Profile picture validation
    profile_picture = forms.ImageField(
        required=False,
        validators=[
            RegexValidator(
                regex=r'\.(jpg|jpeg|png|gif)$',
                message='Only image files (jpg, jpeg, png, gif) are allowed',
                flags=re.IGNORECASE
            )
        ],
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/jpeg,image/png,image/gif'
        })
    )
    
    class Meta:
        model = Users
        fields = {'first_name', 'last_name', 'phone_number', 'profile_picture'}
    
    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            # Check file size (max 5MB)
            if profile_picture.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file too large ( > 5MB )")
            
            # Check file extension
            file_name = profile_picture.name.lower()
            if not (file_name.endswith('.jpg') or file_name.endswith('.jpeg') 
                    or file_name.endswith('.png') or file_name.endswith('.gif')):
                raise forms.ValidationError("Only .jpg, .jpeg, .png, and .gif files are allowed")
        return profile_picture

class ProfileEditForm(forms.ModelForm):
    # Add Facebook URL validation
    facebook_profile = forms.URLField(
        required=False,
        validators=[
            URLValidator(message="Please enter a valid URL"),
            RegexValidator(
                regex=r'(facebook\.com|fb\.com)',
                message="Please enter a valid Facebook URL",
                flags=re.IGNORECASE
            )
        ],
        widget=forms.URLInput(attrs={
            'class': 'form-control', 
            'placeholder': 'https://facebook.com/your.profile'
        })
    )
    
    # Add birthdate validation
    birthdate = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date', 
            'class': 'form-control',
            'max': '2010-01-01'  # Only allow birthdates before 2010 (adjust as needed)
        })
    )
    
    class Meta:
        model = Profile
        fields = {'birthdate', 'facebook_profile', 'country'}
        widgets = {
            'country': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean_birthdate(self):
        birthdate = self.cleaned_data.get('birthdate')
        if birthdate:
            # Import inside method to avoid circular imports
            from django.utils import timezone
            import datetime
            
            # Ensure the birthdate is not in the future
            if birthdate > timezone.now().date():
                raise forms.ValidationError("Birthdate cannot be in the future")
            
            # Ensure person is at least 13 years old (common minimum age requirement)
            min_age = 13
            age_threshold = timezone.now().date() - datetime.timedelta(days=min_age*365)
            if birthdate > age_threshold:
                raise forms.ValidationError(f"You must be at least {min_age} years old")
            
            # Ensure the birthdate is reasonable (e.g., not more than 120 years ago)
            max_age = 120
            max_age_threshold = timezone.now().date() - datetime.timedelta(days=max_age*365)
            if birthdate < max_age_threshold:
                raise forms.ValidationError("Please enter a valid birthdate")
        
        return birthdate


class LoginForm(forms.Form):
    email = forms.EmailField(
        max_length=254, 
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'required': True,
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'required': True
        })
    )


class UserRegistrationForm(forms.ModelForm):
    # Enhanced password validation
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'required': True
        }),
        validators=[
            RegexValidator(
                regex=r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$',
                message="Password must be at least 8 characters and include letters, numbers, and special characters"
            )
        ]
    )
    
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'required': True
        })
    )

    class Meta:
        model = Users
        fields = {'email', 'first_name', 'last_name', 'phone_number', 'profile_picture'}
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email',
                'required': True
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your first name',
                'required': True,
                'minlength': '5'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your last name',
                'required': True,
                'minlength': '5'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '01XXXXXXXXX',
                'pattern': '01[0-2,5][0-9]{8}',
                'title': 'Enter a valid Egyptian mobile number'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png,image/gif'
            })
        }

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Users.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already in use")
        return email