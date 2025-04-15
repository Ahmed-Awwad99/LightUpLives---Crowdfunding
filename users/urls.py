from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views
from .views import custom_logout_view, my_projects, my_donations

urlpatterns = [ 
    path("sign_in/", UserLoginView.as_view(), name="sign_in"),
    path("sign_out/", custom_logout_view, name="sign_out"),
    path(
        "password_change/", CustomPasswordChangeView.as_view(), name="password_change"
    ),
    path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path(
        "reset/<uidb64>/<token>/",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "register/", RegisterView.as_view(), name="sign_up"
    ),  # Uncommented registration path
    path("edit/", EditView.as_view(), name="edit"),
    path("profile/", profile, name="profile"),
    path(
        "activate/<uidb64>/<token>/",
        ActivateAccountView.as_view(),
        name="activate_account",
    ),  # Renamed for clarity
    path(
        "activation_failure/",
        ResendActivationEmailView.as_view(),
        name="resend_activation_mail",
    ),  # Added activation failure view
    # Admin Dashboard URLs
    path("admin-dashboard/", AdminDashboardView.as_view(), name="admin_dashboard"),
    path(
        "admin/delete-project/<int:project_id>/",
        AdminDeleteProjectView.as_view(),
        name="admin_delete_project",
    ),
    path(
        "admin/delete-user/<int:user_id>/",
        AdminDeleteUserView.as_view(),
        name="admin_delete_user",
    ),
    # New admin dashboard functionality
    path(
        "admin/toggle-featured/<int:project_id>/",
        AdminToggleFeaturedView.as_view(),
        name="admin_toggle_featured",
    ),
    path(
        "admin/dismiss-report/<int:report_id>/",
        AdminDismissReportView.as_view(),
        name="admin_dismiss_report",
    ),
    path(
        "admin/approve-comment/<int:comment_id>/",
        AdminApproveCommentView.as_view(),
        name="admin_approve_comment",
    ),
    path(
        "admin/delete-comment/<int:comment_id>/",
        AdminDeleteCommentView.as_view(),
        name="admin_delete_comment",
    ),
    path(
        "admin/add-category/", AdminAddCategoryView.as_view(), name="admin_add_category"
    ),
    path(
        "admin/edit-category/<int:category_id>/",
        AdminEditCategoryView.as_view(),
        name="admin_edit_category",
    ),
    path(
        "admin/delete-category/<int:category_id>/",
        AdminDeleteCategoryView.as_view(),
        name="admin_delete_category",
    ),
    path(
        "admin/export-donations/",
        AdminExportDonationsView.as_view(),
        name="admin_export_donations",
    ),
    path("my-projects/", my_projects, name="my_projects"),
    path("my-donations/", my_donations, name="my_donations"),
    path("delete-account/", DeleteAccountView.as_view(), name="delete_account"),
]
# Set the login URL for the login_required decorator
LOGIN_URL = "sign_in"
