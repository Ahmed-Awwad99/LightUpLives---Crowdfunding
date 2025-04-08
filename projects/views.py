from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal  
from django.http import HttpResponseForbidden  
from django.db.models import Q  
from .forms import *
from .models import *

@login_required
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            tag_input = request.POST.get('tags', '[]')  # Tagify بيرجع JSON
            import json
            try:
                tag_data = json.loads(tag_input)
                for tag_item in tag_data:
                    tag_name = tag_item['value'].strip()
                    if tag_name:
                        tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                        project.tags.add(tag_obj)
            except json.JSONDecodeError:
                pass 
            for image in request.FILES.getlist('images'):
                ProjectImage.objects.create(project=project, image=image)
            return redirect('home')
    else:
        form = ProjectForm()
    return render(request, 'projects/create_project.html', {'form': form})

@login_required
def manage_projects(request):

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
    remaining = project.target - total_donated  # Calculate remaining amount

    # Fix the similar_projects query
    similar_projects = Project.objects.filter(
        tags__in=project.tags.all()
    ).exclude(id=project.id).distinct()[:4]

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
        elif 'rate' in request.POST:
            rating_form = RatingForm(request.POST)
            if rating_form.is_valid():
                rating = rating_form.save(commit=False)
                rating.project = project
                rating.user = request.user
                rating.save()
                return redirect('project_detail', project_id=project.id)
    else:
        form = DonationForm()
        comment_form = CommentForm()
        rating_form = RatingForm()

    return render(request, 'projects/project_detail.html', {
        'project': project,
        'form': form,
        'comment_form': comment_form,
        'rating_form': rating_form,
        'donations': donations,
        'comments': comments,
        'total_donated': total_donated,
        'remaining': remaining,  # Pass remaining amount to the template
        'similar_projects': similar_projects,  
        'average_rating': project.average_rating(),
    })

@login_required
def report_project(request, project_id):
    project = Project.objects.get(id=project_id)
    previous_reports = None
    alert = None 
    alert_type = None  

    if request.user == project.created_by:
        previous_reports = project.reports.all()

    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.project = project
            report.user = request.user
            report.save()
            alert = "Your report has been submitted."
            alert_type = "success"
        else:
            alert = "There was an error submitting your report. Please try again."
            alert_type = "danger"
    else:
        form = ReportForm()

    return render(request, 'projects/report_project.html', {
        'form': form,
        'project': project,
        'user': request.user,
        'previous_reports': previous_reports,  
        'alert': alert,
        'alert_type': alert_type,
        'redirect_url': f"/projects/{project_id}/", 
    })

@login_required
def cancel_project(request, project_id):
    project = Project.objects.get(id=project_id, created_by=request.user)
    total_donated = sum(donation.amount for donation in project.donations.all())
    alert = None  
    alert_type = None  

    if total_donated < (Decimal('0.25') * project.target):  
        project.cancelled = True
        project.save()
        alert = "Project has been successfully canceled."
        alert_type = "success"
    else:
        alert = "You cannot cancel this project as donations exceed 25% of the target."
        alert_type = "danger"

    return render(request, 'projects/manage_projects.html', {
        'alert': alert,
        'alert_type': alert_type,
        'user_projects': Project.objects.filter(created_by=request.user),
        'all_projects': Project.objects.filter(cancelled=False),
    })

def projects_by_tag(request, tag_name):
    tag = Tag.objects.get(name=tag_name)
    projects = tag.projects.filter(cancelled=False)
    return render(request, 'projects/projects_by_tag.html', {'tag': tag, 'projects': projects})


