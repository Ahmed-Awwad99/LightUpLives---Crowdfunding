from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProjectForm
from .models import Project

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
    projects = Project.objects.filter(created_by=request.user)
    return render(request, 'projects/manage_projects.html', {'projects': projects})

def projects_home(request):
    all_projects = Project.objects.all()
    user_projects = Project.objects.filter(created_by=request.user) if request.user.is_authenticated else None
    return render(request, 'projects/projects_home.html', {
        'all_projects': all_projects,
        'user_projects': user_projects,
    })

