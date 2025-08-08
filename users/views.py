from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, AdminApplyForm
from .models import UserProfile

def register_view(request):
    """
    用户注册视图
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '注册成功！欢迎使用 TaskFlowPro')
            return redirect('projects:project_list')
        else:
            messages.error(request, '注册失败，请检查输入信息')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    """
    用户登录视图
    """
    if request.user.is_authenticated:
        return redirect('projects:project_list')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'欢迎回来，{username}！')
                return redirect('projects:project_list')
        else:
            messages.error(request, '用户名或密码错误')
    else:
        form = UserLoginForm()
    
    return render(request, 'users/login.html', {'form': form})

@login_required
def logout_view(request):
    """
    用户注销视图
    """
    logout(request)
    messages.info(request, '您已成功注销')
    return redirect('users:login')

@login_required
def profile_view(request):
    """
    用户个人资料视图
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, '个人资料更新成功')
            return redirect('users:profile')
        else:
            messages.error(request, '更新失败，请检查输入信息')
    else:
        form = UserProfileForm(instance=request.user.profile)
    
    return render(request, 'users/profile.html', {'form': form})

@login_required
def dashboard_view(request):
    """
    用户仪表板视图
    """
    user = request.user
    context = {
        'user': user,
        'total_projects': user.projects.count() if hasattr(user, 'projects') else 0,
        'total_tasks': user.tasks.count() if hasattr(user, 'tasks') else 0,
    }
    return render(request, 'users/dashboard.html', context)

@login_required
def apply_admin_view(request):
    if request.method == 'POST':
        form = AdminApplyForm(request.POST)
        if form.is_valid():
            answer = form.cleaned_data['answer'].strip()
            # 假设正确答案是“张三”
            if answer == '张三':
                request.user.profile.role = 'admin'
                request.user.profile.save()
                messages.success(request, '恭喜你，已成为管理员！')
                return redirect('users:dashboard')
            else:
                messages.error(request, '答案错误，无法成为管理员。')
    else:
        form = AdminApplyForm()
    return render(request, 'users/apply_admin.html', {'form': form})
