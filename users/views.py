from datetime import timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.timezone import now
from django.views import View
import csv

from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Users, Profile
from .utilis import account_token
from projects.models import *

#! static method to use it in resend activation email view and register view
@staticmethod
def send_activation_email(request, user):
    user.token_created_at = now()
    user.save(update_fields=['token_created_at'])

    domain = request.get_host()
    subject = "Please Activate Your Account"
    message = f"""Please activate your account by visiting: 
http://{domain}/users/activate/{urlsafe_base64_encode(force_bytes(user.pk))}/{account_token.make_token(user)}/

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
                    return redirect('home')
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
        return render(request, 'users/edit.html', {
            'user_form': user_form, 
            'profile_form': profile_form,
            'user': request.user  # Pass the user object to the template
        })

    def post(self, request):
        user_form = UserEditForm(
            data=request.POST,
            files=request.FILES,  # Move request.FILES here since profile_picture is in Users model
            instance=request.user
        )
        profile_form = ProfileEditForm(
            data=request.POST,
            instance=request.user.profile
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "You have successfully updated your profile")
            return render(request, 'users/edit.html', {
                'user_form': user_form, 
                'profile_form': profile_form, 
                'success': True,
                'user': request.user  # Pass the user object to the template
            })
        else:
            # Show form errors message
            messages.error(request, "Please correct the errors below.")
        return render(request, 'users/edit.html', {
            'user_form': user_form, 
            'profile_form': profile_form,
            'user': request.user  # Pass the user object to the template
        })


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
    return render(request, 'home.html')

def sign_in(request):
    return render(request, 'users/sign_in.html')

def sign_up(request):
    return render(request, 'users/sign_up.html' )

def account(request):
    return render(request, 'users/account.html')

def profile(request):
    return render(request, 'users/profile.html')

def custom_logout_view(request):
    logout(request)
    return redirect('sign_in')  # Redirect to the sign-in page after logout

# Admin Dashboard Views
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

class AdminDashboardView(AdminRequiredMixin, View):
    def get(self, request):
        projects = Project.objects.all().order_by('-created_at')
        users = Users.objects.filter(is_staff=False).order_by('-date_joined')
        donations = Donation.objects.all().order_by('-donated_at')
        project_reports = Report.objects.filter(dismissed=False).order_by('-created_at')
        comments = Comment.objects.all().order_by('-created_at')
        categories = Category.objects.all().order_by('name')
        
        # Calculate dashboard statistics
        stats = {
            'total_users': Users.objects.filter(is_staff=False).count(),
            'total_projects': Project.objects.count(),
            'total_donations': Donation.objects.count(),
            'total_amount': Donation.objects.aggregate(Sum('amount'))['amount__sum'] or 0,
        }
        
        context = {
            'projects': projects,
            'users': users,
            'donations': donations,
            'project_reports': project_reports,
            'comments': comments,
            'categories': categories,
            'stats': stats,
        }
        
        return render(request, 'users/admin_dashboard.html', context)

class AdminDeleteProjectView(AdminRequiredMixin, View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        project_title = project.title
        project.delete()
        messages.success(request, f"Project '{project_title}' has been successfully deleted.")
        return redirect('admin_dashboard')

class AdminDeleteUserView(AdminRequiredMixin, View):
    def post(self, request, user_id):
        user = get_object_or_404(Users, id=user_id)
        user_email = user.email
        user.delete()
        messages.success(request, f"User '{user_email}' has been successfully deleted along with all their projects and donations.")
        return redirect('admin_dashboard')

class AdminToggleFeaturedView(AdminRequiredMixin, View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        project.is_featured = not project.is_featured
        project.save()
        
        if project.is_featured:
            messages.success(request, f"Project '{project.title}' has been featured.")
        else:
            messages.success(request, f"Project '{project.title}' has been unfeatured.")
        
        return redirect('admin_dashboard')

class AdminDismissReportView(AdminRequiredMixin, View):
    def post(self, request, report_id):
        report = get_object_or_404(Report, id=report_id)
        report.dismissed = True
        report.save()
        messages.success(request, f"Report on project '{report.project.title}' has been dismissed.")
        return redirect('admin_dashboard')

class AdminApproveCommentView(AdminRequiredMixin, View):
    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        comment.is_approved = True
        comment.is_flagged = False
        comment.save()
        messages.success(request, f"Comment on project '{comment.project.title}' has been approved.")
        return redirect('admin_dashboard')

class AdminDeleteCommentView(AdminRequiredMixin, View):
    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        project_title = comment.project.title
        comment.delete()
        messages.success(request, f"Comment on project '{project_title}' has been deleted.")
        return redirect('admin_dashboard')

class AdminAddCategoryView(AdminRequiredMixin, View):
    def post(self, request):
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not name:
            messages.error(request, "Category name is required.")
            return redirect('admin_dashboard')
            
        # Check if category with this name already exists
        if Category.objects.filter(name=name).exists():
            messages.error(request, f"Category '{name}' already exists.")
            return redirect('admin_dashboard')
            
        Category.objects.create(name=name, description=description)
        messages.success(request, f"Category '{name}' has been created successfully.")
        return redirect('admin_dashboard')

class AdminEditCategoryView(AdminRequiredMixin, View):
    def post(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not name:
            messages.error(request, "Category name is required.")
            return redirect('admin_dashboard')
            
        # Check if another category with this name already exists
        if Category.objects.filter(name=name).exclude(id=category_id).exists():
            messages.error(request, f"Category '{name}' already exists.")
            return redirect('admin_dashboard')
            
        category.name = name
        category.description = description
        category.save()
        messages.success(request, f"Category '{name}' has been updated successfully.")
        return redirect('admin_dashboard')

class AdminDeleteCategoryView(AdminRequiredMixin, View):
    def post(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        
        # Check if category has associated projects
        if category.projects.exists():
            messages.error(request, f"Cannot delete category '{category.name}' as it has associated projects.")
            return redirect('admin_dashboard')
            
        category_name = category.name
        category.delete()
        messages.success(request, f"Category '{category_name}' has been deleted.")
        return redirect('admin_dashboard')

class AdminExportDonationsView(AdminRequiredMixin, View):
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="donations.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Project Title', 'Donor Email', 'Amount', 'Date'])
        
        donations = Donation.objects.all().order_by('-donated_at')
        for donation in donations:
            writer.writerow([
                donation.project.title,
                donation.donor.email,
                donation.amount,
                donation.donated_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
            
        return response

