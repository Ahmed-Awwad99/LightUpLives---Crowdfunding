from django.urls import path
from .views import (
    CreateProjectView,
    ProjectDetailView,
    ReportProjectView,
    CancelProjectView,
    ProjectsByTagView,
    ProjectsByCategoryView,
    SearchProjectsView,
    ReportCommentView
)

urlpatterns = [
    path('create/', CreateProjectView.as_view(), name='create_project'),
    path('<int:project_id>/', ProjectDetailView.as_view(), name='project_detail'),
    path('<int:project_id>/report/', ReportProjectView.as_view(), name='report_project'),
    path('<int:project_id>/cancel/', CancelProjectView.as_view(), name='cancel_project'),
    path('tag/<str:tag_name>/', ProjectsByTagView.as_view(), name='projects_by_tag'),
    path('category/<str:category_name>/', ProjectsByCategoryView.as_view(), name='projects_by_category'),
    path('search/', SearchProjectsView.as_view(), name='search_projects'),
    path('comments/<int:comment_id>/report/', ReportCommentView.as_view(), name='report_comment'),
]
