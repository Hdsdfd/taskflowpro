from django import forms
from .models import ProjectFile

class ProjectFileForm(forms.ModelForm):
    class Meta:
        model = ProjectFile
        fields = ['name', 'original_name', 'file', 'file_type', 'project', 'task', 'category', 'description', 'tags', 'is_public']
