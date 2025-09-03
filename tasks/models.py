from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from projects.models import Project
from django.core.validators import MinValueValidator, MaxValueValidator

class TaskTag(models.Model):
    """
    任务标签模型
    """
    name = models.CharField(max_length=50, unique=True, verbose_name='标签名称')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='标签颜色')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '任务标签'
        verbose_name_plural = '任务标签'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Task(models.Model):
    """
    任务模型
    """
    PRIORITY_CHOICES = (
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
        ('urgent', '紧急'),
    )
    
    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('in_progress', '进行中'),
        ('review', '待审核'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    )
    
    title = models.CharField(max_length=200, verbose_name='任务标题')
    description = models.TextField(blank=True, verbose_name='任务描述')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', verbose_name='所属项目')
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks', verbose_name='负责人')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks', verbose_name='创建者')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name='优先级')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    due_date = models.DateTimeField(null=True, blank=True, verbose_name='截止日期')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    order = models.IntegerField(default=0, verbose_name='排序')
    
    # 新增高级功能字段
    parent_task = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subtasks', verbose_name='父任务')
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='预估工时(小时)')
    actual_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='实际工时(小时)')
    start_date = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    tags = models.ManyToManyField(TaskTag, blank=True, verbose_name='任务标签')
    progress = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='任务进度(%)'
    )
    complexity = models.CharField(
        max_length=10,
        choices=[
            ('simple', '简单'),
            ('medium', '中等'),
            ('complex', '复杂'),
            ('very_complex', '非常复杂'),
        ],
        default='medium',
        verbose_name='任务复杂度'
    )
    notes = models.TextField(blank=True, verbose_name='备注')
    
    class Meta:
        verbose_name = '任务'
        verbose_name_plural = '任务'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def is_overdue(self):
        """检查任务是否逾期"""
        if self.due_date and self.status not in ['completed', 'cancelled']:
            return timezone.now() > self.due_date
        return False
    
    @property
    def days_until_due(self):
        """距离截止日期的天数"""
        if self.due_date:
            delta = self.due_date - timezone.now()
            return delta.days
        return None
    
    @property
    def has_subtasks(self):
        """是否有子任务"""
        return self.subtasks.exists()
    
    @property
    def subtask_count(self):
        """子任务数量"""
        return self.subtasks.count()
    
    @property
    def completed_subtask_count(self):
        """已完成的子任务数量"""
        return self.subtasks.filter(status='completed').count()
    
    @property
    def time_variance(self):
        """工时偏差"""
        if self.estimated_hours and self.actual_hours:
            return self.actual_hours - self.estimated_hours
        return None
    
    def update_progress(self):
        """更新任务进度"""
        if self.has_subtasks:
            if self.subtask_count > 0:
                self.progress = int((self.completed_subtask_count / self.subtask_count) * 100)
            else:
                self.progress = 0
        self.save()

class TaskDependency(models.Model):
    """
    任务依赖关系模型
    """
    DEPENDENCY_TYPES = (
        ('finish_to_start', '完成-开始'),
        ('start_to_start', '开始-开始'),
        ('finish_to_finish', '完成-完成'),
        ('start_to_finish', '开始-完成'),
    )
    
    dependent_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='dependencies', verbose_name='依赖任务')
    prerequisite_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='dependent_on', verbose_name='前置任务')
    dependency_type = models.CharField(max_length=20, choices=DEPENDENCY_TYPES, default='finish_to_start', verbose_name='依赖类型')
    lag_days = models.IntegerField(default=0, verbose_name='延迟天数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '任务依赖'
        verbose_name_plural = '任务依赖'
        unique_together = ('dependent_task', 'prerequisite_task')
    
    def __str__(self):
        return f"{self.prerequisite_task.title} -> {self.dependent_task.title}"

class TimeEntry(models.Model):
    """
    工时记录模型
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='time_entries', verbose_name='任务')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_entries', verbose_name='用户')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    duration_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='工时(小时)')
    description = models.TextField(blank=True, verbose_name='工作描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '工时记录'
        verbose_name_plural = '工时记录'
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.task.title}"
    
    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            self.duration_hours = duration.total_seconds() / 3600
        super().save(*args, **kwargs)
