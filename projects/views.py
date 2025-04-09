from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from decimal import Decimal
from .forms import ProjectForm, DonationForm, CommentForm, ReportForm, RatingForm, CommentReportForm
from .models import Project, ProjectImage, Donation, Comment, Report, Rating, Tag, Category


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

            tag_input = request.POST.get('tags', '[]')  
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
        categories = Category.objects.all()
        return render(request, 'projects/projects_home.html', {'categories': categories})


class ProjectDetailView(View):
    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        donations = project.donations.all()
        total_donated = sum(donation.amount for donation in donations)
        comments = project.comments.all()
        remaining = project.target - total_donated
        similar_projects = Project.objects.filter(
        tags__in=project.tags.all()).exclude(id=project.id).distinct()[:4]



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
        similar_projects = Project.objects.filter(
            tags__in=project.tags.all()).exclude(id=project.id).distinct()[:4]
        donation_closed = total_donated >= project.target

        if donation_closed:
            messages.info(request, "Thank you, Donation for this project has been completed.")

        if 'donate' in request.POST and not donation_closed:
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
            # Check if the user has already rated this project
            if project.ratings.filter(user=request.user).exists():
                messages.error(request, "You have already rated this project.")
                return redirect('project_detail', project_id=project.id)

            rating_form = RatingForm(request.POST)
            if rating_form.is_valid():
                rating = rating_form.save(commit=False)
                rating.project = project
                rating.user = request.user
                rating.save()
                messages.success(request, "Your rating has been submitted.")
                return redirect('project_detail', project_id=project.id)
        elif 'report_comment' in request.POST:
            comment_id = request.POST.get('comment_id')
            comment = get_object_or_404(Comment, id=comment_id)

            # Check if the user has already reported this comment
            if comment.reports.filter(user=request.user).exists():
                messages.error(request, "You have already reported this comment.")
                return redirect('project_detail', project_id=project.id)

            report_form = CommentReportForm(request.POST)
            if report_form.is_valid():
                report = report_form.save(commit=False)
                report.comment = comment
                report.user = request.user
                report.save()
                messages.success(request, "Your report has been submitted.")
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

def projects_by_tag(request, tag_name):
    tag = Tag.objects.get(name=tag_name)
    projects = tag.projects.filter(cancelled=False)
    return render(request, 'projects/projects_by_tag.html', {'tag': tag, 'projects': projects})

def projects_by_category(request, category_name):
    category = Category.objects.get(name=category_name)
    projects = category.projects.filter(cancelled=False)
    return render(request, 'projects/projects_by_category.html', {'category': category, 'projects': projects})


class SearchProjectsView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        projects = Project.objects.filter(
            title__icontains=query
        ).distinct() | Project.objects.filter(
            tags__name__icontains=query
        ).distinct()
        return render(request, 'projects/search_results.html', {'projects': projects, 'query': query})


