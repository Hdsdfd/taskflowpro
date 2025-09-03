from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from projects.models import Project

class ThirdPartyService(models.Model):
    """
    第三方服务模型
    """
    SERVICE_TYPES = (
        ('git', 'Git仓库'),
        ('cloud_storage', '云存储'),
        ('communication', '通讯工具'),
        ('design', '设计工具'),
        ('testing', '测试工具'),
        ('monitoring', '监控工具'),
        ('other', '其他'),
    )
    
    name = models.CharField(max_length=100, verbose_name='服务名称')
    service_type = models.CharField(max_length=30, choices=SERVICE_TYPES, verbose_name='服务类型')
    description = models.TextField(blank=True, verbose_name='服务描述')
    
    # 连接信息
    base_url = models.URLField(verbose_name='服务地址')
    api_version = models.CharField(max_length=20, blank=True, verbose_name='API版本')
    documentation_url = models.URLField(blank=True, verbose_name='文档地址')
    
    # 认证信息
    auth_type = models.CharField(
        max_length=20,
        choices=[
            ('api_key', 'API密钥'),
            ('oauth2', 'OAuth 2.0'),
            ('basic', '基本认证'),
            ('token', '访问令牌'),
            ('none', '无需认证'),
        ],
        default='api_key',
        verbose_name='认证类型'
    )
    
    # 状态
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    is_public = models.BooleanField(default=False, verbose_name='是否公开')
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '第三方服务'
        verbose_name_plural = '第三方服务'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class ServiceConnection(models.Model):
    """
    服务连接模型
    """
    STATUS_CHOICES = (
        ('active', '活跃'),
        ('inactive', '非活跃'),
        ('error', '错误'),
        ('testing', '测试中'),
    )
    
    service = models.ForeignKey(ThirdPartyService, on_delete=models.CASCADE, related_name='connections', verbose_name='第三方服务')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='service_connections', verbose_name='关联项目')
    
    # 连接配置
    connection_name = models.CharField(max_length=100, verbose_name='连接名称')
    config = models.JSONField(verbose_name='连接配置')
    
    # 认证凭据
    credentials = models.JSONField(verbose_name='认证凭据')
    credentials_encrypted = models.BooleanField(default=True, verbose_name='凭据已加密')
    
    # 状态和监控
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive', verbose_name='连接状态')
    last_sync_at = models.DateTimeField(null=True, blank=True, verbose_name='最后同步时间')
    last_error_at = models.DateTimeField(null=True, blank=True, verbose_name='最后错误时间')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    
    # 同步设置
    auto_sync = models.BooleanField(default=False, verbose_name='自动同步')
    sync_interval_minutes = models.IntegerField(default=60, verbose_name='同步间隔(分钟)')
    
    # 权限
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建者')
    can_edit = models.ManyToManyField(User, blank=True, related_name='editable_connections', verbose_name='可编辑用户')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '服务连接'
        verbose_name_plural = '服务连接'
        unique_together = ('service', 'project', 'connection_name')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project.name} - {self.connection_name}"
    
    @property
    def is_healthy(self):
        """连接是否健康"""
        if self.last_error_at and self.last_sync_at:
            return self.last_error_at < self.last_sync_at
        return self.status == 'active'

