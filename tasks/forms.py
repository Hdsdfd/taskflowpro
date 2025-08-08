from django import forms
from .models import Task
from projects.models import Project
from django.contrib.auth.models import User

class TaskForm(forms.ModelForm):
    """
    任务表单
    """
    class Meta:
        model = Task
        fields = ['title', 'description', 'project', 'assignee', 'priority', 'status', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入任务标题'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '请输入任务描述'
            }),
            'project': forms.Select(attrs={
                'class': 'form-control'
            }),
            'assignee': forms.Select(attrs={
                'class': 'form-control'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # 根据用户权限过滤项目
            if user.profile.is_admin:
                self.fields['project'].queryset = Project.objects.filter(is_active=True)
                # 管理员可选择所有激活用户为负责人
                self.fields['assignee'].queryset = User.objects.filter(is_active=True)
            else:
                self.fields['project'].queryset = Project.objects.filter(
                    is_active=True,
                    members=user
                )
                # 只显示与该用户相关项目的成员为负责人
                member_ids = Project.objects.filter(
                    is_active=True,
                    members=user
                ).values_list('members', flat=True)
                self.fields['assignee'].queryset = User.objects.filter(id__in=member_ids).distinct()
            # 设置负责人默认值为当前用户
            self.fields['assignee'].initial = user

class TaskFilterForm(forms.Form):
    """
    任务筛选表单
    """
    STATUS_CHOICES = [('', '全部状态')] + list(Task.STATUS_CHOICES)
    PRIORITY_CHOICES = [('', '全部优先级')] + list(Task.PRIORITY_CHOICES)
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    project = forms.ModelChoiceField(
        queryset=Project.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    assignee = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # 根据用户权限设置项目选项
            if user.profile.is_admin:
                self.fields['project'].queryset = Project.objects.filter(is_active=True)
            else:
                self.fields['project'].queryset = Project.objects.filter(
                    is_active=True,
                    members=user
                )
            
            # 设置负责人选项
            self.fields['assignee'].queryset = user.projects.all().distinct().values_list('members', flat=True) 