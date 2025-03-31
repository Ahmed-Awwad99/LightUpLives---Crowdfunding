from django.shortcuts import render
from django.contrib.auth import authenticate, login
from .forms import LoginForm 
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(request, username=data['username'], password=data['password'])
            if user is not None:
                login(request, user)
                return render(request, 'users/login_success.html', {"user": user})
            else:
                return HttpResponse("Invalid username or password")
            

    else:
        form = LoginForm()
        return render(request, 'users/login.html',{"form": form})



@login_required # you have to set up the login url in settings.py
def index(request):
    return render(request, 'users/index.html')

