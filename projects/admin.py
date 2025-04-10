from django.contrib import admin

from .models import Category, Project, Donation, Comment, Report, Tag, ProjectImage,CommentReport


admin.site.register(Category)
admin.site.register(Project)
admin.site.register(ProjectImage)
admin.site.register(Donation)
admin.site.register(Comment)
admin.site.register(Report)
admin.site.register(Tag)  
admin.site.register(CommentReport)







