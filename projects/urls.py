from django.urls import path
from .views import create_project, manage_projects, projects_home, project_detail, report_project, cancel_project

urlpatterns = [
    path('', projects_home, name='projects_home'),
    path('create/', create_project, name='create_project'),
    path('manage/', manage_projects, name='manage_projects'),
    path('<int:project_id>/', project_detail, name='project_detail'),
    path('<int:project_id>/report/', report_project, name='report_project'),
    path('<int:project_id>/cancel/', cancel_project, name='cancel_project'),
]
