from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

from .models import Category, Project, Donation, Comment, Report, Tag, ProjectImage,CommentReport

try:
    admin.site.register(Category)
except AlreadyRegistered:
    pass

admin.site.register(Project)
admin.site.register(ProjectImage)
admin.site.register(Donation)
admin.site.register(Comment)
admin.site.register(Report)
admin.site.register(Tag)  
admin.site.register(CommentReport)







