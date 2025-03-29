from django.urls import path
from .views import * 



urlpatterns = [
    path('home/', home, name='home'),
    path('login/', sign_in, name='sign_in'),
    path('register/', sign_up, name='sign_up'),
    path('account/', account, name='account'),
    path('profile/', profile, name='profile'),
]
