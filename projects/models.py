from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="projects")
    tags = models.ManyToManyField(Tag, blank=True, related_name="projects")
    start_date = models.DateField()
    end_date = models.DateField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    target = models.DecimalField(max_digits=10, decimal_places=2)
    raised = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.title

    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return sum(rating.value for rating in ratings) / ratings.count()
        return 0
    
    @property
    def progress_percentage(self):
        if self.target > 0:
            return round((self.raised / self.target) * 100, 2)
        return 0



class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="projects/images/")

    def __str__(self):
        return f"Image for {self.project.title}"

class Donation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='donations')
    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="donations")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    donated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor.email} donated {self.amount} to {self.project.title}"

class Comment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return f"Comment by {self.user.email} on {self.project.title}"

    @property
    def is_reply(self):
        return self.parent is not None

class CommentReport(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="reports")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comment_reports")
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.user.email} on comment {self.comment.id}"

class Report(models.Model):
    REASON_CHOICES = [
        ('inappropriate', 'Inappropriate Content'),
        ('fraud', 'Fraudulent Project'),
        ('duplicate', 'Duplicate Project'),
        ('other', 'Other Reason')
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="reports")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports")
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, default='other')
    details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    dismissed = models.BooleanField(default=False)

    def __str__(self):
        return f"Report by {self.user.email} on {self.project.title}"

class Rating(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings")
    value = models.PositiveSmallIntegerField()  # Rating value (e.g., 1-5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} rated {self.project.title} with {self.value}"


