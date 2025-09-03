from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from projects.models import Project
from tasks.models import Task

class CalendarEvent(models.Model):
    """
    日历事件模型
    """
    EVENT_TYPES = (
        ('meeting', '会议'),
        ('deadline', '截止日期'),
        ('milestone', '里程碑'),
        ('reminder', '提醒'),
        ('holiday', '假期'),
        ('custom', '自定义'),
    )
    
    PRIORITY_CHOICES = (
        ('low', '低'),
        ('normal', '普通'),
        ('high', '高'),
        ('urgent', '紧急'),
    )
    
    title = models.CharField(max_length=200, verbose_name='事件标题')
    description = models.TextField(blank=True, verbose_name='事件描述')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, verbose_name='事件类型')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal', verbose_name='优先级')
    
    # 时间设置
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    all_day = models.BooleanField(default=False, verbose_name='全天事件')
    
    # 重复设置
    is_recurring = models.BooleanField(default=False, verbose_name='是否重复')
    recurrence_rule = models.CharField(max_length=200, blank=True, verbose_name='重复规则')
    recurrence_end = models.DateTimeField(null=True, blank=True, verbose_name='重复结束时间')
    
    # 关联对象
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='calendar_events', verbose_name='关联项目')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='calendar_events', verbose_name='关联任务')
    
    # 创建者和参与者
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events', verbose_name='创建者')
    attendees = models.ManyToManyField(User, blank=True, related_name='attending_events', verbose_name='参与者')
    
    # 位置和提醒
    location = models.CharField(max_length=200, blank=True, verbose_name='地点')
    reminder_minutes = models.IntegerField(default=15, verbose_name='提前提醒(分钟)')
    
    # 状态
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '日历事件'
        verbose_name_plural = '日历事件'
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['start_time', 'end_time']),
            models.Index(fields=['creator', 'start_time']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def duration(self):
        """事件持续时间"""
        return self.end_time - self.start_time
    
    @property
    def is_past(self):
        """是否已过去"""
        return timezone.now() > self.end_time
    
    @property
    def is_ongoing(self):
        """是否正在进行"""
        now = timezone.now()
        return self.start_time <= now <= self.end_time
    
    @property
    def is_upcoming(self):
        """是否即将到来"""
        return timezone.now() < self.start_time

class Meeting(models.Model):
    """
    会议模型
    """
    MEETING_TYPES = (
        ('project_review', '项目评审'),
        ('team_sync', '团队同步'),
        ('stakeholder', '干系人会议'),
        ('planning', '规划会议'),
        ('retrospective', '回顾会议'),
        ('other', '其他'),
    )
    
    STATUS_CHOICES = (
        ('scheduled', '已安排'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
        ('postponed', '已延期'),
    )
    
    title = models.CharField(max_length=200, verbose_name='会议标题')
    description = models.TextField(verbose_name='会议描述')
    meeting_type = models.CharField(max_length=30, choices=MEETING_TYPES, verbose_name='会议类型')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', verbose_name='会议状态')
    
    # 时间设置
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    timezone = models.CharField(max_length=50, default='Asia/Shanghai', verbose_name='时区')
    
    # 会议信息
    location = models.CharField(max_length=200, blank=True, verbose_name='会议地点')
    meeting_url = models.URLField(blank=True, verbose_name='会议链接')
    meeting_id = models.CharField(max_length=100, blank=True, verbose_name='会议ID')
    meeting_password = models.CharField(max_length=100, blank=True, verbose_name='会议密码')
    
    # 关联对象
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='meetings', verbose_name='关联项目')
    
    # 组织者和参与者
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_meetings', verbose_name='组织者')
    attendees = models.ManyToManyField(User, blank=True, related_name='attending_meetings', verbose_name='参与者')
    required_attendees = models.ManyToManyField(User, blank=True, related_name='required_meetings', verbose_name='必需参与者')
    
    # 议程和记录
    agenda = models.TextField(blank=True, verbose_name='会议议程')
    meeting_notes = models.TextField(blank=True, verbose_name='会议记录')
    action_items = models.JSONField(default=list, verbose_name='行动项')
    
    # 提醒设置
    reminder_minutes = models.IntegerField(default=15, verbose_name='提前提醒(分钟)')
    send_reminder = models.BooleanField(default=True, verbose_name='发送提醒')
    
    # 附件
    attachments = models.JSONField(default=list, verbose_name='会议附件')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '会议'
        verbose_name_plural = '会议'
        ordering = ['start_time']
    
    def __str__(self):
        return self.title
    
    @property
    def duration_minutes(self):
        """会议时长(分钟)"""
        delta = self.end_time - self.start_time
        return int(delta.total_seconds() / 60)
    
    @property
    def is_ongoing(self):
        """会议是否正在进行"""
        now = timezone.now()
        return self.start_time <= now <= self.end_time
    
    @property
    def attendee_count(self):
        """参与者数量"""
        return self.attendees.count()

class MeetingAttendance(models.Model):
    """
    会议出勤记录模型
    """
    ATTENDANCE_STATUS = (
        ('invited', '已邀请'),
        ('accepted', '已接受'),
        ('declined', '已拒绝'),
        ('tentative', '待定'),
        ('attended', '已参加'),
        ('absent', '缺席'),
    )
    
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='attendance_records', verbose_name='会议')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meeting_attendance', verbose_name='用户')
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS, default='invited', verbose_name='出勤状态')
    
    # 响应信息
    response_time = models.DateTimeField(null=True, blank=True, verbose_name='响应时间')
    response_note = models.TextField(blank=True, verbose_name='响应备注')
    
    # 实际参加情况
    joined_at = models.DateTimeField(null=True, blank=True, verbose_name='加入时间')
    left_at = models.DateTimeField(null=True, blank=True, verbose_name='离开时间')
    
    # 通知设置
    email_notification = models.BooleanField(default=True, verbose_name='邮件通知')
    sms_notification = models.BooleanField(default=False, verbose_name='短信通知')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '会议出勤'
        verbose_name_plural = '会议出勤'
        unique_together = ('meeting', 'user')
        ordering = ['meeting', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.meeting.title} ({self.get_status_display()})"
    
    @property
    def attendance_duration(self):
        """实际参加时长"""
        if self.joined_at and self.left_at:
            return self.left_at - self.joined_at
        elif self.joined_at:
            return timezone.now() - self.joined_at
        return None

class TeamCalendar(models.Model):
    """
    团队日历模型
    """
    name = models.CharField(max_length=200, verbose_name='日历名称')
    description = models.TextField(blank=True, verbose_name='日历描述')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='日历颜色')
    
    # 所属团队/项目
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='team_calendars', verbose_name='关联项目')
    
    # 权限设置
    is_public = models.BooleanField(default=False, verbose_name='是否公开')
    can_edit = models.ManyToManyField(User, blank=True, related_name='editable_calendars', verbose_name='可编辑用户')
    can_view = models.ManyToManyField(User, blank=True, related_name='viewable_calendars', verbose_name='可查看用户')
    
    # 日历设置
    default_reminder_minutes = models.IntegerField(default=15, verbose_name='默认提醒时间(分钟)')
    working_hours_start = models.TimeField(default='09:00', verbose_name='工作时间开始')
    working_hours_end = models.TimeField(default='18:00', verbose_name='工作时间结束')
    working_days = models.JSONField(default=list, verbose_name='工作日')
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '团队日历'
        verbose_name_plural = '团队日历'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
