from django.urls import path
from .views import create_project, manage_projects, projects_home, project_detail

urlpatterns = [
    path('', projects_home, name='projects_home'),
    path('create/', create_project, name='create_project'),
    path('manage/', manage_projects, name='manage_projects'),
]
