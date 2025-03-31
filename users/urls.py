from django.urls import path
from .views import user_login,index
from django.contrib.auth import views as auth_views
urlpatterns = [

    path("", index, name="index"),
    path("login/", user_login, name="login"),
    path("logout/", auth_views.LogoutView.as_view(template_name='users/logout.html'), name="logout"),

]
