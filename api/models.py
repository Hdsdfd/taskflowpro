from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class APIToken(models.Model):
    """
    API令牌模型
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_tokens', verbose_name='用户')
    name = models.CharField(max_length=100, verbose_name='令牌名称')
    key = models.CharField(max_length=64, unique=True, verbose_name='令牌密钥')
    
    # 权限设置
    permissions = models.JSONField(default=list, verbose_name='权限列表')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    
    # 使用限制
    rate_limit = models.IntegerField(default=1000, verbose_name='速率限制(次/小时)')
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='过期时间')
    
    # 使用统计
    last_used_at = models.DateTimeField(null=True, blank=True, verbose_name='最后使用时间')
    usage_count = models.IntegerField(default=0, verbose_name='使用次数')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'API令牌'
        verbose_name_plural = 'API令牌'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    @property
    def is_expired(self):
        """是否已过期"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

class APIRequestLog(models.Model):
    """
    API请求日志模型
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='api_requests', verbose_name='用户')
    token = models.ForeignKey(APIToken, on_delete=models.SET_NULL, null=True, blank=True, related_name='request_logs', verbose_name='API令牌')
    
    # 请求信息
    method = models.CharField(max_length=10, verbose_name='HTTP方法')
    endpoint = models.CharField(max_length=500, verbose_name='请求端点')
    query_params = models.JSONField(default=dict, verbose_name='查询参数')
    request_body = models.TextField(blank=True, verbose_name='请求体')
    
    # 响应信息
    status_code = models.IntegerField(verbose_name='状态码')
    response_time = models.FloatField(verbose_name='响应时间(毫秒)')
    
    # 客户端信息
    ip_address = models.GenericIPAddressField(verbose_name='IP地址')
    user_agent = models.TextField(blank=True, verbose_name='用户代理')
    
    # 错误信息
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = 'API请求日志'
        verbose_name_plural = 'API请求日志'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['token', 'created_at']),
            models.Index(fields=['status_code', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code}"

class MobileDevice(models.Model):
    """
    移动设备模型
    """
    DEVICE_TYPES = (
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('web', 'Web'),
        ('desktop', 'Desktop'),
        ('other', '其他'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mobile_devices', verbose_name='用户')
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES, verbose_name='设备类型')
    
    # 设备信息
    device_id = models.CharField(max_length=255, unique=True, verbose_name='设备ID')
    device_name = models.CharField(max_length=200, verbose_name='设备名称')
    device_model = models.CharField(max_length=200, blank=True, verbose_name='设备型号')
    os_version = models.CharField(max_length=50, blank=True, verbose_name='操作系统版本')
    app_version = models.CharField(max_length=50, blank=True, verbose_name='应用版本')
    
    # 推送设置
    push_token = models.CharField(max_length=500, blank=True, verbose_name='推送令牌')
    push_enabled = models.BooleanField(default=True, verbose_name='启用推送')
    
    # 状态
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    last_seen = models.DateTimeField(auto_now=True, verbose_name='最后活跃时间')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '移动设备'
        verbose_name_plural = '移动设备'
        ordering = ['-last_seen']
        unique_together = ('user', 'device_id')
    
    def __str__(self):
        return f"{self.user.username} - {self.device_name}"

class PushNotification(models.Model):
    """
    推送通知模型
    """
    NOTIFICATION_TYPES = (
        ('task_assigned', '任务分配'),
        ('task_due', '任务到期'),
        ('project_update', '项目更新'),
        ('comment_added', '新增评论'),
        ('meeting_reminder', '会议提醒'),
        ('system_alert', '系统提醒'),
    )
    
    PRIORITY_CHOICES = (
        ('low', '低'),
        ('normal', '普通'),
        ('high', '高'),
        ('urgent', '紧急'),
    )
    
    title = models.CharField(max_length=200, verbose_name='通知标题')
    message = models.TextField(verbose_name='通知内容')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES, verbose_name='通知类型')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal', verbose_name='优先级')
    
    # 目标用户
    recipients = models.ManyToManyField(User, related_name='push_notifications', verbose_name='接收者')
    
    # 推送设置
    send_immediately = models.BooleanField(default=True, verbose_name='立即发送')
    scheduled_at = models.DateTimeField(null=True, blank=True, verbose_name='计划发送时间')
    
    # 状态
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', '等待中'),
            ('sending', '发送中'),
            ('sent', '已发送'),
            ('failed', '发送失败'),
            ('cancelled', '已取消'),
        ],
        default='pending',
        verbose_name='发送状态'
    )
    
    # 统计信息
    total_recipients = models.IntegerField(default=0, verbose_name='总接收者数')
    sent_count = models.IntegerField(default=0, verbose_name='发送成功数')
    failed_count = models.IntegerField(default=0, verbose_name='发送失败数')
    
    # 结果
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='发送时间')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '推送通知'
        verbose_name_plural = '推送通知'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def success_rate(self):
        """发送成功率"""
        if self.total_recipients > 0:
            return round((self.sent_count / self.total_recipients) * 100, 2)
        return 0

class OfflineSync(models.Model):
    """
    离线同步模型
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offline_syncs', verbose_name='用户')
    device = models.ForeignKey(MobileDevice, on_delete=models.CASCADE, related_name='offline_syncs', verbose_name='设备')
    
    # 同步信息
    sync_type = models.CharField(
        max_length=20,
        choices=[
            ('upload', '上传'),
            ('download', '下载'),
            ('bidirectional', '双向'),
        ],
        verbose_name='同步类型'
    )
    
    # 数据范围
    data_scope = models.JSONField(default=list, verbose_name='数据范围')
    last_sync_at = models.DateTimeField(null=True, blank=True, verbose_name='最后同步时间')
    
    # 状态
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', '等待中'),
            ('in_progress', '进行中'),
            ('completed', '已完成'),
            ('failed', '失败'),
        ],
        default='pending',
        verbose_name='同步状态'
    )
    
    # 统计信息
    total_items = models.IntegerField(default=0, verbose_name='总项目数')
    synced_items = models.IntegerField(default=0, verbose_name='已同步项目数')
    failed_items = models.IntegerField(default=0, verbose_name='失败项目数')
    
    # 错误信息
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '离线同步'
        verbose_name_plural = '离线同步'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_sync_type_display()}"
    
    @property
    def progress_percentage(self):
        """同步进度百分比"""
        if self.total_items > 0:
            return round((self.synced_items / self.total_items) * 100, 2)
        return 0
