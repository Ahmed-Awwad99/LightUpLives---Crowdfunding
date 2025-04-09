from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views


urlpatterns = [# Changed name to "index"
    path("sign_in/", UserLoginView.as_view(), name="sign_in"),
    path("sign_out/", auth_views.LogoutView.as_view(next_page="sign_in"), name="sign_out"),
    path("password_change/", CustomPasswordChangeView.as_view(), name="password_change"),
    path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path("reset/<uidb64>/<token>/", CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("register/", RegisterView.as_view(), name="sign_up"),  # Uncommented registration path
    path("edit/", EditView.as_view(), name="edit"),
    path('profile/', profile, name='profile'),
    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate_account'),  # Renamed for clarity
    path('activation_failure/', ResendActivationEmailView.as_view(), name='resend_activation_mail'),  # Added activation failure view

]
# Set the login URL for the login_required decorator
LOGIN_URL = 'sign_in'

