from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from projects.models import Project

class Task(models.Model):
    """
    任务模型
    """
    PRIORITY_CHOICES = (
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
    )
    
    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
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
    
    class Meta:
        verbose_name = '任务'
        verbose_name_plural = '任务'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def is_overdue(self):
        """检查任务是否逾期"""
        if self.due_date and self.status != 'completed':
            return timezone.now() > self.due_date
        return False
    
    @property
    def days_until_due(self):
        """距离截止日期的天数"""
        if self.due_date:
            delta = self.due_date - timezone.now()
            return delta.days
        return None
