from django.urls import path
from .views import (
    ProjectsHomeView,
    CreateProjectView,
    ManageProjectsView,
    ProjectDetailView,
    ReportProjectView,
    CancelProjectView,
)

urlpatterns = [
    path('', ProjectsHomeView.as_view(), name='projects_home'),
    path('create/', CreateProjectView.as_view(), name='create_project'),
    path('manage/', ManageProjectsView.as_view(), name='manage_projects'),
    path('<int:project_id>/', ProjectDetailView.as_view(), name='project_detail'),
    path('<int:project_id>/report/', ReportProjectView.as_view(), name='report_project'),
    path('<int:project_id>/cancel/', CancelProjectView.as_view(), name='cancel_project'),
]
