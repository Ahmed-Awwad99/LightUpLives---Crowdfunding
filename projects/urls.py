from django.urls import path
from .views import (
    ProjectsHomeView,
    CreateProjectView,
    ManageProjectsView,
    ProjectDetailView,
    ReportProjectView,
    CancelProjectView,
    projects_by_tag,
    projects_by_category,
    SearchProjectsView
)

urlpatterns = [
    path('', ProjectsHomeView.as_view(), name='projects_home'),
    path('create/', CreateProjectView.as_view(), name='create_project'),
    path('manage/', ManageProjectsView.as_view(), name='manage_projects'),
    path('<int:project_id>/', ProjectDetailView.as_view(), name='project_detail'),
    path('<int:project_id>/report/', ReportProjectView.as_view(), name='report_project'),
    path('<int:project_id>/cancel/', CancelProjectView.as_view(), name='cancel_project'),
    path('tag/<str:tag_name>/', projects_by_tag, name='projects_by_tag'),
    path('category/<str:category_name>/', projects_by_category, name='projects_by_category'),
    path('search/', SearchProjectsView.as_view(), name='search_projects'),
]
