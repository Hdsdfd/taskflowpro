from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Notification(models.Model):
    """
    通知模型
    """
    NOTIFICATION_TYPES = (
        ('task_assigned', '任务分配'),
        ('task_completed', '任务完成'),
        ('task_overdue', '任务逾期'),
        ('comment_added', '新增评论'),
        ('file_uploaded', '文件上传'),
        ('project_update', '项目更新'),
        ('milestone_reached', '里程碑达成'),
        ('deadline_approaching', '截止日期临近'),
        ('team_invitation', '团队邀请'),
        ('system_alert', '系统提醒'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='接收者')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES, verbose_name='通知类型')
    title = models.CharField(max_length=255, verbose_name='通知标题')
    message = models.TextField(verbose_name='通知内容')
    
    # 通用外键，可以关联到任何模型
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    is_sent = models.BooleanField(default=False, verbose_name='是否已发送')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='阅读时间')
    
    # 通知级别
    priority = models.CharField(
        max_length=10,
        choices=[
            ('low', '低'),
            ('normal', '普通'),
            ('high', '高'),
            ('urgent', '紧急'),
        ],
        default='normal',
        verbose_name='通知优先级'
    )
    
    # 通知渠道
    channels = models.JSONField(default=list, verbose_name='通知渠道')
    
    class Meta:
        verbose_name = '通知'
        verbose_name_plural = '通知'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['notification_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.recipient.username} - {self.title}"
    
    def mark_as_read(self):
        """标记为已读"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    @property
    def age(self):
        """通知年龄（小时）"""
        delta = timezone.now() - self.created_at
        return delta.total_seconds() / 3600

class NotificationTemplate(models.Model):
    """
    通知模板模型
    """
    name = models.CharField(max_length=100, verbose_name='模板名称')
    notification_type = models.CharField(max_length=30, choices=Notification.NOTIFICATION_TYPES, verbose_name='通知类型')
    title_template = models.CharField(max_length=255, verbose_name='标题模板')
    message_template = models.TextField(verbose_name='内容模板')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '通知模板'
        verbose_name_plural = '通知模板'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class UserNotificationSettings(models.Model):
    """
    用户通知设置模型
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings', verbose_name='用户')
    
    # 邮件通知设置
    email_notifications = models.BooleanField(default=True, verbose_name='启用邮件通知')
    email_frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediate', '立即'),
            ('hourly', '每小时'),
            ('daily', '每日'),
            ('weekly', '每周'),
        ],
        default='immediate',
        verbose_name='邮件频率'
    )
    
    # 站内通知设置
    site_notifications = models.BooleanField(default=True, verbose_name='启用站内通知')
    browser_notifications = models.BooleanField(default=True, verbose_name='启用浏览器通知')
    
    # 特定类型通知设置
    task_notifications = models.BooleanField(default=True, verbose_name='任务相关通知')
    project_notifications = models.BooleanField(default=True, verbose_name='项目相关通知')
    comment_notifications = models.BooleanField(default=True, verbose_name='评论相关通知')
    file_notifications = models.BooleanField(default=True, verbose_name='文件相关通知')
    
    # 免打扰时间
    quiet_hours_start = models.TimeField(null=True, blank=True, verbose_name='免打扰开始时间')
    quiet_hours_end = models.TimeField(null=True, blank=True, verbose_name='免打扰结束时间')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户通知设置'
        verbose_name_plural = '用户通知设置'
    
    def __str__(self):
        return f"{self.user.username} 的通知设置"
    
    @property
    def is_quiet_hours(self):
        """是否在免打扰时间内"""
        if not self.quiet_hours_start or not self.quiet_hours_end:
            return False
        
        now = timezone.now().time()
        if self.quiet_hours_start <= self.quiet_hours_end:
            return self.quiet_hours_start <= now <= self.quiet_hours_end
        else:  # 跨午夜的情况
            return now >= self.quiet_hours_start or now <= self.quiet_hours_end
