from django import forms
from .models import Project
from .models import Donation

class ProjectForm(forms.ModelForm):
    files = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        required=False
    )

    class Meta:
        model = Project
        fields = ['title', 'description', 'category', 'images', 'target', 'tags', 'start_date', 'end_date', 'files']  # Include 'files' field
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter project title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Enter project description'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'images': forms.ClearableFileInput(attrs={'multiple': True}),
            'target': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': 'Enter target amount'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter tags separated by commas'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': 'Enter donation amount'}),
        }
