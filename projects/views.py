from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from decimal import Decimal
from .forms import ProjectForm, DonationForm, CommentForm, ReportForm, RatingForm
from .models import Project, ProjectImage, Donation, Comment, Report, Rating


class CreateProjectView(LoginRequiredMixin, View):
    def get(self, request):
        form = ProjectForm()
        return render(request, 'projects/create_project.html', {'form': form})

    def post(self, request):
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            for image in request.FILES.getlist('images'):
                ProjectImage.objects.create(project=project, image=image)
            return redirect('home')
        return render(request, 'projects/create_project.html', {'form': form})


class ManageProjectsView(LoginRequiredMixin, View):
    def get(self, request):
        user_projects = Project.objects.filter(created_by=request.user)
        all_projects = Project.objects.filter(cancelled=False)
        return render(request, 'projects/manage_projects.html', {
            'user_projects': user_projects,
            'all_projects': all_projects,
        })


class ProjectsHomeView(View):
    def get(self, request):
        return render(request, 'projects/projects_home.html')


class ProjectDetailView(View):
    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        donations = project.donations.all()
        total_donated = sum(donation.amount for donation in donations)
        comments = project.comments.all()
        remaining = project.target - total_donated
        similar_projects = Project.objects.filter(
            Q(tags__icontains=project.tags) & ~Q(id=project.id)
        ).distinct()[:4]

        form = DonationForm()
        comment_form = CommentForm()
        rating_form = RatingForm()

        donation_closed = total_donated >= project.target  # Check if the target is reached

        return render(request, 'projects/project_detail.html', {
            'project': project,
            'form': form,
            'comment_form': comment_form,
            'rating_form': rating_form,
            'donations': donations,
            'comments': comments,
            'total_donated': total_donated,
            'remaining': remaining,
            'similar_projects': similar_projects,
            'average_rating': project.average_rating(),
            'donation_closed': donation_closed,  # Pass the flag to the template
        })

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        donations = project.donations.all()
        total_donated = sum(donation.amount for donation in donations)
        remaining = project.target - total_donated

        if total_donated >= project.target:  # Prevent donations if the target is reached
            messages.info(request, "Thank you, Donation for this project has been completed.")
            return redirect('project_detail', project_id=project.id)

        if 'donate' in request.POST:
            form = DonationForm(request.POST)
            if form.is_valid():
                donation_amount = form.cleaned_data['amount']
                if donation_amount > remaining:
                    messages.error(request, "Donation amount exceeds the remaining target.")
                    return redirect('project_detail', project_id=project.id)
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
        return self.get(request, project_id)


class ReportProjectView(LoginRequiredMixin, View):
    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        form = ReportForm()
        previous_reports = project.reports.all() if request.user == project.created_by else None
        return render(request, 'projects/report_project.html', {
            'form': form,
            'project': project,
            'previous_reports': previous_reports,
        })

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.project = project
            report.user = request.user
            report.save()
            messages.success(request, "Your report has been submitted.")
        else:
            messages.error(request, "There was an error submitting your report.")
        return redirect('project_detail', project_id=project.id)


class CancelProjectView(LoginRequiredMixin, View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id, created_by=request.user)
        total_donated = sum(donation.amount for donation in project.donations.all())
        if total_donated < (Decimal('0.25') * project.target):
            project.cancelled = True
            project.save()
            messages.success(request, "Project has been successfully canceled.")
        else:
            messages.error(request, "You cannot cancel this project as donations exceed 25% of the target.")
        return redirect('manage_projects')


