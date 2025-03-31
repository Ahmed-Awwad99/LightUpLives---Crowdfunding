from django.shortcuts import render
from django.contrib.auth import authenticate, login
from .forms import LoginForm ,UserRegistrationForm,UserEditForm, ProfileEditForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile

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


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            Profile.objects.create(user=user)
            return render(request, 'users/register_done.html', {"user": user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'users/register.html', {"user_form": user_form})


@login_required
def edit(request):
    if request.method == 'POST':
        user_from = UserEditForm(request.POST, instance=request.user)
        profile_form = ProfileEditForm(data =request.POST, files = request.FILES, instance=request.user.profile)
        if user_from.is_valid() and profile_form.is_valid():
            user_from.save()
            profile_form.save()
    else:
        user_from = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request, 'users/edit.html', {'user_form': user_from, 'profile_form': profile_form})
    
            