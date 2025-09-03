from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from projects.models import Project
from tasks.models import Task
from django.db.models import Sum, Count, Avg, Q
from datetime import timedelta

class ProjectReport(models.Model):
    """
    项目报告模型
    """
    REPORT_TYPES = (
        ('progress', '进度报告'),
        ('performance', '绩效报告'),
        ('resource', '资源报告'),
        ('timeline', '时间线报告'),
        ('cost', '成本报告'),
        ('quality', '质量报告'),
    )
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reports', verbose_name='项目')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, verbose_name='报告类型')
    title = models.CharField(max_length=255, verbose_name='报告标题')
    content = models.JSONField(verbose_name='报告内容')
    
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='生成者')
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name='生成时间')
    period_start = models.DateField(verbose_name='统计开始日期')
    period_end = models.DateField(verbose_name='统计结束日期')
    
    class Meta:
        verbose_name = '项目报告'
        verbose_name_plural = '项目报告'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.project.name} - {self.get_report_type_display()}"

class TeamPerformance(models.Model):
    """
    团队绩效模型
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performance_records', verbose_name='用户')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='team_performance', verbose_name='项目')
    
    # 任务统计
    total_tasks = models.IntegerField(default=0, verbose_name='总任务数')
    completed_tasks = models.IntegerField(default=0, verbose_name='完成任务数')
    overdue_tasks = models.IntegerField(default=0, verbose_name='逾期任务数')
    
    # 工时统计
    estimated_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='预估工时')
    actual_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='实际工时')
    
    # 质量指标
    task_completion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='任务完成率(%)')
    on_time_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='按时完成率(%)')
    
    # 时间范围
    period_start = models.DateField(verbose_name='统计开始日期')
    period_end = models.DateField(verbose_name='统计结束日期')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '团队绩效'
        verbose_name_plural = '团队绩效'
        unique_together = ('user', 'project', 'period_start', 'period_end')
        ordering = ['-period_end', '-task_completion_rate']
    
    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.period_start} 至 {self.period_end})"
    
    @property
    def efficiency_rate(self):
        """效率比率（预估工时/实际工时）"""
        if self.actual_hours > 0:
            return round((self.estimated_hours / self.actual_hours) * 100, 2)
        return 0
    
    @property
    def time_variance(self):
        """工时偏差"""
        return self.actual_hours - self.estimated_hours

class DashboardWidget(models.Model):
    """
    仪表板组件模型
    """
    WIDGET_TYPES = (
        ('chart', '图表'),
        ('metric', '指标'),
        ('table', '表格'),
        ('list', '列表'),
        ('progress', '进度条'),
    )
    
    name = models.CharField(max_length=100, verbose_name='组件名称')
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES, verbose_name='组件类型')
    config = models.JSONField(verbose_name='组件配置')
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboard_widgets', verbose_name='用户')
    position = models.IntegerField(default=0, verbose_name='位置排序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '仪表板组件'
        verbose_name_plural = '仪表板组件'
        ordering = ['user', 'position']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"

class DataExport(models.Model):
    """
    数据导出模型
    """
    EXPORT_FORMATS = (
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
        ('json', 'JSON'),
    )
    
    EXPORT_TYPES = (
        ('project_summary', '项目汇总'),
        ('task_details', '任务详情'),
        ('team_performance', '团队绩效'),
        ('time_tracking', '工时统计'),
        ('custom_report', '自定义报告'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='data_exports', verbose_name='用户')
    export_type = models.CharField(max_length=30, choices=EXPORT_TYPES, verbose_name='导出类型')
    export_format = models.CharField(max_length=10, choices=EXPORT_FORMATS, verbose_name='导出格式')
    
    file_path = models.CharField(max_length=500, blank=True, verbose_name='文件路径')
    file_size = models.BigIntegerField(null=True, blank=True, verbose_name='文件大小(字节)')
    
    filters = models.JSONField(default=dict, verbose_name='导出筛选条件')
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', '等待中'),
            ('processing', '处理中'),
            ('completed', '已完成'),
            ('failed', '失败'),
        ],
        default='pending',
        verbose_name='导出状态'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    
    class Meta:
        verbose_name = '数据导出'
        verbose_name_plural = '数据导出'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_export_type_display()} ({self.get_export_format_display()})"
    
    @property
    def processing_time(self):
        """处理时间（秒）"""
        if self.completed_at:
            delta = self.completed_at - self.created_at
            return delta.total_seconds()
        return None

class AnalyticsCache(models.Model):
    """
    分析数据缓存模型
    """
    cache_key = models.CharField(max_length=255, unique=True, verbose_name='缓存键')
    cache_data = models.JSONField(verbose_name='缓存数据')
    expires_at = models.DateTimeField(verbose_name='过期时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '分析缓存'
        verbose_name_plural = '分析缓存'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['cache_key', 'expires_at']),
        ]
    
    def __str__(self):
        return f"{self.cache_key} (过期: {self.expires_at})"
    
    @property
    def is_expired(self):
        """是否已过期"""
        return timezone.now() > self.expires_at
