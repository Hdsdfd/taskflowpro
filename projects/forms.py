from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    """
    项目表单
    """
    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入项目名称'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '请输入项目描述'
            }),
        } 