from django.db import models
from django.core.validators import RegexValidator 
from django.conf import settings
from django.contrib.auth.models import AbstractUser
import re
from django_countries.fields import CountryField  # Add this import for the country field



# Create your models here.

class Users(AbstractUser):
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


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    birthdate = models.DateField(blank=True, null=True)
    facebook_profile = models.URLField(max_length=255, blank=True, null=True)
    country = CountryField(blank_label='(select country)', blank=True, null=True)  # Updated to include a blank label

    def __str__(self):
        return self.user.username

