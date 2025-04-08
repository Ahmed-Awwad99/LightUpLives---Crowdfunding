from django.contrib import admin
from .models import Category, Project, Donation, Comment, Report, ProjectImage

admin.site.register(Category)
admin.site.register(Project)
admin.site.register(ProjectImage)
admin.site.register(Donation)
admin.site.register(Comment)
admin.site.register(Report)
