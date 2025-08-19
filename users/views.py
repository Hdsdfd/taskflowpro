from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, AdminApplyForm
from .models import UserProfile
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .forms import PasswordResetRequestForm, PasswordResetConfirmForm
from .models import PasswordResetCode
import random

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


def forgot_password_request_view(request):
    """
    第一步：输入邮箱，发送验证码（含频率限制）
    """
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)

            # 频率限制：60秒内只允许发送一次
            last_record = PasswordResetCode.objects.filter(user=user).order_by('-created_at').first()
            if last_record:
                interval_seconds = (timezone.now() - last_record.created_at).total_seconds()
                if interval_seconds < settings.PASSWORD_RESET_RESEND_INTERVAL_SECONDS:
                    remaining = int(settings.PASSWORD_RESET_RESEND_INTERVAL_SECONDS - interval_seconds)
                    messages.warning(request, f'发送过于频繁，请 {remaining} 秒后再试。')
                    request.session['password_reset_email'] = email
                    return redirect('users:forgot_password')

            # 每小时最多5次
            one_hour_ago = timezone.now() - timezone.timedelta(hours=1)
            count_last_hour = PasswordResetCode.objects.filter(user=user, created_at__gte=one_hour_ago).count()
            if count_last_hour >= settings.PASSWORD_RESET_MAX_PER_HOUR:
                messages.error(request, '该邮箱请求过于频繁，请稍后再试。')
                request.session['password_reset_email'] = email
                return redirect('users:forgot_password')

            # 生成6位数字验证码
            code = f"{random.randint(0, 999999):06d}"
            expires_at = timezone.now() + timezone.timedelta(minutes=settings.PASSWORD_RESET_CODE_EXPIRE_MINUTES)
            PasswordResetCode.objects.create(user=user, code=code, expires_at=expires_at)
            # 发送邮件
            send_mail(
                subject='TaskFlowPro 找回密码验证码',
                message=(
                    f'您的验证码为：{code}\n'
                    f'有效期：{settings.PASSWORD_RESET_CODE_EXPIRE_MINUTES}分钟。\n'
                    '若非本人操作请忽略本邮件。'
                ),
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                recipient_list=[email],
                fail_silently=False,
            )
            messages.success(request, '验证码已发送到邮箱，请在有效期内完成验证。')
            request.session['password_reset_email'] = email
            return redirect('users:forgot_password_confirm')
    else:
        initial_email = request.session.get('password_reset_email')
        form = PasswordResetRequestForm(initial={'email': initial_email} if initial_email else None)

    return render(request, 'users/password_forgot.html', {'form': form})


def forgot_password_confirm_view(request):
    """
    第二步：输入验证码并设置新密码
    """
    email = request.session.get('password_reset_email')
    user = None
    if email:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None
    
    if request.method == 'POST':
        if not user:
            messages.error(request, '会话已过期或邮箱无效，请重新请求验证码。')
            return redirect('users:forgot_password')
        form = PasswordResetConfirmForm(user, request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            # 验证验证码
            try:
                record = PasswordResetCode.objects.filter(user=user, code=code, is_used=False).latest('created_at')
            except PasswordResetCode.DoesNotExist:
                record = None
            if not record:
                messages.error(request, '验证码无效，请检查后重试。')
            elif record.is_expired:
                messages.error(request, '验证码已过期，请重新获取。')
            else:
                # 设置新密码
                form.save()
                # 标记验证码已使用，并清理同邮箱其他旧验证码
                record.is_used = True
                record.save()
                PasswordResetCode.objects.filter(user=user, is_used=False).update(is_used=True)
                # 清理session
                request.session.pop('password_reset_email', None)
                messages.success(request, '密码已重置，请使用新密码登录。')
                return redirect('users:login')
    else:
        if not user:
            messages.info(request, '请先输入邮箱获取验证码。')
            return redirect('users:forgot_password')
        form = PasswordResetConfirmForm(user)

    return render(request, 'users/password_reset_confirm.html', {'form': form, 'email': email})
