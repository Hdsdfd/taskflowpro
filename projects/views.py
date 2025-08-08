from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Project
from .forms import ProjectForm

class ProjectListView(LoginRequiredMixin, ListView):
    """
    项目列表视图
    """
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 10
    
    def get_queryset(self):
        """获取用户可见的项目"""
        user = self.request.user
        if user.profile.is_admin:
            return Project.objects.filter(is_active=True)
        else:
            return Project.objects.filter(
                is_active=True,
                members=user
            ).distinct()

@login_required
def project_list_view(request):
    """
    项目列表视图（函数视图版本）
    """
    user = request.user
    if user.profile.is_admin:
        projects = Project.objects.filter(is_active=True)
    else:
        projects = Project.objects.filter(
            is_active=True,
            members=user
        ).distinct()
    
    context = {
        'projects': projects,
        'user': user,
    }
    return render(request, 'projects/project_list.html', context)

class ProjectDetailView(LoginRequiredMixin, DetailView):
    """
    项目详情视图
    """
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'
    
    def get_queryset(self):
        """确保用户有权限查看项目"""
        user = self.request.user
        if user.profile.is_admin:
            return Project.objects.filter(is_active=True)
        else:
            return Project.objects.filter(
                is_active=True,
                members=user
            )

class ProjectCreateView(LoginRequiredMixin, CreateView):
    """
    创建项目视图
    """
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('projects:project_list')
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)  # 先保存，获取主键
        self.object.members.add(self.request.user)  # 再添加成员
        messages.success(self.request, '项目创建成功！')
        return response

class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    编辑项目视图
    """
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    
    def test_func(self):
        """检查用户是否有权限编辑项目"""
        project = self.get_object()
        user = self.request.user
        return user.profile.is_admin or project.owner == user
    
    def get_success_url(self):
        return reverse_lazy('projects:project_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, '项目更新成功！')
        return super().form_valid(form)

class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    删除项目视图
    """
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('projects:project_list')
    
    def test_func(self):
        """检查用户是否有权限删除项目"""
        project = self.get_object()
        user = self.request.user
        return user.profile.is_admin or project.owner == user
    
    def delete(self, request, *args, **kwargs):
        """软删除项目"""
        project = self.get_object()
        project.is_active = False
        project.save()
        messages.success(request, '项目删除成功！')
        return redirect(self.success_url)
