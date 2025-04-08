from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib import messages
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from django.contrib.auth.decorators import login_required
from .models import Users, Profile
from django.views import View
################### Imports for authentication and email functions ###################
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .utilis import account_token
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string

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
                login(request, user)
                return render(request, 'users/home.html', {"user": user})
            else:
                return render(request, 'users/sign_in.html', {"form": form, "error": "Invalid email or password"})
        return render(request, 'users/sign_in.html', {"form": form})


# class UserLoginView(View):
#     def get(self, request):
#         form = LoginForm()
#         return render(request, 'users/sign_in.html', {"form": form})

#     def post(self, request):
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             data = form.cleaned_data
#             user = authenticate(request, email=data['email'], password=data['password'])  # Authenticate using email
#             if user is not None and user.email_confirmed:
#                 login(request, user)
#                 return render(request, 'users/home.html', {"user": user})
#             else:
#                 return render(request, 'users/sign_in.html', {"form": form, "error": "Invalid email or password"})
#         return render(request, 'users/sign_in.html', {"form": form})
class RegisterView(View):
    def get(self, request):
        user_form = UserRegistrationForm()
        return render(request, 'users/sign_up.html', {"user_form": user_form})
    def post(self, request):
        
        user_form = UserRegistrationForm(request.POST, request.FILES)  # Include request.FILES to handle file uploads
        if user_form.is_valid():
            user_object = user_form.save(commit=False)
            user_object.set_password(user_form.cleaned_data['password'])
            user_object.email_confirmed = False  #! Set user inactive until email confirmation
            user_object.save()  # Just save the object without assignment
            user = user_object  # Use the user_object directly
            #? Create the profile object after saving the user
            Profile.objects.create(user=user)
            #? Send activation email
            self.send_activation_email(request,user)
            #? Redirect to sign in page after successful registration
            return redirect('sign_in')  
        #? If the form is not valid, render the sign-up page with the form errors
        return render(request, 'users/sign_up.html', {"user_form": user_form})
    
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
                    return render(request, 'users/activation_failure.html')
            else:
                return render(request, 'users/sign_in.html', {"form": form, "error": "Invalid email or password"})
        return render(request, 'users/sign_in.html', {"form": form})

    
    def send_activation_email(self, request, user):
        domain = request.get_host()  # Get the domain from the request
        subject = "Please Activate Your Account"
        message = f"Please activate your account by visiting: http://{domain}/activate/{urlsafe_base64_encode(force_bytes(user.pk))}/{account_token.make_token(user)}/"

        try:
            # Send email with both text and HTML versions
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            print("Email sent successfully")
        except Exception as e:
            # Log the error (in a real app) but continue with the registration process
            print(f"Error sending email: {e}")

class ResendActivationEmailView(View):
    def get(self, request):
        # Pass any error message if it exists in the session
        error = request.session.pop('resend_error', None)
        return render(request, 'users/activation_failure.html', {'error': error})

    def post(self, request):
        email = request.POST.get('email')
        
        if not email:
            return render(request, 'users/activation_failure.html', {'error': 'Please provide an email address'})
            
        try:
            user = Users.objects.get(email=email, email_confirmed=False)
            self.send_activation_email(request, user)
            email_sent = True  # Assuming the method doesn't return anything
            if email_sent:
                return redirect('sign_in')
            else:
                return render(request, 'users/activation_failure.html', {'error': 'Failed to send email'})
        except Users.DoesNotExist:
            return render(request, 'users/activation_failure.html', {'error': 'No unverified account found with this email'})
    
    def send_activation_email(self, request, user):
        domain = request.get_host()  # Get the domain from the request
        subject = "Please Activate Your Account"
        message = f"Please activate your account by visiting: http://{domain}/activate/{urlsafe_base64_encode(force_bytes(user.pk))}/{account_token.make_token(user)}/"

        try:
            # Send email with both text and HTML versions
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            print("Email sent successfully")
        except Exception as e:
            # Log the error (in a real app) but continue with the registration process
            print(f"Error sending email: {e}")
    
#? The second part of the code is the activation view
class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Users.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Users.DoesNotExist):
            user = None

        if user is not None and account_token.check_token(user, token):
            user.email_confirmed = True  # Set the user to active instead of email_confirmation
            user.save()
            return render(request, 'users/activation_success.html')
        else:
            return render(request, 'users/activation_failure.html')



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

class CustomPasswordResetView(View):
    def get(self, request):
        return render(request, "users/password_reset.html", {"form": PasswordResetForm()})
    
    def post(self, request):
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Get active users with this email
            associated_users = Users.objects.filter(email__iexact=email)
            
            if associated_users.exists():
                user = associated_users.first()
                # Use account_token from utilis like the activation view
                subject = "Password Reset Request"
                # Modify the URL to match your URL pattern for password reset confirmation
                reset_url = f"http://localhost:8000/reset/{urlsafe_base64_encode(force_bytes(user.pk))}/{account_token.make_token(user)}/"
                message = f"Please reset your password by clicking: {reset_url}"
                html_message = f"""
                <html>
                <body>
                    <h2>Reset Your Password</h2>
                    <p>Hello, we received a request to reset your password.</p>
                    <p>Please click the link below to reset your password:</p>
                    <p><a href="{reset_url}">Reset Password</a></p>
                    <p>If the link doesn't work, copy and paste this URL into your browser:</p>
                    <p>{reset_url}</p>
                    <p>If you didn't request this, please ignore this email.</p>
                    <p>Thank you!</p>
                </body>
                </html>
                """
                
                try:
                    # Send email with both text and HTML versions
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    print("Password reset email sent successfully")
                except Exception as e:
                    print(f"Error sending password reset email: {e}")
            
            # Always show success to prevent email enumeration
            return render(request, "users/password_reset.html", {"email_sent": True})
        return render(request, "users/password_reset.html", {"form": form})


class CustomPasswordResetConfirmView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Users.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Users.DoesNotExist):
            user = None
        
        if user is not None and account_token.check_token(user, token):
            return render(request, "users/password_reset_confirm.html", {"form": SetPasswordForm(user), "valid_link": True})
        return render(request, "users/password_reset_confirm.html", {"valid_link": False})
    
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Users.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Users.DoesNotExist):
            user = None
            
        if user is not None and account_token.check_token(user, token):
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return render(request, "users/password_reset_confirm.html", {"password_changed": True, "valid_link": True})
            return render(request, "users/password_reset_confirm.html", {"form": form, "valid_link": True})
        return render(request, "users/password_reset_confirm.html", {"valid_link": False})


class CustomPasswordChangeView(View):
    def get(self, request):
        form = PasswordChangeForm(request.user)
        return render(request, 'users/password_change.html', {
            'form': form,
            'password_changed': False
        })

    def post(self, request):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Keep the user logged in
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return render(request, 'users/password_change.html', {
                'form': None,
                'password_changed': True
            })
        return render(request, 'users/password_change.html', {
            'form': form,
            'password_changed': False
        })


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

