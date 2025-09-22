from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from .models import ProjectFile
from .forms import ProjectFileForm

class ProjectFileListView(LoginRequiredMixin, ListView):
    """文件列表视图：按用户权限过滤可见文件"""
    model = ProjectFile
    template_name = 'files/file_list.html'
    context_object_name = 'files'

    def get_queryset(self):
        # 管理员/staff 查看全部文件，普通用户仅能查看自己参与项目下的文件
        user = self.request.user
        if user.is_staff:
            return ProjectFile.objects.all()
        return ProjectFile.objects.filter(project__members=user).order_by('-uploaded_at')

class ProjectFileDetailView(LoginRequiredMixin, DetailView):
    """文件详情视图：模板变量名为 file"""
    model = ProjectFile
    template_name = 'files/file_detail.html'
    context_object_name = 'file'

class ProjectFileCreateView(LoginRequiredMixin, CreateView):
    """文件上传视图：使用 ModelForm 处理文件与关联信息"""
    model = ProjectFile
    form_class = ProjectFileForm
    template_name = 'files/file_form.html'
    success_url = reverse_lazy('files:file_list')  

    def form_valid(self, form):
        # 记录上传者；file_size/mime_type 在模型 save 中自动补全
        form.instance.uploaded_by = self.request.user
        return super().form_valid(form)
