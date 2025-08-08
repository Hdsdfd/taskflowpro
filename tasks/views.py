from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q
from .models import Task
from .forms import TaskForm, TaskFilterForm
from projects.models import Project

class TaskListView(LoginRequiredMixin, ListView):
    """
    任务列表视图
    """
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 15
    
    def get_queryset(self):
        """获取用户可见的任务"""
        user = self.request.user
        queryset = Task.objects.select_related('project', 'assignee', 'creator')
        
        # 根据用户权限过滤
        if not user.profile.is_admin:
            queryset = queryset.filter(
                Q(project__members=user) | Q(assignee=user) | Q(creator=user)
            ).distinct()
        
        # 应用筛选条件
        form = TaskFilterForm(self.request.GET, user=user)
        if form.is_valid():
            if form.cleaned_data.get('status'):
                queryset = queryset.filter(status=form.cleaned_data['status'])
            if form.cleaned_data.get('priority'):
                queryset = queryset.filter(priority=form.cleaned_data['priority'])
            if form.cleaned_data.get('project'):
                queryset = queryset.filter(project=form.cleaned_data['project'])
            if form.cleaned_data.get('assignee'):
                queryset = queryset.filter(assignee=form.cleaned_data['assignee'])
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = TaskFilterForm(self.request.GET, user=self.request.user)
        return context

@login_required
def task_list_view(request):
    """
    任务列表视图（函数视图版本）
    """
    user = request.user
    queryset = Task.objects.select_related('project', 'assignee', 'creator')
    
    # 根据用户权限过滤
    if not user.profile.is_admin:
        queryset = queryset.filter(
            Q(project__members=user) | Q(assignee=user) | Q(creator=user)
        ).distinct()
    
    # 应用筛选条件
    filter_form = TaskFilterForm(request.GET, user=user)
    if filter_form.is_valid():
        if filter_form.cleaned_data.get('status'):
            queryset = queryset.filter(status=filter_form.cleaned_data['status'])
        if filter_form.cleaned_data.get('priority'):
            queryset = queryset.filter(priority=filter_form.cleaned_data['priority'])
        if filter_form.cleaned_data.get('project'):
            queryset = queryset.filter(project=filter_form.cleaned_data['project'])
        if filter_form.cleaned_data.get('assignee'):
            queryset = queryset.filter(assignee=filter_form.cleaned_data['assignee'])
    
    context = {
        'tasks': queryset,
        'filter_form': filter_form,
        'user': user,
    }
    return render(request, 'tasks/task_list.html', context)

class TaskDetailView(LoginRequiredMixin, DetailView):
    """
    任务详情视图
    """
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'
    
    def get_queryset(self):
        """确保用户有权限查看任务"""
        user = self.request.user
        if user.profile.is_admin:
            return Task.objects.select_related('project', 'assignee', 'creator')
        else:
            return Task.objects.filter(
                Q(project__members=user) | Q(assignee=user) | Q(creator=user)
            ).select_related('project', 'assignee', 'creator')

class TaskCreateView(LoginRequiredMixin, CreateView):
    """
    创建任务视图
    """
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:task_list')
    
    def get_form_kwargs(self):
        """传递用户信息给表单"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """设置任务创建者为当前用户"""
        form.instance.creator = self.request.user
        messages.success(self.request, '任务创建成功！')
        return super().form_valid(form)
    
    def get_initial(self):
        """设置初始值"""
        initial = super().get_initial()
        project_id = self.request.GET.get('project')
        if project_id:
            try:
                project = Project.objects.get(id=project_id)
                initial['project'] = project
            except Project.DoesNotExist:
                pass
        return initial

class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    编辑任务视图
    """
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    
    def get_form_kwargs(self):
        """传递用户信息给表单"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def test_func(self):
        """检查用户是否有权限编辑任务"""
        task = self.get_object()
        user = self.request.user
        return user.profile.is_admin or task.creator == user or task.assignee == user
    
    def get_success_url(self):
        return reverse_lazy('tasks:task_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, '任务更新成功！')
        return super().form_valid(form)

class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    删除任务视图
    """
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks:task_list')
    
    def test_func(self):
        """检查用户是否有权限删除任务"""
        task = self.get_object()
        user = self.request.user
        return user.profile.is_admin or task.creator == user
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '任务删除成功！')
        return super().delete(request, *args, **kwargs)

@login_required
def update_task_status(request, pk):
    """
    AJAX 更新任务状态
    """
    if request.method == 'POST':
        task = get_object_or_404(Task, pk=pk)
        
        # 检查权限
        user = request.user
        if not (user.profile.is_admin or task.creator == user or task.assignee == user):
            return JsonResponse({'success': False, 'message': '权限不足'})
        
        new_status = request.POST.get('status')
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            task.save()
            return JsonResponse({
                'success': True, 
                'message': '状态更新成功',
                'status': task.get_status_display()
            })
        else:
            return JsonResponse({'success': False, 'message': '无效的状态值'})
    
    return JsonResponse({'success': False, 'message': '请求方法不允许'})

@login_required
def update_task_order(request):
    """
    AJAX 更新任务排序
    """
    if request.method == 'POST':
        task_ids = request.POST.getlist('task_ids[]')
        user = request.user
        
        # 检查权限
        if not user.profile.is_admin:
            return JsonResponse({'success': False, 'message': '权限不足'})
        
        try:
            for index, task_id in enumerate(task_ids):
                task = Task.objects.get(id=task_id)
                task.order = index
                task.save()
            
            return JsonResponse({'success': True, 'message': '排序更新成功'})
        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'message': '任务不存在'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '请求方法不允许'})
