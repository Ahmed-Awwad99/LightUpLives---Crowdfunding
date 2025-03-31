from django.db import models
from django.core.validators import RegexValidator 
from django.conf import settings
import re



# Create your models here.

class Users(models.Model):
    first_name = models.CharField(max_length=30, validators=[
        RegexValidator(
            regex=r'^[a-zA-Z]+$',
            message='First name must contain only letters'
        )
    ],db_column="first_name"
    )

    last_name = models.CharField(max_length=30, validators=[
        RegexValidator(
            regex=r'^[a-zA-Z]+$',
            message='Last name must contain only letters'
        )
    ],db_column="last_name"
    )

    email = models.EmailField(max_length=254, unique=True, validators=[
        RegexValidator(
            regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            message='Enter a valid email address'
        )
    ],db_column="email"
    )

    password = models.CharField(max_length=128, validators=[
        RegexValidator(
            regex=r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$',
            message='Password must be at least 8 characters long and contain at least one letter and one number'
        )
    ],db_column="password"
    )

    phone_number = models.CharField(max_length=15, unique=True, validators=[
        RegexValidator(
            regex=r'^01[0-2,5]{1}[0-9]{8}$',
            message='Phone number must be a valid Egyptian number starting with 010, 011, 012, or 015'
        )


    ],db_column="phone_number"
    )
    profile_picture = models.ImageField(
        upload_to='media/profile_images/',
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'\.(jpg|jpeg|png|gif)$',
                message='Only image files (jpg, jpeg, png, gif) are allowed',
                flags=re.IGNORECASE
            )
        ],db_column="profile_picture"
    )
    


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    photo = models.ImageField(upload_to='users/profile_images/', blank=True, null=True)

    def __str__(self):
        return self.user.username
    
