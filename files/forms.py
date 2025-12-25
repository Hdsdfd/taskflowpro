from django import forms
from .models import ProjectFile

class ProjectFileForm(forms.ModelForm):
    """项目文件上传/编辑表单：控制可编辑字段与小部件"""
    class Meta:
        model = ProjectFile
        fields = ['name', 'original_name', 'file', 'file_type', 'project', 'task', 'category', 'description', 'tags', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入文件名'}),
            'original_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '原始文件名'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'file_type': forms.Select(attrs={'class': 'form-control'}),
            'project': forms.Select(attrs={'class': 'form-control'}),
            'task': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '文件描述'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '逗号分隔标签'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
