from django.shortcuts import render
from django.urls import path
from django.views.generic import View

# Create your views here.

def home(request):
    return render(request, 'users/home.html')

def login(request):
    return render(request, 'users/login.html')

def register(request):
    return render(request, 'users/register.html')

