from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Project(models.Model):
    """
    项目模型
    """
    name = models.CharField(max_length=200, verbose_name='项目名称')
    description = models.TextField(blank=True, verbose_name='项目描述')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects', verbose_name='项目负责人')
    members = models.ManyToManyField(User, related_name='projects', blank=True, verbose_name='项目成员')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    
    class Meta:
        verbose_name = '项目'
        verbose_name_plural = '项目'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def task_count(self):
        """获取项目任务数量"""
        return self.tasks.count()
    
    @property
    def completed_task_count(self):
        """获取已完成任务数量"""
        return self.tasks.filter(status='completed').count()
    
    @property
    def progress_percentage(self):
        """获取项目进度百分比"""
        if self.task_count == 0:
            return 0
        return int((self.completed_task_count / self.task_count) * 100)
