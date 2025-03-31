from django.shortcuts import render
from django.contrib.auth import authenticate, login
from .forms import LoginForm ,UserRegistrationForm,UserEditForm, ProfileEditForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile
from django.views import View
from django.views.generic.edit import FormView

class UserLoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'users/login.html', {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(request, username=data['username'], password=data['password'])
            if user is not None:
                login(request, user)
                return render(request, 'users/login_success.html', {"user": user})
            else:
                return HttpResponse("Invalid username or password")
        return render(request, 'users/login.html', {"form": form})


class IndexView(View):
    def get(self, request):
        return render(request, 'users/index.html')


class RegisterView(View):
    def get(self, request):
        user_form = UserRegistrationForm()
        return render(request, 'users/register.html', {"user_form": user_form})

    def post(self, request):
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            Profile.objects.create(user=user)
            return render(request, 'users/register_done.html', {"user": user})
        return render(request, 'users/register.html', {"user_form": user_form})


class EditView(View):
    def get(self, request):
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
        return render(request, 'users/edit.html', {'user_form': user_form, 'profile_form': profile_form})

    def post(self, request):
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = ProfileEditForm(data=request.POST, files=request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
        return render(request, 'users/edit.html', {'user_form': user_form, 'profile_form': profile_form})

