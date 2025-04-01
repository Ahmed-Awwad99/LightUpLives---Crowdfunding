from django.contrib import admin
from .models import Profile, Users
# Register your models here.
admin.site.register(Profile)
admin.site.register(Users)  # Register the custom Users model
