from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Sum
from decimal import Decimal
from .forms import (
    ProjectForm,
    DonationForm,
    CommentForm,
    ReportForm,
    RatingForm,
    CommentReportForm,
)
from .models import (
    Project,
    ProjectImage,
    Donation,
    Comment,
    Report,
    Rating,
    Tag,
    Category,
)
from django.views.generic import ListView
from django.contrib.auth import logout
from django.contrib.contenttypes.models import ContentType
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.conf import settings

# Find and delete the duplicate entry
ContentType.objects.filter(app_label="projects", model="project").delete()


class CreateProjectView(LoginRequiredMixin, View):
    def get(self, request):
        form = ProjectForm()
        categoties = Category.objects.all()
        return render(request, "projects/create_project.html", {"form": form,'categories': categoties})

    def post(self, request):
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()

            tag_input = request.POST.get("tags", "[]")
            import json

            try:
                tag_data = json.loads(tag_input)
                for tag_item in tag_data:
                    tag_name = tag_item["value"].strip()
                    if tag_name:
                        tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                        project.tags.add(tag_obj)
            except json.JSONDecodeError:
                pass

            for image in request.FILES.getlist("images"):
                ProjectImage.objects.create(project=project, image=image)
            return redirect("home")
        return render(request, "projects/create_project.html", {"form": form})


class ProjectDetailView(View):
    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        donations = project.donations.all()
        total_donated = sum(donation.amount for donation in donations)
        comments = project.comments.all()
        categories = Category.objects.all()
        remaining = project.target - total_donated
        similar_projects = (
            Project.objects.filter(tags__in=project.tags.all())
            .exclude(id=project.id)
            .distinct()[:4]
        )

        form = DonationForm()
        comment_form = CommentForm()
        rating_form = RatingForm()

        donation_closed = (
            total_donated >= project.target
        )  # Check if the target is reached

        return render(
            request,
            "projects/project_detail.html",
            {
                "project": project,
                "form": form,
                "comment_form": comment_form,
                "rating_form": rating_form,
                "donations": donations,
                "comments": comments,
                "total_donated": total_donated,
                "remaining": remaining,
                "similar_projects": similar_projects,
                "average_rating": project.average_rating(),
                "donation_closed": donation_closed,
                "categories": categories,
            },
        )

    @method_decorator(login_required)
    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        donations = project.donations.all()
        total_donated = sum(donation.amount for donation in donations)
        remaining = project.target - total_donated
        similar_projects = (
            Project.objects.filter(tags__in=project.tags.all())
            .exclude(id=project.id)
            .distinct()[:4]
        )
        donation_closed = total_donated >= project.target

        if donation_closed:
            messages.info(
                request, "Thank you, Donation for this project has been completed."
            )

        if "donate" in request.POST and not donation_closed:
            form = DonationForm(request.POST)
            if form.is_valid():
                donation_amount = form.cleaned_data["amount"]
                if donation_amount > remaining:
                    messages.error(
                        request, "Donation amount exceeds the remaining target."
                    )
                    return redirect("project_detail", project_id=project.id)
                donation = form.save(commit=False)
                donation.project = project
                donation.donor = request.user
                donation.save()
                return redirect("project_detail", project_id=project.id)
        elif "comment" in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.project = project
                comment.user = request.user
                comment.save()
                return redirect("project_detail", project_id=project.id)
        elif "reply" in request.POST:
            parent_id = request.POST.get('parent_id')
            content = request.POST.get('content')
            if parent_id and content:
                parent_comment = get_object_or_404(Comment, id=parent_id)
                reply = Comment.objects.create(
                    project=project,
                    user=request.user,
                    content=content,
                    parent=parent_comment
                )
                return redirect("project_detail", project_id=project.id)
        elif "rate" in request.POST:
            # Check if the user has already rated this project
            if project.ratings.filter(user=request.user).exists():
                messages.error(request, "You have already rated this project.")
                return redirect("project_detail", project_id=project.id)

            rating_form = RatingForm(request.POST)
            if rating_form.is_valid():
                rating = rating_form.save(commit=False)
                rating.project = project
                rating.user = request.user
                rating.save()
                messages.success(request, "Your rating has been submitted.")
                return redirect("project_detail", project_id=project.id)
        elif "report_comment" in request.POST:
            comment_id = request.POST.get("comment_id")
            comment = get_object_or_404(Comment, id=comment_id)

            # Check if the user has already reported this comment
            if comment.reports.filter(user=request.user).exists():
                messages.error(request, "You have already reported this comment.")
                return redirect("project_detail", project_id=project.id)

            report_form = CommentReportForm(request.POST)
            if report_form.is_valid():
                report = report_form.save(commit=False)
                report.comment = comment
                report.user = request.user
                report.save()
                messages.success(request, "Your report has been submitted.")
                return redirect("project_detail", project_id=project.id)

        return self.get(request, project_id)


