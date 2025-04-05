from django.contrib import admin
from .models import Category, Project, Donation, Comment

admin.site.register(Category)
admin.site.register(Project)
admin.site.register(Donation)
admin.site.register(Comment)
