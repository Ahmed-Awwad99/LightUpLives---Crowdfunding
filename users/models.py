from django.db import models
from django.core.validators import RegexValidator 
from django.conf import settings


# Create your models here.

class Users(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=15, unique=True, validators=[
        RegexValidator(
            regex=r'^01[0-2,5]{1}[0-9]{8}$',
            message='Phone number must be a valid Egyptian number starting with 010, 011, 012, or 015'
        )
    ])
    profile_picture=models.ImageField(upload_to='media/profile_images/', blank=True, null=True)
    

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    photo = models.ImageField(upload_to='media/profile_images/%Y/%m/%d', blank=True, null=True)

    def __str__(self):
        return self.user.username
    