class ReportProjectView(LoginRequiredMixin, View):
    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        form = ReportForm()
        categoties = Category.objects.all()

        previous_reports = (
            project.reports.all() if request.user == project.created_by else None
        )
        return render(
            request,
            "projects/report_project.html",
            {
                "form": form,
                "project": project,
                "previous_reports": previous_reports,
                "categories": categoties,
            },
        )

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        print(request.POST)  # Log POST data for debugging
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.project = project
            report.user = request.user
            report.save()
            messages.success(request, "Your report has been submitted.")
        else:
            print(form.errors)  # Log form errors for debugging
            messages.error(request, "There was an error submitting your report.")
        return redirect("project_detail", project_id=project.id)


class CancelProjectView(LoginRequiredMixin, View):
    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id, created_by=request.user)
        categoties = Category.objects.all()
        return render(request, "projects/cancel_project.html", {"project": project, "categories": categoties})
    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id, created_by=request.user)
        
        total_donated = sum(donation.amount for donation in project.donations.all())
        if total_donated < (Decimal("0.25") * project.target):
            project.cancelled = True
            project.save()
            messages.success(request, "Project has been successfully canceled.")
        else:
            messages.error(
                request,
                "You cannot cancel this project as donations exceed 25% of the target.",
            )
        return redirect("project_detail", project_id=project.id)


class ProjectsByTagView(View):
    def get(self, request, tag_name):
        tag = get_object_or_404(Tag, name=tag_name)
        projects = tag.projects.filter(cancelled=False)
        categoties = Category.objects.all()

        return render(
            request, "projects/projects_by_tag.html", {"tag": tag, "projects": projects, "categories": categoties}
        )


class ProjectsByCategoryView(View):
    def get(self, request, category_name):
        category = get_object_or_404(Category, name=category_name)
        categories = Category.objects.all()
        projects = category.projects.filter(cancelled=False)
        return render(
            request,
            "projects/projects_by_category.html",
            {"category": category, "projects": projects, "categories": categories},
        )


class SearchProjectsView(View):
    def get(self, request):
        query = request.GET.get("q", "")
        categoties = Category.objects.all()

        projects = (
            Project.objects.filter(title__icontains=query).distinct()
            | Project.objects.filter(tags__name__icontains=query).distinct()
        )
        return render(
            request,
            "projects/search_results.html",
            {"projects": projects, "query": query, "categories": categoties},
        )


# New view for the home page
class HomeView(View):
    def get(self, request):
        categories = Category.objects.all()
        projects = Project.objects.filter(cancelled=False)
        all_projects = projects
        top_rated_projects = sorted(
            projects, key=lambda p: p.average_rating(), reverse=True
        )[:5]
        latest_projects = projects.order_by("-created_at")[:5]
        featured_projects = projects.filter(is_featured=True)[:5]

        # Calculate funded amount and progress for all project lists
        for project_list in [latest_projects, top_rated_projects, featured_projects, all_projects]:
            for project in project_list:
                project.funded_amount = project.donations.aggregate(Sum("amount"))["amount__sum"] or 0
                # Calculate progress percentage using a regular attribute name
                project.progress = round((project.funded_amount / project.target * 100), 2) if project.target > 0 else 0

        return render(
            request,
            "home.html",
            {
                "categories": categories,
                "top_rated_projects": top_rated_projects,
                "latest_projects": latest_projects,
                "all_projects": all_projects,
                "featured_projects": featured_projects,
            },
        )


class ReportCommentView(LoginRequiredMixin, View):
    def get(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        form = CommentReportForm()
        categoties = Category.objects.all()

        return render(
            request,
            "projects/report_comment.html",
            {
                "form": form,
                "comment": comment,
                "categories": categoties,
            },
        )

    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)

        # Check if the user has already reported this comment
        if comment.reports.filter(user=request.user).exists():
            messages.error(request, "You have already reported this comment.")
            return redirect("project_detail", project_id=comment.project.id)

        form = CommentReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.comment = comment
            report.user = request.user
            report.save()
            messages.success(request, "Your report has been submitted.")
            return redirect("project_detail", project_id=comment.project.id)
        return render(
            request,
            "projects/report_comment.html",
            {
                "form": form,
                "comment": comment,
            },
        )


def custom_logout_view(request):
    logout(request)
    return redirect("sign_in")  # Redirect to the sign-in page after logout











