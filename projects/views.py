from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal  # Import Decimal for precise arithmetic
from django.http import HttpResponseForbidden  # Import for handling forbidden access
from .forms import ProjectForm, DonationForm, CommentForm, ReportForm
from .models import Project, Donation, Report

@login_required
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            return redirect('home')
    else:
        form = ProjectForm()
    return render(request, 'projects/create_project.html', {'form': form})

@login_required
def manage_projects(request):
    # Include canceled projects only for the creator
    user_projects = Project.objects.filter(created_by=request.user)
    all_projects = Project.objects.filter(cancelled=False)  
    return render(request, 'projects/manage_projects.html', {
        'user_projects': user_projects,
        'all_projects': all_projects,
    })

def projects_home(request):
    return render(request, 'projects/projects_home.html')

def project_detail(request, project_id): 
    project = Project.objects.get(id=project_id)
    donations = project.donations.all()
    total_donated = sum(donation.amount for donation in donations)
    comments = project.comments.all()

    if request.method == "POST":
        if 'donate' in request.POST:
            form = DonationForm(request.POST)
            if form.is_valid():
                donation = form.save(commit=False)
                donation.project = project
                donation.donor = request.user
                donation.save()
                return redirect('project_detail', project_id=project.id)
        elif 'comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.project = project
                comment.user = request.user
                comment.save()
                return redirect('project_detail', project_id=project.id)
        else:
            form = DonationForm()
            comment_form = CommentForm()
    else:
        form = DonationForm()
        comment_form = CommentForm()

    return render(request, 'projects/project_detail.html', {
        'project': project,
        'form': form,
        'comment_form': comment_form,
        'donations': donations,
        'comments': comments,
        'total_donated': total_donated,
    })

@login_required
def report_project(request, project_id):
    project = Project.objects.get(id=project_id)
    previous_reports = None

    if request.user == project.created_by:
        previous_reports = project.reports.all()

    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.project = project
            report.user = request.user
            report.save()
            messages.success(request, "Your report has been submitted.")
            return redirect('project_detail', project_id=project.id)
    else:
        form = ReportForm()

    return render(request, 'projects/report_project.html', {
        'form': form,
        'project': project,
        'previous_reports': previous_reports,  
    })

@login_required
def cancel_project(request, project_id):
    project = Project.objects.get(id=project_id, created_by=request.user)
    total_donated = sum(donation.amount for donation in project.donations.all())
    if total_donated < (Decimal('0.25') * project.target):  # Use Decimal for multiplication
        project.cancelled = True
        project.save()
        messages.success(request, "Project has been successfully canceled.")
    else:
        messages.error(request, "You cannot cancel this project as donations exceed 25% of the target.")
    return redirect('manage_projects')

