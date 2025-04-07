from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("", IndexView.as_view(), name="home"),  # Changed name to "index"
    path("sign_in/", UserLoginView.as_view(), name="sign_in"),
    path("sign_out/", auth_views.LogoutView.as_view(next_page="sign_in"), name="sign_out"),
    path("password_change/", auth_views.PasswordChangeView.as_view(template_name="users/password_change_form.html"), name="password_change"),
    path("password_change/done/", auth_views.PasswordChangeDoneView.as_view(template_name="users/password_change_done.html"), name="password_change_done"),
    path("password_reset/", auth_views.PasswordResetView.as_view(template_name="users/password_reset_form.html"), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="users/password_reset_confirm.html"), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"), name="password_reset_complete"),
    path("register/", RegisterView.as_view(), name="sign_up"),  # Uncommented registration path
    path("edit/", EditView.as_view(), name="edit"),
    path('profile/', profile, name='profile'),
    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate_account'),  # Renamed for clarity

]
# Set the login URL for the login_required decorator
LOGIN_URL = 'sign_in'

