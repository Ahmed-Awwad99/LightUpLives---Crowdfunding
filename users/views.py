from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import *
from .models import *
from django.views import View
from django.utils.timezone import now
from datetime import timedelta, datetime
from django.utils.http import base36_to_int
################### Some imports for email verfication  ###################
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .utilis import account_token
from django.core.mail import send_mail
from django.conf import settings

#! static method to use it in resend activation email view and register view
@staticmethod
def send_activation_email(request, user):
    user.token_created_at = now()
    user.save(update_fields=['token_created_at'])

    domain = request.get_host()
    subject = "Please Activate Your Account"
    message = f"""Please activate your account by visiting: 
http://{domain}/activate/{urlsafe_base64_encode(force_bytes(user.pk))}/{account_token.make_token(user)}/

Note: This activation link will expire in 30 seconds."""

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")

#! Register view with email verification
class RegisterView(View):
    def get(self, request):
        user_form = UserRegistrationForm()
        return render(request, 'users/sign_up.html', {"user_form": user_form})
    def post(self, request):
        
        user_form = UserRegistrationForm(request.POST, request.FILES)  # Include request.FILES to handle file uploads
        if user_form.is_valid():
            user_object = user_form.save(commit=False)
            user_object.set_password(user_form.cleaned_data['password'])
            user_object.email_confirmed = False  #~ Set user unverfied until email confirmation
            user_object.save()  #~ Just save the object without assignment
            user = user_object  #~ Use the user_object directly
            #~ Create the profile object after saving the user
            Profile.objects.create(user=user)
            #~ Send activation email
            send_activation_email(request,user)
            #~ Redirect to sign in page after successful registration
            return redirect('sign_in')  
        #~ If the form is not valid, render the sign-up page with the form errors
        return render(request, 'users/sign_up.html', {"user_form": user_form})
#! Login view with email authentication
class UserLoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'users/sign_in.html', {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(request, email=data['email'], password=data['password'])  # Authenticate using email
            if user is not None:
                if user.email_confirmed:
                    login(request, user)
                    return render(request, 'users/home.html', {"user": user})
                else:
                    return render(request, 'users/activation_failure.html',{"user": user})
            else:
                return render(request, 'users/sign_in.html', {"form": form, "error": "Invalid email or password"})
        return render(request, 'users/sign_in.html', {"form": form})
    
#! The second part of the email verdfication process in register view

class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Users.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Users.DoesNotExist):
            user = None

        if user:
            expiration_time = user.token_created_at + timedelta(days=1)
            if now() > expiration_time:
                return render(request, 'users/activation_failure.html', {
                    'reason': 'Token expired'
                })

            if account_token.check_token(user, token):
                user.email_confirmed = True
                user.save()
                return render(request, 'users/activation_success.html')

        return render(request, 'users/activation_failure.html', {
            'reason': 'Invalid or expired token'
        })
    


#! Resend activation email view
class ResendActivationEmailView(View):
    def get(self, request):
        #? Pass any error message if it exists in the session
        error = request.session.pop('resend_error', None)
        return render(request, 'users/activation_failure.html', {'error': error})

    def post(self, request):
        email = request.POST.get('email')
        if not email:
            return render(request, 'users/activation_failure.html', {'error': 'Please provide an email address'})
        user = Users.objects.get(email=email, email_confirmed=False)
        print(user) # Get the current user
        
        if not email:
            return render(request, 'users/activation_failure.html', {'error': 'Please provide an email address'})
            
        try:
            user = Users.objects.get(email=email, email_confirmed=False)
            send_activation_email(request, user)
            email_sent = True  # Assuming the method doesn't return anything
            if email_sent:
                return redirect('sign_in')
            else:
                return render(request, 'users/activation_failure.html', {'error': 'Failed to send email'})
        except Users.DoesNotExist:
            return render(request, 'users/activation_failure.html', {'error': 'No unverified account found with this email'})
    
    

#! Edit view for user profile and account settings
class EditView(View):
    def get(self, request):
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
        return render(request, 'users/edit.html', {'user_form': user_form, 'profile_form': profile_form})

    def post(self, request):
        user_form = UserEditForm(request.POST, request.FILES, instance=request.user)
        profile_form = ProfileEditForm(data=request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
        return render(request, 'users/edit.html', {'user_form': user_form, 'profile_form': profile_form})

class IndexView(View):
    def get(self, request):
        return render(request, 'users/home.html')

def home(request):
    return render(request, 'users/home.html')

def sign_in(request):
    return render(request, 'users/sign_in.html')

def sign_up(request):
    return render(request, 'users/sign_up.html' )

def account(request):
    return render(request, 'users/account.html')

def profile(request):
    return render(request, 'users/profile.html')

