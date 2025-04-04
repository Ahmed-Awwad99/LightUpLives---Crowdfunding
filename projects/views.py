from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProjectForm, DonationForm
from .models import Project, Donation

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
    user_projects = Project.objects.filter(created_by=request.user)
    all_projects = Project.objects.all()
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

    if request.method == "POST":
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.project = project
            donation.donor = request.user
            donation.save()
            return redirect('project_detail', project_id=project.id)
    else:
        form = DonationForm()

    return render(request, 'projects/project_detail.html', {
        'project': project,
        'form': form,
        'donations': donations,
        'total_donated': total_donated,
    })
