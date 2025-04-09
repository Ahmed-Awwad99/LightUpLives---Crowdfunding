from django.db import models
from django.core.validators import RegexValidator 
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
import re
from django_countries.fields import CountryField  # Add this import for the country field



# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class Users(AbstractUser):
    token_created_at = models.DateTimeField(null=True, blank=True)
    email_confirmed = models.BooleanField(default=False)  # Add a field to track email confirmation status
    username = None  # Remove the username field
    email = models.EmailField(unique=True)  # Make email unique and required
    phone_number = models.CharField(
        max_length=15, unique=True, validators=[
            RegexValidator(
                regex=r'^01[0-2,5]{1}[0-9]{8}$',
                message='Phone number must be a valid Egyptian number starting with 010, 011, 012, or 015'
            )
        ],
        db_column="phone_number"
    )
    profile_picture = models.ImageField(
        upload_to='users/profile_images/',
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'\.(jpg|jpeg|png|gif)$',
                message='Only image files (jpg, jpeg, png, gif) are allowed',
                flags=re.IGNORECASE
            )
        ],
        db_column="profile_picture"
    )

    USERNAME_FIELD = 'email'  # Use email as the username field
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']  # Fields required when creating a superuser

    objects = CustomUserManager()  # Use the custom user manager


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    birthdate = models.DateField(blank=True, null=True)
    facebook_profile = models.URLField(max_length=255, blank=True, null=True)
    country = CountryField(blank_label='(select country)', blank=True, null=True)  # Updated to include a blank label

    def __str__(self):
        return self.user.email

