from django.shortcuts import render
from django.urls import path
from django.views.generic import View

# Create your views here.


def home(request):
    return render(request, 'users/home.html')

def sign_in(request):
    return render(request, 'users/sign_in.html')

def sign_up(request):
    return render(request, 'users/sign_up.html')

def account(request):
    return render(request, 'users/account.html')

def profile(request):
    return render(request, 'users/profile.html')