class GitRepository(models.Model):
    """
    Git仓库模型
    """
    REPO_TYPES = (
        ('github', 'GitHub'),
        ('gitlab', 'GitLab'),
        ('bitbucket', 'Bitbucket'),
        ('gitee', 'Gitee'),
        ('other', '其他'),
    )
    
    name = models.CharField(max_length=200, verbose_name='仓库名称')
    repo_type = models.CharField(max_length=20, choices=REPO_TYPES, verbose_name='仓库类型')
    repo_url = models.URLField(verbose_name='仓库地址')
    
    # 项目关联
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='git_repository', verbose_name='关联项目')
    
    # 分支信息
    default_branch = models.CharField(max_length=100, default='main', verbose_name='默认分支')
    protected_branches = models.JSONField(default=list, verbose_name='受保护分支')
    
    # 连接信息
    connection = models.ForeignKey(ServiceConnection, on_delete=models.CASCADE, related_name='git_repositories', verbose_name='服务连接')
    
    # 同步设置
    auto_sync_commits = models.BooleanField(default=True, verbose_name='自动同步提交')
    auto_sync_issues = models.BooleanField(default=True, verbose_name='自动同步问题')
    auto_sync_pull_requests = models.BooleanField(default=True, verbose_name='自动同步拉取请求')
    
    # 统计信息
    total_commits = models.IntegerField(default=0, verbose_name='总提交数')
    total_issues = models.IntegerField(default=0, verbose_name='总问题数')
    total_pull_requests = models.IntegerField(default=0, verbose_name='总拉取请求数')
    
    # 状态
    last_sync_at = models.DateTimeField(null=True, blank=True, verbose_name='最后同步时间')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'Git仓库'
        verbose_name_plural = 'Git仓库'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class Webhook(models.Model):
    """
    Webhook模型
    """
    WEBHOOK_TYPES = (
        ('github', 'GitHub'),
        ('gitlab', 'GitLab'),
        ('slack', 'Slack'),
        ('discord', 'Discord'),
        ('teams', 'Microsoft Teams'),
        ('dingtalk', '钉钉'),
        ('feishu', '飞书'),
        ('custom', '自定义'),
    )
    
    name = models.CharField(max_length=100, verbose_name='Webhook名称')
    webhook_type = models.CharField(max_length=20, choices=WEBHOOK_TYPES, verbose_name='Webhook类型')
    url = models.URLField(verbose_name='Webhook地址')
    
    # 关联对象
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='webhooks', verbose_name='关联项目')
    service_connection = models.ForeignKey(ServiceConnection, on_delete=models.CASCADE, null=True, blank=True, related_name='webhooks', verbose_name='服务连接')
    
    # 触发事件
    events = models.JSONField(default=list, verbose_name='触发事件')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    
    # 安全设置
    secret_token = models.CharField(max_length=255, blank=True, verbose_name='密钥令牌')
    verify_ssl = models.BooleanField(default=True, verbose_name='验证SSL')
    
    # 统计信息
    total_requests = models.IntegerField(default=0, verbose_name='总请求数')
    successful_requests = models.IntegerField(default=0, verbose_name='成功请求数')
    failed_requests = models.IntegerField(default=0, verbose_name='失败请求数')
    
    # 状态
    last_triggered_at = models.DateTimeField(null=True, blank=True, verbose_name='最后触发时间')
    last_error_at = models.DateTimeField(null=True, blank=True, verbose_name='最后错误时间')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'Webhook'
        verbose_name_plural = 'Webhook'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def success_rate(self):
        """成功率"""
        if self.total_requests > 0:
            return round((self.successful_requests / self.total_requests) * 100, 2)
        return 0

class DataSync(models.Model):
    """
    数据同步模型
    """
    SYNC_TYPES = (
        ('import', '导入'),
        ('export', '导出'),
        ('bidirectional', '双向'),
    )
    
    SYNC_STATUS = (
        ('pending', '等待中'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('cancelled', '已取消'),
    )
    
    name = models.CharField(max_length=200, verbose_name='同步名称')
    sync_type = models.CharField(max_length=20, choices=SYNC_TYPES, verbose_name='同步类型')
    
    # 源和目标
    source_connection = models.ForeignKey(ServiceConnection, on_delete=models.CASCADE, related_name='source_syncs', verbose_name='源连接')
    target_connection = models.ForeignKey(ServiceConnection, on_delete=models.CASCADE, related_name='target_syncs', verbose_name='目标连接')
    
    # 同步配置
    data_mapping = models.JSONField(verbose_name='数据映射')
    sync_schedule = models.CharField(max_length=100, blank=True, verbose_name='同步计划')
    
    # 状态
    status = models.CharField(max_length=20, choices=SYNC_STATUS, default='pending', verbose_name='同步状态')
    progress = models.IntegerField(default=0, verbose_name='同步进度(%)')
    
    # 统计信息
    total_items = models.IntegerField(default=0, verbose_name='总项目数')
    synced_items = models.IntegerField(default=0, verbose_name='已同步项目数')
    failed_items = models.IntegerField(default=0, verbose_name='失败项目数')
    
    # 时间信息
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    last_sync_at = models.DateTimeField(null=True, blank=True, verbose_name='最后同步时间')
    
    # 错误信息
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '数据同步'
        verbose_name_plural = '数据同步'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def duration(self):
        """同步持续时间"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        elif self.started_at:
            return timezone.now() - self.started_at
        return None
