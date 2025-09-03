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
    
    # 新增甘特图相关字段
    start_date = models.DateField(null=True, blank=True, verbose_name='项目开始日期')
    end_date = models.DateField(null=True, blank=True, verbose_name='项目结束日期')
    progress = models.IntegerField(default=0, verbose_name='项目进度百分比')
    status = models.CharField(
        max_length=20,
        choices=[
            ('planning', '规划中'),
            ('active', '进行中'),
            ('on_hold', '暂停'),
            ('completed', '已完成'),
            ('cancelled', '已取消'),
        ],
        default='planning',
        verbose_name='项目状态'
    )
    priority = models.CharField(
        max_length=10,
        choices=[
            ('low', '低'),
            ('medium', '中'),
            ('high', '高'),
            ('urgent', '紧急'),
        ],
        default='medium',
        verbose_name='项目优先级'
    )
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='项目预算')
    actual_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='实际成本')
    
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
    
    @property
    def is_overdue(self):
        """检查项目是否逾期"""
        if self.end_date and self.status not in ['completed', 'cancelled']:
            return timezone.now().date() > self.end_date
        return False
    
    @property
    def days_remaining(self):
        """距离项目结束的天数"""
        if self.end_date:
            delta = self.end_date - timezone.now().date()
            return delta.days
        return None
    
    @property
    def cost_variance(self):
        """成本偏差"""
        if self.budget and self.actual_cost:
            return self.actual_cost - self.budget
        return None

class Milestone(models.Model):
    """
    项目里程碑模型
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones', verbose_name='项目')
    name = models.CharField(max_length=200, verbose_name='里程碑名称')
    description = models.TextField(blank=True, verbose_name='里程碑描述')
    due_date = models.DateField(verbose_name='截止日期')
    completed = models.BooleanField(default=False, verbose_name='是否完成')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '里程碑'
        verbose_name_plural = '里程碑'
        ordering = ['due_date']
    
    def __str__(self):
        return f"{self.project.name} - {self.name}"
    
    @property
    def is_overdue(self):
        """检查里程碑是否逾期"""
        if not self.completed:
            return timezone.now().date() > self.due_date
        return False

class ProjectTemplate(models.Model):
    """
    项目模板模型
    """
    name = models.CharField(max_length=200, verbose_name='模板名称')
    description = models.TextField(blank=True, verbose_name='模板描述')
    category = models.CharField(
        max_length=50,
        choices=[
            ('software', '软件开发'),
            ('marketing', '市场营销'),
            ('research', '研究项目'),
            ('construction', '建设工程'),
            ('event', '活动策划'),
            ('other', '其他'),
        ],
        default='other',
        verbose_name='模板类别'
    )
    is_public = models.BooleanField(default=False, verbose_name='是否公开')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '项目模板'
        verbose_name_plural = '项目模板'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
